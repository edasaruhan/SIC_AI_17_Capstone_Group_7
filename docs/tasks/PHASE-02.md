# PHASE-02 — Reproducible tooling and local infrastructure

Status: COMPLETE — local foundation; hosted CI execution remains external
Goal: Executable locked backend/frontend environment, local infrastructure and CI.
In scope: Package locks, strict lint/types/tests, local setup, CI and health endpoints.
Out of scope: Paid deployment, live provider calls, dataset experiments.
Dependencies: Accepted ADRs; installed Python 3.12, Node 22, PostgreSQL 17.
Acceptance: Clean dependency install; quality commands run; isolated local database
and runtime role available; repeat setup preserves local state.
Validation: uv lock/sync, quality commands, actual DB connectivity and role checks.
Risks: Network downloads and local process permissions; isolate from existing services.

Review: Python/uv and pnpm locks installed; Next.js production build, tsc and ESLint
passed. Python quality gates and real PostgreSQL/Redis tests passed in the foundation
suite. CI has read-only repository permissions and immutable action pins; not run on
GitHub because push is forbidden. Local setup preserves existing `.env`/databases;
Redis startup readiness race was corrected and repeat setup verified.
Files: pyproject/uv lock, package/pnpm locks, apps/web shell, scripts, CI workflow.
Limitations: Container/Terraform release profile and full UI tests belong to later phases.
Decision required: None for continuation. Next: canonical domain foundation.
