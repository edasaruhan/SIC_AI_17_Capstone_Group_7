"""One-shot final temporal holdout evaluation. Never use this output for retuning."""

import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", ".cache/matplotlib")
os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
os.environ.setdefault("UV_CACHE_DIR", ".cache/uv")

import joblib
import matplotlib.pyplot as plt
import mlflow
import pandas as pd
from app.ml.evaluation import bootstrap_intervals, classification_metrics
from sklearn.calibration import calibration_curve  # type: ignore[import-untyped]
from sklearn.metrics import (  # type: ignore[import-untyped]
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)

MODEL = Path(".local/models/final_candidate.joblib")
CANDIDATE = Path("artifacts/ml/final_candidate.json")
TEST = Path("data/processed/ml/test.parquet")
REPORT = Path("artifacts/ml/final_evaluation.json")
FIGURE = Path("artifacts/ml/final_evaluation.png")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if REPORT.exists():
        raise SystemExit("Final test was already evaluated; rerun is intentionally blocked")
    candidate = json.loads(CANDIDATE.read_text())
    if candidate["final_test_accessed"] or candidate["post_test_retuning_permitted"]:
        raise SystemExit("Candidate metadata does not permit first final evaluation")
    if sha256(MODEL) != candidate["artifact_sha256"]:
        raise SystemExit("Frozen model artifact checksum mismatch")
    candidate_manifest_sha = sha256(CANDIDATE)
    test = pd.read_parquet(TEST)
    target = test["target_inactive_90d"].to_numpy(dtype=int)
    model = joblib.load(MODEL)
    probability = model.predict_proba(test)[:, 1]
    metrics = classification_metrics(target, probability)
    intervals = bootstrap_intervals(target, probability, iterations=1000, seed=17)
    threshold = candidate["threshold_metrics"]["threshold"]
    predicted = probability >= threshold
    matrix = confusion_matrix(target, predicted, labels=[0, 1])
    threshold_metrics = {
        "selected_rows": int(predicted.sum()),
        "selected_share": round(float(predicted.mean()), 6),
        "precision": round(float(precision_score(target, predicted, zero_division=0)), 6),
        "recall": round(float(recall_score(target, predicted, zero_division=0)), 6),
        "f1": round(float(f1_score(target, predicted, zero_division=0)), 6),
        "confusion_matrix_tn_fp_fn_tp": [
            int(matrix[0, 0]),
            int(matrix[0, 1]),
            int(matrix[1, 0]),
            int(matrix[1, 1]),
        ],
    }
    precision, recall, _ = precision_recall_curve(target, probability)
    observed, predicted_bins = calibration_curve(
        target, probability, n_bins=10, strategy="quantile"
    )
    figure, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(recall, precision, color="#2f6f55")
    axes[0].axhline(target.mean(), color="#777777", linestyle="--", label="prevalence")
    axes[0].set(
        title="Untouched temporal test: precision-recall",
        xlabel="Recall",
        ylabel="Precision",
        xlim=(0, 1),
        ylim=(0, 1),
    )
    axes[0].legend()
    axes[1].plot([0, 1], [0, 1], color="#777777", linestyle="--")
    axes[1].plot(predicted_bins, observed, marker="o", color="#315c75")
    axes[1].set(
        title="Probability calibration",
        xlabel="Mean predicted probability",
        ylabel="Observed rate",
        xlim=(0, 1),
        ylim=(0, 1),
    )
    figure.tight_layout()
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURE, dpi=160)
    plt.close(figure)

    tracking = Path(".local/mlflow.db")
    mlflow.set_tracking_uri(f"sqlite:///{tracking}")
    with mlflow.start_run(run_id=candidate["mlflow_run_id"]):
        mlflow.log_metrics({f"final_test_{key}": value for key, value in metrics.items()})
        mlflow.log_metrics(
            {
                f"final_threshold_{key}": value
                for key, value in threshold_metrics.items()
                if not isinstance(value, list)
            }
        )
        mlflow.set_tag("final_test_accessed", "true")
        mlflow.log_artifact(str(FIGURE), artifact_path="final_evaluation")
    result = {
        "evidence": "project_executed_untouched_temporal_holdout",
        "target_version": candidate["target_version"],
        "feature_version": candidate["feature_version"],
        "split_version": candidate["split_version"],
        "candidate_manifest_sha256_before_access": candidate_manifest_sha,
        "model_artifact_sha256": candidate["artifact_sha256"],
        "test_parquet_sha256": sha256(TEST),
        "rows": len(test),
        "cutoff": str(pd.Timestamp(test["snapshot_cutoff"].iloc[0]).date()),
        "prevalence": round(float(target.mean()), 6),
        "metrics": metrics,
        "bootstrap_95_intervals": intervals,
        "threshold_policy": candidate["threshold_policy"],
        "threshold": threshold,
        "threshold_metrics": threshold_metrics,
        "interpretation": [
            "This evaluates future-purchase inactivity, not observed contractual churn.",
            "Confidence intervals are nonparametric row bootstrap intervals for this one cutoff.",
            "Repeated-customer temporal design and one retailer limit generalization.",
            "No post-test model, feature, calibration or threshold change is permitted.",
        ],
    }
    REPORT.write_text(json.dumps(result, indent=2) + "\n")
    candidate["final_test_accessed"] = True
    candidate["final_evaluation_sha256"] = sha256(REPORT)
    CANDIDATE.write_text(json.dumps(candidate, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
