# Architecture Decision Register

Status: Pre-architecture register. No production technology stack has been approved.

## Decided

Only these high-level product principles are established:

- One production-oriented GrowthPilot project also supplies the capstone evidence.
- Release 1 is multi-tenant; tenant isolation and server-side authorization are mandatory.
- Provider-specific external schemas must be isolated behind connectors/adapters and normalized into canonical concepts.
- Marketing attribution must distinguish observed, platform-attributed, deterministic, inferred, and unknown claims.
- High-impact campaign and budget actions require human oversight and auditability.
- Churn classification is the initial capstone ML problem; its dataset, target, threshold, and winning model are not decided.
- LLMs are advisory consumers of trusted structured context, not sources of analytical truth.

These are constraints, not a selection of frameworks, vendors, storage engines, or deployment topology.

## Open architecture decisions

Every item below has the same status: **TBD — PROJECT LEAD DECISION REQUIRED**.

| Decision area | Questions to resolve | Status |
|---|---|---|
| Repository topology | Monorepo shape, package boundaries, academic/product organization | TBD — PROJECT LEAD DECISION REQUIRED |
| Backend language/framework | Runtime, framework, typing, operational fit | TBD — PROJECT LEAD DECISION REQUIRED |
| Frontend framework | UI framework, rendering model, design-system direction | TBD — PROJECT LEAD DECISION REQUIRED |
| Relational database | Engine, hosting model, local/test parity | TBD — PROJECT LEAD DECISION REQUIRED |
| ORM/query layer | Mapping/query approach and tenant-safety mechanisms | TBD — PROJECT LEAD DECISION REQUIRED |
| Migration tooling | Schema migration ownership and deployment rules | TBD — PROJECT LEAD DECISION REQUIRED |
| Tenancy model | Isolation strategy, tenant keys/policies, defense in depth | TBD — PROJECT LEAD DECISION REQUIRED |
| Authentication | Identity provider/session/token approach | TBD — PROJECT LEAD DECISION REQUIRED |
| RBAC | Roles, permissions, resource scopes, policy enforcement | TBD — PROJECT LEAD DECISION REQUIRED |
| API style | REST/RPC/GraphQL choice, versioning, error/idempotency contracts | TBD — PROJECT LEAD DECISION REQUIRED |
| Background jobs | Worker/runtime, retry semantics, job ownership | TBD — PROJECT LEAD DECISION REQUIRED |
| Scheduling | Sync/scoring/report cadence and scheduler ownership | TBD — PROJECT LEAD DECISION REQUIRED |
| Event model | Domain/integration events, delivery guarantees, outbox need | TBD — PROJECT LEAD DECISION REQUIRED |
| Cache | Whether a cache is needed, scope, invalidation, tenant isolation | TBD — PROJECT LEAD DECISION REQUIRED |
| Object/file storage | Uploads, raw payloads, datasets, reports, ML artifacts | TBD — PROJECT LEAD DECISION REQUIRED |
| Data import architecture | Staging, mapping, validation, partial failure, provenance | TBD — PROJECT LEAD DECISION REQUIRED |
| Connector architecture | Interfaces, auth boundary, checkpoints, retries, raw-payload retention | TBD — PROJECT LEAD DECISION REQUIRED |
| Warehouse/analytics | Operational queries versus analytical store/materialization | TBD — PROJECT LEAD DECISION REQUIRED |
| Canonical domain model | Aggregate boundaries, IDs, time/money semantics, ownership | TBD — PROJECT LEAD DECISION REQUIRED |
| Feature pipeline | Offline/online reuse, snapshot semantics, versioning | TBD — PROJECT LEAD DECISION REQUIRED |
| Experiment tracking | File/metadata approach or tracking platform | TBD — PROJECT LEAD DECISION REQUIRED |
| Model registry | Approval/version lifecycle and promotion rules | TBD — PROJECT LEAD DECISION REQUIRED |
| ML artifact storage | Format, integrity, retention, access control | TBD — PROJECT LEAD DECISION REQUIRED |
| Inference pattern | Batch versus online scoring and serving boundary | TBD — PROJECT LEAD DECISION REQUIRED |
| Scoring schedule | Cadence, triggers, freshness, backfill behavior | TBD — PROJECT LEAD DECISION REQUIRED |
| LLM provider abstraction | Provider boundary, structured context, safety and evaluation | TBD — PROJECT LEAD DECISION REQUIRED |
| Deployment | Platform, environments, networking, scaling, cost | TBD — PROJECT LEAD DECISION REQUIRED |
| Secrets | Secret manager, rotation, local-development policy | TBD — PROJECT LEAD DECISION REQUIRED |
| CI/CD | Quality gates, artifact promotion, deploy approvals | TBD — PROJECT LEAD DECISION REQUIRED |
| Observability | Logs, metrics, traces, errors, job/data/model monitoring | TBD — PROJECT LEAD DECISION REQUIRED |

## Decision process

Consequential approved choices receive an ADR in `docs/adr/` containing context, decision, alternatives, consequences, status, and date. Do not create speculative ADRs. Material proposed reversals follow the escalation format in `AGENTS.md`.
