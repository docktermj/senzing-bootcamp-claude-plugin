"""Tests that Module 5 defines its completeness presence test instead of leaving it
to be re-invented every run.

The quality score gates the module (≥80% proceed / 70-79% warn / <70% remediate), but
nothing said what counts as a *present* value — so each run re-derived a presence
predicate, and one reported `IDENTIFIER_LIST` coverage as 100% when the true figure was
0%, on the field family that supplies exclusive identifiers. An inverted coverage figure
feeds straight into the mapping decision and looks entirely plausible on screen.

The feedback entry blamed a falsy-membership trap in `value not in (None, "", [], {})`.
That predicate is verified below to count an empty list as *absent* — correctly — so it
cannot have produced the 100%; the likelier mechanism is a key-presence test. The fix is
the same either way and does not depend on resolving it: define the test once.

These tests pin the definition and both traps.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULE5 = os.path.join(
    REPO_ROOT, "plugins", "senzing-bootcamp", "skills", "module-05-data-quality-mapping"
)
PHASE1 = os.path.join(MODULE5, "phase1-quality-assessment.md")
SKILL = os.path.join(MODULE5, "SKILL.md")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def presence_section():
    text = read(PHASE1)
    start = text.index('Define "present" this way')
    return text[start : text.index("Use these thresholds", start)]


class PresenceTestIsDefined(unittest.TestCase):
    def test_phase_one_defines_the_presence_test(self):
        self.assertIn('Define "present" this way', read(PHASE1))

    def test_all_four_emptiness_cases_are_covered(self):
        section = presence_section()
        for case in ("key is missing", "whitespace-only", "empty container", "every element"):
            with self.subTest(case=case):
                self.assertIn(case, section)

    def test_false_and_zero_count_as_present(self):
        """They are values, not absences — the direction the feedback's fix asked for."""
        section = presence_section()
        squashed = re.sub(r"[*\s]+", " ", section)
        self.assertIn("`false`, `0` and `0.0` count as PRESENT", squashed)

    def test_truthiness_test_is_forbidden(self):
        self.assertIn("if value:", presence_section())

    def test_presence_is_a_property_of_the_value_not_the_key(self):
        section = presence_section()
        self.assertRegex(section, r"property of the VALUE, never of the key")
        self.assertIn("100%", section)
        self.assertIn("0%", section)

    def test_the_concrete_failure_is_named(self):
        """A worked wrong number is what makes the rule stick."""
        self.assertIn("IDENTIFIER_LIST", presence_section())


class UniformCoverageIsSanityChecked(unittest.TestCase):
    def test_zero_or_full_coverage_triggers_a_sample_check(self):
        section = presence_section()
        self.assertRegex(section, r"Sanity-check any 0% or 100% figure")
        self.assertRegex(section, r"(?s)Print one sample value")

    def test_it_cites_the_invariant_it_mirrors(self):
        self.assertIn("INV-115", presence_section())

    def test_it_does_not_turn_into_a_blocking_gate(self):
        """The check informs the number; it must not add a new blocker."""
        section = presence_section()
        self.assertNotIn("👉", section)
        self.assertNotIn("⛔ BLOCK", section)


class SkillRoutesToTheDefinition(unittest.TestCase):
    def test_reference_note_points_at_phase_one(self):
        text = read(SKILL)
        squashed = re.sub(r"[*\s]+", " ", text)
        self.assertIn("presence test defined in Phase 1 step 6", squashed)

    def test_reference_note_names_both_traps(self):
        text = read(SKILL)
        self.assertIn("truthiness test", text)
        self.assertIn("key presence as coverage", text)

    def test_ported_guide_must_inherit_the_definition(self):
        self.assertRegex(read(SKILL), r"(?s)When the guide is ported")


class ThresholdsAreUnchanged(unittest.TestCase):
    """This defines a measurement; it must not move a gate."""

    def test_the_three_threshold_bands_survive(self):
        text = read(PHASE1)
        for band in ("≥80% quality score", "70-79% quality score", "<70% quality score"):
            with self.subTest(band=band):
                self.assertIn(band, text)

    def test_structural_not_semantic_caveat_survives(self):
        self.assertIn("What this score does not measure", read(PHASE1))


class ReportedMechanismDoesNotReproduce(unittest.TestCase):
    """Recorded so the spec's Unverified root cause is not silently promoted to fact.

    The entry attributed the inversion to `value not in (None, "", [], {})`. Verified
    here: that predicate counts an empty list as absent (correct), and counts `False`/`0`
    as present (also correct, and what the fix asks for). So it is not the mechanism.
    """

    TUPLE = (None, "", [], {})

    def test_empty_list_is_correctly_treated_as_absent(self):
        self.assertFalse([] not in self.TUPLE)

    def test_false_and_zero_are_treated_as_present(self):
        for value in (False, 0, 0.0):
            with self.subTest(value=value):
                self.assertTrue(value not in self.TUPLE)

    def test_key_presence_would_produce_the_reported_inversion(self):
        """The likelier mechanism: 100% coverage for an always-empty field."""
        records = [{"IDENTIFIER_LIST": []} for _ in range(14119)]
        by_key = sum(1 for r in records if "IDENTIFIER_LIST" in r) / len(records)
        self.assertEqual(1.0, by_key, "key presence yields the wrong 100%")

        def present(value):
            if value is None:
                return False
            if isinstance(value, str):
                return bool(value.strip())
            if isinstance(value, (list, dict, set, tuple)):
                return len(value) > 0 and any(present(v) for v in value) if value else False
            return True

        by_value = sum(1 for r in records if present(r["IDENTIFIER_LIST"])) / len(records)
        self.assertEqual(0.0, by_value, "the defined test yields the true 0%")

    def test_defined_test_keeps_falsy_scalars_present(self):
        def present(value):
            if value is None:
                return False
            if isinstance(value, str):
                return bool(value.strip())
            if isinstance(value, (list, dict, set, tuple)):
                return len(value) > 0
            return True

        for value in (False, 0, 0.0):
            with self.subTest(value=value):
                self.assertTrue(present(value))
        for value in (None, "", "   ", [], {}, ()):
            with self.subTest(value=value):
                self.assertFalse(present(value))


if __name__ == "__main__":
    unittest.main()
