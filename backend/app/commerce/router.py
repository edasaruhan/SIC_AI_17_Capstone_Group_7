from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.commerce import service
from app.commerce.models import Order
from app.commerce.schemas import OrderCreate, OrderRead, PaymentCreate, RefundCreate, RefundRead
from app.identity.context import TenantContext, permitted
from app.identity.permissions import Permission

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


@router.get("", response_model=list[OrderRead])
def orders(
    customer_id: UUID | None = None,
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ctx: TenantContext = Depends(permitted(Permission.READ)),
) -> list[OrderRead]:
    query = select(Order).where(Order.tenant_id == ctx.tenant_id)
    if customer_id:
        query = query.where(Order.customer_id == customer_id)
    rows = ctx.session.scalars(
        query.order_by(Order.placed_at.desc(), Order.id).limit(limit).offset(offset)
    )
    return [service.order_view(ctx, order) for order in rows]


@router.post("", response_model=OrderRead, status_code=201)
def create_order(
    payload: OrderCreate, ctx: TenantContext = Depends(permitted(Permission.COMMERCE_WRITE))
) -> OrderRead:
    return service.order_view(ctx, service.create_order(ctx, payload))


@router.get("/{order_id}", response_model=OrderRead)
def order(order_id: UUID, ctx: TenantContext = Depends(permitted(Permission.READ))) -> OrderRead:
    return service.order_view(ctx, service.get_order(ctx, order_id))


@router.post("/{order_id}/refunds", response_model=RefundRead, status_code=201)
def refund(
    order_id: UUID,
    payload: RefundCreate,
    ctx: TenantContext = Depends(permitted(Permission.COMMERCE_WRITE)),
) -> RefundRead:
    return RefundRead.model_validate(service.return_items(ctx, order_id, payload))


@router.post("/{order_id}/payments", status_code=201)
def payment(
    order_id: UUID,
    payload: PaymentCreate,
    ctx: TenantContext = Depends(permitted(Permission.COMMERCE_WRITE)),
) -> dict[str, str]:
    record = service.record_payment(ctx, order_id, payload)
    return {"id": str(record.id), "amount": str(record.amount), "method": record.method}
