from uuid import UUID

from sqlalchemy import select

from app.catalog.models import Category, InventoryMovement, Product
from app.catalog.schemas import ProductCreate, StockAdjustment
from app.identity.context import TenantContext
from app.identity.models import Organization
from app.platform.audit import record_event
from app.platform.errors import DomainError
from app.platform.idempotency import serialize_key


def get_product(ctx: TenantContext, product_id: UUID, *, lock: bool = False) -> Product:
    query = select(Product).where(Product.id == product_id, Product.tenant_id == ctx.tenant_id)
    if lock:
        query = query.with_for_update()
    product = ctx.session.scalar(query)
    if product is None:
        raise DomainError("Product not found", 404)
    return product


def save_product(
    ctx: TenantContext, payload: ProductCreate, product_id: UUID | None = None
) -> Product:
    organization = ctx.session.get(Organization, ctx.tenant_id)
    assert organization
    if payload.currency != organization.currency:
        raise DomainError("Product currency must match the organization currency")
    if payload.category_id and not ctx.session.scalar(
        select(Category).where(
            Category.id == payload.category_id, Category.tenant_id == ctx.tenant_id
        )
    ):
        raise DomainError("Category not found", 404)
    if product_id:
        product = get_product(ctx, product_id, lock=True)
        for key, value in payload.model_dump().items():
            setattr(product, key, value)
    else:
        product = Product(tenant_id=ctx.tenant_id, **payload.model_dump())
        ctx.session.add(product)
    ctx.session.flush()
    record_event(ctx, "product.updated" if product_id else "product.created", product.id)
    return product


def adjust_stock(ctx: TenantContext, product_id: UUID, payload: StockAdjustment) -> Product:
    if payload.quantity_delta == 0:
        raise DomainError("Stock adjustment must be non-zero")
    key = f"adjustment:{payload.idempotency_key}"
    serialize_key(ctx.session, str(ctx.tenant_id), key)
    existing = ctx.session.scalar(
        select(InventoryMovement).where(
            InventoryMovement.tenant_id == ctx.tenant_id, InventoryMovement.idempotency_key == key
        )
    )
    if existing:
        if (existing.product_id, existing.quantity_delta, existing.reason) != (
            product_id,
            payload.quantity_delta,
            payload.reason,
        ):
            raise DomainError("Idempotency key already used for another adjustment", 409)
        return get_product(ctx, product_id)
    product = get_product(ctx, product_id, lock=True)
    if product.stock_on_hand + payload.quantity_delta < 0:
        raise DomainError("Insufficient stock", 409)
    product.stock_on_hand += payload.quantity_delta
    ctx.session.add(
        InventoryMovement(
            tenant_id=ctx.tenant_id,
            product_id=product_id,
            quantity_delta=payload.quantity_delta,
            reason=payload.reason,
            idempotency_key=key,
            reference_id=None,
        )
    )
    record_event(ctx, "inventory.adjusted", product_id, {"quantity_delta": payload.quantity_delta})
    ctx.session.flush()
    return product
