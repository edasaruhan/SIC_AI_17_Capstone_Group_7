import numpy as np
import pytest
from app.ml.evaluation import (
    bootstrap_intervals,
    classification_metrics,
    expected_calibration_error,
)


def test_perfect_ranking_and_top_k_metrics() -> None:
    target = np.array([0, 0, 1, 1])
    probability = np.array([0.1, 0.2, 0.8, 0.9])
    metrics = classification_metrics(target, probability)
    assert metrics["pr_auc"] == metrics["roc_auc"] == 1
    assert metrics["precision_at_20"] == 1
    assert metrics["lift_at_20"] == 2


def test_calibration_and_invalid_probabilities() -> None:
    target = np.array([0, 1])
    assert expected_calibration_error(target, np.array([0.0, 1.0])) == 0
    with pytest.raises(ValueError, match="between zero and one"):
        classification_metrics(target, np.array([-0.1, 1.1]))
    with pytest.raises(ValueError, match="aligned"):
        classification_metrics(target, np.array([[0.1, 0.9]]))


def test_bootstrap_intervals_are_deterministic_and_bounded() -> None:
    target = np.array([0, 0, 0, 1, 1, 1])
    probability = np.array([0.1, 0.2, 0.4, 0.6, 0.8, 0.9])
    first = bootstrap_intervals(target, probability, iterations=100, seed=17)
    assert first == bootstrap_intervals(target, probability, iterations=100, seed=17)
    assert 0 <= first["brier"]["lower_95"] <= first["brier"]["upper_95"] <= 1
    with pytest.raises(ValueError, match="At least 100"):
        bootstrap_intervals(target, probability, iterations=10)
