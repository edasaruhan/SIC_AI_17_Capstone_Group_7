from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import (  # type: ignore[import-untyped]
    BaseEstimator,
    ClassifierMixin,
    TransformerMixin,
)
from sklearn.compose import ColumnTransformer  # type: ignore[import-untyped]
from sklearn.impute import SimpleImputer  # type: ignore[import-untyped]
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]
from sklearn.preprocessing import OneHotEncoder, RobustScaler  # type: ignore[import-untyped]

RAW_NUMERIC_FEATURES = (
    "purchase_count_365",
    "spend_365",
    "units_365",
    "avg_order_value_365",
    "max_order_value_365",
    "order_value_std_365",
    "avg_basket_units_365",
    "avg_products_per_order_365",
    "purchase_count_90",
    "spend_90",
    "units_90",
    "unique_products_365",
    "purchase_count_observed",
    "mean_gap_days_365",
    "std_gap_days_365",
    "last_gap_days",
    "return_line_count_365",
    "return_value_365",
    "recency_days",
    "tenure_days",
    "return_value_share_365",
    "cutoff_month_sin",
    "cutoff_month_cos",
)
LOG_FEATURES = (
    "purchase_count_365",
    "spend_365",
    "units_365",
    "avg_order_value_365",
    "max_order_value_365",
    "order_value_std_365",
    "avg_basket_units_365",
    "avg_products_per_order_365",
    "purchase_count_90",
    "spend_90",
    "units_90",
    "unique_products_365",
    "purchase_count_observed",
    "return_line_count_365",
    "return_value_365",
    "return_value_share_365",
)
PASSTHROUGH_FEATURES = (
    "mean_gap_days_365",
    "std_gap_days_365",
    "last_gap_days",
    "recency_days",
    "tenure_days",
    "cutoff_month_sin",
    "cutoff_month_cos",
)
ENGINEERED_NUMERIC_FEATURES = tuple(f"log1p_{name}" for name in LOG_FEATURES) + PASSTHROUGH_FEATURES
MODEL_FEATURES = ENGINEERED_NUMERIC_FEATURES + ("country",)
FORBIDDEN_FEATURES = {
    "target_inactive_90d",
    "customer_id",
    "snapshot_cutoff",
    "target_version",
    "feature_version",
    "split_version",
}


class BehaviorFeatureTransformer(TransformerMixin, BaseEstimator):  # type: ignore[misc]
    """Shared deterministic pre-model feature logic for training and inference."""

    def fit(
        self, values: pd.DataFrame, target: pd.Series | None = None
    ) -> "BehaviorFeatureTransformer":
        self._validate(values)
        return self

    def transform(self, values: pd.DataFrame) -> pd.DataFrame:
        self._validate(values)
        result = pd.DataFrame(index=values.index)
        for name in LOG_FEATURES:
            numeric = pd.to_numeric(values[name], errors="coerce")
            if (numeric.dropna() < 0).any():
                raise ValueError(f"Feature {name} must be nonnegative")
            result[f"log1p_{name}"] = np.log1p(numeric)
        for name in PASSTHROUGH_FEATURES:
            result[name] = pd.to_numeric(values[name], errors="coerce")
        result["country"] = values["country"].astype("string")
        return result.loc[:, MODEL_FEATURES]

    @staticmethod
    def _validate(values: pd.DataFrame) -> None:
        if not isinstance(values, pd.DataFrame):
            raise TypeError("Behavior features require a named pandas DataFrame")
        missing = set(RAW_NUMERIC_FEATURES + ("country",)) - set(values.columns)
        if missing:
            raise ValueError(f"Missing required behavior features: {sorted(missing)}")


def model_pipeline(estimator: ClassifierMixin, *, scale: bool) -> Pipeline:
    numeric_steps: list[tuple[str, Any]] = [
        ("impute", SimpleImputer(strategy="median", add_indicator=True))
    ]
    if scale:
        numeric_steps.append(("scale", RobustScaler(quantile_range=(5, 95))))
    preprocessor = ColumnTransformer(
        [
            ("numeric", Pipeline(numeric_steps), list(ENGINEERED_NUMERIC_FEATURES)),
            (
                "country",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="constant", fill_value="__missing__")),
                        (
                            "encode",
                            OneHotEncoder(
                                handle_unknown="infrequent_if_exist",
                                min_frequency=20,
                                sparse_output=False,
                            ),
                        ),
                    ]
                ),
                ["country"],
            ),
        ],
        verbose_feature_names_out=True,
    )
    return Pipeline(
        [
            ("features", BehaviorFeatureTransformer()),
            ("preprocess", preprocessor),
            ("model", estimator),
        ]
    )
