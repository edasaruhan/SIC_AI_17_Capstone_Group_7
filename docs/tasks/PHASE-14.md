# PHASE-14 — Registry and safe inference

Status: COMPLETE
Goal: Preserve immutable model lineage and serve auditable tenant-safe demo inference.
Context: The external-retailer candidate is frozen and evaluated but not domain-validated.
In scope: Local MLflow registration, checksum enforcement, canonical feature extraction,
append-only RLS predictions, permissions, API and audit/outbox evidence.
Out of scope: Non-demo production scoring, automatic action or managed deployment.
Dependencies: PHASE-13 decision contract and canonical commerce/consent data.
Acceptance: Registered alias resolves to frozen checksum; inference is demo-gated,
tenant-scoped, reproducible and never authorizes an action.
Validation: Migration, registry report, static checks and integration/checksum tests.
Risks: Cross-domain model shift, artifact deserialization trust and feature skew.

Review: The frozen checksum was registered locally as
`growthpilot-churn-inactivity@champion`, version 1, run
`6259c8ebe3744b5aac04c1b70cedbb26`. On-demand demo scoring reconstructs the
central feature contract and stores append-only tenant-scoped provenance. Batch
scoring has durable PostgreSQL state and an outbox worker command that rechecks
membership/capability. Non-demo use stays hard-gated pending domain validation.
Three inference tests plus decision tests cover checksum, eligibility and isolation.
Next: production web integration.
