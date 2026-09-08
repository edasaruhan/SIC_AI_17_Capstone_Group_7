from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends

from app.analytics.schemas import CohortCell, CustomerSummary, Overview, ProductPerformance
from app.analytics.service import cohorts, customer_summary, overview, product_performance
from app.identity.context import TenantContext, permitted
from app.identity.permissions import Permission

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/overview", response_model=Overview)
def dashboard(
    start: date | None = None,
    end: date | None = None,
    ctx: TenantContext = Depends(permitted(Permission.READ)),
) -> Overview:
    return overview(ctx, start, end)


@router.get("/customers/{customer_id}", response_model=CustomerSummary)
def customer(
    customer_id: UUID,
    as_of: date | None = None,
    ctx: TenantContext = Depends(permitted(Permission.READ)),
) -> CustomerSummary:
    return customer_summary(ctx, customer_id, as_of)


@router.get("/cohorts", response_model=list[CohortCell])
def retention(
    start: date | None = None,
    end: date | None = None,
    ctx: TenantContext = Depends(permitted(Permission.READ)),
) -> list[CohortCell]:
    return cohorts(ctx, start, end)


@router.get("/products", response_model=list[ProductPerformance])
def products(
    start: date | None = None,
    end: date | None = None,
    ctx: TenantContext = Depends(permitted(Permission.READ)),
) -> list[ProductPerformance]:
    return product_performance(ctx, start, end)
