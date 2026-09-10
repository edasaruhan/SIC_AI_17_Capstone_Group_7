# GrowthPilot AI

GrowthPilot AI is a production-oriented SaaS and Samsung Innovation Campus AI in Marketing capstone project for data-driven customer operations and marketing decisions.

Local development follows the approved [architecture](docs/03_ARCHITECTURE_DECISIONS.md)
and the [24-phase delivery records](docs/tasks/README.md). No push, squash or paid
deployment is authorized at this stage.

The local build includes a tenant-isolated FastAPI/PostgreSQL backend, production
Next.js workspace, CRM/commerce/inventory operations, staged CSV/XLSX imports,
durable Redis/Dramatiq workflows, versioned analytics, calibrated inactivity-risk
scoring, MLflow provenance, provider-neutral ad integrations, deterministic
attribution, consent-aware audiences, campaign approvals and grounded generation.
External provider/cloud validation and real campaign execution remain disabled.

See [local setup](docs/LOCAL_DEVELOPMENT.md), [demo guide](docs/DEMO_GUIDE.md),
[readiness report](docs/PRODUCTION_READINESS_REPORT.md), [academic source package](academic/README.md),
[organized assignment package](ödevler/README.md), and the [project charter](docs/00_PROJECT_CHARTER.md).
Original instructor files remain unchanged under `references/instructor/`.
