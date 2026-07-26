#!/usr/bin/env python3
"""Render the data-discoveries Markdown into a PDF deliverable.

Reads ``docs/bootcamp_data_discoveries.md`` and writes
``docs/bootcamp_data_discoveries.pdf``.

This is the **sibling** of ``generate_recap_pdf.py``, not a replacement for it.
That script is deliberately recap-shaped: it keeps body text only when it sits
under one of four recognised ``### `` sub-headings, so aiming it at a
discoveries document produced a valid-but-nearly-empty PDF. Rather than
generalise a parser whose strictness is load-bearing for the recap, this script
renders a general Markdown subset and reuses the recap generator's low-level PDF
plumbing (page writer, wrapping, escaping) so there is exactly one hand-rolled
PDF writer in the plugin.

Supported Markdown: an H1 title, ``**Key:** value`` preamble meta lines, H2/H3
headings, ``-``/``*`` bullets at two indent levels, ``**Label:** text`` lines,
fenced code blocks (rendered verbatim), table rows (rendered as their source
text), and paragraphs. Everything content-bearing is rendered — that is the
point of the audit below.

A valid PDF is ALWAYS produced when the input is sound, via the same tiered
strategy as the recap generator:

1. ``fpdf2`` when importable — a designed cover plus flowing sections.
2. A stdlib-only writer when it is absent. The reporting bootcamper had none of
   ``pandoc``, ``wkhtmltopdf``, ``weasyprint``, ``reportlab`` or ``fpdf2``
   installed, so the fallback is the common case, not an edge case.

Per INV-110 the input is audited **before** rendering and two outcomes are
distinguished:

* **Incomplete but recognisable** (some required sections missing) — warn on
  stderr, render, exit 0. A partial findings document still has value.
* **Not a discoveries document, or catastrophic content loss** (no headings at
  all, none of the required sections present, or content retention below
  ``MIN_CONTENT_RETENTION``) — write the reason to stderr, print no
  ``PDF generated:`` line, write no PDF, and exit non-zero.

Success signal: on success it prints a line beginning ``PDF generated:`` and
exits 0. Any other outcome means no PDF was written.

Usage:
    python3 generate_discoveries_pdf.py [--input docs/bootcamp_data_discoveries.md]
                                        [--output docs/bootcamp_data_discoveries.pdf]
                                        [--check]

``--check`` audits without rendering and exits non-zero if the document would
not render usefully.

Copying this script elsewhere: it imports the shared PDF plumbing from
``generate_recap_pdf.py`` (expected next to this script) and the palette from
``brand_tokens.py``. Copy **all three** together; a lone copy either fails loudly
on the first import or falls back to the inlined palette, and says so on stderr
(INV-111).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

# The recap generator ships in this same directory. Reuse its PDF plumbing
# rather than carrying a second copy of a hand-rolled page writer.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from generate_recap_pdf import (  # noqa: E402
        _md_inline_to_text,
        _pdf_escape,
        _safe,
        _wrap,
        _write_pdf,
    )
except ImportError as exc:  # pragma: no cover - a broken install, not a data case
    sys.stderr.write(
        "Cannot import the shared PDF helpers from generate_recap_pdf.py "
        f"(expected next to this script): {exc}\n"
    )
    raise SystemExit(2)

try:
    import brand_tokens  # type: ignore

    EMBER = brand_tokens.hex_to_rgb(brand_tokens.EMBER_CORE)
    DARK_INK = brand_tokens.hex_to_rgb(brand_tokens.DARK_INK)
    BODY_INK = brand_tokens.hex_to_rgb(brand_tokens.BODY_INK)
    WARM_LINE = brand_tokens.hex_to_rgb(brand_tokens.WARM_LINE)
except ModuleNotFoundError:  # pragma: no cover - falls back to inlined brand values
    # INV-111: a degraded path is never inferred from silence. The inlined values are
    # kept equal to the tokens (tests/test_brand_sync.py asserts it), so nothing
    # renders wrong — but say which case occurred, because a project-local copy of
    # this script without brand_tokens.py beside it is easy to create by accident.
    sys.stderr.write(
        f"brand_tokens.py not importable from {Path(__file__).resolve().parent} "
        "(copy it next to this script); using the inlined brand palette.\n"
    )
    EMBER = (245, 120, 38)
    DARK_INK = (24, 22, 15)
    BODY_INK = (74, 70, 64)
    WARM_LINE = (229, 223, 211)
except Exception as exc:  # pragma: no cover - present but unusable
    sys.stderr.write(
        f"brand_tokens.py present but unusable ({exc}); using the inlined brand palette.\n"
    )
    EMBER = (245, 120, 38)
    DARK_INK = (24, 22, 15)
    BODY_INK = (74, 70, 64)
    WARM_LINE = (229, 223, 211)

DEFAULT_INPUT = "docs/bootcamp_data_discoveries.md"
DEFAULT_OUTPUT = "docs/bootcamp_data_discoveries.pdf"

# The findings a complete discoveries document carries. Matched case- and
# punctuation-insensitively against H2 headings, so a document may word them
# more naturally ("What Senzing did NOT find, and why") and still match.
REQUIRED_SECTIONS = [
    "headline numbers",
    "merges and match keys",
    "review queue",
    "why and how",
    "relationship networks",
    "what was not found",
]

# Minimum share of the input's content-bearing characters that must survive into
# the parsed document. This renderer keeps essentially everything that is not a
# blank line or a horizontal rule, so a sound document retains ~99%. A value far
# below that means the input is not what this script parses.
MIN_CONTENT_RETENTION = 0.60


@dataclass
class Block:
    """One renderable unit of the document."""

    kind: str  # h2 | h3 | bullet | subbullet | label | code | table | text
    text: str
    label: str = ""


@dataclass
class Discoveries:
    title: str = ""
    meta: List[Tuple[str, str]] = field(default_factory=list)
    blocks: List[Block] = field(default_factory=list)

    def headings(self) -> List[str]:
        return [b.text for b in self.blocks if b.kind in ("h2", "h3")]


# Vertical separation between consecutive list items, so a multi-line bullet cannot
# blend into the next one (its wrapped lines sit at the same spacing otherwise).
ITEM_GAP_MM = 2.4
ITEM_GAP_PT = 3.0

_LIST_KINDS = ("bullet", "subbullet")


def _needs_item_gap(blocks: List[Block], index: int) -> bool:
    """True when block ``index`` is a list item and the next block is one too.

    Gating on the *next* block keeps the gap strictly **between** items: it never
    trails the last item of a list, where the following heading/paragraph already
    brings its own spacing.
    """
    if blocks[index].kind not in _LIST_KINDS:
        return False
    nxt = blocks[index + 1] if index + 1 < len(blocks) else None
    return nxt is not None and nxt.kind in _LIST_KINDS


def _normalize(text: str) -> str:
    """Lowercase, strip Markdown emphasis and punctuation, collapse spaces."""
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def parse_discoveries(text: str) -> Discoveries:
    doc = Discoveries()
    in_code = False
    in_preamble = True
    paragraph: List[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            doc.blocks.append(Block("text", " ".join(paragraph).strip()))
            paragraph.clear()

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            in_code = not in_code
            continue
        if in_code:
            # Verbatim: match keys, JSON fragments and entity IDs live here.
            doc.blocks.append(Block("code", line))
            continue

        if not stripped or stripped == "---":
            flush_paragraph()
            continue

        if stripped.startswith("# ") and not doc.title:
            doc.title = stripped[2:].strip()
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            in_preamble = False
            doc.blocks.append(Block("h2", stripped[3:].strip()))
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            in_preamble = False
            doc.blocks.append(Block("h3", stripped[4:].strip()))
            continue

        # Preamble "**Key:** value" lines become document metadata.
        meta = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", stripped)
        if meta and in_preamble and not stripped.startswith(("-", "*")):
            doc.meta.append((meta.group(1).strip(), meta.group(2).strip()))
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            doc.blocks.append(Block("table", stripped))
            continue

        bullet = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if bullet:
            flush_paragraph()
            kind = "subbullet" if len(bullet.group(1)) >= 2 else "bullet"
            body = bullet.group(2).strip()
            lm = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", body)
            if lm:
                doc.blocks.append(Block(kind, lm.group(2).strip(), lm.group(1).strip()))
            else:
                doc.blocks.append(Block(kind, body))
            continue

        lm = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", stripped)
        if lm:
            flush_paragraph()
            doc.blocks.append(Block("label", lm.group(2).strip(), lm.group(1).strip()))
            continue

        paragraph.append(stripped)

    flush_paragraph()
    return doc


def _source_content_chars(text: str) -> int:
    """Content-bearing characters in the source, ignoring blanks and rules."""
    total = 0
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped == "---" or stripped.startswith("```"):
            continue
        total += len(stripped)
    return total


def _rendered_content_chars(doc: Discoveries) -> int:
    total = len(doc.title)
    for key, value in doc.meta:
        total += len(key) + len(value)
    for block in doc.blocks:
        total += len(block.text.strip()) + len(block.label)
    return total


@dataclass
class DiscoveriesAudit:
    ok: bool
    fatal: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    retention: float = 0.0
    missing_sections: List[str] = field(default_factory=list)


def audit_discoveries(doc: Discoveries, source: str) -> DiscoveriesAudit:
    """Decide whether this document can render as a useful deliverable.

    Mirrors the recap generator's two-outcome contract (INV-110): an imperfect
    document still renders; a document this script cannot meaningfully parse
    does not, because an empty deliverable is worse than none.
    """
    fatal: List[str] = []
    warnings: List[str] = []

    source_chars = _source_content_chars(source)
    rendered_chars = _rendered_content_chars(doc)
    retention = (rendered_chars / source_chars) if source_chars else 0.0

    normalized = [_normalize(h) for h in doc.headings()]
    missing = [
        required
        for required in REQUIRED_SECTIONS
        if not any(required in heading for heading in normalized)
    ]
    present = len(REQUIRED_SECTIONS) - len(missing)

    if not doc.blocks:
        fatal.append("the document has no content-bearing lines")
    elif not doc.headings():
        fatal.append("the document has no '## ' sections")
    elif present == 0:
        fatal.append(
            "none of the required findings sections is present "
            f"(looked for: {', '.join(REQUIRED_SECTIONS)})"
        )

    if source_chars and retention < MIN_CONTENT_RETENTION:
        fatal.append(
            f"content retention {retention:.0%} is below the "
            f"{MIN_CONTENT_RETENTION:.0%} minimum — most of the input would be dropped"
        )

    if missing and present:
        warnings.append(
            "missing findings sections: " + ", ".join(missing) + " — rendering anyway"
        )

    return DiscoveriesAudit(
        ok=not fatal,
        fatal=fatal,
        warnings=warnings,
        retention=retention,
        missing_sections=missing,
    )


def render_with_fpdf2(doc: Discoveries, output: Path) -> bool:
    try:
        from fpdf import FPDF  # type: ignore
    except ModuleNotFoundError:
        return False
    except Exception as exc:  # a broken install is worth reporting, not hiding
        sys.stderr.write(f"fpdf2 present but unusable ({exc}); using the stdlib renderer.\n")
        return False

    try:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.add_page()
        epw = pdf.w - pdf.l_margin - pdf.r_margin

        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(*DARK_INK)
        _full_width(pdf, epw, 10, _safe(doc.title or "Data Discoveries"))
        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(*EMBER)
        _full_width(pdf, epw, 7, "What Senzing found in your data")
        pdf.ln(2)

        pdf.set_text_color(*BODY_INK)
        pdf.set_font("Helvetica", "", 10.5)
        for key, value in doc.meta:
            _full_width(pdf, epw, 5.5, _safe(f"{key}: {_md_inline_to_text(value)}"))
        if doc.meta:
            pdf.ln(3)

        for index, block in enumerate(doc.blocks):
            _render_block_fpdf2(pdf, epw, block)
            if _needs_item_gap(doc.blocks, index):
                pdf.ln(ITEM_GAP_MM)

        _ensure_parent(output)
        pdf.output(str(output))
        return True
    except Exception as exc:
        sys.stderr.write(f"fpdf2 rendering failed ({exc}); using the stdlib renderer.\n")
        return False


def _full_width(pdf, width: float, height: float, text: str, indent: float = 0.0) -> None:
    """``multi_cell`` that always starts at the left margin (plus ``indent``).

    fpdf2's ``multi_cell`` defaults to ``new_x=RIGHT``, leaving the cursor at the
    right margin — measured at x = 200 mm on a 210 mm page after a full-width call.
    A following ``multi_cell(epw, ...)`` then draws from 200 mm across the full
    width: entirely off-sheet, rendering as blank space with no error raised and no
    effect on the content-retention figure, because the text *is* in the content
    stream — merely positioned outside the page box.

    Every full-width write goes through here so a new block kind cannot be added
    without inheriting the reset. Do NOT use this for text that must continue on the
    current line (a bullet's body after its prefix and bold label) — that path sets x
    itself.
    """
    pdf.set_x(pdf.l_margin + indent)
    pdf.multi_cell(width, height, text)


def _render_block_fpdf2(pdf, epw: float, block: Block) -> None:
    if block.kind == "h2":
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 15)
        pdf.set_text_color(*EMBER)
        _full_width(pdf, epw, 7.5, _safe(_md_inline_to_text(block.text)))
        pdf.set_draw_color(*WARM_LINE)
        y = pdf.get_y() + 1
        pdf.line(pdf.l_margin, y, pdf.l_margin + epw, y)
        pdf.ln(3)
        return
    if block.kind == "h3":
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*DARK_INK)
        _full_width(pdf, epw, 6, _safe(_md_inline_to_text(block.text)))
        pdf.ln(1)
        return

    pdf.set_text_color(*BODY_INK)
    if block.kind == "code":
        pdf.set_font("Courier", "", 9)
        _full_width(pdf, epw, 4.6, _safe(block.text) or " ")
        return
    if block.kind == "table":
        pdf.set_font("Courier", "", 8.5)
        _full_width(pdf, epw, 4.4, _safe(block.text))
        return

    indent = 0.0
    prefix = ""
    if block.kind == "bullet":
        indent, prefix = 6.0, "-  "
    elif block.kind == "subbullet":
        indent, prefix = 12.0, "-  "

    pdf.set_x(pdf.l_margin + indent)
    if prefix:
        pdf.set_font("Helvetica", "", 10.5)
        pdf.cell(6, 5.5, prefix)
    if block.label:
        pdf.set_font("Helvetica", "B", 10.5)
        label = _safe(block.label + ": ")
        pdf.cell(pdf.get_string_width(label) + 1, 5.5, label)
    pdf.set_font("Helvetica", "", 10.5)
    remaining = epw - (pdf.get_x() - pdf.l_margin)
    # A long bold label leaves a narrow column, and every wrapped line then stacks in
    # it beside a large empty gutter. A bare 20 mm floor is an order of magnitude too
    # low to catch that: ~60 mm of a 190 mm line clears it comfortably and still reads
    # as a ribbon. Break once the label has eaten half the width, continuing at a
    # modest hanging indent — short labels still render inline, which reads well.
    if remaining < max(20.0, epw * 0.5):
        indent = min(indent + 6.0, epw - 20.0)
        remaining = epw - indent
        pdf.ln(5.5)
        pdf.set_x(pdf.l_margin + indent)
    pdf.multi_cell(remaining, 5.5, _safe(_md_inline_to_text(block.text)) or " ")


def render_with_stdlib(doc: Discoveries, output: Path) -> bool:
    """Write a valid, paginated PDF using only the standard library."""
    try:
        page_w, page_h = 595.0, 842.0  # A4 in points
        margin = 54.0
        line_h = 14.0
        max_width_chars = 92

        tokens: List[Tuple[str, str, float, float]] = []

        def add(text: str, font: str = "F1", size: float = 10.5, indent: float = 0.0) -> None:
            tokens.append((text, font, size, indent))

        def add_wrapped(text: str, font: str, size: float, indent: float) -> None:
            width = max(20, max_width_chars - int(indent / 6))
            for chunk in _wrap(text, width):
                add(chunk, font, size, indent)

        def add_gap(points: float) -> None:
            """Advance by an exact number of points, below the line-height floor.

            An ordinary empty token still costs a full ``line_h``; an inter-item gap
            needs to be smaller than a line or it reads as a paragraph break.
            """
            tokens.append(("", "GAP", points, 0.0))

        add(doc.title or "Data Discoveries", "F2", 20, 0)
        add("What Senzing found in your data", "F1", 12, 0)
        add("", "F1", 6, 0)
        for key, value in doc.meta:
            add_wrapped(f"{key}: {_md_inline_to_text(value)}", "F1", 11, 0)
        if doc.meta:
            add("", "F1", 6, 0)

        for index, block in enumerate(doc.blocks):
            if block.kind == "h2":
                add("", "F1", 6, 0)
                add_wrapped(_md_inline_to_text(block.text), "F2", 14, 0)
                continue
            if block.kind == "h3":
                add("", "F1", 3, 0)
                add_wrapped(_md_inline_to_text(block.text), "F2", 11.5, 0)
                continue
            if block.kind in ("code", "table"):
                add(block.text[:max_width_chars], "F1", 9, 12)
                continue
            indent = 12.0 if block.kind == "bullet" else 24.0 if block.kind == "subbullet" else 0.0
            body = _md_inline_to_text(block.text)
            if block.label:
                body = f"{block.label}: {body}".rstrip(": ")
            if block.kind in ("bullet", "subbullet"):
                body = "- " + body
            add_wrapped(body, "F1", 10.5, indent)
            # Mirror the fpdf2 path's inter-item gap so the two renderers do not drift.
            if _needs_item_gap(doc.blocks, index):
                add_gap(ITEM_GAP_PT)

        pages: List[str] = []
        current: List[str] = []
        y = page_h - margin

        def flush_page() -> None:
            if current:
                pages.append("\n".join(current))
                current.clear()

        for text, font, size, indent in tokens:
            # A "GAP" token is pure vertical space; it never emits a font reference.
            advance = size if font == "GAP" else max(line_h, size + 3.5)
            if y < margin + advance:
                flush_page()
                y = page_h - margin
            if text:
                current.append(
                    f"BT /{font} {size} Tf {margin + indent} {y} Td "
                    f"({_pdf_escape(text)}) Tj ET"
                )
            y -= advance
        flush_page()

        if not pages:
            pages = [""]
        _ensure_parent(output)
        _write_pdf(output, pages, [(page_w, page_h)] * len(pages))
        return True
    except Exception as exc:
        sys.stderr.write(f"Stdlib PDF rendering failed: {exc}\n")
        return False


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="audit the input without rendering; non-zero exit if it would not render usefully",
    )
    args = parser.parse_args(argv)

    source_path = Path(args.input)
    if not source_path.exists():
        sys.stderr.write(f"Input not found: {source_path}\n")
        return 1
    source = source_path.read_text(encoding="utf-8")

    doc = parse_discoveries(source)
    audit = audit_discoveries(doc, source)

    for warning in audit.warnings:
        sys.stderr.write(f"Warning: {warning}\n")

    if not audit.ok:
        sys.stderr.write(
            f"Refusing to render {source_path}: " + "; ".join(audit.fatal) + "\n"
        )
        sys.stderr.write(
            "No PDF was written. Fix the document and re-run — an empty "
            "deliverable is worse than none.\n"
        )
        return 1

    if args.check:
        sys.stdout.write(
            f"OK: {source_path} would render "
            f"({audit.retention:.0%} of its content, "
            f"{len(REQUIRED_SECTIONS) - len(audit.missing_sections)}"
            f"/{len(REQUIRED_SECTIONS)} findings sections present).\n"
        )
        return 0

    output = Path(args.output)
    for renderer, name in ((render_with_fpdf2, "fpdf2"), (render_with_stdlib, "stdlib")):
        if renderer(doc, output):
            sys.stdout.write(
                f"PDF generated: {output} (renderer: {name}, "
                f"content retained: {audit.retention:.0%})\n"
            )
            return 0

    sys.stderr.write("Failed to generate a PDF by any strategy.\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
