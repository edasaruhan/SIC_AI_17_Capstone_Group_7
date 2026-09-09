from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from app.intelligence import service
from app.intelligence.service import LocalCandidatePredictor
from conftest import auth_headers
from fastapi.testclient import TestClient
from test_commerce import setup_sale

pytestmark = pytest.mark.integration


class FakePredictor:
    manifest = {
        "target_version": "future-inactivity-v1",
        "feature_version": "customer-behavior-v1",
        "split_version": "temporal-split-v1",
        "mlflow_run_id": "synthetic-test-model",
        "artifact_sha256": "a" * 64,
        "threshold_metrics": {"threshold": 0.8},
    }

    def predict(self, features: object) -> float:
        return 0.9


def create_recent_order(client: TestClient, tenant: dict[str, object]) -> str:
    customer, product = setup_sale(client, tenant)
    response = client.post(
        "/api/v1/orders",
        headers=auth_headers(tenant),
        json={
            "customer_id": customer,
            "placed_at": (datetime.now(UTC) - timedelta(days=5)).isoformat(),
            "items": [{"product_id": product, "quantity": 2}],
            "idempotency_key": f"scoring-order-{customer}",
        },
    )
    assert response.status_code == 201, response.text
    return customer


def test_demo_scoring_is_immutable_consent_safe_and_tenant_scoped(
    client: TestClient, tenants: dict[str, dict[str, object]], monkeypatch: pytest.MonkeyPatch
) -> None:
    customer = create_recent_order(client, tenants["a"])
    monkeypatch.setattr(service, "get_predictor", lambda: FakePredictor())
    created = client.post(
        f"/api/v1/intelligence/customers/{customer}/score",
        headers=auth_headers(tenants["a"]),
    )
    assert created.status_code == 201, created.text
    result = created.json()
    assert result["inactivity_probability"] == 0.9
    assert result["decision_state"] == "no_contact_review"
    assert result["eligible_channels"] == []
    assert result["human_approval_required"] is True
    assert result["action_authorized"] is False
    assert result["provenance"]["model_sha256"] == "a" * 64

    history = client.get(
        f"/api/v1/intelligence/customers/{customer}/predictions",
        headers=auth_headers(tenants["a"]),
    )
    assert history.status_code == 200 and len(history.json()) == 1
    hidden = client.get(
        f"/api/v1/intelligence/customers/{customer}/predictions",
        headers=auth_headers(tenants["b"]),
    )
    assert hidden.status_code == 404


def test_scoring_requires_recent_purchase(
    client: TestClient, tenants: dict[str, dict[str, object]], monkeypatch: pytest.MonkeyPatch
) -> None:
    customer, _ = setup_sale(client, tenants["a"])
    monkeypatch.setattr(service, "get_predictor", lambda: FakePredictor())
    response = client.post(
        f"/api/v1/intelligence/customers/{customer}/score",
        headers=auth_headers(tenants["a"]),
    )
    assert response.status_code == 409
    assert "180-day" in response.json()["detail"]


def test_candidate_loader_rejects_checksum_mismatch(tmp_path: Path) -> None:
    model = tmp_path / "candidate.joblib"
    manifest = tmp_path / "manifest.json"
    model.write_bytes(b"not-a-trusted-model")
    manifest.write_text('{"artifact_sha256":"' + "0" * 64 + '"}')
    with pytest.raises(RuntimeError, match="checksum"):
        LocalCandidatePredictor(model, manifest)
