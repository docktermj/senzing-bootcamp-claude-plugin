"""INV-265: a check that matches nothing has not passed — it has not run.

`module-03b-truthset-visualization/phase2-close.md`'s pre-advancement self-check compares the
tab identifiers in the saved snapshot against the running server's. On a dry run the first
attempt matched `data-tab="…"`, found **zero in both files**, and reported *"tab sets match:
True"* — `data-tab` appears nowhere in the generated app. A comparison of two empty sets
reported agreement.

⛔ **The failure mode is silence, which is why INV-265 exists rather than a note.** An emptied
input produces a passing check indistinguishable from a correct one, and every instance on
record was found by accident:

  * the tab comparison above;
  * `test_every_named_script_exists` and `test_no_hook_parses_its_payload_as_source`, which
    keyed off `resolved_args()` and passed while asserting nothing once the hook scripts moved
    into `command` — the tell was a 0.000s run that spawned no subprocess;
  * `conformance.py rules` reading clean while its pattern missed 145 mid-line rules;
  * a malformed ledger heading being *absent* rather than invalid to `(?m)^## (\\S+)$`, so every
    entry-level guard skipped it in silence.

⛔ **This guard asserts the shipped RULE is stated with both halves.** It cannot assert that a
live turn constructs its checks correctly — that is a conversational outcome and belongs to
`dry-run` phase 3. What it holds is that the instruction cannot be followed while still
reporting agreement on nothing.

Per **INV-246** the site set is derived by scanning shipped prose for the rule's subject rather
than naming `phase2-close.md`, so a second check written to the same rule is covered without
editing this file. Today the scan finds one site; the anti-vacuity class below fails if it finds
none.

Source spec: `specs/a-check-that-matches-nothing-must-not-report-agreement.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"

#: The rule's subject, in shipped prose. Matched on the distinctive half — a check that finds
#: nothing — rather than on a file path (INV-246).
RULE_SUBJECT = re.compile(
    r"(?i)finds ZERO [a-z]+ on both sides|matches nothing|empty match", re.M)

#: How much prose around a hit forms the rule for assertion purposes. A character window: a
#: line-count window does not survive reflowing, which cost two escaped controls earlier in
#: this repo's history.
WINDOW_CHARS = 900


def shipped_markdown():
    return sorted(SKILLS.glob("**/*.md"))


def flat(text):
    """Whitespace-flattened, blockquote prefixes stripped — the rule is inside a blockquote."""
    return re.sub(r"\s+", " ", re.sub(r"(?m)^\s*>\s?", "", text))


def rule_sites():
    """(path, window) for each shipped passage stating the empty-match rule."""
    out = []
    for path in shipped_markdown():
        text = path.read_text(encoding="utf-8")
        for match in RULE_SUBJECT.finditer(text):
            lo = max(0, match.start() - WINDOW_CHARS)
            window = flat(text[lo:match.end() + WINDOW_CHARS])
            # Only a passage about CHECK CONSTRUCTION. `NAME_FULL matches nothing` is about a
            # Senzing search returning no rows (INV-164's subject), not about a vacuous check.
            if re.search(r"(?i)has not\s*run|broken check|non-zero count|certifies", window):
                out.append((path, window))
    return out


class TheScanFindsTheRule(unittest.TestCase):
    def test_at_least_one_shipped_site_states_it(self):
        found = rule_sites()
        self.assertGreater(
            len(found), 0,
            "no shipped file states the empty-match rule — either it was removed or this "
            "guard's subject pattern no longer matches it, and either way the guard is "
            "inspecting nothing")


class EverySiteStatesBothHalves(unittest.TestCase):
    """Stating the hazard without the guard against it leaves the reader where they started."""

    def test_each_site_requires_a_non_zero_count_before_comparing(self):
        offenders = []
        for path, window in rule_sites():
            if not re.search(r"(?i)non-zero count on both sides", window):
                offenders.append(path.name)
        self.assertEqual(
            [], offenders,
            "a site states the empty-match hazard without requiring a non-zero count on both "
            "sides before comparing: %s. The hazard alone is a caution; the floor is what "
            "makes it actionable" % offenders)

    def test_each_site_says_an_empty_match_is_not_agreement(self):
        offenders = []
        for path, window in rule_sites():
            if not re.search(r"(?i)has not\s*passed|broken check rather than agreement", window):
                offenders.append(path.name)
        self.assertEqual(
            [], offenders,
            "a site requires a non-zero count without saying that an empty match is a FAILED "
            "check rather than agreement: %s. That is the half that was actually wrong — the "
            "comparison returned True" % offenders)

    def test_each_site_cites_the_invariant_at_the_rule(self):
        """INV-183: a rule binding a step must be lookup-able at that step."""
        offenders = []
        for path, window in rule_sites():
            if "INV-265" not in window:
                offenders.append(path.name)
        self.assertEqual(
            [], offenders,
            "a site states the rule without citing INV-265 at it: %s. A rule with no ID is one "
            "a later editor cannot look up and will 'tidy' away" % offenders)


class TheInvariantSaysWhatTheSitesSay(unittest.TestCase):
    """A registered rule and a shipped rule that drift apart is the reverse-contract defect."""

    def setUp(self):
        body = INVARIANTS.read_text(encoding="utf-8")
        match = re.search(r"^- \*\*INV-265\*\* — .*$", body, re.M)
        self.assertIsNotNone(match, "INV-265 is not registered in INVARIANTS.md")
        self.invariant = match.group(0)

    def test_it_requires_a_non_empty_input(self):
        self.assertRegex(
            self.invariant, r"(?i)non-empty",
            "INV-265 does not require the input be established non-empty")

    def test_it_forbids_reporting_an_empty_match_as_a_pass(self):
        self.assertRegex(
            self.invariant, r"(?i)never as agreement",
            "INV-265 does not say an empty match must not be reported as agreement")

    def test_it_covers_both_sides_of_a_comparison(self):
        self.assertRegex(
            self.invariant, r"(?i)\*\*both\*\* sides|both sides MUST be asserted",
            "INV-265 does not require both sides of a comparison be asserted non-empty — the "
            "tab check compared two empty sets, so one side would not have caught it")

    def test_it_covers_a_test_whose_assertion_can_be_vacuous(self):
        self.assertRegex(
            self.invariant, r"(?i)anti-vacuity",
            "INV-265 does not extend to a test that can be satisfied by an empty input, which "
            "is where four of the five recorded instances happened")

    def test_it_keeps_its_evidence(self):
        """The 'observed:' narrative is what stops a rule being re-argued (audit guardrail)."""
        for evidence in ("data-tab", "0.000s", "145 mid-line"):
            with self.subTest(evidence=evidence):
                self.assertIn(
                    evidence, self.invariant,
                    "INV-265 no longer names %r among the instances that produced it; without "
                    "the evidence the rule reads as theory" % evidence)


if __name__ == "__main__":
    unittest.main()
