from datetime import UTC, datetime, timedelta

import pytest
from conftest import auth_headers
from fastapi.testclient import TestClient
from test_commerce import setup_sale

pytestmark = pytest.mark.integration


def create_order(
    client: TestClient, tenant: dict[str, object], customer: str, product: str
) -> dict:
    response = client.post(
        "/api/v1/orders",
        headers=auth_headers(tenant),
        json={
            "customer_id": customer,
            "placed_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
            "items": [{"product_id": product, "quantity": 1}],
            "idempotency_key": f"marketing-order-{customer}",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_last_touch_attribution_is_deterministic_and_noncausal(
    client: TestClient, tenants: dict[str, dict[str, object]]
) -> None:
    tenant = tenants["a"]
    customer, product = setup_sale(client, tenant)
    headers = auth_headers(tenant)
    touch = client.post(
        "/api/v1/marketing/touchpoints",
        headers=headers,
        json={
            "customer_id": customer,
            "occurred_at": (datetime.now(UTC) - timedelta(hours=2)).isoformat(),
            "source": "web",
            "utm_source": "project-test",
            "utm_campaign": "observed-only",
        },
    )
    assert touch.status_code == 201, touch.text
    order = create_order(client, tenant, customer, product)
    first = client.post(f"/api/v1/marketing/orders/{order['id']}/attribution", headers=headers)
    second = client.post(f"/api/v1/marketing/orders/{order['id']}/attribution", headers=headers)
    assert first.status_code == 201 and second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["method_version"] == "deterministic-last-touch-v1"
    assert first.json()["evidence"] == "first_party_observed"


def test_audience_snapshot_requires_explicit_latest_consent(
    client: TestClient, tenants: dict[str, dict[str, object]]
) -> None:
    tenant = tenants["a"]
    customer, product = setup_sale(client, tenant)
    headers = auth_headers(tenant)
    create_order(client, tenant, customer, product)
    consent = client.post(
        f"/api/v1/customers/{customer}/consents",
        headers=headers,
        json={"channel": "email", "granted": True, "source": "synthetic-test"},
    )
    assert consent.status_code == 201
    audience = client.post(
        "/api/v1/marketing/audiences",
        headers=headers,
        json={
            "name": f"Consented buyers {customer}",
            "rule": {"min_purchase_count": 1, "consent_channel": "email"},
        },
    )
    assert audience.status_code == 201, audience.text
    snapshot = client.post(
        f"/api/v1/marketing/audiences/{audience.json()['id']}/snapshots", headers=headers
    )
    assert snapshot.status_code == 201, snapshot.text
    assert snapshot.json()["member_count"] == 1
    assert snapshot.json()["evidence"] == "canonical_operational_data"


def test_campaign_needs_approval_and_kill_switch_blocks_queue(
    client: TestClient, tenants: dict[str, dict[str, object]]
) -> None:
    headers = auth_headers(tenants["a"])
    campaign = client.post(
        "/api/v1/marketing/campaigns",
        headers=headers,
        json={
            "name": "No live spend",
            "provider": "meta_ads",
            "budget": "10.00",
            "currency": "TRY",
        },
    )
    assert campaign.status_code == 201 and campaign.json()["status"] == "draft"
    campaign_id = campaign.json()["id"]
    pending = client.post(
        f"/api/v1/marketing/campaigns/{campaign_id}/transitions",
        headers=headers,
        json={
            "target": "pending_approval",
            "reason": "Ready for review",
            "idempotency_key": f"pending-{campaign_id}",
        },
    )
    assert pending.status_code == 200 and pending.json()["status"] == "pending_approval"
    approved = client.post(
        f"/api/v1/marketing/campaigns/{campaign_id}/transitions",
        headers=headers,
        json={
            "target": "approved",
            "reason": "Synthetic approval test",
            "idempotency_key": f"approve-{campaign_id}",
        },
    )
    assert approved.status_code == 200 and approved.json()["approved_at"]
    queued = client.post(
        f"/api/v1/marketing/campaigns/{campaign_id}/transitions",
        headers=headers,
        json={
            "target": "queued",
            "reason": "Must remain blocked",
            "idempotency_key": f"queue-{campaign_id}",
        },
    )
    assert queued.status_code == 409
    assert "kill switch" in queued.json()["detail"]
