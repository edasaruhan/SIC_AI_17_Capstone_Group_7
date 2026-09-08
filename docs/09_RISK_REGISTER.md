# Risk Register

Status: Initial qualitative register created 2026-09-08. Likelihood is Low/Medium/High only; no unsupported numeric probabilities are implied.

| Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| Release 1 breadth exceeds available capacity | High | High | Deliver through bounded internal milestones; define acceptance gates; Project Lead controls sequencing without silently deleting scope | Product Owner / Project Lead | Open |
| Confirmed assignment deadlines elapsed before initialization | High | High | Confirm submission status and revised/final dates immediately; re-plan from authoritative instructor direction | Product Owner / Project Lead | Open — decision needed |
| Capstone schedule pressure reduces methodological depth | High | High | Prioritize research/target validity/reproducible baseline evidence; keep product tasks bounded and evidence-linked | Project Lead | Open |
| Candidate dataset is unsuitable or unlicensed | Medium | High | Use a scored candidate register covering provenance, licence, access, temporal depth, repeat behavior, and target feasibility before selection | Project Lead | Open |
| Churn definition is commercially or statistically invalid | Medium | High | Require purchase-cycle/censoring analysis and an approved Target Definition Memo before labels | Project Lead | Open |
| Temporal leakage inflates model performance | High | Critical | Cutoff-safe snapshots, temporal validation, frozen holdout, pipeline-fit isolation, and automated leakage/split tests | Project Lead / Codex | Open |
| Class imbalance makes headline metrics misleading | Medium | High | Report PR-AUC, calibration, lift/top-k capture, confusion/cost tradeoffs; tune threshold on validation only | Project Lead / Codex | Open |
| Academic reports diverge from product reality | Medium | Critical | One repository/source of truth; provenance maps; generate reports from real outputs; audit claims against code/artifacts | Project Lead / Codex | Open |
| Meta API permissions/policies block required operations | Medium | High | Verify current official docs and app-review/scopes; separate ingestion/draft/publish capabilities; provide honest, approved fallback | Project Lead / Codex | Open |
| Google Ads permissions/policies block required operations | Medium | High | Verify developer-token/OAuth/account requirements and policies; use provider boundaries and capability matrix | Project Lead / Codex | Open |
| Attribution is ambiguous or double counted | High | High | Persist evidence class, method/window/version, deterministic confidence, unknown amounts, and deduplication rules | Project Lead | Open |
| Privacy or marketing-consent misuse | Medium | Critical | Data minimization, consent/purpose enforcement, lifecycle controls, auditability, and qualified legal review before compliance claims | Product Owner / Project Lead | Open |
| Cross-tenant data leakage | Medium | Critical | Tenant keys/policies, server-side authz, scoped jobs/artifacts, defense in depth, and negative isolation tests | Project Lead / Codex | Open |
| LLM hallucinates facts or unsafe marketing claims | High | High | Structured trusted context, schema validation, unsupported-claim tests, brand/policy filters, and human review | Project Lead / Codex | Open |
| Automated campaign action causes uncontrolled spend | Medium | Critical | Draft/review/approval/execution gates, limits, exact-payload audit, idempotency, provider validation, and stop controls | Product Owner / Project Lead / Codex | Open |
| Provider rate limits or outages corrupt sync state | High | High | Checkpoints, idempotency, bounded retry/backoff, rate-limit handling, replay safety, and visible partial failure | Codex | Open |
| External provider schema drift causes silent corruption | Medium | High | Contract/schema validation, raw-payload provenance, quarantine, alerts, and versioned mappings | Codex | Open |
| Data/model drift degrades recommendations | Medium | High | Monitor input quality, score/feature distributions, calibration/performance when labels arrive, and retraining approval | Project Lead / Codex | Open |
| Overengineering consumes time and operating budget | Medium | High | Approve architecture against measured needs; avoid premature microservices, streaming, or platform additions | Project Lead / Codex | Open |
| Coding-agent changes become inconsistent | Medium | High | Enforce `AGENTS.md`, bounded tasks, control-doc updates, ADRs, tests, and structured handoffs | Project Lead / Codex | Open |
| Limited Codex usage budget reduces throughput | Medium | Medium | Persist decisions, avoid rescans/rework, prefer small high-value tasks, and use reproducible commands | Product Owner / Project Lead / Codex | Open |
| Documentation drifts from implementation | Medium | High | Documentation is part of acceptance; review affected control docs/task log/ADRs in every significant task | Codex | Open |
| Weekly-report reference is mistaken for Group 7 evidence | Medium | High | Label as a Group 10 example only; never copy claims; obtain a blank/current template or recreate only verified field structure | Project Lead / Codex | Open |
| Original presentation statistics or technical claims are reused without verification | Medium | High | Preserve citations, verify source/date/scope before reuse, and treat LightGBM/SHAP statements as hypotheses until evidence supports them | Project Lead | Open |

## Review rule

Update this register when evidence changes likelihood, impact, ownership, mitigation, or status. “Open” does not mean accepted; it means not yet closed by evidence or decision.
