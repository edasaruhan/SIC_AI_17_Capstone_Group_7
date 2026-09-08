# PHASE-06 — Secure staged imports

Status: COMPLETE — bounded import and delivery workflow
Goal: Inspect, map, validate and atomically import customer/catalog source files.
Context: Canonical CRM/commerce APIs and tenant policies are executable.
In scope: Bounded CSV/XLSX parser, immutable raw storage, explicit mapping/preview,
row errors, durable commit workflow, retries, provenance and tenant authorization.
Out of scope: Provider synchronization, implicit destructive upserts, ML dataset ingestion.
Dependencies: PHASE-03/04/05 backend boundaries; PostgreSQL and storage abstraction.
Acceptance: Invalid files rejected; no partial canonical writes; retries do not
duplicate rows; errors are retrievable without leaking another tenant's data.
Validation: Adversarial parser unit tests and real PostgreSQL/API integration tests.
Risks: Parser bombs, PII retention and worker retries. Explicit resource limits and
private UUID-based object keys; production scanning/storage policy reviewed later.

Review: Parser adversarial cases, mapping/preview, tenant/role guards, same-key
collision, all-or-nothing commit conflict, replay, authorization revocation and
exhausted delivery tested. A real Redis/Dramatiq message committed a batch exactly
once. S3 is contract-tested with a stub; local storage isolation/immutability tested.
Files: imports/platform storage/jobs, 0004/0005 migrations, parser/import/worker/storage
tests; `docs/IMPORTS_AND_JOBS.md` includes contracts and exact limitations.
Limitations: Insert-only customers/catalog; other facts use their canonical APIs.
No production malware scanner or live S3 validation; retention hardening follows.
Decision required: None locally. Next: versioned analytics.
