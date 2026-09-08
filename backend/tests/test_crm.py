from uuid import uuid4

import pytest
from app.platform.db import get_engine, set_context
from conftest import auth_headers, identifier
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration


def test_customer_profile_search_edit_and_consent(client: TestClient, tenants: dict) -> None:
    headers = auth_headers(tenants["a"])
    customer = {"name": "Synthetic Ada", "email": "Ada@Example.test", "tags": ["loyal", "loyal"]}
    created = client.post("/api/v1/customers", json=customer, headers=headers)
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["email"] == "ada@example.test"
    assert payload["tags"] == ["loyal"]
    customer_id = payload["id"]
    found = client.get("/api/v1/customers?search=ada&tag=loyal", headers=headers).json()
    assert found["total"] == 1
    assert found["items"][0]["id"] == customer_id
    updated = client.put(
        f"/api/v1/customers/{customer_id}", headers=headers, json={**customer, "status": "inactive"}
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "inactive"
    path = f"/api/v1/customers/{customer_id}"
    assert (
        client.post(
            f"{path}/interactions",
            headers=headers,
            json={"kind": "note", "body": "Synthetic call follow-up"},
        ).status_code
        == 201
    )
    assert len(client.get(f"{path}/interactions", headers=headers).json()) == 1
    for granted in (True, False):
        response = client.post(
            f"{path}/consents",
            headers=headers,
            json={"channel": "email", "granted": granted, "source": "synthetic-test"},
        )
        assert response.status_code == 201
    consents = client.get(f"{path}/consents", headers=headers).json()
    assert len(consents) == 2 and consents[0]["granted"] is False


def test_customer_isolation_and_analyst_denial(client: TestClient, tenants: dict) -> None:
    created = client.post(
        "/api/v1/customers",
        json={"name": "Synthetic private customer"},
        headers=auth_headers(tenants["a"]),
    )
    assert created.status_code == 201
    identifier = created.json()["id"]
    other_headers = auth_headers(tenants["b"])
    assert client.get("/api/v1/customers", headers=other_headers).json()["total"] == 0
    assert client.get(f"/api/v1/customers/{identifier}", headers=other_headers).status_code == 404
    assert (
        client.post(
            f"/api/v1/customers/{identifier}/interactions",
            headers=other_headers,
            json={"body": "Must not be persisted"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/customers", json={"name": "Denied"}, headers=auth_headers(tenants["analyst"])
        ).status_code
        == 403
    )


def test_rls_blocks_inserts_and_cross_tenant_references(client: TestClient, tenants: dict) -> None:
    created = client.post(
        "/api/v1/customers",
        headers=auth_headers(tenants["b"]),
        json={"name": "Synthetic foreign customer"},
    ).json()
    with Session(get_engine()) as session:
        set_context(
            session,
            actor_id=identifier(tenants["a"]["actor"]),
            tenant_id=identifier(tenants["a"]["tenant"]),
        )
        with pytest.raises(DBAPIError):
            session.execute(
                text("INSERT INTO customers(id,tenant_id,name) VALUES (:id,:tenant,'Blocked')"),
                {"id": uuid4(), "tenant": tenants["b"]["tenant"]},
            )
        session.rollback()
        set_context(
            session,
            actor_id=identifier(tenants["a"]["actor"]),
            tenant_id=identifier(tenants["a"]["tenant"]),
        )
        with pytest.raises(DBAPIError):
            session.execute(
                text(
                    "INSERT INTO customer_interactions"
                    "(id,tenant_id,customer_id,kind,body,actor_id) "
                    "VALUES (:id,:tenant,:customer,'note','Blocked',:actor)"
                ),
                {
                    "id": uuid4(),
                    "tenant": tenants["a"]["tenant"],
                    "customer": created["id"],
                    "actor": tenants["a"]["actor"],
                },
            )


def test_audit_is_append_only_and_duplicate_transaction_is_atomic(
    client: TestClient, tenants: dict
) -> None:
    headers = auth_headers(tenants["a"])
    payload = {"name": "Synthetic customer", "external_id": "test-source-1"}
    assert client.post("/api/v1/customers", headers=headers, json=payload).status_code == 201
    assert client.post("/api/v1/customers", headers=headers, json=payload).status_code == 409
    with Session(get_engine()) as session:
        set_context(
            session,
            actor_id=identifier(tenants["a"]["actor"]),
            tenant_id=identifier(tenants["a"]["tenant"]),
        )
        assert session.scalar(text("SELECT count(*) FROM audit_events")) == 1
        assert session.scalar(text("SELECT count(*) FROM outbox_events")) == 1
        with pytest.raises(DBAPIError):
            session.execute(text("UPDATE audit_events SET event_type='tampered'"))
