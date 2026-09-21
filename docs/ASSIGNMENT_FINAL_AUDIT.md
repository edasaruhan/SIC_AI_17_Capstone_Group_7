# Assignment Final Audit

**Status:** COMPLETE — Turkish deliverables ready for human submission review and repository publication

**Audit date:** 2026-09-21

**Scope:** Six written assignments, the final presentation, their organized delivery copies,
the seven preserved instructor references, and the repository evidence cited by the submissions.

This audit checks the deliverables against the exact instructor files under
`references/instructor/`. It does not claim an instructor grade, a submission receipt, or
acceptance of an elapsed deadline.

## Requirement coverage

| Deliverable | Instructor requirement coverage | Final format | Audit verdict |
|---|---|---|---|
| 01 — Literature, data and technology | Thematic literature synthesis; comparison and gap; dataset selection, provenance, licence, profile, quality/privacy, EDA; technology comparison, real-world marketing products/use cases and reported outcomes, limitations and project application | DOCX + PDF; Markdown source | PASS. Salesforce/Grammarly and Google/Aritaum outcomes are attributed to official vendor case studies and explicitly labelled external-source, vendor-reported evidence rather than independent or GrowthPilot results. |
| 02 — Concept note and implementation plan | Problem, users, objectives/KPIs, method, data, literature, workflow diagram, stack, actual timeline/ownership, milestones, risks/fallbacks, ethics/responsible AI, references and AI disclosure | DOCX + PDF; Markdown source | PASS. Planned outcomes remain explicitly separate from measured project evidence. |
| 03 — Data preparation, feature engineering and model exploration | Collection/provenance, cleaning, missingness/outliers, temporal leakage controls, EDA, feature rationale, transforms/encoding, code excerpt, model candidates and validation metrics | DOCX + PDF; Markdown source | PASS. Values and model-selection claims match versioned repository artifacts. |
| 04 — Model refinement and test | Initial weaknesses, tuning, calibration, chronological validation, feature decision, explainability, frozen-test integrity, application code excerpt, metrics/intervals, confusion matrix, curves, deployment truth, conclusion and references | DOCX + PDF; Markdown source | PASS. Frozen-threshold and top-10% metrics are correctly distinguished. |
| 05 — Weekly progress report | All six template questions in no more than one page | DOCX + one-page PDF; Markdown source | PASS for content and format. The report is truthfully dated 9 September 2026; the instructor template requests Tuesday reporting, so acceptance of this historical Wednesday report and the submission channel remains an external process check. |
| 06 — Final presentation | Eight-slide editable presentation and matching PDF summarizing the problem, product, data/target, model selection, frozen evaluation, explainability/governance and remaining external validation | PPTX + eight-slide PDF | PASS against the known eight-slide reference and repository evidence. No separate final-presentation rubric was supplied. |
| 07 — Model deployment | Overview, model serialization/storage, model serving/platform choice, API inputs/outputs, security, monitoring/logging, code and synthetic response examples, diagrams, conclusion, references and AI disclosure | Template-derived DOCX + 13-page A4 PDF; Markdown source | PASS against `Deployment Submission.docx` and repository evidence. The A4 page system, Times New Roman hierarchy and six-section order are preserved; two real deployment-contract defects were fixed and tested. |

## File and render validation

| Check | Result |
|---|---:|
| Academic-source files matched to organized `ödevler/` copies | 14 / 14 byte-identical |
| Written DOCX files rendered and visually inspected | 6 files / 36 pages |
| Final presentation PDF visually inspected | 8 / 8 slides |
| Written PDF pages matched to fresh DOCX renders | 36 / 36 pixel-identical |
| DOCX accessibility findings | 0 high / 0 medium / 0 low across all six files |
| Office ZIP-package integrity | 7 / 7 passed |
| Tracked insertions/deletions in DOCX | 0 / 0 |
| Comments and macros in Office files | 0 / 0 |
| PDF encryption | None in all seven PDFs |

Page counts are 7, 5, 5, 5, 1 and 13 for written reports 01–05 and 07; the presentation
is eight 16:9 pages. Visual inspection found no clipped text, overlap, broken table,
missing image, unreadable chart or unintended blank page.

## Turkish-language correction

- The six written assignments and all eight presentation slides use Turkish narrative,
  headings, labels and AI-assistance disclosures.
- Bibliographic work titles, code, product/library names, standard metric abbreviations
  and evidence-figure technical labels remain in their original form to preserve
  citation, execution and artifact traceability.
- Turkish Markdown is now the source of truth for written regeneration. The presentation
  translation is a deterministic, repeatable OOXML transformation that preserves the
  editable deck design.

## Evidence integrity

- Instructor originals remain unchanged under `references/instructor/`.
- Reported dataset and final-model metrics were cross-checked against the committed JSON
  artifacts, including 2,772 final-test rows, PR-AUC 0.647525, ROC-AUC 0.765878, Brier
  0.199854 and top-10% lift 1.904513.
- The frozen-threshold result remains separate from the exact top-10% ranking result:
  302 selected customers, precision 0.735099, recall 0.203857 and F1 0.319195.
- The final model SHA-256 is
  `942d705d66a9469d57494626a99da83c91a9a895a3a2b2d7e977ff3ba56952ad`.
- AI drafting is disclosed in every deliverable. Project-generated, external-source and
  planned/forecast evidence boundaries are explicit; no revenue, campaign, user or
  production outcome is fabricated.

## Remaining human/external checks

The deliverables are locally complete and correctly formatted. Before an LMS/email
submission, the Project Lead should still confirm the destination, filename convention,
elapsed-deadline handling and whether the Wednesday weekly report is accepted for the
required reporting cycle. Human academic review remains required by the disclosures.
Live provider/cloud validation, deployment and campaign outcomes are outside assignment
format completion and remain explicitly unclaimed.

## Repository publication gate

- Ruff and formatting passed for 127 Python files; strict mypy passed for 75 source files.
- Backend tests: 86 / 86 passed.
- Frontend: TypeScript, ESLint, 2 / 2 Vitest tests and the Next.js production build passed.
- Browser/accessibility: 26 / 26 desktop/mobile Chromium-Axe route checks passed.
- Python and Node third-party dependency audits reported no known vulnerabilities. The local
  editable `growthpilot` package is correctly excluded from the PyPI vulnerability lookup.
- Strong secret-pattern, tracked-junk and sensitive-filename scans returned zero findings;
  all 82 project-internal Markdown links resolve.
