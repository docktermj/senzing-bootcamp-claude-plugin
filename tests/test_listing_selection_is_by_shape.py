"""INV-267: a step choosing from an MCP listing selects on a property, never a position.

Two shipped steps face the same problem — an MCP tool returns a listing of snippets and the step
must pick one — and both solve it the same way:

  * `module-03-system-verification/phase1-verification.md` Step 4 (`full_pipeline`): pick the
    loading snippet that READS AN INPUT FILE, not the demo with hardcoded records; "match on the
    **shape** … never on position in the list".
  * `module-02-sdk-setup/SKILL.md` Step 9 (`initialize`): pick the snippet whose body CALLS A
    METHOD ON the engine; "a count or a position in the listing is NOT the selector, and neither
    is the filename".

Neither cited an invariant until 2026-08-23, and none existed. INV-234 governs how a call site
must *document* that a response is a listing; INV-212 governs the query vocabulary that reaches
the material. **Naming a route and selecting from its response are different acts**, and only
the first was registered — which is how the rule shipped twice with nothing binding a third site
to it.

⛔ **The rule exists because the counts move.** `full_pipeline` returned 18 snippets across three
groups on server 1.32.2 and 22 across four on 1.32.9 — a whole group appeared — while the two
snippets Step 4 names by shape stayed exactly where they were.

⚠️ **"Creates an engine" is the cautionary case, and it is why this guard checks for an EXCLUDED
near-miss rather than only for a named item.** Both `initialization/engine_priming.py` and
`initialization/abstract_factory.py` call `create_engine()`, so "the snippet that creates an
engine" — the phrase an earlier spec asked Step 9 to use — distinguishes nothing. A step that
names its pick without naming what the property rules out has not given a criterion.

Per **INV-246** the site set is derived by scanning for the rule's subject, never by listing the
two known paths: a guard given the paths certifies the sites already thought of and is blind to
the third.

Source spec: `specs/selecting-from-an-mcp-listing-by-shape-is-unregistered.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"

#: The rule's subject in shipped prose: a statement that position/count/filename is not the
#: selector. Matched on the distinctive negation rather than on a path.
RULE_SUBJECT = re.compile(
    r"(?i)never on position in the list"
    r"|(?:count or a position) in the listing is (?:\*\*)?NOT(?:\*\*)? the selector", re.M)

WINDOW_CHARS = 1400


def shipped_markdown():
    return sorted(SKILLS.glob("**/*.md"))


def flat(text):
    return re.sub(r"\s+", " ", re.sub(r"(?m)^\s*>\s?", "", text))


def selection_sites():
    """(path, window) for each shipped step stating the listing-selection rule."""
    out = []
    for path in shipped_markdown():
        text = path.read_text(encoding="utf-8")
        for match in RULE_SUBJECT.finditer(text):
            lo = max(0, match.start() - WINDOW_CHARS)
            out.append((path, flat(text[lo:match.end() + WINDOW_CHARS])))
    return out


class TheScanFindsBothKnownSites(unittest.TestCase):
    def test_at_least_two_sites_state_the_rule(self):
        found = selection_sites()
        self.assertGreaterEqual(
            len(found), 2,
            "fewer than two shipped steps state the listing-selection rule (found %d: %s). The "
            "rule is stated in Module 2 Step 9 and Module 3 Step 4; a lower count means the "
            "wording moved and this guard is checking less than it appears to"
            % (len(found), [p.name for p, _ in found]))

    def test_both_known_modules_are_among_them(self):
        names = {p.name for p, _ in selection_sites()}
        for expected in ("SKILL.md", "phase1-verification.md"):
            with self.subTest(file=expected):
                self.assertIn(
                    expected, names,
                    "%s no longer states the listing-selection rule; it is one of the two sites "
                    "this guard exists for" % expected)


class EverySiteGivesATestablePropertyAndAnExclusion(unittest.TestCase):
    def test_each_site_names_a_property_of_the_item(self):
        offenders = []
        for path, window in selection_sites():
            if not re.search(r"(?i)match on the \*{0,2}shape|pick by shape|whose body", window):
                offenders.append(path.name)
        self.assertEqual(
            [], offenders,
            "a site forbids selecting by position without naming the property to select ON: "
            "%s. Forbidding the wrong criterion is not supplying the right one" % offenders)

    def test_each_site_names_an_item_the_property_excludes(self):
        """The half that makes a criterion checkable rather than aspirational."""
        offenders = []
        for path, window in selection_sites():
            # Both sites name a concrete near-miss: `add_records.py` (hardcoded records) and
            # `abstract_factory.py` (creates an engine and never uses it).
            if not re.search(r"(?i)versus |Compare\b|not the self-contained", window):
                offenders.append(path.name)
        self.assertEqual(
            [], offenders,
            "a site names its pick without naming the plausible near-miss the property excludes: "
            "%s. 'Creates an engine' is the cautionary case — it is true of both candidates, so "
            "a criterion with no exclusion distinguishes nothing" % offenders)

    def test_each_site_rules_out_count_and_position(self):
        offenders = []
        for path, window in selection_sites():
            if not re.search(r"(?i)position", window):
                offenders.append(path.name)
        self.assertEqual([], offenders,
                         "a site does not rule out position as the selector: %s" % offenders)

    def test_each_site_cites_the_invariant_at_the_rule(self):
        """INV-183 — and the reason this spec existed at all."""
        offenders = []
        for path, window in selection_sites():
            if "INV-267" not in window:
                offenders.append(path.name)
        self.assertEqual(
            [], offenders,
            "a site states the rule without citing INV-267 at it: %s. Both sites stated this "
            "rule uncited for weeks, which is exactly how it went unregistered" % offenders)


class TheQuotedCountsAreMarkedAsIllustration(unittest.TestCase):
    """A count that reads as a check is the thing the rule is against."""

    def test_a_site_quoting_a_snippet_count_marks_it_illustrative(self):
        offenders = []
        for path, window in selection_sites():
            if re.search(r"(?i)\b(1[0-9]|2[0-9]) snippets\b", window):
                if not re.search(r"(?i)illustration|not a check to perform|indexing more",
                                 window):
                    offenders.append(path.name)
        self.assertEqual(
            [], offenders,
            "a site quotes a snippet count without marking it as illustration: %s. The counts "
            "move — 18/3 groups to 22/4 between two server versions — so an unmarked count "
            "reads as a check and breaks silently" % offenders)


class TheInvariantSaysWhatTheSitesSay(unittest.TestCase):
    def setUp(self):
        body = INVARIANTS.read_text(encoding="utf-8")
        match = re.search(r"^- \*\*INV-267\*\* — .*$", body, re.M)
        self.assertIsNotNone(match, "INV-267 is not registered in INVARIANTS.md")
        self.invariant = match.group(0)

    def test_it_requires_a_testable_property(self):
        self.assertRegex(
            self.invariant, r"(?i)property of the item",
            "INV-267 does not require the criterion be a property of the item")

    def test_it_forbids_position_length_and_filename(self):
        for forbidden in ("position", "length", "filename"):
            with self.subTest(criterion=forbidden):
                self.assertIn(
                    forbidden, self.invariant,
                    "INV-267 does not rule out %r as a selector; the filename half is what the "
                    "Module 2 walk actually used" % forbidden)

    def test_it_requires_naming_an_excluded_item(self):
        self.assertRegex(
            self.invariant, r"(?i)\*\*excludes\*\*|property excludes",
            "INV-267 does not require naming an item the property excludes")

    def test_it_distinguishes_itself_from_the_adjacent_invariants(self):
        for adjacent in ("INV-234", "INV-212"):
            with self.subTest(adjacent=adjacent):
                self.assertIn(
                    adjacent, self.invariant,
                    "INV-267 does not say how it differs from %s. Conflating them is precisely "
                    "why this rule went unregistered — a ledger entry reasoned that INV-212 "
                    "already covered it" % adjacent)

    def test_it_keeps_the_evidence_that_counts_move(self):
        self.assertRegex(
            self.invariant, r"18 snippets.{0,120}22",
            "INV-267 no longer records that the snippet count moved between server versions — "
            "that measurement is the whole argument for selecting on shape")


if __name__ == "__main__":
    unittest.main()
