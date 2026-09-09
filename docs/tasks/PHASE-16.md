# PHASE-16 — Integration Hub

Status: COMPLETE — live providers not connected
Goal: Isolate provider details behind durable, tenant-safe synchronization contracts.
Context: External APIs need raw provenance, retries, health and canonical normalization.
In scope: Integration accounts, write-only secret references, sync runs, cursor/state,
private raw objects, canonical ad facts, outbox dispatch and adapter protocol.
Out of scope: Claiming a credentialed live synchronization.
Dependencies: Object storage, audit/outbox and tenant RLS.
Acceptance: No secret values in API data; raw payload checksum; explicit status/errors;
provider facts cannot leak across tenants.
Validation: Migrations, RBAC/tenant integration tests and adapter contract tests.
Risks: Provider schema/version changes and partial external outages.

Review: Meta/Google accounts are versioned and unique per tenant. Sync requests are
durable and membership is rechecked by the worker; raw bytes are privately stored,
bounded and hashed before normalized daily facts are inserted idempotently. Credentials
remain environment secret references. Live calls remain unvalidated without accounts.
