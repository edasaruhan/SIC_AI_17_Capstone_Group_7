from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import jwt
import pytest
from app.identity.models import Membership, Organization, User
from app.platform.config import Settings, get_settings
from app.platform.db import get_engine, set_context
from app.platform.storage import get_object_store
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session


@pytest.fixture
def tenants(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> dict[str, dict[str, object]]:
    settings = Settings()
    assert settings.environment != "production"
    assert settings.migration_database_url and settings.dev_signing_secret
    owner_url = make_url(settings.migration_database_url.get_secret_value()).set(
        database="growthpilot_test"
    )
    runtime_url = make_url(settings.database_url.get_secret_value()).set(
        database="growthpilot_test"
    )
    monkeypatch.setenv("GP_DATABASE_URL", runtime_url.render_as_string(hide_password=False))
    monkeypatch.setenv("GP_ENVIRONMENT", "test")
    monkeypatch.setenv("GP_OBJECT_ROOT", str(tmp_path / "private_objects"))
    get_object_store.cache_clear()
    get_engine.cache_clear()
    get_settings.cache_clear()
    owner_engine = create_engine(owner_url)
    result: dict[str, dict[str, object]] = {}
    with Session(owner_engine) as session, session.begin():
        for key, role in [("a", "OWNER"), ("b", "OWNER"), ("analyst", "ANALYST")]:
            actor, tenant = uuid4(), uuid4()
            set_context(session, actor_id=actor, tenant_id=tenant)
            subject = f"synthetic-test-{actor}"
            session.add(
                User(
                    id=actor,
                    issuer="growthpilot-local",
                    subject=subject,
                    display_name="Synthetic fixture",
                )
            )
            session.add(Organization(id=tenant, name=f"Synthetic tenant {key}", is_demo=True))
            session.flush()
            session.add(
                Membership(id=uuid4(), tenant_id=tenant, user_id=actor, role=role, active=True)
            )
            session.flush()
            token = jwt.encode(
                {
                    "iss": "growthpilot-local",
                    "sub": subject,
                    "aud": "growthpilot-api",
                    "iat": datetime.now(UTC),
                    "exp": datetime.now(UTC) + timedelta(minutes=10),
                },
                settings.dev_signing_secret.get_secret_value(),
                algorithm="HS256",
            )
            result[key] = {"actor": actor, "tenant": tenant, "token": token, "subject": subject}
    owner_engine.dispose()
    return result


@pytest.fixture
def client(tenants: dict[str, dict[str, object]]) -> Iterator[TestClient]:
    from app.main import create_app

    with TestClient(create_app()) as instance:
        yield instance
    get_engine.cache_clear()
    get_settings.cache_clear()


def auth_headers(tenant: dict[str, object]) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {tenant['token']}",
        "X-Organization-ID": str(tenant["tenant"]),
    }


def identifier(value: object) -> UUID:
    assert isinstance(value, UUID)
    return value
