# PHASE-03 — Canonical foundation, tenancy and identity

Status: COMPLETE — canonical/auth foundation
Goal: Establish authenticated membership, capability checks and real database isolation.
In scope: User/organization/membership, Alembic, restricted roles, transaction-local
tenant context, OIDC/dev boundaries, cross-tenant API/direct-SQL tests.
Out of scope: Password management, live IdP provisioning, commercial data ingestion.
Dependencies: Approved ADR-002 and executable local PostgreSQL.
Acceptance: Wrong-tenant reads/writes fail; pooled context resets; forged/expired
tokens and inactive membership fail; runtime cannot own/bypass RLS; migrations run.
Validation: PostgreSQL integration tests and API tests with synthetic fixtures.
Risks: Role-owner RLS bypass, insecure dev auth, forged tenant header, unsafe error details.

Review: Migration/runtime roles separated; real PostgreSQL policies enforce both
application-filtered and unfiltered access; foreign header, inactive membership,
expired/forged/wrong-audience tokens, owner/bypass and pool reset tests pass.
Files: identity/platform modules, 0001 migration, identity/config integration tests.
Limitations: Managed IdP live validation, onboarding/team UI and release hardening
remain tracked later; no production-auth validation against a real IdP is claimed.
Decision required: None locally. Next: CRM operations.
