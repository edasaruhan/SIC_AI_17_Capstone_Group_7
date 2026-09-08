# ADR-006: Local and production operations

Status: Accepted
Date: 2026-09-08
Authority: Project Lead decisions conveyed in founder's full local authorization.

## Context

Development must be reproducible without purchasing cloud infrastructure.

## Decision

Use uv/locked Python dependencies and pnpm/locked frontend dependencies. Local PostgreSQL/Redis via Compose or scoped native services. CI runs formatting/lint/types/tests/build/security. OTel-compatible logs/request/job IDs, readiness and metrics. Containerized workloads and Terraform reference for AWS runtime/RDS/Redis/S3/secrets/TLS/logs.

## Alternatives

Unpinned installs break reproducibility; manually provisioned infrastructure is hard to audit; automatic paid deployment is unauthorized.

## Consequences

Provider account settings and backup RPO/RTO are explicit deployment requirements, not achieved service claims. Database restore must be rehearsed. Remote CI and cloud deployment require later authorized access.
