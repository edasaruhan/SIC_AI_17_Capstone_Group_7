"""Build frozen cutoff-safe snapshots and evidence manifest."""

import hashlib
import json
from pathlib import Path

from app.ml.data import (
    FEATURE_VERSION,
    SPLIT_VERSION,
    SPLITS,
    TARGET_VERSION,
    build_split,
    load_source,
    normalize_source,
    validate_source_coverage,
)

SOURCE = Path("data/raw/uci_online_retail_ii/source.zip")
OUTPUT = Path("data/processed/ml")
REPORT = Path("artifacts/reports/data_preparation.json")


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    normalized, cleaning = normalize_source(load_source(SOURCE))
    validate_source_coverage(normalized)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    splits: dict[str, dict[str, object]] = {}
    for name, cutoffs in SPLITS.items():
        frame = build_split(normalized, cutoffs)
        path = OUTPUT / f"{name}.parquet"
        frame.to_parquet(path, index=False)
        record: dict[str, object] = {
            "cutoffs": [value.isoformat() for value in cutoffs],
            "rows": len(frame),
            "columns": len(frame.columns),
            "sha256": checksum(path),
        }
        if name != "test":
            record["inactive_rows"] = int(frame["target_inactive_90d"].sum())
            record["inactive_rate"] = round(float(frame["target_inactive_90d"].mean()), 6)
        else:
            record["label_review_status"] = "sealed_until_final_evaluation"
        splits[name] = record
    manifest = {
        "target_version": TARGET_VERSION,
        "feature_version": FEATURE_VERSION,
        "split_version": SPLIT_VERSION,
        "source_sha256": checksum(SOURCE),
        "cleaning": cleaning,
        "splits": splits,
        "policy": [
            "Features use only events strictly before each cutoff.",
            "Final-test label prevalence and metrics are intentionally not reported here.",
            "Processed customer identifiers remain in ignored local artifacts only.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
