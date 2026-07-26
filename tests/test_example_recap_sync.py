"""Tests that the shipped example recap PDF matches its source Markdown.

INV-065 ships a sanitized reference pair inside the plugin:
``docs/examples/bootcamp_recap.example.md`` and its rendered ``.pdf``. The
invariant says the PDF must remain *regenerable* from the ``.md`` — but nothing
checked that the committed PDF still *matches* it, and the pair silently drifted
when the ``.md`` was edited without re-rendering. A stale reference artifact is
the kind of defect nobody notices, because the PDF still opens and still looks
right.

Two traps are pinned here:

1. **Staleness.** Distinctive strings from the current ``.md`` must appear in the
   PDF's extracted text. Editing the Markdown without re-rendering fails.
2. **Wrong regeneration directory.** The example references its screenshot as
   ``docs/examples/bootcamp_recap.example.truthset.png`` — a path relative to a
   bootcamp *project root*. The renderer resolves image paths against the current
   working directory, and INV-048 has it silently skip missing images, so
   regenerating from the repo root produces a valid PDF that quietly loses the
   screenshot (~105KB, 0 images) instead of the correct one (~122KB, 3 images).

   Regenerate from ``plugins/senzing-bootcamp/``:

       cd plugins/senzing-bootcamp
       python3 scripts/generate_recap_pdf.py \\
           --input docs/examples/bootcamp_recap.example.md \\
           --output docs/examples/bootcamp_recap.example.pdf

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest
import zlib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp", "docs", "examples")
EXAMPLE_MD = os.path.join(EXAMPLES, "bootcamp_recap.example.md")
EXAMPLE_PDF = os.path.join(EXAMPLES, "bootcamp_recap.example.pdf")
EXAMPLE_PNG = os.path.join(EXAMPLES, "bootcamp_recap.example.truthset.png")


def pdf_text(path):
    """Drawn text from a PDF, decompressing streams (fpdf2 compresses them).

    `(...)Tj` strings may contain escaped parens, so the capture skips `\\(`
    and `\\)`. Fragments are joined with a space because `multi_cell` wraps one
    source line into several `Tj` operators, and joining bare would weld the
    last word of one line onto the first of the next.
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
    fragments = re.findall(r"\(((?:\\.|[^()\\])*)\)\s*Tj", "\n".join(chunks))
    return " ".join(f.replace("\\(", "(").replace("\\)", ")") for f in fragments)


def squash(text):
    """Reduce to lowercase alphanumerics.

    Comparisons then survive PDF escaping, line wrapping, and whitespace
    differences — the three things that make raw substring matching on extracted
    PDF text unreliable.
    """
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def pdf_bytes():
    with open(EXAMPLE_PDF, "rb") as handle:
        return handle.read()


def normalize(text):
    """Fold the substitutions `_pdf_escape` makes, so comparisons are fair.

    Non-Latin-1 typography is approximated on the way into the PDF (en dash ->
    '-', curly quotes -> straight), so the Markdown side must be folded the same
    way before searching.
    """
    for src, dst in (
        ("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"'),
        ("–", "-"), ("—", "-"), ("•", "-"), ("…", "..."),
        ("→", "->"),
    ):
        text = text.replace(src, dst)
    return text


class TestExampleAssetsExist(unittest.TestCase):
    """INV-065: the sanitized reference pair ships inside the plugin."""

    def test_all_three_assets_present(self):
        for path in (EXAMPLE_MD, EXAMPLE_PDF, EXAMPLE_PNG):
            with self.subTest(path=os.path.basename(path)):
                self.assertTrue(os.path.exists(path), f"missing: {path}")

    def test_pdf_is_valid(self):
        raw = pdf_bytes()
        self.assertTrue(raw.startswith(b"%PDF-"))
        self.assertIn(b"%%EOF", raw)


class TestPdfEmbedsTheScreenshot(unittest.TestCase):
    """Guards against regenerating from the wrong working directory."""

    def test_screenshot_is_embedded(self):
        raw = pdf_bytes()
        images = raw.count(b"/Subtype /Image") + raw.count(b"/Subtype/Image")
        self.assertGreater(
            images,
            0,
            "The example PDF embeds no images. It was probably regenerated from "
            "the repo root: the example's image path resolves only from "
            "plugins/senzing-bootcamp/, and INV-048 silently skips missing "
            "images. See this module's docstring for the correct command.",
        )

    def test_markdown_references_the_screenshot(self):
        with open(EXAMPLE_MD, encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("bootcamp_recap.example.truthset.png", text)


class TestPdfMatchesItsSource(unittest.TestCase):
    """The committed PDF must not lag edits to the Markdown."""

    def setUp(self):
        with open(EXAMPLE_MD, encoding="utf-8") as handle:
            self.md = normalize(handle.read())
        self.pdf = pdf_text(EXAMPLE_PDF)

    def sampled_lines(self):
        """Distinctive prose lines from the recap's rendered subsections.

        Headings and bullets are rendered; blank lines, rules, meta lines and
        image tags are not. Long lines are sampled because short ones repeat.
        """
        keep = []
        for raw in self.md.splitlines():
            line = raw.strip()
            if not line or line.startswith(("#", "---", "!", "|", ">", "```")):
                continue
            if line.startswith("<!--"):
                continue  # maintainer notes: the renderer drops these by design
            line = re.sub(r"^[-*]\s+", "", line)
            line = line.replace("**", "").replace("`", "").strip()
            if len(line) >= 60 and " " in line:
                keep.append(line)
        return keep

    def test_source_lines_appear_in_the_pdf(self):
        lines = self.sampled_lines()
        self.assertGreater(len(lines), 20, "sampler found too little to compare")
        haystack = squash(self.pdf)
        # Compare a distinctive leading run of each line, squashed, so wrapping
        # and PDF escaping cannot produce a false failure.
        missing = [ln for ln in lines if squash(ln)[:50] not in haystack]
        self.assertEqual(
            [],
            missing[:5],
            f"{len(missing)} of {len(lines)} source lines are absent from the "
            "example PDF — it is stale relative to the Markdown. Re-render it "
            "(see this module's docstring for the command).",
        )

    def test_certificate_page_present(self):
        """INV-100: the recap ends with a Certificate of Completion page."""
        self.assertIn(squash("Certificate of Completion"), squash(self.pdf))


if __name__ == "__main__":
    unittest.main()
