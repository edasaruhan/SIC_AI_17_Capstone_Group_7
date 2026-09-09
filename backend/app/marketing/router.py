from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.identity.context import TenantContext, permitted
from app.identity.permissions import Permission
from app.marketing import attribution, audiences, campaigns
from app.marketing.models import AudienceDefinition, Campaign
from app.marketing.schemas import (
    AttributionRead,
    AudienceCreate,
    AudienceRead,
    AudienceSnapshotRead,
    CampaignCreate,
    CampaignRead,
    CampaignTransition,
    TouchpointCreate,
)

router = APIRouter(prefix="/api/v1/marketing", tags=["Marketing"])


@router.post("/touchpoints", status_code=201)
def touchpoint(
    payload: TouchpointCreate,
    ctx: TenantContext = Depends(permitted(Permission.MARKETING_WRITE)),
) -> dict[str, str]:
    row = attribution.record_touchpoint(ctx, payload)
    return {"id": str(row.id), "evidence": "first_party_observed"}


@router.post("/orders/{order_id}/attribution", response_model=AttributionRead, status_code=201)
def attribute(
    order_id: UUID,
    ctx: TenantContext = Depends(permitted(Permission.MARKETING_WRITE)),
) -> AttributionRead:
    return AttributionRead.model_validate(attribution.attribute_order(ctx, order_id))


@router.get("/audiences", response_model=list[AudienceRead])
def list_audiences(
    ctx: TenantContext = Depends(permitted(Permission.READ)),
) -> list[AudienceRead]:
    rows = ctx.session.scalars(
        select(AudienceDefinition)
        .where(AudienceDefinition.tenant_id == ctx.tenant_id)
        .order_by(AudienceDefinition.created_at.desc())
    )
    return [AudienceRead.model_validate(row) for row in rows]


@router.post("/audiences", response_model=AudienceRead, status_code=201)
def create_audience(
    payload: AudienceCreate,
    ctx: TenantContext = Depends(permitted(Permission.MARKETING_WRITE)),
) -> AudienceRead:
    return AudienceRead.model_validate(audiences.create_audience(ctx, payload))


@router.post(
    "/audiences/{audience_id}/snapshots", response_model=AudienceSnapshotRead, status_code=201
)
def snapshot(
    audience_id: UUID,
    ctx: TenantContext = Depends(permitted(Permission.MARKETING_WRITE)),
) -> AudienceSnapshotRead:
    return AudienceSnapshotRead.model_validate(audiences.build_snapshot(ctx, audience_id))


@router.get("/campaigns", response_model=list[CampaignRead])
def list_campaigns(
    ctx: TenantContext = Depends(permitted(Permission.READ)),
) -> list[CampaignRead]:
    rows = ctx.session.scalars(
        select(Campaign)
        .where(Campaign.tenant_id == ctx.tenant_id)
        .order_by(Campaign.created_at.desc())
    )
    return [CampaignRead.model_validate(row) for row in rows]


@router.post("/campaigns", response_model=CampaignRead, status_code=201)
def create_campaign(
    payload: CampaignCreate,
    ctx: TenantContext = Depends(permitted(Permission.MARKETING_WRITE)),
) -> CampaignRead:
    return CampaignRead.model_validate(campaigns.create_campaign(ctx, payload))


@router.post("/campaigns/{campaign_id}/transitions", response_model=CampaignRead)
def transition_campaign(
    campaign_id: UUID,
    payload: CampaignTransition,
    ctx: TenantContext = Depends(permitted(Permission.MARKETING_WRITE)),
) -> CampaignRead:
    return CampaignRead.model_validate(campaigns.transition(ctx, campaign_id, payload))
