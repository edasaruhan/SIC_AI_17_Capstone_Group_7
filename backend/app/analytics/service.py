from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import func, select, text

from app.analytics.schemas import (
    CohortCell,
    CustomerSummary,
    Overview,
    ProductPerformance,
    RevenueDay,
)
from app.catalog.models import Product
from app.commerce.models import Order
from app.crm.models import Customer
from app.crm.service import get_customer
from app.identity.context import TenantContext
from app.identity.models import Organization
from app.platform.errors import DomainError


def period(
    ctx: TenantContext, start: date | None, end: date | None
) -> tuple[Organization, date, date, datetime, datetime]:
    org = ctx.session.get(Organization, ctx.tenant_id)
    assert org
    zone = ZoneInfo(org.timezone)
    end = end or datetime.now(zone).date()
    start = start or end - timedelta(days=29)
    if start > end or (end - start).days > 365:
        raise DomainError("Use an ordered range of at most 366 calendar days")
    return (
        org,
        start,
        end,
        datetime.combine(start, time.min, zone).astimezone(UTC),
        datetime.combine(end + timedelta(days=1), time.min, zone).astimezone(UTC),
    )


def overview(ctx: TenantContext, start: date | None, end: date | None) -> Overview:
    org, first, last, since, until = period(ctx, start, end)
    parameters = {"tenant": ctx.tenant_id, "since": since, "until": until, "zone": org.timezone}
    rows = ctx.session.execute(
        text("""
      SELECT (occurred_at AT TIME ZONE :zone)::date AS day,
        COALESCE(sum(amount) FILTER (WHERE kind='sale'),0) AS sales,
        -COALESCE(sum(amount) FILTER (WHERE kind='refund'),0) AS refunds,
        sum(amount) AS net_revenue
      FROM analytics_revenue_v1
      WHERE tenant_id=:tenant AND occurred_at>=:since AND occurred_at<:until
      GROUP BY day ORDER BY day
    """),
        parameters,
    ).mappings()
    by_date = {
        row["day"]: RevenueDay(
            date=row["day"],
            sales=row["sales"],
            refunds=row["refunds"],
            net_revenue=row["net_revenue"],
        )
        for row in rows
    }
    daily = [
        by_date.get(
            day, RevenueDay(date=day, sales=Decimal(0), refunds=Decimal(0), net_revenue=Decimal(0))
        )
        for day in (first + timedelta(days=i) for i in range((last - first).days + 1))
    ]
    sales = sum((day.sales for day in daily), Decimal(0))
    refunds = sum((day.refunds for day in daily), Decimal(0))
    orders, buyers = ctx.session.execute(
        select(func.count(Order.id), func.count(func.distinct(Order.customer_id))).where(
            Order.tenant_id == ctx.tenant_id, Order.placed_at >= since, Order.placed_at < until
        )
    ).one()
    customers = (
        ctx.session.scalar(
            select(func.count(Customer.id)).where(Customer.tenant_id == ctx.tenant_id)
        )
        or 0
    )
    products, low_stock = ctx.session.execute(
        select(
            func.count(Product.id), func.count(Product.id).filter(Product.stock_on_hand <= 5)
        ).where(Product.tenant_id == ctx.tenant_id, Product.active.is_(True))
    ).one()
    return Overview(
        start=first,
        end=last,
        timezone=org.timezone,
        currency=org.currency,
        generated_at=datetime.now(UTC),
        evidence="synthetic_demo" if org.is_demo else "canonical_operational_data",
        sales=sales,
        refunds=refunds,
        net_revenue=sales - refunds,
        orders=orders,
        buyers=buyers,
        average_order_value=(sales / orders).quantize(Decimal("0.01")) if orders else None,
        customers=customers,
        products=products,
        low_stock_products=low_stock,
        availability_notes=[
            "Advertising spend/ROAS require verified provider data",
            "Current customer/stock counts are not historical snapshots",
            "Sales are discounted totals; refunds post on return date",
            "Tax and shipping are not modeled",
        ],
        daily=daily,
    )


def customer_summary(ctx: TenantContext, customer_id: UUID, as_of: date | None) -> CustomerSummary:
    get_customer(ctx, customer_id)
    org, _, cutoff, _, until = period(ctx, as_of, as_of)
    count, first, last = ctx.session.execute(
        select(func.count(Order.id), func.min(Order.placed_at), func.max(Order.placed_at)).where(
            Order.tenant_id == ctx.tenant_id,
            Order.customer_id == customer_id,
            Order.placed_at < until,
            Order.total > 0,
        )
    ).one()
    monetary = ctx.session.execute(
        text("""
        SELECT COALESCE(sum(amount),0) FROM analytics_revenue_v1
        WHERE tenant_id=:tenant AND customer_id=:customer AND occurred_at<:until
    """),
        {"tenant": ctx.tenant_id, "customer": customer_id, "until": until},
    ).scalar_one()
    return CustomerSummary(
        customer_id=customer_id,
        as_of=cutoff,
        currency=org.currency,
        recency_days=(cutoff - last.astimezone(ZoneInfo(org.timezone)).date()).days
        if last
        else None,
        frequency=count,
        monetary=monetary,
        first_purchase=first,
        last_purchase=last,
        segment="no_purchase" if not count else "one_time" if count == 1 else "repeat",
    )


def cohorts(ctx: TenantContext, start: date | None, end: date | None) -> list[CohortCell]:
    org, _, _, since, until = period(ctx, start, end)
    rows = ctx.session.execute(
        text("""
      WITH firsts AS (
        SELECT customer_id, date_trunc('month',min(placed_at) AT TIME ZONE :zone)::date AS cohort
        FROM orders WHERE tenant_id=:tenant AND placed_at<:until AND total>0 GROUP BY customer_id
      ), sizes AS (
        SELECT cohort,count(*) AS cohort_size FROM firsts GROUP BY cohort
      )
      SELECT f.cohort, date_trunc('month',o.placed_at AT TIME ZONE :zone)::date AS activity_month,
        count(DISTINCT o.customer_id) AS customers, s.cohort_size,
        count(DISTINCT o.customer_id)::numeric/s.cohort_size AS active_share
      FROM orders o JOIN firsts f ON f.customer_id=o.customer_id JOIN sizes s ON s.cohort=f.cohort
      WHERE o.tenant_id=:tenant AND o.placed_at>=:since AND o.placed_at<:until AND o.total>0
      GROUP BY f.cohort,activity_month,s.cohort_size ORDER BY f.cohort,activity_month
    """),
        {"tenant": ctx.tenant_id, "zone": org.timezone, "since": since, "until": until},
    ).mappings()
    return [CohortCell.model_validate(dict(row)) for row in rows]


def product_performance(
    ctx: TenantContext, start: date | None, end: date | None
) -> list[ProductPerformance]:
    _, _, _, since, until = period(ctx, start, end)
    rows = ctx.session.execute(
        text("""
      WITH facts AS (
        SELECT i.product_id,i.quantity AS sold_units,0 AS returned_units,i.line_total AS amount
        FROM order_items i JOIN orders o ON o.tenant_id=i.tenant_id AND o.id=i.order_id
        WHERE i.tenant_id=:tenant AND o.placed_at>=:since AND o.placed_at<:until
        UNION ALL
        SELECT i.product_id,0,r.quantity,-r.amount
        FROM refunds r JOIN order_items i ON i.tenant_id=r.tenant_id AND i.id=r.order_item_id
        WHERE r.tenant_id=:tenant AND r.created_at>=:since AND r.created_at<:until
      )
      SELECT p.id AS product_id,p.name,sum(f.sold_units) AS sold_units,
        sum(f.returned_units) AS returned_units,sum(f.amount) AS net_revenue
      FROM facts f JOIN products p ON p.id=f.product_id AND p.tenant_id=:tenant
      GROUP BY p.id,p.name ORDER BY net_revenue DESC,p.id LIMIT 50
    """),
        {"tenant": ctx.tenant_id, "since": since, "until": until},
    ).mappings()
    return [ProductPerformance.model_validate(dict(row)) for row in rows]
