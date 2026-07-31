"""`specs/DECLINED.md` is the second terminal state a spec can reach, and it must stay honest.

A spec used to have exactly one ending: implemented. `implement-spec` computed
``Unimplemented = candidates - implemented``, so a spec the maintainer ruled out stayed in the
candidate set permanently — re-offered every run, with the spec's own text arguing *for* the change
and nothing recording the argument against it. The first case was
`no-route-for-bootcampers-who-cannot-add-an-mcp-server`, declined 2026-07-31 as an architectural
decision.

The design precedent is `delegate-to-mcp-server`'s `keep-by-design` verdict, which requires a reason
for a stated cause: *"An unreasoned keep is indistinguishable from 'nobody looked', and the next run
will look again."* These tests enforce the same discipline here, plus the two integrity properties a
second ledger introduces — no spec in both, and no entry naming a file that does not exist.

⚠️ Every `##` heading in `DECLINED.md` is read as a spec name, which is why its prose uses bold
rather than headings. `test_no_declined_name_is_prose` is what catches a regression: a `## Why …`
section added to the header was counted as a declined spec the first time this ran.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "specs"
DECLINED = SPECS / "DECLINED.md"
IMPLEMENTED = SPECS / "IMPLEMENTED.md"
SKILL = REPO_ROOT / ".claude" / "skills" / "implement-spec" / "SKILL.md"

HEADING = re.compile(r"^## (.+)$", re.M)
#: The template block inside the HTML comment, which is not an entry.
PLACEHOLDER = "<spec-name>"


def headings(path):
    if not path.is_file():
        return []
    return [h.strip() for h in HEADING.findall(path.read_text(encoding="utf-8"))
            if h.strip() != PLACEHOLDER]


def entries():
    """(name, body) per declined entry, excluding the comment template."""
    text = DECLINED.read_text(encoding="utf-8")
    found = re.findall(r"^## (.+?)$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return [(n.strip(), b) for n, b in found if n.strip() != PLACEHOLDER]


class TheLedgerExists(unittest.TestCase):
    def test_the_file_ships(self):
        self.assertTrue(DECLINED.is_file(), "specs/DECLINED.md is missing")

    def test_it_has_at_least_one_entry(self):
        """Not vacuous: with no entries every check below would pass trivially."""
        self.assertTrue(entries(), "no declined entries — the checks below assert nothing")


class EveryEntryIsComplete(unittest.TestCase):
    """Reason is required for the `keep-by-design` reason; Revisit-if stops a graveyard."""

    def test_each_entry_has_a_date(self):
        for name, body in entries():
            with self.subTest(spec=name):
                self.assertRegex(body, r"- \*\*Declined:\*\*\s*\d{4}-\d{2}-\d{2}")

    def test_each_entry_names_who_decided(self):
        for name, body in entries():
            with self.subTest(spec=name):
                self.assertRegex(body, r"- \*\*Decided by:\*\*\s*\S")

    def test_each_entry_carries_a_non_empty_reason(self):
        for name, body in entries():
            with self.subTest(spec=name):
                m = re.search(r"- \*\*Reason:\*\*(.*?)(?=\n- \*\*|\Z)", body, re.S)
                self.assertIsNotNone(m, "%s has no Reason field" % name)
                self.assertGreater(
                    len(m.group(1).strip()), 40,
                    "%s's Reason is too thin to be a reason — an unreasoned decline is "
                    "indistinguishable from nobody having looked" % name,
                )

    def test_each_entry_says_what_would_reopen_it(self):
        for name, body in entries():
            with self.subTest(spec=name):
                m = re.search(r"- \*\*Revisit if:\*\*(.*?)(?=\n- \*\*|\Z)", body, re.S)
                self.assertIsNotNone(m, "%s has no Revisit-if field" % name)
                self.assertGreater(len(m.group(1).strip()), 10,
                                   "%s must name a trigger or say 'nothing foreseeable'" % name)


class TheTwoLedgersAgree(unittest.TestCase):
    def test_no_spec_is_both_implemented_and_declined(self):
        both = sorted(set(headings(DECLINED)) & set(headings(IMPLEMENTED)))
        self.assertEqual(
            [], both,
            "spec(s) in both ledgers — a spec has one terminal state, and discovery would "
            "subtract it twice while a reader cannot tell what happened: %s" % both,
        )

    def test_every_declined_name_resolves_to_a_spec_file(self):
        missing = [n for n in headings(DECLINED) if not (SPECS / f"{n}.md").is_file()]
        self.assertEqual(
            [], missing,
            "DECLINED.md names spec file(s) that do not exist — the decision's reasoning is "
            "unreachable: %s" % missing,
        )

    def test_no_declined_name_is_prose(self):
        """Every `##` here is parsed as a spec name, so a prose heading becomes a phantom entry.

        This fired on the first run: a `## Why every entry needs a reason` section in the header
        was counted as a declined spec, reporting 2 where there was 1.
        """
        for name in headings(DECLINED):
            with self.subTest(heading=name):
                self.assertTrue(
                    (SPECS / f"{name}.md").is_file(),
                    "%r is a prose heading, not a spec — use bold text instead, or it is "
                    "counted as a declined spec" % name,
                )

    def test_the_declined_spec_file_is_left_in_place(self):
        """Declining never archives or deletes: the analysis is why the call could be made."""
        for name in headings(DECLINED):
            with self.subTest(spec=name):
                self.assertTrue((SPECS / f"{name}.md").is_file())
                self.assertFalse((SPECS / "archive" / f"{name}.md").is_file(),
                                 "%s was archived; a declined spec stays in specs/" % name)


class TheSkillKnowsAboutIt(unittest.TestCase):
    """A ledger nothing reads is a file, not a mechanism."""

    def setUp(self):
        self.text = SKILL.read_text(encoding="utf-8")

    def test_step_1_subtracts_the_declined_set(self):
        flat = " ".join(self.text.split())
        self.assertIn("candidates − implemented − declined", flat,
                      "Step 1 still computes only candidates − implemented, so a declined "
                      "spec is re-offered every run")

    def test_declined_md_is_listed_as_a_meta_file(self):
        self.assertRegex(self.text, r"`DECLINED\.md`\s*—")

    def test_it_forbids_declining_unilaterally(self):
        flat = " ".join(self.text.split())
        self.assertRegex(flat, r"(?i)Never decline a spec on your own initiative")

    def test_it_requires_a_reason_and_a_revisit_condition(self):
        flat = " ".join(self.text.split())
        self.assertIn("**Reason:**", flat)
        self.assertIn("**Revisit if:**", flat)

    def test_it_says_the_spec_file_stays_put(self):
        flat = " ".join(self.text.split())
        self.assertRegex(flat, r"(?i)Leave the spec file where it is")

    def test_it_preserves_dedup_visibility(self):
        """A declined spec must still be found by feedback triage, or the next entry on the
        same subject produces a duplicate spec."""
        flat = " ".join(self.text.split())
        self.assertRegex(flat, r"(?i)deduplication|deduplicat")


class TheCensusSeparatesTheTwoStates(unittest.TestCase):
    """`citations.py` was the second consumer: it reported declined specs as unimplemented."""

    def test_declined_is_a_meta_spec(self):
        src = (REPO_ROOT / ".claude" / "skills" / "compact-dev-environment"
               / "citations.py").read_text(encoding="utf-8")
        self.assertRegex(src, r'META_SPECS = \{[^}]*"DECLINED"',
                         "DECLINED.md would be counted as a spec file by the census")

    def test_the_census_reports_them_apart(self):
        import subprocess
        import sys
        proc = subprocess.run(
            # `--repo` is a top-level argument and must precede the subcommand.
            [sys.executable,
             str(REPO_ROOT / ".claude/skills/compact-dev-environment/citations.py"),
             "--repo", str(REPO_ROOT), "census", "--area", "specs"],
            capture_output=True, text=True,
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("declined (decided not to build)", proc.stdout)
        self.assertIn("genuinely unimplemented", proc.stdout)
        m = re.search(r"declined \(decided not to build\): (\d+)", proc.stdout)
        self.assertIsNotNone(m)
        self.assertEqual(len(headings(DECLINED)), int(m.group(1)),
                         "the census's declined count disagrees with the ledger")

    def test_the_unimplemented_count_actually_excludes_the_declined(self):
        """Printing both labels is not the same as subtracting one from the other.

        An earlier version asserted only that both lines appeared and that the declined
        count was right — so reverting the subtraction (`specs - headings - declined` back
        to `specs - headings`) left every assertion passing while the census again reported
        settled work as outstanding. Assert the arithmetic, not the labels.
        """
        import subprocess
        import sys
        proc = subprocess.run(
            [sys.executable,
             str(REPO_ROOT / ".claude/skills/compact-dev-environment/citations.py"),
             "--repo", str(REPO_ROOT), "census", "--area", "specs"],
            capture_output=True, text=True,
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        not_in_ledger = int(re.search(r"spec files not in ledger\s*: (\d+)", proc.stdout).group(1))
        declined = int(re.search(r"declined \(decided not to build\): (\d+)", proc.stdout).group(1))
        outstanding = int(re.search(r"genuinely unimplemented\s*: (\d+)", proc.stdout).group(1))
        self.assertGreater(declined, 0, "no declined specs — this check would be vacuous")
        self.assertEqual(
            not_in_ledger - declined, outstanding,
            "genuinely-unimplemented (%d) is not 'not in ledger' (%d) minus declined (%d) — the "
            "census is counting settled decisions as outstanding work"
            % (outstanding, not_in_ledger, declined),
        )


if __name__ == "__main__":
    unittest.main()
