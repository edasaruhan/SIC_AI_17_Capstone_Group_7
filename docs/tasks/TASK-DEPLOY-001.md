# TASK-DEPLOY-001 — Model deployment submission and contract audit

**Status:** COMPLETE WITH EXTERNAL PRODUCTION GATES

**Started:** 2026-09-20

**Completed:** 2026-09-21

**Readability revision:** 2026-09-22

**Owner:** Codex

## Goal

Produce the Turkish Samsung Innovation Campus model-deployment submission from verified
GrowthPilot repository evidence, repair bounded defects found in the deployment path, and
deliver visually audited Markdown, DOCX and PDF outputs without claiming a live deployment.

## Context

The local 24-phase roadmap was complete, but the newly requested deployment assignment
required a repository-wide evidence review. The named `Deployment Submission.docx` was
absent during the first pass and was supplied on 2026-09-21. The final pass distilled the
template, rechecked every prompt and rebuilt the output from the retained source.

## In scope

- Verify the frozen model, manifest, inference API, batch worker, security, observability,
  container definitions and AWS Terraform reference.
- Fix deployment-contract defects that stay within accepted architecture.
- Add proportionate automated tests.
- Create a Turkish report with the six required sections, code/JSON examples, diagrams,
  conclusion, references and AI-use disclosure.
- Render and inspect the final DOCX/PDF, synchronize organized delivery copies and update
  affected repository control documents.

## Out of scope

Cloud apply, image publication, Docker build/scan/sign, production OIDC configuration,
managed monitoring, external pentest, live advertising, paid infrastructure, history
rewrite and any claim of production model performance.

## Dependencies

- Accepted architecture and completed PHASE-01 through PHASE-24 records.
- Frozen `future-inactivity-v1` evidence and checksum-bearing manifest.
- Existing FastAPI, PostgreSQL RLS, Redis/Dramatiq and Terraform implementation.
- Local LibreOffice/Poppler toolchain for document rendering.

## Acceptance criteria

- The report distinguishes implemented/tested, infrastructure reference, planned and
  unvalidated production behavior.
- All six required sections are present and repository metrics/checksums match artifacts.
- Model binary provisioning fails before deserialization when the checksum is wrong.
- ECS worker starts the module that defines the broker and actor.
- The operational `country="__missing__"` value is recorded as a training-serving skew
  risk and an explicit production-readiness gate without post-test tuning.
- New and existing backend tests, lint, formatting, mypy and Terraform validation pass.
- Final DOCX/PDF have no clipping, overlap, missing image, unintended blank page,
  accessibility finding, tracked change, comment, macro or package-integrity error.
- No live infrastructure, external message, campaign spend or history rewrite occurs.

## Validation plan

- Recompute and compare model checksums; inspect manifests, routes, schemas, migrations,
  middleware, runtime configuration, Dockerfile and Terraform resources.
- Add focused correct-hash, mismatch and static deployment-contract tests.
- Run `sh scripts/quality.sh` against the isolated local PostgreSQL/Redis services.
- Run `terraform fmt -check -recursive` and `terraform -chdir=infra/terraform/aws validate`.
- Render DOCX to PDF/PNG, inspect all pages, run DOCX accessibility/section/style/image
  audits, check Office ZIP integrity and compare source/organized hashes.

## Risks

- Pickle/joblib deserialization remains unsafe for untrusted inputs; checksum verification
  must be combined with private artifact provenance and a controlled promotion process.
- Template fidelity can regress when a one-page guidance file is expanded into a detailed
  report; preserve its page system, typography and section order, then render every page.
- Static Terraform validation does not prove cloud behavior, budget, region, IAM or TLS.
- Docker engine absence prevents a real image build/scan/sign result.

## Completion record

### Files changed

- Deployment runtime contract: `backend/app/platform/model_artifact.py`,
  `infra/containers/backend.Dockerfile`, `infra/terraform/aws/main.tf`, `infra/README.md`.
- Tests: `backend/tests/test_deployment_contract.py`.
- Submission sources/outputs: `academic/submissions/07_Deployment_Submission.*`, two
  deployment figures, `scripts/generate_deployment_submission.py`, and
  `ödevler/07_Deployment/`.
- Control documentation: root/academic/scripts/submission README files, academic map,
  final audit, production readiness, model registry/inference guide and task records.

### Implementation summary

The audit found that the backend image copied the manifest but could not receive the ignored
model binary, and that the Terraform worker command targeted `app.platform.jobs` rather
than the module containing the Dramatiq broker/actor. The image now requires a BuildKit
secret, streams and verifies the model against the manifest without deserializing it,
installs it read-only at a fixed runtime path, and retains the existing runtime checksum
check. The worker command now targets `app.platform.worker`. The report records these
repairs and every remaining production gate. It also elevates the operational
`country="__missing__"` behavior from a minor limitation to a training-serving skew gate:
reliable country data, a country-free candidate, or an all-missing sensitivity/holdout
test is required before production use.

### Tests and commands run

- `sh scripts/quality.sh`
- `terraform fmt -check -recursive`
- `terraform -chdir=infra/terraform/aws validate`
- Document generation and LibreOffice DOCX render/export
- `pdfinfo`, `pdftotext`, `unzip -t`, checksum comparison
- DOCX accessibility, section, style and image audits
- Template distillation and source/final package comparison
- Manual visual inspection of all 13 rendered report pages

### Results

- Ruff and format checks: pass, 127 Python files.
- Strict mypy: pass, 75 source files.
- Pytest: 86/86 pass; two upstream deprecation warnings.
- Terraform format/validate: pass.
- Deployment report: 13 A4, tagged, unencrypted PDF pages; 0 accessibility findings; two
  inline diagrams; source and organized DOCX/PDF pairs byte-identical. The instructor
  template retained its original SHA-256, while its A4 geometry, Times New Roman hierarchy
  and six-section order were carried into the final report.
- Model SHA-256 independently confirmed as
  `942d705d66a9469d57494626a99da83c91a9a895a3a2b2d7e977ff3ba56952ad`.
- The 2026-09-22 readability pass shortened dense prose, removed mixed-language labels,
  enlarged code examples and diagram text, fixed a diagram-label overlap, and kept the
  second figure with its caption. The 13-page report was regenerated and each page
  visually inspected; DOCX accessibility remained at zero findings. Ruff/format, mypy
  and all 86 backend tests passed again.

### Known limitations

- No real Docker image was built, scanned, signed or started in this environment.
- No AWS resource was planned against an account or applied.
- Production OIDC, credentials, trace/metric backends, alerting, RDS TLS enforcement,
  restore drill, load/failure tests and external security review remain unvalidated.
- Current model use remains demo-only pending representative business-domain validation.
- The training data contains country variation while operational inference supplies
  `country="__missing__"` for every row; no post-test tuning was performed.

### Residual risks

Artifact provenance, dependency provenance, operational alert ownership, model drift,
delayed-label performance and tenant-specific fitness require production governance. Static
hash equality alone does not establish artifact authenticity.

### Open questions

- Which production identity provider, AWS region/residency, artifact registry, monitoring
  backend and on-call owner will be approved?
- What legally approved retention, model-use and subgroup-review policy will apply?

### Decisions required

No decision is required to accept the academic package. Any cloud apply, image publication
or production validation requires its existing explicit gate.

### Recommended next task

Conduct human academic review and treat production release as a separate gated task.
