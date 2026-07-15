#!/usr/bin/env python3
"""Render the bootcamp recap Markdown into a professional PDF trophy.

Reads ``docs/bootcamp_recap.md`` and writes ``docs/bootcamp_recap.pdf``.

A valid PDF is ALWAYS produced, via a tiered strategy:

1. Rich renderer using ``fpdf2`` when it is importable: a designed cover page
   plus one section per completed module, each carrying its four labeled
   sub-sections (Information Shared, Questions & Responses, Actions Taken,
   Journal).
2. Stdlib-only fallback writer when ``fpdf2`` is absent: a plainer but valid,
   paginated PDF rendered from the same parsed content, with no third-party
   dependency.

The script is self-contained: it imports nothing from sibling scripts, so it
works when bundled inside the Claude plugin and invoked from a bootcamp
working directory.

Success signal (matches the graduation skill's contract): on success it prints
a line beginning ``PDF generated:`` and exits 0. Any other outcome means no PDF
was written.

Usage:
    python3 generate_recap_pdf.py [--input docs/bootcamp_recap.md]
                                  [--output docs/bootcamp_recap.pdf]
                                  [--check]

``--check`` verifies, without rendering, that every module section in the
recap carries the required labeled sub-sections and exits non-zero if any are
missing.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

DEFAULT_INPUT = "docs/bootcamp_recap.md"
DEFAULT_OUTPUT = "docs/bootcamp_recap.pdf"

# The labeled sub-sections a complete per-module recap section carries. The
# graduation "trophy" requirement names Information Shared, Questions &
# Responses, Actions Taken, and Journal. "Actions Taken" / "Action Taken" are
# both accepted on parse.
REQUIRED_SECTIONS = [
    "Information Shared",
    "Questions & Responses",
    "Actions Taken",
    "Journal",
]


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
@dataclass
class ModuleSection:
    """One ``## Module N: ...`` block from the recap."""

    number: Optional[int]
    title: str
    date: str = ""
    # Ordered (heading, [lines]) sub-sections under ### headings.
    subsections: List[Tuple[str, List[str]]] = field(default_factory=list)

    def subsection(self, name: str) -> Optional[List[str]]:
        target = _normalize_heading(name)
        for heading, lines in self.subsections:
            if _normalize_heading(heading) == target:
                return lines
        return None

    def missing_required(self) -> List[str]:
        present = {_normalize_heading(h) for h, _ in self.subsections}
        missing = []
        for req in REQUIRED_SECTIONS:
            if _normalize_heading(req) not in present:
                missing.append(req)
        return missing


@dataclass
class Recap:
    title: str
    meta: List[Tuple[str, str]]  # ("Bootcamper", "Ada"), ...
    modules: List[ModuleSection]


def _split_title_date(rest: str) -> Tuple[str, str]:
    """Split ``Name — 2026-07-15T10:05:00-05:00`` into (name, date).

    Splits on an em dash or hyphen separator only when the right side looks like
    a date/timestamp (begins with 4 digits). Otherwise the whole string is the
    title.
    """
    for sep in (" — ", " – ", " - "):
        if sep in rest:
            left, right = rest.rsplit(sep, 1)
            if re.match(r"^\d{4}\b", right.strip()):
                return left.strip(), right.strip()
    return rest.strip(), ""


def _normalize_heading(name: str) -> str:
    """Normalize a heading for tolerant comparison.

    ``Actions Taken`` and ``Action Taken`` compare equal; case and surrounding
    punctuation/whitespace are ignored.
    """
    n = name.strip().lower()
    n = n.rstrip(":").strip()
    n = re.sub(r"\s+", " ", n)
    if n == "action taken":
        n = "actions taken"
    return n


def parse_recap(text: str) -> Recap:
    lines = text.splitlines()

    title = "Senzing Bootcamp Recap"
    meta: List[Tuple[str, str]] = []
    modules: List[ModuleSection] = []

    current_module: Optional[ModuleSection] = None
    current_sub: Optional[Tuple[str, List[str]]] = None
    seen_first_module = False

    module_re = re.compile(r"^##\s+Module\s+(\d+)\s*[:\-—]?\s*(.*)$", re.IGNORECASE)
    generic_h2_re = re.compile(r"^##\s+(.*)$")
    h1_re = re.compile(r"^#\s+(.*)$")
    h3_re = re.compile(r"^###\s+(.*)$")
    meta_re = re.compile(r"^\*\*(.+?)\*\*:?\s*(.*)$")

    def close_sub() -> None:
        nonlocal current_sub
        if current_module is not None and current_sub is not None:
            current_module.subsections.append(current_sub)
        current_sub = None

    def close_module() -> None:
        nonlocal current_module
        close_sub()
        if current_module is not None:
            modules.append(current_module)
        current_module = None

    for raw in lines:
        line = raw.rstrip("\n")

        m = module_re.match(line)
        if m:
            close_module()
            num = int(m.group(1))
            rest = m.group(2).strip().lstrip(":-— ").strip()
            title, date = _split_title_date(rest)
            current_module = ModuleSection(
                number=num, title=title or f"Module {num}", date=date
            )
            seen_first_module = True
            continue

        if current_module is not None:
            hm = h3_re.match(line)
            if hm:
                close_sub()
                current_sub = (hm.group(1).strip(), [])
                continue
            # A new H2 that is not a module ends the module block.
            gm = generic_h2_re.match(line)
            if gm:
                close_module()
                continue
            if line.strip() == "---":
                # Separator between modules; keep it out of content.
                continue
            if current_sub is not None:
                current_sub[1].append(line)
            continue

        # Preamble (before the first module section).
        if not seen_first_module:
            hm = h1_re.match(line)
            if hm:
                title = hm.group(1).strip()
                continue
            mm = meta_re.match(line)
            if mm:
                key = mm.group(1).strip().rstrip(":")
                val = mm.group(2).strip()
                if val:
                    meta.append((key, val))
                continue

    close_module()

    # Trim trailing blank lines inside each sub-section.
    for mod in modules:
        for _, content in mod.subsections:
            while content and not content[-1].strip():
                content.pop()
            while content and not content[0].strip():
                content.pop(0)

    return Recap(title=title, meta=meta, modules=modules)


# --------------------------------------------------------------------------- #
# Verification (--check and post-render round trip)
# --------------------------------------------------------------------------- #
def verify_recap(recap: Recap) -> List[str]:
    """Return a list of human-readable problems; empty means complete."""
    problems: List[str] = []
    if not recap.modules:
        problems.append("recap contains no '## Module N:' sections")
    for mod in recap.modules:
        missing = mod.missing_required()
        if missing:
            label = f"Module {mod.number}" if mod.number else mod.title
            problems.append(f"{label} is missing: {', '.join(missing)}")
    return problems


# --------------------------------------------------------------------------- #
# Rich renderer (fpdf2)
# --------------------------------------------------------------------------- #
# Senzing-flavored palette (deep blue + slate + a warm accent).
NAVY = (12, 35, 64)
BLUE = (23, 92, 168)
SLATE = (71, 85, 105)
LIGHT = (241, 245, 249)
ACCENT = (200, 146, 42)
INK = (30, 41, 59)


def _md_inline_to_text(s: str) -> str:
    """Strip the small subset of inline Markdown we emit, for plain text."""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    return s


# fpdf2's core fonts (Helvetica) only cover Latin-1 (ISO-8859-1). Map the
# common typographic characters the recap may contain to ASCII, then drop any
# remaining out-of-range character, so the rich renderer never raises.
_UNICODE_MAP = {
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "–": "-",
    "—": "-",
    "•": "-",
    "…": "...",
    "→": "->",
    "✅": "[done]",
    "✓": "[x]",
    "⛔": "",
    "\U0001f6d1": "",
    "\U0001f393": "",
    "\U0001f680": "",
    "\U0001f4c4": "",
    "\U0001f3c6": "",
}


def _safe(s: str) -> str:
    """Return a string safe for fpdf2's Latin-1 core fonts."""
    for uni, rep in _UNICODE_MAP.items():
        s = s.replace(uni, rep)
    return s.encode("latin-1", "replace").decode("latin-1")


def render_with_fpdf2(recap: Recap, output: Path) -> bool:
    try:
        from fpdf import FPDF  # type: ignore
    except Exception:
        return False

    try:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=18)
        epw = pdf.w - pdf.l_margin - pdf.r_margin  # effective page width

        def text_color(rgb: Tuple[int, int, int]) -> None:
            pdf.set_text_color(*rgb)

        def fill_color(rgb: Tuple[int, int, int]) -> None:
            pdf.set_fill_color(*rgb)

        # ---- Cover page -------------------------------------------------- #
        pdf.add_page()
        fill_color(NAVY)
        pdf.rect(0, 0, pdf.w, 78, style="F")
        fill_color(ACCENT)
        pdf.rect(0, 78, pdf.w, 3, style="F")

        pdf.set_xy(pdf.l_margin, 26)
        text_color((255, 255, 255))
        pdf.set_font("Helvetica", "B", 30)
        pdf.cell(epw, 14, "Senzing Bootcamp", align="C")
        pdf.set_xy(pdf.l_margin, 44)
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(epw, 12, "Completion Recap", align="C")

        pdf.set_xy(pdf.l_margin, 96)
        text_color(INK)
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(
            epw,
            7,
            "A record of everything you built and learned, module by module. "
            "Keep it, revisit it, and share it with your team.",
            align="C",
        )

        # Metadata card.
        pdf.ln(8)
        card_x = pdf.l_margin + 18
        card_w = epw - 36
        y0 = pdf.get_y()
        rows = recap.meta or [("Bootcamper", "Bootcamper")]
        card_h = 12 + len(rows) * 9 + 6
        fill_color(LIGHT)
        pdf.set_draw_color(210, 218, 228)
        pdf.rect(card_x, y0, card_w, card_h, style="DF")
        pdf.set_xy(card_x + 8, y0 + 6)
        text_color(NAVY)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(card_w - 16, 8, "Bootcamp Summary")
        pdf.ln(11)
        for key, val in rows:
            pdf.set_x(card_x + 8)
            text_color(SLATE)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(48, 8, _safe(f"{key}:"))
            text_color(INK)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(card_w - 16 - 48, 8, _safe(_md_inline_to_text(val)))

        # Modules-completed line.
        pdf.set_xy(card_x + 8, y0 + card_h + 8)
        text_color(SLATE)
        pdf.set_font("Helvetica", "", 11)
        completed = ", ".join(
            f"Module {m.number}" for m in recap.modules if m.number is not None
        )
        if completed:
            pdf.multi_cell(card_w - 16, 7, _safe(f"Modules completed: {completed}"))

        # Footer accent.
        pdf.set_y(-24)
        text_color(SLATE)
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(epw, 6, "Generated by the Senzing Bootcamp Claude plugin", align="C")

        # ---- Per-module pages ------------------------------------------- #
        for mod in recap.modules:
            pdf.add_page()
            # Module header band.
            fill_color(BLUE)
            pdf.rect(0, 0, pdf.w, 24, style="F")
            pdf.set_xy(pdf.l_margin, 6)
            text_color((255, 255, 255))
            pdf.set_font("Helvetica", "B", 16)
            heading = (
                f"Module {mod.number}: {mod.title}"
                if mod.number is not None
                else mod.title
            )
            pdf.cell(epw, 9, _clip(_safe(heading), 62))
            if mod.date:
                pdf.set_xy(pdf.l_margin, 15)
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(epw, 5, _safe(f"Completed {mod.date}"))
            pdf.ln(24)

            for name in REQUIRED_SECTIONS:
                content = mod.subsection(name)
                _render_subsection(pdf, epw, name, content)

            # Any extra sub-sections (e.g. Duration) after the required set.
            for heading, content in mod.subsections:
                if _normalize_heading(heading) not in {
                    _normalize_heading(r) for r in REQUIRED_SECTIONS
                }:
                    _render_subsection(pdf, epw, heading, content)

        _ensure_parent(output)
        pdf.output(str(output))
        return output.exists() and output.stat().st_size > 0
    except Exception as exc:  # pragma: no cover - defensive
        sys.stderr.write(f"fpdf2 render failed: {exc}\n")
        return False


def _render_subsection(pdf, epw, name: str, content: Optional[List[str]]) -> None:
    from_missing = content is None
    pdf.ln(1)
    pdf.set_text_color(*NAVY)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(epw, 8, _safe(name))
    pdf.ln(9)
    pdf.set_text_color(*INK)
    pdf.set_font("Helvetica", "", 10.5)
    if from_missing or not any(l.strip() for l in content):
        pdf.set_text_color(*SLATE)
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(epw, 6, "(not recorded)")
        pdf.ln(1)
        return
    for line in content:
        _render_line(pdf, epw, line)
    pdf.ln(2)


def _render_line(pdf, epw, line: str) -> None:
    stripped = line.strip()
    if not stripped:
        pdf.ln(3)
        return
    indent = 0
    bullet = ""
    m = re.match(r"^(\s*)([-*])\s+(.*)$", line)
    if m:
        lead = len(m.group(1))
        indent = 6 + (6 if lead >= 4 else 0)
        bullet = "·  "  # middle dot (Latin-1 safe)
        stripped = m.group(3).strip()
    # Bold "Key:" prefix (e.g. **Q:**, **What we did:**).
    bold_prefix = ""
    bm = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", stripped)
    if bm:
        bold_prefix = _safe(bm.group(1) + ": ")
        stripped = bm.group(2).strip()
    stripped = _safe(_md_inline_to_text(stripped))
    x = pdf.l_margin + indent
    pdf.set_x(x)
    if bullet:
        pdf.set_font("Helvetica", "", 10.5)
        pdf.cell(6, 5.5, bullet)
        x = pdf.get_x()
    if bold_prefix:
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.cell(pdf.get_string_width(bold_prefix) + 1, 5.5, bold_prefix)
    pdf.set_font("Helvetica", "", 10.5)
    remaining = epw - (pdf.get_x() - pdf.l_margin)
    if remaining < 20:
        remaining = epw - indent
        pdf.ln(5.5)
        pdf.set_x(pdf.l_margin + indent)
    pdf.multi_cell(remaining, 5.5, stripped if stripped else " ")


def _clip(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


# --------------------------------------------------------------------------- #
# Stdlib-only fallback renderer
# --------------------------------------------------------------------------- #
def render_with_stdlib(recap: Recap, output: Path) -> bool:
    """Write a valid, paginated PDF using only the standard library.

    Uses the built-in Helvetica/Helvetica-Bold fonts (no embedding needed) and
    a hand-rolled page/xref writer. Plainer than the fpdf2 output but a
    genuinely valid PDF carrying the same content.
    """
    try:
        page_w, page_h = 595.0, 842.0  # A4 in points
        margin = 54.0
        line_h = 14.0
        max_width_chars = 92  # conservative wrap for 10pt Helvetica

        # Build a flat list of (text, font, size, indent) render tokens.
        tokens: List[Tuple[str, str, float, float]] = []

        def add(text: str, font: str = "F1", size: float = 10.5, indent: float = 0.0) -> None:
            tokens.append((text, font, size, indent))

        def add_wrapped(text: str, font: str, size: float, indent: float) -> None:
            width = max(20, max_width_chars - int(indent / 6))
            for chunk in _wrap(text, width):
                add(chunk, font, size, indent)

        add(recap.title, "F2", 22, 0)
        add("Completion Recap", "F2", 14, 0)
        add("", "F1", 6, 0)
        for key, val in recap.meta:
            add_wrapped(f"{key}: {_md_inline_to_text(val)}", "F1", 11, 0)
        completed = ", ".join(
            f"Module {m.number}" for m in recap.modules if m.number is not None
        )
        if completed:
            add("", "F1", 4, 0)
            add_wrapped(f"Modules completed: {completed}", "F1", 11, 0)

        for mod in recap.modules:
            add("", "F1", 10, 0)
            heading = (
                f"Module {mod.number}: {mod.title}"
                if mod.number is not None
                else mod.title
            )
            add_wrapped(heading, "F2", 15, 0)
            for name in REQUIRED_SECTIONS:
                _stdlib_subsection(add, add_wrapped, name, mod.subsection(name))
            for h, content in mod.subsections:
                if _normalize_heading(h) not in {
                    _normalize_heading(r) for r in REQUIRED_SECTIONS
                }:
                    _stdlib_subsection(add, add_wrapped, h, content)

        # Paginate tokens into pages of content streams.
        pages: List[str] = []
        y = page_h - margin
        buf: List[str] = []

        def flush_page() -> None:
            if buf:
                pages.append("\n".join(buf))

        for text, font, size, indent in tokens:
            if y - line_h < margin:
                flush_page()
                buf = []
                y = page_h - margin
            esc = _pdf_escape(text)
            x = margin + indent
            buf.append(
                f"BT /{font} {size:.1f} Tf 1 0 0 1 {x:.1f} {y:.1f} Tm ({esc}) Tj ET"
            )
            y -= line_h if text else line_h * 0.6
        flush_page()
        if not pages:
            pages = [f"BT /F1 11 Tf 1 0 0 1 {margin} {page_h - margin} Tm (Bootcamp recap) Tj ET"]

        _ensure_parent(output)
        _write_pdf(output, pages, page_w, page_h)
        return output.exists() and output.stat().st_size > 0
    except Exception as exc:  # pragma: no cover - defensive
        sys.stderr.write(f"stdlib render failed: {exc}\n")
        return False


def _stdlib_subsection(add, add_wrapped, name: str, content: Optional[List[str]]) -> None:
    add("", "F1", 4, 0)
    add(name, "F2", 12, 0)
    if content is None or not any(l.strip() for l in content):
        add_wrapped("(not recorded)", "F1", 10, 6)
        return
    for line in content:
        s = line.strip()
        if not s:
            add("", "F1", 4, 0)
            continue
        indent = 6.0
        m = re.match(r"^(\s*)([-*])\s+(.*)$", line)
        if m:
            s = "- " + _md_inline_to_text(m.group(3).strip())
            indent = 12.0 if len(m.group(1)) >= 4 else 6.0
        else:
            s = _md_inline_to_text(s)
        add_wrapped(s, "F1", 10.5, indent)


def _wrap(text: str, width: int) -> List[str]:
    text = text.rstrip()
    if not text:
        return [""]
    words = text.split(" ")
    out: List[str] = []
    cur = ""
    for w in words:
        if len(w) > width:
            if cur:
                out.append(cur)
                cur = ""
            for i in range(0, len(w), width):
                out.append(w[i : i + width])
            continue
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= width:
            cur += " " + w
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def _pdf_escape(s: str) -> str:
    # PDF text within () strings: escape \, (, ) and drop non-Latin-1.
    out = []
    for ch in s:
        o = ord(ch)
        if ch in "\\()":
            out.append("\\" + ch)
        elif 32 <= o < 127:
            out.append(ch)
        elif 160 <= o <= 255:
            out.append("\\%03o" % o)
        else:
            # Approximate common typographic characters, else '?'.
            repl = {
                0x2018: "'",
                0x2019: "'",
                0x201C: '"',
                0x201D: '"',
                0x2013: "-",
                0x2014: "-",
                0x2022: "-",
                0x2026: "...",
                0x2192: "->",
            }.get(o, "?")
            out.append(repl)
    return "".join(out)


def _write_pdf(output: Path, pages: List[str], page_w: float, page_h: float) -> None:
    objects: List[bytes] = []

    def add_obj(body: bytes) -> int:
        objects.append(body)
        return len(objects)  # 1-based object number

    # Reserve: 1=Catalog, 2=Pages, fonts, then per-page (content, page).
    font_regular = add_obj(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    )
    font_bold = add_obj(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
    )

    page_obj_nums: List[int] = []
    # We need the Pages object number ahead of the page objects; compute it.
    pages_obj_num = len(objects) + 1  # next object we will create is Pages
    add_obj(b"__PAGES_PLACEHOLDER__")

    for stream in pages:
        data = stream.encode("latin-1", "replace")
        content_num = add_obj(
            b"<< /Length %d >>\nstream\n%s\nendstream" % (len(data), data)
        )
        page_num = add_obj(
            (
                "<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %.2f %.2f] "
                "/Resources << /Font << /F1 %d 0 R /F2 %d 0 R >> >> "
                "/Contents %d 0 R >>"
                % (pages_obj_num, page_w, page_h, font_regular, font_bold, content_num)
            ).encode("latin-1")
        )
        page_obj_nums.append(page_num)

    kids = " ".join(f"{n} 0 R" for n in page_obj_nums)
    objects[pages_obj_num - 1] = (
        "<< /Type /Pages /Count %d /Kids [%s] >>" % (len(page_obj_nums), kids)
    ).encode("latin-1")

    catalog_num = add_obj(
        ("<< /Type /Catalog /Pages %d 0 R >>" % pages_obj_num).encode("latin-1")
    )

    # Serialize with xref.
    out = bytearray()
    out += b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = [0] * (len(objects) + 1)
    for i, body in enumerate(objects, start=1):
        offsets[i] = len(out)
        out += ("%d 0 obj\n" % i).encode("latin-1")
        out += body if isinstance(body, bytes) else body.encode("latin-1")
        out += b"\nendobj\n"
    xref_pos = len(out)
    n = len(objects) + 1
    out += ("xref\n0 %d\n" % n).encode("latin-1")
    out += b"0000000000 65535 f \n"
    for i in range(1, n):
        out += ("%010d 00000 n \n" % offsets[i]).encode("latin-1")
    out += (
        "trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
        % (n, catalog_num, xref_pos)
    ).encode("latin-1")

    output.write_bytes(bytes(out))


# --------------------------------------------------------------------------- #
# Helpers + entry point
# --------------------------------------------------------------------------- #
def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify required sections exist; do not render.",
    )
    args = parser.parse_args(argv)

    inp = Path(args.input)
    if not inp.exists():
        sys.stderr.write(f"Recap not found: {inp}\n")
        return 1

    recap = parse_recap(inp.read_text(encoding="utf-8"))

    if args.check:
        problems = verify_recap(recap)
        if problems:
            for p in problems:
                sys.stderr.write(f"INCOMPLETE: {p}\n")
            return 1
        print("Recap complete: all module sections carry the required subsections.")
        return 0

    out = Path(args.output)
    used = "fpdf2"
    ok = render_with_fpdf2(recap, out)
    if not ok:
        used = "stdlib"
        ok = render_with_stdlib(recap, out)

    if ok:
        # Non-fatal content warning (never blocks; graduation is non-blocking).
        problems = verify_recap(recap)
        if problems:
            sys.stderr.write(
                "WARNING: recap PDF generated but some sections are incomplete:\n"
            )
            for p in problems:
                sys.stderr.write(f"  - {p}\n")
        print(f"PDF generated: {out} (renderer: {used})")
        return 0

    sys.stderr.write("Failed to generate a PDF by any strategy.\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
