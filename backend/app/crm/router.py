from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.crm import service
from app.crm.models import Interaction, MarketingConsent
from app.crm.schemas import (
    ConsentCreate,
    ConsentRead,
    CustomerCreate,
    CustomerPage,
    CustomerRead,
    InteractionCreate,
    InteractionRead,
)
from app.identity.context import TenantContext, permitted
from app.identity.permissions import Permission

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


@router.get("", response_model=CustomerPage)
def customers(
    search: str = Query("", max_length=200),
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    status: str | None = None,
    tag: str | None = None,
    ctx: TenantContext = Depends(permitted(Permission.READ)),
) -> CustomerPage:
    return service.list_customers(ctx, search, limit, offset, status, tag)


@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(
    payload: CustomerCreate, ctx: TenantContext = Depends(permitted(Permission.CRM_WRITE))
) -> CustomerRead:
    return CustomerRead.model_validate(service.save_customer(ctx, payload))


@router.get("/{customer_id}", response_model=CustomerRead)
def customer(
    customer_id: UUID, ctx: TenantContext = Depends(permitted(Permission.READ))
) -> CustomerRead:
    return CustomerRead.model_validate(service.get_customer(ctx, customer_id))


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: UUID,
    payload: CustomerCreate,
    ctx: TenantContext = Depends(permitted(Permission.CRM_WRITE)),
) -> CustomerRead:
    return CustomerRead.model_validate(service.save_customer(ctx, payload, customer_id))


@router.post("/{customer_id}/interactions", response_model=InteractionRead, status_code=201)
def add_interaction(
    customer_id: UUID,
    payload: InteractionCreate,
    ctx: TenantContext = Depends(permitted(Permission.CRM_WRITE)),
) -> InteractionRead:
    return InteractionRead.model_validate(service.add_interaction(ctx, customer_id, payload))


@router.get("/{customer_id}/interactions", response_model=list[InteractionRead])
def interactions(
    customer_id: UUID, ctx: TenantContext = Depends(permitted(Permission.READ))
) -> list[InteractionRead]:
    service.get_customer(ctx, customer_id)
    rows = ctx.session.scalars(
        select(Interaction)
        .where(Interaction.tenant_id == ctx.tenant_id, Interaction.customer_id == customer_id)
        .order_by(Interaction.created_at.desc())
        .limit(100)
    )
    return [InteractionRead.model_validate(row) for row in rows]


@router.post("/{customer_id}/consents", response_model=ConsentRead, status_code=201)
def consent(
    customer_id: UUID,
    payload: ConsentCreate,
    ctx: TenantContext = Depends(permitted(Permission.CRM_WRITE)),
) -> ConsentRead:
    return ConsentRead.model_validate(service.add_consent(ctx, customer_id, payload))


@router.get("/{customer_id}/consents", response_model=list[ConsentRead])
def consents(
    customer_id: UUID, ctx: TenantContext = Depends(permitted(Permission.READ))
) -> list[ConsentRead]:
    service.get_customer(ctx, customer_id)
    rows = ctx.session.scalars(
        select(MarketingConsent)
        .where(
            MarketingConsent.tenant_id == ctx.tenant_id, MarketingConsent.customer_id == customer_id
        )
        .order_by(MarketingConsent.created_at.desc())
        .limit(100)
    )
    return [ConsentRead.model_validate(row) for row in rows]
