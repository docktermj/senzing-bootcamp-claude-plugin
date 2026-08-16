"""The production-readiness audit's lead generators run, and report what they exist for.

`.claude/skills/production-readiness-audit/conformance.py` backs the audit that enforces
INV-003 and INV-004 — the only two invariants no test can hold, because they are
properties of the whole rather than of any one file.

Like `dry-run`'s `coverage_reports.py`, none of these scans can be a failing test: a hit
in any of them is usually legitimate (a rule deliberately restated at the step it
governs is INV-183, not redundancy). They are reports. That makes them exactly the kind
of apparatus that rots unnoticed — nothing fails when a report stops reporting — so the
script is *executed* here rather than asserted present, the discipline INV-175 settled
for shipped snippets.

Each scan is checked against a **fixture tree whose answer is known**, not only against
live output, because "found 16" tells you nothing about whether 16 is right. The live
repo is then used only for not-vacuous guards and for properties that must hold of it.

Run:  python3 -m unittest discover -s tests
"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = (REPO_ROOT / ".claude" / "skills" / "production-readiness-audit"
          / "conformance.py")

SCANS = ("rules", "duplication", "enumerations", "size")


def run(scan, repo, cwd=None, extra=()):
    """Run one scan against `repo`, returning (returncode, stdout, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(repo), scan, *extra],
        capture_output=True, text=True, cwd=str(cwd or REPO_ROOT),
    )
    return proc.returncode, proc.stdout, proc.stderr


def fixture(tmp, files, invariants="- **INV-001** — A rule.\n"):
    """A minimal repo the script can be pointed at. `files` maps relpath -> text."""
    root = Path(tmp)
    (root / "specs").mkdir(parents=True, exist_ok=True)
    (root / "specs" / "INVARIANTS.md").write_text(invariants, encoding="utf-8")
    plugin = root / "plugins" / "senzing-bootcamp"
    for name, body in files.items():
        p = plugin / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    plugin.mkdir(parents=True, exist_ok=True)
    return root


class TestTheScansRun(unittest.TestCase):
    def test_the_script_ships(self):
        self.assertTrue(SCRIPT.is_file(), "missing: %s" % SCRIPT)

    def test_every_scan_runs_from_an_unrelated_directory_and_exits_zero(self):
        """The audit workflows run from a scratch project, not the repo root."""
        with tempfile.TemporaryDirectory() as tmp:
            for scan in SCANS + ("all",):
                with self.subTest(scan=scan):
                    code, out, err = run(scan, REPO_ROOT, cwd=tmp)
                    self.assertEqual(0, code, "%s exited %d; stderr:\n%s"
                                     % (scan, code, err))
                    self.assertTrue(out.strip(), "%s produced no output" % scan)

    def test_a_wrong_repo_fails_loudly_rather_than_reporting_a_clean_sweep(self):
        """`0 findings` and `0 files read` are indistinguishable in the output.

        This is the INV-110/INV-115 shape: an empty result that reads as a pass is worse
        than an error, because the run records a clean bill of health it never earned.
        """
        with tempfile.TemporaryDirectory() as tmp:
            for scan in SCANS:
                with self.subTest(scan=scan):
                    code, _out, err = run(scan, tmp)
                    self.assertEqual(2, code, "%s accepted a repo with no plugin" % scan)
                    self.assertIn("wrong --repo", err)

    def test_no_subcommand_prints_help_and_exits_zero(self):
        proc = subprocess.run([sys.executable, str(SCRIPT)],
                              capture_output=True, text=True)
        self.assertEqual(0, proc.returncode)
        for scan in SCANS:
            self.assertIn(scan, proc.stdout)


class TestTheReverseDirectionScan(unittest.TestCase):
    """`rules` is the half no other skill does: a plugin rule with no invariant."""

    UNCITED = (
        "# A heading\n\n"
        "⛔ **The loader MUST refuse an unregistered source.**\n\n"
        "Ordinary prose that merely says something must happen.\n"
    )
    CITED = (
        "# A heading\n\n"
        "Governed by INV-001.\n\n"
        "⛔ **The loader MUST refuse an unregistered source.**\n"
    )

    def hits(self, body):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixture(tmp, {"skills/m/SKILL.md": body})
            _code, out, _err = run("rules", root)
        return out

    def test_a_hard_rule_with_no_invariant_in_its_section_is_reported(self):
        out = self.hits(self.UNCITED)
        self.assertIn("skills/m/SKILL.md", out)
        self.assertIn("refuse an unregistered source", out)

    def test_the_same_rule_is_not_reported_when_its_section_cites_one(self):
        """Section scope, not a line window — a citation 30 lines up still covers it."""
        out = self.hits(self.CITED)
        self.assertNotIn("skills/m/SKILL.md", out)

    def test_bare_prose_must_is_not_treated_as_a_hard_rule(self):
        """Including it took the candidate list from 16 to 202, which no one reads."""
        out = self.hits("# H\n\nThe file must exist before the step runs.\n")
        self.assertNotIn("skills/m", out)

    def test_a_citation_in_a_later_section_does_not_cover_an_earlier_rule(self):
        body = ("# One\n\n⛔ **MUST refuse an unregistered source.**\n\n"
                "# Two\n\nGoverned by INV-001.\n")
        self.assertIn("refuse an unregistered source", self.hits(body))

    def test_the_live_scan_is_not_vacuous(self):
        _code, out, _err = run("rules", REPO_ROOT)
        m = re.search(r"(\d+) hard-rule lines", out)
        self.assertIsNotNone(m, "the summary line is gone:\n%s" % out[-400:])
        self.assertGreater(int(m.group(1)), 50,
                           "the plugin's ⛔/MUST convention stopped being detected")


class TestTheDuplicationScan(unittest.TestCase):
    """Where "one rule, four sites, fixed in one" hides."""

    PASSAGE = ("every screenshot the visualization capture produced must reach the "
               "recap document without exception at all")

    def test_a_passage_in_two_files_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixture(tmp, {"skills/a.md": "# A\n\n" + self.PASSAGE + "\n",
                                 "skills/b.md": "# B\n\n" + self.PASSAGE + "\n"})
            _code, out, _err = run("duplication", root)
        self.assertIn("skills/a.md", out)
        self.assertIn("skills/b.md", out)

    def test_a_passage_in_one_file_only_is_not_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixture(tmp, {"skills/a.md": "# A\n\n" + self.PASSAGE + "\n",
                                 "skills/b.md": "# B\n\nsomething entirely different\n"})
            _code, out, _err = run("duplication", root)
        self.assertIn("0 repeated passages", out)

    def test_emphasis_and_invariant_ids_do_not_defeat_the_match(self):
        """The same sentence bolded in one place and citing an ID in the other is a match."""
        with tempfile.TemporaryDirectory() as tmp:
            root = fixture(tmp, {
                "skills/a.md": "# A\n\n**" + self.PASSAGE + "**\n",
                "skills/b.md": "# B\n\n" + self.PASSAGE + " (INV-146)\n",
            })
            _code, out, _err = run("duplication", root)
        self.assertNotIn("0 repeated passages", out)


class TestTheEnumerationScan(unittest.TestCase):
    """Enumerations are what go stale — an invariant listing members, not stating one."""

    def signals(self, statement):
        """Return the signal labels the scan attached to a one-invariant fixture.

        Asserting only that the ID was flagged is too weak: "is exactly six" trips both
        the exact-count and closed-list signals, so a test written that way passes with
        exact-count deleted. It did — the mutation was caught only after this changed.
        """
        inv = "- **INV-001** — %s\n" % statement
        with tempfile.TemporaryDirectory() as tmp:
            root = fixture(tmp, {"skills/a.md": "# A\n"}, invariants=inv)
            _code, out, _err = run("enumerations", root)
        m = re.search(r"^   INV-001  \[(.+?)\]", out, re.M)
        return [s.strip() for s in m.group(1).split(",")] if m else []

    def test_an_exact_count_is_flagged_as_an_exact_count(self):
        """Worded to trip exact-count ONLY — "carries exactly", not "is exactly"."""
        self.assertEqual(["exact count"],
                         self.signals("Each section carries exactly four subsections."))

    def test_every_closed_list_phrase_is_flagged(self):
        """One case per alternative. Covering only one lets the others be deleted.

        That happened: a mutation dropping `is exactly`/`the following` escaped, because
        the single case used `consists of` and nothing exercised the rest.
        """
        for statement in (
            "The set consists of the tabs named below.",
            "The set is exactly the tabs named below.",
            "The set is precisely the tabs named below.",
            "The step MUST cover the following artifacts.",
            "The step MUST cover these and no other artifacts.",
            "The step MUST cover only these artifacts.",
        ):
            with self.subTest(statement=statement):
                self.assertIn("closed list", self.signals(statement))

    def test_a_series_of_three_literals_is_flagged_as_a_comma_series(self):
        self.assertEqual(["comma series"],
                         self.signals("Keep `_A`, `_B` and `_C` equal to the source."))

    def test_a_series_written_with_oxford_commas_is_also_flagged(self):
        self.assertEqual(["comma series"],
                         self.signals("Keep `_A`, `_B`, `_C` equal to the source."))

    def test_two_literals_are_not_a_series(self):
        """`A` and `B` is a pair, not an enumeration — flagging it would drown the report."""
        self.assertEqual([], self.signals("Keep `_A` and `_B` equal to the source."))

    def test_a_plain_property_is_not_flagged(self):
        self.assertEqual([], self.signals("The SBCP MUST be programming-language agnostic."))

    def test_every_id_it_reports_is_defined_in_the_real_invariants_file(self):
        _code, out, _err = run("enumerations", REPO_ROOT)
        defined = set(re.findall(r"\*\*(INV-\d{3})\*\*",
                                 (REPO_ROOT / "specs" / "INVARIANTS.md")
                                 .read_text(encoding="utf-8")))
        reported = set(re.findall(r"^   (INV-\d{3})  \[", out, re.M))
        self.assertTrue(reported, "the scan reported nothing — it has gone vacuous")
        self.assertEqual(set(), reported - defined,
                         "reported IDs that are not defined: %s" % (reported - defined))


class TestTheSizeScan(unittest.TestCase):
    def test_the_word_total_matches_an_independent_recount(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixture(tmp, {"skills/a.md": "one two three four five\n",
                                 "docs/b.md": "six seven\n"})
            _code, out, _err = run("size", root)
        self.assertIn("2 files, 7 words", out)

    def test_it_refuses_to_present_a_target(self):
        """A size report that reads as a budget invites cutting rationale to hit it."""
        _code, out, _err = run("size", REPO_ROOT)
        self.assertIn("not a target", out)
        self.assertIn("rationale", out)


class TestTheSkillDocumentsWhatTheScansCannotDo(unittest.TestCase):
    """The scans are lead generators; a run that reports their counts has run a grep."""

    def setUp(self):
        self.skill = (SCRIPT.parent / "SKILL.md").read_text(encoding="utf-8")

    def test_the_skill_ships(self):
        self.assertTrue((SCRIPT.parent / "SKILL.md").is_file())

    def test_it_says_the_scans_are_leads_not_verdicts(self):
        flat = " ".join(self.skill.split())
        self.assertIn("lead generators, not verdicts", flat)

    def test_it_routes_the_conversational_invariants_to_dry_run(self):
        """Reading cannot establish them, and letting them pass silently is a false pass."""
        flat = " ".join(self.skill.split())
        self.assertIn("dry-run", flat)
        self.assertRegex(flat, r"(?i)conversational invariants are out of scope")

    def test_it_forbids_cutting_rationale_for_concision(self):
        flat = " ".join(self.skill.split())
        self.assertRegex(flat, r"(?i)never cut rationale")

    def test_it_states_that_concision_is_not_yet_an_invariant(self):
        """INV-003 says consistent/coherent/complete; reading concision into it is wrong."""
        flat = " ".join(self.skill.split())
        self.assertRegex(flat, r"(?i)concision is not currently an invariant")

    def test_it_names_both_directions_of_the_invariant_check(self):
        flat = " ".join(self.skill.split())
        self.assertIn("Forward", flat)
        self.assertIn("Reverse", flat)


if __name__ == "__main__":
    unittest.main()
