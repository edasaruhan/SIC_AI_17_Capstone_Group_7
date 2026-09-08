import joblib
import numpy as np
import pandas as pd
import pytest
from app.ml.features import (
    FORBIDDEN_FEATURES,
    MODEL_FEATURES,
    BehaviorFeatureTransformer,
    model_pipeline,
)
from sklearn.linear_model import LogisticRegression


def frame() -> pd.DataFrame:
    from app.ml.features import RAW_NUMERIC_FEATURES

    values = {name: [1.0, 2.0, 3.0, 4.0] for name in RAW_NUMERIC_FEATURES}
    values["mean_gap_days_365"] = [np.nan, 2, 3, 4]
    values["std_gap_days_365"] = [np.nan, np.nan, 3, 4]
    return pd.DataFrame({**values, "country": ["UK", "TR", "UK", "TR"]})


def test_allowlist_excludes_identity_target_and_convenience_columns() -> None:
    values = frame()
    for name in FORBIDDEN_FEATURES:
        values[name] = "would-leak"
    transformed = BehaviorFeatureTransformer().fit_transform(values)
    assert tuple(transformed.columns) == MODEL_FEATURES
    assert not FORBIDDEN_FEATURES.intersection(transformed.columns)
    changed = values.copy()
    changed[list(FORBIDDEN_FEATURES)] = "changed-future-or-identity"
    pd.testing.assert_frame_equal(transformed, BehaviorFeatureTransformer().transform(changed))


def test_missing_or_negative_feature_fails() -> None:
    values = frame().drop(columns="recency_days")
    with pytest.raises(ValueError, match="Missing required"):
        BehaviorFeatureTransformer().fit(values)
    values = frame()
    values.loc[0, "spend_365"] = -1
    with pytest.raises(ValueError, match="nonnegative"):
        BehaviorFeatureTransformer().transform(values)


def test_unknown_category_missingness_and_serialization(tmp_path) -> None:
    values = frame()
    target = pd.Series([0, 1, 0, 1])
    pipeline = model_pipeline(LogisticRegression(random_state=17), scale=True)
    pipeline.fit(values, target)
    candidate = values.iloc[[0]].copy()
    candidate["country"] = "NEW"
    before = pipeline.predict_proba(candidate)
    path = tmp_path / "model.joblib"
    joblib.dump(pipeline, path)
    after = joblib.load(path).predict_proba(candidate)
    np.testing.assert_allclose(before, after)
