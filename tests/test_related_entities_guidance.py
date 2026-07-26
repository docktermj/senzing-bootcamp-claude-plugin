"""Tests that the plugin never tells a reader to get `RELATED_ENTITIES` from an export.

Phase D's match-key audit sends the reader to both
`RESOLVED_ENTITY.RECORDS[].MATCH_KEY` and `RELATED_ENTITIES[].MATCH_KEY` as if both were
readable "from the loaded results". They are not: every relationship-detail flag lists
only the per-entity, `why_*` and `find_*` methods in its `applies_to` — the export
methods are absent — confirmed via
`get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_ALL_RELATIONS')`.

An export-based reader therefore returns no `RELATED_ENTITIES` at all, and the audit
reports an empty cross-source suppressor list, which reads exactly like a clean result.
`visualization-api-reference.md` documented the limitation for graph edges but then
offered a relationship-inclusion export flag as the remedy — a workaround that does not
work, in the file that is otherwise the authority.

These tests pin both halves so the two files cannot drift apart again.

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


class TestExportCannotSupplyRelatedEntities(unittest.TestCase):
    """Both files must state the constraint, not just one of them."""

    def test_phase_d_states_the_export_constraint(self):
        text = read(PHASE_D)
        self.assertRegex(
            text,
            r"(?s)Do not expect `RELATED_ENTITIES` from `export_json_entity_report`",
            "phase D must warn that an export cannot supply RELATED_ENTITIES",
        )

    def test_phase_d_names_the_methods_that_do_supply_it(self):
        text = read(PHASE_D)
        for method in ("get_entity_by_entity_id", "find_network_by_entity_id"):
            with self.subTest(method=method):
                self.assertIn(method, text)

    def test_viz_reference_no_longer_offers_an_export_flag_as_the_remedy(self):
        """The bullet that contradicted the observation must be gone."""
        text = read(VIZ_REF)
        self.assertNotRegex(
            text,
            r"(?s)SZ_ENTITY_INCLUDE_ALL_RELATIONS.{0,80}so `RELATED_ENTITIES` is populated",
            "the relationship-inclusion export-flag remedy does not work; it must not be offered",
        )

    def test_viz_reference_states_the_constraint(self):
        self.assertRegex(
            read(VIZ_REF),
            r"(?s)export_json_entity_report` does not supply `RELATED_ENTITIES`",
            "the visualization contract must state the export constraint outright",
        )

    def test_neither_file_claims_an_export_flag_populates_related_entities(self):
        pattern = re.compile(
            r"export.{0,200}?(SZ_ENTITY_INCLUDE_ALL_RELATIONS|relationship-inclusion export flag)"
            r".{0,120}?(populate|so `RELATED_ENTITIES`)",
            re.S | re.I,
        )
        for path in (PHASE_D, VIZ_REF):
            with self.subTest(path=os.path.basename(path)):
                self.assertIsNone(pattern.search(read(path)))


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
