from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: UUID
    channel: Literal["email", "sms"]
    objective: str = Field(min_length=3, max_length=500)


class DraftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    customer_id: UUID
    channel: str
    objective: str
    verified_facts: dict[str, object]
    provider: str
    provider_model: str
    output: str
    status: str
    human_approval_required: bool
    action_authorized: bool
    created_at: datetime
