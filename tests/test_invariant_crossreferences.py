"""Invariants that only make sense together must say so, in both directions.

Three pairs were found on 2026-07-31 stating requirements that interact — one constraining
another, one bounding another, one scoping a third — with **no cross-reference between them**.
Each was reconcilable by a careful reader and misleading to a fast one, and in every case the
resolution existed only in code comments or in the finder's head:

- **INV-162 ↔ INV-193.** INV-162 requires an `embedded N of M` count; INV-193 forbids exactly
  that shape as completeness evidence and its worked example *is* that count. The generator
  was already correct (`generate_recap_pdf.py` routes coverage to capture's external
  manifest), so the constraint lived in Python comments that a server generated in another
  language never reads (INV-002/INV-090).
- **INV-048 ↔ INV-110.** INV-048 says the recap PDF "is **always** created"; INV-110 requires
  writing no file and exiting non-zero on structural mismatch. Shipped behaviour is INV-110's.
- **INV-002 → INV-052/INV-108/INV-090.** INV-002 stated language-agnosticism unqualified while
  two invariants mandate Python. The apparatus-versus-bootcamper-artifact distinction the
  ruleset actually operates on was written nowhere.

These are prose assertions, which this repo normally avoids in favour of behavioural ones —
justified here because the artifact under test *is* prose, and its defect mode is a later
edit trimming the reconciliation back out. Each asserts the requirement, not a phrase: a
reworded note that still carries the link and the substance passes.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"


def bodies():
    """{'INV-nnn': single-line body}, emphasis stripped and whitespace collapsed."""
    text = INVARIANTS.read_text(encoding="utf-8")
    pairs = re.findall(r"^- \*\*(INV-\d{3})\*\* — (.+?)(?=\n- \*\*INV-|\n##|\Z)",
                       text, re.M | re.S)
    return {k: re.sub(r"\s+", " ", v.replace("**", "")) for k, v in pairs}


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_invariants_parse(self):
        found = bodies()
        self.assertGreater(len(found), 150, "the invariant parser has drifted")
        for ident in ("INV-002", "INV-048", "INV-110", "INV-162", "INV-193"):
            self.assertIn(ident, found)


class TheLossCountIsNotACompletenessMeasure(unittest.TestCase):
    """INV-162 ↔ INV-193. A self-derived denominator cannot see what was never referenced."""

    def setUp(self):
        self.b = bodies()

    def test_inv162_points_at_inv193(self):
        self.assertIn("INV-193", self.b["INV-162"],
                      "INV-162 requires the count INV-193 constrains and must name it")

    def test_inv193_points_at_inv162(self):
        self.assertIn("INV-162", self.b["INV-193"],
                      "INV-193 constrains INV-162's count and must name it")

    def test_inv162_says_the_count_is_not_completeness_evidence(self):
        body = self.b["INV-162"].lower()
        self.assertRegex(body, r"must not be presented as evidence|not .{0,30}completeness",
                         "INV-162 must say its count is not completeness evidence")

    def test_inv162_names_where_a_real_denominator_comes_from(self):
        """Saying "not completeness" without saying what is leaves the reader stuck."""
        self.assertRegex(self.b["INV-162"].lower(), r"outside the artifact|external")

    def test_inv162_still_requires_the_count(self):
        """The loss signal is the whole reason INV-162 exists; constraining it must not
        become removing it — a recap once lost all six screenshots at 99% retention."""
        self.assertRegex(self.b["INV-162"], r"(?i)MUST report an embedded-of-referenced count")

    def test_the_skipped_route_is_named_for_when_no_external_count_exists(self):
        self.assertIn("INV-163", self.b["INV-162"])


class AlwaysCreatedHasExactlyOneException(unittest.TestCase):
    """INV-048 ↔ INV-110. "Always" is load-bearing; the boundary must be written, not the
    word removed."""

    def setUp(self):
        self.b = bodies()

    def test_inv048_points_at_inv110(self):
        self.assertIn("INV-110", self.b["INV-048"])

    def test_inv110_points_at_inv048(self):
        self.assertIn("INV-048", self.b["INV-110"])

    def test_inv048_still_says_always(self):
        """Four invariants cite INV-048 for its non-blocking sense; scoping it must not
        weaken it."""
        self.assertRegex(self.b["INV-048"], r"(?i)\bis\b.{0,12}always.{0,12}created")

    def test_inv048_names_the_invariants_that_rely_on_its_non_blocking_sense(self):
        for ident in ("INV-129", "INV-157", "INV-163", "INV-173"):
            with self.subTest(relies=ident):
                self.assertIn(ident, self.b["INV-048"])

    def test_the_named_reliers_really_do_cite_inv048(self):
        """A criterion that names a second consumer is checked against that consumer
        (INV-182) — otherwise this test pins a claim nobody verified."""
        for ident in ("INV-129", "INV-157", "INV-163", "INV-173"):
            with self.subTest(relier=ident):
                self.assertIn("INV-048", self.b[ident],
                              "%s is named as relying on INV-048 but does not cite it" % ident)

    def test_inv110_calls_the_refusal_the_sole_exception(self):
        self.assertRegex(self.b["INV-110"].lower(), r"\bone case\b|sole exception|only case")

    def test_the_retention_half_stays_non_blocking(self):
        self.assertRegex(self.b["INV-110"], r"(?i)warn, render,? and exit 0|warn, render, exit 0")


class LanguageAgnosticismNamesItsScope(unittest.TestCase):
    """INV-002. Unqualified, it reads as forbidding the Python hooks INV-052 mandates."""

    def setUp(self):
        self.b = bodies()

    def test_it_still_states_the_requirement(self):
        self.assertRegex(self.b["INV-002"], r"(?i)MUST be programming-language agnostic")

    def test_it_names_what_is_bound(self):
        self.assertRegex(self.b["INV-002"].lower(),
                         r"builds, runs, or takes away|bootcamper builds")

    def test_it_names_what_is_exempt_and_why(self):
        for ident in ("INV-052", "INV-108", "INV-090"):
            with self.subTest(names=ident):
                self.assertIn(ident, self.b["INV-002"])

    def test_it_states_the_boundary_test(self):
        """The half with teeth: a rule reaching generated code only via the Python
        reference violates INV-002 even though the reference is exempt."""
        body = self.b["INV-002"].lower()
        self.assertIn("any-language contract", body)
        self.assertRegex(body, r"never only in a python reference|solely through the reference")

    def test_it_cites_the_defects_that_prove_the_boundary(self):
        for ident in ("INV-164", "INV-190"):
            with self.subTest(names=ident):
                self.assertIn(ident, self.b["INV-002"])

    def test_the_cited_defects_really_bind_any_language(self):
        """Same INV-182 discipline: check the consumer, do not assume it."""
        for ident in ("INV-164", "INV-190"):
            with self.subTest(cited=ident):
                self.assertRegex(self.b[ident], r"(?i)any.{0,3}language")


class AnInertCaptureIsCaptionedNeverOmitted(unittest.TestCase):
    """INV-123 ↔ INV-146. The omission branch INV-146 had already made unavailable.

    Added after a mutation escaped: the shipped-guidance sweep in
    `test_screenshot_retention_and_order.py` scans `plugins/` and never reads the ruleset, so
    putting "or the image MUST be omitted" back into INV-123 broke nothing. The invariant's own
    text needs its own guard.
    """

    def setUp(self):
        self.b = bodies()

    def operative(self, ident):
        """The requirement itself, without the dated clarification note.

        A note recording an in-place edit must quote the wording it replaced, so a naive
        "the forbidden phrase is absent" check fires on the note's own history. Cut at the
        first ⚠️ marker, which is how this file opens every such note.
        """
        body = self.b[ident]
        marker = body.find("(⚠️")
        operative = body[:marker] if marker > 0 else body
        self.assertGreater(len(operative), 80,
                           "%s's operative text could not be separated from its note" % ident)
        return operative

    def test_inv123_offers_no_omission(self):
        self.assertNotRegex(
            self.operative("INV-123"),
            r"(?i)\bor\s+the\s+image\s+(?:MUST\s+)?be\s+omitted|\bor\s+(?:omit|drop)\s+it\b",
            "INV-123 offers omission again; INV-146 permits deleting only a same-tab duplicate",
        )

    def test_inv123_still_requires_the_caption_to_say_so(self):
        self.assertRegex(self.b["INV-123"], r"(?i)the caption MUST say so")

    def test_inv123_points_at_inv146(self):
        self.assertIn("INV-146", self.b["INV-123"])

    def test_inv146_records_that_it_closed_the_branch(self):
        self.assertIn("INV-123", self.b["INV-146"])

    def test_inv146_is_unchanged_in_substance(self):
        """Closing INV-123's branch must not have relaxed INV-146 itself."""
        body = self.b["INV-146"]
        self.assertRegex(body, r"(?i)Every screenshot a visualization capture produced MUST "
                               r"reach the recap")
        self.assertRegex(body, r"(?i)only a true duplicate")


class TheClarificationsAreDatedAndDisclaimMeaningChange(unittest.TestCase):
    """Rule 2 allows in-place edits only to clarify. An undated edit that changed meaning
    silently is the one thing the maintenance rules forbid outright."""

    def test_each_edited_invariant_carries_a_date_and_a_no_meaning_change_note(self):
        b = bodies()
        for ident in ("INV-002", "INV-017", "INV-048", "INV-050", "INV-107",
                      "INV-110", "INV-123", "INV-162"):
            with self.subTest(invariant=ident):
                self.assertRegex(b[ident], r"20\d\d-\d\d-\d\d",
                                 "%s's clarification is undated" % ident)
                self.assertRegex(b[ident].lower(), r"no meaning change",
                                 "%s must state that the edit changed no meaning" % ident)


class AWidenedScopeIsAnnouncedOnTheNarrowerRule(unittest.TestCase):
    """INV-107 → INV-184 and INV-050 → INV-202.

    When a later invariant widens an earlier one's scope, the earlier one is the rule an
    implementer reaches *first* — INV-107 names the actual palette constants, and INV-050
    holds the tree itself. Both were left with no pointer forward, so each read as complete
    while binding less than the ruleset actually requires. INV-107 is the sharper case: it
    is the exact wording that let `generate_discoveries_pdf.py` drift out of scope, which is
    why INV-184 exists at all.

    Asserted as the requirement, not a phrase — a reworded note carrying the link and the
    substance passes (2026-08-12).
    """

    def setUp(self):
        self.b = bodies()

    def test_inv107_points_at_inv184(self):
        self.assertIn("INV-184", self.b["INV-107"],
                      "INV-107 enumerates two generators; INV-184 widened it to every "
                      "generator and INV-107 must route the reader there")

    def test_inv107_says_the_rule_is_not_limited_to_the_files_it_names(self):
        self.assertRegex(self.b["INV-107"].lower(),
                         r"every.{0,40}generator|belongs to the pattern|enumerates two")

    def test_inv107_still_binds_its_own_constants(self):
        """Routing forward must not read as retirement: 15 citations rely on this rule."""
        self.assertRegex(self.b["INV-107"], r"(?i)MUST equal the values")
        self.assertRegex(self.b["INV-107"].lower(), r"nothing here is superseded|still bind")

    def test_inv050_points_at_inv202(self):
        self.assertIn("INV-202", self.b["INV-050"],
                      "INV-202 binds every edit to INV-050's tree and INV-050 must say so")

    def test_inv050_states_the_annotate_rather_than_delete_rule(self):
        """The half an editor gets wrong: deleting a dead entry looks like tidying."""
        self.assertRegex(self.b["INV-050"].lower(),
                         r"rather than being deleted|rather than be deleted|gain the annotation")

    def test_the_named_successors_really_do_generalize_the_narrower_rule(self):
        """INV-182 discipline: a criterion naming a second consumer is checked against it."""
        self.assertIn("INV-107", self.b["INV-184"],
                      "INV-184 is cited as generalizing INV-107 but does not name it")
        self.assertIn("INV-050", self.b["INV-202"],
                      "INV-202 is cited as binding INV-050's tree but does not name it")


if __name__ == "__main__":
    unittest.main()
