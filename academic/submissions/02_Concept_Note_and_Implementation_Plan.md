# Concept Note and Implementation Plan

GrowthPilot AI — governed customer operations and marketing intelligence for small retail teams

**AI AUTHORSHIP DISCLOSURE:** This document was drafted with OpenAI Codex/ChatGPT assistance and checked against repository evidence. Human review remains required.

## Part I — Concept note

### 1. Project overview, context and intended impact

GrowthPilot AI is a multi-tenant, production-oriented application that unifies customer, order, product, inventory and advertising data; provides CRM/ERP-lite workflows; and turns versioned analytics and ML-supported evidence into reviewed marketing decisions. The first capstone ML problem is 90-day future-purchase inactivity classification. It is one component of the product, not the whole product.

The intended users are small retail operators and marketing managers who need a consistent customer record and a safer way to prioritize retention work. Intended impact is faster analysis, fewer definition disputes and more disciplined outreach review. No revenue uplift, adoption, campaign outcome or user result has yet been measured.

### 2. Objectives and KPIs

| Objective | KPI | Baseline | Target / decision rule |
| --- | --- | --- | --- |
| Unify operating data | Valid imports, rejected-row visibility, provenance coverage | No production baseline available | 100% of accepted imports record tenant, source, actor and checksum |
| Surface reliable customer intelligence | KPI freshness; prediction version coverage | No production baseline available | Every prediction stores model/feature/target versions and checksum |
| Prioritize limited outreach | Precision, recall and lift at capacity | Test prevalence 0.392857 | Frozen ~10% policy; report evidence, do not promise uplift |
| Protect customers and tenants | Cross-tenant denials; unauthorized actions | Not applicable before implementation | Zero known leakage in automated isolation tests; all actions server-authorized |
| Govern marketing execution | Consent checks; approvals; budget/kill-switch blocks | No live execution | Execution disabled by default; explicit approval and live validation required |

Targets are governance/quality acceptance rules, not fabricated commercial outcomes.

### 3. Background and rationale

The product concept responds to fragmentation: analytics notebooks alone do not resolve data capture, identity, permission, consent or execution safety. Literature on non-contractual customer bases shows that inactivity is latent and model-dependent. GrowthPilot therefore defines an observable future purchase window, uses time-based validation and stores a clear evidence trail.

### 4. AI methodology and evaluation

1. Profile purchase cadence on training history only and freeze a 90-day label horizon.

1. Construct leakage-safe customer snapshots using events strictly before each cutoff.

1. Compare a recency heuristic, a prevalence dummy, regularized logistic regression, random forest and LightGBM.

1. Select by validation PR-AUC; refine hyperparameters and probability calibration before touching the final test.

1. Freeze the model artifact and ~10% capacity threshold, evaluate once on the untouched 2011-09-01 temporal test and prohibit post-test retuning.

1. Validate SHAP/log-odds additivity; store local explanations as fitted-model evidence only.

Primary measures are PR-AUC, ROC-AUC, Brier score, log loss and ECE, with precision/recall/lift at capacity and bootstrap intervals on the final test. A later business-impact test must randomize eligible customers into treatment/control or use another defensible causal design.

### 5. Architecture and workflow

![Figure 1. Implemented data-to-decision architecture. Execution is disabled by default.](../../academic/figures/architecture_workflow.png)

*Figure 1. Implemented data-to-decision architecture. Execution is disabled by default.*

The web application calls a FastAPI modular monolith. PostgreSQL enforces tenant keys, constraints and row-level security; Redis/Dramatiq workers consume durable outbox jobs. Validated imports and provider adapters populate canonical records. Analytics and scoring share versioned definitions. Audiences are snapshot-based, current consent is checked, and campaigns must be approved before queueing. External action remains blocked by the kill switch and zero default budget.

### 6. Data

The capstone experiment uses UCI Online Retail II (Chen, 2012; CC BY 4.0; DOI 10.24432/C5CG6D), 1,067,371 transaction lines covering 2009-12-01 through 2011-12-09. Production use would require each tenant’s own authorized customer/order data and provider credentials. Raw sources are checksum-verified; customer-level prepared artifacts are local and ignored.

### 7. Literature and industry context

Jerath, Fader and Hardie (2011), Batislam et al. (2007), and Platzer and Reutterer (2016) motivate a purchase-cadence-aware but operational definition of inactivity. Modern CRM and ad platforms expose pieces of the workflow, but GrowthPilot’s concept is an integrated, provider-neutral control plane with explicit provenance, tenant scope and human authorization. This comparison is functional, not a claim of commercial superiority.

## Part II — Implementation plan

### 1. Technology stack

| Layer | Technology | Responsibility |
| --- | --- | --- |
| Web | Next.js, React, strict TypeScript | Operator navigation, honest loading/empty/error states, customer 360 |
| API | Python 3.12, FastAPI, Pydantic, SQLAlchemy | Validation, RBAC, domain rules, OpenAPI |
| Data | PostgreSQL + RLS; S3-compatible object boundary | Canonical records, provenance, tenant isolation, bounded raw payloads |
| Async | Redis, Dramatiq, outbox | Import, sync and scoring jobs with rechecked permissions |
| ML | pandas/Polars, scikit-learn, LightGBM, SHAP, MLflow | Feature pipeline, experiments, registry, explanations |
| Quality/ops | pytest, Ruff, mypy, Vitest, ESLint, OTel, Prometheus | Automated gates and observability |



### 2. Timeline and ownership

| Phase window | Work package | Owner / reviewer | Evidence / status |
| --- | --- | --- | --- |
| 2026-09-08 | Governance, architecture, domain and data contracts | Codex / Project Lead | Local commits; ADRs; requirements — complete |
| 2026-09-08 | Dataset research, preparation, features and model exploration | Codex / ML-AI Lead | Profiles, splits, MLflow runs — complete |
| 2026-09-08 | Refinement, frozen test, explanations and decision evidence | Codex / ML-AI Lead | Final artifacts and checksums — complete |
| 2026-09-09 | Inference, UI, integrations, attribution, audiences and generation | Codex / Project Lead | Local code/tests — complete; live credentials absent |
| 2026-09-09 | Security hardening, academic package and release readiness | Codex / Founder | Local validation — in final review |
| After approval | Credentialed sandboxes, deployment, pilot and causal impact test | Founder / Project Lead | External validation — not started |

These are actual local execution dates, not backdated instructor submission claims.

### 3. Milestones and evidence

- M0–M1: governance baseline, accepted ADRs, threat/data contracts and clean Git history.

- M2–M5: cited research, licensed source, reproducible preparation, model comparison, frozen evaluation and explanation evidence.

- M6–M10: tenant-safe API/UI, CRM/commerce/imports, intelligence, adapters, attribution, audiences and approval lifecycle.

- M11–M12: security/recovery boundaries, complete tests, academic deliverables, demo script and release-readiness report.

### 4. Challenges, mitigations and fallback plans

| Risk | Mitigation | Fallback / decision boundary |
| --- | --- | --- |
| Historical single-retailer bias | Temporal holdout, intervals, explicit evidence labels | Do not deploy model until tenant data is validated |
| Inactivity is not contractual churn | Operational label and target version | Present score as inactivity risk only |
| Cross-tenant leakage | Tenant keys, server guards, PostgreSQL RLS, adversarial tests | Block release on any unresolved leakage |
| Provider/API change or missing credentials | Adapters, fixed origins, mocks, durable sync records | Keep integration disabled; import CSV/XLSX |
| Uncertain campaign effect | Separate prediction from causal measurement | Use no-send planning mode until approved experiment |
| Unsafe generated content | Server-derived facts, forbidden-claim validation, human approval | Disabled provider; manual draft only |
| Operational outage/data loss | Health/metrics, backups/runbooks, durable jobs | RPO/RTO remain targets until restore drill |



### 5. Ethics and responsible AI

- Purpose limitation and minimization: customer-level outputs stay inside tenant scope; academic deliverables use aggregates.

- Consent and human agency: scoring never authorizes an action; audience membership is rechecked; approvals are explicit.

- Transparency: target, features, model, threshold and limitations are versioned; explanations are noncausal.

- Fairness: country and other sensitive/proxy effects require lawful subgroup review before production. No fairness claim is made from this dataset.

- Security: secret references, not secret values, are stored; provider requests use fixed HTTPS origins and no redirects.

### 6. Current delivery boundary

The local implementation and academic evidence are complete for review. Automated desktop/mobile Chromium and Axe checks pass; live Meta/Google/LLM/OIDC/cloud validation, production restore drills, manual multi-browser and assistive-technology testing, and any real campaign execution remain external. No push, paid deployment or advertising spend is authorized by this plan.

## References

Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

Jerath, K., Fader, P. S., & Hardie, B. G. S. (2011). New perspectives on customer “death” using a generalization of the Pareto/NBD model. Marketing Science, 30(5), 866–880. https://doi.org/10.1287/mksc.1110.0654

Batislam, E. P., Denizel, M., & Filiztekin, A. (2007). Empirical validation and comparison of models for customer base analysis. International Journal of Research in Marketing, 24(3), 201–209. https://doi.org/10.1016/j.ijresmar.2006.12.005

Project sources: docs/03_ARCHITECTURE_DECISIONS.md, docs/08_DELIVERY_PLAN.md, docs/07_SECURITY_PRIVACY_RESPONSIBLE_AI.md, artifacts/reports and artifacts/ml.
