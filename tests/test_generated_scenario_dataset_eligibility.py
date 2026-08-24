"""Two stale-or-missing facts about what the server returns, in two modules.

**`truthset` cannot back a generated scenario, and nothing said so.** Step 4a requires the
generated scenario's data to be "mapping-complexity-rich (needs at least one transformation when
mapped to the Senzing Entity Specification)". `truthset` is **pre-mapped** — the server's own
word, in `get_capabilities`: "the Senzing demo truth set: CUSTOMERS, REFERENCE, WATCHLIST —
small, pre-mapped, used in quickstarts". So it structurally cannot satisfy that invariant, while
being the most inviting of the four datasets: smallest, already used elsewhere in the bootcamp,
described as for quickstarts. A guide that picked it produced a scenario passing every check the
step enumerates except the one it could not meet, and left the mapping module nothing to
transform. Second, unstated reason: Truth Set visualization already runs on it.
(`specs/truthset-cannot-satisfy-the-generated-scenario-invariants.md`)

**The scaffold snippet count and group list had drifted.** Module 3 Step 4 described
`generate_scaffold(workflow='full_pipeline')` as "snippets across initialization, loading and
searching — 18 of them for Python on server 1.32.2". On 1.32.9 it is **22 across four groups**;
the missing group is `configuration` (4 snippets). No instruction depended on either figure — the
selection rule is explicitly shape-based — which is exactly why the drift is worth correcting:
a reader who checks the stated count against a live response and finds it wrong has been handed
a reason to distrust the paragraph containing the correct rule.
(`specs/scaffold-snippet-count-and-group-list-are-stale.md`)

Both are re-verified against server 1.32.9 on 2026-08-14: `get_sample_data(dataset='list')`
returns the four datasets with those source lists, and
`generate_scaffold(language='python', workflow='full_pipeline')` returns 10 initialization + 4
configuration + 6 loading + 2 searching = 22.

⛔ These tests assert the PROSE, not the server. They cannot detect the next drift — nothing
offline can — which is why both sites are stamped with a version and date and why the scaffold
site now says explicitly that the count is illustration rather than a check.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
DISCOVERY = SKILLS / "module-01-business-problem" / "phase1-discovery.md"
M3_PHASE1 = SKILLS / "module-03-system-verification" / "phase1-verification.md"


def squash(text):
    return re.sub(r"\s+", " ", re.sub(r"^[ \t]*>[ \t]?", "", text, flags=re.M))


def step_4b():
    text = DISCOVERY.read_text(encoding="utf-8")
    start = text.index("### 4b. CORD sourcing for the generated scenario")
    end = text.find("### 5", start)
    return squash(text[start:end if end != -1 else len(text)])


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_files_exist(self):
        for path in (DISCOVERY, M3_PHASE1):
            with self.subTest(file=path.name):
                self.assertTrue(path.is_file(), "%s moved" % path)

    def test_step_4b_is_locatable_and_still_the_sourcing_step(self):
        self.assertIn("get_sample_data", step_4b(),
                      "the located section is not Step 4b")

    def test_step_4a_still_requires_cross_source_mapping_divergence(self):
        """The invariant `truthset` cannot satisfy. If it goes, the exclusion is moot.

        ⚠️ Reworded 2026-08-17 from "mapping-complexity-rich (needs at least one
        transformation)" — that wording was unsatisfiable by the examples the modules gave
        for it. The Truth Set is pre-mapped and uniform, so it fails the reworded
        requirement exactly as it failed the old one; only the phrasing moved.
        """
        self.assertRegex(
            squash(DISCOVERY.read_text(encoding="utf-8")),
            r"(?i)cross-source\*{0,2} mapping divergence",
            "Step 4a's cross-source mapping-divergence invariant is gone")


class TruthsetIsIneligible(unittest.TestCase):
    def setUp(self):
        self.step = step_4b()

    def test_it_is_named_ineligible(self):
        self.assertRegex(
            self.step,
            r"(?i)`truthset` is NOT eligible to back a generated scenario",
            "truthset is not excluded, and it is the most inviting of the four datasets")

    def test_both_reasons_are_given(self):
        self.assertRegex(
            self.step, r"(?i)It is pre-mapped\*?\*?, so it can never satisfy Step 4a's",
            "the mapping-complexity reason is missing")
        self.assertRegex(
            self.step, r"(?i)Truth Set visualization already runs on it",
            "the second reason — two modules on one dataset — is missing")

    def test_the_pre_mapped_word_is_attributed_to_the_server(self):
        self.assertRegex(
            self.step, r"(?i)`get_capabilities` describes it as",
            "the disqualifying fact is asserted without naming the tool that states it "
            "(INV-080)")
        self.assertRegex(
            self.step, r"(?i)server 1\.32\.9, re-verified 2026-08-14",
            "the citation carries no version or date, so a reader cannot tell whether it "
            "is still true")

    def test_it_says_why_truthset_is_inviting(self):
        """Excluding it without saying why invites the exclusion being dropped."""
        self.assertRegex(
            self.step, r"(?i)most inviting choice",
            "nothing records why this needs saying at all")


class TheEligibleCollectionsAreDistinguished(unittest.TestCase):
    def setUp(self):
        self.step = step_4b()

    def test_each_eligible_dataset_is_named_with_its_domain(self):
        for dataset, domain in (("las-vegas", "risk, ownership and licensing"),
                                ("london", "sanctions and corporate-registry"),
                                ("moscow", "sanctions and ownership")):
            with self.subTest(dataset=dataset):
                self.assertRegex(
                    self.step, r"`%s`\s*\|\s*%s" % (re.escape(dataset), re.escape(domain)),
                    "%s is not described by domain, so the guide must infer fit from "
                    "vendor names" % dataset)

    def test_the_counts_are_not_hardcoded(self):
        """INV-080: the server owns the source lists and counts."""
        self.assertRegex(
            self.step,
            r"(?i)take the dataset names, source lists\s*and counts from `get_sample_data` at "
            r"runtime, never from here",
            "the eligibility note does not say to source the data at runtime")
        self.assertNotRegex(
            self.step, r"11 sources|5 sources|6 sources|3 sources",
            "source counts are hardcoded here; the server owns them")


class SynthesizedIsTheExpectedOutcome(unittest.TestCase):
    def setUp(self):
        self.step = step_4b()

    def test_it_is_stated_as_expected_not_as_a_fallback(self):
        self.assertRegex(
            self.step,
            r"(?i)For the customer-facing categories, `synthesized` is the EXPECTED outcome, "
            r"not a failure",
            "the synthesized branch still reads as giving up")

    def test_it_names_the_categories_and_the_reason(self):
        for category in ("Customer 360", "Marketing", "Vendor MDM"):
            with self.subTest(category=category):
                self.assertIn(category, self.step,
                              "%s is not named as a synthesized-by-default category"
                              % category)
        self.assertRegex(
            self.step,
            r"(?i)all three\s*eligible collections are risk / sanctions / ownership data",
            "the reason no CORD dataset fits those categories is unstated")

    def test_it_forbids_stretching_a_dataset_to_reach_the_cord_branch(self):
        self.assertRegex(
            self.step,
            r"(?i)do not stretch a sanctions\s*collection to cover a customer-360 problem",
            "nothing discourages forcing a fit, which is what an 'expected outcome' "
            "framing has to guard against")

    def test_the_branch_is_marked_complete_not_deferred(self):
        self.assertRegex(
            self.step, r"(?i)this branch is complete, not\s*deferred",
            "the synthesized branch does not say Data collection generates the files, so "
            "it still reads as unfinished")

    def test_truthset_only_fits_route_to_synthesized(self):
        self.assertRegex(
            self.step,
            r"(?i)including every case where the only apparent fit was `truthset`",
            "the ineligibility is stated but not wired into the branch that acts on it")


class TheScaffoldFiguresAreCurrent(unittest.TestCase):
    def setUp(self):
        self.flat = squash(M3_PHASE1.read_text(encoding="utf-8"))

    def test_the_stale_figures_are_gone(self):
        self.assertNotRegex(
            self.flat,
            r"(?i)snippets across initialization, loading and searching — 18 of\s*them",
            "the stale 18-across-three-groups description survives")

    def test_the_four_groups_are_enumerated(self):
        self.assertRegex(
            self.flat,
            r"(?i)four groups — `initialization`,\s*`configuration`, `loading` and `searching`",
            "the group list does not match what the server returns; `configuration` was "
            "the missing one")

    def test_the_count_is_current_and_stamped(self):
        self.assertRegex(
            self.flat,
            r"(?i)\*\*22\*\* snippets \(10 / 4 / 6 / 2\) on server 1\.32\.9, verified "
            r"2026-08-14",
            "the count is absent, wrong, or unstamped")

    def test_the_figure_is_marked_as_illustration(self):
        """Criterion: the correction must not read as a check to perform."""
        self.assertRegex(
            self.flat, r"(?i)That figure is illustration, never a check to perform",
            "a corrected count with no framing invites a reader to verify it and report a "
            "mismatch as a defect")
        self.assertRegex(
            self.flat,
            r"(?i)that is the server indexing\s*more snippets, not a problem to report",
            "the step does not say what to do when the live count differs")

    def test_the_drift_supports_the_shape_rule(self):
        self.assertRegex(
            self.flat,
            r"(?i)the count moved and a whole group \(`configuration`\) appeared, while the "
            r"two loading snippets named\s*below stayed exactly where they were",
            "the drift is corrected without being used as the evidence for the rule, which "
            "is the spec's third proposal and the reason the fix is worth making")

    def test_the_shape_based_selection_rule_survives(self):
        self.assertRegex(
            self.flat,
            r"(?i)match on the\s*\*\*shape\*\* — does it open a data file\? — never on position",
            "the selection rule this correction exists to protect was lost")
        for snippet in ("loading/add_records_loop.py", "loading/add_records.py"):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, self.flat,
                              "the named loading pair was lost")


if __name__ == "__main__":
    unittest.main()
