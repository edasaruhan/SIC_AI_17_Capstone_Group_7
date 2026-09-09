"""Register the checksum-verified frozen candidate in the local MLflow registry."""

import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
os.environ.setdefault("MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING", "false")

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature

MODEL = Path(".local/models/final_candidate.joblib")
MANIFEST = Path("artifacts/ml/final_candidate.json")
SAMPLE = Path("data/processed/ml/calibration.parquet")
FINAL = Path("artifacts/ml/final_evaluation.json")
REPORT = Path("artifacts/ml/model_registry.json")
REGISTERED_NAME = "growthpilot-churn-inactivity"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    final = json.loads(FINAL.read_text())
    checksum = hashlib.sha256(MODEL.read_bytes()).hexdigest()
    if checksum != manifest["artifact_sha256"]:
        raise RuntimeError("Frozen candidate checksum mismatch")
    candidate = joblib.load(MODEL)
    sample = pd.read_parquet(SAMPLE).head(20)
    for column in sample.select_dtypes(include="number").columns:
        sample[column] = sample[column].astype(float)
    signature = infer_signature(sample, candidate.predict_proba(sample))
    mlflow.set_tracking_uri("sqlite:///.local/mlflow.db")
    mlflow.set_experiment("growthpilot-churn")
    with mlflow.start_run(run_name="registered_frozen_candidate") as run:
        mlflow.set_tags(
            {
                "stage": "registered_candidate",
                "target_version": manifest["target_version"],
                "feature_version": manifest["feature_version"],
                "split_version": manifest["split_version"],
                "model_sha256": checksum,
                "domain_validation": "required_before_non_demo_use",
            }
        )
        mlflow.log_metrics(
            {
                "final_pr_auc": final["metrics"]["pr_auc"],
                "final_roc_auc": final["metrics"]["roc_auc"],
                "final_brier": final["metrics"]["brier"],
            }
        )
        info = mlflow.sklearn.log_model(
            candidate,
            name="model",
            signature=signature,
            input_example=sample,
            registered_model_name=REGISTERED_NAME,
            skops_trusted_types=[
                "app.ml.features.BehaviorFeatureTransformer",
                "numpy.dtype",
                "sklearn.calibration._CalibratedClassifier",
                "sklearn.calibration._SigmoidCalibration",
            ],
        )
        run_id = run.info.run_id
    client = mlflow.MlflowClient()
    versions = client.search_model_versions(f"name='{REGISTERED_NAME}'")
    version = max(
        (item for item in versions if item.run_id == run_id),
        key=lambda item: int(item.version),
    )
    client.set_registered_model_alias(REGISTERED_NAME, "champion", version.version)
    client.set_model_version_tag(REGISTERED_NAME, version.version, "model_sha256", checksum)
    client.set_model_version_tag(
        REGISTERED_NAME, version.version, "deployment_gate", "demo_only_domain_validation_required"
    )
    report = {
        "evidence": "project_generated_local_registry",
        "registered_model": REGISTERED_NAME,
        "alias": "champion",
        "version": version.version,
        "run_id": run_id,
        "model_uri": info.model_uri,
        "model_sha256": checksum,
        "target_version": manifest["target_version"],
        "feature_version": manifest["feature_version"],
        "split_version": manifest["split_version"],
        "deployment_gate": "demo_only_until_business_domain_validation",
        "serialization_note": (
            "MLflow sklearn model is a local trusted artifact; never load untrusted models."
        ),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
