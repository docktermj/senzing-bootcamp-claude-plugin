"""The Entity Graph's per-source legend counts are PARTICIPATION, and must be labeled as such.

The block was headed `Single-source:` while `counts` accumulated once per source per node --
participation by construction, cross-source entities included. On a two-source run it read
`CRM_CUSTOMERS 65` and `WEBSTORE_ACCOUNTS 70` against **121** entities of which **14** spanned
both (`65 + 70 - 14 = 121`); the true single-source figures were 51 and 56.

⛔ **Every figure was individually correct, which is why nothing caught it.** Each agreed with the
totals shown elsewhere in the app, so no plausibility check fired and a reader simply concluded 65
entities were CRM-only. A count's label is a claim about its denominator, and single-source was
never the denominator in use.

⚠️ **Relabeling is the fix; recomputing is not.** The whole row is participation-shaped -- the
tooltip filters the *source*, the click handler keeps a node when ANY of its sources is still on,
and the swatch is the per-source color while a cross-source entity is drawn in its own combination
color. True single-source counts would agree with the old label and disagree with all three, so
this guard asserts those three are UNCHANGED as firmly as it asserts the new label.

⚠️ **The heading was also conditional**, sitting inside the combinations branch, so it vanished on
single-source runs -- where the label is accidentally correct -- and appeared only where
participation and single-source diverge. That is the run the module exists to demonstrate, so the
heading is now unconditional.

⚠️ Contract text is flattened before matching: these sentences wrap across lines in shipped
markdown, and an unflattened scan silently matches nothing (INV-265 -- an empty match is not
agreement).

Stdlib only.

Source spec: `specs/entity-graph-legend-labels-participation-counts-as-single-source.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVER = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts" / "senzing_viz_server.py"
CONTRACT = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
            / "module-03b-truthset-visualization" / "visualization-api-reference.md")


def _load_server():
    """Load the bundled reference so the RENDERED page can be asserted, not just its source."""
    spec = importlib.util.spec_from_file_location("viz_legend_under_test", SERVER)
    module = importlib.util.module_from_spec(spec)
    sys.modules["viz_legend_under_test"] = module
    spec.loader.exec_module(module)
    return module


VIZ = _load_server()


def flat(text):
    return " ".join(text.split())


def participation_counts(nodes):
    """Exactly what the legend's `counts` accumulator computes: one increment per source."""
    counts = {}
    for node in nodes:
        for source in node["data_sources"]:
            counts[source] = counts.get(source, 0) + 1
    return counts


def single_source_counts(nodes):
    """What the old label CLAIMED the numbers were."""
    counts = {}
    for node in nodes:
        sources = set(node["data_sources"])
        if len(sources) == 1:
            source = next(iter(sources))
            counts[source] = counts.get(source, 0) + 1
    return counts


#: The reported run, reconstructed: 121 entities over two sources, 14 spanning both.
FIXTURE = (
    [{"data_sources": ["CRM_CUSTOMERS"]}] * 51
    + [{"data_sources": ["WEBSTORE_ACCOUNTS"]}] * 56
    + [{"data_sources": ["CRM_CUSTOMERS", "WEBSTORE_ACCOUNTS"]}] * 14
)


class TheFixtureReproducesTheReportedArithmetic(unittest.TestCase):
    """Anti-vacuity (INV-265): the fixture must actually distinguish the two denominators."""

    def test_the_fixture_matches_the_reported_numbers(self):
        self.assertEqual(121, len(FIXTURE))
        self.assertEqual({"CRM_CUSTOMERS": 65, "WEBSTORE_ACCOUNTS": 70},
                         participation_counts(FIXTURE))
        self.assertEqual({"CRM_CUSTOMERS": 51, "WEBSTORE_ACCOUNTS": 56},
                         single_source_counts(FIXTURE))

    def test_the_two_denominators_actually_differ_here(self):
        """If they agreed, every assertion below would pass on a mislabeled legend."""
        self.assertNotEqual(participation_counts(FIXTURE), single_source_counts(FIXTURE),
                            "the fixture cannot distinguish participation from single-source, so "
                            "it cannot detect the defect it exists for")

    def test_inclusion_exclusion_closes_on_the_entity_total(self):
        """65 + 70 - 14 = 121 -- the arithmetic that identified what the numbers are."""
        counts = participation_counts(FIXTURE)
        overlap = sum(1 for n in FIXTURE if len(set(n["data_sources"])) > 1)
        self.assertEqual(len(FIXTURE), sum(counts.values()) - overlap)

    def test_the_general_identity_holds_for_any_arity(self):
        """Generalized past pairs: each entity contributes len(sources), so subtract len-1."""
        nodes = FIXTURE + [{"data_sources": ["A", "B", "C"]}, {"data_sources": ["A", "C"]}]
        counts = participation_counts(nodes)
        excess = sum(len(set(n["data_sources"])) - 1 for n in nodes)
        self.assertEqual(len(nodes), sum(counts.values()) - excess)


class TheReferenceLegendNamesItsDenominator(unittest.TestCase):
    def setUp(self):
        self.source = SERVER.read_text(encoding="utf-8")
        start = self.source.index("function drawLegend(nodes)")
        self.legend = self.source[start:self.source.index("function openModal", start)]

    def test_no_legend_block_is_labeled_single_source(self):
        self.assertNotIn(
            '.text("Single-source:")', self.legend,
            "the legend still labels participation counts as single-source, so a reader concludes "
            "the per-source figures exclude cross-source entities",
        )

    def test_the_per_source_block_is_labeled_entities_per_source(self):
        self.assertTrue(
            re.search(r'\.text\("Entities per source:"\)', self.legend),
            "the per-source block carries no participation-shaped label",
        )

    def test_the_label_is_emitted_outside_the_combinations_branch(self):
        """It must appear on single-source runs too, where it is correct."""
        combo_branch = self.legend.index("if(combos.length){")
        label = self.legend.index('.text("Entities per source:")')
        closing = self.legend.index("\n  }\n", combo_branch)
        self.assertGreater(
            label, closing,
            "the per-source heading sits inside the combinations branch, so it vanishes on runs "
            "with no cross-source entities -- which is how the wrong label stayed invisible in the "
            "simple case",
        )

    def test_the_overlap_between_the_two_blocks_is_stated(self):
        self.assertTrue(
            re.search(r"counted in each of its sources", self.legend),
            "nothing tells the reader that an entity in several sources appears in each source's "
            "row, so the combination block and the per-source block read as a partition",
        )


class TheParticipationShapedBehaviorIsUnchanged(unittest.TestCase):
    """Criterion: this is a labeling fix. Altering these would desynchronize the counts."""

    def setUp(self):
        source = SERVER.read_text(encoding="utf-8")
        start = source.index("function drawLegend(nodes)")
        self.legend = source[start:source.index("function openModal", start)]

    def test_the_counts_are_still_participation(self):
        self.assertTrue(
            re.search(r"counts\[s\]=\(counts\[s\]\|\|0\)\+1", self.legend),
            "the per-source accumulator changed; the label now describes a denominator the code "
            "no longer computes, which is the original defect with the sides swapped",
        )

    def test_the_tooltip_still_filters_the_source(self):
        self.assertIn('"Show only "+s+" (click again to restore)"', self.legend)

    def test_the_click_handler_still_keeps_a_node_on_any_live_source(self):
        self.assertTrue(
            re.search(r"\(d\.data_sources\|\|\[\]\)\.some\(function\(x\)\{return !off\[x\];\}\)",
                      self.legend),
            "the click filter no longer keeps a node when any of its sources is on, so clicking a "
            "source hides cross-source entities its own count includes",
        )

    def test_the_swatch_is_still_the_per_source_color(self):
        self.assertTrue(re.search(r'\.style\("background",color\(s\)\)', self.legend))


class TheContractCarriesTheRuleForEveryLanguage(unittest.TestCase):
    """INV-002/INV-090 — every non-Python bootcamp builds its server from the contract."""

    def setUp(self):
        self.text = flat(CONTRACT.read_text(encoding="utf-8"))

    def test_the_contract_names_the_label(self):
        self.assertIn('**"Entities per source:"**, never "Single-source:"', self.text,
                      "the contract does not fix the label, so a bootcamp building its own server "
                      "in another language reproduces the same claim")

    def test_the_contract_states_the_denominator_principle(self):
        self.assertIn("a claim about its denominator", self.text)

    def test_the_contract_forbids_recomputing_the_counts_instead(self):
        self.assertRegex(
            self.text, r'(?i)Do not "fix" it by recomputing the counts',
            "the contract does not warn against the recompute route, which agrees with the old "
            "label and disagrees with the tooltip, the click filter and the swatch",
        )

    def test_the_contract_requires_the_overlap_clause_and_an_unconditional_heading(self):
        self.assertIn("counted in **each** of its sources' rows", self.text)
        self.assertRegex(
            self.text, r"(?i)whether or not combination rows exist",
            "the contract does not require the per-source block to be labeled when no combination "
            "rows are present",
        )

    def test_the_contract_keeps_the_reported_arithmetic_as_evidence(self):
        """The numbers are what make the finding checkable rather than a style opinion."""
        self.assertIn("65 + 70", self.text)
        self.assertIn("121", self.text)


class TheRenderedLegendDoesNotClaimSingleSource(unittest.TestCase):
    """Criterion 4's second half — asserted against the RENDERED page, not the source text.

    The source could carry the right literal and still emit the wrong page if the label were
    built by concatenation or swapped by a branch. Rendering closes that gap.
    """

    def setUp(self):
        self.page = VIZ.render_page(
            "T", sources=["CRM_CUSTOMERS", "WEBSTORE_ACCOUNTS", "CRM_CUSTOMERS|WEBSTORE_ACCOUNTS"])

    def test_the_rendered_page_labels_the_block_by_participation(self):
        self.assertIn("Entities per source:", self.page)

    def test_the_rendered_page_never_says_single_source(self):
        self.assertNotIn(
            "Single-source:", self.page,
            "the rendered legend still claims the per-source counts are single-source entities",
        )

    def test_the_rendered_page_states_the_overlap(self):
        self.assertIn("counted in each of its sources", self.page)

    def test_the_rendered_page_is_actually_a_page(self):
        """Anti-vacuity (INV-265): assertNotIn passes trivially on an empty string."""
        self.assertGreater(len(self.page), 10000,
                           "render_page returned almost nothing, so the absence assertions above "
                           "prove nothing")
        self.assertIn("function drawLegend(nodes)", self.page)


if __name__ == "__main__":
    unittest.main()
