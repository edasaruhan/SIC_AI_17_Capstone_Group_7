import pytest
from app.intelligence.decision import (
    DecisionEvidence,
    DecisionInput,
    DecisionState,
    decide,
)
from pydantic import ValidationError

EVIDENCE = DecisionEvidence(
    target_version="future-inactivity-v1",
    feature_version="customer-behavior-v1",
    split_version="temporal-snapshot-v1",
    model_version="candidate-v1",
    model_sha256="a" * 64,
    explanation_method="linear_shap_log_odds",
)


def decision_input(**changes: object) -> DecisionInput:
    values: dict[str, object] = {
        "inactivity_probability": 0.83,
        "frozen_threshold": 0.81,
        "consent": {"email": True, "sms": False, "ads": False},
        "evidence": EVIDENCE,
        "explanation_reason_codes": ("HIGH_RECENCY_CONTRIBUTION",),
    }
    values.update(changes)
    return DecisionInput.model_validate(values)


def test_elevated_customer_with_consent_requires_review() -> None:
    result = decide(decision_input())
    assert result.state is DecisionState.REVIEW_RETENTION
    assert result.eligible_channels == ("email",)
    assert result.human_approval_required is True
    assert result.action_authorized is False
    assert result.evidence == EVIDENCE


def test_absent_consent_never_produces_contact_channel() -> None:
    result = decide(
        decision_input(consent={"email": False, "sms": False, "ads": False})
    )
    assert result.state is DecisionState.NO_CONTACT_REVIEW
    assert result.eligible_channels == ()
    assert "NO_CONSENTED_CHANNEL" in result.reason_codes
    assert result.action_authorized is False


def test_below_threshold_is_monitor_only_even_with_consent() -> None:
    result = decide(decision_input(inactivity_probability=0.2))
    assert result.state is DecisionState.MONITOR
    assert result.eligible_channels == ()
    assert result.human_approval_required is False
    assert result.action_authorized is False


@pytest.mark.parametrize("probability", [-0.01, 1.01])
def test_probability_bounds_are_enforced(probability: float) -> None:
    with pytest.raises(ValidationError):
        decision_input(inactivity_probability=probability)


def test_all_channel_consent_states_are_mandatory() -> None:
    with pytest.raises(ValidationError, match="explicitly cover"):
        decision_input(consent={"email": True})
