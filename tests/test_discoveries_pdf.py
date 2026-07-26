"""Tests for the data-discoveries PDF generator and its wiring.

`docs/bootcamp_data_discoveries.md` + `.pdf` are the payoff for every preceding
module, and they used to exist only if the bootcamper opted into the Discover
tutorial. `generate_discoveries_pdf.py` is the sibling renderer that produces the
PDF; these tests pin both halves of the fix:

* The renderer honors the same two-outcome contract as the recap generator
  (INV-110): an imperfect document renders, a document it cannot meaningfully
  parse does not — no PDF, no success line, non-zero exit. Pointing it at a
  recap-shaped document is the concrete case that motivated it.
* The stdlib fallback produces a genuinely valid PDF carrying the findings. The
  reporting bootcamper had no PDF dependency installed at all, so that path is
  the common case, not an edge case — and a `PDF generated:` line is not
  evidence, so the text is extracted and searched.
* The module skill produces the deliverable on every branch of the Discover
  opt-in, at the convergence point all four branches return to.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zlib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")
SCRIPT = os.path.join(PLUGIN, "scripts", "generate_discoveries_pdf.py")
MODULE7 = os.path.join(PLUGIN, "skills", "module-07-query-visualize-discover")
PHASE1 = os.path.join(MODULE7, "phase1-query-visualize.md")
PHASE2 = os.path.join(MODULE7, "phase2-discover.md")

SUCCESS_LINE = "PDF generated:"

GOOD_DOC = """# Data Discoveries

**Bootcamper:** Ada Lovelace
**Sources:** ENFORMION, EQUIFAX

## Headline numbers, interpreted

- **Records loaded:** 4,012 across two sources, which is the full mapped set
- **Resolved entities:** 3,864 — a 3.7% collapse, modest and expected at this overlap

## Merges and match keys

Every merge below carries the match key that drove it, so each one is auditable.

| Entity | Match key | Sources |
|---|---|---|
| 1042 | +NAME+ADDRESS | ENFORMION, EQUIFAX |

## Review queue

Cross-source pairs awaiting one human decision each before they can be actioned.

- **Entity 2210 / 8891:** POSSIBLY_SAME on +NAME-REGISTRATION_DATE

## Why and how: worked examples

### A near miss worth reading

Entity 3301 did not merge with 3302 because the two addresses disagreed outright.

## Relationship networks

Multi-hop paths that no single record states on its own were found here.

## What was not found, and why

The two sources shared only 8 organization names, so 4 cross-source merges was
near the achievable ceiling. This is low overlap in the source data, not pipeline
underperformance, and the measurement above is what distinguishes the two.
"""

# A recap-shaped document: the concrete input that produced a near-empty PDF and
# exit 0 before this renderer existed.
RECAP_SHAPED = """# Senzing Bootcamp Recap

**Bootcamper:** Ada Lovelace

## Data collection — 2026-07-21T09:00:00-05:00

### Information Shared

We talked through where the records were going to come from originally.

### Actions Taken

Collected two source extracts and registered them in the data source registry.
"""

NO_HEADINGS = "just some prose about the data\nand a second line of prose\n"

PARTIAL_DOC = """# Data Discoveries

## Headline numbers, interpreted

- Loaded 10 records and resolved 9 of them into distinct resolved entities today

## What was not found, and why

Low overlap between the two sources explains the small cross-source merge count.
"""


def run(args, cwd):
    return subprocess.run(
        [sys.executable, SCRIPT] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def write_doc(directory, text, name="bootcamp_data_discoveries.md"):
    docs = os.path.join(directory, "docs")
    os.makedirs(docs, exist_ok=True)
    path = os.path.join(docs, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def pdf_text(path):
    """Extract drawn text from a PDF, decompressing streams when needed.

    fpdf2 compresses its content streams, so a raw byte search reports a false
    negative — the mistake this helper exists to prevent.
    """
    with open(path, "rb") as handle:
        raw = handle.read()
    chunks = []
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", raw, re.S):
        body = match.group(1)
        try:
            body = zlib.decompress(body)
        except zlib.error:
            pass
        chunks.append(body.decode("latin-1", "replace"))
    joined = "\n".join(chunks)
    return "".join(re.findall(r"\((.*?)\)\s*Tj", joined))


class TestRendersASoundDocument(unittest.TestCase):
    def test_renders_and_reports_retention(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_doc(tmp, GOOD_DOC)
            result = run([], tmp)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn(SUCCESS_LINE, result.stdout)
            self.assertIn("content retained:", result.stdout)
            self.assertTrue(
                os.path.exists(os.path.join(tmp, "docs", "bootcamp_data_discoveries.pdf"))
            )

    def test_check_mode_passes_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_doc(tmp, GOOD_DOC)
            result = run(["--check"], tmp)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("6/6 findings sections present", result.stdout)
            self.assertFalse(
                os.path.exists(os.path.join(tmp, "docs", "bootcamp_data_discoveries.pdf")),
                "--check must not write a PDF.",
            )

    def test_pdf_carries_the_findings(self):
        """A success line is not verification; the text must be in the PDF."""
        with tempfile.TemporaryDirectory() as tmp:
            write_doc(tmp, GOOD_DOC)
            run([], tmp)
            text = pdf_text(os.path.join(tmp, "docs", "bootcamp_data_discoveries.pdf"))
            for probe in (
                "Data Discoveries",
                "Headline numbers",
                "Review queue",
                "POSSIBLY_SAME",
                "achievable ceiling",
                "Relationship networks",
            ):
                with self.subTest(probe=probe):
                    self.assertIn(probe, text)


class TestRefusesToShipAnEmptyDeliverable(unittest.TestCase):
    """INV-110: no success line and no file when content would be lost."""

    def assert_refused(self, tmp, doc_name="bootcamp_data_discoveries.md"):
        out_pdf = os.path.join(tmp, "docs", "out.pdf")
        result = run(
            ["--input", os.path.join("docs", doc_name), "--output", os.path.join("docs", "out.pdf")],
            tmp,
        )
        self.assertNotEqual(0, result.returncode, "must exit non-zero")
        self.assertNotIn(SUCCESS_LINE, result.stdout, "must print no success line")
        self.assertFalse(os.path.exists(out_pdf), "must write no PDF")
        return result

    def test_recap_shaped_document_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_doc(tmp, RECAP_SHAPED)
            result = self.assert_refused(tmp)
            self.assertIn("required findings sections", result.stderr)

    def test_document_without_headings_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_doc(tmp, NO_HEADINGS)
            result = self.assert_refused(tmp)
            self.assertIn("no '## ' sections", result.stderr)

    def test_missing_input_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "docs"), exist_ok=True)
            result = run([], tmp)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Input not found", result.stderr)


class TestPartialDocumentStillRenders(unittest.TestCase):
    """Incomplete but recognisable: warn, render, exit 0 — never block."""

    def test_warns_and_renders(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_doc(tmp, PARTIAL_DOC)
            result = run([], tmp)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn(SUCCESS_LINE, result.stdout)
            self.assertIn("missing findings sections", result.stderr)


class TestStdlibFallback(unittest.TestCase):
    """No optional PDF dependency installed is the common case, not an edge one."""

    def load_module(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("discoveries_gen", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        # Register before exec: @dataclass resolves its module via sys.modules.
        sys.modules["discoveries_gen"] = module
        spec.loader.exec_module(module)
        return module

    def test_stdlib_renderer_writes_a_valid_pdf_with_content(self):
        from pathlib import Path

        module = self.load_module()
        doc = module.parse_discoveries(GOOD_DOC)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "stdlib.pdf"
            self.assertTrue(module.render_with_stdlib(doc, out))
            with open(out, "rb") as handle:
                raw = handle.read()
            self.assertTrue(raw.startswith(b"%PDF-"), "must be a valid PDF")
            self.assertIn(b"%%EOF", raw)
            text = pdf_text(out)
            self.assertIn("Headline numbers", text)
            self.assertIn("POSSIBLY_SAME", text)

    def test_audit_accepts_the_good_document(self):
        module = self.load_module()
        doc = module.parse_discoveries(GOOD_DOC)
        audit = module.audit_discoveries(doc, GOOD_DOC)
        self.assertTrue(audit.ok, audit.fatal)
        self.assertEqual([], audit.missing_sections)
        self.assertGreater(audit.retention, module.MIN_CONTENT_RETENTION)


class TestModuleWiring(unittest.TestCase):
    """The deliverable must be produced on every branch of the Discover opt-in."""

    def read(self, path):
        with open(path, encoding="utf-8") as handle:
            return handle.read()

    def test_gate_produces_the_deliverable(self):
        text = self.read(PHASE1)
        self.assertIn("docs/bootcamp_data_discoveries.md", text)
        self.assertIn("generate_discoveries_pdf.py", text)

    def test_all_six_sections_are_specified(self):
        text = self.read(PHASE1)
        for section in (
            "Headline numbers",
            "Merges and match keys",
            "Review queue",
            "Why and how",
            "Relationship networks",
            "What was not found",
        ):
            with self.subTest(section=section):
                self.assertIn(section, text)

    def test_decline_branch_says_findings_are_not_skipped(self):
        text = self.read(PHASE2)
        self.assertIn("Declining skips the walkthrough, not the findings", text)

    def test_deliverable_is_non_blocking(self):
        text = self.read(PHASE1)
        self.assertIn("never blocks the gate below or graduation", text)

    def test_verification_is_required_not_just_a_success_line(self):
        text = self.read(PHASE1)
        self.assertIn("is not verification", text)

    def test_findings_come_through_mcp_not_sql(self):
        text = self.read(PHASE1)
        self.assertIn("never direct SQL", text)

    def test_recap_generator_is_not_reused_for_this_document(self):
        text = self.read(PHASE1)
        self.assertIn("do not point", text.lower())


if __name__ == "__main__":
    unittest.main()
