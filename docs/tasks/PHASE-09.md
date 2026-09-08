# PHASE-09 — Target definition, preparation and EDA

Status: COMPLETE — target frozen, snapshots and EDA reproduced
Goal: Build cutoff-safe learning snapshots only after freezing an operational target.
Context: Selected data has a 24.197-day median and 134.134-day 90th-percentile
observed interpurchase gap; attrition itself is not observed.
In scope: Target memo, versioned cleaning, time splits, censored-window controls,
data-quality assertions and training-only EDA.
Out of scope: Feature/model selection using final holdout results, deployment scoring.
Dependencies: Completed dataset decision/profile.
Acceptance: No feature occurs at/after cutoff; every label window is complete; raw
data unchanged; test statistics/labels remain outside tuning evidence.
Validation: Deterministic data hashes, boundary tests, split/cutoff assertions and
reproduced EDA artifacts.
Risks: Future leakage, duplicate customers across scoring dates, holiday shift,
ambiguous inactivity labels and selection bias from identified-only customers.

Review: Target/horizon/population/splits were frozen before constructing labels.
Exact boundary and future-value mutation tests verify cutoff isolation; incomplete
final windows fail. The checksum-pinned source produced deterministic Parquet split
hashes and training-only EDA; no final-test prevalence/metric was opened.
Results: training 20,677 rows/4,250 customers, 48.3823% operational inactivity;
validation 3,349/57.7187%; calibration 2,659/49.9436%; final test 2,772 sealed rows.
Cleaning removed 34,335 exact duplicates and excluded 235,151 remaining rows lacking
usable identity/date from supervised snapshots. Missing gap features are explicit for
short histories and handled inside fitted preprocessing.
Files: `TARGET_DEFINITION.md`, `app/ml/data.py`, preparation/EDA scripts, boundary
tests, data-preparation manifest and training-only EDA images/summary.
Limitations: label is an inactivity proxy; repeated customer snapshots and source/
historical retailer bias are explicit. Processed tables remain ignored local data.
Decision required: None. Next: centralize and validate feature/model contracts.
