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


class TheClarificationsAreDatedAndDisclaimMeaningChange(unittest.TestCase):
    """Rule 2 allows in-place edits only to clarify. An undated edit that changed meaning
    silently is the one thing the maintenance rules forbid outright."""

    def test_each_edited_invariant_carries_a_date_and_a_no_meaning_change_note(self):
        b = bodies()
        for ident in ("INV-002", "INV-048", "INV-110", "INV-162"):
            with self.subTest(invariant=ident):
                self.assertRegex(b[ident], r"20\d\d-\d\d-\d\d",
                                 "%s's clarification is undated" % ident)
                self.assertRegex(b[ident].lower(), r"no meaning change",
                                 "%s must state that the edit changed no meaning" % ident)


if __name__ == "__main__":
    unittest.main()
