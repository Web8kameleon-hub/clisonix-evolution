#!/usr/bin/env python3
"""Generate PDF exports for legal documentation under docs/legal/de.

Produces one PDF per source document and one combined bundle PDF.
Uses reportlab so the output works reliably on Windows.
"""
from __future__ import annotations

import argparse
import csv
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = REPO_ROOT / "docs" / "legal" / "de"
DEFAULT_OUTPUT_DIR = DEFAULT_SOURCE_DIR / "pdf"
DEFAULT_BUNDLE_NAME = "legal-pack-bundle.pdf"

SOURCE_EXTENSIONS = {".md", ".markdown", ".txt", ".csv"}
EXCLUDED_DIR_PREFIXES = {"pdf", "dpma-handoff-", "wipo-ready-"}


@dataclass(frozen=True)
class SourceDoc:
    path: Path
    kind: str


def iter_sources(source_dir: Path) -> List[SourceDoc]:
    docs: List[SourceDoc] = []

    for path in sorted(source_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        if path.suffix.lower() == ".pdf" or path.suffix.lower() == ".zip":
            continue
        docs.append(SourceDoc(path=path, kind=path.suffix.lower()))

    for child_dir in sorted(source_dir.iterdir()):
        if not child_dir.is_dir():
            continue
        if any(child_dir.name.startswith(prefix) for prefix in EXCLUDED_DIR_PREFIXES):
            continue
        if child_dir.name == "iso27001-stage1":
            for path in sorted(child_dir.iterdir()):
                if path.is_file() and path.suffix.lower() in SOURCE_EXTENSIONS and path.suffix.lower() not in {".pdf", ".zip"}:
                    docs.append(SourceDoc(path=path, kind=path.suffix.lower()))
        if child_dir.name.startswith("evidence-freeze-"):
            for path in sorted(child_dir.iterdir()):
                if path.is_file() and path.suffix.lower() in {".txt", ".json"}:
                    docs.append(SourceDoc(path=path, kind=path.suffix.lower()))
    return docs


def heading_level(line: str) -> int | None:
    match = re.match(r"^(#{1,6})\s+(.*)$", line)
    if not match:
        return None
    return len(match.group(1))


def escape_paragraph(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="LegalTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111111"),
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LegalSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#444444"),
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LegalH1",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#111111"),
            spaceBefore=10,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LegalH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LegalH3",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#374151"),
            spaceBefore=6,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LegalBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.black,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LegalBullet",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12.5,
            leftIndent=12,
            bulletIndent=0,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LegalCode",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=8.4,
            leading=10,
            textColor=colors.HexColor("#111827"),
            backColor=colors.HexColor("#f3f4f6"),
            borderPadding=6,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LegalSmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#555555"),
        )
    )
    return styles


def pdf_header(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(colors.HexColor("#111111"))
    canvas.drawString(doc.leftMargin, height - 1.2 * cm, "Clisonix Legal PDF Export")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawRightString(width - doc.rightMargin, height - 1.2 * cm, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def pdf_footer(canvas, doc):
    canvas.saveState()
    width, _ = A4
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(doc.leftMargin, 0.8 * cm, "Generated from repo sources for counsel review")
    canvas.drawRightString(width - doc.rightMargin, 0.8 * cm, "No legal advice")
    canvas.restoreState()


def paragraph_for_line(line: str, styles) -> Paragraph:
    if line.startswith("- ") or line.startswith("* "):
        return Paragraph(escape_paragraph(line[2:]), styles["LegalBullet"])
    if re.match(r"^\d+[.)]\s+", line):
        stripped = re.sub(r"^\d+[.)]\s+", "", line)
        return Paragraph(escape_paragraph(stripped), styles["LegalBody"])
    return Paragraph(escape_paragraph(line), styles["LegalBody"])


def markdown_to_flowables(text: str, styles) -> List:
    flowables: List = []
    in_code = False
    code_lines: List[str] = []

    def flush_code() -> None:
        nonlocal code_lines
        if code_lines:
            flowables.append(Preformatted("\n".join(code_lines), styles["LegalCode"]))
            code_lines = []

    lines = text.splitlines()
    for raw_line in lines:
        line = raw_line.rstrip("\n")
        if line.strip().startswith("```"):
            if in_code:
                in_code = False
                flush_code()
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_code()
            flowables.append(Spacer(1, 4))
            continue

        level = heading_level(line)
        if level:
            flush_code()
            title = re.sub(r"^#{1,6}\s+", "", line).strip()
            style_name = {1: "LegalH1", 2: "LegalH2", 3: "LegalH3"}.get(level, "LegalBody")
            flowables.append(Paragraph(escape_paragraph(title), styles[style_name]))
            continue

        if line.startswith("---"):
            flush_code()
            flowables.append(Spacer(1, 8))
            continue

        flowables.append(paragraph_for_line(line, styles))

    flush_code()
    return flowables


def csv_to_table(path: Path, styles) -> Table:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        rows = [["(empty)"]]
    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.2),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def build_document(source: SourceDoc, output_path: Path, title_prefix: str, include_cover: bool = True):
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.7 * cm,
        rightMargin=1.7 * cm,
        topMargin=2.0 * cm,
        bottomMargin=1.8 * cm,
        title=source.path.stem,
        author="Clisonix Cloud",
        subject="Legal document PDF export",
    )

    story: List = []
    if include_cover:
        story.append(Paragraph(escape_paragraph(f"{title_prefix}: {source.path.name}"), styles["LegalTitle"]))
        story.append(Paragraph(escape_paragraph(str(source.path.relative_to(REPO_ROOT))), styles["LegalSubtitle"]))
        story.append(Paragraph(escape_paragraph("Generated for legal review and attorney handoff"), styles["LegalSubtitle"]))
        story.append(Spacer(1, 14))

    if source.kind == ".csv":
        story.append(csv_to_table(source.path, styles))
    else:
        text = source.path.read_text(encoding="utf-8")
        story.extend(markdown_to_flowables(text, styles))

    doc.build(story, onFirstPage=pdf_header, onLaterPages=pdf_header)


def render_source_pdf(source: SourceDoc, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{source.path.stem}.pdf"
    build_document(source, output_path, "Legal Source PDF")
    return output_path


def render_bundle_pdf(sources: Iterable[SourceDoc], output_path: Path) -> Path:
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.7 * cm,
        rightMargin=1.7 * cm,
        topMargin=2.0 * cm,
        bottomMargin=1.8 * cm,
        title="Clisonix Legal Bundle",
        author="Clisonix Cloud",
        subject="Combined legal PDF bundle",
    )

    story: List = []
    story.append(Paragraph("Clisonix Legal PDF Bundle", styles["LegalTitle"]))
    story.append(Paragraph("Combined PDF for DPMA / WIPO / counsel handoff", styles["LegalSubtitle"]))
    story.append(Paragraph(f"Generated from {DEFAULT_SOURCE_DIR.relative_to(REPO_ROOT)}", styles["LegalSubtitle"]))
    story.append(Spacer(1, 14))

    first = True
    for source in sources:
        if not first:
            story.append(PageBreak())
        first = False

        rel = source.path.relative_to(REPO_ROOT)
        story.append(Paragraph(escape_paragraph(rel.as_posix()), styles["LegalH1"]))
        story.append(Paragraph(escape_paragraph("Source type: " + source.kind.lstrip(".")), styles["LegalSmall"]))
        story.append(Spacer(1, 6))

        if source.kind == ".csv":
            story.append(csv_to_table(source.path, styles))
        else:
            story.extend(markdown_to_flowables(source.path.read_text(encoding="utf-8"), styles))

    doc.build(story, onFirstPage=pdf_header, onLaterPages=pdf_header)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate PDF exports for docs/legal/de")
    parser.add_argument("--source-dir", default=str(DEFAULT_SOURCE_DIR), help="Directory containing legal source documents")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for per-file PDFs")
    parser.add_argument("--bundle-name", default=DEFAULT_BUNDLE_NAME, help="Name of the combined PDF bundle")
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)
    if not source_dir.exists():
        raise SystemExit(f"Source directory not found: {source_dir}")

    sources = iter_sources(source_dir)
    if not sources:
        raise SystemExit(f"No markdown/csv sources found under: {source_dir}")

    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: List[Path] = []

    for source in sources:
        pdf_path = render_source_pdf(source, output_dir)
        generated.append(pdf_path)
        print(f"generated: {pdf_path}")

    bundle_path = output_dir / args.bundle_name
    render_bundle_pdf(sources, bundle_path)
    generated.append(bundle_path)
    print(f"generated: {bundle_path}")
    print(f"total PDFs: {len(generated)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
