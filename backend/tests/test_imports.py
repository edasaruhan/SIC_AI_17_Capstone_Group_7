from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from app.identity.models import Membership
from app.platform.audit import OutboxEvent
from app.platform.db import get_engine, set_context
from app.platform.jobs import dispatch, process_event
from conftest import auth_headers, identifier
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session


def upload_csv(
    client: TestClient,
    tenant: dict[str, object],
    content: bytes,
    key: str = "source-v1",
    kind: str = "customers",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/imports",
        content=content,
        headers={
            **auth_headers(tenant),
            "X-File-Name": "source.csv",
            "X-Import-Kind": kind,
            "Idempotency-Key": key,
            "Content-Type": "application/octet-stream",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def drain(tenant: dict[str, object]) -> list[tuple[str, str]]:
    messages: list[tuple[str, str]] = []
    dispatch(identifier(tenant["tenant"]), lambda t, e: messages.append((t, e)))
    for t, e in messages:
        process_event(UUID(t), UUID(e))
    return messages


def test_import_mapping_preview_idempotent_commit(
    client: TestClient, tenants: dict[str, dict[str, object]]
) -> None:
    tenant = tenants["a"]
    headers = auth_headers(tenant)
    raw = (
        b"Full Name,ID,Email\nSynthetic One,C1,one@example.invalid\n"
        b"Synthetic Two,C2,two@example.invalid"
    )
    batch = upload_csv(client, tenant, raw)
    assert upload_csv(client, tenant, raw)["id"] == batch["id"]
    assert "object_id" not in batch and "source_rows" not in batch
    base = f"/api/v1/imports/{batch['id']}"
    assert client.get(base, headers=auth_headers(tenants["b"])).status_code == 404
    assert client.get(base, headers=auth_headers(tenants["analyst"])).status_code == 403
    assert client.post(base + "/commit", headers=headers).status_code == 409
    mapping = {"fields": {"name": "Full Name", "external_id": "ID", "email": "Email"}}
    response = client.put(base + "/mapping", headers=headers, json=mapping)
    assert response.json()["status"] == "validated", response.text
    assert client.get(base + "/preview", headers=headers).json()["total_rows"] == 2
    assert client.post(base + "/commit", headers=headers).json()["status"] == "queued"
    assert client.put(base + "/mapping", headers=headers, json=mapping).status_code == 409
    messages = drain(tenant)
    for t, e in messages:
        process_event(UUID(t), UUID(e))  # duplicate delivery after commit/ack loss
    assert client.get(base, headers=headers).json()["committed_count"] == 2
    assert client.get("/api/v1/customers", headers=headers).json()["total"] == 2
    assert client.post(base + "/commit", headers=headers).json()["status"] == "succeeded"


def test_row_errors_and_atomic_conflict(
    client: TestClient, tenants: dict[str, dict[str, object]]
) -> None:
    tenant = tenants["a"]
    headers = auth_headers(tenant)
    invalid = upload_csv(
        client, tenant, b"name,id,email\nOne,X,not-an-email\nTwo,X,two@example.invalid"
    )
    mapping = {"fields": {"name": "name", "external_id": "id", "email": "email"}}
    base = f"/api/v1/imports/{invalid['id']}"
    response = client.put(base + "/mapping", json=mapping, headers=headers)
    assert response.json()["status"] == "invalid"
    assert response.json()["errors"][0]["row"] == 2
    assert "not-an-email" not in str(response.json()["errors"])
    assert client.post(base + "/commit", headers=headers).status_code == 409
    valid = upload_csv(client, tenant, b"name,id\nOne,X1\nTwo,X2", key="second")
    base = f"/api/v1/imports/{valid['id']}"
    assert (
        client.put(
            base + "/mapping",
            json={"fields": {"name": "name", "external_id": "id"}},
            headers=headers,
        ).json()["status"]
        == "validated"
    )
    # Conflict is introduced AFTER preview. The earlier successful row must roll back.
    assert (
        client.post(
            "/api/v1/customers", json={"name": "Manual", "external_id": "X2"}, headers=headers
        ).status_code
        == 201
    )
    assert client.post(base + "/commit", headers=headers).status_code == 202
    drain(tenant)
    detail = client.get(base, headers=headers).json()
    assert detail["status"] == "failed" and detail["committed_count"] == 0
    assert client.get("/api/v1/customers", headers=headers).json()["total"] == 1


def test_products_and_permission_revocation(
    client: TestClient, tenants: dict[str, dict[str, object]]
) -> None:
    tenant = tenants["a"]
    headers = auth_headers(tenant)
    batch = upload_csv(client, tenant, b"sku,name,price\nSKU1,Product,12.50", kind="products")
    base = f"/api/v1/imports/{batch['id']}"
    mapping = {"fields": {"name": "name", "sku": "sku", "unit_price": "price"}}
    assert (
        client.put(base + "/mapping", json=mapping, headers=headers).json()["status"] == "validated"
    )
    client.post(base + "/commit", headers=headers)
    with Session(get_engine()) as session, session.begin():
        set_context(
            session, tenant_id=identifier(tenant["tenant"]), actor_id=identifier(tenant["actor"])
        )
        member = session.scalar(select(Membership).where(Membership.user_id == tenant["actor"]))
        assert member
        member.role = "ANALYST"
    drain(tenant)
    with Session(get_engine()) as session, session.begin():
        set_context(
            session, tenant_id=identifier(tenant["tenant"]), actor_id=identifier(tenant["actor"])
        )
        member = session.scalar(select(Membership).where(Membership.user_id == tenant["actor"]))
        assert member
        member.role = "OWNER"
    assert client.get(base, headers=headers).json()["errors"][0]["code"] == "authorization_revoked"
    assert client.get("/api/v1/products", headers=headers).json() == []
    # Revalidate after the permission is restored, then a new durable event succeeds.
    client.put(base + "/mapping", json=mapping, headers=headers)
    client.post(base + "/commit", headers=headers)
    drain(tenant)
    assert client.get(base, headers=headers).json()["status"] == "succeeded"


def test_broker_failure_is_durable_and_bounded(
    client: TestClient, tenants: dict[str, dict[str, object]]
) -> None:
    tenant = tenants["a"]
    headers = auth_headers(tenant)
    batch = upload_csv(client, tenant, b"name,id\nOne,X")
    base = f"/api/v1/imports/{batch['id']}"
    client.put(
        base + "/mapping", json={"fields": {"name": "name", "external_id": "id"}}, headers=headers
    )
    client.post(base + "/commit", headers=headers)

    def unavailable(t: str, e: str) -> None:
        raise ConnectionError("synthetic-secret-not-to-persist")

    for _ in range(6):
        dispatch(identifier(tenant["tenant"]), unavailable)
        with Session(get_engine()) as session, session.begin():
            set_context(
                session,
                tenant_id=identifier(tenant["tenant"]),
                actor_id=identifier(tenant["actor"]),
            )
            for event in session.scalars(select(OutboxEvent)):
                event.available_at = datetime.now(UTC) - timedelta(seconds=1)
                assert "synthetic-secret" not in (event.last_error or "")
    detail = client.get(base, headers=headers).json()
    assert detail["status"] == "failed"
    assert detail["errors"][0]["code"] == "delivery_exhausted"


@pytest.mark.parametrize("content", [b"name,id\nOne,X", b"a" * (5 * 1024 * 1024 + 1)])
def test_upload_key_collision_and_size(
    client: TestClient, tenants: dict[str, dict[str, object]], content: bytes
) -> None:
    upload_csv(client, tenants["a"], b"name,id\nOriginal,X")
    response = client.post(
        "/api/v1/imports",
        content=content,
        headers={
            **auth_headers(tenants["a"]),
            "X-File-Name": "source.csv",
            "X-Import-Kind": "customers",
            "Idempotency-Key": "source-v1",
        },
    )
    assert response.status_code == (413 if len(content) > 5 * 1024 * 1024 else 409)
