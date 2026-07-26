"""Tests that the plugin's pre-code SDK lookup covers INPUTS, not just outputs.

INV-115 requires looking up a method's **response** structure before parsing it. Nothing
required confirming what a method *takes*, and `get_sdk_reference`'s `flags` and
`response_schemas` topics do not cover parameter shapes either — so the only remaining
source is cross-language documentation, which is wrong for Python's graph methods. A
bootcamp did the flags and response lookups correctly and still lost a round trip passing
`{"ENTITIES": [{"ENTITY_ID": n}]}` to `find_network_by_entity_id`, which takes `List[int]`.

A second, related gap: flag *families* answer different questions. On the export methods
`SZ_EXPORT_INCLUDE_*` selects which entities appear as rows while `SZ_ENTITY_INCLUDE_*`
selects what detail each row carries, so an export flagged with only the former succeeds
and writes rows containing nothing but `ENTITY_ID`.

⚠️ These tests also pin a **correction**: `SZ_EXPORT_ALL_FLAGS` does exist for the export
methods (MCP: `get_sdk_reference(topic='flags', filter='export_json_entity_report')`,
sourced from the Java SDK flag enum). It is the *Python* binding that lacks it. The
guidance must qualify it by binding rather than deny it, because writing a Senzing
falsehood into the plugin breaches INV-080 exactly as a guess would.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp", "skills")
GROUND_RULES = os.path.join(SKILLS, "bootcamp-onboarding", "ground-rules.md")
PHASE_D = os.path.join(SKILLS, "module-06-data-processing", "phaseD-validation.md")
PHASE_2B = os.path.join(
    SKILLS, "module-07-query-visualize-discover", "phase2b-discover.md"
)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def squash(text):
    return re.sub(r"[*\s]+", " ", text)


class GroundRulesCoverParameterShapes(unittest.TestCase):
    def setUp(self):
        self.text = read(GROUND_RULES)

    def test_parameter_shape_rule_exists(self):
        self.assertIn("Parameter shapes, for the bootcamper's binding", self.text)

    def test_it_says_the_existing_topics_do_not_cover_inputs(self):
        squashed = squash(self.text)
        self.assertIn("It does not cover what it takes", squashed)

    def test_cross_language_docs_are_declared_non_authoritative(self):
        self.assertIn(
            "Cross-language documentation is not authoritative", self.text
        )

    def test_introspection_is_the_documented_fallback(self):
        for probe in ("inspect.signature", "dir(SzEngineFlags)"):
            with self.subTest(probe=probe):
                self.assertIn(probe, self.text)

    def test_flag_families_rule_exists(self):
        self.assertIn("Flag families answer different questions", self.text)

    def test_flag_families_state_rows_versus_detail(self):
        squashed = squash(self.text)
        self.assertIn("chooses which entities appear as rows", squashed)
        self.assertIn("chooses what detail each row carries", squashed)
        self.assertIn("nothing but `ENTITY_ID`", squashed)


class ExportCompositeIsQualifiedByBinding(unittest.TestCase):
    """The correction: qualify by binding, never deny the constant outright."""

    def test_neither_file_claims_the_composite_does_not_exist(self):
        for path in (GROUND_RULES, PHASE_D):
            with self.subTest(path=os.path.basename(path)):
                text = read(path)
                self.assertNotRegex(text, r"[Tt]here is no `SZ_EXPORT_ALL_FLAGS`")
                self.assertNotRegex(text, r"`SZ_EXPORT_ALL_FLAGS` does not exist")

    def test_ground_rules_qualifies_it_by_binding(self):
        squashed = squash(read(GROUND_RULES))
        self.assertIn("absent from the Python binding's `SzEngineFlags`", squashed)

    def test_phase_d_qualifies_it_by_binding(self):
        squashed = squash(read(PHASE_D))
        self.assertIn("absent from the Python binding's `SzEngineFlags`", squashed)


class PhaseDCarriesAWorkedExportExpression(unittest.TestCase):
    def setUp(self):
        self.text = read(PHASE_D)

    def test_a_runnable_flag_expression_is_shown(self):
        self.assertIn("SZ_EXPORT_DEFAULT_FLAGS", self.text)
        self.assertRegex(self.text, r"(?s)```python.{0,900}export_json_entity_report")

    def test_it_marks_itself_as_needing_per_session_confirmation(self):
        """A worked example must not become a substitute for the MCP lookup (INV-080)."""
        squashed = squash(self.text)
        self.assertIn("Re-confirm both names via MCP this session", squashed)
        self.assertIn("INV-080", self.text)

    def test_it_uses_the_correct_close_call(self):
        """`close_export_report`, not `close_export` — the Python-specific name."""
        self.assertIn("close_export_report", self.text)

    def test_raw_row_dump_precedes_parsing(self):
        squashed = squash(read(PHASE_D))
        self.assertIn("dump one raw row", squashed)
        self.assertIn("INV-115", read(PHASE_D))


class GraphMethodParameterShapesAreDocumented(unittest.TestCase):
    def setUp(self):
        self.text = read(PHASE_2B)

    def test_step_4d_states_the_topics_do_not_cover_arguments(self):
        squashed = squash(self.text)
        self.assertIn("Neither of those topics tells you the ARGUMENT types", squashed)

    def test_python_signature_is_given_for_both_graph_methods(self):
        self.assertIn("find_network_by_entity_id(entity_ids: List[int]", self.text)
        self.assertIn("find_path_by_entity_id(start_entity_id: int", self.text)

    def test_the_wrong_form_is_named_explicitly(self):
        """Naming the wrong shape is what prevents the natural inference."""
        self.assertIn('{"ENTITIES": [{"ENTITY_ID"', self.text)
        self.assertIn("SzSdkError", self.text)

    def test_guidance_stays_language_agnostic(self):
        """INV-002: only the known-divergent case is spelled out."""
        squashed = squash(self.text)
        self.assertIn("For any other language, confirm the shape from the installed binding", squashed)
        self.assertIn("INV-002", self.text)

    def test_response_schema_rule_still_present(self):
        """The new input rule must not have displaced the INV-115 output rule."""
        self.assertIn("INV-115", self.text)
        self.assertIn("response_schemas", self.text)


if __name__ == "__main__":
    unittest.main()
