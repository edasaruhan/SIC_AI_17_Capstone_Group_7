from datetime import UTC, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.platform.db import get_engine, set_context
from conftest import auth_headers, identifier
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session
from test_commerce import setup_sale


def test_empty_analytics_are_honest(client: TestClient, tenants: dict) -> None:
    headers = auth_headers(tenants["a"])
    result = client.get("/api/v1/analytics/overview", headers=headers).json()
    assert Decimal(result["net_revenue"]) == 0
    assert result["average_order_value"] is None
    assert result["roas"] is None and result["ad_spend"] is None
    assert result["evidence"] == "synthetic_demo"
    assert len(result["daily"]) == 30
    customer, _ = setup_sale(client, tenants["a"])
    summary = client.get(f"/api/v1/analytics/customers/{customer}", headers=headers).json()
    assert summary["recency_days"] is None and summary["churn_probability"] is None
    assert summary["segment"] == "no_purchase"
    assert (
        client.get(
            "/api/v1/analytics/overview?start=2020-01-01&end=2025-01-01", headers=headers
        ).status_code
        == 422
    )


def test_refunds_post_in_refund_period_not_sale_period(client: TestClient, tenants: dict) -> None:
    tenant = tenants["a"]
    headers = auth_headers(tenant)
    customer, product = setup_sale(client, tenant)
    yesterday = datetime.now(ZoneInfo("Europe/Istanbul")) - timedelta(days=1)
    response = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "customer_id": customer,
            "placed_at": yesterday.isoformat(),
            "items": [{"product_id": product, "quantity": 2, "unit_discount": "0.50"}],
            "idempotency_key": "historical-sale",
        },
    )
    assert response.status_code == 201, response.text
    order = response.json()
    returned = client.post(
        f"/api/v1/orders/{order['id']}/refunds",
        headers=headers,
        json={
            "order_item_id": order["items"][0]["id"],
            "quantity": 1,
            "restock": True,
            "reason": "Synthetic return",
            "idempotency_key": "refund-today",
        },
    )
    assert returned.status_code == 201, returned.text
    sale_day = yesterday.date().isoformat()
    result = client.get(
        f"/api/v1/analytics/overview?start={sale_day}&end={sale_day}", headers=headers
    ).json()
    assert Decimal(result["net_revenue"]) == Decimal("24.00")
    assert Decimal(result["refunds"]) == 0 and result["orders"] == 1
    today = datetime.now(ZoneInfo("Europe/Istanbul")).date().isoformat()
    result = client.get(
        f"/api/v1/analytics/overview?start={today}&end={today}", headers=headers
    ).json()
    assert Decimal(result["net_revenue"]) == Decimal("-12.00")
    assert result["orders"] == 0 and result["average_order_value"] is None
    summary = client.get(
        f"/api/v1/analytics/customers/{customer}?as_of={sale_day}", headers=headers
    ).json()
    assert Decimal(summary["monetary"]) == 24
    current = client.get(f"/api/v1/analytics/customers/{customer}", headers=headers).json()
    assert Decimal(current["monetary"]) == 12
    assert current["frequency"] == 1 and current["recency_days"] == 1
    ranked = client.get("/api/v1/analytics/products", headers=headers).json()
    assert ranked[0]["sold_units"] == 2 and ranked[0]["returned_units"] == 1
    assert Decimal(ranked[0]["net_revenue"]) == 12
    cohort = client.get("/api/v1/analytics/cohorts", headers=headers).json()
    assert cohort[0]["customers"] == cohort[0]["cohort_size"] == 1
    assert Decimal(cohort[0]["active_share"]) == 1
    assert (
        client.get(
            f"/api/v1/analytics/customers/{customer}", headers=auth_headers(tenants["b"])
        ).status_code
        == 404
    )
    assert (
        Decimal(
            client.get("/api/v1/analytics/overview", headers=auth_headers(tenants["b"])).json()[
                "net_revenue"
            ]
        )
        == 0
    )
    with Session(get_engine()) as session, session.begin():
        set_context(
            session,
            actor_id=identifier(tenants["b"]["actor"]),
            tenant_id=identifier(tenants["b"]["tenant"]),
        )
        assert session.execute(text("SELECT * FROM analytics_revenue_v1")).all() == []


def test_calendar_day_uses_organization_timezone(client: TestClient, tenants: dict) -> None:
    headers = auth_headers(tenants["a"])
    customer, product = setup_sale(client, tenants["a"])
    # UTC 21:00 is the next day in Istanbul, including historical queries.
    utc_boundary = (datetime.now(UTC) - timedelta(days=3)).replace(
        hour=21, minute=0, second=0, microsecond=0
    )
    for key, timestamp in (
        ("before", utc_boundary - timedelta(seconds=1)),
        ("after", utc_boundary),
    ):
        response = client.post(
            "/api/v1/orders",
            headers=headers,
            json={
                "customer_id": customer,
                "placed_at": timestamp.isoformat(),
                "items": [{"product_id": product, "quantity": 1}],
                "idempotency_key": key,
            },
        )
        assert response.status_code == 201, response.text
    next_day = utc_boundary.astimezone(ZoneInfo("Europe/Istanbul")).date().isoformat()
    result = client.get(
        f"/api/v1/analytics/overview?start={next_day}&end={next_day}", headers=headers
    ).json()
    assert result["orders"] == 1
    assert Decimal(result["sales"]) == Decimal("12.50")
