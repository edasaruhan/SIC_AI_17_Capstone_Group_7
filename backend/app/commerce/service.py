import hashlib
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select

from app.catalog.models import InventoryMovement
from app.catalog.service import get_product
from app.commerce.models import Order, OrderItem, Payment, Refund
from app.commerce.schemas import OrderCreate, OrderLineRead, OrderRead, PaymentCreate, RefundCreate
from app.crm.service import get_customer
from app.identity.context import TenantContext
from app.identity.models import Organization
from app.platform.audit import record_event
from app.platform.errors import DomainError
from app.platform.idempotency import serialize_key


def get_order(ctx: TenantContext, order_id: UUID, *, lock: bool = False) -> Order:
    query = select(Order).where(Order.tenant_id == ctx.tenant_id, Order.id == order_id)
    if lock:
        query = query.with_for_update()
    order = ctx.session.scalar(query)
    if not order:
        raise DomainError("Order not found", 404)
    return order


def order_view(ctx: TenantContext, order: Order) -> OrderRead:
    lines = ctx.session.scalars(
        select(OrderItem)
        .where(OrderItem.tenant_id == ctx.tenant_id, OrderItem.order_id == order.id)
        .order_by(OrderItem.id)
    )
    result = OrderRead.model_validate(order)
    result.items = [OrderLineRead.model_validate(item) for item in lines]
    return result


def create_order(ctx: TenantContext, payload: OrderCreate) -> Order:
    request_hash = hashlib.sha256(payload.model_dump_json().encode()).hexdigest()
    serialize_key(ctx.session, str(ctx.tenant_id), f"order:{payload.idempotency_key}")
    existing = ctx.session.scalar(
        select(Order).where(
            Order.tenant_id == ctx.tenant_id, Order.idempotency_key == payload.idempotency_key
        )
    )
    if existing:
        if existing.request_hash != request_hash:
            raise DomainError("Idempotency key already used for another order", 409)
        return existing
    get_customer(ctx, payload.customer_id)
    placed_at = payload.placed_at or datetime.now(UTC)
    if placed_at > datetime.now(UTC):
        raise DomainError("Order date must not be in the future")
    if len({line.product_id for line in payload.items}) != len(payload.items):
        raise DomainError("Combine duplicate products into a single order line")
    organization = ctx.session.get(Organization, ctx.tenant_id)
    assert organization
    order = Order(
        tenant_id=ctx.tenant_id,
        customer_id=payload.customer_id,
        placed_at=placed_at,
        currency=organization.currency,
        total=Decimal("0"),
        idempotency_key=payload.idempotency_key,
        request_hash=request_hash,
    )
    ctx.session.add(order)
    ctx.session.flush()
    # Stable row-lock order avoids deadlocks when two carts contain the same products.
    for line in sorted(payload.items, key=lambda item: str(item.product_id)):
        product = get_product(ctx, line.product_id, lock=True)
        if not product.active:
            raise DomainError("Inactive product cannot be sold", 409)
        if product.stock_on_hand < line.quantity:
            raise DomainError("Insufficient stock", 409)
        if line.unit_discount > product.unit_price:
            raise DomainError("Discount exceeds unit price")
        line_total = (product.unit_price - line.unit_discount) * line.quantity
        order.total += line_total
        if order.total > Decimal("999999999999.99"):
            raise DomainError("Order value exceeds supported monetary precision")
        product.stock_on_hand -= line.quantity
        ctx.session.add(
            OrderItem(
                tenant_id=ctx.tenant_id,
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                quantity=line.quantity,
                unit_price=product.unit_price,
                unit_discount=line.unit_discount,
                line_total=line_total,
            )
        )
        ctx.session.add(
            InventoryMovement(
                tenant_id=ctx.tenant_id,
                product_id=product.id,
                quantity_delta=-line.quantity,
                reason="sale",
                reference_id=order.id,
                idempotency_key=f"order:{order.id}:{product.id}",
            )
        )
    record_event(ctx, "order.created", order.id)
    ctx.session.flush()
    return order


def return_items(ctx: TenantContext, order_id: UUID, payload: RefundCreate) -> Refund:
    serialize_key(ctx.session, str(ctx.tenant_id), f"refund:{payload.idempotency_key}")
    existing = ctx.session.scalar(
        select(Refund).where(
            Refund.tenant_id == ctx.tenant_id, Refund.idempotency_key == payload.idempotency_key
        )
    )
    if existing:
        if (
            existing.order_id,
            existing.order_item_id,
            existing.quantity,
            existing.restock,
            existing.reason,
        ) != (order_id, payload.order_item_id, payload.quantity, payload.restock, payload.reason):
            raise DomainError("Idempotency key already used for another refund", 409)
        return existing
    order = get_order(ctx, order_id, lock=True)
    item = ctx.session.scalar(
        select(OrderItem)
        .where(
            OrderItem.tenant_id == ctx.tenant_id,
            OrderItem.id == payload.order_item_id,
            OrderItem.order_id == order_id,
        )
        .with_for_update()
    )
    if not item:
        raise DomainError("Order item not found", 404)
    if item.returned_quantity + payload.quantity > item.quantity:
        raise DomainError("Return quantity exceeds remaining sold quantity", 409)
    amount = (item.unit_price - item.unit_discount) * payload.quantity
    item.returned_quantity += payload.quantity
    order.refunded_total += amount
    remaining_quantity = ctx.session.scalar(
        select(func.sum(OrderItem.quantity - OrderItem.returned_quantity)).where(
            OrderItem.tenant_id == ctx.tenant_id, OrderItem.order_id == order_id
        )
    )
    order.status = "refunded" if remaining_quantity == 0 else "partially_refunded"
    refund = Refund(
        tenant_id=ctx.tenant_id, order_id=order_id, amount=amount, **payload.model_dump()
    )
    ctx.session.add(refund)
    ctx.session.flush()
    if payload.restock:
        product = get_product(ctx, item.product_id, lock=True)
        product.stock_on_hand += payload.quantity
        ctx.session.add(
            InventoryMovement(
                tenant_id=ctx.tenant_id,
                product_id=product.id,
                quantity_delta=payload.quantity,
                reason="return",
                reference_id=refund.id,
                idempotency_key=f"refund:{refund.id}",
            )
        )
    record_event(ctx, "order.refunded", order.id)
    ctx.session.flush()
    return refund


def record_payment(ctx: TenantContext, order_id: UUID, payload: PaymentCreate) -> Payment:
    serialize_key(ctx.session, str(ctx.tenant_id), f"payment:{payload.idempotency_key}")
    existing = ctx.session.scalar(
        select(Payment).where(
            Payment.tenant_id == ctx.tenant_id, Payment.idempotency_key == payload.idempotency_key
        )
    )
    if existing:
        if (existing.order_id, existing.amount, existing.method) != (
            order_id,
            payload.amount,
            payload.method,
        ):
            raise DomainError("Idempotency key already used for another payment", 409)
        return existing
    order = get_order(ctx, order_id, lock=True)
    paid = ctx.session.scalar(
        select(func.sum(Payment.amount)).where(
            Payment.tenant_id == ctx.tenant_id, Payment.order_id == order_id
        )
    ) or Decimal("0")
    if paid + payload.amount > order.total - order.refunded_total:
        raise DomainError("Payment exceeds outstanding order balance", 409)
    payment = Payment(tenant_id=ctx.tenant_id, order_id=order_id, **payload.model_dump())
    ctx.session.add(payment)
    ctx.session.flush()
    record_event(ctx, "payment.recorded", order_id)
    return payment
