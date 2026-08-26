"""The source-set encoding check is contract behavior, not a Python-reference feature.

INV-259 requires a graph node's fill, stroke and stroke width to derive from the entity's whole
**sorted set** of data sources. That rule is stated in three places -- the any-language contract,
Module 7 step 3c, and the invariant itself -- and on **2026-08-25** it was still re-implemented
wrong in a generated Java app, which colored from `data_sources[0]`: 294 of 5,619 cross-source
entities rendered in a single-source color, beneath a legend saying they were single-source. The
bundled Python reference was already correct and had been for eight days; the defect reappeared
where the rule had to be *followed* rather than *inherited*.

⛔ **So the gap was never a missing rule -- it was that nothing checked the generated app against
one.** This guard covers the check that closes it: distinct legend color keys MUST equal distinct
sorted source-set keys over the nodes drawn. First-source coloring collapses every combination onto
a single-source key, so the legend count drops below the source-set count exactly when the
misencoding is present.

⚠️ **INV-002 is the reason this guard exists at all.** A check that lives only in
`senzing_viz_server.py` reaches generated code solely through the reference -- the failure INV-164
and INV-190 each had to record case by case, and precisely the failure that produced this
recurrence. So the assertions below are about the **contract** and the **build steps**; the
reference is checked separately, for behavior, and must not be the only place the rule exists.

⚠️ **INV-265 is the other half.** With one registered data source every source-set key is that
source, the comparison cannot fail, and a "pass" would be agreement from a match that could not
disagree. That is the *normal* Truth Set situation, not a corner case -- it is why the module that
builds the app cannot provoke the defect -- so both build sites must report **not exercised**
rather than passed.

Stdlib only. The contract and build steps are read as text; the reference's own check is exercised
by import, which is a dev-only read of a bundled script (INV-108).

Source spec: `specs/the-source-set-coloring-rule-is-stated-three-times-and-verified-nowhere.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
SCRIPTS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts"
CONTRACT = SKILLS / "module-03b-truthset-visualization" / "visualization-api-reference.md"

#: The field the contract defines and both build steps compare against. One name, so a build step
#: cannot claim to run the check while comparing something else.
FIELD = "encoding_check"
COUNT_FIELD = "distinct_source_set_keys"


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def build_sites():
    """The shipped steps that stand up the app and capture from it.

    Derived by scanning for steps that invoke the bundled capture script, rather than by naming
    paths (INV-246): a third module that builds the app inherits this guard.
    """
    out = []
    for path in sorted(SKILLS.glob("**/*.md")):
        text = flat(path)
        if "capture_screenshots.py" in text and FIELD in text:
            out.append((path, text))
    return out


class TheContractStatesItAsBehavior(unittest.TestCase):
    """INV-002 — stated for every language, not only in the reference."""

    def setUp(self):
        self.text = flat(CONTRACT)

    def test_the_contract_defines_the_self_check(self):
        self.assertIn(FIELD, self.text,
                      "the any-language contract does not define the encoding self-check, so it "
                      "can only reach generated code through the Python reference (INV-002)")
        self.assertIn(COUNT_FIELD, self.text)

    def test_it_is_marked_required_and_language_neutral(self):
        self.assertRegex(
            self.text,
            r"encoding self-check \(required — behavior, in every language\)",
            "the self-check section is not marked required-behavior-in-every-language, the heading "
            "form the rest of this contract uses for rules that bind generated code",
        )

    def test_it_states_the_equality_that_detects_the_defect(self):
        self.assertRegex(
            self.text,
            r"(?i)legend names\*?\*? MUST equal|MUST equal\s+`?distinct_source_set_keys",
            "the contract does not state the equality between legend color keys and distinct "
            "source-set keys, which is the whole detection mechanism",
        )

    def test_it_explains_why_the_equality_catches_first_source_coloring(self):
        self.assertRegex(
            self.text, r"(?i)collapses every combination onto a single-source key",
            "the contract states the check without saying why it works, so a reader cannot tell "
            "whether a mismatch is the defect or a bug in the check",
        )

    def test_it_requires_not_exercised_rather_than_passed(self):
        """INV-265 — an empty or trivial match is an unrun check, never agreement."""
        self.assertIn("not_exercised", self.text)
        self.assertRegex(
            self.text, r"(?i)never \"passed\"|never ['\"]?passed",
            "the contract does not forbid reporting a pass when the check cannot fail (INV-265)",
        )

    def test_it_stops_before_capture_on_a_mismatch(self):
        self.assertRegex(
            self.text, r"(?i)stop and fix the encoding before capturing",
            "the contract does not require stopping before capture on a mismatch, so the wrong "
            "picture is captured into the recap and found afterwards",
        )


class BothBuildSitesInvokeIt(unittest.TestCase):
    def test_two_build_sites_are_found(self):
        found = build_sites()
        self.assertGreaterEqual(
            len(found), 2,
            "fewer than the two shipped build sites reference the encoding check — the Truth Set "
            f"build and Module 7 step 3c must both run it (found {len(found)})",
        )

    def test_each_build_site_compares_against_the_contract_field(self):
        for path, text in build_sites():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertIn(
                    COUNT_FIELD, text,
                    "the build step mentions the check without naming the field it compares "
                    "against, so 'run the check' is unfalsifiable",
                )

    def test_each_build_site_stops_rather_than_capturing_on_a_mismatch(self):
        for path, text in build_sites():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertRegex(
                    text, r"(?i)fix the encoding.{0,80}(?:before capture|re-render before capture)"
                          r"|stop and\s+fix the encoding",
                    "the build step does not say to stop and fix before capturing, so a mismatch "
                    "still produces screenshots of the wrong encoding",
                )

    def test_the_truthset_site_says_the_check_is_usually_vacuous_there(self):
        """The defect's whole survival mechanism, stated where it applies."""
        truthset = [t for p, t in build_sites() if "module-03b" in str(p)]
        self.assertTrue(truthset, "the Truth Set build site no longer references the check")
        self.assertRegex(
            truthset[0], r"(?i)not exercised|not_exercised",
            "the Truth Set build step does not name the not-exercised outcome, which is its "
            "expected result with one data source (INV-265)",
        )

    def test_the_module7_site_says_the_check_has_teeth_there(self):
        module7 = [t for p, t in build_sites() if "module-07" in str(p)]
        self.assertTrue(module7, "Module 7 step 3c no longer references the check")
        self.assertRegex(
            module7[0], r"(?i)not vacuous|has teeth|multi-source by construction",
            "Module 7 step 3c does not say the check is meaningful on the bootcamper's data, "
            "which is the one run where the defect actually shows",
        )


class TheReferenceImplementsIt(unittest.TestCase):
    """Behavior, exercised -- the reference must stay a correct example of the contract."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(SCRIPTS))
        from senzing_viz_server import Model  # noqa: E402
        # staticmethod(...) so `self.check(nodes)` does not bind `self` as the first argument.
        cls.check = staticmethod(Model._encoding_check)

    def test_a_cross_source_set_is_keyed_by_the_whole_sorted_set(self):
        result = self.check([{"data_sources": ["REFERENCE", "CUSTOMERS"]}])
        self.assertEqual(["CUSTOMERS|REFERENCE"], result["source_set_keys"],
                         "the key is not the sorted, joined source set (INV-259)")

    def test_key_order_does_not_depend_on_input_order(self):
        a = self.check([{"data_sources": ["REFERENCE", "CUSTOMERS"]}])
        b = self.check([{"data_sources": ["CUSTOMERS", "REFERENCE"]}])
        self.assertEqual(a["source_set_keys"], b["source_set_keys"])

    def test_a_single_source_corpus_is_not_exercised_rather_than_ok(self):
        """INV-265 — the Truth Set case must not report agreement."""
        result = self.check([{"data_sources": ["CUSTOMERS"]}] * 5)
        self.assertEqual("not_exercised", result["status"])
        self.assertNotIn("passed", result["detail"].lower())

    def test_multiple_distinct_keys_are_exercised(self):
        result = self.check([{"data_sources": ["A"]}, {"data_sources": ["A", "B"]}])
        self.assertEqual("ok", result["status"])
        self.assertEqual(2, result["distinct_source_set_keys"])
        self.assertEqual(["A|B"], result["combination_keys"])

    def test_empty_and_sourceless_nodes_do_not_raise_or_pass(self):
        for nodes in ([], [{}], [{"data_sources": []}]):
            with self.subTest(nodes=nodes):
                self.assertEqual("not_exercised", self.check(nodes)["status"])

    def test_the_graph_payload_carries_the_field(self):
        source = (SCRIPTS / "senzing_viz_server.py").read_text(encoding="utf-8")
        self.assertRegex(
            source, r'"encoding_check":\s*self\._encoding_check\(nodes\)',
            "the graph payload does not carry encoding_check, so the build step has nothing to read",
        )

    def test_the_reference_still_colors_by_the_whole_set(self):
        """Unchanged by this spec -- srcKeyOf must survive at all three attributes.

        Asserted per attribute rather than by counting call sites: a count is wrong the
        moment anything nearby is refactored, while "fill derives from the set key" is the
        property INV-259 actually requires. Leaving any ONE of the three reading the first
        source keeps a partial version of the same misencoding, so each is named.
        """
        source = (SCRIPTS / "senzing_viz_server.py").read_text(encoding="utf-8")
        self.assertIn("function srcKeyOf(d)", source)
        # assertTrue(re.search(...)) rather than assertRegex: a failed assertRegex embeds the
        # whole 240KB script in its message, which buries the finding it is reporting.
        for attribute, pattern in (
            ("fill", r'\.attr\("fill",.{0,80}?srcKeyOf\(d\)'),
            ("stroke", r'\.attr\("stroke",.{0,80}?srcKeyOf\(d\)'),
            ("stroke-width", r'\.attr\("stroke-width",.{0,80}?srcKeyOf\(d\)'),
        ):
            with self.subTest(attribute=attribute):
                self.assertTrue(
                    re.search(pattern, source),
                    f"the node's {attribute} no longer derives from srcKeyOf, so cross-source "
                    "entities are encoded by one member of their source set (INV-259)",
                )
        self.assertTrue(
            re.search(r"srcKeyOf\(n\);\s*if\(isCombo\(k\)\)", source),
            "the legend no longer counts combinations over the source-set key, so a color on "
            "screen can have no row naming it (INV-259)",
        )


if __name__ == "__main__":
    unittest.main()
