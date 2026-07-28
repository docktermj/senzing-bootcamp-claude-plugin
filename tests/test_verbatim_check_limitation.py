"""The verbatim check cannot express a non-string source value, and the plugin must say so.

`sz_verbatim_check.py` is delivered by the MCP server as a workflow resource. Verified
against the current resource (server 1.32.1, 2026-07-28):

* `collect_strings()` builds the allowed set under `isinstance(obj, str)` only — it
  recurses through lists and dicts but captures no other primitive;
* the test is whole-value membership, `if v.strip() not in allowed`;
* the only waiver is key-based — `EXEMPT_KEYS = {"DATA_SOURCE", "RECORD_ID"}` plus any
  attribute ending `_TYPE` — so a *value* cannot be exempted at all, and
  `REL_POINTER_KEY` is not covered.

So where a source stores a value as a JSON number, **both** emissions are reported:
emit it as a number and the checker cannot see it, emit it as a string and it is not in
`allowed`. The gate is unsatisfiable rather than strict, and it fired on all 53,321
relationship rows of a real run. The tempting way out — changing the emitted value to
turn the gate green — does not even work, and distorts the data.

The upstream defect was reported to Senzing on 2026-07-28. These tests pin the
plugin-side mitigation that has to hold until (and whether or not) it is fixed there.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
PHASE2 = PLUGIN / "skills" / "module-05-data-quality-mapping" / "phase2-data-mapping.md"
PHASE_D = PLUGIN / "skills" / "module-06-data-processing" / "phaseD-validation.md"


def flat(path):
    """Whitespace-collapsed text with blockquote markers stripped."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    return re.sub(r"\s+", " ", text)


class TheLimitationIsStated(unittest.TestCase):
    def test_phase2_says_the_gate_is_unsatisfiable_not_strict(self):
        self.assertRegex(flat(PHASE2), r"(?i)unsatisfiable — not strict|unsatisfiable rather than strict")

    def test_it_names_the_string_only_harvesting(self):
        text = flat(PHASE2)
        self.assertIn("collect_strings()", text)
        self.assertIn("isinstance(obj, str)", text)

    def test_it_names_the_membership_test(self):
        self.assertIn("v.strip() not in allowed", flat(PHASE2))

    def test_it_states_both_emissions_are_reported(self):
        """The symmetry is the whole point: there is no emission that passes."""
        text = flat(PHASE2)
        self.assertRegex(text, r"(?i)emit it as a number")
        self.assertRegex(text, r"(?i)emit it as a string")

    def test_it_records_the_key_only_waiver(self):
        text = flat(PHASE2)
        self.assertIn('EXEMPT_KEYS = {"DATA_SOURCE", "RECORD_ID"}', text)
        self.assertRegex(text, r"(?i)a \*value\* cannot be exempted")

    def test_the_facts_carry_their_provenance(self):
        """INV-080: a Senzing/resource fact in shipped text says how it was established."""
        self.assertRegex(flat(PHASE2), r"(?i)server 1\.32\.1, 2026-07-28")


class TheMappingIsNotPresumedWrong(unittest.TestCase):
    def test_it_says_not_to_conclude_the_mapping_is_wrong(self):
        self.assertRegex(flat(PHASE2), r"(?i)[Dd]o not conclude the mapping is wrong")

    def test_it_attributes_the_finding_to_the_checker(self):
        self.assertRegex(
            flat(PHASE2),
            r"(?i)limitation of the checker|checker limitation",
        )

    def test_phase_d_carries_the_same_caveat(self):
        """A violation list arriving unresolved must not read as a mapping defect."""
        text = flat(PHASE_D)
        self.assertRegex(text, r"(?i)cannot express a non-string source value")
        self.assertRegex(text, r"(?i)checker limitation and not a mapping error")


class TheDataIsNeverAlteredToPassTheGate(unittest.TestCase):
    def test_altering_a_source_value_is_forbidden(self):
        self.assertRegex(flat(PHASE2), r"(?i)[Nn]ever change a source value to satisfy the tool")

    def test_it_says_why_the_workaround_does_not_even_work(self):
        """Stringifying still fails, because `allowed` was built without the value."""
        self.assertRegex(
            flat(PHASE2),
            r"(?i)stringifying a numeric identifier still fails",
        )


class TheFlowIsNotBlocked(unittest.TestCase):
    def test_the_guidance_says_to_proceed(self):
        self.assertRegex(flat(PHASE2), r"(?i)then \*\*proceed\*\*|and \*\*proceed\*\*")

    def test_it_forbids_an_iterate_forever_loop(self):
        self.assertRegex(
            flat(PHASE2),
            r"(?i)MUST NOT become an iterate-forever loop or a blocked module",
        )

    def test_it_cites_the_non_blocking_invariant(self):
        self.assertIn("INV-048", flat(PHASE2))


class TheResourceIsNotForked(unittest.TestCase):
    """INV-080: the checker comes from the MCP server; a fork would mask the fix."""

    def test_the_guidance_forbids_shipping_a_patched_copy(self):
        self.assertRegex(
            flat(PHASE2),
            r"(?i)[Dd]o not ship a patched copy of `sz_verbatim_check\.py`",
        )

    def test_the_plugin_ships_no_copy_of_the_checker(self):
        matches = list(PLUGIN.rglob("sz_verbatim_check*.py"))
        self.assertEqual([], matches, "the checker must come from the MCP server")

    def test_the_upstream_report_is_referenced(self):
        self.assertRegex(flat(PHASE2), r"(?i)reported 2026-07-28")


class TheEmissionChoiceIsSpecDriven(unittest.TestCase):
    """The Entity Specification decides the form, not what the checker can see."""

    def test_it_routes_the_type_question_to_the_specification(self):
        self.assertRegex(flat(PHASE2), r"search_docs\(category='data_mapping'\)")

    def test_it_reports_that_the_spec_mandates_no_type(self):
        text = flat(PHASE2)
        self.assertRegex(text, r"(?i)does not\s+mandate a type")

    def test_it_does_not_assert_an_unverified_engine_behavior(self):
        """The reporter's live-engine finding is not repeatable here; it must not be
        stated as fact in shipped guidance (INV-080)."""
        text = flat(PHASE2)
        self.assertNotRegex(
            text,
            r"(?i)Senzing links disclosed relationships for both",
            "a live-engine observation must not be shipped as an assertion",
        )


if __name__ == "__main__":
    unittest.main()
