"""Tests that the plugin routes `RELATED_ENTITIES` reads on evidence, not on an absolute.

Phase D's match-key audit originally sent the reader to both
`RESOLVED_ENTITY.RECORDS[].MATCH_KEY` and `RELATED_ENTITIES[].MATCH_KEY` as if both were
readable "from the loaded results", with no note that they might need different methods —
and an audit that silently measured only the first reported an empty cross-source
suppressor list, which reads exactly like a clean result.

**The fix over-corrected, and this file used to pin the over-correction.** Phase D was
given a ⛔ absolute — "Do not expect `RELATED_ENTITIES` from `export_json_entity_report`"
— generalized from one session's flag set. That absolute is false:
`reporting_guide(topic='evaluation')` documents each row of an export taken with
`SZ_EXPORT_DEFAULT_FLAGS` as carrying `RESOLVED_ENTITY` **and** `RELATED_ENTITIES[]`, and
its worked pattern computes relationship statistics in a single export pass (verified
2026-07-28); a live SDK 4.3.3 run agreed. The earlier session's rows genuinely lacked the
key because its flags were assembled from `SZ_ENTITY_INCLUDE_*` members, which do not list
the export methods in their `applies_to`. Both observations are real: **the flag set is the
variable, not the method.**

So these tests now pin the evidence-based routing instead of either absolute:

* neither file asserts that an export cannot return `RELATED_ENTITIES`
* both instruct dumping one row and routing on its top-level keys (INV-115/INV-149)
* the export-with-defaults case is attributed to the MCP reporting guide, not asserted
* the deduplication requirement is stated, since each relationship appears in both
  entities and an un-deduplicated single-pass read double-counts every one of them
* the defensive guarantees the earlier spec established — the reader-capability check, the
  three-outcome gate, no direct SQL — all survive unchanged

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp", "skills")
PHASE_D = os.path.join(SKILLS, "module-06-data-processing", "phaseD-validation.md")
VIZ_REF = os.path.join(
    SKILLS, "module-03b-truthset-visualization", "visualization-api-reference.md"
)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class TestExportCapabilityIsFlagConditional(unittest.TestCase):
    """Neither absolute may be asserted: the dumped row decides."""

    def test_no_file_claims_the_export_cannot_supply_related_entities(self):
        """The reversed absolute must be gone from both files."""
        for path in (PHASE_D, VIZ_REF):
            with self.subTest(path=os.path.basename(path)):
                text = read(path)
                self.assertNotRegex(
                    text, r"Do not expect `RELATED_ENTITIES` from `export_json_entity_report`"
                )
                self.assertNotRegex(
                    text, r"export_json_entity_report` does not supply `RELATED_ENTITIES`"
                )

    def test_both_files_condition_the_answer_on_the_flag_set(self):
        for path in (PHASE_D, VIZ_REF):
            with self.subTest(path=os.path.basename(path)):
                self.assertRegex(
                    read(path),
                    r"(?is)depends on the flag set",
                    "state that the flag set, not the method, decides",
                )

    def test_both_files_require_dumping_one_row_before_choosing_a_reader(self):
        for path in (PHASE_D, VIZ_REF):
            with self.subTest(path=os.path.basename(path)):
                self.assertRegex(read(path), r"(?is)dump one row|dump one raw row")

    def test_phase_d_routes_on_the_dumped_keys(self):
        text = read(PHASE_D)
        self.assertRegex(text, r"(?is)RELATED_ENTITIES` present")
        self.assertRegex(text, r"(?is)RELATED_ENTITIES` absent")

    def test_the_export_case_is_attributed_to_the_mcp_reporting_guide(self):
        """INV-080: an SDK behavior claim must carry its MCP source, not our word."""
        for path in (PHASE_D, VIZ_REF):
            with self.subTest(path=os.path.basename(path)):
                self.assertRegex(
                    read(path), r"reporting_guide\(topic='evaluation'\)"
                )

    def test_both_files_require_pair_deduplication(self):
        """Each relationship appears in both entities; a single pass double-counts."""
        for path in (PHASE_D, VIZ_REF):
            with self.subTest(path=os.path.basename(path)):
                self.assertRegex(read(path), r"(?is)dedupl")
                self.assertRegex(read(path), r"min_id, max_id|both entities")

    def test_phase_d_still_names_the_per_entity_fallback_methods(self):
        text = read(PHASE_D)
        for method in ("get_entity_by_entity_id", "find_network_by_entity_id"):
            with self.subTest(method=method):
                self.assertIn(method, text)

    def test_viz_reference_keeps_the_per_entity_and_network_routes(self):
        """They stay correct — they are the fallback, not the only way."""
        text = read(VIZ_REF)
        self.assertIn("find_network_by_entity_id", text)
        self.assertIn("get_entity_by_entity_id", text)


class TestEmptyResultIsTreatedAsPlumbingFailure(unittest.TestCase):
    """INV-115: a blank parsed field is a probable wrong reader before it is real absence."""

    def test_phase_d_requires_a_reader_capability_check(self):
        text = read(PHASE_D)
        self.assertRegex(
            text,
            r"(?s)empty cross-source suppressor list is a plumbing failure",
            "an empty suppressor list must be challenged before being reported as clean",
        )
        self.assertIn("could not read relationship match keys", text)

    def test_phase_d_gate_has_three_outcomes(self):
        """'Could not measure' must not collapse into 'no finding'."""
        text = read(PHASE_D)
        start = text.index("## Iterate vs. proceed decision gate")
        section = text[start : start + 2000]
        for outcome in ("A finding", "No finding", "Could not measure"):
            with self.subTest(outcome=outcome):
                self.assertIn(outcome, section)

    def test_viz_reference_challenges_an_empty_edge_array(self):
        self.assertRegex(
            read(VIZ_REF),
            r"(?s)edges` array is empty.{0,200}probable reader failure",
            "an empty edges array must be challenged, not rendered as 'no relationships'",
        )

    def test_audit_still_forbids_direct_sql(self):
        """INV-117 must survive the rewrite."""
        self.assertIn("never direct SQL", read(PHASE_D))


class TestBindingSpecificFlagNames(unittest.TestCase):
    def test_phase_d_does_not_claim_sz_export_all_flags_is_absent_everywhere(self):
        """It exists for the export methods (Java enum); it is the *Python* binding that lacks it.

        Overstating it would put a Senzing falsehood into the plugin, which INV-080 forbids
        as much as it forbids a guess.
        """
        text = read(PHASE_D)
        self.assertNotRegex(text, r"There is no `SZ_EXPORT_ALL_FLAGS`")
        if "SZ_EXPORT_ALL_FLAGS" in text:
            self.assertRegex(
                text,
                r"(?s)SZ_EXPORT_ALL_FLAGS.{0,300}(absent from the Python binding|Java SDK)",
                "qualify the constant by binding rather than denying it outright",
            )

    def test_phase_d_distinguishes_the_two_export_flag_families(self):
        text = read(PHASE_D)
        self.assertIn("SZ_EXPORT_INCLUDE_", text)
        self.assertIn("SZ_EXPORT_DEFAULT_FLAGS", text)
        self.assertRegex(
            text,
            r"(?s)SZ_EXPORT_INCLUDE_\*` selects \*\*which\s*\n?\s*entities\*\*",
            "state that the INCLUDE family selects rows, not per-row detail",
        )

    def test_phase_d_requires_a_raw_row_dump_before_parsing(self):
        self.assertRegex(read(PHASE_D), r"(?s)dump one raw row")


if __name__ == "__main__":
    unittest.main()
