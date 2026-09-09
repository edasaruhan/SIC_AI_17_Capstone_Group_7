from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.db import Base
from app.platform.records import TenantRecord


class GenerationDraft(TenantRecord, Base):
    __tablename__ = "generation_drafts"
    customer_id: Mapped[UUID]
    actor_id: Mapped[UUID]
    channel: Mapped[str] = mapped_column(String(24))
    objective: Mapped[str] = mapped_column(String(500))
    verified_facts: Mapped[dict[str, object]] = mapped_column(JSONB)
    provider: Mapped[str] = mapped_column(String(40))
    provider_model: Mapped[str] = mapped_column(String(160))
    output: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32))
    human_approval_required: Mapped[bool] = mapped_column(default=True)
    action_authorized: Mapped[bool] = mapped_column(default=False)
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        ForeignKeyConstraint(["tenant_id", "customer_id"], ["customers.tenant_id", "customers.id"]),
    )
