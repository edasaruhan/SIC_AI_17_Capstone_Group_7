import pytest
from conftest import auth_headers
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_integration_secret_reference_is_write_only_and_tenant_scoped(
    client: TestClient, tenants: dict[str, dict[str, object]]
) -> None:
    created = client.post(
        "/api/v1/integrations",
        headers=auth_headers(tenants["a"]),
        json={
            "provider": "meta_ads",
            "name": "Meta reporting",
            "external_account_id": "123",
            "secret_ref": "env:GP_PROVIDER_META_TOKEN",
        },
    )
    assert created.status_code == 201, created.text
    assert "secret_ref" not in created.json()
    assert created.json()["api_version"] == "v25.0"
    assert client.get("/api/v1/integrations", headers=auth_headers(tenants["b"])).json() == []
    queued = client.post(
        f"/api/v1/integrations/{created.json()['id']}/syncs",
        headers=auth_headers(tenants["a"]),
    )
    assert queued.status_code == 202 and queued.json()["status"] == "queued"


def test_analyst_cannot_configure_provider(
    client: TestClient, tenants: dict[str, dict[str, object]]
) -> None:
    response = client.post(
        "/api/v1/integrations",
        headers=auth_headers(tenants["analyst"]),
        json={
            "provider": "google_ads",
            "name": "Forbidden",
            "external_account_id": "1",
            "secret_ref": "env:GP_PROVIDER_GOOGLE_TOKEN",
        },
    )
    assert response.status_code == 403
