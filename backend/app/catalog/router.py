from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.catalog import service
from app.catalog.models import Category, InventoryMovement, Product
from app.catalog.schemas import (
    CategoryCreate,
    CategoryRead,
    MovementRead,
    ProductCreate,
    ProductRead,
    StockAdjustment,
)
from app.identity.context import TenantContext, permitted
from app.identity.permissions import Permission
from app.platform.audit import record_event

router = APIRouter(prefix="/api/v1", tags=["Catalog & inventory"])


@router.get("/categories", response_model=list[CategoryRead])
def categories(ctx: TenantContext = Depends(permitted(Permission.READ))) -> list[CategoryRead]:
    rows = ctx.session.scalars(
        select(Category)
        .where(Category.tenant_id == ctx.tenant_id)
        .order_by(Category.name)
        .limit(500)
    )
    return [CategoryRead.model_validate(row) for row in rows]


@router.post("/categories", response_model=CategoryRead, status_code=201)
def category(
    payload: CategoryCreate, ctx: TenantContext = Depends(permitted(Permission.COMMERCE_WRITE))
) -> CategoryRead:
    record = Category(tenant_id=ctx.tenant_id, name=payload.name)
    ctx.session.add(record)
    ctx.session.flush()
    record_event(ctx, "category.created", record.id)
    return CategoryRead.model_validate(record)


@router.get("/products", response_model=list[ProductRead])
def products(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctx: TenantContext = Depends(permitted(Permission.READ)),
) -> list[ProductRead]:
    rows = ctx.session.scalars(
        select(Product)
        .where(Product.tenant_id == ctx.tenant_id)
        .order_by(Product.name, Product.id)
        .offset(offset)
        .limit(limit)
    )
    return [ProductRead.model_validate(row) for row in rows]


@router.post("/products", response_model=ProductRead, status_code=201)
def create_product(
    payload: ProductCreate, ctx: TenantContext = Depends(permitted(Permission.COMMERCE_WRITE))
) -> ProductRead:
    return ProductRead.model_validate(service.save_product(ctx, payload))


@router.put("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: UUID,
    payload: ProductCreate,
    ctx: TenantContext = Depends(permitted(Permission.COMMERCE_WRITE)),
) -> ProductRead:
    return ProductRead.model_validate(service.save_product(ctx, payload, product_id))


@router.post("/products/{product_id}/stock", response_model=ProductRead)
def adjust_stock(
    product_id: UUID,
    payload: StockAdjustment,
    ctx: TenantContext = Depends(permitted(Permission.COMMERCE_WRITE)),
) -> ProductRead:
    return ProductRead.model_validate(service.adjust_stock(ctx, product_id, payload))


@router.get("/inventory/movements", response_model=list[MovementRead])
def movements(
    limit: int = Query(100, ge=1, le=200), ctx: TenantContext = Depends(permitted(Permission.READ))
) -> list[MovementRead]:
    rows = ctx.session.scalars(
        select(InventoryMovement)
        .where(InventoryMovement.tenant_id == ctx.tenant_id)
        .order_by(InventoryMovement.created_at.desc())
        .limit(limit)
    )
    return [MovementRead.model_validate(row) for row in rows]
