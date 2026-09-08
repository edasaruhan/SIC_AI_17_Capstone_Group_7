from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.db import Base
from app.platform.records import TenantRecord


class Customer(TenantRecord, Base):
    __tablename__ = "customers"
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(320))
    phone: Mapped[str | None] = mapped_column(String(32))
    external_id: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(24), default="active")
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "external_id"),
    )


class Interaction(TenantRecord, Base):
    __tablename__ = "customer_interactions"
    customer_id: Mapped[UUID]
    kind: Mapped[str] = mapped_column(String(24))
    body: Mapped[str] = mapped_column(Text)
    actor_id: Mapped[UUID]
    __table_args__ = (
        ForeignKeyConstraint(["tenant_id", "customer_id"], ["customers.tenant_id", "customers.id"]),
    )


class MarketingConsent(TenantRecord, Base):
    __tablename__ = "marketing_consents"
    customer_id: Mapped[UUID]
    channel: Mapped[str] = mapped_column(String(24))
    granted: Mapped[bool]
    source: Mapped[str] = mapped_column(String(200))
    actor_id: Mapped[UUID]
    __table_args__ = (
        ForeignKeyConstraint(["tenant_id", "customer_id"], ["customers.tenant_id", "customers.id"]),
    )
