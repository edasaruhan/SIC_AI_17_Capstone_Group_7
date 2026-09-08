from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CustomerCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=200)
    email: str | None = Field(default=None, max_length=320, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    phone: str | None = Field(default=None, max_length=32)
    external_id: str | None = Field(default=None, min_length=1, max_length=200)
    status: Literal["active", "inactive", "lead"] = "active"
    tags: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        return value.casefold() if value else None

    @field_validator("tags")
    @classmethod
    def bounded_tags(cls, tags: list[str]) -> list[str]:
        if any(not tag.strip() or len(tag) > 64 for tag in tags):
            raise ValueError("Tags must contain between 1 and 64 characters")
        return sorted(set(tag.strip() for tag in tags))


class CustomerRead(CustomerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime


class CustomerPage(BaseModel):
    items: list[CustomerRead]
    total: int
    limit: int
    offset: int


class InteractionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    kind: Literal["note", "call", "email", "meeting"] = "note"
    body: str = Field(min_length=1, max_length=5000)


class InteractionRead(InteractionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime


class ConsentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    channel: Literal["email", "sms", "ads"]
    granted: bool
    source: str = Field(min_length=1, max_length=200)


class ConsentRead(ConsentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
