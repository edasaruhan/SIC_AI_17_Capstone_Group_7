# GrowthPilot academic submission package

This directory contains new project deliverables created from the untouched instructor
references in `references/instructor/`. The originals are never modified.

## Deliverables

- `submissions/01_Literature_Data_Technology_Submission.docx` and `.pdf`
- `submissions/02_Concept_Note_and_Implementation_Plan.docx` and `.pdf`
- `submissions/03_Data_Preparation_Feature_Engineering_Model_Exploration.docx` and `.pdf`
- `submissions/04_Model_Refinement_and_Test_Submission.docx` and `.pdf`
- `submissions/05_Weekly_Progress_Report_2026-09-09.docx` and `.pdf`
- `presentation/GrowthPilot_AI_Final_Presentation.pptx` and `.pdf`

The Markdown files beside the reports are human-readable source copies. Every reported
metric is reproduced from committed project artifacts. External-source claims are cited.
AI-assisted drafting is disclosed in each deliverable. The presentation is a final,
evidence-based replacement for the earlier concept-only instructor reference deck.

Regenerate the written package with:

```bash
uv run python scripts/generate_academic_deliverables.py
```

The PPTX is the editable presentation source. It was generated with the required
`@oai/artifact-tool` presentation workflow and independently rendered through
LibreOffice. The generation workspace is retained outside the repository as QA scratch;
it is intentionally not a project runtime dependency.
