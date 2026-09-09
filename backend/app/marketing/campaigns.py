from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select

from app.identity.context import TenantContext
from app.identity.permissions import Permission
from app.marketing.models import Campaign, CampaignAction
from app.marketing.schemas import CampaignCreate, CampaignTransition
from app.platform.audit import record_event
from app.platform.config import get_settings
from app.platform.errors import DomainError

TRANSITIONS = {
    "draft": {"pending_approval", "cancelled"},
    "pending_approval": {"approved", "cancelled"},
    "approved": {"queued", "cancelled"},
    "queued": {"paused", "cancelled"},
    "active": {"paused", "cancelled"},
    "paused": {"queued", "cancelled"},
}


def create_campaign(ctx: TenantContext, payload: CampaignCreate) -> Campaign:
    row = Campaign(tenant_id=ctx.tenant_id, created_by=ctx.actor_id, **payload.model_dump())
    ctx.session.add(row)
    ctx.session.flush()
    record_event(ctx, "campaign.draft_created", row.id)
    return row


def transition(ctx: TenantContext, campaign_id: UUID, payload: CampaignTransition) -> Campaign:
    campaign = ctx.session.scalar(
        select(Campaign)
        .where(Campaign.tenant_id == ctx.tenant_id, Campaign.id == campaign_id)
        .with_for_update()
    )
    if campaign is None:
        raise DomainError("Campaign not found", 404)
    existing = ctx.session.scalar(
        select(CampaignAction).where(
            CampaignAction.tenant_id == ctx.tenant_id,
            CampaignAction.idempotency_key == payload.idempotency_key,
        )
    )
    if existing:
        if existing.campaign_id != campaign.id or existing.to_status != payload.target:
            raise DomainError("Idempotency key was used for another action", 409)
        return campaign
    if payload.target not in TRANSITIONS.get(campaign.status, set()):
        raise DomainError("Campaign transition is not allowed", 409)
    if payload.target == "approved":
        ctx.require(Permission.APPROVE)
        campaign.approved_by = ctx.actor_id
        campaign.approved_at = datetime.now(UTC)
    if payload.target == "queued":
        settings = get_settings()
        if settings.marketing_kill_switch:
            raise DomainError("Marketing execution kill switch is enabled", 409)
        if float(campaign.budget) > settings.max_campaign_budget:
            raise DomainError("Campaign exceeds the configured budget ceiling", 409)
        if campaign.approved_at is None:
            raise DomainError("Campaign approval evidence is missing", 409)
    previous = campaign.status
    campaign.status = payload.target
    action = CampaignAction(
        tenant_id=ctx.tenant_id,
        campaign_id=campaign.id,
        actor_id=ctx.actor_id,
        from_status=previous,
        to_status=payload.target,
        reason=payload.reason,
        idempotency_key=payload.idempotency_key,
    )
    ctx.session.add(action)
    ctx.session.flush()
    record_event(ctx, f"campaign.{payload.target}", campaign.id)
    return campaign
