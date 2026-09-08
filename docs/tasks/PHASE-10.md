# PHASE-10 — Versioned feature engineering

Status: COMPLETE — shared transformation contract
Goal: Centralize training/inference-safe features and preprocessing contracts.
Context: `customer-behavior-v1` snapshots contain only pre-cutoff behavior.
In scope: Feature definitions, model columns, missingness semantics, learned
preprocessing, skew handling, unknown categories and training/inference parity tests.
Out of scope: Model-family winner, SHAP claims, provider data or final-test access.
Dependencies: PHASE-09 frozen target/split and local prepared snapshots.
Acceptance: Identifiers/targets/cutoffs cannot enter model matrix; transformers fit
on training only; unknown categories and missing short-history gaps are supported.
Validation: Column allowlist and serialization/parity tests with synthetic frames.
Risks: leakage through convenience columns, unstable categories, outliers and
inconsistent on-demand feature computation.

Review: `BehaviorFeatureTransformer` allowlists all model inputs, creates versioned
log transformations and excludes identity/target/cutoff/version fields even when a
full snapshot is passed. Learned imputation, missingness indicators, robust scaling
and unknown-country handling live in the serialized pipeline. Tests mutate forbidden
columns, reject missing/negative values and prove joblib probability parity.
Files: `app/ml/features.py`, `FEATURE_CONTRACT.md`, feature tests.
Limitations: Monetary outliers remain represented after log transform; country proxy
risk requires interpretation review. Production event-to-feature persistence follows
model evaluation and registry.
Decision required: None. Next: fixed baseline/model-family exploration.
