# Architecture decision register

Approved by Project Lead through founder authorization on 2026-09-08. This replaces
the TASK-000 stack TBD register. Status describes decisions, not implementation.

| Area | Accepted decision | Record |
|---|---|---|
| Repository and backend | Monorepo; Python 3.12, FastAPI, Pydantic 2, SQLAlchemy 2, Alembic; modular monolith | ADR-001 |
| Frontend and contracts | Next.js, React, strict TypeScript, Tailwind, shadcn/ui; REST/OpenAPI typed contracts | ADR-001 |
| Database and tenancy | PostgreSQL shared schema; tenant keys, RLS and application guards; restricted runtime role | ADR-002 |
| Identity | Provider-neutral OIDC/OAuth2/JWT; explicitly gated development auth; managed production IdP | ADR-002 |
| Permissions | Owner/admin/marketing manager/analyst/operator mapped to server capabilities | ADR-002 |
| Jobs and events | Redis + Dramatiq; transactional PostgreSQL outbox and durable workflow state; bounded retries | ADR-003 |
| Storage and analytics | S3 interface, local filesystem option; PostgreSQL analytics/versioned transformations; no initial warehouse | ADR-003 |
| Imports and connectors | Secure staged CSV/XLSX imports; provider adapters, raw provenance, checkpoints | ADR-003 |
| Marketing | Deterministic identity and baseline last-touch attribution; auditable audiences/actions and spend controls | ADR-004 |
| Generative AI | Provider abstraction, verified structured facts, human-authorized actions | ADR-004 |
| ML | pandas/Polars, sklearn, LightGBM, SHAP; justified XGBoost/Optuna; matplotlib; MLflow tracking/registry | ADR-005 |
| ML execution | Offline training; shared versioned features; batch and on-demand inference in backend/workers | ADR-005 |
| Operations | Compose-compatible local services; container workloads, Terraform AWS reference; OTel-compatible instrumentation | ADR-006 |
| Quality | Ruff, strict typing, pytest; ESLint, tsc, Vitest and critical-flow Playwright; GitHub Actions | ADR-006 |

Deployment-specific IdP, domains, provider accounts, paid infrastructure, legal
obligations, retention periods and live validation remain configuration or external
readiness items. Dataset and churn target must be justified by research; the latest
authorization permits implementation-side selection from evidence and a written memo.

Sources verified for initial implementation on 2026-09-08:

- [PostgreSQL RLS](https://www.postgresql.org/docs/17/ddl-rowsecurity.html)
- [SQLAlchemy transactions](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)
- [FastAPI JWT integration](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Next.js installation](https://nextjs.org/docs/app/getting-started/installation)

Consequential departures still require an evidence-backed escalation. Ordinary
implementation details follow the accepted architecture and are documented locally.
