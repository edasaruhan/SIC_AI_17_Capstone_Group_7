# GrowthPilot Türkçe akademik teslim paketi

This directory contains new project deliverables created from the untouched instructor
references in `references/instructor/`. The originals are never modified.

## Deliverables

- `submissions/01_Literature_Data_Technology_Submission.docx` and `.pdf`
- `submissions/02_Concept_Note_and_Implementation_Plan.docx` and `.pdf`
- `submissions/03_Data_Preparation_Feature_Engineering_Model_Exploration.docx` and `.pdf`
- `submissions/04_Model_Refinement_and_Test_Submission.docx` and `.pdf`
- `submissions/05_Weekly_Progress_Report_2026-09-09.docx` and `.pdf`
- `presentation/GrowthPilot_AI_Final_Presentation.pptx` and `.pdf`
- `submissions/07_Deployment_Submission.md`, `.docx` and `.pdf`

Raporların yanındaki Markdown dosyaları Türkçe, okunabilir ve yeniden üretimde kullanılan
asıl metinlerdir. Raporlanan her ölçüt commit edilmiş proje eserlerinden yeniden
üretilmiştir. Dış kaynak iddiaları kaynaklandırılmış, yapay zekâ desteği her teslimde
açıklanmıştır. Sunum, önceki yalnız kavram odaklı eğitmen referansının kanıta dayalı nihai
karşılığıdır.

Regenerate the written package and synchronized `ödevler/` DOCX/PDF copies with:

```bash
uv run python scripts/generate_academic_deliverables.py
```

LibreOffice (`soffice`) must be available on `PATH` for deterministic PDF export. The
generator fails visibly if a PDF cannot be produced; it never leaves a silent stale copy.

Deployment submission 07 has a separate deterministic generator because it is derived from
the retained instructor template `references/instructor/Deployment Submission.docx`:

```bash
uv run python scripts/generate_deployment_submission.py
```

The script starts from the retained template, preserves its A4/Times New Roman visual system,
generates the Markdown-aligned figures and DOCX, and synchronizes the organized DOCX copy.
PDF export is performed with LibreOffice and retained only after render/visual QA.

PPTX düzenlenebilir sunum kaynağıdır. İlk tasarım gerekli `@oai/artifact-tool` sunum
iş akışıyla üretilmiş, Türkçe metin düzeltmesi tasarımı koruyan OOXML dönüşümüyle
uygulanmış ve sistemde önceden kurulu LibreOffice ile bağımsız PDF olarak işlenmiştir.
Sunum üretim çalışma alanı kalite kontrolü amacıyla depo dışında tutulur ve proje çalışma
zamanı bağımlılığı değildir.
