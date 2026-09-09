from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TouchpointCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: UUID | None = None
    occurred_at: datetime
    source: Literal["web", "meta_ads", "google_ads", "manual_import"]
    session_identifier: str | None = Field(default=None, min_length=8, max_length=500)
    click_identifier: str | None = Field(default=None, min_length=8, max_length=500)
    utm_source: str | None = Field(default=None, max_length=160)
    utm_medium: str | None = Field(default=None, max_length=160)
    utm_campaign: str | None = Field(default=None, max_length=300)
    external_campaign_id: str | None = Field(default=None, max_length=160)

    @model_validator(mode="after")
    def require_identity(self) -> "TouchpointCreate":
        if not (self.customer_id or self.session_identifier or self.click_identifier):
            raise ValueError("A deterministic customer, session, or click identifier is required")
        return self


class AttributionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    order_id: UUID
    touchpoint_id: UUID
    method: str
    method_version: str
    evidence: str
    quality: str
    created_at: datetime


class AudienceRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["active", "inactive", "lead"] | None = None
    tags_any: list[str] = Field(default_factory=list, max_length=20)
    min_purchase_count: int = Field(default=0, ge=0)
    min_net_revenue: Decimal = Field(default=Decimal(0), ge=0)
    min_inactivity_probability: float | None = Field(default=None, ge=0, le=1)
    consent_channel: Literal["email", "sms", "ads"] | None = None


class AudienceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=160)
    rule: AudienceRule


class AudienceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    version: int
    status: str
    rule: dict[str, object]
    created_at: datetime


class AudienceSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    audience_id: UUID
    definition_version: int
    member_count: int
    evidence: str
    created_at: datetime


class CampaignCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=200)
    provider: Literal["meta_ads", "google_ads"]
    budget: Decimal = Field(ge=0, decimal_places=2, max_digits=14)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    integration_id: UUID | None = None
    audience_snapshot_id: UUID | None = None


class CampaignTransition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target: Literal["pending_approval", "approved", "queued", "paused", "cancelled"]
    reason: str = Field(min_length=3, max_length=500)
    idempotency_key: str = Field(min_length=8, max_length=160)


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    provider: str
    budget: Decimal
    currency: str
    status: str
    integration_id: UUID | None
    audience_snapshot_id: UUID | None
    approved_at: datetime | None
    provider_campaign_id: str | None
    failure_code: str | None
    created_at: datetime
