# Capstone Requirements

Status: Source files inventoried on 2026-09-08 and deployment template added/audited on 2026-09-21; known deliverables are complete and synchronized. Instructor submission-channel/date confirmation remains external.

## Source inventory and precedence

All seven known reference files are present under `references/instructor/`. Originals are read-only project evidence and must not be edited. Exact wording in those files outranks this summary.

| Source file | Confirmed contents | Important timing/status |
|---|---|---|
| `AI_in_Marketing_Literature_Data_Technology_Submission.docx` | Literature Review, Data Research, and Technology Review guidelines | Deadline stated as 2026-08-16 23:59 Istanbul; elapsed as of initialization |
| `AI_in_Marketing_Concept_Note_and_Implementation_Plan.docx` | Concept Note and Implementation Plan guidelines | Deadline stated as 2026-08-30 23:59 Istanbul; elapsed as of initialization |
| `Data preparationFeature Engineering and Model exploration.docx` | Data Preparation/Feature Engineering and Model Exploration sections | No deadline or explicit output format found in file |
| `Model Refinement_Template.docx` | Model Refinement and Test Submission sections, conclusion, references | No deadline or explicit output format found in file |
| `GrowthPilot_AI_Sunum_8slayt.pdf` | Eight-slide original GrowthPilot concept presentation | Project reference; not evidence that implementation or models exist |
| `Samsung Innovation Campus_Capstone Projesi  Kısa İlerleme Raporu Şablonu.docx (2).pdf` | Weekly short-report instructions plus a completed Group 10 example | Says every Tuesday and maximum one page, but supplied PDF is a two-page, pre-filled report for another team |
| `Deployment Submission.docx` | Deployment overview, model serialization, model serving, API integration, security, monitoring and logging | One-page A4/Times New Roman guidance template; no deadline or output-length limit stated |

## Requirement matrix

| Requirement | Source file | Deliverable | Project evidence needed | Status |
|---|---|---|---|---|
| Frame the marketing problem, target audience/context, research questions, and value | Literature/Data/Technology guidelines | Literature Review | Cited sources, synthesis, gap linked to GrowthPilot | Complete — report 01 |
| Summarize and compare literature rather than listing it | Literature/Data/Technology guidelines | Literature Review | Objective/data/method/findings/strengths/limitations comparison | Complete — report 01 |
| Document dataset source, access, format, size, period, granularity, variables, and classification | Literature/Data/Technology guidelines | Data Research | Verified provenance/licence/access and reproducible profiling | Complete — report 01 + profile artifacts |
| Assess data quality, bias, representativeness, privacy, and limitations | Literature/Data/Technology guidelines | Data Research | Real validation outputs and documented limitations | Complete — report 01 |
| Provide descriptive statistics, visuals, and marketing insights where possible | Literature/Data/Technology guidelines | Data Research | Reproducible code, inputs, figures, and raw outputs | Complete — report 01 + EDA artifacts |
| Compare technologies using task-relevant quality, data, interpretability, latency, cost, integration, scalability, privacy, maintenance, and deployment criteria | Literature/Data/Technology guidelines | Technology Review | Current primary documentation, research evidence, decision matrix | Complete — report 01; live cost/latency unmeasured |
| Define overview, objectives, KPIs, background, methodology, evaluation, data, and literature context | Concept Note/Implementation Plan guidelines | Concept Note | Approved product/ML methodology and cited evidence | Complete — report 02 |
| Supply a realistic input-to-marketing-action architecture/workflow diagram | Concept Note/Implementation Plan guidelines | Concept Note | Approved architecture at appropriate abstraction; human review/KPI loop | Complete — report 02 + source figure |
| List a relevant technology stack only after selection | Concept Note/Implementation Plan guidelines | Implementation Plan | Approved decisions/ADRs | Complete — report 02 |
| Provide timeline, task ownership, milestones, evidence, risks, mitigations, and fallbacks | Concept Note/Implementation Plan guidelines | Implementation Plan | Approved delivery plan and owners | Complete — report 02; future dates require review |
| Cover privacy, consent, bias/fairness, transparency, explainability, manipulation, brand safety, and human oversight | Concept Note/Implementation Plan guidelines | Implementation Plan | Controls, risk analysis, and traceable design evidence | Complete — report 02 |
| Highlight direct AI authorship | Concept Note/Implementation Plan guidelines | Implementation Plan | Visible disclosure in submitted artifact | Complete — visible disclosure in every output |
| Document collection, cleaning, missingness/outliers, EDA, features, transformations, and code | Data Preparation/Feature Engineering template | Data Preparation / Feature Engineering | Reproducible pipeline, validations, figures, rationale | Complete — report 03 |
| Justify model selection; report training, hyperparameters, cross-validation, metrics, confusion matrix/ROC or relevant visuals, and code | Data Preparation/Feature Engineering template | Model Exploration | Baselines, experiment records, preserved validation artifacts | Complete — report 03; temporal design replaces random CV |
| Explain evaluation weaknesses, refinement methods, additional tuning, cross-validation changes, and feature selection if used | Model Refinement template | Model Refinement | Pre/post results from validation only and documented experiment lineage | Complete — report 04 |
| Prepare untouched test data, apply the selected model, compare train/validation/test metrics, discuss deployment if applicable, and provide code | Model Refinement template | Test Submission | Frozen split, final evaluation outputs, deployment evidence only if real | Complete — report 04 |
| Report weekly, concisely, with concrete progress, current focus/status, blockers/support, and next work | Weekly report PDF | Weekly Progress Report | Current repository evidence; maximum one page | Complete — Group 7 report 05, one page |
| Provide final presentation/deliverable | Original concept deck; no separate final instructions present | Final deliverable | Reproducible product/demo and ML evidence | Complete to known scope — eight-slide PPTX/PDF; final channel requirements unknown |
| Document model deployment, serialization, serving platform, API inputs/outputs, security and monitoring/logging | Deployment Submission template | Model Deployment | Repository-backed local implementation, reference architecture and explicit unvalidated production gates | Complete — report 07, template-derived DOCX/PDF |

## Confirmed special instructions

- GitHub is the instructed submission location for the first two assignment families.
- AI in Marketing is the required focus; SDG alignment is optional unless genuinely relevant.
- A new ML model is not mandatory for every possible capstone, but GrowthPilot's approved initial ML focus is churn classification.
- Academic figures and quantitative claims must be traceable and must never be synthetic fixtures presented as real evidence.

## Conflicts and ambiguities requiring review

- Both dated assignment deadlines had passed by repository initialization on 2026-09-08; submission status and any revised deadline are unknown.
- The weekly-report reference is a completed Group 10 example, not a blank Group 7 template, and renders as two pages despite its stated one-page maximum.
- The original presentation says LightGBM “will be preferred.” Current governance treats LightGBM as a candidate that must earn selection through comparison; this interpretation should be retained unless Project Lead directs otherwise.
- Output formats and deadlines for the data-preparation/model-exploration and refinement/test assignments are not stated in their source files.
- Final presentation/submission requirements beyond the original idea deck are not available.
