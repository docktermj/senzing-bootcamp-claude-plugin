"""The how-analysis step names the one key pair that half-exists.

Writing the how-analysis renderer, a guide reached for
`RESOLUTION_STEPS[].INBOUND_VIRTUAL_ENTITY` and `CANDIDATE_VIRTUAL_ENTITY` as the two sides
of a resolution step. The real keys are `VIRTUAL_ENTITY_1` and `VIRTUAL_ENTITY_2`. Nothing
raised: every step rendered as `? joined ?` while the rule and match key beside them
populated correctly.

⛔ **The wrong name is plausible, not careless, and that is the finding.** The response does
contain `INBOUND_VIRTUAL_ENTITY_ID` — a *string ID* on the step, not the object holding
`MEMBER_RECORDS[]` — and the `INBOUND_`/`CANDIDATE_` pairing is genuinely real **inside the
same response**, one level deeper, as `INBOUND_FEAT_DESC` / `CANDIDATE_FEAT_DESC` under
`MATCH_INFO.FEATURE_SCORES.<FAMILY>[]` and `MATCH_INFO.MATCH_KEY_DETAILS.CONFIRMATIONS[]`.
Generalizing that pairing upward lands on a key that exists at a different depth and type.

⚠️ **So the existing lookup-before-parse instruction does not by itself prevent this.** A
wholly invented key dies at the first lookup; a key that appears in the schema at the wrong
depth survives it. Only reading the returned paths' *types* — or dumping one raw step —
separates them, which is INV-115's discipline at the point where skipping it is most
tempting, because the lookup looks like it confirmed the name.

Verified against the live server via
`get_sdk_reference(topic='response_schemas', filter='how_entity')` on **1.32.9, 2026-08-17**:
`INBOUND_VIRTUAL_ENTITY_ID` (string) and `RESULT_VIRTUAL_ENTITY_ID` (string) sit alongside
`VIRTUAL_ENTITY_1` / `VIRTUAL_ENTITY_2` (objects), and no `CANDIDATE_VIRTUAL_ENTITY` appears
at any depth.

Source spec: `specs/how-analysis-step-does-not-name-the-confusable-virtual-entity-keys.md`.

Run:  python3 -m unittest discover -s tests
"""
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
STEP4C = (PLUGIN / "skills" / "module-07-query-visualize-discover" /
          "phase2-discover.md")
API_REFERENCE = (PLUGIN / "skills" / "module-03b-truthset-visualization" /
                 "visualization-api-reference.md")
VIZ_SERVER = PLUGIN / "scripts" / "senzing_viz_server.py"


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class TheStepNamesTheCorrectKeys(unittest.TestCase):

    def setUp(self):
        self.text = flat(STEP4C)

    def test_it_names_both_sides_of_a_resolution_step(self):
        self.assertIn("`VIRTUAL_ENTITY_1` and `VIRTUAL_ENTITY_2`", self.text)

    def test_it_identifies_the_string_id_as_a_string_id(self):
        self.assertIn("`INBOUND_VIRTUAL_ENTITY_ID` is a **string ID** on the step, not",
                      self.text)

    def test_it_names_the_string_ids_real_partner(self):
        self.assertIn("`RESULT_VIRTUAL_ENTITY_ID`", self.text)

    def test_it_states_the_invented_key_does_not_exist(self):
        self.assertIn("no `CANDIDATE_VIRTUAL_ENTITY` at any depth", self.text)

    def test_it_names_the_member_records_path(self):
        self.assertIn("`.MEMBER_RECORDS[].RECORDS[].{DATA_SOURCE, RECORD_ID}`",
                      self.text.replace("RECORD_ID}`", "RECORD_ID}`"))

    def test_the_claim_carries_its_route_version_and_date(self):
        """INV-080 — a response-shape fact ships with the call that established it."""
        self.assertIn("get_sdk_reference(topic='response_schemas', filter='how_entity')",
                      self.text)
        self.assertIn("server 1.32.9, 2026-08-17", self.text)


class ItSaysWhyTheWrongPairingIsReachable(unittest.TestCase):
    """⛔ Naming only the correct key does not stop the error recurring."""

    def setUp(self):
        self.text = flat(STEP4C)

    def test_it_names_the_real_inbound_candidate_pairing(self):
        self.assertIn("`INBOUND_FEAT_DESC` / `CANDIDATE_FEAT_DESC`", self.text)

    def test_it_locates_that_pairing_inside_the_same_response(self):
        self.assertIn("one level deeper", self.text)
        self.assertIn("MATCH_INFO.FEATURE_SCORES", self.text)

    def test_it_describes_the_silent_failure_mode(self):
        self.assertIn("? joined ?", self.text)
        self.assertIn("raises no error", self.text)


class TheLookupInstructionSurvivesAndIsQualified(unittest.TestCase):

    def test_the_response_schemas_lookup_is_still_prescribed(self):
        self.assertIn(
            "get_sdk_reference(topic='response_schemas', filter='how_entity_by_entity_id')",
            flat(STEP4C))

    def test_inv115_is_still_cited(self):
        self.assertIn("(INV-115)", flat(STEP4C))

    def test_it_says_a_name_level_lookup_is_insufficient_here(self):
        text = flat(STEP4C)
        self.assertIn("a name-level lookup is not enough here", text)
        self.assertIn("read the returned paths' TYPES, or dump one raw step", text)


class TheKeysAreRecordedWithTheOtherConfirmedPaths(unittest.TestCase):
    """Both hazards live together, so a reader meets them in one place."""

    def setUp(self):
        self.text = flat(API_REFERENCE)

    def test_the_how_entity_row_names_the_object_keys(self):
        self.assertIn("A step's two sides are `VIRTUAL_ENTITY_1` / `VIRTUAL_ENTITY_2`",
                      self.text)

    def test_it_names_the_confusable_string_id_and_the_absent_key(self):
        self.assertIn("`INBOUND_VIRTUAL_ENTITY_ID` is a **string ID**", self.text)
        self.assertIn("no `CANDIDATE_VIRTUAL_ENTITY` exists at any depth", self.text)

    def test_it_carries_its_server_version_and_date(self):
        self.assertIn("re-verified on MCP server 1.32.9, 2026-08-17", self.text)

    def test_the_sibling_hazard_is_still_there(self):
        """The `MIN_ENTITY_ID`/`MAX_ENTITY_ID` entry this one was filed beside."""
        self.assertIn("`MIN_ENTITY_ID` / `MAX_ENTITY_ID`", self.text)


class ThePluginsOwnParserAlreadyUsesTheCorrectKeys(unittest.TestCase):
    """The right answer was in the repo the whole time; it never reached the step."""

    def test_the_visualization_server_reads_virtual_entity_1_and_2(self):
        source = VIZ_SERVER.read_text(encoding="utf-8")
        self.assertIn("VIRTUAL_ENTITY_1", source)
        self.assertIn("VIRTUAL_ENTITY_2", source)

    def test_it_never_reads_the_invented_key(self):
        self.assertNotIn("CANDIDATE_VIRTUAL_ENTITY",
                         VIZ_SERVER.read_text(encoding="utf-8"))


class NoShippedFileNamesTheInventedKeyAsReal(unittest.TestCase):
    """⛔ Derived by scanning, so a future file that adopts the wrong name fails here."""

    #: Words that make a mention a denial rather than a use.
    DENIALS = ("no `CANDIDATE_VIRTUAL_ENTITY`", "invented partner", "does not exist",
               "returns nothing", "at any depth")

    def test_the_invented_key_appears_only_where_it_is_denied(self):
        """⚠️ Judged over a WINDOW, not a line.

        The denial is prose and wraps, so a line-level check reported this file's own
        correction as an offense — the same wrapping trap that bit the suppressed-branch
        guard. A window around each mention is what a reader actually sees.
        """
        offenders = []
        for path in sorted(PLUGIN.rglob("*.md")):
            text = " ".join(path.read_text(encoding="utf-8").split())
            start = 0
            while True:
                found = text.find("CANDIDATE_VIRTUAL_ENTITY", start)
                if found == -1:
                    break
                start = found + 1
                window = text[max(0, found - 160):found + 160]
                if any(denial in window for denial in self.DENIALS):
                    continue
                offenders.append(f"{path.relative_to(REPO_ROOT)}: …{window}…")
        self.assertEqual(
            [], offenders,
            "a shipped file names CANDIDATE_VIRTUAL_ENTITY as though it exists — it is "
            "absent from the how_entity response at every depth (server 1.32.9, "
            "2026-08-17):\n  " + "\n  ".join(offenders))

    def test_the_denial_check_is_not_vacuous(self):
        """A bare use, with no denial nearby, must be reported."""
        window = "parse RESOLUTION_STEPS[].CANDIDATE_VIRTUAL_ENTITY for the other side"
        self.assertFalse(any(denial in window for denial in self.DENIALS))


if __name__ == "__main__":
    unittest.main()
