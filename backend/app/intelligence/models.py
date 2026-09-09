from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.db import Base
from app.platform.records import TenantRecord


class CustomerPrediction(TenantRecord, Base):
    __tablename__ = "customer_predictions"
    customer_id: Mapped[UUID]
    actor_id: Mapped[UUID]
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    feature_cutoff: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    inactivity_probability: Mapped[float]
    frozen_threshold: Mapped[float]
    decision_state: Mapped[str] = mapped_column(String(32))
    eligible_channels: Mapped[list[str]] = mapped_column(JSONB, default=list)
    reason_codes: Mapped[list[str]] = mapped_column(JSONB, default=list)
    feature_snapshot: Mapped[dict[str, object]] = mapped_column(JSONB)
    provenance: Mapped[dict[str, object]] = mapped_column(JSONB)
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        ForeignKeyConstraint(["tenant_id", "customer_id"], ["customers.tenant_id", "customers.id"]),
    )


class ScoringJob(TenantRecord, Base):
    __tablename__ = "scoring_jobs"
    requested_by: Mapped[UUID]
    status: Mapped[str] = mapped_column(String(24), default="queued")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_customers: Mapped[int] = mapped_column(default=0)
    scored_customers: Mapped[int] = mapped_column(default=0)
    skipped_customers: Mapped[int] = mapped_column(default=0)
    failed_customers: Mapped[int] = mapped_column(default=0)
    model_sha256: Mapped[str] = mapped_column(String(64))
    error_code: Mapped[str | None] = mapped_column(String(80))
