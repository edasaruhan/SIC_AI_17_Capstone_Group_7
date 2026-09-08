from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=120)


class CategoryRead(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID


class ProductCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    category_id: UUID | None = None
    unit_price: Decimal = Field(ge=0, le=999999999, decimal_places=2)
    currency: str = Field(default="TRY", pattern="^[A-Z]{3}$")
    active: bool = True


class ProductRead(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    stock_on_hand: int
    created_at: datetime


class StockAdjustment(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    quantity_delta: int = Field(ge=-1000000, le=1000000)
    reason: str = Field(min_length=1, max_length=200)
    idempotency_key: str = Field(min_length=1, max_length=150)


class MovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    product_id: UUID
    quantity_delta: int
    reason: str
    reference_id: UUID | None
    created_at: datetime
