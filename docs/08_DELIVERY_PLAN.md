# Delivery Plan

Status: The founder approved architecture and the full 24-phase local execution
roadmap on 2026-09-08. `docs/tasks/` is the current execution sequence. The M0–M12
grouping below is retained as a product-deliverable map, not a contradictory schedule.
No instructor submission dates have been changed or inferred.

## Scheduling constraint discovered in TASK-000

Instructor files state deadlines of 2026-08-16 for Literature/Data/Technology and 2026-08-30 for Concept Note/Implementation Plan. Both preceded repository initialization on 2026-09-08. The Product Owner/Project Lead must confirm submission status, revised dates if any, final-capstone dates, and team availability before calendar commitments are added.

## Internal milestones

These milestones sequence Release 1 work; later milestone placement does not mean “future scope.” Each requires a bounded task definition and evidence-based exit review.

### M0 — Project foundation and requirements

Expected evidence: verified official repository, preserved references, control documents, requirement matrices, decision register, risk register, and task log.

### M1 — Architecture and domain/data contracts

Expected evidence: approved stack/topology decisions, ADRs, bounded-domain contracts, tenancy/auth/RBAC strategy, canonical time/money/ID semantics, import/connector boundaries, test strategy, and initial deployment/observability direction.

### M2 — Dataset research and academic research deliverables

Expected evidence: cited literature and technology comparison, candidate-dataset register, licence/provenance review, reproducible profiling, selected dataset decision, and submitted/reviewed research deliverables.

### M3 — Data preparation, EDA, and feature pipeline

Expected evidence: approved Target Definition Memo, immutable/raw handling, validation results, temporal split design, reproducible EDA/figures, versioned feature definitions, leakage tests, and prepared datasets.

### M4 — Baseline and model exploration

Expected evidence: business/logistic baselines, candidate-model experiments, validation metrics, calibration/lift/top-k analysis, error analysis, reproducible artifacts, and model-exploration submission evidence.

### M5 — Model refinement and explainability

Expected evidence: validation-driven refinement, tuning records, imbalance/calibration decisions, frozen candidate/threshold, untouched-test evaluation, global/local explanation validation, and honest refinement/test submissions.

### M6 — Core SaaS foundation

Expected evidence: tenant-safe identity/access foundation, core API/UI shell, database/migrations, audit and observability baseline, CI quality gates, environment/secrets practices, and critical isolation tests.

### M7 — CRM and ERP-lite

Expected evidence: customer profiles/timeline/search, consent representation, products/categories, orders/items/refunds, inventory/movements, imports with error/provenance workflow, and tenant-safe integration tests.

### M8 — Analytics and customer-intelligence integration

Expected evidence: canonical KPI service, dashboard/customer 360, versioned RFM/value/segments, churn scoring/explanations, prioritization rules, and prediction/decision provenance.

### M9 — Marketing data and connectors

Expected evidence: verified Meta/Google capability matrix, provider-neutral contracts, authorization/account ownership, reliable metric/campaign sync, rate-limit/schema-drift handling, attribution evidence types, and contract tests/mocks clearly labeled where credentials are absent.

### M10 — Decision, audience, and campaign orchestration

Expected evidence: versioned audiences, recommendations, campaign drafts, budget-optimization prototype with constraints/uncertainty, review/approval/execution/audit lifecycle, provider-policy enforcement, and safe failure/stop controls.

### M11 — Security, observability, and production hardening

Expected evidence: threat/privacy review, access/isolation testing, upload/webhook/outbound protections, retention/export/deletion paths, performance/resilience checks, dependency security, alerts/runbooks, model/data/job monitoring, and deployment readiness review.

### M12 — Final capstone packaging and demo

Expected evidence: final requirements confirmation, reproducible figures/metrics, source-to-evidence map, honest limitations, demo workflow, editable and required submission artifacts, AI-use disclosure where required, final presentation, and clean-clone verification.

## Delivery controls

- The full local roadmap is authorized; continue through bounded, validated phases.
- Do not use test data or synthetic fixtures as academic results.
- A milestone is not complete without stored validation evidence and documentation updates.
- Dates, team assignments, capacity, and branch/PR policy remain open until confirmed.
