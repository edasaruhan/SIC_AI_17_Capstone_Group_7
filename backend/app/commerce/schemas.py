from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class OrderLineCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_id: UUID
    quantity: int = Field(ge=1, le=100000)
    unit_discount: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)


class OrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: UUID
    placed_at: AwareDatetime | None = None
    items: list[OrderLineCreate] = Field(min_length=1, max_length=100)
    idempotency_key: str = Field(min_length=1, max_length=150)


class OrderLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    returned_quantity: int
    unit_price: Decimal
    unit_discount: Decimal
    line_total: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    customer_id: UUID
    placed_at: datetime
    currency: str
    total: Decimal
    refunded_total: Decimal
    status: str
    items: list[OrderLineRead] = []


class RefundCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order_item_id: UUID
    quantity: int = Field(ge=1, le=100000)
    restock: bool = True
    reason: str = Field(min_length=1, max_length=200)
    idempotency_key: str = Field(min_length=1, max_length=150)


class RefundRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    amount: Decimal
    quantity: int
    restock: bool


class PaymentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: Decimal = Field(gt=0, decimal_places=2)
    method: Literal["cash", "bank_transfer", "external_card"]
    idempotency_key: str = Field(min_length=1, max_length=150)
