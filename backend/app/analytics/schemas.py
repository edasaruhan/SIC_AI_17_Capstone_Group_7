from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class RevenueDay(BaseModel):
    date: date
    sales: Decimal
    refunds: Decimal
    net_revenue: Decimal


class Overview(BaseModel):
    version: str = "kpi-v1"
    start: date
    end: date
    timezone: str
    currency: str
    generated_at: datetime
    evidence: str = "canonical_operational_data"
    sales: Decimal
    refunds: Decimal
    net_revenue: Decimal
    orders: int
    buyers: int
    average_order_value: Decimal | None
    customers: int
    products: int
    low_stock_products: int
    ad_spend: Decimal | None = None
    roas: Decimal | None = None
    availability_notes: list[str]
    daily: list[RevenueDay]


class CustomerSummary(BaseModel):
    customer_id: UUID
    as_of: date
    version: str = "rfm-v1"
    currency: str
    recency_days: int | None
    frequency: int
    monetary: Decimal
    first_purchase: datetime | None
    last_purchase: datetime | None
    segment: str
    churn_probability: float | None = None
    model_status: str = "not_scored"


class CohortCell(BaseModel):
    cohort: date
    activity_month: date
    customers: int
    cohort_size: int
    active_share: Decimal


class ProductPerformance(BaseModel):
    product_id: UUID
    name: str
    sold_units: int
    returned_units: int
    net_revenue: Decimal
