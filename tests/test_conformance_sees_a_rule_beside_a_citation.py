"""`conformance.py`'s per-rule and since views see a rule the section-scoped count cannot.

`conformance.py rules` is the mechanical half of the audit's reverse contract, and
`implement-spec` Step 5 tells a run to check it before writing a ledger entry. Its unit is
the **enclosing section**, so a brand-new unregistered rule passes the moment it lands
anywhere near an unrelated `INV-nnn` -- and it passes more reliably as citations get denser.

⚠️ **Measured, not argued.** On 2026-08-21 a run added 26 hard-rule lines to shipped markdown
(net +25; one rule was reworded, so it counts as both an addition and a removal) and the
section-scoped count held at **1**, its session baseline, while three of those rules were on
subjects `INVARIANTS.md` covers nowhere. The audit report and two specs said **37**; the
mechanical count against the session's base commit says 26 added / 25 net, and the mechanical
count governs. That correction is itself the defect class this file guards -- a figure carried
as prose with nothing re-measuring it.

The negative control is the whole point and it is structural: a hard rule is added **beside an
unrelated citation**, and the test asserts the section-scoped count does NOT move while the
per-rule view DOES report it. A guard that only checked the per-rule view would pass against a
per-rule view that had silently become section-scoped too.

Runs `conformance.py` as a subprocess against a synthetic repo, so it asserts the shipped
behavior of the script rather than a reimplementation of its regex (stdlib only, INV-108).

Run:  python3 -m unittest discover -s tests
"""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFORMANCE = REPO_ROOT / ".claude/skills/production-readiness-audit/conformance.py"

# A section that cites an invariant for a reason unrelated to the rule added below it. This is
# the shape that hides a new rule: the citation is correct, present, and about something else.
SECTION = """# A module step

## Step 7: create the datastore

Place the file under the project root (INV-200) and source the path from the server (INV-080).

Some ordinary prose that is not a hard rule at all.
"""

# The rule under test. Bolded MUST, no citation on its own line or either neighbor.
NEW_RULE = "⛔ **The datastore's filesystem MUST be measured before the file is created.**\n"


def make_repo(root, body):
    d = root / "plugins" / "senzing-bootcamp" / "skills" / "module-02-sdk-setup"
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(body, encoding="utf-8")
    (root / "specs").mkdir(parents=True, exist_ok=True)
    (root / "specs" / "INVARIANTS.md").write_text("- **INV-200** — placement.\n",
                                                  encoding="utf-8")
    return root


def run_conformance(repo, *argv):
    proc = subprocess.run([sys.executable, str(CONFORMANCE), "--repo", str(repo)] + list(argv),
                          capture_output=True, text=True)
    return proc


class TheScriptShipsBothViews(unittest.TestCase):
    def test_per_rule_and_since_are_invocable(self):
        for argv in (["per-rule"], ["per-rule", "--uncited"], ["since", "--ref", "HEAD"]):
            with tempfile.TemporaryDirectory() as td:
                repo = make_repo(Path(td), SECTION)
                proc = run_conformance(repo, *argv)
                # `since` needs a git repo; exit 2 with a named git failure is a correct
                # refusal, not a missing subcommand. What must not happen is argparse
                # rejecting the subcommand itself.
                self.assertNotIn("invalid choice", proc.stderr,
                                 "conformance.py does not ship %r: %s" % (argv, proc.stderr))


class ARuleBesideAnUnrelatedCitation(unittest.TestCase):
    """The negative control, run in both directions in one test so they cannot drift apart."""

    def counts(self, body):
        with tempfile.TemporaryDirectory() as td:
            repo = make_repo(Path(td), body)
            sec = run_conformance(repo, "rules")
            self.assertEqual(0, sec.returncode, sec.stderr)
            m = re.search(r"(\d+) hard-rule lines, (\d+) in a section citing no invariant",
                          sec.stdout)
            self.assertIsNotNone(m, "`rules` output did not parse:\n%s" % sec.stdout)
            per = run_conformance(repo, "per-rule", "--uncited")
            self.assertEqual(0, per.returncode, per.stderr)
            p = re.search(r"(\d+) hard-rule lines, (\d+) citing no invariant at the rule itself",
                          per.stdout)
            self.assertIsNotNone(p, "`per-rule` output did not parse:\n%s" % per.stdout)
            return {"section_total": int(m.group(1)), "section_uncited": int(m.group(2)),
                    "per_total": int(p.group(1)), "per_uncited": int(p.group(2)),
                    "per_out": per.stdout}

    def test_the_section_count_is_blind_and_the_per_rule_view_is_not(self):
        before = self.counts(SECTION)
        after = self.counts(SECTION + "\n" + NEW_RULE)

        # Direction 1: the section-scoped count cannot see it. If this ever starts moving,
        # `rules` has changed unit and this file's premise -- and the spec's -- needs revisiting.
        self.assertEqual(
            before["section_uncited"], after["section_uncited"],
            "the section-scoped count MOVED for a rule added beside an unrelated citation "
            "(%d -> %d). That is a better script than the one this test was written against; "
            "re-read `conformance-rules-cannot-see-a-new-rule-beside-an-old-citation.md` "
            "before relaxing anything here."
            % (before["section_uncited"], after["section_uncited"]))
        self.assertEqual(0, after["section_uncited"],
                         "expected the citation to cover the whole section:\n%s" % after)

        # Direction 2: the per-rule view does see it, and says where.
        self.assertEqual(
            before["per_uncited"] + 1, after["per_uncited"],
            "the per-rule view did NOT report a hard rule citing no invariant at itself "
            "(%d -> %d). It has widened back toward the section scope, which reintroduces "
            "exactly the blind spot it exists to remove."
            % (before["per_uncited"], after["per_uncited"]))
        self.assertIn("module-02-sdk-setup/SKILL.md", after["per_out"],
                      "the per-rule view must name the file:line of each rule:\n%s"
                      % after["per_out"])

    def test_a_citation_on_the_rules_own_line_is_credited(self):
        """The per-rule view is narrow, not blind: a citation AT the rule counts."""
        cited = NEW_RULE.rstrip("\n").rstrip("*") + " (INV-200)**\n"
        after = self.counts(SECTION + "\n" + cited)
        before = self.counts(SECTION)
        self.assertEqual(
            before["per_uncited"], after["per_uncited"],
            "a rule citing an invariant on its own line was still counted as uncited; the "
            "per-rule window is too narrow to be usable.")
        self.assertEqual(before["per_total"] + 1, after["per_total"],
                         "the rule was not recognized as a hard rule at all")

    def test_the_adjacent_sentence_counts_but_the_section_does_not(self):
        """The window is the rule plus one non-blank line either side -- and stops there."""
        adjacent = self.counts(SECTION + "\n" + NEW_RULE + "This is required by INV-200.\n")
        distant = self.counts(SECTION + "\n" + NEW_RULE
                              + "\nUnrelated prose.\n\nMore prose.\n\nSee INV-200.\n")
        self.assertEqual(0, adjacent["per_uncited"] - self.counts(SECTION)["per_uncited"],
                         "a citation in the sentence immediately after the rule was not "
                         "credited:\n%s" % adjacent["per_out"])
        self.assertEqual(1, distant["per_uncited"] - self.counts(SECTION)["per_uncited"],
                         "a citation three paragraphs away WAS credited -- the window has "
                         "widened into section scope:\n%s" % distant["per_out"])


class TheSinceViewFiltersByRef(unittest.TestCase):
    def test_it_reports_only_hard_rules_and_only_from_shipped_markdown(self):
        proc = run_conformance(REPO_ROOT, "since", "--ref", "HEAD")
        self.assertEqual(0, proc.returncode, proc.stderr)
        m = re.search(r"(\d+) hard-rule line\(s\) added since HEAD", proc.stdout)
        self.assertIsNotNone(m, "`since` output did not parse:\n%s" % proc.stdout)
        self.assertEqual(0, int(m.group(1)),
                         "diffing against HEAD reported added rules with a clean-of-plugins "
                         "tree; the diff parse is picking up context or removed lines:\n%s"
                         % proc.stdout)

    def test_a_bad_ref_fails_loudly_rather_than_reporting_zero(self):
        proc = run_conformance(REPO_ROOT, "since", "--ref", "no-such-ref-exists-here")
        self.assertEqual(2, proc.returncode,
                         "a nonexistent ref must exit non-zero: '0 rules added' and 'the ref "
                         "was wrong' are indistinguishable otherwise (INV-110/INV-115)")
        self.assertIn("no-such-ref-exists-here", proc.stderr)


if __name__ == "__main__":
    unittest.main()
