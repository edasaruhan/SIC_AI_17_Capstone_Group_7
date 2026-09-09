from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IntegrationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: Literal["meta_ads", "google_ads"]
    name: str = Field(min_length=1, max_length=120)
    external_account_id: str = Field(min_length=1, max_length=160, pattern=r"^[A-Za-z0-9_-]+$")
    secret_ref: str = Field(pattern=r"^env:GP_PROVIDER_[A-Z0-9_]+$", max_length=220)


class IntegrationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    provider: str
    name: str
    external_account_id: str
    api_version: str
    status: str
    last_success_at: datetime | None
    last_error_code: str | None
    created_at: datetime


class SyncRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    integration_id: UUID
    status: str
    records_received: int
    error_code: str | None
    created_at: datetime
    completed_at: datetime | None
