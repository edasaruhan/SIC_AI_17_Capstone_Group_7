from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MappingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fields: dict[str, str] = Field(min_length=1, max_length=64)


class BatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    kind: str
    filename: str
    checksum: str
    status: str
    headers: list[str]
    mapping: dict[str, str]
    errors: list[dict[str, object]]
    committed_count: int
    attempts: int
    transform_version: str
    created_at: datetime
