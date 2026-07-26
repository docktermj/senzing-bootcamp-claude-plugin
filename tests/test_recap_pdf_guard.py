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
