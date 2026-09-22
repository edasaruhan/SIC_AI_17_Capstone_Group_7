# Production-readiness report

Date: 2026-09-22
Status: **LOCAL BUILD COMPLETE — NOT APPROVED FOR PRODUCTION DEPLOYMENT**

## Executive decision

The authorized 24-phase local roadmap and Project Lead academic-package audit are complete. The application,
frozen ML evidence, academic package, container definitions and AWS Terraform reference exist and
pass the locally executable gates. Production approval is withheld because live identity/provider/
LLM/cloud validation, manual multi-browser/assistive-technology review, load/resilience, managed
restore and external security review have not occurred. Marketing execution is disabled by default
and no spend was performed.

## Readiness matrix

| Area | Local evidence | Status / remaining gate |
|---|---|---|
| Architecture | Six accepted ADRs; modular monolith and bounded domains | Ready for audit |
| Tenancy/auth/RBAC | Application guards, tenant keys, PostgreSQL RLS, restricted runtime role, isolation tests | Local pass; live OIDC tenant mapping required |
| CRM/commerce/catalog | APIs, constraints, migrations and integration tests | Local pass |
| Imports/jobs | Content validation, staging, idempotency, outbox, durable status and worker rechecks | Local pass; load/malware service validation required |
| Analytics | Canonical KPI and RFM/value definitions, explicit null states | Local pass; production data reconciliation required |
| ML | Versioned data/features/splits, baselines, calibration, frozen test, SHAP and registry | Reproducible historical evidence; tenant drift/fitness required |
| Training-serving parity | Shared feature transformer and named model inputs | Blocked: training used country variation while operational inference sets every country to `__missing__` |
| Web | Required B2B areas, real API states, server-only credentials | Build/unit tests and 26 desktop/mobile Chromium route+Axe checks pass; manual browser/assistive-tech matrix external |
| Integrations | Meta/Google fixed-origin adapters, normalization, mocks/contract tests | No credentialed live validation |
| Attribution | Deterministic HMAC-protected last-touch, method/version/evidence | Local pass; noncausal by design |
| Audiences/campaigns | Immutable snapshots, current consent, approvals, spend/kill-switch blocks | Local pass; execution intentionally disabled |
| Generative AI | Provider abstraction, verified fact context, unsupported-claim rejection | Disabled; no live provider adapter validated |
| Security/observability | Secure headers, CORS policy, HMAC webhooks, privacy-safe rate keys, audit, health, metrics, OTel span | Local pass; external monitoring/pentest/WAF policy required |
| Recovery | Backup/restore runbook and RPO/RTO targets | Not achieved until managed restore drill |
| Deployment | Non-root containers; build-time model checksum contract; corrected worker entrypoint; encrypted private AWS reference; Terraform validates | Static/local contract pass; no Docker engine build and no cloud apply |
| Academic | Six source/DOCX/PDF reports, figures and eight-slide PPTX/PDF | Complete for reviewer/submission-channel check; report 07 validated against its instructor template |

## Executed quality evidence

The backend and Terraform local quality gates were re-executed on 2026-09-22; the
frontend, dependency, migration and document results below are from the earlier full
publication audit unless separately dated. The combined local evidence is:

- Ruff lint passed and all 127 checked Python files were already formatted.
- Strict mypy passed for 75 backend application source files.
- Pytest passed 86/86 tests, including PostgreSQL RLS/tenant, Redis delivery and the new
  deployment artifact/entrypoint contract tests; two
  upstream deprecation warnings remain.
- Frontend TypeScript and ESLint passed, Vitest passed 2/2 tests, and the Next.js Webpack
  production build completed for all application routes. Playwright passed 26/26 checks across
  13 primary routes in desktop and mobile Chromium viewports, with no Axe WCAG 2.0/2.1 A/AA
  violation, page exception or horizontal overflow.
- Alembic `current` and `heads` both reported migration `0011 (head)`.
- `pip-audit` found no known vulnerability in auditable Python packages. `pnpm audit` initially
  identified three development-tool findings; Vitest/OpenAPI tooling and the transitive
  `js-yaml` resolution were patched, after which no known vulnerability remained.
- `terraform fmt -check -recursive` passed and `terraform validate` reported a valid
  configuration.
- The eight-slide canvas overflow test passed. All six DOCX accessibility audits reported zero
  high/medium/low findings; LibreOffice/Poppler rendering and ZIP/PDF container checks passed.
  The 13-page deployment DOCX/PDF was separately regenerated and visually inspected on
  2026-09-22, with zero accessibility findings.
- Secret-pattern scanning found no credential token/private key. The three generic assignment
  candidates were reviewed and contain runtime secret generation or secret references, not values.
  All seven instructor originals remain byte-unchanged and present.

CI configuration mirrors the backend and frontend gates, including Vitest. A passing
GitHub-hosted run for this local revision cannot be claimed before publication and
verification.

## Frozen ML evidence

- Target: `future-inactivity-v1`, no eligible purchase in the next 90 days.
- Final cutoff/rows/prevalence: 2011-09-01 / 2,772 / 0.392857.
- PR-AUC 0.647525 (95% bootstrap interval 0.618131–0.678937).
- ROC-AUC 0.765878 (0.748534–0.782761).
- Brier 0.199854 (0.192598–0.207125); log loss 0.582761; ECE 0.095054.
- Top-10% precision 0.748201, recall 0.191001, lift 1.904513.
- Frozen threshold 0.812509305136 selected 302 rows: precision 0.735099, recall 0.203857,
  F1 0.319195; TN 1,603, FP 80, FN 867, TP 222.
- Model SHA-256: `942d705d66a9469d57494626a99da83c91a9a895a3a2b2d7e977ff3ba56952ad`.

These are project-executed results on one historical retailer, not production, causal or revenue
claims. No post-test tuning is permitted.

## External validation required before production

1. Select and configure production OIDC, domains, residency/region and legal/retention policy.
2. Build/scan/sign immutable images; run migrations as a separately authorized one-shot task.
3. Run credentialed Meta and Google sandbox sync tests against current permissions, quotas and schemas.
4. Select/approve an LLM provider and validate privacy, logging, retention and output controls.
5. Perform manual multi-browser and assistive-technology review plus production-like
   performance/load, queue retry and failure-injection tests.
6. Apply infrastructure only after budget/WAF/alert/runbook review; conduct database/object restore drill.
7. Validate model drift, calibration, subgroup risks and lawful use on current tenant data;
   resolve the country mismatch through reliable input data, a country-free candidate or an
   all-missing sensitivity/holdout test without tuning on the frozen final test.
8. Design an approved randomized holdout before claiming incremental campaign effect.
9. Obtain an external security review and resolve any high/critical finding.

## Release blockers and non-blockers

Missing live credentials are not local-development blockers but are production blockers for those
capabilities. The elapsed instructor deadlines are submission-process blockers, not evidence-quality
blockers. There is no known critical local defect. The previously audited baseline exists on
`origin/main`. Later local commits and working-tree documentation changes are not a claim
that GitHub already displays this revision; publication must be verified separately. Paid
deployment, production infrastructure mutation and live advertising spend remain separately
unauthorized.
