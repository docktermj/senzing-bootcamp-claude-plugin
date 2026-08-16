"""The completeness denominator has one reading, and an empty one is undefined.

Module 5 Phase 1 step 6 opens by naming cross-guide reproducibility as its reason for
existing — "the number routes a gate banded to the percentage point, so two guides must reach
the same figure" — and then defined the denominator with a verb the same phase uses in a
narrower sense twelve steps earlier:

* **Step 5a** — "resolves to" means *the key itself is a catalog attribute*, allowing for a
  leading label (`BUSINESS_NAME_ORG` -> `NAME_ORG`). A question about an already-Senzing-ready
  source.
* **Step 6** — "resolves to" was intended as *the field has a counterpart*, as identified at
  Step 4. A question about a raw source.

On a fully raw source — the module's most common input — the two readings differ by "no score
at all" (0/0, nothing is a catalog attribute yet) versus a real percentage. Observed
2026-08-14: three raw sources scored 100.0 / 100.0 / 100.0 under the intended reading and
produce no score at all under the other. The tie-breaker sentence was what kept the wrong
reading alive: "a raw source column the bootcamper has not yet been asked about does not
count" reads as excluding a column the guide merely judged to have a counterpart.

Enforces **INV-238** — an empty denominator is reported as undefined, never as zero, and a
metric whose gate exists for reproducibility states its membership rule positively rather than
resting on a verb used in two senses.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
          / "module-05-data-quality-mapping")
PHASE1 = MODULE / "phase1-quality-assessment.md"

#: Step 6 runs from its heading to step 7's.
STEP6 = re.compile(r"## 6\. Assess data quality and apply thresholds(.*?)## 7\. ", re.S)
#: Step 5a, which must not change.
STEP5A = re.compile(r"## 5a\. (.*?)## 6\. ", re.S)


def text():
    return PHASE1.read_text(encoding="utf-8")


def squash(value):
    return re.sub(r"\s+", " ", value)


def step6():
    found = STEP6.search(text())
    assert found, "step 6's section boundaries moved"
    return squash(found.group(1))


def step5a():
    found = STEP5A.search(text())
    assert found, "step 5a's section boundaries moved"
    return squash(found.group(1))


class TheDenominatorIsStatedPositively(unittest.TestCase):
    """Criterion 1 — which fields count, and where the set comes from."""

    def test_it_is_stated_positively(self):
        self.assertRegex(step6(), r"(?i)Which fields count — stated positively")

    def test_it_cites_step_4_as_where_the_set_is_established(self):
        self.assertRegex(
            step6(),
            r"(?i)Step 4 identified an Entity Specification counterpart",
            "the denominator's source set is unattributed, which is what left it ambiguous",
        )

    def test_it_names_all_three_ways_in(self):
        block = step6()
        self.assertRegex(block, r"(?i)dispositioned in mapping")
        self.assertRegex(block, r"(?i)structural key")
        self.assertRegex(block, r"`DATA_SOURCE`, `RECORD_ID`")


class TheTwoSensesOfResolveAreDistinguished(unittest.TestCase):
    """Criterion 2 — one clause, and Step 5a untouched."""

    def test_step_6_names_the_narrower_sense_and_where_it_lives(self):
        block = step6()
        self.assertRegex(block, r"(?i)Step 5a uses \"resolves to\" in a narrower sense")
        self.assertRegex(block, r"(?i)the \*\*key itself\*\* is a catalog attribute")
        self.assertRegex(block, r"(?i)has a counterpart")

    def test_step_6_says_the_wrong_reading_yields_no_score(self):
        """The consequence is the reason the clause is load-bearing, so it is pinned."""
        self.assertRegex(
            step6(), r"(?i)zero\*\* countable fields",
            "without the consequence the clause reads as a style note",
        )

    def test_step_6_says_not_to_change_step_5a(self):
        self.assertRegex(step6(), r"(?i)Do not change Step 5a")

    def test_step_5a_is_unchanged(self):
        block = step5a()
        self.assertIn(
            "Do not resolve the second set by exact string match against the attribute catalog.",
            block,
        )
        self.assertRegex(block, r"BUSINESS_NAME_ORG")
        # Unbolded in the file; the spec's quotation of it added emphasis.
        self.assertRegex(block, r"(?i)keys that resolve to an attribute in the Entity Specification")


class TheInv174ExclusionSurvives(unittest.TestCase):
    """Criterion 3 — narrowed, not removed."""

    def test_the_exclusion_is_still_stated(self):
        block = step6()
        self.assertRegex(block, r"(?i)no\*\* counterpart \*\*and\*\* no disposition")
        self.assertIn("INV-174", block)

    def test_it_still_says_why(self):
        self.assertRegex(
            step6(),
            r"(?i)scoring a source down for work this module has not done yet",
        )

    def test_it_names_what_must_not_be_excluded(self):
        self.assertRegex(
            step6(),
            r"(?i)must\*\* not\*\* be excluded is a column whose counterpart Step 4 has just "
            r"identified|What must \*\*not\*\* be excluded is a column whose counterpart Step 4 "
            r"has just identified",
        )


class AWorkedExampleOnARawSource(unittest.TestCase):
    """Criterion 4 — every prior example came from a case that did not discriminate."""

    def test_the_example_is_present_and_names_a_raw_source(self):
        self.assertRegex(step6(), r"(?i)Worked example — a fully raw source")

    def test_it_shows_a_counting_field_and_a_non_counting_one(self):
        block = step6()
        self.assertRegex(block, r"full_name -> NAME_FULL")
        self.assertRegex(block, r"created_date -> \(none\)")
        self.assertRegex(block, r"(?i)does NOT count")

    def test_it_shows_the_resulting_denominator(self):
        # The number is the point: an example that stops before the denominator leaves the
        # same question open.
        self.assertRegex(
            step6(), r"denominator = 2 applicable fields per record",
            "the example does not state the denominator it produces",
        )
        self.assertRegex(step6(), r"(?i)not 3, and not 0")


class AnEmptyDenominatorIsUndefined(unittest.TestCase):
    """Criterion 5 — 0/0 is never 0%, and it routes differently."""

    def test_the_empty_case_is_named(self):
        self.assertRegex(step6(), r"(?i)An empty denominator means completeness is UNDEFINED")

    def test_it_forbids_reporting_zero(self):
        self.assertRegex(step6(), r"(?i)Never report 0/0 as 0%")
        self.assertIn("INV-238", step6())

    def test_it_routes_to_needs_enrichment(self):
        self.assertRegex(step6(), r'(?i)route that source to \*\*"Needs enrichment"\*\*')
        # The category must actually exist in this phase, or the route is a dead end.
        self.assertRegex(text(), r"(?i)\*\*Needs enrichment:\*\*")

    def test_it_says_why_reporting_zero_is_wrong(self):
        block = step6()
        self.assertRegex(block, r"(?i)arithmetic rather than evidence")
        self.assertRegex(
            block, r"(?i)a source with\s+nothing to measure is not a source measured as bad")

    def test_no_instruction_permits_reporting_an_empty_denominator_as_zero(self):
        """The sweep criterion 5 asks for, over every file in the module.

        Stated **positively**: wherever the module names an empty denominator, "undefined"
        must be named with it. Three earlier formulations were discarded, and the reasons are
        worth keeping because each looked right:

        * Detecting a *zero* claim needed `\\b` after `0%`, which can never match — `%` and the
          following comma are both non-word characters, so the pattern silently matched
          nothing.
        * Segmenting by `[^.]*\\.` is unusable here: a fenced example contains no period, so a
          "sentence" spanned hundreds of characters and absorbed an unrelated negation.
        * Requiring a negation near the claim fails on this very page, whose worked example
          legitimately ends "not 3, and not 0".

        Controlled by **insertion**, not by editing the block — for a "no instruction permits
        X" sweep, deleting every mention passes correctly (nothing permits it), so the control
        has to add a permissive instruction. Verified 2026-08-14: inserting "If the
        completeness denominator is empty, report 0/0 as 0% and continue." into
        `phase2-data-mapping.md` produces two offenders. The handling's *existence* is pinned
        separately by the three tests above, which do fail when the block is removed.
        """
        empty_mention = re.compile(r"(?i)0/0|empty denominator|denominator is empty")
        window = 160
        for path in sorted(MODULE.rglob("*.md")):
            body = squash(path.read_text(encoding="utf-8"))
            for found in empty_mention.finditer(body):
                near = body[max(0, found.start() - window):found.end() + window]
                with self.subTest(file=path.name, near=near[:90]):
                    self.assertRegex(
                        near, r"(?i)undefined",
                        "an empty denominator is named here without 'undefined' nearby, so "
                        "this reads as permitting a 0/0 to be reported as a number",
                    )


class TheRestOfTheMeasurementIsUnchanged(unittest.TestCase):
    """Criterion 6 — this clarifies membership only."""

    def test_the_formula_is_unchanged(self):
        self.assertIn(
            "quality_score = 0.70 × completeness + 0.25 × format_consistency "
            "+ 0.05 × (100 − duplicate_rate)",
            text(),
        )

    def test_the_three_bands_are_unchanged(self):
        body = text()
        self.assertRegex(body, r"\*\*≥80% quality score\*\* → Proceed to Phase 2")
        self.assertRegex(body, r"\*\*70-79% quality score\*\* → Warn the user")
        self.assertRegex(body, r"\*\*<70% quality score\*\* → Strongly recommend fixing")

    def test_the_presence_test_is_unchanged(self):
        block = step6()
        self.assertRegex(block, r"(?i)Define \"present\" this way — do not re-invent it")
        self.assertRegex(block, r"(?i)`false`, `0` and `0\.0` count as PRESENT")
        self.assertRegex(block, r"(?i)Presence is a property of the VALUE, never of the key")

    def test_the_per_record_type_applicability_rule_is_unchanged(self):
        self.assertRegex(
            step6(),
            r"(?i)per-`RECORD_TYPE`\s+applicability \(INV-174\)",
        )

    def test_the_duplicate_rate_definition_is_unchanged(self):
        block = step6()
        self.assertRegex(block, r"(?i)Compute it on that pair, never on whole-row equality")
        self.assertIn("INV-180", block)


if __name__ == "__main__":
    unittest.main()
