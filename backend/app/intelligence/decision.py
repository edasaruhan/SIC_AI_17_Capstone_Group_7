"""Pure, consent-aware recommendation policy for reviewed retention workflows."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Probability = Annotated[float, Field(ge=0.0, le=1.0)]
NonNegative = Annotated[float, Field(ge=0.0)]
Channel = Literal["email", "sms", "ads"]
CHANNELS: tuple[Channel, ...] = ("email", "sms", "ads")


class DecisionState(StrEnum):
    MONITOR = "monitor"
    REVIEW_RETENTION = "review_retention"
    NO_CONTACT_REVIEW = "no_contact_review"


class DecisionEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    target_version: str = Field(min_length=1)
    feature_version: str = Field(min_length=1)
    split_version: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    explanation_method: Literal["linear_shap_log_odds"]


class DecisionInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    inactivity_probability: Probability
    frozen_threshold: Probability
    consent: dict[Channel, bool]
    evidence: DecisionEvidence
    explanation_reason_codes: tuple[str, ...] = Field(default=(), max_length=10)
    monetary_365: NonNegative | None = None
    recency_days: NonNegative | None = None

    @model_validator(mode="after")
    def require_all_consent_states(self) -> "DecisionInput":
        expected = {"email", "sms", "ads"}
        if set(self.consent) != expected:
            raise ValueError("Consent must explicitly cover email, sms and ads")
        return self


class DecisionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    state: DecisionState
    risk_band: Literal["routine", "elevated"]
    eligible_channels: tuple[Channel, ...]
    reason_codes: tuple[str, ...]
    human_approval_required: bool
    action_authorized: Literal[False]
    evidence: DecisionEvidence
    safety_note: str


def decide(value: DecisionInput) -> DecisionOutput:
    """Recommend an auditable review state without authorizing or executing contact."""
    elevated = value.inactivity_probability >= value.frozen_threshold
    channels = tuple(channel for channel in CHANNELS if value.consent[channel])
    reasons = list(value.explanation_reason_codes)
    reasons.append("ABOVE_FROZEN_REVIEW_THRESHOLD" if elevated else "BELOW_REVIEW_THRESHOLD")

    if not elevated:
        state = DecisionState.MONITOR
        channels = ()
    elif channels:
        state = DecisionState.REVIEW_RETENTION
        reasons.append("CONSENTED_CHANNEL_AVAILABLE")
    else:
        state = DecisionState.NO_CONTACT_REVIEW
        reasons.append("NO_CONSENTED_CHANNEL")

    return DecisionOutput(
        state=state,
        risk_band="elevated" if elevated else "routine",
        eligible_channels=channels,
        reason_codes=tuple(dict.fromkeys(reasons)),
        human_approval_required=state is not DecisionState.MONITOR,
        action_authorized=False,
        evidence=value.evidence,
        safety_note=(
            "This prioritization is not causal evidence or contact authorization. "
            "A permitted human reviewer must approve any outreach."
        ),
    )
