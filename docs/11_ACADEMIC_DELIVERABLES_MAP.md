# Academic Deliverables Map

Status: Synchronized completion map, 2026-09-09. All known deliverables are complete for Project Lead review; no submission/upload is claimed.

| Assignment | Source template/guideline | Expected output format | Required evidence | Dependencies | Current status | Next action |
|---|---|---|---|---|---|---|
| Literature Review | Instructor literature/data/technology DOCX | Markdown + DOCX + PDF in report 01 | Thematic synthesis, comparison, gap, citations | Research/target evidence | Complete; deadline in source elapsed | Project Lead content review; confirm submission channel/date |
| Data Research | Instructor literature/data/technology DOCX | Included in report 01 | DOI/licence/profile, quality/privacy/limitations, EDA | Selected UCI source and reproducible profiler | Complete | Review source attribution |
| Technology Review | Instructor literature/data/technology DOCX | Included in report 01 | Architecture comparison, marketing fit, limitations | Accepted ADRs and official docs | Complete; live cost/latency not measured | Review wording |
| Concept Note | Instructor concept/plan DOCX | Markdown + DOCX + PDF in report 02 | Scope, KPIs, method, data, workflow diagram | Implemented architecture/evidence | Complete | Project Lead narrative review |
| Implementation Plan | Instructor concept/plan DOCX | Included in report 02 | Stack, actual timeline, ownership, risks, responsible AI, disclosure | Delivery records and ADRs | Complete; future schedule not invented | Confirm external owners/dates |
| Data Preparation / Feature Engineering | Instructor data/model DOCX | Markdown + DOCX + PDF in report 03 | Cleaning, missingness/outliers, EDA, features, transforms, code | Versioned data pipeline | Complete | Review figures/code excerpt |
| Model Exploration | Instructor data/model DOCX | Included in report 03 | Rationale, candidates, temporal validation, metrics, code | Preserved MLflow/artifacts | Complete | Review model comparison |
| Model Refinement | Instructor refinement DOCX | Markdown + DOCX + PDF in report 04 | Weaknesses, tuning, calibration, temporal design, SHAP | Frozen candidate evidence | Complete | Review noncausal language |
| Test Submission | Instructor refinement DOCX | Included in report 04 | Test integrity, metrics, confusion matrix/curves, deployment truth | Untouched holdout | Complete | Review final numbers/checksums |
| Weekly Progress Report | Instructor weekly-report PDF | Markdown + DOCX + one-page PDF report 05 | Six required questions and current evidence | Current readiness audit | Complete for current cycle | Confirm Tuesday/submission process |
| Final presentation | Original eight-slide concept PDF | Editable eight-slide PPTX + PDF | Actual product/ML evidence, sources, limitations, AI disclosure | All completed phases | Complete to known requirements | Confirm any additional instructor rubric |

## Evidence package convention used

Each report has Markdown source plus DOCX/PDF; shared figures and presentation outputs are
under `academic/`. Reproducible metric inputs remain under `artifacts/` and generation code
under `scripts/`. Submission naming/channel may be adjusted only after reviewer confirmation.

## Provenance classes

Every figure or quantitative statement must be labeled or traceable as:

- PROJECT-GENERATED / REPRODUCED;
- EXTERNAL-SOURCE; or
- PLANNED / FORECAST.

Synthetic software-test fixtures are never real academic experiment evidence.
