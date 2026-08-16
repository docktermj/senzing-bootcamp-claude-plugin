"""Data collection must recognize BOTH generated provenances, and judge load time on what loads.

MCP-NEGATIVE-SCAN: ignore-file — this file quotes the MCP-NEGATIVE marker's shape in order to
assert that the real one (in module-04's SKILL.md) carries its `owner:` clause. The pattern
literal below is a matcher, not a dated claim about the server, so the negatives scanner would
otherwise report this test as a malformed marker.


Two defects on the default path of a required module, both from the same file.

**The skip guard knew only `cord`.** The Business Case Offer produces two provenances — `cord`
when a CORD collection fits the chosen category, `synthesized` when none does — and for the
customer-facing categories `synthesized` is the *normal* outcome. So a Bootcamper with a
generated synthetic scenario was asked, once per source (four times, on the walk that found it),
how they would like to provide data they had already told the bootcamp they do not have. The
step's own prose condemns exactly that. Worse, the branch it fell into "recommend[s] CORD data as
the primary alternative" — the option Module 1 had already evaluated and rejected for that
category, so the question could not resolve.
(`specs/data-collection-does-not-recognize-a-synthesized-scenario.md`)

**The load-time warning ignored the cap set one step earlier.** Step 8a settles the license
question; a Bootcamper who declines a key is capped at the built-in evaluation license. Step 8b
then judged SQLite load time from the **collected** total: 19,500 collected against a 500-record
cap produced a warning about a roughly half-hour load, for a load of about two minutes — and
offered "sample down to a smaller record count", which is what Step 8a had just decided.
(`specs/load-time-warning-ignores-the-license-cap-decided-one-step-earlier.md`)

Both are conversational instructions, so this file pins them as requirements on the prose. The
Senzing routing claim is checked as a claim about the *route*, not about the numbers.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_04 = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
             / "module-04-data-collection" / "SKILL.md")
DISCOVERY = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
             / "module-01-business-problem" / "phase1-discovery.md")


def read():
    return MODULE_04.read_text(encoding="utf-8")


def squash(text):
    return re.sub(r"\s+", " ", re.sub(r"^[ \t]*>[ \t]?", "", text, flags=re.M))


def section(text, start, end):
    i = text.index(start)
    j = text.find(end, i + len(start))
    return text[i:j if j != -1 else len(text)]


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_module_exists(self):
        self.assertTrue(MODULE_04.is_file(), "module-04 SKILL.md moved")

    def test_module_1_still_produces_both_provenances(self):
        """The premise. If Module 1 stops emitting `synthesized`, this guard is moot."""
        flat = squash(DISCOVERY.read_text(encoding="utf-8"))
        self.assertRegex(flat, r"(?i)provenance `cord`",
                         "Module 1 no longer records the cord provenance")
        self.assertRegex(flat, r"(?i)provenance `synthesized`",
                         "Module 1 no longer records the synthesized provenance")


class TheSkipGuardRecognizesBothProvenances(unittest.TestCase):
    def setUp(self):
        self.step2 = squash(section(read(), "### 2. For each data source, collect the data",
                                    "### 3."))

    def test_the_marker_is_the_signal_and_the_provenance_selects_the_action(self):
        self.assertRegex(
            self.step2,
            r"(?i)The signal is the MARKER; the provenance selects the ACTION",
            "the two questions the guard conflated are still conflated")

    def test_cord_is_no_longer_described_as_the_case_the_offer_produces(self):
        self.assertNotRegex(
            self.step2,
            r"(?i)`provenance: cord` is the case the Business Case Offer produces",
            "the guard still names cord as the only generated provenance")

    def test_both_provenances_have_a_branch(self):
        for provenance in (r"\*\*`provenance: cord`\*\*", r"\*\*`provenance: synthesized`\*\*"):
            with self.subTest(provenance=provenance):
                self.assertRegex(self.step2, provenance,
                                 "no branch for %s" % provenance)

    def test_the_synthesized_branch_generates_files(self):
        self.assertRegex(
            self.step2, r"(?i)\*\*generate the source files\.\*\*",
            "the synthesized branch does not say to generate anything")
        self.assertRegex(
            self.step2, r"(?i)one file per source into `data/raw/`",
            "the generated files have no stated destination")
        self.assertRegex(
            self.step2, r"(?i)record the actual counts back into the registry",
            "nothing records the produced record counts, which the next steps read")

    def test_the_synthesized_branch_asks_nothing_and_recommends_no_cord(self):
        self.assertRegex(
            self.step2,
            r"(?i)Ask nothing, recommend no CORD alternative, and do not enter the "
            r"free-data hierarchy",
            "the synthesized branch can still fall into the CORD recommendation that "
            "Module 1 already ruled out for this category")

    def test_it_says_why_synthesized_is_the_normal_outcome(self):
        self.assertRegex(
            self.step2, r"(?i)no CORD collection fits the chosen\s*category",
            "without the reason, synthesized still reads as the exceptional case")

    def test_the_mapping_complexity_requirement_is_carried_through(self):
        self.assertRegex(
            self.step2, r"(?i)Generate the mapping complexity the scenario promised",
            "generated files may be clean and uniform, which makes the mapping module "
            "vacuous — Module 1 Step 4a's invariant promised otherwise")

    def test_the_cord_branch_keeps_its_fetch_integrity_routing(self):
        self.assertRegex(
            self.step2, r"(?i)fetch under\s*\[CORD fetch integrity\]",
            "the cord branch lost its throttle-aware fetch routing")


class TheLastResortFramingIsScoped(unittest.TestCase):
    def setUp(self):
        self.flat = squash(read())

    def test_the_hierarchy_is_conditioned_on_having_no_scenario(self):
        self.assertRegex(
            self.flat, r"(?i)has \*\*no\s*bootcamp-generated scenario\*\*",
            "the free-data hierarchy still applies to a Bootcamper whose scenario is "
            "already decided")

    def test_last_resort_is_explicitly_not_a_judgment_on_the_provenance(self):
        self.assertRegex(
            self.flat,
            r'(?i)"Last resort" is scoped to that Bootcamper',
            "the last-resort framing is unscoped, so it contradicts Step 2's synthesized "
            "branch")
        self.assertRegex(
            self.flat, r"(?i)not\*?\*? a judgment on `provenance: synthesized`",
            "nothing separates the act of synthesizing from the recorded provenance")


class TheLoadTimeWarningUsesTheLoadableTotal(unittest.TestCase):
    def setUp(self):
        self.step8b = squash(section(read(), "### 8b. SQLite load-time warning",
                                     "### 9."))

    def test_the_scoping_sentence_names_the_loadable_dataset(self):
        self.assertRegex(
            self.step8b, r"(?i)judges the Module 6 SQLite load time from the\s*"
                         r"\*\*loadable\*\* dataset",
            "the step still scopes itself to the collected dataset")

    def test_the_no_cap_clause_is_kept(self):
        """It is correct — the spec says so — and only its mirror was missing."""
        self.assertRegex(
            self.step8b, r"(?i)fires even when the effective license imposes no record cap",
            "the correct half of the scoping was removed instead of complemented")
        self.assertRegex(
            self.step8b, r"(?i)Its mirror is what was missing",
            "the mirror case is added without saying it is the mirror, so a later editor "
            "may read the two clauses as contradictory")

    def test_it_reads_step_8as_outcome(self):
        # ⛔ The key NAMES alone are not the requirement — a mutation that kept them while
        # replacing the instruction with "Ignore the license" escaped this test. Assert the
        # imperative too.
        self.assertRegex(
            self.step8b,
            r"(?i)Also read Step 8a's outcome, which this step ran seconds after",
            "Step 8b is not instructed to read the license outcome, so it can carry the "
            "key names while ignoring them")
        for key in ("license_record_limit", "config/bootcamp_preferences.yaml",
                    "config/bootcamp_progress.json"):
            with self.subTest(key=key):
                self.assertIn(key, self.step8b,
                              "Step 8b does not read %s, though Step 8a wrote it seconds "
                              "earlier" % key)

    def test_the_loadable_formula_is_stated(self):
        self.assertRegex(
            self.step8b,
            r"loadable = min\(collected_total, effective_limit\)",
            "the formula is not given, so 'loadable' is left to interpretation")
        self.assertRegex(
            self.step8b, r"(?i)\*\*unbounded\*\* when the limit is `0`",
            "the unbounded case is not defined")
        self.assertRegex(
            self.step8b, r"(?i)unreadable license state as unbounded",
            "an unreadable license state could invent a cap, which is worse than the "
            "defect being fixed")

    def test_the_warn_decision_uses_the_loadable_total(self):
        self.assertRegex(
            self.step8b,
            r"(?i)Warn only when the database is SQLite \*\*and the LOADABLE total\*\*",
            "the warn decision still keys off the collected total")
        self.assertRegex(
            self.step8b, r"(?i)19,500-record collection under a 500-record cap therefore "
                         r"says \*\*nothing\*\*",
            "the reported case is not stated as the expected outcome")

    def test_both_numbers_are_stated_when_they_differ(self):
        self.assertRegex(
            self.step8b, r"(?i)State both numbers whenever they differ",
            "suppressing the collected figure would be worse than the defect")

    def test_sampling_is_not_re_offered_under_a_cap(self):
        self.assertRegex(
            self.step8b,
            r"(?i)Omit option 2 when the license already caps the load",
            "sampling is still offered one step after Step 8a decided it")
        self.assertRegex(
            self.step8b, r"(?i)INV-006 shape",
            "the reason it must not be re-offered is unstated")
        self.assertRegex(
            self.step8b, r"(?i)present all three unchanged",
            "the uncapped case must keep all three options")

    def test_the_timing_route_is_named_with_its_exact_query(self):
        self.assertIn("search_docs(query='hardware sizing capacity planning')", self.step8b,
                      "the step still says only 'consult the Senzing MCP server', which is "
                      "not a route")
        self.assertRegex(
            self.step8b, r"(?i)Hardware Sizing FAQ",
            "the document that carries the figures is not named")
        self.assertRegex(
            self.step8b, r"(?i)the wording matters",
            "a paraphrase of that query does not return the FAQ, and nothing says so")

    def test_the_sdk_guide_negative_carries_a_marker_with_its_owner(self):
        """INV-194: an absence claim needs the route that owns the fact."""
        raw = read()
        marker = re.search(r"<!-- MCP-NEGATIVE: sdk_guide\(topic='load'[^>]*-->", raw)
        self.assertIsNotNone(
            marker, "the 'sdk_guide returns no timing figures' claim has no MCP-NEGATIVE "
                    "marker, so no dry run will re-ask it")
        text = marker.group(0)
        self.assertIn("owner:", text, "the marker names no owning route (INV-194)")
        self.assertIn("hardware sizing capacity planning", text,
                      "the owner clause does not name the query that carries the figures")
        self.assertRegex(text, r"server 1\.32\.9, 2026-08-\d\d",
                         "the marker carries no server version and date")

    def test_the_never_substitute_rule_survives(self):
        self.assertRegex(
            self.step8b, r"(?i)never\s*substitute a remembered number",
            "the rule that an unavailable figure stays unavailable was lost")


if __name__ == "__main__":
    unittest.main()
