"""The End-of-Module Summary's three labeled blocks always reach the recap PDF (INV-103).

INV-103 has required "What you accomplished / Files produced / Why it matters" inside every
module's End-of-Module Summary since 2026-07-23, and said in the same breath that
`generate_recap_pdf.py`'s `--check` "MUST validate it". It validated the *heading* only. So a
summary written as one prose paragraph — the three blocks nowhere in it — passed as
"Recap complete", rendered without complaint, and reached a bootcamper's keepsake with all
three missing. Every downstream signal said success: the heading was present, content
retention was ~100%, and the page looked finished. Reported from a real bootcamp run.

Three properties are pinned here, one per layer, because any one alone leaves the hole:

1. **Detection** — `--check` fails and the render warns, naming the missing blocks. Without
   this the gap is invisible until someone reads the PDF closely.
2. **Rendering** — a block the recap does not carry is drawn as "(not recorded)" instead of
   vanishing. The renderer cannot invent accomplishments, but it can refuse to let an
   absence look like completeness — and it must do so in both renderers (INV-066).
3. **Tolerance** — a block that is *present* but written differently (`**Files produced**:`,
   a bare `Files produced:`, a bulleted label) must never be reported missing. A false
   positive here sends graduation off to backfill content that is already there, or to
   rewrite a finished section (INV-085). Legacy `### Journal` sections, which predate the
   three blocks and which INV-103 explicitly tolerates, stay exempt.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zlib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(
    REPO_ROOT, "plugins", "senzing-bootcamp", "scripts", "generate_recap_pdf.py"
)

PREAMBLE = """# Senzing Bootcamp Recap

**Bootcamper:** Ada Lovelace
**Started:** 2026-07-20

## Data processing — 2026-07-20T15:10:00-05:00

### Information Shared

Loading with the SDK, the redo queue, and how resolution results are validated once a
batch load has completed and the queue has drained all the way to empty.

### Questions & Responses

- **Q:** Which loader shape do you want?
    - **R:** The orchestrator, so every source loads in one run.

### Actions Taken

- Built src/load/ProductionLoader.java and loaded all four of the sources.
- Drained the redo queue and validated the resolved entities against the problem.

"""

# The shape reported from the bootcamp: a summary heading followed by prose, with none of
# the three labeled blocks.
PROSE_SUMMARY = PREAMBLE + """### End-of-Module Summary

You built a production loader, loaded all four sources, drained the redo queue, and
validated the results against the business problem defined in the first module.
"""

LABELED_SUMMARY = PREAMBLE + """### End-of-Module Summary

**What you accomplished:** Built a production loader and loaded all four sources, then
drained the redo queue and validated the resolved entities.

**Files produced:** src/load/ProductionLoader.java, docs/results_validation.md

**Why it matters:** The resolved entities are what the query and visualization module
explores, so the loaded data is the whole basis of what comes next.
"""

# Written differently, but every block is genuinely there.
VARIANT_SUMMARY = PREAMBLE + """### End-of-Module Summary

- **What you accomplished:** Built the loader and loaded all four of the data sources.

**Files produced**: src/load/ProductionLoader.java

Why it matters: The resolved entities are what the next module explores in depth.
"""

# Pre-INV-103 recap: the fourth subsection was a free-narrative Journal.
LEGACY_JOURNAL = PREAMBLE.replace(
    "### Actions Taken", "### Actions Taken"
) + """### Journal

Loading went smoothly once the data sources were registered before the load rather
than after it, which is the ordering the SDK requires of every caller.
"""


def load_generator():
    spec = importlib.util.spec_from_file_location("recap_gen_summary", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["recap_gen_summary"] = module
    spec.loader.exec_module(module)
    return module


def run(markdown, args=()):
    """Run the generator as a subprocess: the real exit-code and stderr contract."""
    workdir = tempfile.mkdtemp()
    src = os.path.join(workdir, "recap.md")
    out = os.path.join(workdir, "recap.pdf")
    with open(src, "w", encoding="utf-8") as handle:
        handle.write(markdown)
    proc = subprocess.run(
        [sys.executable, SCRIPT, "--input", src, "--output", out, *args],
        capture_output=True, text=True, cwd=workdir,
    )
    return proc.returncode, proc.stdout, proc.stderr, out


def pdf_text(path):
    """Drawn text from a PDF, joined so a wrapped line still reads as one string."""
    with open(path, "rb") as handle:
        raw = handle.read()
    chunks = []
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", raw, re.S):
        body = match.group(1)
        try:
            body = zlib.decompressobj().decompress(body)
        except zlib.error:
            pass
        chunks.append(body.decode("latin-1", "replace"))
    fragments = re.findall(r"\(((?:\\.|[^()\\])*)\)\s*Tj", "\n".join(chunks))
    return " ".join(f.replace("\\(", "(").replace("\\)", ")") for f in fragments)


class CheckReportsAMissingBlock(unittest.TestCase):
    """Layer 1: `--check` is what graduation runs before rendering (INV-103)."""

    def test_a_prose_summary_fails_check(self):
        code, _stdout, stderr, _ = run(PROSE_SUMMARY, args=("--check",))
        self.assertEqual(1, code, "a summary with none of the three blocks passed --check")
        self.assertIn("End-of-Module Summary is missing its labeled block", stderr)
        for block in ("What you accomplished", "Files produced", "Why it matters"):
            with self.subTest(block=block):
                self.assertIn(block, stderr)

    def test_one_missing_block_is_named_alone(self):
        code, _stdout, stderr, _ = run(
            LABELED_SUMMARY.replace("**Files produced:**", "**Files delivered:**"),
            args=("--check",),
        )
        self.assertEqual(1, code)
        self.assertIn("Files produced", stderr)
        self.assertNotIn("What you accomplished", stderr)

    def test_a_labeled_summary_passes(self):
        code, stdout, stderr, _ = run(LABELED_SUMMARY, args=("--check",))
        self.assertEqual(0, code, stderr)
        self.assertIn("Recap complete", stdout)

    def test_rendering_warns_but_still_ships_the_pdf(self):
        """Non-blocking, like every recap gap: graduation must not lose the PDF."""
        code, stdout, stderr, out = run(PROSE_SUMMARY)
        self.assertEqual(0, code, stderr)
        self.assertIn("PDF generated:", stdout)
        self.assertTrue(os.path.exists(out))
        self.assertIn("End-of-Module Summary is missing its labeled block", stderr)

    def test_a_missing_subsection_is_not_reported_twice(self):
        """Both messages name the same gap; two lines read as two defects."""
        without = PROSE_SUMMARY.replace("### End-of-Module Summary\n", "")
        _code, _stdout, stderr, _ = run(without, args=("--check",))
        self.assertIn("is missing: End-of-Module Summary", stderr)
        self.assertNotIn("missing its labeled block", stderr)


class EveryBlockReachesThePdf(unittest.TestCase):
    """Layer 2: the guarantee the maintainer asked for — they always show up."""

    def test_absent_blocks_are_drawn_as_not_recorded(self):
        _code, _stdout, _stderr, out = run(PROSE_SUMMARY)
        text = pdf_text(out)
        for block in ("What you accomplished", "Files produced", "Why it matters"):
            with self.subTest(block=block):
                self.assertIn(block, text, f"{block!r} is absent from the rendered PDF")
        self.assertIn("(not recorded)", text)

    def test_recorded_blocks_are_drawn_with_their_content(self):
        _code, _stdout, _stderr, out = run(LABELED_SUMMARY)
        text = pdf_text(out)
        self.assertIn("docs/results_validation.md", text)
        self.assertNotIn("(not recorded)", text)

    def test_an_entirely_absent_summary_still_shows_all_three(self):
        without = PROSE_SUMMARY.replace("### End-of-Module Summary\n", "")
        _code, _stdout, _stderr, out = run(without)
        text = pdf_text(out)
        for block in ("What you accomplished", "Files produced", "Why it matters"):
            with self.subTest(block=block):
                self.assertIn(block, text)

    def test_the_stdlib_fallback_renders_them_too(self):
        """INV-066 binds both renderers; the fallback is what runs without fpdf2."""
        import pathlib

        module = load_generator()
        for source, expected in ((PROSE_SUMMARY, "(not recorded)"),
                                 (LABELED_SUMMARY, "docs/results_validation.md")):
            with self.subTest(expected=expected):
                out = pathlib.Path(tempfile.mkdtemp()) / "stdlib.pdf"
                self.assertTrue(
                    module.render_with_stdlib(module.parse_recap(source), out)
                )
                text = pdf_text(str(out))
                for block in ("What you accomplished", "Files produced", "Why it matters"):
                    self.assertIn(block, text)
                self.assertIn(expected, text)


class PresentBlocksAreNeverCalledMissing(unittest.TestCase):
    """Layer 3: a false "missing" is worse than the bug — it invites a rewrite."""

    def test_emphasis_and_bullet_variants_all_count(self):
        code, _stdout, stderr, _ = run(VARIANT_SUMMARY, args=("--check",))
        self.assertEqual(0, code, stderr)

    def test_label_matcher_accepts_the_forms_a_live_recap_produces(self):
        module = load_generator()
        for line in (
            "**Files produced:** a.txt",
            "**Files produced**: a.txt",
            "- **Files produced:** a.txt",
            "Files produced: a.txt",
            "**Files Produced:**",
            "  **Files produced:** a.txt",
        ):
            with self.subTest(line=line):
                self.assertEqual("files produced", module._summary_block_label(line))

    def test_prose_is_not_mistaken_for_a_label(self):
        module = load_generator()
        self.assertEqual("", module._summary_block_label("Loading went smoothly today"))

    def test_the_optional_takeaway_is_not_required(self):
        module = load_generator()
        self.assertNotIn("Bootcamper's takeaway", module.END_SUMMARY_BLOCKS)

    def test_a_legacy_journal_section_is_exempt(self):
        """INV-103 tolerates the pre-rename heading; a Journal never had the blocks."""
        code, stdout, stderr, _ = run(LEGACY_JOURNAL, args=("--check",))
        self.assertEqual(0, code, stderr)
        self.assertIn("Recap complete", stdout)

    def test_a_legacy_journal_is_not_annotated_in_the_pdf(self):
        _code, _stdout, _stderr, out = run(LEGACY_JOURNAL)
        self.assertNotIn("(not recorded)", pdf_text(out))

    def test_the_shipped_example_recap_is_clean(self):
        """The reference pair is what a correct recap looks like (INV-065)."""
        module = load_generator()
        path = os.path.join(
            REPO_ROOT, "plugins", "senzing-bootcamp", "docs", "examples",
            "bootcamp_recap.example.md",
        )
        with open(path, encoding="utf-8") as handle:
            recap = module.parse_recap(handle.read())
        offenders = {
            mod.title: mod.missing_summary_blocks()
            for mod in recap.modules
            if mod.missing_summary_blocks()
        }
        self.assertEqual({}, offenders)


class TheRequirementIsStatedWhereTheRecapIsWritten(unittest.TestCase):
    """The generator can only report the gap; the guide is what prevents it."""

    def read(self, *parts):
        with open(os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp", *parts),
                  encoding="utf-8") as handle:
            return handle.read()

    def test_module_completion_requires_the_labeled_blocks(self):
        text = self.read("skills", "bootcamp-onboarding", "module-completion.md")
        self.assertIn("never as one prose paragraph", text)
        self.assertIn("**Why it matters:**", text)

    def test_module_completion_verifies_them_in_the_same_read(self):
        """Step 2c already re-reads the recap; catching it there is cheapest."""
        text = self.read("skills", "bootcamp-onboarding", "module-completion.md")
        step = text.split("### 2c.")[1].split("### 2d.")[0]
        self.assertIn("three labeled blocks", step)

    def test_graduation_backfills_them_before_rendering(self):
        text = self.read("skills", "graduation", "SKILL.md")
        self.assertIn("Backfill the End-of-Module Summary blocks", text)
        self.assertIn("Never invent content to fill a label", text)

    def test_graduations_check_step_mentions_the_blocks(self):
        text = self.read("skills", "graduation", "SKILL.md")
        check = text.split("**Content check")[1].split("\n")[0]
        self.assertIn("three labeled blocks", check)


if __name__ == "__main__":
    unittest.main()
