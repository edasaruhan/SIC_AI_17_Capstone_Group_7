"""Explain the frozen linear candidate on calibration data without touching test data."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", ".cache/matplotlib")
os.environ.setdefault("OMP_NUM_THREADS", "4")

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

MODEL = Path(".local/models/final_candidate.joblib")
CANDIDATE = Path("artifacts/ml/final_candidate.json")
CALIBRATION = Path("data/processed/ml/calibration.parquet")
REPORT = Path("artifacts/ml/explanations.json")
FIGURE = Path("artifacts/ml/explanations_global.png")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(value: Any) -> float | str:
    if isinstance(value, (np.floating, np.integer)):
        return float(value)
    return str(value)


def main() -> None:
    manifest = json.loads(CANDIDATE.read_text())
    if sha256(MODEL) != manifest["artifact_sha256"]:
        raise RuntimeError("Frozen candidate checksum mismatch")

    calibration = pd.read_parquet(CALIBRATION)
    calibrated = joblib.load(MODEL)
    pipeline = calibrated.estimator.estimator
    engineered = pipeline.named_steps["features"].transform(calibration)
    matrix = pipeline.named_steps["preprocess"].transform(engineered)
    estimator = pipeline.named_steps["model"]
    feature_names = pipeline.named_steps["preprocess"].get_feature_names_out().tolist()

    explainer = shap.LinearExplainer(estimator, matrix)
    explanation = explainer(matrix)
    values = np.asarray(explanation.values, dtype=float)
    base_values = np.asarray(explanation.base_values, dtype=float).reshape(-1)
    if base_values.size == 1:
        base_values = np.repeat(base_values, len(calibration))
    decision = np.asarray(estimator.decision_function(matrix), dtype=float)
    reconstructed = base_values + values.sum(axis=1)
    max_error = float(np.max(np.abs(decision - reconstructed)))
    if max_error > 1e-8:
        raise RuntimeError(f"SHAP additivity failed: max absolute error {max_error}")

    mean_absolute = np.mean(np.abs(values), axis=0)
    ordering = np.argsort(mean_absolute)[::-1]
    global_importance = [
        {
            "feature": feature_names[index],
            "mean_absolute_log_odds_contribution": round(float(mean_absolute[index]), 8),
        }
        for index in ordering
    ]
    probabilities = calibrated.predict_proba(calibration)[:, 1]
    local_cases: list[dict[str, object]] = []
    representative_indices = [
        int(np.argmax(probabilities)),
        int(np.argsort(probabilities)[len(probabilities) // 2]),
        int(np.argmin(probabilities)),
    ]
    for label, row_index in zip(
        ("highest", "median", "lowest"), representative_indices, strict=True
    ):
        local_order = np.argsort(np.abs(values[row_index]))[::-1][:5]
        local_cases.append(
            {
                "anonymous_case": f"calibration-{label}-score",
                "calibrated_probability": round(float(probabilities[row_index]), 8),
                "underlying_log_odds": round(float(decision[row_index]), 8),
                "base_log_odds": round(float(base_values[row_index]), 8),
                "top_contributions": [
                    {
                        "feature": feature_names[index],
                        "feature_value": plain(matrix[row_index, index]),
                        "log_odds_contribution": round(float(values[row_index, index]), 8),
                        "direction": "higher_inactivity_score"
                        if values[row_index, index] >= 0
                        else "lower_inactivity_score",
                    }
                    for index in local_order
                ],
            }
        )

    report = {
        "evidence": "project_generated_calibration_explanation",
        "scope": "underlying_logistic_log_odds_not_calibrated_probability",
        "causal_interpretation_permitted": False,
        "data_split": "calibration_only",
        "rows": len(calibration),
        "target_version": manifest["target_version"],
        "feature_version": manifest["feature_version"],
        "split_version": manifest["split_version"],
        "model_sha256": manifest["artifact_sha256"],
        "method": "linear_shap_log_odds",
        "max_additivity_error": max_error,
        "global_importance": global_importance,
        "anonymous_local_cases": local_cases,
        "limitations": [
            "Correlated inputs can divide or redistribute apparent importance.",
            "Contributions describe model behavior, not causes or intervention effects.",
            "The outer sigmoid calibrator is monotonic but is not decomposed by this report.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n")

    top = ordering[:15][::-1]
    fig, axis = plt.subplots(figsize=(10, 7))
    axis.barh([feature_names[index] for index in top], mean_absolute[top], color="#2563eb")
    axis.set_xlabel("Mean absolute SHAP contribution (log-odds)")
    axis.set_title("Frozen churn-proxy model — calibration explanation")
    axis.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    print(json.dumps({"report": str(REPORT), "figure": str(FIGURE), "max_error": max_error}))


if __name__ == "__main__":
    main()
