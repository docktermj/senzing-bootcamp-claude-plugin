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

    def test_it_names_the_value_only_harvesting(self):
        """Repointed 2026-07-29: `collect_strings()` is no longer string-only.

        It flattens every string AND every int/float (stringified via `str(obj)`), skipping only
        `bool`. What survives is the *shape* of the limitation — the allowed set is built from
        source VALUES — so that is what this pins, rather than the superseded implementation
        detail `isinstance(obj, str)`.
        """
        text = flat(PHASE2)
        self.assertIn("collect_strings()", text)
        self.assertRegex(text, r"(?i)harvests source \*values\* only")
        self.assertRegex(
            text,
            r"(?i)int/float",
            "the current branch set must be stated, or the text drifts back to string-only",
        )

    def test_it_names_the_membership_test(self):
        self.assertIn("v.strip() not in allowed", flat(PHASE2))

    def test_it_names_what_cannot_be_harvested(self):
        """Replaces `test_it_states_both_emissions_are_reported` (2026-07-29).

        That test pinned "emit it as a number / emit it as a string" — the symmetry argument for
        the NUMERIC case, which server 1.32.2 fixed. Two causes remain, and naming them is what
        keeps a bootcamper from recording an exemption for a gate that is now green.
        """
        text = flat(PHASE2)
        self.assertRegex(text, r"(?i)\*\*A boolean\.\*\*|a \*\*boolean\*\*")
        self.assertRegex(text, r"(?i)derived from a source field NAME|source \*\*field NAME\*\*")

    def test_the_numeric_case_is_recorded_as_FIXED_not_as_a_limitation(self):
        """The defect this repointing exists to prevent: guidance for a superseded server.

        The plugin pins no MCP server version, so every bootcamper is on the current server. Text
        describing 1.32.1's behavior can only mislead — here into recording a spurious exemption.
        """
        text = flat(PHASE2)
        self.assertRegex(
            text,
            r"(?i)Numbers are NOT in that list any more|numeric source value now enters the allowed set",
        )
        self.assertRegex(
            text,
            r"(?i)do \*\*not\*\* record a numeric-value exemption|do not record a numeric-value exemption",
        )
        self.assertNotRegex(
            text,
            r"(?i)where a source stores a value as a JSON \*\*number\*\* .{0,80}never enters the allowed set",
            "the superseded claim is back in shipped guidance",
        )

    def test_it_records_the_key_only_waiver(self):
        text = flat(PHASE2)
        self.assertIn('EXEMPT_KEYS = {"DATA_SOURCE", "RECORD_ID"}', text)
        self.assertRegex(text, r"(?i)a \*value\* cannot be exempted")

    def test_the_facts_carry_their_provenance(self):
        """INV-080: a Senzing/resource fact in shipped text says how it was established.

        Repointed 2026-07-29 from `server 1.32.1, 2026-07-28`: the claim was re-established
        against 1.32.2, and the provenance must move with the fact it attests.
        """
        self.assertRegex(flat(PHASE2), r"(?i)server \*\*1\.32\.2\*\*, \*\*2026-07-29\*\*")


class TheMappingIsNotPresumedWrong(unittest.TestCase):
    def test_it_says_not_to_conclude_the_mapping_is_wrong(self):
        self.assertRegex(flat(PHASE2), r"(?i)[Dd]o not conclude the mapping is wrong")

    def test_it_attributes_the_finding_to_the_checker(self):
        self.assertRegex(
            flat(PHASE2),
            r"(?i)limitation of the checker|checker limitation",
        )

    def test_phase_d_carries_the_same_caveat(self):
        """A violation list arriving unresolved must not read as a mapping defect.

        Repointed 2026-07-29: phase D carried its own copy of the string-only claim
        ("cannot express a non-string source value ... reports every emission of a numeric source
        value as a violation"). Two files stating one Senzing fact is two places for it to go
        stale, and both had.
        """
        text = flat(PHASE_D)
        self.assertRegex(text, r"(?i)harvests source \*values\* only")
        self.assertRegex(text, r"(?i)checker limitation and not a mapping error")
        self.assertRegex(
            text,
            r"(?i)Numeric source values used to fail this way and \*\*no longer do\*\*",
            "phase D must not send a bootcamper to record a numeric exemption either",
        )


class TheDataIsNeverAlteredToPassTheGate(unittest.TestCase):
    def test_altering_a_source_value_is_forbidden(self):
        self.assertRegex(flat(PHASE2), r"(?i)[Nn]ever change a source value to satisfy the tool")

    def test_it_says_why_the_workaround_does_not_even_work(self):
        """Repointed 2026-07-29 to the general reason, not the numeric example.

        The old assertion pinned "stringifying a numeric identifier still fails" — true through
        1.32.1, false now. The reason it was citing is unchanged for the causes that remain: the
        allowed set was built without the value, so no re-emission of it can be found there.
        """
        self.assertRegex(
            flat(PHASE2),
            r"(?i)the allowed set was built without it, under either emission",
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


class ThreeFurtherGateLimitationsAreDocumented(unittest.TestCase):
    """The gate rejects two mechanisms the same server prescribes, and crashes on CSV.

    Reported 2026-07-27 across four sources mapped end to end. All three are a *different* kind of
    limitation from the two harvesting gaps above them: here the harvester works and something else
    does not — the equality test's shape (`extract`), the key waiver's coverage (`REL_*`), and the
    input format (CSV). Keeping them in a separate block is why the harvesting section can still
    truthfully say "that is the whole of the harvesting limitation".

    These assert the *requirement*, not phrasing: that a mapper meeting one of the three finds it
    named, learns why, and is routed to INV-173's exemption path rather than to changing the data.
    """

    def setUp(self):
        self.text = flat(PHASE2)

    def test_the_extract_disposition_limitation_is_named(self):
        # The *claim*, not words near it. An earlier version asserted that "`extract`",
        # "allowed_values()" and "a.k.a." each appeared somewhere — all true even after the
        # sentence stating that extract output is rejected was deleted, because `extract` is a
        # documented disposition named elsewhere in this file and the rest of the paragraph
        # survived. Assert the statement that makes it a limitation.
        self.assertRegex(
            self.text, r"(?i)`extract` output is rejected",
            "the text never states that correct `extract` output fails the gate — without that "
            "claim the surrounding detail explains nothing",
        )
        self.assertRegex(self.text, r"(?i)allowed_values\(\)",
                         "the cause — whole value / delimiter segment / whitespace token — is absent")
        self.assertRegex(self.text, r"(?i)a\.k\.a\.",
                         "the worked repro that makes the failure concrete is absent")

    def test_the_relationship_scaffolding_limitation_is_named(self):
        for attribute in ("REL_ANCHOR_DOMAIN", "REL_POINTER_DOMAIN", "REL_POINTER_ROLE"):
            with self.subTest(attribute=attribute):
                self.assertIn(attribute, self.text)

    def test_it_says_which_relationship_attributes_pass(self):
        """`REL_*_KEY` passing is what identifies the cause as the waiver, not the harvester."""
        self.assertRegex(self.text, r"(?i)REL_ANCHOR_KEY.{0,80}REL_POINTER_KEY.{0,60}pass")

    def test_the_csv_limitation_is_named_with_its_error(self):
        self.assertRegex(self.text, r"(?i)load_jsonl")
        self.assertRegex(self.text, r"json\.decoder\.JSONDecodeError")

    def test_the_csv_limitation_appears_at_the_gate_presentation(self):
        """INV-183: the rule belongs where the artifact is produced, not one section away.

        A crash reads as environment trouble unless the step that runs the script says otherwise,
        and that step is where the reader is when it happens.
        """
        gate = self.text[:self.text.find("harvests source *values* only")]
        self.assertIn("JSONDecodeError", gate,
                      "the CSV crash is documented only in the limitations block, not at the gate")
        self.assertRegex(gate, r"(?i)tool limitation, not an environment problem")

    def test_all_three_are_dated_field_observations_not_current_mcp_claims(self):
        """INV-080/INV-169: the rejection half was never re-run against the current server."""
        self.assertRegex(self.text, r"(?i)field observations from 2026-07-27")
        self.assertRegex(self.text, r"(?i)4\.3\.3\.26191")
        self.assertRegex(self.text, r"(?i)not.{0,20}re-run",
                         "the text must say the observations were not re-verified")

    def test_the_prescriptions_carry_current_mcp_provenance(self):
        """What *was* re-verified: that the server still prescribes both mechanisms."""
        self.assertRegex(self.text, r"(?i)1\.32\.3")
        self.assertRegex(self.text, r"(?i)Feature: REL_ANCHOR",
                         "the Entity Specification sections that prescribe REL_* are not cited")

    def test_handling_routes_to_the_existing_exemption_path(self):
        self.assertRegex(self.text, r"(?i)Handling is the same for all three")
        self.assertIn("INV-173", self.text)

    def test_it_forbids_forking_the_scripts(self):
        self.assertRegex(self.text, r"(?i)Do not ship a patched copy",
                         "INV-173's no-fork rule must survive next to a workaround")

    def test_the_harvesting_section_no_longer_claims_to_be_exhaustive(self):
        """It said "they are the whole of this limitation", which three more entries falsify."""
        self.assertNotRegex(
            self.text, r"(?i)they are the whole of this limitation",
            "the harvesting block still claims to cover every limitation",
        )
