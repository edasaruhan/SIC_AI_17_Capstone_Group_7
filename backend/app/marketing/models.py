from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKeyConstraint, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.db import Base
from app.platform.records import TenantRecord


class MarketingTouchpoint(TenantRecord, Base):
    __tablename__ = "marketing_touchpoints"
    customer_id: Mapped[UUID | None]
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(40))
    session_hash: Mapped[str | None] = mapped_column(String(64))
    click_hash: Mapped[str | None] = mapped_column(String(64))
    utm_source: Mapped[str | None] = mapped_column(String(160))
    utm_medium: Mapped[str | None] = mapped_column(String(160))
    utm_campaign: Mapped[str | None] = mapped_column(String(300))
    external_campaign_id: Mapped[str | None] = mapped_column(String(160))
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        ForeignKeyConstraint(["tenant_id", "customer_id"], ["customers.tenant_id", "customers.id"]),
    )


class OrderAttribution(TenantRecord, Base):
    __tablename__ = "order_attributions"
    order_id: Mapped[UUID]
    touchpoint_id: Mapped[UUID]
    method: Mapped[str] = mapped_column(String(40))
    method_version: Mapped[str] = mapped_column(String(40))
    evidence: Mapped[str] = mapped_column(String(80))
    quality: Mapped[str] = mapped_column(String(40))
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "order_id", "method_version"),
        ForeignKeyConstraint(["tenant_id", "order_id"], ["orders.tenant_id", "orders.id"]),
        ForeignKeyConstraint(
            ["tenant_id", "touchpoint_id"],
            ["marketing_touchpoints.tenant_id", "marketing_touchpoints.id"],
        ),
    )


class AudienceDefinition(TenantRecord, Base):
    __tablename__ = "audience_definitions"
    created_by: Mapped[UUID]
    name: Mapped[str] = mapped_column(String(160))
    version: Mapped[int] = mapped_column(default=1)
    status: Mapped[str] = mapped_column(String(24), default="active")
    rule: Mapped[dict[str, object]] = mapped_column(JSONB)
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "name", "version"),
    )


class AudienceSnapshot(TenantRecord, Base):
    __tablename__ = "audience_snapshots"
    audience_id: Mapped[UUID]
    definition_version: Mapped[int]
    generated_by: Mapped[UUID]
    member_count: Mapped[int] = mapped_column(default=0)
    evidence: Mapped[str] = mapped_column(String(80), default="canonical_operational_data")
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        ForeignKeyConstraint(
            ["tenant_id", "audience_id"],
            ["audience_definitions.tenant_id", "audience_definitions.id"],
        ),
    )


class AudienceMember(TenantRecord, Base):
    __tablename__ = "audience_members"
    snapshot_id: Mapped[UUID]
    customer_id: Mapped[UUID]
    reason_codes: Mapped[list[str]] = mapped_column(JSONB)
    consent_channels: Mapped[list[str]] = mapped_column(JSONB)
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "snapshot_id", "customer_id"),
        ForeignKeyConstraint(
            ["tenant_id", "snapshot_id"], ["audience_snapshots.tenant_id", "audience_snapshots.id"]
        ),
        ForeignKeyConstraint(["tenant_id", "customer_id"], ["customers.tenant_id", "customers.id"]),
    )


class Campaign(TenantRecord, Base):
    __tablename__ = "campaigns"
    created_by: Mapped[UUID]
    integration_id: Mapped[UUID | None]
    audience_snapshot_id: Mapped[UUID | None]
    name: Mapped[str] = mapped_column(String(200))
    provider: Mapped[str] = mapped_column(String(24))
    budget: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(32), default="draft")
    provider_campaign_id: Mapped[str | None] = mapped_column(String(160))
    approved_by: Mapped[UUID | None]
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_code: Mapped[str | None] = mapped_column(String(80))
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        ForeignKeyConstraint(
            ["tenant_id", "integration_id"], ["integrations.tenant_id", "integrations.id"]
        ),
        ForeignKeyConstraint(
            ["tenant_id", "audience_snapshot_id"],
            ["audience_snapshots.tenant_id", "audience_snapshots.id"],
        ),
    )


class CampaignAction(TenantRecord, Base):
    __tablename__ = "campaign_actions"
    campaign_id: Mapped[UUID]
    actor_id: Mapped[UUID]
    from_status: Mapped[str] = mapped_column(String(32))
    to_status: Mapped[str] = mapped_column(String(32))
    reason: Mapped[str] = mapped_column(String(500))
    idempotency_key: Mapped[str] = mapped_column(String(160))
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        ForeignKeyConstraint(["tenant_id", "campaign_id"], ["campaigns.tenant_id", "campaigns.id"]),
    )
