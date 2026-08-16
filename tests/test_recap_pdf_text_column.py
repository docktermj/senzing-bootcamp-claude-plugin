"""The recap generator resets to the left margin before every full-width write (INV-121).

INV-121 binds a **class** — "a bundled generator that renders a bootcamper-facing deliverable" —
and names `tests/test_discoveries_pdf.py` as its enforcement. That test imports
`generate_discoveries_pdf` only, so until this file existed the rule was guarded in one generator
of two, and the unguarded one is the larger (3,366 lines against 945) and the one carrying the
certificate page, where the auto page-break is off and INV-121's failure mode is worst.

The behaviour was already correct in both — this closes a coverage gap, not a live defect. The
recap generator resets via `pdf.set_x(pdf.l_margin)` / `set_xy(pdf.l_margin, …)` throughout. What
was missing is anything that fails if a future block forgets.

**The hazard, exactly as INV-121 states it:** in fpdf2 a `multi_cell` leaves the cursor at the
right margin (`new_x=RIGHT`), so an unreset following write draws off-sheet — producing blank space
with no error raised, no effect on the content-retention figure (the text *is* in the content
stream, merely outside the page box), and therefore a successful-looking render that lost content.
So the fixture puts a table immediately before full-width prose, which is that sequence, and the
assertion is positional: the prose run's **start x** must sit in the left half of the page. That
threshold is the one `test_discoveries_pdf.py` calibrated — the defect it was written for put full,
correct text at x ≈ 567 pt on a 595 pt page, which is *inside the sheet* and so invisible to an
on-page check.

Skipped rather than passed when `fpdf2` is absent (INV-163): the stdlib fallback positions text
differently, so this would assert nothing about the renderer it names.

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
SCRIPTS = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp", "scripts")
RECAP = os.path.join(SCRIPTS, "generate_recap_pdf.py")

A4_W_PT = 595.28

#: Generators this guard covers, derived rather than hardcoded — a hardcoded pair is how the
#: brand palette drifted out of INV-107's scope until INV-184 was needed. `generate_document_pdf.py`
#: is excluded **explicitly, with the reason**: it is a thin wrapper that imports
#: `generate_discoveries_pdf.main` and parses no arguments, so it has no drawing code of its own and
#: a guard pretending to cover it would assert something it never tests.
WRAPPER_WITH_NO_DRAWING_CODE = "generate_document_pdf.py"


def pdf_generators():
    return sorted(
        name for name in os.listdir(SCRIPTS)
        if name.startswith("generate_") and name.endswith("_pdf.py")
        and name != WRAPPER_WITH_NO_DRAWING_CODE
    )


def have_fpdf2():
    return importlib.util.find_spec("fpdf") is not None


RECAP_SOURCE = """# Senzing Bootcamp Recap

**Bootcamper:** Test Person
**Started:** 2026-07-31T09:00:00+00:00

---

## System verification — 2026-07-31T10:00:00+00:00

### Information Shared

- A table immediately precedes full-width prose, which is INV-121's hazard sequence.

| Match key | Count |
|---|---|
| +NAME+ADDRESS | 12 |
| +NAME+PHONE | 7 |

UNIQUEMARKERPROSE this paragraph follows a table directly and must start at the left margin.

```text
UNIQUEMARKERCODE a fenced block, which the generator draws through a different write path
```

UNIQUEMARKERAFTERCODE prose after the fenced block, a third write path in sequence.

### Questions & Responses

- **Q:** Did the pipeline resolve?
- **R:** Yes.

### Actions Taken

- Ran the verification load.

### End-of-Module Summary

**What you accomplished:**

- Verified the pipeline end to end.

**Files produced:**

- `src/system_verification/verify.py` — the verification script.

**Why it matters:** it proves Senzing works on this workstation.

---
"""


def render(markdown):
    """Render through the CLI — the real contract — and return the PDF path."""
    workdir = tempfile.mkdtemp()
    src = os.path.join(workdir, "recap.md")
    out = os.path.join(workdir, "recap.pdf")
    with open(src, "w", encoding="utf-8") as handle:
        handle.write(markdown)
    proc = subprocess.run(
        [sys.executable, RECAP, "--input", src, "--output", out],
        capture_output=True, text=True, cwd=workdir,
    )
    assert proc.returncode == 0, proc.stderr
    return out


def all_runs(path):
    """Every drawn text run as (x, y, text) in points, across every page.

    `Td` and `Tm` both set the text position; keying off the operator rather than `BT` handles the
    forms fpdf2 emits. Streams that are not text (images) simply yield no matches.
    """
    with open(path, "rb") as handle:
        raw = handle.read()
    pattern = re.compile(r"([\d.]+)\s+([\d.]+)\s+(?:Td|Tm)\b(.*?)\bTj", re.S)
    runs = []
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", raw, re.S):
        body = match.group(1)
        try:
            body = zlib.decompressobj().decompress(body)
        except zlib.error:
            pass
        for run in pattern.finditer(body.decode("latin-1", "replace")):
            text = re.findall(r"\((.*?)\)\s*$", run.group(3).strip())
            if text:
                runs.append((float(run.group(1)), float(run.group(2)), text[0]))
    return runs


@unittest.skipUnless(have_fpdf2(), "fpdf2 absent — the stdlib fallback positions text differently, "
                                   "so this would assert nothing about the named renderer (INV-163)")
class FullWidthProseStartsAtTheLeftMargin(unittest.TestCase):
    """The positional check INV-121 requires, on the generator its named test does not import."""

    @classmethod
    def setUpClass(cls):
        cls.runs = all_runs(render(RECAP_SOURCE))

    def test_the_render_produced_drawn_text(self):
        self.assertGreater(len(self.runs), 20,
                           "almost nothing was drawn; the fixture or extractor has drifted")

    #: One marker per distinct full-width write path the fixture reaches. Verified by injection:
    #: forcing the cursor to the right margin before each path's `multi_cell` fails the matching
    #: assertion below. Paths the fixture does **not** reach are named in the module docstring.
    MARKERS = ("UNIQUEMARKERPROSE", "UNIQUEMARKERCODE", "UNIQUEMARKERAFTERCODE")

    def test_every_marker_rendered(self):
        """Without this, each positional assertion below would pass on an empty selection."""
        for marker in self.MARKERS:
            with self.subTest(marker=marker):
                self.assertTrue([r for r in self.runs if marker in r[2]],
                                "%s did not render at all" % marker)

    def test_each_full_width_write_starts_in_the_left_half(self):
        """The sequence INV-121 names: an unreset write after a `multi_cell` draws off-sheet."""
        for marker in self.MARKERS:
            for x, _y, text in [r for r in self.runs if marker in r[2]]:
                with self.subTest(marker=marker, text=text[:40]):
                    self.assertLess(
                        x, A4_W_PT / 2,
                        "%s starts at x=%.1f pt — the cursor was not reset to the left margin "
                        "before the write, so it renders off the text column (INV-121)"
                        % (marker, x),
                    )

    def test_no_run_is_drawn_at_a_negative_x(self):
        """The certificate's own failure mode: a ~78-character name once drew from x = -18 mm,
        off the card and off the page, on the one page with the auto page-break disabled."""
        offsheet = [(x, t) for x, _y, t in self.runs if x < 0]
        self.assertEqual([], offsheet, "run(s) drawn off the left edge: %r" % offsheet[:3])

    def test_the_table_itself_stays_in_the_text_column(self):
        cells = [r for r in self.runs if "NAME+ADDRESS" in r[2] or "Match key" in r[2]]
        self.assertTrue(cells, "the table did not render")
        for x, _y, text in cells:
            with self.subTest(text=text):
                self.assertLess(x, A4_W_PT / 2, "table cell drawn outside the text column")


class TheGuardCoversTheWholeClass(unittest.TestCase):
    """INV-121 binds every bundled PDF generator, so the covered set is derived, not listed."""

    def test_both_pdf_generators_are_discovered(self):
        found = pdf_generators()
        self.assertIn("generate_recap_pdf.py", found)
        self.assertIn("generate_discoveries_pdf.py", found)

    def test_the_derivation_is_not_vacuous(self):
        self.assertGreaterEqual(
            len(pdf_generators()), 2,
            "fewer than two PDF generators discovered — the naming convention changed and this "
            "guard would silently stop covering the class",
        )

    def test_each_discovered_generator_has_a_positional_guard(self):
        """Every generator in the class is asserted positionally *somewhere* in `tests/`."""
        coverage = {
            "generate_recap_pdf.py": "test_recap_pdf_text_column.py",
            "generate_discoveries_pdf.py": "test_discoveries_pdf.py",
        }
        for name in pdf_generators():
            with self.subTest(generator=name):
                guard = coverage.get(name)
                self.assertIsNotNone(
                    guard,
                    "%s renders a bootcamper-facing PDF and no positional guard is mapped to it; "
                    "INV-121 binds it (this is how the third generator drifted out of INV-107's "
                    "scope)" % name,
                )
                path = os.path.join(REPO_ROOT, "tests", guard)
                self.assertTrue(os.path.isfile(path), "missing guard file: %s" % guard)
                with open(path, encoding="utf-8") as handle:
                    body = handle.read()
                self.assertIn("A4_W_PT", body,
                              "%s does not use the text-column threshold" % guard)

    def test_the_wrapper_is_excluded_with_its_reason(self):
        """Excluded explicitly, not silently — it has no drawing code to guard."""
        self.assertNotIn(WRAPPER_WITH_NO_DRAWING_CODE, pdf_generators())
        wrapper = os.path.join(SCRIPTS, WRAPPER_WITH_NO_DRAWING_CODE)
        self.assertTrue(os.path.isfile(wrapper))
        with open(wrapper, encoding="utf-8") as handle:
            body = handle.read()
        self.assertIn("generate_discoveries_pdf", body,
                      "the wrapper no longer delegates, so it may now have drawing code of its "
                      "own and this exclusion is no longer safe")


if __name__ == "__main__":
    unittest.main()
