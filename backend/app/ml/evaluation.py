import math

import numpy as np
from sklearn.metrics import (  # type: ignore[import-untyped]
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)


def expected_calibration_error(
    target: np.ndarray, probability: np.ndarray, bins: int = 10
) -> float:
    edges = np.linspace(0, 1, bins + 1)
    assignments = np.clip(np.digitize(probability, edges[1:-1]), 0, bins - 1)
    result = 0.0
    for index in range(bins):
        selected = assignments == index
        if selected.any():
            result += float(selected.mean()) * abs(
                float(target[selected].mean()) - float(probability[selected].mean())
            )
    return result


def classification_metrics(target: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    if target.ndim != 1 or probability.shape != target.shape:
        raise ValueError("Target and probability must be aligned one-dimensional arrays")
    if not np.isfinite(probability).all() or ((probability < 0) | (probability > 1)).any():
        raise ValueError("Probabilities must be finite and between zero and one")
    base = float(target.mean())
    metrics = {
        "pr_auc": float(average_precision_score(target, probability)),
        "roc_auc": float(roc_auc_score(target, probability)),
        "log_loss": float(log_loss(target, probability, labels=[0, 1])),
        "brier": float(brier_score_loss(target, probability)),
        "ece_10": expected_calibration_error(target, probability),
        "prevalence": base,
    }
    order = np.argsort(-probability, kind="stable")
    positives = max(int(target.sum()), 1)
    for fraction in (0.05, 0.10, 0.20):
        count = max(1, math.ceil(len(target) * fraction))
        selected = target[order[:count]]
        precision = float(selected.mean())
        suffix = str(int(fraction * 100))
        metrics[f"precision_at_{suffix}"] = precision
        metrics[f"recall_at_{suffix}"] = float(selected.sum() / positives)
        metrics[f"lift_at_{suffix}"] = precision / base if base else 0.0
    return {name: round(value, 6) for name, value in metrics.items()}
