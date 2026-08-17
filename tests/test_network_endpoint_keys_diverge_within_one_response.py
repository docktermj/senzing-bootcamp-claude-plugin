"""One `find_network` response uses two endpoint conventions, and step 4d must say so.

A guide building the relationship-network view read the **path** endpoint names off a
**link** element. All 38 edges of a corporate hierarchy printed `null -> null`, with no
error — and a silently empty edge list is indistinguishable from *"this data has no
relationships"*, which is the wrong conclusion to hand an analyst in the capability the
fraud-detection pattern leans on hardest.

    ENTITY_PATHS[]          START_ENTITY_ID / END_ENTITY_ID   (directed)
    ENTITY_NETWORK_LINKS[]  MIN_ENTITY_ID  / MAX_ENTITY_ID    (undirected, low-to-high)

⚠️ **Step 4d's existing warning runs along the wrong axis.** It is a long, careful block
about carrying a parser between `find_path` and `find_network` — the *cross-method* axis. It
never mentioned the *within-response* axis, where two arrays of a single response disagree.

⛔ **And the sentence that would be the natural place to say so pointed away from it.**
"Everything else matches … both link elements carry the same seven fields" is literally true
about the comparison it is making, and still misleads: the step named the links' seven
fields explicitly while never naming `ENTITY_PATHS[]`'s three, and told the reader the two
documents differ in "exactly one key". A reader reasonably concludes the endpoint convention
is uniform.

⚠️ **The one endpoint warning already there is for a DIFFERENT wrong guess.** It cautions
against `ENTITY_ID` / `RELATED_ENTITY_ID`, the pairing related-entity records use. The
failure here is `START_`/`END_` — a pairing that is *correct in the same response*, one array
over. Two plausible wrong namings, and the pair is the point, so both must survive.

Re-verified on MCP server **1.32.9, 2026-08-17** via
`get_sdk_reference(topic='response_schemas', filter='find_network', language='java')`.

⛔ **No upstream report is owed and none must be sent.** The feedback entry routed this
`mcp-server` and asked Senzing to document both arrays' fields; the server already documents
every one of them, including the MIN/MAX versus START/END split. Filing it would report a
gap that does not exist.

Source spec: `specs/paths-and-links-in-one-network-response-use-different-endpoint-keys.md`.

Run:  python3 -m unittest discover -s tests
"""
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
STEP4D = (PLUGIN / "skills" / "module-07-query-visualize-discover" /
          "phase2b-discover.md")
API_REFERENCE = (PLUGIN / "skills" / "module-03b-truthset-visualization" /
                 "visualization-api-reference.md")


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class BothEndpointPairsAreNamedAtStepFourD(unittest.TestCase):

    def setUp(self):
        self.text = flat(STEP4D)

    def test_the_path_endpoints_are_named(self):
        self.assertIn("`START_ENTITY_ID` / `END_ENTITY_ID`", self.text)

    def test_the_link_endpoints_are_named(self):
        self.assertIn("`MIN_ENTITY_ID` / `MAX_ENTITY_ID`", self.text)

    def test_they_are_identified_as_the_same_response(self):
        self.assertIn("ONE `find_network` response uses two different endpoint conventions",
                      self.text)

    def test_it_says_why_they_differ(self):
        """The reason is what makes it memorable rather than another name to recall."""
        self.assertIn("a link is an unordered pair, a path is directed", self.text)

    def test_it_names_which_one_to_read_off_a_link(self):
        self.assertIn("Read the endpoint names off a link element, never off a path",
                      self.text)

    def test_the_claim_carries_its_route_version_and_date(self):
        self.assertIn("filter='find_network', language='java'", self.text)
        self.assertIn("server 1.32.9, 2026-08-17", self.text)

    def test_the_observed_cost_is_recorded(self):
        self.assertIn("38 edges", self.text)
        self.assertIn("null -> null", self.text)


class NoSentenceClaimsAUniformEndpointConvention(unittest.TestCase):
    """⛔ The misleading-but-true sentence, repaired rather than deleted."""

    def setUp(self):
        self.text = flat(STEP4D)

    def test_the_everything_else_matches_claim_is_scoped_to_the_documents(self):
        self.assertIn("Everything else matches **across the two documents**", self.text)
        self.assertIn("claim about the two DOCUMENTS and nothing more", self.text)

    def test_it_points_the_reader_at_the_within_response_trap(self):
        self.assertIn("does not mean the endpoint convention is uniform", self.text)

    def test_the_path_sub_fields_are_named_where_the_link_fields_are(self):
        """The asymmetry must be visible, not inferred from silence."""
        self.assertIn("(`START_ENTITY_ID`, `END_ENTITY_ID`, `ENTITIES[]`)", self.text)


class TheExistingCautionsSurvive(unittest.TestCase):
    """⚠️ This adds a second wrong guess; it does not replace the first."""

    def setUp(self):
        self.text = flat(STEP4D)

    def test_the_related_entity_pairing_caution_is_intact(self):
        self.assertIn("`ENTITY_ID` / `RELATED_ENTITY_ID` pairing that related-entity "
                      "records use", self.text)

    def test_the_array_name_trap_is_intact(self):
        self.assertIn("`ENTITY_PATH_LINKS[]`", self.text)
        self.assertIn("`ENTITY_NETWORK_LINKS[]`", self.text)

    def test_the_paired_matching_info_flags_note_is_intact(self):
        self.assertIn("SZ_FIND_PATH_INCLUDE_MATCHING_INFO", self.text)
        self.assertIn("SZ_FIND_NETWORK_INCLUDE_MATCHING_INFO", self.text)

    def test_the_dump_before_parse_instruction_is_intact(self):
        self.assertIn("Dump one raw link element and read its keys anyway", self.text)


class TheConfirmedPathsTableRecordsThePathFields(unittest.TestCase):

    def setUp(self):
        self.text = flat(API_REFERENCE)

    def test_the_three_path_fields_are_recorded(self):
        self.assertIn("`START_ENTITY_ID`, `END_ENTITY_ID`, `ENTITIES[]`", self.text)

    def test_the_two_conventions_are_named_together(self):
        self.assertIn("carries TWO endpoint conventions at once", self.text)

    def test_it_carries_its_route_version_and_date(self):
        self.assertIn("re-verified on MCP server 1.32.9, 2026-08-17", self.text)

    def test_the_link_row_still_carries_its_seven_fields(self):
        for field in ("`MATCH_LEVEL_CODE`", "`MATCH_KEY`", "`ERRULE_CODE`",
                      "`IS_DISCLOSED`", "`IS_AMBIGUOUS`"):
            with self.subTest(field=field):
                self.assertIn(field, self.text)


if __name__ == "__main__":
    unittest.main()
