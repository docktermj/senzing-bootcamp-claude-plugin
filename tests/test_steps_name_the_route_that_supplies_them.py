"""Four steps that name an outcome must also name the route that supplies it.

INV-212 requires the retrieval strategy to live **at the step**, not merely in the tool's name.
Four steps stated the *what* and omitted the *how*, so each left the guide to compose a route --
and in a plugin whose ⛔ rule is "never fill a Senzing fact from training data", a step naming an
outcome without naming a route is an instruction whose only frictionless completion is the
forbidden one. Observed on a phase-3 walk, 2026-08-22, following the files as written:

1. **`module-01-business-problem/phase1-discovery.md`** -- on a pattern pick, use it as a template
   "(pre-fill source types, suggest matching criteria)". No tool, no query, no source. The natural
   completion is to write plausible source types from memory, and Step 3 has already told the
   bootcamper the gallery is Senzing-sourced, so a guessed pre-fill inherits that attribution.

2. **`module-02-sdk-setup/SKILL.md`** -- Step 9 said to "pick the snippet that creates an engine".
   On server 1.33.0 (2026-08-23) `generate_scaffold(language='python', workflow='initialize')`
   returns **14** snippets with `content` absent -- only `file_path`, `raw_url`, `size_bytes`,
   `line_count` -- and nothing marking any of them as engine-creating. The walk picked
   `initialization/engine_priming.py` by inferring from the filename. Compare Module 3's Step 4,
   which faces the same listing and names the file *with its discriminator*; Step 9 was the same
   problem without the answer.

   ⚠️ **The walk's guess happened to be right, which is the trap.** Reading both snippets:
   `engine_priming.py` builds the factory, calls `create_engine()`, then calls
   `sz_engine.prime_engine()`; `abstract_factory.py` calls `create_engine()` beside
   `create_configmanager()`, `create_diagnostic()` and `create_product()` and never uses any of
   them. So the discriminator is *does the body invoke an engine method*, which is what Step 9's
   own ⛔ demands ("create **and use** an `SzEngine`") -- and "creates an engine" alone does not
   distinguish them.

3. **`module-00-entity-resolution-concepts/concepts.md`** -- "How Senzing handles it" required
   covering "principle-based matching (frequency, exclusivity, stability)" with no query for that
   phrasing. A query composed from the step's own words returns the **A1ES behavior-code**
   material: an FAQ on composite behavior codes, then ~8 KB of `addFeature`, `sz_configtool` and
   `FTYPE_FREQ`/`FTYPE_EXCL`/`FTYPE_STAB` stewardship guidance for someone customizing an engine
   configuration. Not wrong -- it names all three dimensions -- but configuration guidance rather
   than primer material, which is precisely the wrong-altitude retrieval the file's own ⛔ warns
   self-composed queries produce.

4. **`module-03b-truthset-visualization/phase2-close.md`** -- the pre-advancement self-check said
   to "count and compare the tab identifiers" without naming the marker they are written with. On
   a walk the first attempt matched `data-tab="…"`, found **zero in both files**, and reported
   "tab sets match: True". Verified against the generated app: `data-tab` appears **nowhere**, and
   the real marker is `id="tab-<name>"` with six identifiers (`tab-graph`, `tab-stats`,
   `tab-matchkeys`, `tab-features`, `tab-overlap`, `tab-probe`), matching INV-155. ⛔ **A check
   that passes by matching nothing is worse than no check, because it certifies what it never
   compared.**

⛔ **This asserts the steps NAME their routes; it cannot assert a live turn follows them.** That is
`dry-run` phase 3's job. A clean run here means the instruction can no longer be satisfied without
a retrieval route.

Source spec: `specs/a-step-names-what-to-select-without-naming-the-route.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
VIZ_SERVER = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts" /
              "senzing_viz_server.py")

DISCOVERY = SKILLS / "module-01-business-problem" / "phase1-discovery.md"
SDK_SETUP = SKILLS / "module-02-sdk-setup" / "SKILL.md"
CONCEPTS = SKILLS / "module-00-entity-resolution-concepts" / "concepts.md"
PHASE2_CLOSE = SKILLS / "module-03b-truthset-visualization" / "phase2-close.md"

#: The marker the app actually writes its tab identifiers with.
TAB_MARKER = 'id="tab-'


def flat(path):
    """Whitespace-flattened text with blockquote prefixes stripped first.

    ⚠️ **The strip matters.** `phase2-close.md`'s pre-advancement self-check is written as a
    blockquote, so flattening alone turns a wrapped sentence into "has not > passed" and a phrase
    assertion fails on correct text. Same normalization as
    `test_verbatim_check_limitation._flatten`.
    """
    text = re.sub(r"(?m)^\s*>\s?", "", path.read_text(encoding="utf-8"))
    return re.sub(r"\s+", " ", text)


class TheTabMarkerClaimIsTrueOfTheShippedApp(unittest.TestCase):
    """Anti-vacuity of the strongest kind: the guidance must describe the real app.

    Naming a marker is only useful if it is the marker. Both halves are asserted against the
    generator, so a future rename of either the app's markup or the guidance fails here rather
    than reproducing the vacuous-pass defect with a fresh string.
    """

    def setUp(self):
        self.server = VIZ_SERVER.read_text(encoding="utf-8")

    def test_the_app_writes_id_tab_identifiers(self):
        found = sorted(set(re.findall(r'id="(tab-[a-z-]+)"', self.server)))
        self.assertGreaterEqual(
            len(found), 6,
            "the generated app emits fewer than six `id=\"tab-…\"` identifiers (found %r). "
            "Either the markup changed or this guard is reading the wrong file" % found)

    def test_the_app_does_not_use_the_marker_the_walk_guessed(self):
        """If `data-tab` ever appears, the guidance's warning needs rewording, not deleting."""
        self.assertNotIn(
            "data-tab", self.server,
            "`data-tab` now appears in the generated app, so phase2-close's warning that it "
            "matches nothing is stale — re-verify before trusting the check")


class ModuleOneStepThreeNamesItsRoute(unittest.TestCase):
    def setUp(self):
        self.flat = flat(DISCOVERY)

    def test_the_template_prefill_names_where_its_content_comes_from(self):
        self.assertRegex(
            self.flat,
            r"(?i)pre-fill it from the `search_docs` response that\s+supplied that gallery entry",
            "Step 3's template pre-fill does not name the route its content comes from, so the "
            "frictionless completion is to write plausible source types from memory")

    def test_it_forbids_filling_from_what_the_guide_knows(self):
        self.assertRegex(
            self.flat, r"(?i)never from what you know about the pattern",
            "the pre-fill instruction does not forbid the training-data completion, which is "
            "the one a reader reaches for when no route is given")

    def test_it_says_what_to_do_when_the_entry_carried_no_sources(self):
        self.assertRegex(
            self.flat, r"(?i)re-query with the documentation's own\s+vocabulary before pre-filling",
            "the step gives no route for the case its own text describes — a `[Read More]` stub "
            "that supplies none of the four attributes")

    def test_it_cites_the_invariants_that_govern_it(self):
        self.assertRegex(
            self.flat, r"INV-080/INV-212|INV-212/INV-080",
            "the pre-fill rule cites neither the no-speculation invariant nor the retrieval-"
            "strategy one, so a later editor cannot look up why a bare instruction is not enough")


class ModuleTwoStepNineNamesTheSnippetAndItsDiscriminator(unittest.TestCase):
    def setUp(self):
        self.flat = flat(SDK_SETUP)

    def test_it_names_the_snippet(self):
        self.assertIn(
            "initialization/engine_priming.py", self.flat,
            "Step 9 does not name the initialization snippet to pick, so the choice still "
            "depends on inferring from a filename")

    def test_it_names_the_property_that_identifies_it(self):
        self.assertRegex(
            self.flat, r"(?i)CALLS A METHOD ON the engine, not merely one that creates it",
            "Step 9 names a snippet without the discriminator. 'Creates an engine' does not "
            "separate it from `abstract_factory.py`, which also calls create_engine() — the "
            "distinguishing property is whether the body USES the engine")

    def test_it_names_the_confusable_alternative(self):
        self.assertIn(
            "initialization/abstract_factory.py", self.flat,
            "Step 9 does not name the snippet that looks equally correct, so a reader cannot "
            "check they picked the right one")

    def test_it_forbids_selecting_by_count_or_position(self):
        self.assertRegex(
            self.flat, r"(?i)count or a position in the listing is \*\*NOT\*\* the selector"
                       r"|count or a position in the listing is NOT the selector",
            "Step 9 does not rule out selecting by count or position — the failure mode Module "
            "3's Step 4 documents, where the snippet count moved and a whole group appeared")

    def test_it_records_the_listing_shape_with_provenance(self):
        self.assertRegex(
            self.flat, r"(?i)returned \*\*14\*\* snippets with `content` absent",
            "Step 9 does not record that the response is a listing with no inline content, "
            "which is why a shape test is needed at all")
        self.assertRegex(
            self.flat, r"server 1\.\d+\.\d+ \(verified \d{4}-\d{2}-\d{2}\)",
            "the listing observation carries no server version and date; the suite is offline "
            "(INV-108), so the date is the re-check mechanism")

    def test_it_stays_language_agnostic(self):
        self.assertRegex(
            self.flat, r"(?i)rather than transliterating the Python filenames",
            "Step 9 names Python filenames without telling the reader to apply the shape test "
            "in their own chosen language (INV-090)")


class ConceptsNamesTheQueryAndTheAltitudeHazard(unittest.TestCase):
    def setUp(self):
        self.flat = flat(CONCEPTS)

    def test_it_prescribes_the_query_for_the_principles_material(self):
        self.assertRegex(
            self.flat,
            r'(?i)Use `"Senzing principle-based entity resolution approach"` for this',
            "the 'How Senzing handles it' step does not name the query that reaches its "
            "material, so the guide composes one")

    def test_the_rule_cites_the_invariant_that_governs_it(self):
        """INV-183: the rule must be lookup-able at the step. Caught by `conformance.py rules`."""
        self.assertRegex(
            self.flat,
            r'"frequency exclusivity stability" \(INV-\d{3}',
            "the query rule cites no invariant, so `conformance.py rules` counts it as a hard "
            "rule in a section citing none — and a later editor cannot look up why a "
            "self-composed query is not acceptable here")

    def test_it_forbids_the_obvious_self_composed_query(self):
        self.assertRegex(
            self.flat,
            r'(?i)do NOT compose a query\s+from the words "frequency exclusivity stability"',
            "the step does not warn against the query its own wording invites")

    def test_it_names_what_the_wrong_query_actually_returns(self):
        for marker in ("A1ES", "sz_configtool", "addFeature"):
            with self.subTest(marker=marker):
                self.assertIn(
                    marker, self.flat,
                    "the altitude hazard does not name %r, so a reader who lands on that "
                    "material cannot recognize it as the documented wrong turn" % marker)

    def test_it_says_the_wrong_hit_is_misaimed_rather_than_incorrect(self):
        """The honest framing: the A1ES material is accurate and aimed at another audience."""
        self.assertRegex(
            self.flat, r"(?i)configuration guidance, not primer material",
            "the hazard is described as if the material were wrong. It names all three "
            "dimensions correctly — the problem is altitude, and saying so is what stops a "
            "reader 'correcting' it back in")

    def test_the_hazard_carries_its_provenance(self):
        self.assertRegex(
            self.flat,
            r"verified server 1\.\d+\.\d+, docs index \d{4}-\d{2}-\d{2}[^,]*, \d{4}-\d{2}-\d{2}",
            "the altitude observation carries no server version, index date and check date")


class ThePhaseTwoTabCheckNamesItsMarker(unittest.TestCase):
    def setUp(self):
        self.flat = flat(PHASE2_CLOSE)

    def test_it_names_the_marker_the_identifiers_use(self):
        self.assertIn(
            TAB_MARKER, self.flat,
            'the tab-set comparison does not name `id="tab-<name>"`, so a regex that matches '
            "nothing can still pass the check")

    def test_it_enumerates_the_expected_identifiers(self):
        for tab in ("tab-graph", "tab-stats", "tab-matchkeys",
                    "tab-features", "tab-overlap", "tab-probe"):
            with self.subTest(tab=tab):
                self.assertIn(
                    tab, self.flat,
                    "the check does not name %r, so a reader cannot tell a genuine divergence "
                    "from a regex that found part of the set" % tab)

    def test_it_forbids_a_zero_match_from_counting_as_agreement(self):
        self.assertRegex(
            self.flat,
            r"(?i)finds ZERO identifiers on both sides has not\s+passed — it has not run",
            "the check does not rule out the vacuous pass — zero matches on both sides "
            "reporting agreement, which is what actually happened")

    def test_it_requires_a_non_zero_count_before_comparing(self):
        self.assertRegex(
            self.flat, r"(?i)assert a non-zero count on both sides before comparing",
            "the check states the hazard without giving the guard against it")

    def test_it_names_the_marker_that_matched_nothing(self):
        self.assertIn(
            "data-tab", self.flat,
            "the check does not name `data-tab` as the marker that matched nothing, so the "
            "next reader can repeat the same wrong guess")


if __name__ == "__main__":
    unittest.main()
