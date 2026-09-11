"""Generate the GrowthPilot written capstone submission package.

The instructor originals remain untouched. Reported numbers are fixed project artifacts;
external claims are explicitly cited. The selected DOCX preset is
``standard_business_brief`` with the ``memo_masthead`` first-page pattern.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "academic" / "submissions"
FIG = ROOT / "academic" / "figures"
ML = ROOT / "artifacts" / "ml"
EDA = ROOT / "artifacts" / "eda"
REPORTS = ROOT / "artifacts" / "reports"
ASSIGNMENTS = ROOT / "ödevler"

GREEN = "1E5A49"
GREEN_LIGHT = "E8F1ED"
BLUE = "2E74B5"
BLUE_DARK = "1F4D78"
INK = "173B32"
MUTED = "547068"
GRAY = "F2F4F7"
WHITE = "FFFFFF"
RED = "9B1C1C"


@dataclass(frozen=True)
class Block:
    kind: str
    value: Any
    note: str | None = None


@dataclass(frozen=True)
class Submission:
    stem: str
    title: str
    subtitle: str
    blocks: list[Block]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def set_run_font(
    run: Any,
    *,
    name: str = "Calibri",
    size: float | None = None,
    color: str | None = None,
    bold: bool | None = None,
    italic: bool | None = None,
) -> None:
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def shade(cell: Any, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(
    cell: Any, top: int = 80, start: int = 120, bottom: int = 80, end: int = 120
) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for edge, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        tag = tc_mar.find(qn(f"w:{edge}"))
        if tag is None:
            tag = OxmlElement(f"w:{edge}")
            tc_mar.append(tag)
        tag.set(qn("w:w"), str(value))
        tag.set(qn("w:type"), "dxa")


def set_table_geometry(table: Any, widths: list[int]) -> None:
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), "9360")
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), "120")
    tbl_ind.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for cell, width in zip(row.cells, widths, strict=True):
            tc_w = cell._tc.get_or_add_tcPr().find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                cell._tc.get_or_add_tcPr().append(tc_w)
            tc_w.set(qn("w:w"), str(width))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell)


def set_repeat_table_header(row: Any) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def prevent_table_row_split(row: Any) -> None:
    """Keep each logical record together when a table crosses a page boundary."""
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    cant_split.set(qn("w:val"), "true")
    tr_pr.append(cant_split)


def add_field(paragraph: Any, instruction: str) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    text = OxmlElement("w:instrText")
    text.set(qn("xml:space"), "preserve")
    text.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, text, separate, end])


def add_page_number(paragraph: Any) -> None:
    paragraph.add_run("Page ")
    add_field(paragraph, "PAGE")
    paragraph.add_run(" of ")
    add_field(paragraph, "NUMPAGES")


def paragraph_border_bottom(paragraph: Any, color: str = GREEN, size: str = "12") -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    borders = p_pr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        p_pr.append(borders)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), "6")
    bottom.set(qn("w:color"), color)
    borders.append(bottom)


def configure_numbering(doc: Document) -> None:
    numbering = doc.part.numbering_part.element
    for style_name, num_fmt, marker in (
        ("Academic Bullet", "bullet", "•"),
        ("Academic Number", "decimal", "%1."),
    ):
        abstract_ids = [
            int(x.get(qn("w:abstractNumId"))) for x in numbering.findall(qn("w:abstractNum"))
        ]
        abstract_id = max(abstract_ids, default=0) + 1
        abstract = OxmlElement("w:abstractNum")
        abstract.set(qn("w:abstractNumId"), str(abstract_id))
        multi = OxmlElement("w:multiLevelType")
        multi.set(qn("w:val"), "singleLevel")
        abstract.append(multi)
        lvl = OxmlElement("w:lvl")
        lvl.set(qn("w:ilvl"), "0")
        start = OxmlElement("w:start")
        start.set(qn("w:val"), "1")
        fmt = OxmlElement("w:numFmt")
        fmt.set(qn("w:val"), num_fmt)
        text = OxmlElement("w:lvlText")
        text.set(qn("w:val"), marker)
        suff = OxmlElement("w:suff")
        suff.set(qn("w:val"), "tab")
        p_pr = OxmlElement("w:pPr")
        tabs = OxmlElement("w:tabs")
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), "num")
        tab.set(qn("w:pos"), "720")
        tabs.append(tab)
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), "720")
        ind.set(qn("w:hanging"), "360")
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:after"), "160")
        spacing.set(qn("w:line"), "280")
        spacing.set(qn("w:lineRule"), "auto")
        p_pr.extend([tabs, ind, spacing])
        lvl.extend([start, fmt, text, suff, p_pr])
        abstract.append(lvl)
        numbering.append(abstract)
        nums = [int(x.get(qn("w:numId"))) for x in numbering.findall(qn("w:num"))]
        num_id = max(nums, default=0) + 1
        num = OxmlElement("w:num")
        num.set(qn("w:numId"), str(num_id))
        ref = OxmlElement("w:abstractNumId")
        ref.set(qn("w:val"), str(abstract_id))
        num.append(ref)
        numbering.append(num)
        style = doc.styles.add_style(style_name, 1)
        style.base_style = doc.styles["Normal"]
        num_pr = OxmlElement("w:numPr")
        ilvl = OxmlElement("w:ilvl")
        ilvl.set(qn("w:val"), "0")
        num_id_el = OxmlElement("w:numId")
        num_id_el.set(qn("w:val"), str(num_id))
        num_pr.extend([ilvl, num_id_el])
        style.element.get_or_add_pPr().append(num_pr)


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor.from_string("000000")
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.10
    for name, size, color, before, after in (
        ("Heading 1", 16, BLUE, 16, 8),
        ("Heading 2", 13, BLUE, 12, 6),
        ("Heading 3", 12, BLUE_DARK, 8, 4),
    ):
        style = styles[name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)
        style.font.bold = True
        style._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
    code = styles.add_style("Academic Code", 1)
    code.base_style = normal
    code.font.name = "Menlo"
    code.font.size = Pt(8.5)
    code._element.rPr.rFonts.set(qn("w:ascii"), "Menlo")
    code._element.rPr.rFonts.set(qn("w:hAnsi"), "Menlo")
    code.paragraph_format.left_indent = Inches(0.2)
    code.paragraph_format.right_indent = Inches(0.2)
    code.paragraph_format.space_before = Pt(4)
    code.paragraph_format.space_after = Pt(8)
    configure_numbering(doc)


def set_header_footer(doc: Document, label: str) -> None:
    section = doc.sections[0]
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header.paragraph_format.space_after = Pt(2)
    run = header.add_run(f"GROWTHPILOT AI  |  {label.upper()}")
    set_run_font(run, size=8.5, color=MUTED, bold=True)
    paragraph_border_bottom(header, color="B8D2C8", size="6")
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer.paragraph_format.space_before = Pt(2)
    add_page_number(footer)
    for run in footer.runs:
        set_run_font(run, size=8.5, color=MUTED)


def add_masthead(
    doc: Document, title: str, subtitle: str, status: str = "Final local academic package"
) -> None:
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(12)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(title)
    set_run_font(r, size=23, color=INK, bold=True)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run(subtitle)
    set_run_font(r, size=13.5, color=MUTED)
    for label, value in (
        ("Course", "Samsung Innovation Campus — AI in Marketing Capstone"),
        ("Team", "Group 7"),
        ("Project", "GrowthPilot AI"),
        ("Prepared by", "Şahin Başcı"),
        ("Date", "9 September 2026"),
        ("Status", status),
    ):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.keep_together = True
        set_run_font(p.add_run(f"{label}: "), size=10.5, bold=True, color=INK)
        set_run_font(p.add_run(value), size=10.5, color="000000")
    rule = doc.add_paragraph()
    rule.paragraph_format.space_after = Pt(12)
    paragraph_border_bottom(rule)
    p = doc.add_paragraph()
    shade_paragraph(p, GREEN_LIGHT)
    p.paragraph_format.left_indent = Inches(0.08)
    p.paragraph_format.right_indent = Inches(0.08)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(
        "AI AUTHORSHIP DISCLOSURE — This document was drafted with OpenAI Codex/ChatGPT "
        "assistance and checked against repository evidence. Reported project metrics come "
        "from executed, versioned artifacts; external claims are cited. Human review remains required."
    )
    set_run_font(r, size=9.5, color=INK, bold=True)
    doc.add_paragraph()


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[int]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    set_table_geometry(table, widths)
    set_repeat_table_header(table.rows[0])
    prevent_table_row_split(table.rows[0])
    for cell, text in zip(table.rows[0].cells, headers, strict=True):
        shade(cell, GRAY)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        set_run_font(p.add_run(text), size=9.5, bold=True, color=INK)
    for values in rows:
        row = table.add_row()
        prevent_table_row_split(row)
        cells = row.cells
        for cell, text in zip(cells, values, strict=True):
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            set_run_font(p.add_run(str(text)), size=9.2, color="000000")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_figure(doc: Document, relative_path: str, caption: str, width: float = 6.35) -> None:
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(path)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    picture = p.add_run().add_picture(str(path), width=Inches(width))
    picture._inline.docPr.set("descr", caption)
    picture._inline.docPr.set("title", caption.split(".", maxsplit=1)[0])
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_before = Pt(4)
    c.paragraph_format.space_after = Pt(8)
    set_run_font(c.add_run(caption), size=9, color=MUTED, italic=True)


def render_blocks(doc: Document, blocks: list[Block]) -> None:
    for block in blocks:
        if block.kind == "h1":
            doc.add_heading(block.value, level=1)
        elif block.kind == "h2":
            doc.add_heading(block.value, level=2)
        elif block.kind == "h3":
            doc.add_heading(block.value, level=3)
        elif block.kind == "p":
            doc.add_paragraph(block.value)
        elif block.kind == "bullet":
            doc.add_paragraph(block.value, style="Academic Bullet")
        elif block.kind == "number":
            doc.add_paragraph(block.value, style="Academic Number")
        elif block.kind == "code":
            p = doc.add_paragraph(style="Academic Code")
            shade_paragraph(p, "F7F9F8")
            set_run_font(p.add_run(block.value), name="Menlo", size=8.5, color=INK)
        elif block.kind == "table":
            headers, rows, widths = block.value
            add_table(doc, headers, rows, widths)
            if block.note:
                p = doc.add_paragraph(block.note)
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)
                for run in p.runs:
                    set_run_font(run, size=8.5, color=MUTED, italic=True)
        elif block.kind == "figure":
            path, caption, width = block.value
            add_figure(doc, path, caption, width)
        elif block.kind == "break":
            doc.add_page_break()
        else:
            raise ValueError(f"Unknown block kind: {block.kind}")


def shade_paragraph(paragraph: Any, fill: str) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    p_pr.append(shd)


def markdown_for(submission: Submission) -> str:
    lines = [
        f"# {submission.title}",
        "",
        submission.subtitle,
        "",
        "**AI AUTHORSHIP DISCLOSURE:** This document was drafted with OpenAI Codex/ChatGPT assistance and checked against repository evidence. Human review remains required.",
        "",
    ]
    for block in submission.blocks:
        if block.kind == "h1":
            lines.extend([f"## {block.value}", ""])
        elif block.kind == "h2":
            lines.extend([f"### {block.value}", ""])
        elif block.kind == "h3":
            lines.extend([f"#### {block.value}", ""])
        elif block.kind == "p":
            lines.extend([block.value, ""])
        elif block.kind == "bullet":
            lines.extend([f"- {block.value}", ""])
        elif block.kind == "number":
            lines.extend([f"1. {block.value}", ""])
        elif block.kind == "code":
            lines.extend(["```python", block.value, "```", ""])
        elif block.kind == "table":
            headers, rows, _ = block.value
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join("---" for _ in headers) + " |")
            for row in rows:
                lines.append("| " + " | ".join(str(x).replace("\n", " ") for x in row) + " |")
            lines.extend(["", block.note or "", ""])
        elif block.kind == "figure":
            path, caption, _ = block.value
            lines.extend([f"![{caption}](../../{path})", "", f"*{caption}*", ""])
        elif block.kind == "break":
            lines.extend(["---", ""])
    return "\n".join(lines).rstrip() + "\n"


def build_submission(submission: Submission) -> None:
    doc = Document()
    configure_document(doc)
    set_header_footer(doc, submission.title)
    add_masthead(doc, submission.title, submission.subtitle)
    if submission.stem == "03_Data_Preparation_Feature_Engineering_Model_Exploration":
        # The long two-line title and dense first section need a true cover page in
        # LibreOffice; otherwise its pagination engine can visually collapse two
        # adjacent metadata paragraphs while trying to keep the first table intact.
        doc.add_page_break()
    render_blocks(doc, submission.blocks)
    doc.core_properties.title = submission.title
    doc.core_properties.subject = "Samsung Innovation Campus — AI in Marketing Capstone"
    doc.core_properties.author = "Şahin Başcı; AI-assisted drafting disclosed"
    doc.core_properties.keywords = "GrowthPilot, capstone, AI in marketing, Group 7"
    doc.save(OUT / f"{submission.stem}.docx")
    (OUT / f"{submission.stem}.md").write_text(markdown_for(submission), encoding="utf-8")


def literature_submission(profile: dict[str, Any]) -> Submission:
    raw = profile["raw"]
    return Submission(
        "01_Literature_Data_Technology_Submission",
        "Literature, Data and Technology Submission",
        "Evidence-led research foundation for a governed retail churn decision system",
        [
            Block("h1", "Executive summary"),
            Block(
                "p",
                "GrowthPilot AI addresses a practical marketing problem: small retail teams hold customer, order, product, inventory and advertising information in disconnected tools, so retention decisions are late, difficult to explain and hard to audit. The capstone narrows the first supervised-learning problem to future-purchase inactivity in a non-contractual retail setting. This is a prediction problem, not proof that a customer has permanently churned and not evidence that an intervention causes retention.",
            ),
            Block(
                "p",
                "The research synthesis supports four methodological choices: define the outcome operationally; use chronological observation and outcome windows; compare a transparent baseline and logistic model before complex learners; and evaluate probability quality plus capacity-constrained ranking rather than accuracy alone. UCI Online Retail II was selected because its two-year transaction history supports temporal snapshots. The implemented technology stack keeps data provenance, tenant isolation, model versioning, consent and human approval inside one auditable workflow.",
            ),
            Block("h1", "Part I — Literature review"),
            Block("h2", "1. Problem statement and research question"),
            Block(
                "p",
                "In a contractual service, a cancellation can identify churn directly. In non-contractual retail, silence is ambiguous: a customer may be between purchases, seasonally inactive or permanently lost. GrowthPilot therefore asks: How accurately and usefully can pre-cutoff transaction behavior identify customers who will make no eligible purchase during a fixed 90-day future window, while preserving calibration, explanation and governed marketing use?",
            ),
            Block("h2", "2. Theme one: customer status is latent"),
            Block(
                "p",
                "Jerath, Fader and Hardie (2011) show that models of customer “death” can encode materially different assumptions about when dropout occurs. Pareto/NBD treats dropout as a calendar-time process; BG/NBD attaches the opportunity to transaction time. Their comparison matters operationally because customer-status estimates depend on model assumptions, not an observable fact. Batislam, Denizel and Filiztekin (2007) likewise compare Pareto/NBD and BG/NBD on grocery transactions and frame active status and future purchasing as distinct predictive goals.",
            ),
            Block(
                "p",
                "Platzer and Reutterer (2016) add purchase regularity to non-contractual customer-base models. This is important for GrowthPilot: a memoryless rule may mark a naturally periodic buyer as inactive. The implementation therefore includes recency, frequency, tenure and interpurchase-gap features, while still naming the target future inactivity rather than true churn.",
            ),
            Block("h2", "3. Theme two: evaluation must match a marketing decision"),
            Block(
                "p",
                "A marketing team cannot contact every customer. Model evaluation therefore needs both statistical discrimination and an operating policy. PR-AUC is emphasized because inactivity prevalence changes across time; ROC-AUC remains a secondary ranking measure. Brier score, log loss and expected calibration error test probability quality. Precision, recall and lift in the highest-risk 5%, 10% and 20% translate scores into outreach-capacity evidence.",
            ),
            Block(
                "p",
                "The final operating threshold was chosen on a separate calibration period as the score boundary for approximately 10% capacity, then frozen. This avoids choosing a threshold on the final temporal test. Campaign outcomes would require a randomized or credible quasi-experimental design; predictive lift alone cannot establish incremental marketing impact.",
            ),
            Block("h2", "4. Theme three: explanation and governance"),
            Block(
                "p",
                "Explainability is useful only when its scope is explicit. Logistic coefficients and SHAP decompositions explain how the fitted model formed a score; they do not show that changing a feature will change behavior. GrowthPilot stores model, feature, target and split versions, artifact checksums and explanation payloads. Any recommendation is still constrained by current consent, purpose, role permissions, approval state, kill switch and budget limit.",
            ),
            Block("h2", "5. Comparative synthesis"),
            Block(
                "table",
                (
                    [
                        "Source",
                        "Objective / data / method",
                        "Findings used",
                        "Strength / limitation",
                    ],
                    [
                        [
                            "Jerath, Fader & Hardie (2011)",
                            "Non-contractual customer death; two empirical datasets; PDO vs Pareto/NBD/BG-NBD",
                            "Dropout-time assumptions change customer metrics",
                            "Strong conceptual warning; not a supervised campaign-effect study",
                        ],
                        [
                            "Batislam et al. (2007)",
                            "Grocery customer base; empirical Pareto/NBD and BG/NBD comparison",
                            "Active status and future purchasing require validation",
                            "Retail evidence; context does not guarantee transfer",
                        ],
                        [
                            "Platzer & Reutterer (2016)",
                            "Non-contractual transactions; purchase regularity extension",
                            "Periodic behavior can improve customer-base modeling",
                            "Addresses cadence; still model-dependent latent status",
                        ],
                        [
                            "Saito & Rehmsmeier (2015)",
                            "Imbalanced classification; ROC vs PR visualization",
                            "PR analysis is informative when positives are uneven",
                            "Metric guidance; not retail-specific",
                        ],
                        [
                            "Lundberg & Lee (2017)",
                            "Unified additive feature-attribution framework",
                            "Local/global fitted-model explanations can be validated additively",
                            "Explanation is not causal attribution",
                        ],
                    ],
                    [1450, 2850, 2700, 2360],
                ),
                note="Evidence class: external-source synthesis. No GrowthPilot performance result is claimed in this table.",
            ),
            Block("h2", "6. Marketing gap and contribution"),
            Block(
                "p",
                "The gap is not another isolated churn notebook. Small teams need a traceable path from raw records to a human decision: canonical data, versioned features, honest probability estimates, consent-aware prioritization and an approval gate. GrowthPilot contributes an integrated implementation and a reproducible capstone evaluation. It does not claim that one historical UK retailer represents every market, that future inactivity equals permanent churn, or that targeted outreach produces incremental revenue.",
            ),
            Block("h2", "7. Literature conclusion"),
            Block(
                "p",
                "The literature justifies a conservative label and evaluation design. It also motivates explicit cadence features and the separation of prediction, explanation and causal effectiveness. These principles are encoded in the target memo, temporal split, model card and guarded marketing workflow.",
            ),
            Block("h1", "Part II — Data research"),
            Block("h2", "1. Objective and data needs"),
            Block(
                "p",
                "The data must support customer-level history before a cutoff and fully observed future outcomes after it. Required fields are a stable customer identifier, transaction/invoice identifier, timestamp, product identifier, quantity and price. Cancellation indicators, country and descriptions help quality checks. Advertising data is not required to train the first churn-proxy model; it belongs to later attribution and activation workflows.",
            ),
            Block("h2", "2. Candidate assessment"),
            Block(
                "table",
                (
                    ["Dataset", "Scope / access", "Fit", "Decision"],
                    [
                        [
                            "UCI Online Retail II",
                            "1,067,371 lines; 2009-12-01 to 2011-12-09; XLSX; CC BY 4.0; DOI 10.24432/C5CG6D",
                            "Two years, stable customer/invoice/time fields, multiple temporal cutoffs",
                            "Selected",
                        ],
                        [
                            "UCI Online Retail",
                            "541,909 lines; approximately one year; CC BY 4.0; DOI 10.24432/C5BW33",
                            "Same retailer but shorter history",
                            "Rejected in favor of longer source",
                        ],
                        [
                            "Online Shoppers Purchasing Intention",
                            "12,330 sessions; CC BY 4.0; DOI 10.24432/C5F88Q",
                            "Session conversion, not longitudinal customer inactivity",
                            "Rejected",
                        ],
                    ],
                    [1900, 3300, 2780, 1380],
                ),
                note="Sources: UCI dataset records and repository dataset decision memo.",
            ),
            Block("h2", "3. Selected source profile"),
            Block(
                "table",
                (
                    ["Dimension", "Project-reproduced value"],
                    [
                        ["Raw size", f"{raw['rows']:,} rows; 8 fields; 43 countries"],
                        ["Period", f"{raw['date_min'][:10]} to {raw['date_max'][:10]}"],
                        [
                            "Customers / invoices",
                            f"{raw['identified_customers']:,} identified customers; {raw['invoices']:,} invoices",
                        ],
                        [
                            "Missingness",
                            f"{raw['missing_customer_rows']:,} rows missing customer ID; {raw['missing_description_rows']:,} missing description",
                        ],
                        [
                            "Transaction anomalies",
                            f"{raw['cancellation_rows']:,} cancellation rows; {raw['nonpositive_quantity_rows']:,} nonpositive quantity; {raw['nonpositive_price_rows']:,} nonpositive price",
                        ],
                        ["Duplicates", f"{raw['exact_duplicate_rows']:,} exact duplicate rows"],
                        [
                            "Eligible purchase evidence",
                            f"{profile['eligible_purchase_lines']:,} lines; {profile['purchase_events']:,} purchase events; {profile['purchase_customers']:,} customers",
                        ],
                    ],
                    [2500, 6860],
                ),
                note="Evidence class: project-reproduced from external source. Values are generated by scripts/profile_dataset.py.",
            ),
            Block("h2", "4. Quality, privacy and limitations"),
            Block(
                "bullet",
                "Raw data is checksum-verified and ignored from Git; generated profiles record source URL, DOI, licence, size and SHA-256.",
            ),
            Block(
                "bullet",
                "Modeling excludes exact duplicates, unusable identity/date rows, cancellations and nonpositive purchase lines from eligible purchase events; raw evidence is not overwritten.",
            ),
            Block(
                "bullet",
                "Customer IDs are pseudonymous identifiers but still treated as linkable data. Processed customer-level files remain local and ignored; academic outputs contain only aggregates.",
            ),
            Block(
                "bullet",
                "The source is historical, single-retailer, UK-based and partly wholesale. Missing identifiers and survivor/censoring effects restrict representativeness.",
            ),
            Block("h2", "5. Exploratory evidence and marketing insight"),
            Block(
                "figure",
                (
                    "artifacts/eda/training_label_recency.png",
                    "Figure 1. Training-snapshot inactivity prevalence and recency distribution. Project-generated evidence.",
                    6.25,
                ),
            ),
            Block(
                "figure",
                (
                    "artifacts/eda/training_frequency_spend.png",
                    "Figure 2. Training-snapshot frequency and spend behavior. Project-generated evidence.",
                    6.25,
                ),
            ),
            Block(
                "p",
                "Median purchases per identified purchase customer are 3; the median observed interpurchase gap is 24.197 days and the 75th percentile is 61.194 days. These aggregates support a 90-day future window as a practical, purchase-cycle-informed inactivity horizon. They do not prove permanent loss. The skewed frequency/spend distributions also support log transformations and robust evaluation rather than raw-scale assumptions.",
            ),
            Block("h2", "6. Data conclusion"),
            Block(
                "p",
                "Online Retail II is adequate for a reproducible temporal classification study and inadequate for claiming universal churn or campaign causality. Its licensing and provenance are explicit. Production use requires tenant-owned, consent-governed current data and new drift/quality validation.",
            ),
            Block("h1", "Part III — Technology review"),
            Block("h2", "1. Technology objective and marketing relevance"),
            Block(
                "p",
                "The technology must support ordinary customer operations and auditable intelligence in the same product. The priority is not maximum algorithmic complexity; it is reliable imports, canonical definitions, reproducible training/inference, tenant isolation, useful explanations and controlled actions.",
            ),
            Block("h2", "2. Comparison"),
            Block(
                "table",
                (
                    ["Area", "Selected technology", "Why selected", "Trade-off / control"],
                    [
                        [
                            "API/domain",
                            "Python 3.12, FastAPI, Pydantic, SQLAlchemy",
                            "Typed validation, OpenAPI, shared ML ecosystem",
                            "Modular-monolith discipline and strict typing required",
                        ],
                        [
                            "Database/tenancy",
                            "PostgreSQL RLS",
                            "Transactions, constraints, analytics and row-level tenant policy",
                            "RLS is defense-in-depth; application scope tests still required",
                        ],
                        [
                            "Web",
                            "Next.js, React, strict TypeScript",
                            "Server-rendered operator UI and typed boundaries",
                            "Automated desktop/mobile Chromium and Axe checks pass; manual multi-browser and assistive-technology review remains external",
                        ],
                        [
                            "Jobs",
                            "Redis, Dramatiq, transactional outbox",
                            "Durable async imports/sync/scoring with retries",
                            "Operational monitoring and managed Redis needed",
                        ],
                        [
                            "Modeling",
                            "scikit-learn + LightGBM candidates",
                            "Transparent pipelines plus nonlinear challenger",
                            "Validation chose regularized logistic regression, not assumed LightGBM",
                        ],
                        [
                            "Tracking",
                            "MLflow",
                            "Run, parameter, metric and artifact provenance",
                            "Local registry is not a production registry service",
                        ],
                        [
                            "Explanation",
                            "SHAP + logistic coefficients",
                            "Local/global score decomposition",
                            "Not causal; categorical encoding and correlated features complicate interpretation",
                        ],
                        [
                            "Deployment",
                            "Containers + Terraform AWS reference",
                            "Portable local-to-cloud boundary",
                            "Paid cloud deployment and restore drills remain external",
                        ],
                    ],
                    [1300, 1900, 3200, 2960],
                ),
                note="Performance and cost conclusions are architectural assessments, not benchmark claims. Live provider latency/cost was not measured.",
            ),
            Block("h2", "3. Industry examples and project use cases"),
            Block(
                "p",
                "The following external-source examples show how established platforms place machine learning inside marketing operations. They document product capabilities, not outcomes achieved by GrowthPilot.",
            ),
            Block(
                "table",
                (
                    ["External product", "Marketing use / evidence", "Lesson for GrowthPilot"],
                    [
                        [
                            "Salesforce Einstein Lead Scoring",
                            "Analyzes historical lead-conversion patterns to prioritize current leads and exposes influential fields in CRM views.",
                            "A score becomes operationally useful when it appears in the user's workflow with an explanation; vendor capability is not GrowthPilot outcome evidence.",
                        ],
                        [
                            "Google Ads Smart Bidding",
                            "Uses Google AI for auction-time bidding toward conversions or conversion value; it depends on conversion tracking and may depend on historical conversion volume.",
                            "Optimization quality depends on measurement and provider data. GrowthPilot therefore keeps provider execution separate from first-party decision governance.",
                        ],
                    ],
                    [1800, 3700, 3860],
                ),
                note="External-source capability examples. No vendor performance claim or GrowthPilot business outcome is asserted.",
            ),
            Block("h3", "GrowthPilot application"),
            Block(
                "bullet",
                "Customer 360: orders, value, RFM segment, predictions and consent in one tenant-scoped view.",
            ),
            Block(
                "bullet",
                "Capacity-aware retention review: sort customers by calibrated inactivity risk and commercial importance, then require approval.",
            ),
            Block(
                "bullet",
                "Operational analytics: versioned revenue/order/customer/inventory metrics with explicit null states when data is unavailable.",
            ),
            Block(
                "bullet",
                "Provider-neutral marketing ingestion: bounded raw payload provenance and canonical daily facts through fixed-origin adapters.",
            ),
            Block("h2", "4. Limitations and opportunities"),
            Block(
                "p",
                "No live Meta, Google Ads, OIDC, LLM or cloud credentials were supplied; these boundaries are implemented and mock-tested but not live-validated. The local MLflow registry and single historical dataset do not establish production robustness. Next work after review should include credentialed sandbox validation, load/resilience tests, manual multi-browser and assistive-technology review, managed backup/restore rehearsal and monitoring thresholds based on real operating data.",
            ),
            Block("h2", "5. Technology conclusion"),
            Block(
                "p",
                "The stack is appropriate because it makes the capstone reproducible without separating the evidence pipeline from product controls. It remains a production-oriented local implementation, not a production deployment.",
            ),
            Block("h1", "References"),
            Block(
                "p",
                "Batislam, E. P., Denizel, M., & Filiztekin, A. (2007). Empirical validation and comparison of models for customer base analysis. International Journal of Research in Marketing, 24(3), 201–209. https://doi.org/10.1016/j.ijresmar.2006.12.005",
            ),
            Block(
                "p",
                "Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D",
            ),
            Block(
                "p",
                "Jerath, K., Fader, P. S., & Hardie, B. G. S. (2011). New perspectives on customer “death” using a generalization of the Pareto/NBD model. Marketing Science, 30(5), 866–880. https://doi.org/10.1287/mksc.1110.0654",
            ),
            Block(
                "p",
                "Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems, 30. https://arxiv.org/abs/1705.07874",
            ),
            Block(
                "p",
                "Platzer, M., & Reutterer, T. (2016). Ticking away the moments: Timing regularity helps to better predict customer activity. Marketing Science, 35(5), 779–799. https://doi.org/10.1287/mksc.2015.0963",
            ),
            Block(
                "p",
                "Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. PLOS ONE, 10(3), e0118432. https://doi.org/10.1371/journal.pone.0118432",
            ),
            Block(
                "p",
                "Salesforce. (n.d.). Einstein Lead Scoring. Salesforce Help. https://help.salesforce.com/s/articleView?id=einstein_sales_lead_insights.htm&language=en_US. Accessed 11 September 2026.",
            ),
            Block(
                "p",
                "Google Ads Help. (n.d.). About Smart Bidding. https://support.google.com/google-ads/answer/7065882?hl=en. Accessed 11 September 2026.",
            ),
            Block(
                "p",
                "Technology documentation: PostgreSQL row security; scikit-learn model evaluation and calibration; LightGBM Python API; SHAP documentation; MLflow tracking; FastAPI security; Next.js App Router. Accessed 8–9 September 2026; URLs are recorded in repository ADRs and research notes.",
            ),
        ],
    )


def concept_submission() -> Submission:
    return Submission(
        "02_Concept_Note_and_Implementation_Plan",
        "Concept Note and Implementation Plan",
        "GrowthPilot AI — governed customer operations and marketing intelligence for small retail teams",
        [
            Block("h1", "Part I — Concept note"),
            Block("h2", "1. Project overview, context and intended impact"),
            Block(
                "p",
                "GrowthPilot AI is a multi-tenant, production-oriented application that unifies customer, order, product, inventory and advertising data; provides CRM/ERP-lite workflows; and turns versioned analytics and ML-supported evidence into reviewed marketing decisions. The first capstone ML problem is 90-day future-purchase inactivity classification. It is one component of the product, not the whole product.",
            ),
            Block(
                "p",
                "The intended users are small retail operators and marketing managers who need a consistent customer record and a safer way to prioritize retention work. Intended impact is faster analysis, fewer definition disputes and more disciplined outreach review. No revenue uplift, adoption, campaign outcome or user result has yet been measured.",
            ),
            Block("h2", "2. Objectives and KPIs"),
            Block(
                "table",
                (
                    ["Objective", "KPI", "Baseline", "Target / decision rule"],
                    [
                        [
                            "Unify operating data",
                            "Valid imports, rejected-row visibility, provenance coverage",
                            "No production baseline available",
                            "100% of accepted imports record tenant, source, actor and checksum",
                        ],
                        [
                            "Surface reliable customer intelligence",
                            "KPI freshness; prediction version coverage",
                            "No production baseline available",
                            "Every prediction stores model/feature/target versions and checksum",
                        ],
                        [
                            "Prioritize limited outreach",
                            "Precision, recall and lift at capacity",
                            "Test prevalence 0.392857",
                            "Frozen ~10% policy; report evidence, do not promise uplift",
                        ],
                        [
                            "Protect customers and tenants",
                            "Cross-tenant denials; unauthorized actions",
                            "Not applicable before implementation",
                            "Zero known leakage in automated isolation tests; all actions server-authorized",
                        ],
                        [
                            "Govern marketing execution",
                            "Consent checks; approvals; budget/kill-switch blocks",
                            "No live execution",
                            "Execution disabled by default; explicit approval and live validation required",
                        ],
                    ],
                    [2400, 2500, 1900, 2560],
                ),
                note="Targets are governance/quality acceptance rules, not fabricated commercial outcomes.",
            ),
            Block("h2", "3. Background and rationale"),
            Block(
                "p",
                "The product concept responds to fragmentation: analytics notebooks alone do not resolve data capture, identity, permission, consent or execution safety. Literature on non-contractual customer bases shows that inactivity is latent and model-dependent. GrowthPilot therefore defines an observable future purchase window, uses time-based validation and stores a clear evidence trail.",
            ),
            Block("h2", "4. AI methodology and evaluation"),
            Block(
                "number",
                "Profile purchase cadence on training history only and freeze a 90-day label horizon.",
            ),
            Block(
                "number",
                "Construct leakage-safe customer snapshots using events strictly before each cutoff.",
            ),
            Block(
                "number",
                "Compare a recency heuristic, a prevalence dummy, regularized logistic regression, random forest and LightGBM.",
            ),
            Block(
                "number",
                "Select by validation PR-AUC; refine hyperparameters and probability calibration before touching the final test.",
            ),
            Block(
                "number",
                "Freeze the model artifact and ~10% capacity threshold, evaluate once on the untouched 2011-09-01 temporal test and prohibit post-test retuning.",
            ),
            Block(
                "number",
                "Validate SHAP/log-odds additivity; store local explanations as fitted-model evidence only.",
            ),
            Block(
                "p",
                "Primary measures are PR-AUC, ROC-AUC, Brier score, log loss and ECE, with precision/recall/lift at capacity and bootstrap intervals on the final test. A later business-impact test must randomize eligible customers into treatment/control or use another defensible causal design.",
            ),
            Block("h2", "5. Architecture and workflow"),
            Block(
                "figure",
                (
                    "academic/figures/architecture_workflow.png",
                    "Figure 1. Implemented data-to-decision architecture. Execution is disabled by default.",
                    6.4,
                ),
            ),
            Block(
                "p",
                "The web application calls a FastAPI modular monolith. PostgreSQL enforces tenant keys, constraints and row-level security; Redis/Dramatiq workers consume durable outbox jobs. Validated imports and provider adapters populate canonical records. Analytics and scoring share versioned definitions. Audiences are snapshot-based, current consent is checked, and campaigns must be approved before queueing. External action remains blocked by the kill switch and zero default budget.",
            ),
            Block("h2", "6. Data"),
            Block(
                "p",
                "The capstone experiment uses UCI Online Retail II (Chen, 2012; CC BY 4.0; DOI 10.24432/C5CG6D), 1,067,371 transaction lines covering 2009-12-01 through 2011-12-09. Production use would require each tenant’s own authorized customer/order data and provider credentials. Raw sources are checksum-verified; customer-level prepared artifacts are local and ignored.",
            ),
            Block("h2", "7. Literature and industry context"),
            Block(
                "p",
                "Jerath, Fader and Hardie (2011), Batislam et al. (2007), and Platzer and Reutterer (2016) motivate a purchase-cadence-aware but operational definition of inactivity. Modern CRM and ad platforms expose pieces of the workflow, but GrowthPilot’s concept is an integrated, provider-neutral control plane with explicit provenance, tenant scope and human authorization. This comparison is functional, not a claim of commercial superiority.",
            ),
            Block("h1", "Part II — Implementation plan"),
            Block("h2", "1. Technology stack"),
            Block(
                "table",
                (
                    ["Layer", "Technology", "Responsibility"],
                    [
                        [
                            "Web",
                            "Next.js, React, strict TypeScript",
                            "Operator navigation, honest loading/empty/error states, customer 360",
                        ],
                        [
                            "API",
                            "Python 3.12, FastAPI, Pydantic, SQLAlchemy",
                            "Validation, RBAC, domain rules, OpenAPI",
                        ],
                        [
                            "Data",
                            "PostgreSQL + RLS; S3-compatible object boundary",
                            "Canonical records, provenance, tenant isolation, bounded raw payloads",
                        ],
                        [
                            "Async",
                            "Redis, Dramatiq, outbox",
                            "Import, sync and scoring jobs with rechecked permissions",
                        ],
                        [
                            "ML",
                            "pandas/Polars, scikit-learn, LightGBM, SHAP, MLflow",
                            "Feature pipeline, experiments, registry, explanations",
                        ],
                        [
                            "Quality/ops",
                            "pytest, Ruff, mypy, Vitest, ESLint, OTel, Prometheus",
                            "Automated gates and observability",
                        ],
                    ],
                    [1700, 3000, 4660],
                ),
            ),
            Block("h2", "2. Timeline and ownership"),
            Block(
                "table",
                (
                    ["Phase window", "Work package", "Owner / reviewer", "Evidence / status"],
                    [
                        [
                            "2026-09-08",
                            "Governance, architecture, domain and data contracts",
                            "Codex / Project Lead",
                            "Local commits; ADRs; requirements — complete",
                        ],
                        [
                            "2026-09-08",
                            "Dataset research, preparation, features and model exploration",
                            "Codex / ML-AI Lead",
                            "Profiles, splits, MLflow runs — complete",
                        ],
                        [
                            "2026-09-08",
                            "Refinement, frozen test, explanations and decision evidence",
                            "Codex / ML-AI Lead",
                            "Final artifacts and checksums — complete",
                        ],
                        [
                            "2026-09-09",
                            "Inference, UI, integrations, attribution, audiences and generation",
                            "Codex / Project Lead",
                            "Local code/tests — complete; live credentials absent",
                        ],
                        [
                            "2026-09-09",
                            "Security hardening, academic package and release readiness",
                            "Codex / Founder",
                            "Local validation — in final review",
                        ],
                        [
                            "After approval",
                            "Credentialed sandboxes, deployment, pilot and causal impact test",
                            "Founder / Project Lead",
                            "External validation — not started",
                        ],
                    ],
                    [1600, 3000, 2100, 2660],
                ),
                note="These are actual local execution dates, not backdated instructor submission claims.",
            ),
            Block("h2", "3. Milestones and evidence"),
            Block(
                "bullet",
                "M0–M1: governance baseline, accepted ADRs, threat/data contracts and clean Git history.",
            ),
            Block(
                "bullet",
                "M2–M5: cited research, licensed source, reproducible preparation, model comparison, frozen evaluation and explanation evidence.",
            ),
            Block(
                "bullet",
                "M6–M10: tenant-safe API/UI, CRM/commerce/imports, intelligence, adapters, attribution, audiences and approval lifecycle.",
            ),
            Block(
                "bullet",
                "M11–M12: security/recovery boundaries, complete tests, academic deliverables, demo script and release-readiness report.",
            ),
            Block("h2", "4. Challenges, mitigations and fallback plans"),
            Block(
                "table",
                (
                    ["Risk", "Mitigation", "Fallback / decision boundary"],
                    [
                        [
                            "Historical single-retailer bias",
                            "Temporal holdout, intervals, explicit evidence labels",
                            "Do not deploy model until tenant data is validated",
                        ],
                        [
                            "Inactivity is not contractual churn",
                            "Operational label and target version",
                            "Present score as inactivity risk only",
                        ],
                        [
                            "Cross-tenant leakage",
                            "Tenant keys, server guards, PostgreSQL RLS, adversarial tests",
                            "Block release on any unresolved leakage",
                        ],
                        [
                            "Provider/API change or missing credentials",
                            "Adapters, fixed origins, mocks, durable sync records",
                            "Keep integration disabled; import CSV/XLSX",
                        ],
                        [
                            "Uncertain campaign effect",
                            "Separate prediction from causal measurement",
                            "Use no-send planning mode until approved experiment",
                        ],
                        [
                            "Unsafe generated content",
                            "Server-derived facts, forbidden-claim validation, human approval",
                            "Disabled provider; manual draft only",
                        ],
                        [
                            "Operational outage/data loss",
                            "Health/metrics, backups/runbooks, durable jobs",
                            "RPO/RTO remain targets until restore drill",
                        ],
                    ],
                    [2250, 3650, 3460],
                ),
            ),
            Block("h2", "5. Ethics and responsible AI"),
            Block(
                "bullet",
                "Purpose limitation and minimization: customer-level outputs stay inside tenant scope; academic deliverables use aggregates.",
            ),
            Block(
                "bullet",
                "Consent and human agency: scoring never authorizes an action; audience membership is rechecked; approvals are explicit.",
            ),
            Block(
                "bullet",
                "Transparency: target, features, model, threshold and limitations are versioned; explanations are noncausal.",
            ),
            Block(
                "bullet",
                "Fairness: country and other sensitive/proxy effects require lawful subgroup review before production. No fairness claim is made from this dataset.",
            ),
            Block(
                "bullet",
                "Security: secret references, not secret values, are stored; provider requests use fixed HTTPS origins and no redirects.",
            ),
            Block("h2", "6. Current delivery boundary"),
            Block(
                "p",
                "The local implementation and academic evidence are complete for review. Automated desktop/mobile Chromium and Axe checks pass; live Meta/Google/LLM/OIDC/cloud validation, production restore drills, manual multi-browser and assistive-technology testing, and any real campaign execution remain external. No push, paid deployment or advertising spend is authorized by this plan.",
            ),
            Block("h1", "References"),
            Block(
                "p",
                "Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D",
            ),
            Block(
                "p",
                "Jerath, K., Fader, P. S., & Hardie, B. G. S. (2011). New perspectives on customer “death” using a generalization of the Pareto/NBD model. Marketing Science, 30(5), 866–880. https://doi.org/10.1287/mksc.1110.0654",
            ),
            Block(
                "p",
                "Batislam, E. P., Denizel, M., & Filiztekin, A. (2007). Empirical validation and comparison of models for customer base analysis. International Journal of Research in Marketing, 24(3), 201–209. https://doi.org/10.1016/j.ijresmar.2006.12.005",
            ),
            Block(
                "p",
                "Project sources: docs/03_ARCHITECTURE_DECISIONS.md, docs/08_DELIVERY_PLAN.md, docs/07_SECURITY_PRIVACY_RESPONSIBLE_AI.md, artifacts/reports and artifacts/ml.",
            ),
        ],
    )


def data_model_submission(prep: dict[str, Any], exploration: dict[str, Any]) -> Submission:
    models = exploration["models"]
    return Submission(
        "03_Data_Preparation_Feature_Engineering_Model_Exploration",
        "Data Preparation, Feature Engineering and Model Exploration",
        "Reproducible temporal customer modeling for future-purchase inactivity",
        [
            Block("h1", "Part I — Data preparation and feature engineering"),
            Block("h2", "1. Overview and collection"),
            Block(
                "p",
                "The pipeline downloads UCI Online Retail II from its stable repository URL, verifies SHA-256 572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb, profiles both worksheets and writes deterministic reports. Raw and customer-level prepared files are local/ignored; aggregate evidence and scripts are versioned.",
            ),
            Block("h2", "2. Cleaning and validation"),
            Block(
                "table",
                (
                    ["Step", "Rows / rule", "Rationale"],
                    [
                        [
                            "Raw input",
                            f"{prep['cleaning']['raw_rows']:,}",
                            "Preserved external-source evidence",
                        ],
                        [
                            "Exact duplicate removal",
                            f"{prep['cleaning']['exact_duplicates_removed']:,} removed",
                            "Avoid repeated identical transaction lines",
                        ],
                        [
                            "Identity/date usability",
                            f"{prep['cleaning']['rows_without_usable_identity_or_date']:,} excluded",
                            "Customer snapshots require stable ID and time",
                        ],
                        [
                            "Normalized retained rows",
                            f"{prep['cleaning']['normalized_rows']:,}",
                            "Canonical names/types after deterministic rules",
                        ],
                        [
                            "Eligible purchase event",
                            "Positive quantity and price; non-cancellation; pre-cutoff",
                            "Separate purchases from returns/cancellations",
                        ],
                    ],
                    [2500, 2400, 4460],
                ),
                note="Evidence class: project-generated from artifacts/reports/data_preparation.json.",
            ),
            Block(
                "p",
                "Missing customer identifiers are not imputed because arbitrary identity assignment would create false histories. Missing descriptions do not block customer-level behavior features. Nonpositive quantity/price and cancellation invoices are excluded from eligible purchase events but remain part of source-quality evidence. Monetary outliers are not winsorized before aggregation; log1p and standardized transformations reduce scale dominance inside fitted pipelines.",
            ),
            Block("h2", "3. Temporal snapshots and leakage prevention"),
            Block(
                "table",
                (
                    ["Split", "Cutoff(s)", "Rows", "Inactivity rate"],
                    [
                        [
                            "Training",
                            "2010-06-01 monthly through 2010-12-01",
                            f"{prep['splits']['train']['rows']:,}",
                            f"{prep['splits']['train']['inactive_rate']:.6f}",
                        ],
                        [
                            "Validation",
                            "2011-03-01",
                            f"{prep['splits']['validation']['rows']:,}",
                            f"{prep['splits']['validation']['inactive_rate']:.6f}",
                        ],
                        [
                            "Calibration",
                            "2011-06-01",
                            f"{prep['splits']['calibration']['rows']:,}",
                            f"{prep['splits']['calibration']['inactive_rate']:.6f}",
                        ],
                        [
                            "Final test",
                            "2011-09-01",
                            f"{prep['splits']['test']['rows']:,}",
                            "Sealed until final evaluation",
                        ],
                    ],
                    [1900, 3000, 1800, 2660],
                ),
                note="All features use events strictly before the cutoff; each 90-day label window is fully observed.",
            ),
            Block("h2", "4. EDA"),
            Block(
                "figure",
                (
                    "artifacts/eda/training_label_recency.png",
                    "Figure 1. Label prevalence and recency across training snapshots.",
                    6.25,
                ),
            ),
            Block(
                "figure",
                (
                    "artifacts/eda/training_frequency_spend.png",
                    "Figure 2. Frequency and spend distributions support transformed modeling.",
                    6.25,
                ),
            ),
            Block(
                "p",
                "Training contains 20,677 customer snapshots with 48.3823% inactivity labels. Validation has 3,349 rows with 57.7187% inactivity. The prevalence shift is one reason accuracy is unsuitable as the primary measure. Skew and repeat observations also motivate time-based evaluation and customer-behavior aggregates rather than random line-level splitting.",
            ),
            Block("h2", "5. Feature design"),
            Block(
                "table",
                (
                    ["Feature family", "Examples", "Rationale"],
                    [
                        [
                            "Recency/tenure",
                            "recency_days, tenure_days",
                            "How recently and how long the relationship has existed",
                        ],
                        [
                            "Frequency/cadence",
                            "invoice_count, active_days, mean/median/max gap",
                            "Repeat behavior and purchase periodicity",
                        ],
                        [
                            "Monetary",
                            "gross/net spend, average order value, return value",
                            "Commercial magnitude and reversal behavior",
                        ],
                        [
                            "Product breadth",
                            "distinct products, quantity, basket breadth",
                            "Depth and diversity of engagement",
                        ],
                        [
                            "Windowed behavior",
                            "30/60/90-day counts/spend; trend deltas",
                            "Recent acceleration or decline before cutoff",
                        ],
                        [
                            "Context",
                            "country and snapshot month",
                            "Market/time context, encoded inside the pipeline",
                        ],
                    ],
                    [2100, 3300, 3960],
                ),
            ),
            Block("h2", "6. Scaling, normalization and encoding"),
            Block(
                "p",
                "The scikit-learn ColumnTransformer fits preprocessing only on training data. Numeric columns use median imputation, log1p where defined and StandardScaler for logistic regression. Categorical values use most-frequent imputation and one-hot encoding with unknown-category tolerance. Tree candidates use compatible encoded input without assuming that scaling improves trees.",
            ),
            Block(
                "code",
                "numeric = Pipeline([\n    ('impute', SimpleImputer(strategy='median')),\n    ('scale', StandardScaler()),\n])\ncategorical = Pipeline([\n    ('impute', SimpleImputer(strategy='most_frequent')),\n    ('onehot', OneHotEncoder(handle_unknown='ignore')),\n])\nmodel = Pipeline([('preprocess', ColumnTransformer(...)),\n                  ('classifier', LogisticRegression(C=0.01, max_iter=2000))])",
            ),
            Block("h1", "Part II — Model exploration"),
            Block("h2", "1. Candidate selection rationale"),
            Block(
                "p",
                "The recency heuristic is a business baseline; the dummy prior detects whether a model adds ranking information. Logistic regression is transparent, fast and regularizable. Random forest captures nonlinear interactions with modest preprocessing. LightGBM is an efficient boosted-tree challenger. The concept deck anticipated LightGBM, but the experiment did not privilege it: validation PR-AUC selected logistic regression.",
            ),
            Block(
                "table",
                (
                    ["Candidate", "Strength", "Weakness"],
                    [
                        [
                            "Recency heuristic",
                            "Simple, explainable business reference",
                            "Ignores frequency, value and cadence",
                        ],
                        [
                            "Dummy prior",
                            "Calibration/prevalence sanity check",
                            "No individualized ranking",
                        ],
                        [
                            "Logistic regression",
                            "Transparent, efficient, stable regularization",
                            "Linear log-odds boundary; encoded interactions limited",
                        ],
                        [
                            "Random forest",
                            "Nonlinear interactions and robustness",
                            "Larger model; probability calibration may degrade",
                        ],
                        [
                            "LightGBM",
                            "Strong nonlinear tabular learner",
                            "More tuning/interpretation complexity and overfit risk",
                        ],
                    ],
                    [2100, 3500, 3760],
                ),
            ),
            Block("h2", "2. Training, hyperparameters and validation"),
            Block(
                "p",
                "Candidate preprocessing and models are fit on seven pre-test training cutoffs. Model family is selected by the single 2011-03-01 validation snapshot. A later 2011-06-01 calibration snapshot is reserved for sigmoid probability calibration and the operational threshold; the final 2011-09-01 cutoff is never used during exploration.",
            ),
            Block(
                "table",
                (
                    [
                        "Model",
                        "Key parameters",
                        "Validation PR-AUC",
                        "ROC-AUC",
                        "Brier",
                        "Top-10% lift",
                    ],
                    [
                        [
                            "Recency",
                            "clip(recency/180)",
                            f"{models['recency_heuristic']['validation']['pr_auc']:.6f}",
                            f"{models['recency_heuristic']['validation']['roc_auc']:.6f}",
                            f"{models['recency_heuristic']['validation']['brier']:.6f}",
                            f"{models['recency_heuristic']['validation']['lift_at_10']:.6f}",
                        ],
                        [
                            "Dummy",
                            "prior",
                            f"{models['dummy_prior']['validation']['pr_auc']:.6f}",
                            f"{models['dummy_prior']['validation']['roc_auc']:.6f}",
                            f"{models['dummy_prior']['validation']['brier']:.6f}",
                            f"{models['dummy_prior']['validation']['lift_at_10']:.6f}",
                        ],
                        [
                            "Logistic",
                            "C=1.0",
                            f"{models['logistic']['validation']['pr_auc']:.6f}",
                            f"{models['logistic']['validation']['roc_auc']:.6f}",
                            f"{models['logistic']['validation']['brier']:.6f}",
                            f"{models['logistic']['validation']['lift_at_10']:.6f}",
                        ],
                        [
                            "Random forest",
                            "300 trees; leaf=10",
                            f"{models['random_forest']['validation']['pr_auc']:.6f}",
                            f"{models['random_forest']['validation']['roc_auc']:.6f}",
                            f"{models['random_forest']['validation']['brier']:.6f}",
                            f"{models['random_forest']['validation']['lift_at_10']:.6f}",
                        ],
                        [
                            "LightGBM",
                            "300 trees; lr=.05; leaves=31",
                            f"{models['lightgbm']['validation']['pr_auc']:.6f}",
                            f"{models['lightgbm']['validation']['roc_auc']:.6f}",
                            f"{models['lightgbm']['validation']['brier']:.6f}",
                            f"{models['lightgbm']['validation']['lift_at_10']:.6f}",
                        ],
                    ],
                    [1300, 2160, 1500, 1400, 1400, 1600],
                ),
                note="Selection metric: validation PR-AUC. Initial winner: logistic regression.",
            ),
            Block("h2", "3. Evaluation interpretation"),
            Block(
                "p",
                "Logistic PR-AUC 0.805322 narrowly exceeds LightGBM 0.805223 and random forest 0.803517 in initial exploration. Tree candidates have better uncalibrated Brier values, which motivates a separate calibration step rather than changing the selection metric after seeing results. The recency baseline is meaningfully weaker but nontrivial, confirming that simple recency carries signal.",
            ),
            Block("h2", "4. Reproducibility"),
            Block(
                "code",
                "make data-download\nmake data-profile\nmake data-prepare\nmake features-build\nmake train\n# Outputs include split hashes, MLflow run IDs, parameters and validation metrics.",
            ),
            Block(
                "p",
                "Every split has a SHA-256 checksum and versioned target/feature/split identifiers. MLflow records model runs. The final test flag in model_exploration.json is false, demonstrating that exploration completed before final-test access.",
            ),
            Block("h2", "5. Conclusion"),
            Block(
                "p",
                "The preparation pipeline is leakage-aware, deterministic and suitable for the chosen historical study. Initial exploration selected logistic regression for refinement. This conclusion is limited to the stated validation cutoff and metric; it does not claim universal superiority or production readiness.",
            ),
            Block("h1", "References"),
            Block(
                "p",
                "Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D",
            ),
            Block(
                "p",
                "scikit-learn developers. Model evaluation, preprocessing and probability calibration documentation. https://scikit-learn.org/stable/",
            ),
            Block(
                "p",
                "Ke, G., et al. (2017). LightGBM: A highly efficient gradient boosting decision tree. Advances in Neural Information Processing Systems, 30.",
            ),
            Block(
                "p",
                "Project evidence: artifacts/reports/dataset_profile.json, artifacts/reports/data_preparation.json, artifacts/eda, artifacts/ml/model_exploration.json and the corresponding scripts/tests.",
            ),
        ],
    )


def refinement_submission(candidate: dict[str, Any], final: dict[str, Any]) -> Submission:
    val = candidate["validation"]
    cal = candidate["calibration_fit"]
    test = final["metrics"]
    return Submission(
        "04_Model_Refinement_and_Test_Submission",
        "Model Refinement and Test Submission",
        "Frozen, calibrated logistic churn-proxy candidate and untouched temporal evaluation",
        [
            Block("h1", "Part I — Model refinement"),
            Block("h2", "1. Initial evaluation and weaknesses"),
            Block(
                "p",
                "Initial exploration selected logistic regression by validation PR-AUC 0.805322. Its weaknesses were probability miscalibration (Brier 0.213300; ECE 0.169377) and sensitivity to regularization. LightGBM was nearly tied on PR-AUC and had better raw calibration, so refinement compared all three learned families without changing the primary selection rule.",
            ),
            Block("h2", "2. Refinement techniques"),
            Block(
                "bullet",
                "Logistic grid: C ∈ {0.01, 0.05, 0.2, 1.0, 5.0}; class weighting kept off because ranking/calibration and capacity metrics were evaluated directly.",
            ),
            Block(
                "bullet",
                "Random forest grid: 400 trees, minimum leaf {5,10,20}, maximum depth {8,16}.",
            ),
            Block(
                "bullet",
                "LightGBM: 12 seeded search trials across learning rate, leaves, depth, minimum child samples, L2 regularization, row and column subsampling.",
            ),
            Block(
                "bullet", "Sigmoid calibration fitted only on the 2011-06-01 calibration snapshot."
            ),
            Block(
                "bullet",
                "Operating threshold fixed at 0.812509305136 from approximately 10% calibration capacity.",
            ),
            Block("h2", "3. Tuning impact"),
            Block(
                "table",
                (
                    ["Stage", "PR-AUC", "ROC-AUC", "Brier", "ECE", "Top-10% precision / lift"],
                    [
                        [
                            "Initial logistic validation",
                            "0.805322",
                            "0.782819",
                            "0.213300",
                            "0.169377",
                            "0.871642 / 1.510154",
                        ],
                        [
                            "Refined logistic C=.01 validation",
                            f"{val['pr_auc']:.6f}",
                            f"{val['roc_auc']:.6f}",
                            f"{val['brier']:.6f}",
                            f"{val['ece_10']:.6f}",
                            f"{val['precision_at_10']:.6f} / {val['lift_at_10']:.6f}",
                        ],
                        [
                            "Calibration-fit descriptive",
                            f"{cal['pr_auc']:.6f}",
                            f"{cal['roc_auc']:.6f}",
                            f"{cal['brier']:.6f}",
                            f"{cal['ece_10']:.6f}",
                            f"{cal['precision_at_10']:.6f} / {cal['lift_at_10']:.6f}",
                        ],
                    ],
                    [2250, 1300, 1300, 1200, 1100, 2210],
                ),
                note="Calibration-fit metrics reuse calibration labels and are descriptive, not unbiased test estimates.",
            ),
            Block(
                "p",
                "Lowering C from 1.0 to 0.01 increased validation PR-AUC to 0.812223 and reduced Brier to 0.196710. Sigmoid calibration on the later calibration split reduced ECE to 0.040863 descriptively. The final serialized candidate checksum is 942d705d66a9469d57494626a99da83c91a9a895a3a2b2d7e977ff3ba56952ad.",
            ),
            Block("h2", "4. Cross-validation and feature selection decisions"),
            Block(
                "p",
                "Random k-fold cross-validation was not used because it would mix future and past snapshots and repeated customers. The design instead uses expanding chronological training cutoffs plus distinct validation, calibration and final-test dates. No post-hoc feature selection was performed: the regularized logistic pipeline controls coefficient magnitude, and removing features after observing the test would violate the freeze.",
            ),
            Block("h2", "5. Explainability validation"),
            Block(
                "figure",
                (
                    "artifacts/ml/explanations_global.png",
                    "Figure 1. Global mean absolute SHAP contribution in calibrated log-odds. Project-generated diagnostic.",
                    6.25,
                ),
            ),
            Block(
                "p",
                "The SHAP decomposition was computed in calibrated log-odds for the frozen logistic pipeline. Maximum additivity error is 8.881784197001252×10⁻¹⁶, confirming numerical consistency. Contributions explain this model’s score formation; they are not causal effects and must not be turned into unsupported personal claims.",
            ),
            Block("h1", "Part II — Final test submission"),
            Block("h2", "1. Test preparation and integrity"),
            Block(
                "p",
                "The final test is the 2,772-customer snapshot at cutoff 2011-09-01 with a fully observed 90-day label window. Its prepared-file SHA-256 is 2830e4738acfee8c5561f5eb513874d0cacae32f3b3095c412db62dc2cf78ff6. Before access, the candidate manifest, preprocessing, sigmoid calibrator, artifact checksum and threshold were frozen. Post-test retuning is prohibited.",
            ),
            Block("h2", "2. Model application"),
            Block(
                "code",
                "bundle = joblib.load('artifacts/models/final_candidate.joblib')\nassert sha256_file(model_path) == EXPECTED_MODEL_SHA256\nscores = bundle['calibrated_model'].predict_proba(X_test)[:, 1]\npredicted = scores >= 0.812509305136\n# target, feature and split versions are checked before reporting",
            ),
            Block("h2", "3. Final test metrics"),
            Block(
                "table",
                (
                    ["Measure", "Final test result", "95% bootstrap interval"],
                    [
                        [
                            "Rows / prevalence",
                            f"{final['rows']:,} / {final['prevalence']:.6f}",
                            "Not applicable",
                        ],
                        ["PR-AUC", f"{test['pr_auc']:.6f}", "[0.618131, 0.678937]"],
                        ["ROC-AUC", f"{test['roc_auc']:.6f}", "[0.748534, 0.782761]"],
                        ["Brier score", f"{test['brier']:.6f}", "[0.192598, 0.207125]"],
                        ["Log loss", f"{test['log_loss']:.6f}", "Not bootstrapped"],
                        ["ECE (10 bins)", f"{test['ece_10']:.6f}", "Not bootstrapped"],
                        [
                            "Top-10% precision / recall / lift",
                            f"{test['precision_at_10']:.6f} / {test['recall_at_10']:.6f} / {test['lift_at_10']:.6f}",
                            "Not bootstrapped",
                        ],
                    ],
                    [2600, 3800, 2960],
                ),
                note="Evidence class: project-executed, untouched temporal holdout. Intervals are nonparametric row bootstrap intervals for this cutoff.",
            ),
            Block(
                "figure",
                (
                    "artifacts/ml/final_evaluation.png",
                    "Figure 2. Final temporal-test precision–recall and probability calibration.",
                    6.3,
                ),
            ),
            Block("h2", "4. Frozen-threshold confusion matrix"),
            Block(
                "table",
                (
                    ["Actual / predicted", "Predicted active", "Predicted inactive"],
                    [
                        ["Actual active", "TN = 1,603", "FP = 80"],
                        ["Actual inactive", "FN = 867", "TP = 222"],
                    ],
                    [3200, 3080, 3080],
                ),
                note="Threshold 0.812509305136 selected 302 customers (10.8947%): precision 0.735099, recall 0.203857, F1 0.319195.",
            ),
            Block("h2", "5. Validation-to-test comparison"),
            Block(
                "table",
                (
                    ["Split", "PR-AUC", "ROC-AUC", "Brier", "Prevalence", "Interpretation"],
                    [
                        [
                            "Validation",
                            f"{val['pr_auc']:.6f}",
                            f"{val['roc_auc']:.6f}",
                            f"{val['brier']:.6f}",
                            f"{val['prevalence']:.6f}",
                            "Used for family/tuning selection",
                        ],
                        [
                            "Calibration",
                            f"{cal['pr_auc']:.6f}",
                            f"{cal['roc_auc']:.6f}",
                            f"{cal['brier']:.6f}",
                            f"{cal['prevalence']:.6f}",
                            "Used for sigmoid and threshold; descriptive",
                        ],
                        [
                            "Final test",
                            f"{test['pr_auc']:.6f}",
                            f"{test['roc_auc']:.6f}",
                            f"{test['brier']:.6f}",
                            f"{test['prevalence']:.6f}",
                            "Single untouched temporal holdout",
                        ],
                    ],
                    [1500, 1200, 1200, 1200, 1300, 2960],
                ),
            ),
            Block(
                "p",
                "PR-AUC falls from validation 0.812223 to test 0.647525 while prevalence also falls from 0.577187 to 0.392857. ROC-AUC remains 0.765878 and top-10% lift rises to 1.904513. The gap is evidence of temporal/data shift and uncertainty, not a reason to revise the frozen test result.",
            ),
            Block("h2", "6. Deployment truth"),
            Block(
                "p",
                "The artifact is registered locally as growthpilot-churn-inactivity version 1 with alias champion and is integrated into tenant-scoped on-demand and durable batch-scoring services. “Champion” is a local registry alias, not proof of production deployment. On-demand scoring is demo-gated; live cloud, tenant-data drift and service-level performance are unvalidated. Every score remains non-authorizing.",
            ),
            Block("h2", "7. Conclusion"),
            Block(
                "p",
                "The frozen model provides useful ranking signal on the historical temporal test, especially within limited outreach capacity, but misses most inactive customers at the strict threshold. It should support review, not replace human judgment. Production adoption requires current tenant data, lawful use, monitored calibration/drift and a causal campaign evaluation.",
            ),
            Block("h1", "References and evidence"),
            Block(
                "p",
                "scikit-learn developers. Probability calibration and model evaluation documentation. https://scikit-learn.org/stable/modules/calibration.html",
            ),
            Block(
                "p",
                "Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. NeurIPS 30. https://arxiv.org/abs/1705.07874",
            ),
            Block(
                "p",
                "Project evidence: artifacts/ml/final_candidate.json, final_evaluation.json/png, explanations.json/png, model_registry.json; scripts/refine_model.py, evaluate_final.py, explain_model.py and register_model.py.",
            ),
        ],
    )


def weekly_report() -> None:
    doc = Document()
    configure_document(doc)
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.header_distance = Inches(0.25)
    section.footer_distance = Inches(0.25)
    set_header_footer(doc, "Weekly Progress Report")
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    set_run_font(p.add_run("SHORT WEEKLY PROGRESS REPORT"), size=18, color=INK, bold=True)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    set_run_font(
        p.add_run("Samsung Innovation Campus · Group 7 · GrowthPilot AI"),
        size=10.5,
        color=MUTED,
        bold=True,
    )
    add_table(
        doc,
        ["Date", "Reporter", "Overall status"],
        [
            [
                "9 September 2026",
                "Şahin Başcı",
                "GREEN — local scope complete; external validation open",
            ]
        ],
        [2500, 2500, 4360],
    )
    entries = [
        (
            "1. Progress since the previous report",
            "Completed the production-oriented local application, temporal churn-proxy data/ML pipeline, frozen final evaluation, model registry/inference, integrations, attribution, audiences/campaign approval, security boundaries and all academic submission artifacts. No fabricated business result or live provider result is included.",
        ),
        (
            "2. Current focus",
            "Final audit: rendered document/slide QA, clean full test suite, dependency/secret scans, evidence mapping and Phase 22–24 readiness documentation.",
        ),
        (
            "3. Status and evidence",
            "Green for authorized local delivery. Backend: 83 tests passing before final package audit; frontend typecheck/lint/Vitest/webpack build passing. Final test: PR-AUC 0.647525, ROC-AUC 0.765878, Brier 0.199854; model SHA-256 942d705d…52ad.",
        ),
        (
            "4. Problems and risks",
            "No live Meta, Google Ads, LLM, OIDC or cloud credentials; automated desktop/mobile Chromium and Axe checks pass, but manual multi-browser and assistive-technology review is outstanding; production backup/restore and load tests were not performed. Dataset is historical, single-retailer, UK-based; inactivity is a proxy, not contractual churn; predictive results are noncausal.",
        ),
        (
            "5. Support or decision needed",
            "Project Lead should audit deliverables and decide whether to authorize final squash/publication. Founder must provide sandbox credentials and approve any deployment or real campaign. Submission dates in instructor files have elapsed and require instructor confirmation.",
        ),
        (
            "6. Tasks before next report",
            "Address audit findings; run credentialed sandbox and manual browser/assistive-technology validation; rehearse backup/restore; define pilot eligibility and randomized holdout; only then request separate deployment/publication authorization.",
        ),
    ]
    for title, body in entries:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(1)
        set_run_font(p.add_run(title), size=10.2, color=GREEN, bold=True)
        p = doc.add_paragraph(body)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.0
        for run in p.runs:
            set_run_font(run, size=8.9, color="000000")
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(0)
    shade_paragraph(p, GREEN_LIGHT)
    set_run_font(
        p.add_run(
            "AI disclosure: drafted with OpenAI Codex/ChatGPT assistance and verified against repository evidence; human review required."
        ),
        size=8.2,
        color=INK,
        bold=True,
    )
    stem = "05_Weekly_Progress_Report_2026-09-09"
    doc.core_properties.title = "GrowthPilot AI Weekly Progress Report — 2026-09-09"
    doc.core_properties.author = "Şahin Başcı; AI-assisted drafting disclosed"
    doc.save(OUT / f"{stem}.docx")
    md = "# Short Weekly Progress Report\n\n**Team:** Group 7\n**Project:** GrowthPilot AI\n**Date:** 9 September 2026\n**Reporter:** Şahin Başcı\n**Status:** GREEN — local scope complete; external validation open\n\n"
    for title, body in entries:
        md += f"## {title}\n\n{body}\n\n"
    md += "**AI disclosure:** drafted with OpenAI Codex/ChatGPT assistance and verified against repository evidence; human review required.\n"
    (OUT / f"{stem}.md").write_text(md, encoding="utf-8")


def render_pdfs() -> None:
    soffice = shutil.which("soffice")
    if soffice is None:
        raise RuntimeError("LibreOffice 'soffice' is required to regenerate submission PDFs")
    with tempfile.TemporaryDirectory(prefix="growthpilot_lo_") as profile:
        profile_uri = Path(profile).as_uri()
        for docx_path in sorted(OUT.glob("*.docx")):
            subprocess.run(
                [
                    soffice,
                    f"-env:UserInstallation={profile_uri}",
                    "--headless",
                    "--norestore",
                    "--convert-to",
                    "pdf:writer_pdf_Export",
                    "--outdir",
                    str(OUT),
                    str(docx_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            pdf_path = docx_path.with_suffix(".pdf")
            if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
                raise RuntimeError(f"LibreOffice did not produce {pdf_path}")


def sync_assignment_package() -> None:
    mapping = {
        "01_Literature_Data_Technology_Submission": (
            "01_Literatur_Veri_Teknoloji",
            "Odev_01_Literatur_Veri_Teknoloji",
        ),
        "02_Concept_Note_and_Implementation_Plan": (
            "02_Kavram_Notu_Uygulama_Plani",
            "Odev_02_Kavram_Notu_Uygulama_Plani",
        ),
        "03_Data_Preparation_Feature_Engineering_Model_Exploration": (
            "03_Veri_Hazirlama_Ozellik_Muhendisligi_Model_Kesfi",
            "Odev_03_Veri_Hazirlama_Ozellik_Muhendisligi_Model_Kesfi",
        ),
        "04_Model_Refinement_and_Test_Submission": (
            "04_Model_Iyilestirme_ve_Test",
            "Odev_04_Model_Iyilestirme_ve_Test",
        ),
        "05_Weekly_Progress_Report_2026-09-09": (
            "05_Haftalik_Ilerleme_Raporu",
            "Odev_05_Haftalik_Ilerleme_Raporu",
        ),
    }
    for source_stem, (directory, destination_stem) in mapping.items():
        destination = ASSIGNMENTS / directory
        destination.mkdir(parents=True, exist_ok=True)
        for suffix in (".docx", ".pdf"):
            shutil.copy2(
                OUT / f"{source_stem}{suffix}", destination / f"{destination_stem}{suffix}"
            )
    presentation_source = ROOT / "academic" / "presentation"
    presentation_destination = ASSIGNMENTS / "06_Final_Sunumu"
    presentation_destination.mkdir(parents=True, exist_ok=True)
    for suffix in (".pptx", ".pdf"):
        source_filename = f"GrowthPilot_AI_Final_Presentation{suffix}"
        destination_filename = f"Odev_06_GrowthPilot_Final_Sunumu{suffix}"
        shutil.copy2(
            presentation_source / source_filename,
            presentation_destination / destination_filename,
        )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    profile = load_json(REPORTS / "dataset_profile.json")
    prep = load_json(REPORTS / "data_preparation.json")
    exploration = load_json(ML / "model_exploration.json")
    candidate = load_json(ML / "final_candidate.json")
    final = load_json(ML / "final_evaluation.json")
    for submission in (
        literature_submission(profile),
        concept_submission(),
        data_model_submission(prep, exploration),
        refinement_submission(candidate, final),
    ):
        build_submission(submission)
    weekly_report()
    render_pdfs()
    sync_assignment_package()
    print(
        f"Generated 5 academic DOCX/Markdown/PDF sets in {OUT} and synchronized "
        f"all written and presentation deliverables in {ASSIGNMENTS}"
    )


if __name__ == "__main__":
    main()
