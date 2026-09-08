# ADR-002: Tenant isolation and authentication

Status: Accepted
Date: 2026-09-08
Authority: Project Lead decisions conveyed in founder's full local authorization.

## Context

Operational customer data must not cross tenant boundaries, including joins, jobs and artifacts.

## Decision

Use PostgreSQL 17 shared schema with tenant_id, composite tenant foreign keys, ENABLE/FORCE RLS, transaction-local context and non-owner/NOBYPASSRLS runtime role. Authenticate first, resolve membership, then set tenant context. Capabilities enforce RBAC. Production validates OIDC issuer/audience/signature/expiry; development tokens require explicit non-production mode and random local signing secret.

## Alternatives

Application filters alone miss raw SQL; schema-per-tenant adds migration overhead; tenant headers alone cannot authenticate ownership.

## Consequences

Migration role is separate from runtime. Denied/unknown resources use safe errors. Connection reuse must not retain context. Tests exercise direct SQL under actual runtime privileges.
