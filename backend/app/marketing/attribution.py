import hashlib
import hmac
from datetime import timedelta
from uuid import UUID

from sqlalchemy import select

from app.commerce.models import Order
from app.crm.service import get_customer
from app.identity.context import TenantContext
from app.marketing.models import MarketingTouchpoint, OrderAttribution
from app.marketing.schemas import TouchpointCreate
from app.platform.audit import record_event
from app.platform.config import get_settings
from app.platform.errors import DomainError

METHOD_VERSION = "deterministic-last-touch-v1"


def protected_identifier(value: str) -> str:
    configured = get_settings().identifier_hmac_secret
    if configured is None:
        raise DomainError("Identifier protection secret is unavailable", 409)
    return hmac.new(
        configured.get_secret_value().encode(), value.encode(), hashlib.sha256
    ).hexdigest()


def record_touchpoint(ctx: TenantContext, payload: TouchpointCreate) -> MarketingTouchpoint:
    if payload.customer_id:
        get_customer(ctx, payload.customer_id)
    row = MarketingTouchpoint(
        tenant_id=ctx.tenant_id,
        customer_id=payload.customer_id,
        occurred_at=payload.occurred_at,
        source=payload.source,
        session_hash=protected_identifier(payload.session_identifier)
        if payload.session_identifier
        else None,
        click_hash=protected_identifier(payload.click_identifier)
        if payload.click_identifier
        else None,
        utm_source=payload.utm_source,
        utm_medium=payload.utm_medium,
        utm_campaign=payload.utm_campaign,
        external_campaign_id=payload.external_campaign_id,
    )
    ctx.session.add(row)
    ctx.session.flush()
    record_event(ctx, "attribution.touchpoint_recorded", row.id)
    return row


def attribute_order(ctx: TenantContext, order_id: UUID) -> OrderAttribution:
    existing = ctx.session.scalar(
        select(OrderAttribution).where(
            OrderAttribution.tenant_id == ctx.tenant_id,
            OrderAttribution.order_id == order_id,
            OrderAttribution.method_version == METHOD_VERSION,
        )
    )
    if existing:
        return existing
    order = ctx.session.scalar(
        select(Order).where(Order.tenant_id == ctx.tenant_id, Order.id == order_id)
    )
    if order is None:
        raise DomainError("Order not found", 404)
    touch = ctx.session.scalar(
        select(MarketingTouchpoint)
        .where(
            MarketingTouchpoint.tenant_id == ctx.tenant_id,
            MarketingTouchpoint.customer_id == order.customer_id,
            MarketingTouchpoint.occurred_at <= order.placed_at,
            MarketingTouchpoint.occurred_at >= order.placed_at - timedelta(days=30),
        )
        .order_by(MarketingTouchpoint.occurred_at.desc(), MarketingTouchpoint.id.desc())
        .limit(1)
    )
    if touch is None:
        raise DomainError("No eligible deterministic touchpoint was observed", 404)
    row = OrderAttribution(
        tenant_id=ctx.tenant_id,
        order_id=order.id,
        touchpoint_id=touch.id,
        method="deterministic_last_touch",
        method_version=METHOD_VERSION,
        evidence="first_party_observed",
        quality="exact_customer",
    )
    ctx.session.add(row)
    ctx.session.flush()
    record_event(ctx, "attribution.order_attributed", row.id, {"method": METHOD_VERSION})
    return row
