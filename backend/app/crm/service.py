from uuid import UUID

from sqlalchemy import func, or_, select

from app.crm.models import Customer, Interaction, MarketingConsent
from app.crm.schemas import (
    ConsentCreate,
    CustomerCreate,
    CustomerPage,
    CustomerRead,
    InteractionCreate,
)
from app.identity.context import TenantContext
from app.platform.audit import record_event
from app.platform.errors import DomainError


def get_customer(ctx: TenantContext, customer_id: UUID) -> Customer:
    result = ctx.session.scalar(
        select(Customer).where(Customer.id == customer_id, Customer.tenant_id == ctx.tenant_id)
    )
    if result is None:
        raise DomainError("Customer not found", 404)
    return result


def list_customers(
    ctx: TenantContext,
    search: str,
    limit: int,
    offset: int,
    status: str | None = None,
    tag: str | None = None,
) -> CustomerPage:
    query = select(Customer).where(Customer.tenant_id == ctx.tenant_id)
    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.where(
            or_(Customer.name.ilike(f"%{escaped}%"), Customer.email.ilike(f"%{escaped}%"))
        )
    if status:
        query = query.where(Customer.status == status)
    if tag:
        query = query.where(Customer.tags.contains([tag]))
    count = ctx.session.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = ctx.session.scalars(
        query.order_by(Customer.created_at.desc(), Customer.id).offset(offset).limit(limit)
    )
    return CustomerPage(
        items=[CustomerRead.model_validate(row) for row in rows],
        total=count,
        limit=limit,
        offset=offset,
    )


def save_customer(
    ctx: TenantContext, payload: CustomerCreate, customer_id: UUID | None = None
) -> Customer:
    if customer_id:
        customer = get_customer(ctx, customer_id)
        for key, value in payload.model_dump().items():
            setattr(customer, key, value)
    else:
        customer = Customer(tenant_id=ctx.tenant_id, **payload.model_dump())
        ctx.session.add(customer)
    ctx.session.flush()
    record_event(ctx, "customer.updated" if customer_id else "customer.created", customer.id)
    return customer


def add_interaction(
    ctx: TenantContext, customer_id: UUID, payload: InteractionCreate
) -> Interaction:
    get_customer(ctx, customer_id)
    event = Interaction(
        tenant_id=ctx.tenant_id,
        customer_id=customer_id,
        actor_id=ctx.actor_id,
        **payload.model_dump(),
    )
    ctx.session.add(event)
    ctx.session.flush()
    record_event(ctx, "customer.interaction_created", customer_id)
    return event


def add_consent(ctx: TenantContext, customer_id: UUID, payload: ConsentCreate) -> MarketingConsent:
    get_customer(ctx, customer_id)
    consent = MarketingConsent(
        tenant_id=ctx.tenant_id,
        customer_id=customer_id,
        actor_id=ctx.actor_id,
        **payload.model_dump(),
    )
    ctx.session.add(consent)
    ctx.session.flush()
    record_event(
        ctx,
        "customer.consent_recorded",
        customer_id,
        {"channel": payload.channel, "granted": payload.granted},
    )
    return consent
