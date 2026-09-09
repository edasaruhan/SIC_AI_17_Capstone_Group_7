from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select

from app.commerce.models import Order
from app.crm.models import Customer
from app.identity.context import TenantContext
from app.intelligence.decision import Channel
from app.intelligence.models import CustomerPrediction
from app.intelligence.service import latest_consent
from app.marketing.models import AudienceDefinition, AudienceMember, AudienceSnapshot
from app.marketing.schemas import AudienceCreate, AudienceRule
from app.platform.audit import record_event
from app.platform.errors import DomainError


def create_audience(ctx: TenantContext, payload: AudienceCreate) -> AudienceDefinition:
    row = AudienceDefinition(
        tenant_id=ctx.tenant_id,
        created_by=ctx.actor_id,
        name=payload.name,
        rule=payload.rule.model_dump(mode="json"),
    )
    ctx.session.add(row)
    ctx.session.flush()
    record_event(ctx, "audience.definition_created", row.id)
    return row


def build_snapshot(ctx: TenantContext, audience_id: UUID) -> AudienceSnapshot:
    audience = ctx.session.scalar(
        select(AudienceDefinition).where(
            AudienceDefinition.tenant_id == ctx.tenant_id,
            AudienceDefinition.id == audience_id,
            AudienceDefinition.status == "active",
        )
    )
    if audience is None:
        raise DomainError("Active audience definition not found", 404)
    rule = AudienceRule.model_validate(audience.rule)
    members: list[tuple[UUID, list[str], list[Channel]]] = []
    customers = ctx.session.scalars(
        select(Customer).where(Customer.tenant_id == ctx.tenant_id).order_by(Customer.id)
    )
    for customer in customers:
        if rule.status and customer.status != rule.status:
            continue
        if rule.tags_any and not set(rule.tags_any).intersection(customer.tags):
            continue
        count, revenue = ctx.session.execute(
            select(
                func.count(Order.id), func.coalesce(func.sum(Order.total - Order.refunded_total), 0)
            ).where(Order.tenant_id == ctx.tenant_id, Order.customer_id == customer.id)
        ).one()
        if count < rule.min_purchase_count or Decimal(revenue) < rule.min_net_revenue:
            continue
        prediction = ctx.session.scalar(
            select(CustomerPrediction)
            .where(
                CustomerPrediction.tenant_id == ctx.tenant_id,
                CustomerPrediction.customer_id == customer.id,
            )
            .order_by(CustomerPrediction.scored_at.desc())
            .limit(1)
        )
        if rule.min_inactivity_probability is not None and (
            prediction is None
            or prediction.inactivity_probability < rule.min_inactivity_probability
        ):
            continue
        consent = latest_consent(ctx, customer.id)
        channels = [channel for channel, granted in consent.items() if granted]
        if rule.consent_channel and rule.consent_channel not in channels:
            continue
        reasons = ["RULE_VERSION_MATCH"]
        if rule.consent_channel:
            reasons.append("EXPLICIT_CHANNEL_CONSENT")
        members.append((customer.id, reasons, channels))
    snapshot = AudienceSnapshot(
        tenant_id=ctx.tenant_id,
        audience_id=audience.id,
        definition_version=audience.version,
        generated_by=ctx.actor_id,
        member_count=len(members),
    )
    ctx.session.add(snapshot)
    ctx.session.flush()
    for customer_id, reasons, channels in members:
        ctx.session.add(
            AudienceMember(
                tenant_id=ctx.tenant_id,
                snapshot_id=snapshot.id,
                customer_id=customer_id,
                reason_codes=reasons,
                consent_channels=[str(channel) for channel in channels],
            )
        )
    ctx.session.flush()
    record_event(
        ctx,
        "audience.snapshot_generated",
        snapshot.id,
        {"member_count": snapshot.member_count, "definition_version": audience.version},
    )
    return snapshot
