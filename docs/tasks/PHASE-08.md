# PHASE-08 — Dataset and academic research

Status: COMPLETE — dataset selected and profiled before labels
Goal: Select a lawful, reproducible dataset and ground ML/technology choices in sources.
Context: Release 1 requires non-contractual retail churn classification, where
customer departure is unobserved and must be operationally labeled.
In scope: Candidate comparison, licence/provenance, actual raw-file checksum/profile,
peer-reviewed churn/customer-base literature, approved-stack technology sources.
Out of scope: Labels, features, model fitting or performance claims.
Dependencies: Instructor research requirements and ADR-005.
Acceptance: Dataset decision explains tradeoffs and licence; raw source is reproducible;
research distinguishes non-contractual inactivity from observed contractual churn.
Validation: Official metadata, source checksum, structural/data-quality profiling.
Risks: Historical single-retailer bias, unobserved churn, missing customer IDs,
returns/cancellations and seasonal cutoff censoring.

Review: Four candidates were compared using official metadata/access terms. Online
Retail II was selected for two-year customer-level temporal evidence and explicit
CC BY 4.0 reuse; the exact downloaded archive was pinned and profiled. Peer-reviewed
non-contractual customer-base work established the latent-churn limitation. Approved
technology roles and non-causal boundaries are documented in the research foundation.
Files: `DATASET_DECISION.md`, `RESEARCH_FOUNDATION.md`, download/profile scripts and
`artifacts/reports/dataset_profile.json`.
Results: 1,067,371 lines, 5,878 eligible purchasing customers and 31,155 observed
interpurchase gaps; full exclusions/quantiles are machine readable.
Limitations: Single historical UK retailer, wholesale mix, no ad exposure/consent/
explicit churn. Raw source is ignored and must be reproduced locally.
Decision required: None. Next: freeze target definition before labels.
