import io
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import cast
from zipfile import ZipFile

import numpy as np
import pandas as pd

TARGET_VERSION = "future-inactivity-v1"
SPLIT_VERSION = "temporal-split-v1"
FEATURE_VERSION = "customer-behavior-v1"
HORIZON_DAYS = 90
ELIGIBILITY_DAYS = 180
LOOKBACK_DAYS = 365
SPLITS: dict[str, tuple[date, ...]] = {
    "train": tuple(date(2010, month, 1) for month in range(6, 13)),
    "validation": (date(2011, 3, 1),),
    "calibration": (date(2011, 6, 1),),
    "test": (date(2011, 9, 1),),
}


def load_source(source: Path) -> pd.DataFrame:
    with ZipFile(source) as archive:
        workbook = archive.read("online_retail_II.xlsx")
    sheets = pd.read_excel(io.BytesIO(workbook), sheet_name=None, engine="openpyxl")
    frame = pd.concat(sheets.values(), ignore_index=True)
    frame.columns = [
        "invoice",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
    ]
    return frame


def normalize_source(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    raw_rows = len(frame)
    frame = frame.drop_duplicates().copy()
    frame["invoice"] = frame["invoice"].astype("string").str.strip()
    frame["stock_code"] = frame["stock_code"].astype("string").str.strip()
    frame["country"] = frame["country"].astype("string").str.strip()
    frame["invoice_date"] = pd.to_datetime(frame["invoice_date"], errors="coerce", format="mixed")
    frame["customer_id"] = pd.to_numeric(frame["customer_id"], errors="coerce").astype("Int64")
    frame["quantity"] = pd.to_numeric(frame["quantity"], errors="coerce")
    frame["unit_price"] = pd.to_numeric(frame["unit_price"], errors="coerce")
    frame["is_cancellation"] = frame["invoice"].str.upper().str.startswith("C", na=False)
    frame["line_value"] = frame["quantity"] * frame["unit_price"]
    valid_identity = frame["customer_id"].notna() & frame["invoice_date"].notna()
    normalized = frame[valid_identity].copy()
    report = {
        "raw_rows": raw_rows,
        "exact_duplicates_removed": raw_rows - len(frame),
        "rows_without_usable_identity_or_date": len(frame) - len(normalized),
        "normalized_rows": len(normalized),
    }
    return normalized, report


def purchase_lines(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[
        ~frame["is_cancellation"]
        & (frame["quantity"] > 0)
        & (frame["unit_price"] > 0)
        & frame["stock_code"].notna()
    ].copy()


def purchase_events(lines: pd.DataFrame) -> pd.DataFrame:
    ordered = lines.sort_values(["customer_id", "invoice_date", "invoice"])
    return (
        ordered.groupby(["customer_id", "invoice", "invoice_date"], as_index=False)
        .agg(
            order_value=("line_value", "sum"),
            units=("quantity", "sum"),
            line_count=("stock_code", "size"),
            products=("stock_code", "nunique"),
            country=("country", "last"),
        )
        .sort_values(["customer_id", "invoice_date", "invoice"])
    )


def _days(cutoff: pd.Timestamp, values: pd.Series) -> pd.Series:
    return cast(pd.Series, (cutoff - values).dt.total_seconds() / 86400)


def validate_source_coverage(frame: pd.DataFrame) -> None:
    latest_required = pd.Timestamp(max(SPLITS["test"])) + pd.Timedelta(days=HORIZON_DAYS)
    latest_observed = frame["invoice_date"].max()
    if pd.isna(latest_observed) or latest_observed < latest_required:
        raise ValueError("Source does not fully observe the frozen final label window")


def build_snapshot(frame: pd.DataFrame, cutoff_date: date) -> pd.DataFrame:
    cutoff = pd.Timestamp(cutoff_date)
    horizon = cutoff + pd.Timedelta(days=HORIZON_DAYS)
    lines = purchase_lines(frame)
    events = purchase_events(lines)
    recent_start = cutoff - pd.Timedelta(days=ELIGIBILITY_DAYS)
    lookback_start = cutoff - pd.Timedelta(days=LOOKBACK_DAYS)
    recent = events[(events["invoice_date"] >= recent_start) & (events["invoice_date"] < cutoff)]
    eligible = pd.Index(recent["customer_id"].unique(), name="customer_id")
    history = events[
        events["customer_id"].isin(eligible)
        & (events["invoice_date"] >= lookback_start)
        & (events["invoice_date"] < cutoff)
    ].copy()
    all_history = events[events["customer_id"].isin(eligible) & (events["invoice_date"] < cutoff)]
    features = history.groupby("customer_id").agg(
        purchase_count_365=("invoice", "size"),
        spend_365=("order_value", "sum"),
        units_365=("units", "sum"),
        avg_order_value_365=("order_value", "mean"),
        max_order_value_365=("order_value", "max"),
        order_value_std_365=("order_value", "std"),
        avg_basket_units_365=("units", "mean"),
        avg_products_per_order_365=("products", "mean"),
        last_purchase=("invoice_date", "max"),
        country=("country", "last"),
    )
    trailing_90 = history[history["invoice_date"] >= cutoff - pd.Timedelta(days=90)]
    ninety = trailing_90.groupby("customer_id").agg(
        purchase_count_90=("invoice", "size"),
        spend_90=("order_value", "sum"),
        units_90=("units", "sum"),
    )
    product_history = lines[
        lines["customer_id"].isin(eligible)
        & (lines["invoice_date"] >= lookback_start)
        & (lines["invoice_date"] < cutoff)
    ]
    products = (
        product_history.groupby("customer_id")["stock_code"].nunique().rename("unique_products_365")
    )
    firsts = all_history.groupby("customer_id")["invoice_date"].min().rename("first_purchase")
    all_counts = all_history.groupby("customer_id").size().rename("purchase_count_observed")
    history["gap_days"] = (
        history.groupby("customer_id")["invoice_date"].diff().dt.total_seconds() / 86400
    )
    gap_features = history.groupby("customer_id")["gap_days"].agg(
        mean_gap_days_365="mean", std_gap_days_365="std", last_gap_days="last"
    )
    returns = frame[
        frame["customer_id"].isin(eligible)
        & (frame["invoice_date"] >= lookback_start)
        & (frame["invoice_date"] < cutoff)
        & (frame["is_cancellation"] | (frame["quantity"] < 0))
    ].copy()
    returns["return_value"] = returns["line_value"].abs()
    return_features = returns.groupby("customer_id").agg(
        return_line_count_365=("invoice", "size"), return_value_365=("return_value", "sum")
    )
    result = features.join([ninety, products, firsts, all_counts, gap_features, return_features])
    result["recency_days"] = _days(cutoff, result.pop("last_purchase"))
    result["tenure_days"] = _days(cutoff, result.pop("first_purchase"))
    zero_columns = [
        "purchase_count_90",
        "spend_90",
        "units_90",
        "order_value_std_365",
        "return_line_count_365",
        "return_value_365",
    ]
    result[zero_columns] = result[zero_columns].fillna(0)
    result["return_value_share_365"] = (
        result["return_value_365"] / result["spend_365"].replace(0, np.nan)
    ).fillna(0)
    result["cutoff_month_sin"] = np.sin(2 * np.pi * cutoff.month / 12)
    result["cutoff_month_cos"] = np.cos(2 * np.pi * cutoff.month / 12)
    future_customers = set(
        events[(events["invoice_date"] >= cutoff) & (events["invoice_date"] < horizon)][
            "customer_id"
        ]
    )
    result["target_inactive_90d"] = [
        int(customer not in future_customers) for customer in result.index
    ]
    result["snapshot_cutoff"] = cutoff
    result["customer_id"] = result.index.astype("int64").astype("string")
    result["target_version"] = TARGET_VERSION
    result["feature_version"] = FEATURE_VERSION
    result["split_version"] = SPLIT_VERSION
    return result.reset_index(drop=True).sort_values(["snapshot_cutoff", "customer_id"])


def build_split(frame: pd.DataFrame, cutoffs: Iterable[date]) -> pd.DataFrame:
    snapshots = [build_snapshot(frame, cutoff) for cutoff in cutoffs]
    return pd.concat(snapshots, ignore_index=True)
