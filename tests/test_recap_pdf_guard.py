"""Tests for the recap PDF generator's content-loss guard.

`plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` used to print
`PDF generated:` and exit 0 even when it had dropped essentially all of its
input — body text is kept only under a module section's `### ` sub-headings, so a
document with `## ` headings and no recognised sub-headings rendered as headings
with empty bodies. A success message plus a plausibly-sized PDF is the failure
nobody checks, so these tests pin the two outcome classes apart:

* recognisable but imperfect recap  -> warn, render, exit 0 (non-blocking)
* not a recap / catastrophic loss   -> no PDF, no success line, exit non-zero

Each case runs the generator as a subprocess (mirroring `test_write_gate.py`) so
the real exit code and the real stdout/stderr contract are asserted, not an
in-process approximation.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")
SCRIPT = os.path.join(PLUGIN, "scripts", "generate_recap_pdf.py")
EXAMPLE = os.path.join(PLUGIN, "docs", "examples", "bootcamp_recap.example.md")

SUCCESS_LINE = "PDF generated:"

# A minimal well-formed recap: one module section carrying all four sub-sections.
# Body text is deliberately long relative to the headings so retention stays high,
# which is what a real recap looks like.
GOOD_RECAP = """# Senzing Bootcamp Recap

**Bootcamper:** Ada Lovelace
**Started:** 2026-07-20

## Entity Resolution Concepts — 2026-07-20T10:00:00-05:00

### Information Shared

Entity resolution distinguishes records that describe the same real-world thing
from records that merely look similar, which is the whole point of the exercise.

### Questions & Responses

- **Q:** What is a false positive?
- **A:** Two records merged into one entity that describe different real people.

### Actions Taken

- Completed the concepts primer and the optional knowledge-check quiz.

### End-of-Module Summary

Built a working vocabulary for the hands-on modules that follow this one.
"""

# H2 headings but no recognised H3 sub-headings: the shape of the discoveries
# document that originally produced a 6-page PDF containing none of its findings.
NON_RECAP = """# Bootcamp Data Discoveries

**Generated:** 2026-07-25

## Headline resolution numbers

3,986 entities resolved from 4,000 records. APM MEDICAL and ABSOLUTE DENTAL were
the two largest merges found in the loaded data.

## What was NOT found, and why

The two sources share only 8 organization names, so 4 cross-source merges is
near the achievable ceiling rather than a weak result.
"""


def run(markdown, args=(), env=None):
    """Render `markdown` in a temp dir; return (exit_code, stdout, stderr, pdf_exists)."""
    workdir = tempfile.mkdtemp()
    src = os.path.join(workdir, "recap.md")
    out = os.path.join(workdir, "recap.pdf")
    with open(src, "w", encoding="utf-8") as fh:
        fh.write(markdown)
    run_env = dict(os.environ)
    if env:
        run_env.update(env)
    proc = subprocess.run(
        [sys.executable, SCRIPT, "--input", src, "--output", out, *args],
        capture_output=True, text=True, cwd=workdir, env=run_env,
    )
    return proc.returncode, proc.stdout, proc.stderr, os.path.exists(out)


def run_file(path, args=()):
    """Render an on-disk file (used for the shipped example recap)."""
    out = os.path.join(tempfile.mkdtemp(), "recap.pdf")
    proc = subprocess.run(
        [sys.executable, SCRIPT, "--input", path, "--output", out, *args],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr, os.path.exists(out)


class NonRecapInputFails(unittest.TestCase):
    """The fatal class: refuse to render, and never claim success."""

    def test_exits_non_zero(self):
        code, _, _, _ = run(NON_RECAP)
        self.assertNotEqual(code, 0)

    def test_prints_no_success_line(self):
        # The graduation skill treats a `PDF generated:` line as success, so its
        # absence is the load-bearing assertion of this whole spec.
        _, stdout, _, _ = run(NON_RECAP)
        self.assertNotIn(SUCCESS_LINE, stdout)

    def test_writes_no_pdf(self):
        _, _, _, pdf_exists = run(NON_RECAP)
        self.assertFalse(pdf_exists)

    def test_names_the_structural_mismatch(self):
        _, _, stderr, _ = run(NON_RECAP)
        self.assertIn("does not look like a bootcamp recap", stderr)
        self.assertIn("sub-section", stderr)

    def test_reports_retention_figure(self):
        _, _, stderr, _ = run(NON_RECAP)
        self.assertIn("source characters", stderr)

    def test_no_module_sections_at_all_also_fails(self):
        code, stdout, _, pdf_exists = run("# Notes\n\nJust prose, no sections.\n")
        self.assertNotEqual(code, 0)
        self.assertNotIn(SUCCESS_LINE, stdout)
        self.assertFalse(pdf_exists)


class ValidRecapSucceeds(unittest.TestCase):
    """The non-blocking guarantee: a recognisable recap always renders."""

    def test_complete_recap_renders(self):
        code, stdout, _, pdf_exists = run(GOOD_RECAP)
        self.assertEqual(code, 0)
        self.assertIn(SUCCESS_LINE, stdout)
        self.assertTrue(pdf_exists)

    def test_success_line_reports_retention(self):
        _, stdout, _, _ = run(GOOD_RECAP)
        self.assertIn("source characters", stdout)

    def test_incomplete_recap_still_renders_and_exits_zero(self):
        # One missing sub-section is the "imperfect but recognisable" class: it
        # must warn and still ship the PDF, because graduation is non-blocking.
        incomplete = GOOD_RECAP.replace("### Actions Taken\n", "")
        code, stdout, stderr, pdf_exists = run(incomplete)
        self.assertEqual(code, 0)
        self.assertIn(SUCCESS_LINE, stdout)
        self.assertTrue(pdf_exists)
        self.assertIn("WARNING", stderr)

    def test_shipped_example_recap_renders(self):
        # Guards the retention threshold against false positives: the reference
        # recap must never trip the content-loss check.
        code, stdout, _, pdf_exists = run_file(EXAMPLE)
        self.assertEqual(code, 0)
        self.assertIn(SUCCESS_LINE, stdout)
        self.assertTrue(pdf_exists)


class RendererDowngradeIsNeverSilent(unittest.TestCase):
    """An unavailable fpdf2 must say which case it was, and name the interpreter."""

    def test_broken_install_is_reported(self):
        # A module that raises on import = installed but unusable. Shadowing it on
        # PYTHONPATH simulates that without touching the real environment.
        shim = tempfile.mkdtemp()
        with open(os.path.join(shim, "fpdf.py"), "w", encoding="utf-8") as fh:
            fh.write('raise ImportError("simulated broken fpdf2 install")\n')
        code, stdout, stderr, pdf_exists = run(GOOD_RECAP, env={"PYTHONPATH": shim})
        self.assertEqual(code, 0)                 # INV-066: a PDF is still produced
        self.assertTrue(pdf_exists)
        self.assertIn("could not be imported", stderr)
        self.assertIn(sys.executable, stderr)     # venv mismatch must be legible
        self.assertIn("renderer: stdlib", stdout)


class StdlibFallbackKeepsCertificate(unittest.TestCase):
    """INV-066 + INV-100: the fallback still ends in a landscape certificate."""

    def test_certificate_page_present_in_stdlib_render(self):
        shim = tempfile.mkdtemp()
        with open(os.path.join(shim, "fpdf.py"), "w", encoding="utf-8") as fh:
            fh.write('raise ImportError("force stdlib")\n')
        workdir = tempfile.mkdtemp()
        src = os.path.join(workdir, "recap.md")
        out = os.path.join(workdir, "recap.pdf")
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(GOOD_RECAP)
        env = dict(os.environ, PYTHONPATH=shim)
        proc = subprocess.run(
            [sys.executable, SCRIPT, "--input", src, "--output", out],
            capture_output=True, text=True, cwd=workdir, env=env,
        )
        self.assertEqual(proc.returncode, 0)
        with open(out, "rb") as fh:
            raw = fh.read().decode("latin-1")
        self.assertIn("Certificate of Completion", raw)
        landscape = [
            (w, h)
            for w, h in re.findall(r"/MediaBox \[0 0 ([\d.]+) ([\d.]+)\]", raw)
            if float(w) > float(h)
        ]
        self.assertEqual(len(landscape), 1, "expected exactly one landscape page")


# A recap whose lists exercise every spacing decision at once: spaced subsections,
# the spaced "What you accomplished" label block, and the two deliberate exclusions.
SPACING_RECAP = """# Senzing Bootcamp Recap

**Bootcamper:** Ada Lovelace
**Started:** 2026-07-20
**Plugin version:** 9.9.9

## SDK setup — 2026-07-20T10:00:00-05:00

### Information Shared

- First shared item, long enough that it wraps onto a second rendered line so the
  gap between items has to be larger than the gap inside one item.
- Second shared item, also long enough to wrap across more than a single line in
  the rendered output of this subsection.
- Third and final shared item of this list.

### Questions & Responses

- **Q:** Which database would you like to use?
  - **R:** SQLite
- **Q:** Do you have a Senzing License Key?
  - **R:** No, request an evaluation license

### Actions Taken

- Created the SQLite database and schema at database/G2C.db.
- Created the engine configuration at config/engine_config.json.

### End-of-Module Summary

**What you accomplished:**
- Verified the SDK works end to end.
- Configured the database and engine.

**Files produced:**
- `artifacts/alpha-marker.db`
- `artifacts/beta-marker.json`
"""


def load_generator():
    """Import the generator as a module so its helpers can be unit-tested."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("recap_gen_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["recap_gen_under_test"] = module
    spec.loader.exec_module(module)
    return module


def drawn_runs(path):
    """Every drawn text run as (x, y, text) in points.

    Position is what distinguishes "rendered" from "present in the file", and it is the
    only way to measure spacing. A stream that will not decompress is kept raw rather
    than skipped — dropping it fabricates missing content (it did, during this
    implementation, and briefly looked like a lost module section).
    """
    import zlib

    with open(path, "rb") as handle:
        raw = handle.read()
    runs = []
    pattern = re.compile(r"([\d.]+)\s+([\d.]+)\s+(?:Td|Tm)\b(.*?)\bTj", re.S)
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", raw, re.S):
        body = match.group(1)
        # `decompressobj` decodes the valid prefix and tolerates a slice whose tail
        # is off by a few bytes; strict `decompress` raises on that, which silently
        # hid a whole page of text and looked exactly like a lost module section.
        try:
            body = zlib.decompressobj().decompress(body)
        except zlib.error:
            pass
        for run_match in pattern.finditer(body.decode("latin-1", "replace")):
            text = re.findall(r"\((.*?)\)\s*$", run_match.group(3).strip())
            if text:
                runs.append(
                    (round(float(run_match.group(1)), 1), round(float(run_match.group(2)), 1), text[0])
                )
    return runs


def render_to(markdown, args=()):
    """Render `markdown` and return the output PDF path (kept for inspection)."""
    workdir = tempfile.mkdtemp()
    src = os.path.join(workdir, "recap.md")
    out = os.path.join(workdir, "recap.pdf")
    with open(src, "w", encoding="utf-8") as fh:
        fh.write(markdown)
    proc = subprocess.run(
        [sys.executable, SCRIPT, "--input", src, "--output", out, *args],
        capture_output=True, text=True, cwd=workdir,
    )
    assert proc.returncode == 0, proc.stderr
    return out


class CertificateCarriesThePluginVersion(unittest.TestCase):
    """The certificate is the page most likely to be detached and shared on its own, so
    it has to say which plugin produced it."""

    def test_version_line_is_rendered(self):
        runs = drawn_runs(render_to(SPACING_RECAP))
        self.assertTrue(
            any("Senzing Bootcamp Claude plugin v9.9.9" == t for _x, _y, t in runs),
            "the certificate must name the plugin version from the header meta row",
        )

    def test_version_is_omitted_when_the_meta_row_is_absent(self):
        """Omit, never a placeholder — a certificate is permanently visible."""
        without = SPACING_RECAP.replace("**Plugin version:** 9.9.9\n", "")
        runs = drawn_runs(render_to(without))
        self.assertFalse(any("Claude plugin v" in t for _x, _y, t in runs))
        self.assertTrue(
            any(t.strip() == "Senzing Bootcamp" for _x, _y, t in runs),
            "the existing attribution line must survive",
        )

    def test_both_attribution_lines_clear_the_inner_border(self):
        """The ember border's bottom edge is at h - 14 mm; a line at h - 17 is clipped.

        Text extraction reported the string present and correct while the glyphs were
        visually sliced in half, so this asserts geometry, not presence.
        """
        module = load_generator()
        runs = drawn_runs(render_to(SPACING_RECAP))
        # Landscape A4 height = 210 mm; the border bottom sits 14 mm above the page
        # bottom, i.e. at y = 14 mm in fpdf2's top-down space.
        attribution = [
            (y, t) for _x, y, t in runs
            if t.strip() == "Senzing Bootcamp" or "Claude plugin v" in t
        ]
        self.assertEqual(2, len(attribution), "expected exactly two attribution lines")
        for y, text in attribution:
            with self.subTest(text=text):
                # y here is a PDF baseline in points from the page bottom; both lines
                # must sit above the 14 mm (≈39.7 pt) border.
                self.assertGreater(y, 39.7, f"{text!r} is clipped by the inner border")
        self.assertEqual(2, len(module._cert_attribution(module.parse_recap(SPACING_RECAP))))

    def test_partition_meta_docstring_matches_the_code(self):
        """It used to claim identity rows drive the certificate; they do not."""
        module = load_generator()
        doc = re.sub(r"\s+", " ", module._partition_meta.__doc__ or "")
        self.assertIn("cover card", doc)
        self.assertRegex(doc, r"certificate does \*\*not\*\* consume this partition")


class ListItemsAreSpacedWhereItHelps(unittest.TestCase):
    """Bullets ended with no trailing gap, so the space between two items equalled the
    space inside one wrapped item and multi-line bullets ran together."""

    def setUp(self):
        self.module = load_generator()
        self.runs = drawn_runs(render_to(SPACING_RECAP))

    def _y_of(self, needle):
        for _x, y, text in self.runs:
            if needle in text:
                return y
        self.fail(f"{needle!r} was not drawn")

    def test_spaced_and_unspaced_subsections_are_declared(self):
        self.assertEqual(
            ("information shared", "actions taken"), self.module._SPACED_SUBSECTIONS
        )
        self.assertEqual(("what you accomplished",), self.module._SPACED_LABELS)

    def test_action_taken_singular_is_covered(self):
        """INV-048 names it singular; every surface uses the plural."""
        self.assertIn(
            self.module._normalize_heading("Action Taken"), self.module._SPACED_SUBSECTIONS
        )

    def test_consecutive_actions_taken_items_are_more_than_one_line_apart(self):
        first = self._y_of("Created the SQLite database")
        second = self._y_of("Created the engine configuration")
        gap = first - second
        # One line is 5.5 mm ≈ 15.6 pt; the item gap adds 2.4 mm ≈ 6.8 pt.
        self.assertGreater(gap, 17.0, "Actions Taken items are still one line apart")

    def test_question_and_response_stay_together(self):
        """Spacing here would separate each answer from the question it answers."""
        question = self._y_of("Which database would you like to use")
        response = self._y_of("SQLite")
        self.assertLess(
            question - response, 17.0, "Q/R pairing must not be broken by item spacing"
        )

    def test_files_produced_list_stays_tight(self):
        first = self._y_of("artifacts/alpha-marker.db")
        second = self._y_of("artifacts/beta-marker.json")
        self.assertLess(
            first - second, 17.0, "Files produced is a short path list; keep it tight"
        )

    def test_accomplishments_list_is_spaced(self):
        first = self._y_of("Verified the SDK works end to end")
        second = self._y_of("Configured the database and engine")
        self.assertGreater(first - second, 17.0)

    def test_gap_is_between_items_never_after_the_last(self):
        lines = [
            "- first item",
            "- second item",
            "",
            "not a bullet",
        ]
        self.assertTrue(self.module._next_nonblank_is_bullet(lines, 0))
        self.assertFalse(self.module._next_nonblank_is_bullet(lines, 1))
        self.assertFalse(self.module._next_nonblank_is_bullet(lines, 3))

    def test_block_label_only_matches_a_standalone_label(self):
        """A bullet carrying `- **Q:**` must not switch spacing on."""
        self.assertEqual(
            "what you accomplished", self.module._block_label("**What you accomplished:**")
        )
        self.assertEqual("", self.module._block_label("- **Q:** a question"))

    def test_content_is_not_lost_to_the_added_spacing(self):
        """INV-110/INV-121: extra vertical space must never push content out."""
        for probe in (
            "First shared item",
            "Third and final shared item",
            "Created the engine configuration",
            "Verified the SDK works end to end",
            "config/engine_config.json",
        ):
            with self.subTest(probe=probe):
                self.assertTrue(any(probe in t for _x, _y, t in self.runs))


class StdlibFallbackMatchesTheFpdf2Certificate(unittest.TestCase):
    """The two renderers must not drift on the certificate footer."""

    def test_stdlib_certificate_carries_the_version_line(self):
        module = load_generator()
        recap = module.parse_recap(SPACING_RECAP)
        stream = module._stdlib_certificate_stream(recap, 842.0, 595.0)
        self.assertIn("Senzing Bootcamp Claude plugin v9.9.9", stream)
        self.assertIn("Senzing Bootcamp", stream)

    def test_stdlib_certificate_omits_an_absent_version(self):
        module = load_generator()
        recap = module.parse_recap(SPACING_RECAP.replace("**Plugin version:** 9.9.9\n", ""))
        stream = module._stdlib_certificate_stream(recap, 842.0, 595.0)
        self.assertNotIn("Claude plugin v", stream)
        self.assertIn("Senzing Bootcamp", stream)

    def test_stdlib_gap_token_emits_no_text_operator(self):
        """A GAP token is pure vertical space; it must not reference a font."""
        module = load_generator()
        recap = module.parse_recap(SPACING_RECAP)
        out = os.path.join(tempfile.mkdtemp(), "stdlib.pdf")
        self.assertTrue(module.render_with_stdlib(recap, __import__("pathlib").Path(out)))
        with open(out, "rb") as handle:
            raw = handle.read().decode("latin-1")
        self.assertNotIn("/GAP", raw, "the gap sentinel must never reach the PDF")
        self.assertIn("Certificate of Completion", raw)


class CheckModeContract(unittest.TestCase):
    """`--check` keeps its exit semantics: 0 when complete, non-zero on any gap."""

    def test_complete_recap_passes_check(self):
        code, stdout, _, _ = run(GOOD_RECAP, args=("--check",))
        self.assertEqual(code, 0)
        self.assertIn("Recap complete", stdout)

    def test_incomplete_recap_fails_check(self):
        incomplete = GOOD_RECAP.replace("### Actions Taken\n", "")
        code, _, stderr, _ = run(incomplete, args=("--check",))
        self.assertNotEqual(code, 0)
        self.assertIn("INCOMPLETE", stderr)

    def test_check_does_not_write_a_pdf(self):
        _, _, _, pdf_exists = run(GOOD_RECAP, args=("--check",))
        self.assertFalse(pdf_exists)


class UnfinalizedModuleIsReported(unittest.TestCase):
    """A missed module-completion step 2d must not pass silently.

    Step 2d appends the finalized `## {Name}` section and then removes the
    durability hooks' folded `<!-- RECAP-CHECKPOINT -->` block. Skipping the
    removal leaves two copies of the module, and the markers are HTML comments
    that the renderers drop — so the keepsake PDF renders the module twice with
    nothing on stderr to say why. Neither symptom blocks graduation (INV-110
    keeps a recognisable recap renderable), but both must be *reported*.
    """

    def duplicated(self):
        """GOOD_RECAP with its module section repeated."""
        head, sep, body = GOOD_RECAP.partition("## Entity Resolution Concepts")
        return head + sep + body + "\n" + sep + body

    def with_marker_block(self):
        head, sep, body = GOOD_RECAP.partition("## Entity Resolution Concepts")
        return (
            head
            + "<!-- RECAP-CHECKPOINT:START -->\n\n"
            + sep
            + body
            + "\n<!-- RECAP-CHECKPOINT:END -->\n"
        )

    def test_duplicate_section_fails_check(self):
        code, _, stderr, _ = run(self.duplicated(), args=("--check",))
        self.assertNotEqual(code, 0, "a duplicated module section must fail --check")
        self.assertIn("more than one recap section", stderr)

    def test_duplicate_section_still_renders_but_warns(self):
        """Non-blocking: graduation still gets its PDF (INV-048/INV-110)."""
        code, stdout, stderr, pdf_exists = run(self.duplicated())
        self.assertEqual(code, 0, stderr)
        self.assertIn(SUCCESS_LINE, stdout)
        self.assertTrue(pdf_exists)
        self.assertIn("more than one recap section", stderr)

    def test_stray_checkpoint_block_fails_check(self):
        code, _, stderr, _ = run(self.with_marker_block(), args=("--check",))
        self.assertNotEqual(code, 0, "a surviving checkpoint block must fail --check")
        self.assertIn("RECAP-CHECKPOINT", stderr)

    def test_stray_checkpoint_block_still_renders_but_warns(self):
        code, stdout, stderr, pdf_exists = run(self.with_marker_block())
        self.assertEqual(code, 0, stderr)
        self.assertIn(SUCCESS_LINE, stdout)
        self.assertTrue(pdf_exists)
        self.assertIn("RECAP-CHECKPOINT", stderr)

    def test_markers_match_the_hook_that_writes_them(self):
        """The renderer's fence constants must equal recap_checkpoint.py's."""
        import re

        def constants(path):
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            return set(re.findall(r'"(<!-- RECAP-CHECKPOINT:(?:START|END) -->)"', text))

        hook = os.path.join(PLUGIN, "scripts", "recap_checkpoint.py")
        self.assertEqual(
            constants(hook),
            constants(SCRIPT),
            "the fold hook and the renderer disagree on the checkpoint markers, "
            "so the renderer would stop detecting unfinalized modules",
        )

    def test_clean_recap_reports_neither(self):
        code, _, stderr, _ = run(GOOD_RECAP, args=("--check",))
        self.assertEqual(code, 0, stderr)
        self.assertNotIn("more than one recap section", stderr)
        self.assertNotIn("RECAP-CHECKPOINT", stderr)


if __name__ == "__main__":
    unittest.main()
