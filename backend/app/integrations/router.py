from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.identity.context import TenantContext, permitted
from app.identity.permissions import Permission
from app.integrations import service
from app.integrations.models import Integration
from app.integrations.schemas import IntegrationCreate, IntegrationRead, SyncRunRead

router = APIRouter(prefix="/api/v1/integrations", tags=["Integrations"])


@router.get("", response_model=list[IntegrationRead])
def integrations(
    ctx: TenantContext = Depends(permitted(Permission.READ)),
) -> list[IntegrationRead]:
    rows = ctx.session.scalars(
        select(Integration)
        .where(Integration.tenant_id == ctx.tenant_id)
        .order_by(Integration.created_at.desc())
    )
    return [IntegrationRead.model_validate(row) for row in rows]


@router.post("", response_model=IntegrationRead, status_code=201)
def create(
    payload: IntegrationCreate,
    ctx: TenantContext = Depends(permitted(Permission.INTEGRATION_WRITE)),
) -> IntegrationRead:
    return IntegrationRead.model_validate(service.create_integration(ctx, payload))


@router.post("/{integration_id}/syncs", response_model=SyncRunRead, status_code=202)
def sync(
    integration_id: UUID,
    ctx: TenantContext = Depends(permitted(Permission.INTEGRATION_WRITE)),
) -> SyncRunRead:
    return SyncRunRead.model_validate(service.queue_sync(ctx, integration_id))
