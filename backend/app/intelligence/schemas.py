from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PredictionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    created_at: datetime
    scored_at: datetime
    feature_cutoff: datetime
    inactivity_probability: float
    frozen_threshold: float
    decision_state: str
    eligible_channels: list[str]
    reason_codes: list[str]
    provenance: dict[str, object]
    human_approval_required: bool
    action_authorized: bool = False


class ScoringJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    total_customers: int
    scored_customers: int
    skipped_customers: int
    failed_customers: int
    model_sha256: str
    error_code: str | None
    created_at: datetime
    completed_at: datetime | None
