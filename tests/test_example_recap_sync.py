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
2. **An image path that only resolves from one directory.** The example used to
   reference its screenshot as ``docs/examples/bootcamp_recap.example.truthset.png``
   — a path relative to a bootcamp *project root* — back when the renderer resolved
   against the current working directory. **INV-161 ended that**: paths now resolve
   against the recap document's own directory, so the reference is plainly
   ``bootcamp_recap.example.truthset.png`` (the PNG sits beside the ``.md``), which
   is also what a Markdown reader of the source needs. The invariant is explicit
   that *no step may require a ``cd`` to make assets resolve*, so there is no
   correct working directory to regenerate from any more — every directory is.

   The 2026-07-28 deep-dive audit caught the pair mid-transition: the resolver had
   been fixed, the example had not, and the committed PDF could no longer be
   reproduced from its own source (``embedded 0 of 1 images``, 4 image objects
   against 5). ``TestPdfRegeneratesFromItsSource`` below now renders freshly from an
   unrelated cwd, so a repeat cannot hide behind a PDF whose image was baked in by
   an earlier render.

   Regenerate from anywhere:

       python3 plugins/senzing-bootcamp/scripts/generate_recap_pdf.py \\
           --input plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md \\
           --output plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf

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
        # `decompressobj` decodes the valid prefix and tolerates a slice whose tail
        # is off by a few bytes; strict `decompress` raises on that, which silently
        # hid a whole page of text and looked exactly like a lost module section.
        try:
            body = zlib.decompressobj().decompress(body)
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
    """The committed PDF must actually carry the screenshot."""

    # The cover logo and the certificate art always embed, because they resolve
    # relative to the *script*. So "any image at all" cannot detect a lost
    # screenshot — only a count that exceeds what the chrome contributes can.
    MIN_IMAGE_OBJECTS = 5

    WRONG_DIR_HINT = (
        "The example's screenshot did not embed. Its path must be relative to the "
        "recap document itself (INV-161) — bootcamp_recap.example.truthset.png, not "
        "docs/examples/... — and the generator names every drop on stderr with an "
        "'embedded N of M images' count (INV-162). See this module's docstring."
    )

    def test_screenshot_is_embedded(self):
        raw = pdf_bytes()
        images = raw.count(b"/Subtype /Image") + raw.count(b"/Subtype/Image")
        self.assertGreaterEqual(
            images,
            self.MIN_IMAGE_OBJECTS,
            f"The example PDF carries {images} image object(s), expected at least "
            f"{self.MIN_IMAGE_OBJECTS} (cover logo, its soft mask, and the Truth "
            f"Set screenshot). {self.WRONG_DIR_HINT}",
        )

    def test_screenshot_caption_is_rendered(self):
        """The caption travels with the image, so its absence dates the loss.

        Asserted separately from the object count: a future cover change could
        alter how many image objects the logo contributes, but the caption is
        rendered only when the screenshot itself resolved and embedded.
        """
        self.assertIn(
            "159 records resolved into 84 entities",
            normalize(pdf_text(EXAMPLE_PDF)),
            "The Truth Set screenshot's caption is missing from the example PDF. "
            + self.WRONG_DIR_HINT,
        )

    def test_markdown_references_the_screenshot(self):
        with open(EXAMPLE_MD, encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("bootcamp_recap.example.truthset.png", text)

    def test_the_reference_is_document_relative(self):
        """INV-161: the path a Markdown reader needs is the path the renderer needs."""
        with open(EXAMPLE_MD, encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("](bootcamp_recap.example.truthset.png)", text)
        self.assertNotIn(
            "](docs/examples/bootcamp_recap.example.truthset.png)",
            text,
            "a cwd-relative path resolves from exactly one directory, which INV-161 forbids",
        )


class TestPdfRegeneratesFromItsSource(unittest.TestCase):
    """INV-065's 'regenerable' is a property of a *fresh* render, not the committed file.

    The committed PDF keeps whatever was baked into it by whichever render produced
    it, so inspecting it cannot tell you the pair still reproduces. The 2026-07-28
    audit found exactly that gap: the resolver had moved to document-relative
    (INV-161), the example had not, and every assertion against the committed bytes
    still passed while a fresh render silently lost the screenshot.
    """

    def _render(self, out_dir):
        script = os.path.join(
            REPO_ROOT, "plugins", "senzing-bootcamp", "scripts", "generate_recap_pdf.py"
        )
        out = os.path.join(out_dir, "regen.pdf")
        proc = subprocess.run(
            [sys.executable, script, "--input", EXAMPLE_MD, "--output", out],
            capture_output=True,
            text=True,
            cwd=tempfile.gettempdir(),  # deliberately unrelated to the repo
        )
        return proc, out

    def test_a_fresh_render_embeds_every_referenced_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc, out = self._render(tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            combined = proc.stdout + proc.stderr
            self.assertIn(
                "embedded 1 of 1 images",
                combined,
                "the example references one screenshot and it must embed (INV-161/INV-162):\n"
                + combined,
            )
            self.assertNotIn("skipped image", combined)

    def test_a_fresh_render_matches_the_committed_pdf_image_count(self):
        """A committed PDF richer than a fresh render means the pair has drifted."""
        with tempfile.TemporaryDirectory() as tmp:
            _, out = self._render(tmp)
            with open(out, "rb") as handle:
                fresh = handle.read()
            committed = pdf_bytes()

            def count(raw):
                return raw.count(b"/Subtype /Image") + raw.count(b"/Subtype/Image")

            self.assertEqual(
                count(fresh),
                count(committed),
                "the committed example PDF is not reproducible from its Markdown "
                "(INV-065). Regenerate it — see this module's docstring.",
            )

    def test_check_mode_reports_no_missing_image(self):
        """--check is what graduation runs; it must be clean on the shipped example."""
        script = os.path.join(
            REPO_ROOT, "plugins", "senzing-bootcamp", "scripts", "generate_recap_pdf.py"
        )
        proc = subprocess.run(
            [sys.executable, script, "--input", EXAMPLE_MD, "--check"],
            capture_output=True,
            text=True,
            cwd=tempfile.gettempdir(),
        )
        self.assertNotIn("embedded image not found", proc.stdout + proc.stderr)


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
