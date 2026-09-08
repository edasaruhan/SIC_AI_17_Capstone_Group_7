"""Training-only EDA; never reads calibration or final-test artifacts."""

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", ".cache/matplotlib")

import matplotlib.pyplot as plt
import pandas as pd

SOURCE = Path("data/processed/ml/train.parquet")
OUTPUT = Path("artifacts/eda")


def main() -> None:
    frame = pd.read_parquet(SOURCE)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    figure, axes = plt.subplots(1, 2, figsize=(10, 4))
    frame["target_inactive_90d"].value_counts().sort_index().plot.bar(
        ax=axes[0], color=["#2f6f55", "#d08b45"]
    )
    axes[0].set(title="Training snapshot labels", xlabel="Inactive in next 90 days", ylabel="Rows")
    axes[1].hist(frame["recency_days"], bins=30, color="#2f6f55")
    axes[1].set(title="Training recency", xlabel="Days", ylabel="Snapshot rows")
    figure.tight_layout()
    figure.savefig(OUTPUT / "training_label_recency.png", dpi=160)
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(10, 4))
    frequency_limit = frame["purchase_count_365"].quantile(0.99)
    axes[0].hist(
        frame.loc[frame["purchase_count_365"] <= frequency_limit, "purchase_count_365"],
        bins=25,
        color="#315c75",
    )
    axes[0].set(title="Purchase frequency (through training p99)", xlabel="Events", ylabel="Rows")
    spend_limit = frame["spend_365"].quantile(0.99)
    axes[1].hist(
        frame.loc[frame["spend_365"] <= spend_limit, "spend_365"],
        bins=30,
        color="#315c75",
    )
    axes[1].set(title="Spend (visualized through training p99)", xlabel="GBP", ylabel="Rows")
    figure.tight_layout()
    figure.savefig(OUTPUT / "training_frequency_spend.png", dpi=160)
    plt.close(figure)

    summary = {
        "evidence": "project_reproduced_training_split_only",
        "rows": len(frame),
        "customers": int(frame["customer_id"].nunique()),
        "cutoffs": sorted(
            pd.Timestamp(value).isoformat() for value in frame["snapshot_cutoff"].unique()
        ),
        "inactive_rate": round(float(frame["target_inactive_90d"].mean()), 6),
        "recency_days": frame["recency_days"].describe().round(3).to_dict(),
        "purchase_count_365": frame["purchase_count_365"].describe().round(3).to_dict(),
        "spend_365": frame["spend_365"].describe().round(3).to_dict(),
        "missing_values": {
            column: int(count) for column, count in frame.isna().sum().items() if count
        },
        "countries": int(frame["country"].nunique()),
        "limitations": [
            "Repeated customer snapshots are expected for recurring operational scoring.",
            "Rows above training p99 are omitted from two plots only; tables retain them.",
            "No calibration or final-test artifact was read.",
        ],
    }
    (OUTPUT / "training_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
