from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.identity.context import TenantContext, permitted
from app.identity.permissions import Permission
from app.platform.audit import AuditEvent

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    actor_id: UUID
    event_type: str
    entity_id: UUID
    details: dict[str, object]
    created_at: datetime


@router.get("", response_model=list[AuditEventRead])
def events(
    limit: int = Query(100, ge=1, le=200),
    ctx: TenantContext = Depends(permitted(Permission.AUDIT)),
) -> list[AuditEventRead]:
    rows = ctx.session.scalars(
        select(AuditEvent)
        .where(AuditEvent.tenant_id == ctx.tenant_id)
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
        .limit(limit)
    )
    return [AuditEventRead.model_validate(row) for row in rows]
