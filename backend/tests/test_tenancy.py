from datetime import UTC, datetime, timedelta

import jwt
import pytest
from app.identity.models import Membership, Organization
from app.platform.config import get_settings
from app.platform.db import get_engine, set_context, verify_runtime_role
from conftest import auth_headers, identifier
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration


def test_membership_controls_tenant_selection(client: TestClient, tenants: dict) -> None:
    headers = auth_headers(tenants["a"])
    response = client.get("/api/v1/workspace", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(tenants["a"]["tenant"])
    headers["X-Organization-ID"] = str(tenants["b"]["tenant"])
    assert client.get("/api/v1/workspace", headers=headers).status_code == 403


def test_rls_protects_unfiltered_sql_and_pool_reuse(tenants: dict) -> None:
    with Session(get_engine()) as session:
        verify_runtime_role(session)
        assert session.scalars(select(Organization)).all() == []
        set_context(
            session,
            actor_id=identifier(tenants["a"]["actor"]),
            tenant_id=identifier(tenants["a"]["tenant"]),
        )
        rows = session.execute(text("SELECT id FROM organizations")).scalars().all()
        assert rows == [tenants["a"]["tenant"]]
        session.commit()
        assert session.execute(text("SELECT id FROM organizations")).all() == []


def test_runtime_has_no_ddl_or_rls_bypass(tenants: dict) -> None:
    with Session(get_engine()) as session:
        with pytest.raises(DBAPIError):
            session.execute(text("CREATE TABLE forbidden_schema_change(id integer)"))


def test_expired_wrong_audience_and_forged_tokens(client: TestClient, tenants: dict) -> None:
    settings = get_settings()
    assert settings.dev_signing_secret
    base = {
        "iss": "growthpilot-local",
        "sub": tenants["a"]["subject"],
        "aud": "growthpilot-api",
        "iat": datetime.now(UTC) - timedelta(hours=2),
        "exp": datetime.now(UTC) - timedelta(hours=1),
    }
    expired = jwt.encode(base, settings.dev_signing_secret.get_secret_value(), algorithm="HS256")
    wrong_audience = jwt.encode(
        {**base, "exp": datetime.now(UTC) + timedelta(hours=1), "aud": "other-api"},
        settings.dev_signing_secret.get_secret_value(),
        algorithm="HS256",
    )
    for token in (expired, wrong_audience, "forged.token.value"):
        headers = {**auth_headers(tenants["a"]), "Authorization": f"Bearer {token}"}
        assert client.get("/api/v1/workspace", headers=headers).status_code == 401
    assert client.get("/api/v1/workspace").status_code == 401


def test_readiness_and_safe_validation(client: TestClient, tenants: dict) -> None:
    assert client.get("/health/ready").status_code == 200
    response = client.get(
        "/api/v1/workspace", headers={**auth_headers(tenants["a"]), "X-Organization-ID": "invalid"}
    )
    assert response.status_code == 422
    assert "input" not in response.json()["detail"][0]
    assert "X-Request-ID" in response.headers


def test_inactive_membership_is_rejected(client: TestClient, tenants: dict) -> None:
    with Session(get_engine()) as session, session.begin():
        set_context(
            session,
            actor_id=identifier(tenants["a"]["actor"]),
            tenant_id=identifier(tenants["a"]["tenant"]),
        )
        membership = session.scalar(
            select(Membership).where(Membership.user_id == tenants["a"]["actor"])
        )
        assert membership
        membership.active = False
    assert client.get("/api/v1/workspace", headers=auth_headers(tenants["a"])).status_code == 403
