"""Fixed model-family exploration. This script never opens calibration or test data."""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

os.environ.setdefault("MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING", "false")
os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("UV_CACHE_DIR", ".cache/uv")

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from app.ml.data import FEATURE_VERSION, SPLIT_VERSION, TARGET_VERSION
from app.ml.evaluation import classification_metrics
from app.ml.features import model_pipeline
from lightgbm import LGBMClassifier
from sklearn.dummy import DummyClassifier  # type: ignore[import-untyped]
from sklearn.ensemble import RandomForestClassifier  # type: ignore[import-untyped]
from sklearn.linear_model import LogisticRegression  # type: ignore[import-untyped]

DATA = Path("data/processed/ml")
OUTPUT = Path("artifacts/ml/model_exploration.json")
MODELS = Path(".local/models/exploration")


def git_revision() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()


def candidates() -> dict[str, tuple[Any, bool, dict[str, object]]]:
    return {
        "dummy_prior": (DummyClassifier(strategy="prior"), False, {"strategy": "prior"}),
        "logistic": (
            LogisticRegression(C=1.0, max_iter=2000, random_state=17),
            True,
            {"C": 1.0, "class_weight": "none"},
        ),
        "random_forest": (
            RandomForestClassifier(
                n_estimators=300,
                min_samples_leaf=10,
                max_features="sqrt",
                class_weight="balanced_subsample",
                random_state=17,
                n_jobs=4,
            ),
            False,
            {"n_estimators": 300, "min_samples_leaf": 10, "max_features": "sqrt"},
        ),
        "lightgbm": (
            LGBMClassifier(
                n_estimators=300,
                learning_rate=0.05,
                num_leaves=31,
                min_child_samples=40,
                subsample=0.9,
                colsample_bytree=0.9,
                reg_lambda=1.0,
                random_state=17,
                n_jobs=4,
                deterministic=True,
                force_col_wise=True,
                verbosity=-1,
            ),
            False,
            {"n_estimators": 300, "learning_rate": 0.05, "num_leaves": 31},
        ),
    }


def main() -> None:
    train = pd.read_parquet(DATA / "train.parquet")
    validation = pd.read_parquet(DATA / "validation.parquet")
    target_name = "target_inactive_90d"
    target_train = train[target_name].to_numpy(dtype=int)
    target_validation = validation[target_name].to_numpy(dtype=int)
    weights = 1 / train.groupby("customer_id")["customer_id"].transform("size").to_numpy()
    tracking = Path(".local/mlflow.db")
    tracking.parent.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"sqlite:///{tracking}")
    mlflow.set_experiment("growthpilot-churn")
    MODELS.mkdir(parents=True, exist_ok=True)
    results: dict[str, object] = {
        "evidence": "project_executed_validation_only",
        "target_version": TARGET_VERSION,
        "feature_version": FEATURE_VERSION,
        "split_version": SPLIT_VERSION,
        "git_revision": git_revision(),
        "selection_metric": "validation_pr_auc",
        "models": {},
        "final_test_accessed": False,
    }
    model_results: dict[str, object] = {}

    recency_probability = np.clip(validation["recency_days"].to_numpy() / 180, 0, 1)
    recency_metrics = classification_metrics(target_validation, recency_probability)
    with mlflow.start_run(run_name="recency_heuristic") as run:
        mlflow.set_tags(
            {
                "target_version": TARGET_VERSION,
                "feature_version": FEATURE_VERSION,
                "split_version": SPLIT_VERSION,
                "git_revision": git_revision(),
                "evaluation_split": "validation",
            }
        )
        mlflow.log_param("formula", "clip(recency_days/180,0,1)")
        mlflow.log_metrics(recency_metrics)
        model_results["recency_heuristic"] = {
            "run_id": run.info.run_id,
            "parameters": {"formula": "clip(recency_days/180,0,1)"},
            "validation": recency_metrics,
        }

    for name, (estimator, scale, parameters) in candidates().items():
        pipeline = model_pipeline(estimator, scale=scale)
        with mlflow.start_run(run_name=name) as run:
            mlflow.set_tags(
                {
                    "target_version": TARGET_VERSION,
                    "feature_version": FEATURE_VERSION,
                    "split_version": SPLIT_VERSION,
                    "git_revision": git_revision(),
                    "evaluation_split": "validation",
                }
            )
            mlflow.log_params(parameters)
            pipeline.fit(train, target_train, model__sample_weight=weights)
            probability = pipeline.predict_proba(validation)[:, 1]
            metrics = classification_metrics(target_validation, probability)
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(
                pipeline,
                name="model",
                skops_trusted_types=[
                    "app.ml.features.BehaviorFeatureTransformer",
                    "collections.OrderedDict",
                    "lightgbm.basic.Booster",
                    "lightgbm.sklearn.LGBMClassifier",
                    "numpy.dtype",
                ],
            )
            path = MODELS / f"{name}.joblib"
            joblib.dump(pipeline, path)
            model_results[name] = {
                "run_id": run.info.run_id,
                "parameters": parameters,
                "validation": metrics,
            }
    results["models"] = model_results
    winner = max(model_results, key=lambda name: model_results[name]["validation"]["pr_auc"])  # type: ignore[index]
    results["validation_winner"] = winner
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
