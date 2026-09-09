from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKeyConstraint, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.db import Base
from app.platform.records import TenantRecord


class Integration(TenantRecord, Base):
    __tablename__ = "integrations"
    created_by: Mapped[UUID]
    provider: Mapped[str] = mapped_column(String(24))
    name: Mapped[str] = mapped_column(String(120))
    external_account_id: Mapped[str] = mapped_column(String(160))
    secret_ref: Mapped[str] = mapped_column(String(220))
    api_version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(24), default="configured")
    cursor: Mapped[str | None] = mapped_column(String(500))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error_code: Mapped[str | None] = mapped_column(String(80))
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "provider", "external_account_id"),
    )


class IntegrationSyncRun(TenantRecord, Base):
    __tablename__ = "integration_sync_runs"
    integration_id: Mapped[UUID]
    requested_by: Mapped[UUID]
    status: Mapped[str] = mapped_column(String(24), default="queued")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    input_cursor: Mapped[str | None] = mapped_column(String(500))
    output_cursor: Mapped[str | None] = mapped_column(String(500))
    records_received: Mapped[int] = mapped_column(default=0)
    raw_object_id: Mapped[UUID | None]
    raw_sha256: Mapped[str | None] = mapped_column(String(64))
    error_code: Mapped[str | None] = mapped_column(String(80))
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        ForeignKeyConstraint(
            ["tenant_id", "integration_id"], ["integrations.tenant_id", "integrations.id"]
        ),
    )


class AdPerformanceDaily(TenantRecord, Base):
    __tablename__ = "ad_performance_daily"
    integration_id: Mapped[UUID]
    sync_run_id: Mapped[UUID]
    provider: Mapped[str] = mapped_column(String(24))
    metric_date: Mapped[date] = mapped_column(Date)
    external_campaign_id: Mapped[str] = mapped_column(String(160))
    campaign_name: Mapped[str] = mapped_column(String(300))
    impressions: Mapped[int]
    clicks: Mapped[int]
    spend: Mapped[Decimal] = mapped_column(Numeric(16, 4))
    conversions: Mapped[Decimal | None] = mapped_column(Numeric(16, 4))
    conversion_value: Mapped[Decimal | None] = mapped_column(Numeric(16, 4))
    currency: Mapped[str | None] = mapped_column(String(3))
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "integration_id", "metric_date", "external_campaign_id"),
        ForeignKeyConstraint(
            ["tenant_id", "integration_id"], ["integrations.tenant_id", "integrations.id"]
        ),
        ForeignKeyConstraint(
            ["tenant_id", "sync_run_id"],
            ["integration_sync_runs.tenant_id", "integration_sync_runs.id"],
        ),
    )
