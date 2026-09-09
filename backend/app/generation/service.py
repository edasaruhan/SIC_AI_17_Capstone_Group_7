import json
import re
from typing import Protocol

from sqlalchemy import select

from app.analytics.service import customer_summary
from app.generation.models import GenerationDraft
from app.generation.schemas import DraftRequest
from app.identity.context import TenantContext
from app.intelligence.models import CustomerPrediction
from app.intelligence.service import latest_consent
from app.platform.audit import record_event
from app.platform.errors import DomainError

NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:[.,]\d+)?%?")
UNSUPPORTED_CLAIMS = ("guarantee", "guaranteed", "will purchase", "will return", "best customer")


class LLMProvider(Protocol):
    name: str
    model: str

    def generate(self, prompt: str) -> str: ...


class DisabledProvider:
    name = "disabled"
    model = "none"

    def generate(self, prompt: str) -> str:
        raise DomainError("No generative provider credential is configured", 409)


def get_provider() -> LLMProvider:
    # Live network execution intentionally remains disabled until credentials and
    # the deployment-specific provider adapter are validated.
    return DisabledProvider()


def prompt_for(objective: str, channel: str, facts: dict[str, object]) -> str:
    return (
        "Draft concise marketing copy. Use only the verified JSON facts below. "
        "Do not infer missing numbers, outcomes, causes, or personal characteristics. "
        "Do not promise that the customer will act. Human approval is mandatory.\n"
        f"Channel: {channel}\nObjective: {objective}\nVerified facts: "
        f"{json.dumps(facts, sort_keys=True)}"
    )


def validate_grounding(output: str, facts: dict[str, object]) -> None:
    lowered = output.casefold()
    if any(claim in lowered for claim in UNSUPPORTED_CLAIMS):
        raise DomainError("Generated draft contains an unsupported outcome claim", 502)
    allowed_numbers = {
        token.replace(",", ".").removesuffix("%")
        for value in facts.values()
        for token in NUMBER.findall(str(value))
    }
    output_numbers = {token.replace(",", ".").removesuffix("%") for token in NUMBER.findall(output)}
    if not output_numbers.issubset(allowed_numbers):
        raise DomainError("Generated draft contains an unsupported number", 502)


def generate_draft(ctx: TenantContext, payload: DraftRequest) -> GenerationDraft:
    consent = latest_consent(ctx, payload.customer_id)
    if not consent[payload.channel]:
        raise DomainError("Explicit consent is required before drafting for this channel", 409)
    summary = customer_summary(ctx, payload.customer_id, None)
    prediction = ctx.session.scalar(
        select(CustomerPrediction)
        .where(
            CustomerPrediction.tenant_id == ctx.tenant_id,
            CustomerPrediction.customer_id == payload.customer_id,
        )
        .order_by(CustomerPrediction.scored_at.desc())
        .limit(1)
    )
    facts: dict[str, object] = {
        "currency": summary.currency,
        "observed_purchase_count": summary.frequency,
        "observed_net_revenue": str(summary.monetary),
        "deterministic_segment": summary.segment,
    }
    if summary.recency_days is not None:
        facts["recency_days"] = summary.recency_days
    if prediction:
        facts["inactivity_probability"] = round(prediction.inactivity_probability, 6)
        facts["model_sha256"] = str(prediction.provenance["model_sha256"])
    provider = get_provider()
    output = provider.generate(prompt_for(payload.objective, payload.channel, facts)).strip()
    if not output or len(output) > 5000:
        raise DomainError("Generated draft has an invalid length", 502)
    validate_grounding(output, facts)
    row = GenerationDraft(
        tenant_id=ctx.tenant_id,
        customer_id=payload.customer_id,
        actor_id=ctx.actor_id,
        channel=payload.channel,
        objective=payload.objective,
        verified_facts=facts,
        provider=provider.name,
        provider_model=provider.model,
        output=output,
        status="generated",
        human_approval_required=True,
        action_authorized=False,
    )
    ctx.session.add(row)
    ctx.session.flush()
    record_event(ctx, "generation.draft_created", row.id, {"channel": payload.channel})
    return row
