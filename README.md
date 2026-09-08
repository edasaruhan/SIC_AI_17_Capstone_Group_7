# GrowthPilot AI

GrowthPilot AI is a production-oriented SaaS and Samsung Innovation Campus AI in Marketing capstone project for data-driven customer operations and marketing decisions.

Local development follows the approved [architecture](docs/03_ARCHITECTURE_DECISIONS.md)
and the [24-phase delivery records](docs/tasks/README.md). No push, squash or paid
deployment is authorized at this stage.

The current foundation includes a tenant-isolated FastAPI/PostgreSQL backend,
CRM/commerce and inventory operations, staged CSV/XLSX imports, durable Redis/Dramatiq
delivery, and versioned operational analytics. Next.js tooling is executable; full
product UI and later ML/marketing phases are tracked separately, not claimed complete.

See [local setup](docs/LOCAL_DEVELOPMENT.md), [import workflow](docs/IMPORTS_AND_JOBS.md),
[KPI definitions](docs/ANALYTICS_CONTRACT.md), and the [project charter](docs/00_PROJECT_CHARTER.md).
Original instructor files remain unchanged under `references/instructor/`.
