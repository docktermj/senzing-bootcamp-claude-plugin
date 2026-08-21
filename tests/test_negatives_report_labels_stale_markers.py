"""The negatives report can answer the staleness question it is read for.

`MCP-NEGATIVE` markers record "tool X does not contain Y" with the server version and date the
claim was checked. That is the one claim shape which cannot go stale detectably: the suite is
offline (INV-108), so nothing notices when the server gains the coverage the plugin routed around.

⚠️ **On 2026-08-21, 21 of 23 markers were dated `server 1.32.9` against a live 1.33.0 and none had
been re-asked — and three audit runs that day each read the report as CLEAN.** The report answered
"is every marker well-formed?" and was read as "has any expired?", so an eight-day-stale marker was
indistinguishable in its output from one re-asked that morning. The label this file guards is what
ends that ambiguity.

⛔ **The current version is always SUPPLIED, never inferred.** An offline scan that guessed what the
live server runs would be the same silent-staleness defect one level down, so with no `--server`
argument the split is not attempted and the report says so rather than implying every marker is
current.

⚠️ **What the label does NOT mean.** DUE means the claim has not been re-asked since an older
server, not that it is wrong. When all 21 were finally re-asked on 2026-08-21, **all 21 held** —
and the audit's own claim that one had become false was itself a wrong-route error: it re-asked
`search_docs(query='globalization')` as
`search_docs(query='UTF-8 supported languages…', category='globalization')`, a different query with
a filter, which is INV-194's mistake made while auditing for it. A DUE marker is a worklist item,
never a verdict.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS = REPO_ROOT / ".claude/skills/dry-run/coverage_reports.py"


def load():
    """Load the maintainer script. Under `.claude/`, so no `plugins/` import (INV-108)."""
    spec = importlib.util.spec_from_file_location("_coverage_reports", REPORTS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


COV = load()


def run(*argv):
    return subprocess.run([sys.executable, str(REPORTS)] + list(argv),
                          capture_output=True, text=True, cwd=str(REPO_ROOT))


class TheHelpersExist(unittest.TestCase):
    def test_the_module_exposes_the_split(self):
        for name in ("version_tuple", "negatives_due", "find_negatives"):
            self.assertTrue(callable(getattr(COV, name, None)),
                            "coverage_reports.py no longer exposes %s(); this file is vacuous" % name)

    def test_version_tuple_parses_and_refuses(self):
        self.assertEqual((1, 33, 0), COV.version_tuple("1.33.0"))
        self.assertEqual((1, 32, 9), COV.version_tuple("**1.32.9**"))
        self.assertIsNone(COV.version_tuple(""), "an unparseable version must be None, not a guess")
        self.assertIsNone(COV.version_tuple(None))


def row(version):
    """A marker row in find_negatives' tuple shape: (key, version, date, claim, owner, path, line)."""
    return ("k", version, "2026-01-01", "claim", "owner", "f.md", 1)


# ⛔ SYNTHETIC rows, not the live corpus, and that is the point. A first version drove these
# assertions off `find_negatives(REPO_ROOT)` — and the "infer a default version instead of
# requiring one" mutation ESCAPED, because the corpus had just been re-dated so every marker sat
# at the version the mutant inferred. A test whose verdict depends on today's corpus state cannot
# see a logic defect; these fixtures pin the logic and the corpus test below stays separate.
MIXED = [row("1.30.0"), row("1.32.9"), row("1.33.0"), row("1.34.0"), row("")]


class TheSplitIsDrivenBySuppliedVersion(unittest.TestCase):
    """The negative control the spec asks for, in both directions, on fixtures."""

    def test_a_future_version_marks_every_marker_due(self):
        due, ok = COV.negatives_due(MIXED, "99.0.0")
        self.assertEqual(len(MIXED), len(due),
                         "a version above every marker must mark them ALL due")
        self.assertEqual([], ok)

    def test_an_ancient_version_marks_only_the_unparseable_due(self):
        due, ok = COV.negatives_due(MIXED, "0.0.1")
        self.assertEqual([r[1] for r in due], [""],
                         "below every marker, only the UNPARSEABLE one may be due — an "
                         "unreadable version is not evidence of currency")
        self.assertEqual(4, len(ok))

    def test_no_version_declines_to_split(self):
        due, ok = COV.negatives_due(MIXED, None)
        self.assertEqual([], due,
                         "with no supplied version the split must NOT be attempted. Inferring a "
                         "default is the same silent-staleness defect one level down: the scan is "
                         "offline and cannot know what the live server runs.")
        self.assertEqual(len(MIXED), len(ok))
        self.assertEqual(([], list(MIXED)), COV.negatives_due(MIXED, ""),
                         "an empty version string must also decline to split")

    def test_the_boundary_is_strictly_below(self):
        """A marker recorded AT the supplied version is current, not due."""
        due, ok = COV.negatives_due(MIXED, "1.33.0")
        self.assertEqual(["1.30.0", "1.32.9", ""], [r[1] for r in due])
        self.assertEqual(["1.33.0", "1.34.0"], [r[1] for r in ok],
                         "a marker at or above the supplied version was marked due; the "
                         "comparison must be strictly-below, or every run re-asks everything")


class TheScanReachesTheRealCorpus(unittest.TestCase):
    """Separate from the logic tests, so neither can mask the other."""

    def test_markers_are_found_in_the_repository(self):
        found = COV.find_negatives(REPO_ROOT)
        self.assertGreaterEqual(
            len(found), 10,
            "only %d marker(s) found; the corpus scan is near-vacuous and the report would read "
            "clean because it saw nothing" % len(found))
        for r in found:
            self.assertTrue(COV.version_tuple(r[1]),
                            "marker at %s:%s has an unparseable server version %r — it can never "
                            "be labeled current" % (r[5], r[6], r[1]))


class TheReportSaysWhichQuestionItAnswered(unittest.TestCase):
    def test_with_a_version_it_prints_the_due_count(self):
        out = run("negatives", "--server", "1.33.0")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertRegex(out.stdout, r"markers: \d+ — \d+ DUE",
                         "the report does not print a DUE count:\n%s" % out.stdout[:600])
        self.assertIn("Re-ask each one INDIVIDUALLY", out.stdout,
                      "the report must warn against a bulk re-date — that makes every marker look "
                      "reviewed at the cost of reviewing none")

    def test_without_a_version_it_says_no_split_was_attempted(self):
        out = run("negatives")
        self.assertEqual(0, out.returncode, out.stderr)
        # ⛔ Checks no marker is LABELED due, not that the word is absent: the no-version output
        # legitimately names the flag ("pass --server … to get the DUE count"), and a bare
        # substring check failed on that instruction — asserting against the help text rather
        # than the behavior.
        self.assertNotRegex(out.stdout, r"markers: \d+ — \d+ DUE",
                            "a DUE count appeared with no supplied version, so it was inferred")
        self.assertNotRegex(out.stdout, r"(?m)^\s*DUE\s+server ",
                            "a marker was labeled DUE with no supplied version")
        self.assertIn("No --server given", out.stdout,
                      "the report must say the staleness question was NOT answered, rather than "
                      "leaving a clean-looking listing to be misread as current")


if __name__ == "__main__":
    unittest.main()
