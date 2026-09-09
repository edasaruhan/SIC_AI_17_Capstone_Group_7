import pytest
from app.generation import service
from app.generation.service import prompt_for, validate_grounding
from app.platform.errors import DomainError
from conftest import auth_headers
from fastapi.testclient import TestClient
from test_commerce import setup_sale


class FakeProvider:
    name = "synthetic-test-provider"
    model = "synthetic-test-model"

    def generate(self, prompt: str) -> str:
        assert "Verified facts" in prompt
        return "We would be glad to reconnect."


def test_prompt_marks_facts_as_verified_and_requires_human_review() -> None:
    prompt = prompt_for("Reconnect", "email", {"observed_purchase_count": 2})
    assert '"observed_purchase_count": 2' in prompt
    assert "Human approval is mandatory" in prompt
    assert "infer missing numbers" in prompt


def test_grounding_accepts_only_fact_backed_numbers() -> None:
    facts = {"observed_purchase_count": 2, "inactivity_probability": 0.75}
    validate_grounding("We noticed 2 prior purchases; the recorded score is 0.75.", facts)
    with pytest.raises(DomainError, match="unsupported number"):
        validate_grounding("Get 30% off after 2 purchases.", facts)


def test_grounding_rejects_outcome_promises() -> None:
    with pytest.raises(DomainError, match="outcome claim"):
        validate_grounding("This is guaranteed to bring you back.", {})


@pytest.mark.integration
def test_draft_uses_server_facts_consent_and_never_authorizes_action(
    client: TestClient,
    tenants: dict[str, dict[str, object]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    customer, _ = setup_sale(client, tenants["a"])
    headers = auth_headers(tenants["a"])
    denied = client.post(
        "/api/v1/assistant/drafts",
        headers=headers,
        json={"customer_id": customer, "channel": "email", "objective": "Reconnect"},
    )
    assert denied.status_code == 409
    consent = client.post(
        f"/api/v1/customers/{customer}/consents",
        headers=headers,
        json={"channel": "email", "granted": True, "source": "synthetic-test"},
    )
    assert consent.status_code == 201
    monkeypatch.setattr(service, "get_provider", lambda: FakeProvider())
    result = client.post(
        "/api/v1/assistant/drafts",
        headers=headers,
        json={"customer_id": customer, "channel": "email", "objective": "Reconnect"},
    )
    assert result.status_code == 201, result.text
    body = result.json()
    assert body["provider"] == "synthetic-test-provider"
    assert body["verified_facts"]["observed_purchase_count"] == 0
    assert body["human_approval_required"] is True
    assert body["action_authorized"] is False
