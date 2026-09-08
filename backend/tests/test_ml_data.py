from datetime import date

import pandas as pd
import pytest
from app.ml.data import build_snapshot, normalize_source, validate_source_coverage


def raw(rows: list[list[object]]) -> pd.DataFrame:
    return pd.DataFrame(
        rows,
        columns=[
            "invoice",
            "stock_code",
            "description",
            "quantity",
            "invoice_date",
            "unit_price",
            "customer_id",
            "country",
        ],
    )


def test_cutoff_and_horizon_boundaries_are_leakage_safe() -> None:
    source = raw(
        [
            ["A", "P1", "One", 1, "2010-05-02", 10, 1, "UK"],
            ["B", "P2", "Two", 2, "2010-05-22", 5, 2, "UK"],
            ["C", "P3", "Three", 1, "2009-12-01", 5, 3, "UK"],
            ["C4", "P4", "Cancel", 1, "2010-05-31", 5, 4, "UK"],
            ["AT", "P1", "One", 1, "2010-06-01", 999, 1, "UK"],
            ["H", "P2", "Two", 1, "2010-08-29 23:59:59", 5, 2, "UK"],
            ["BOUNDARY", "P5", "Five", 1, "2010-08-30", 5, 5, "UK"],
        ]
    )
    normalized, report = normalize_source(pd.concat([source, source.iloc[[0]]], ignore_index=True))
    assert report["exact_duplicates_removed"] == 1
    snapshot = build_snapshot(normalized, date(2010, 6, 1)).set_index("customer_id")
    assert set(snapshot.index) == {"1", "2"}
    assert snapshot.loc["1", "spend_365"] == 10
    assert snapshot.loc["1", "target_inactive_90d"] == 0
    assert snapshot.loc["2", "target_inactive_90d"] == 0

    # Move the only in-window future purchase exactly onto cutoff+90.
    boundary = normalized.copy()
    boundary.loc[boundary["invoice"] == "H", "invoice_date"] = pd.Timestamp("2010-08-30")
    result = build_snapshot(boundary, date(2010, 6, 1)).set_index("customer_id")
    assert result.loc["2", "target_inactive_90d"] == 1


def test_future_values_cannot_change_features() -> None:
    source = raw(
        [
            ["A", "P1", "One", 2, "2010-05-15", 10, 1, "UK"],
            ["F", "P2", "Future", 1, "2010-06-05", 1, 1, "UK"],
        ]
    )
    normalized, _ = normalize_source(source)
    first = build_snapshot(normalized, date(2010, 6, 1))
    normalized.loc[normalized["invoice"] == "F", ["quantity", "unit_price", "line_value"]] = [
        99,
        999,
        98901,
    ]
    second = build_snapshot(normalized, date(2010, 6, 1))
    pd.testing.assert_frame_equal(first, second)


def test_incomplete_final_window_is_rejected() -> None:
    frame, _ = normalize_source(raw([["A", "P", "One", 1, "2011-11-29", 1, 1, "UK"]]))
    with pytest.raises(ValueError, match="fully observe"):
        validate_source_coverage(frame)
