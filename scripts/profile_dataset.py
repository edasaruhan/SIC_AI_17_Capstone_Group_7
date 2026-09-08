"""Generate a deterministic structural and purchase-cycle profile; no labels/models."""

import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

SOURCE = Path("data/raw/uci_online_retail_ii/source.zip")
OUTPUT = Path("artifacts/reports/dataset_profile.json")


def quantiles(series: pd.Series) -> dict[str, float]:
    return {
        str(key): round(float(value), 3)
        for key, value in series.quantile([0.25, 0.5, 0.75, 0.9, 0.95]).items()
    }


def main() -> None:
    with ZipFile(SOURCE) as archive:
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
    frame["invoice"] = frame["invoice"].astype("string")
    frame["invoice_date"] = pd.to_datetime(frame["invoice_date"], errors="coerce")
    frame["customer_id"] = pd.to_numeric(frame["customer_id"], errors="coerce").astype("Int64")
    cancellation = frame["invoice"].str.upper().str.startswith("C", na=False)
    purchase = frame[
        frame["customer_id"].notna()
        & frame["invoice_date"].notna()
        & (frame["quantity"] > 0)
        & (frame["unit_price"] > 0)
        & ~cancellation
    ].copy()
    events = (
        purchase[["customer_id", "invoice", "invoice_date"]]
        .drop_duplicates()
        .sort_values(["customer_id", "invoice_date", "invoice"])
    )
    events["gap_days"] = (
        events.groupby("customer_id")["invoice_date"].diff().dt.total_seconds() / 86400
    )
    gaps = events["gap_days"].dropna()
    purchases_per_customer = events.groupby("customer_id")["invoice"].nunique()
    profile = {
        "profile_version": "dataset-profile-v1",
        "evidence": "project_reproduced_from_external_source",
        "source": {
            "dataset": "UCI Online Retail II",
            "doi": "10.24432/C5CG6D",
            "license": "CC BY 4.0",
            "url": "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip",
            "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "size_bytes": SOURCE.stat().st_size,
        },
        "sheets": {name: int(len(sheet)) for name, sheet in sheets.items()},
        "raw": {
            "rows": int(len(frame)),
            "columns": list(frame.columns),
            "date_min": frame["invoice_date"].min().isoformat(),
            "date_max": frame["invoice_date"].max().isoformat(),
            "missing_customer_rows": int(frame["customer_id"].isna().sum()),
            "missing_description_rows": int(frame["description"].isna().sum()),
            "invalid_date_rows": int(frame["invoice_date"].isna().sum()),
            "cancellation_rows": int(cancellation.sum()),
            "nonpositive_quantity_rows": int((frame["quantity"] <= 0).sum()),
            "nonpositive_price_rows": int((frame["unit_price"] <= 0).sum()),
            "exact_duplicate_rows": int(frame.duplicated().sum()),
            "identified_customers": int(frame["customer_id"].nunique()),
            "invoices": int(frame["invoice"].nunique()),
            "countries": int(frame["country"].nunique()),
        },
        "eligible_purchase_lines": int(len(purchase)),
        "purchase_events": int(len(events)),
        "purchase_customers": int(events["customer_id"].nunique()),
        "customers_with_2plus_events": int((purchases_per_customer >= 2).sum()),
        "purchases_per_customer_quantiles": quantiles(purchases_per_customer),
        "interpurchase_gap_days_quantiles": quantiles(gaps),
        "interpurchase_gap_observations": int(len(gaps)),
        "notes": [
            "Eligible purchases are identified, dated, positive quantity/price, "
            "non-cancellation invoice lines.",
            "Same invoice/customer/time is one purchase event; product lines remain "
            "available for feature construction.",
            "Cancellations/returns are retained in raw data and excluded only from "
            "purchase-event cadence.",
            "Profile statistics describe this historical source and are not product "
            "or model results.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(profile, indent=2) + "\n")
    print(json.dumps(profile, indent=2))


if __name__ == "__main__":
    main()
