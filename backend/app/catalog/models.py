from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.db import Base
from app.platform.records import TenantRecord


class Category(TenantRecord, Base):
    __tablename__ = "product_categories"
    name: Mapped[str] = mapped_column(String(120))
    __table_args__ = (UniqueConstraint("tenant_id", "id"), UniqueConstraint("tenant_id", "name"))


class Product(TenantRecord, Base):
    __tablename__ = "products"
    sku: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(200))
    category_id: Mapped[UUID | None]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3))
    stock_on_hand: Mapped[int] = mapped_column(default=0)
    active: Mapped[bool] = mapped_column(default=True)
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "sku"),
        ForeignKeyConstraint(
            ["tenant_id", "category_id"], ["product_categories.tenant_id", "product_categories.id"]
        ),
    )


class InventoryMovement(TenantRecord, Base):
    __tablename__ = "inventory_movements"
    product_id: Mapped[UUID]
    quantity_delta: Mapped[int]
    reason: Mapped[str] = mapped_column(String(200))
    idempotency_key: Mapped[str] = mapped_column(String(200))
    reference_id: Mapped[UUID | None]
    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key"),
        ForeignKeyConstraint(["tenant_id", "product_id"], ["products.tenant_id", "products.id"]),
    )
