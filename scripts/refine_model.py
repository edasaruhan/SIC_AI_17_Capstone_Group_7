"""Validation-only refinement and calibration-date fitting. Never opens final test."""

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
os.environ.setdefault("MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING", "false")
os.environ.setdefault("UV_CACHE_DIR", ".cache/uv")
os.environ.setdefault("OMP_NUM_THREADS", "4")

import joblib
import mlflow
import numpy as np
import optuna
import pandas as pd
from app.ml.data import FEATURE_VERSION, SPLIT_VERSION, TARGET_VERSION
from app.ml.evaluation import classification_metrics
from app.ml.features import model_pipeline
from lightgbm import LGBMClassifier
from sklearn.calibration import CalibratedClassifierCV  # type: ignore[import-untyped]
from sklearn.ensemble import RandomForestClassifier  # type: ignore[import-untyped]
from sklearn.frozen import FrozenEstimator  # type: ignore[import-untyped]
from sklearn.linear_model import LogisticRegression  # type: ignore[import-untyped]
from sklearn.metrics import f1_score, precision_score, recall_score  # type: ignore[import-untyped]

DATA = Path("data/processed/ml")
MODEL = Path(".local/models/final_candidate.joblib")
REPORT = Path("artifacts/ml/final_candidate.json")


def revision() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()


def weights(frame: pd.DataFrame) -> np.ndarray:
    return (1 / frame.groupby("customer_id")["customer_id"].transform("size")).to_numpy()


def fit_score(
    estimator: Any,
    scale: bool,
    train: pd.DataFrame,
    validation: pd.DataFrame,
) -> tuple[Any, dict[str, float]]:
    pipeline = model_pipeline(estimator, scale=scale)
    pipeline.fit(
        train,
        train["target_inactive_90d"].to_numpy(dtype=int),
        model__sample_weight=weights(train),
    )
    probability = pipeline.predict_proba(validation)[:, 1]
    return pipeline, classification_metrics(
        validation["target_inactive_90d"].to_numpy(dtype=int), probability
    )


def log_trial(name: str, parameters: dict[str, object], metrics: dict[str, float]) -> str:
    with mlflow.start_run(run_name=name) as run:
        mlflow.set_tags(
            {
                "stage": "refinement",
                "evaluation_split": "validation",
                "target_version": TARGET_VERSION,
                "feature_version": FEATURE_VERSION,
                "split_version": SPLIT_VERSION,
                "git_revision": revision(),
            }
        )
        mlflow.log_params(parameters)
        mlflow.log_metrics(metrics)
        return run.info.run_id


def main() -> None:
    train = pd.read_parquet(DATA / "train.parquet")
    validation = pd.read_parquet(DATA / "validation.parquet")
    calibration = pd.read_parquet(DATA / "calibration.parquet")
    tracking = Path(".local/mlflow.db")
    mlflow.set_tracking_uri(f"sqlite:///{tracking}")
    mlflow.set_experiment("growthpilot-churn")
    trials: list[dict[str, object]] = []
    best: tuple[str, Any, bool, dict[str, object], dict[str, float]] | None = None

    def consider(name: str, estimator: Any, scale: bool, parameters: dict[str, object]) -> float:
        nonlocal best
        _, metrics = fit_score(estimator, scale, train, validation)
        run_id = log_trial(name, parameters, metrics)
        trials.append(
            {"name": name, "parameters": parameters, "validation": metrics, "run_id": run_id}
        )
        if best is None or metrics["pr_auc"] > best[4]["pr_auc"]:
            best = (name, estimator, scale, parameters, metrics)
        return metrics["pr_auc"]

    for regularization in (0.01, 0.05, 0.2, 1.0, 5.0):
        consider(
            f"logistic_c_{regularization}",
            LogisticRegression(C=regularization, max_iter=2000, random_state=17),
            True,
            {"family": "logistic", "C": regularization, "class_weight": "none"},
        )
    for leaf, depth in ((5, 8), (10, 8), (20, 8), (5, 16), (10, 16), (20, 16)):
        consider(
            f"forest_leaf_{leaf}_depth_{depth}",
            RandomForestClassifier(
                n_estimators=400,
                min_samples_leaf=leaf,
                max_depth=depth,
                max_features="sqrt",
                class_weight="balanced_subsample",
                random_state=17,
                n_jobs=4,
            ),
            False,
            {
                "family": "random_forest",
                "n_estimators": 400,
                "min_samples_leaf": leaf,
                "max_depth": depth,
            },
        )

    sampler = optuna.samplers.TPESampler(seed=17)
    study = optuna.create_study(direction="maximize", sampler=sampler)

    def objective(trial: optuna.Trial) -> float:
        parameters: dict[str, object] = {
            "family": "lightgbm",
            "n_estimators": trial.suggest_int("n_estimators", 150, 550, step=50),
            "learning_rate": trial.suggest_float("learning_rate", 0.015, 0.12, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 7, 63),
            "max_depth": trial.suggest_int("max_depth", 3, 9),
            "min_child_samples": trial.suggest_int("min_child_samples", 20, 120, step=10),
            "reg_lambda": trial.suggest_float("reg_lambda", 0.01, 10, log=True),
            "subsample": trial.suggest_float("subsample", 0.7, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.7, 1.0),
        }
        estimator_parameters = {key: value for key, value in parameters.items() if key != "family"}
        estimator = LGBMClassifier(
            **estimator_parameters,
            subsample_freq=1,
            random_state=17,
            n_jobs=4,
            deterministic=True,
            force_col_wise=True,
            verbosity=-1,
        )
        return consider(f"lightgbm_trial_{trial.number}", estimator, False, parameters)

    study.optimize(objective, n_trials=12, show_progress_bar=False)
    assert best is not None
    name, estimator, scale, parameters, validation_metrics = best
    refit = pd.concat([train, validation], ignore_index=True)
    pipeline = model_pipeline(estimator, scale=scale)
    pipeline.fit(
        refit,
        refit["target_inactive_90d"].to_numpy(dtype=int),
        model__sample_weight=weights(refit),
    )
    calibrated = CalibratedClassifierCV(FrozenEstimator(pipeline), method="sigmoid")
    calibration_target = calibration["target_inactive_90d"].to_numpy(dtype=int)
    calibrated.fit(calibration, calibration_target)
    probability = calibrated.predict_proba(calibration)[:, 1]
    calibration_metrics = classification_metrics(calibration_target, probability)
    threshold = float(np.quantile(probability, 0.9, method="higher"))
    predicted = probability >= threshold
    threshold_metrics = {
        "threshold": round(threshold, 12),
        "selected_share": round(float(predicted.mean()), 6),
        "precision": round(float(precision_score(calibration_target, predicted)), 6),
        "recall": round(float(recall_score(calibration_target, predicted)), 6),
        "f1": round(float(f1_score(calibration_target, predicted)), 6),
    }
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(calibrated, MODEL)
    artifact_hash = hashlib.sha256(MODEL.read_bytes()).hexdigest()
    with mlflow.start_run(run_name="frozen_calibrated_candidate") as run:
        mlflow.set_tags(
            {
                "stage": "candidate",
                "target_version": TARGET_VERSION,
                "feature_version": FEATURE_VERSION,
                "split_version": SPLIT_VERSION,
                "git_revision": revision(),
                "final_test_accessed": "false",
            }
        )
        mlflow.log_params({**parameters, "calibration": "sigmoid", "capacity": "top_10_pct"})
        mlflow.log_metrics(
            {f"validation_{key}": value for key, value in validation_metrics.items()}
        )
        mlflow.log_metrics(
            {f"calibration_fit_{key}": value for key, value in calibration_metrics.items()}
        )
        mlflow.log_metrics({f"threshold_{key}": value for key, value in threshold_metrics.items()})
        mlflow.log_artifact(str(MODEL), artifact_path="candidate")
        candidate_run_id = run.info.run_id
    result = {
        "evidence": "project_executed_validation_and_calibration_only",
        "target_version": TARGET_VERSION,
        "feature_version": FEATURE_VERSION,
        "split_version": SPLIT_VERSION,
        "git_revision": revision(),
        "search": {"logistic_trials": 5, "random_forest_trials": 6, "lightgbm_trials": 12},
        "trials": trials,
        "selected_family": name,
        "selected_parameters": parameters,
        "validation": validation_metrics,
        "calibration_fit": calibration_metrics,
        "threshold_policy": "top_10_percent_capacity_on_calibration_scores",
        "threshold_metrics": threshold_metrics,
        "calibration_note": "Metrics reuse sigmoid-fit labels and are descriptive, not unbiased.",
        "artifact_sha256": artifact_hash,
        "mlflow_run_id": candidate_run_id,
        "final_test_accessed": False,
        "post_test_retuning_permitted": False,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in result if key != "trials"}, indent=2))


if __name__ == "__main__":
    main()
