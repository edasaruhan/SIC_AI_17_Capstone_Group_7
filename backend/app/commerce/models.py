from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKeyConstraint, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.db import Base
from app.platform.records import TenantRecord


class Order(TenantRecord, Base):
    __tablename__ = "orders"
    customer_id: Mapped[UUID]
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    currency: Mapped[str] = mapped_column(String(3))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    refunded_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    status: Mapped[str] = mapped_column(String(24), default="placed")
    idempotency_key: Mapped[str] = mapped_column(String(150))
    request_hash: Mapped[str] = mapped_column(String(64))
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        ForeignKeyConstraint(["tenant_id", "customer_id"], ["customers.tenant_id", "customers.id"]),
    )


class OrderItem(TenantRecord, Base):
    __tablename__ = "order_items"
    order_id: Mapped[UUID]
    product_id: Mapped[UUID]
    product_name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[int]
    returned_quantity: Mapped[int] = mapped_column(default=0)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    unit_discount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    line_total: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        ForeignKeyConstraint(["tenant_id", "order_id"], ["orders.tenant_id", "orders.id"]),
        ForeignKeyConstraint(["tenant_id", "product_id"], ["products.tenant_id", "products.id"]),
    )


class Refund(TenantRecord, Base):
    __tablename__ = "refunds"
    order_id: Mapped[UUID]
    order_item_id: Mapped[UUID]
    quantity: Mapped[int]
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    restock: Mapped[bool]
    reason: Mapped[str] = mapped_column(String(200))
    idempotency_key: Mapped[str] = mapped_column(String(150))
    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key"),
        ForeignKeyConstraint(["tenant_id", "order_id"], ["orders.tenant_id", "orders.id"]),
        ForeignKeyConstraint(
            ["tenant_id", "order_item_id"], ["order_items.tenant_id", "order_items.id"]
        ),
    )


class Payment(TenantRecord, Base):
    __tablename__ = "payments"
    order_id: Mapped[UUID]
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    method: Mapped[str] = mapped_column(String(24))
    idempotency_key: Mapped[str] = mapped_column(String(150))
    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key"),
        ForeignKeyConstraint(["tenant_id", "order_id"], ["orders.tenant_id", "orders.id"]),
    )
