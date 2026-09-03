"""Finding an SDK already installed skips the INSTALL, never Step 3 entirely.

SDK setup's Step 3 does two jobs: it installs the SDK, and it writes the
project-local environment script that exports the library and language paths.
Only the first is redundant when the SDK is already present. Skipping both
leaves the Bootcamper with a healthy install and no environment, and every later
module then fails at import with ``libSz.so: cannot open shared object file`` --
which reads as a broken install, in a *later* module, far from the decision that
caused it.

Step 1's own filesystem fallback exists precisely because the import check fails
on a working install when ``PYTHONPATH``/``LD_LIBRARY_PATH`` are unset, so routing
past the step that fixes that is the specific trap.

The module said both things at once: its fallback paragraph read "skip Steps 2 and
3 entirely" while the branch 27 lines below read "Not Step 3 entirely". The first
is what a guide reads at the moment the check succeeds, and it is phrased as a
complete instruction.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "plugins" / "senzing-bootcamp" / "skills"

#: "skip ... Step 3" with no narrowing word between them. ``[^.\n]`` keeps the
#: match inside one sentence so a later sentence's "Step 3" cannot satisfy it.
SKIPS_STEP_3 = re.compile(r"skip[^.\n]{0,60}\bStep(?:s)?\s+2\s+and\s+3\b", re.IGNORECASE)

#: The words that narrow such a statement to the install half.
NARROWERS = ("installation", "install commands", "not step 3 entirely")


def shipped_markdown():
    return sorted(SKILLS.rglob("*.md"))


class NoShippedTextLicensesSkippingStep3Wholesale(unittest.TestCase):
    def test_no_sentence_says_to_skip_steps_2_and_3_without_narrowing_it(self):
        """Derived by scanning (INV-246), not by naming the file the spec cited."""
        offenders = []
        for path in shipped_markdown():
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not SKIPS_STEP_3.search(line):
                    continue
                window = line.lower()
                if any(w in window for w in NARROWERS):
                    continue
                offenders.append("%s:%d %s" % (path.relative_to(REPO), n, line.strip()[:90]))
        self.assertEqual(
            [], offenders,
            "A shipped line tells the guide to skip Steps 2 and 3 without narrowing the skip to "
            "the INSTALLATION. Step 3 also writes the project-local environment script, which an "
            "existing install is the most likely thing to be missing -- and the failure surfaces "
            "in a later module as what looks like a broken SDK: %s" % offenders,
        )

    def test_the_scan_pattern_still_matches_the_historical_defect(self):
        """Guards the guard: a pattern matching nothing passes vacuously forever."""
        historical = ("If the library is present, report the SDK as installed, skip Steps 2 and 3 "
                      "entirely, and proceed to Step 4 verification.")
        self.assertTrue(
            SKIPS_STEP_3.search(historical),
            "The scan no longer matches the exact sentence this guard was written for, so it "
            "would not catch the defect returning.",
        )
        self.assertFalse(
            any(w in historical.lower() for w in NARROWERS),
            "The historical sentence must NOT contain a narrowing word -- if it did, the guard "
            "would exempt the very line it exists to reject.",
        )


class Step1StillRoutesAnExistingInstallThroughTheEnvironmentScript(unittest.TestCase):
    def setUp(self):
        self.text = (SKILLS / "module-02-sdk-setup" / "SKILL.md").read_text(encoding="utf-8")

    def test_the_fallback_paragraph_names_the_environment_script(self):
        """A guide arriving via the fallback must be routed without reading further branches.

        The contradiction was survivable only for a reader who continued to the
        V4.0+ branch; the fallback paragraph is a complete instruction on its own
        and is where the wrong turn was taken.
        """
        i = self.text.find("If the library is present")
        self.assertNotEqual(i, -1, "Step 1's filesystem-fallback conclusion was not found.")
        window = self.text[i:i + 500].lower()
        self.assertTrue(
            "environment-script" in window or "environment script" in window,
            "Step 1's fallback conclusion must say the environment-script work still runs. "
            "Without it the paragraph reads as a complete instruction to skip all of Step 3.",
        )

    def test_the_required_stops_block_is_intact(self):
        """The spec's third criterion: the fix must not disturb the block it points at."""
        for expected in ("Required stops", "senzing-env.sh"):
            self.assertIn(
                expected, self.text,
                "The 'Required stops' block is what the corrected sentence now points at; "
                "it must survive the fix intact.",
            )


if __name__ == "__main__":
    unittest.main()
