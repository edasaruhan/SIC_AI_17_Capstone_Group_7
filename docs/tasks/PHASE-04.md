# PHASE-04 — Customer operations

Status: COMPLETE — CRM backend workflows
Goal: Usable tenant-safe customer profiles, search, notes/interactions and consent history.
In scope: Validated API contracts, pagination/filtering, immutable audit/outbox events.
Out of scope: ML-generated risk claims and live contact-channel delivery.
Dependencies: Identity/RLS migration and permission tests.
Acceptance: CRUD/search and interaction/consent round trips; no cross-tenant foreign
keys; analyst writes denied; failed changes leave no audit/outbox side effects.
Validation: Real PostgreSQL tests, API tests, strict types/lint and migration reruns.
Risks: PII in logs, reference leakage, unbounded lists, lost consent history.

Review: Create/read/update/search/tag/status, interaction timeline, append-only
consent history and audit/outbox rollback are tested through the API and PostgreSQL.
Files: crm modules, 0002 migration, test_crm.py. No hard-delete endpoint was added;
privacy erasure/export is a separately safeguarded hardening workflow.
Limitations: Full frontend integration is PHASE-15; real outbound messaging not implied.
Decision required: None. Next: commerce and inventory.
