from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.identity.context import TenantContext
from app.platform.db import Base
from app.platform.records import TenantRecord


class AuditEvent(TenantRecord, Base):
    __tablename__ = "audit_events"
    actor_id: Mapped[UUID]
    event_type: Mapped[str] = mapped_column(String(120))
    entity_id: Mapped[UUID]
    details: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict)


class OutboxEvent(TenantRecord, Base):
    __tablename__ = "outbox_events"
    event_type: Mapped[str] = mapped_column(String(120))
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(24), default="pending")
    attempts: Mapped[int] = mapped_column(default=0)
    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    last_error: Mapped[str | None] = mapped_column(String(120))


def record_event(
    ctx: TenantContext, event_type: str, entity_id: UUID, details: dict[str, object] | None = None
) -> None:
    ctx.session.add(
        AuditEvent(
            tenant_id=ctx.tenant_id,
            actor_id=ctx.actor_id,
            event_type=event_type,
            entity_id=entity_id,
            details=details or {},
        )
    )
    ctx.session.add(
        OutboxEvent(
            tenant_id=ctx.tenant_id,
            event_type=event_type,
            payload={"entity_id": str(entity_id), "actor_id": str(ctx.actor_id)},
        )
    )
