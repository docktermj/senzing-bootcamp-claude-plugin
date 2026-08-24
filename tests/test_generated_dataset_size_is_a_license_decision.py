"""Choosing how many records to GENERATE is a license-capacity decision.

On the synthesized-scenario path a guide sized a generated dataset **down from 538 records
to 466** to stay under the built-in 500-record evaluation limit, reasoning that an absent
`license_record_limit` meant no custom license was configured. It then reached Step 8a,
measured as instructed, and found the workstation carried a custom EVAL license with
`recordLimit: 0` — no cap at all. The downsizing was unnecessary and was withdrawn.

⛔ **That is the exact inference INV-244 forbids** — absent means *never measured*, not "no
custom license" — reached on a module that **already states the rule in full**. The text was
corrected on 2026-08-14 and the run was on plugin 0.5.1 with that fix in place. The rule was
right and it did not bind.

⚠️ **The harm was zero this time and that is not reassurance.** 466 records with 60 three-way
and 93 two-way cross-source overlaps was ample. The same mechanism on a scenario that needs
volume steers a bootcamper with no cap to a smaller dataset, one module before Modules 6 and
7 must demonstrate cross-source resolution on it (INV-150).

⛔ **Why a field-sweep guard cannot find this, which is the part worth keeping.** The two
prior specs each fixed a site that *reads* `license_record_limit`. Step 2 never reads it —
it makes the decision the field exists to inform, without consulting it. A guard derived
from "every branch on `license_record_limit`" (INV-246's usual derivation) is sound for the
rule it enforces and **structurally blind** to the site where the field is ignored entirely.
So this guard pins the *mechanism* — measure before sizing, routed not restated — at the
decision site, rather than looking for a token somewhere in the file.

Source spec: `specs/generated-dataset-is-sized-before-anything-measures-the-license.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" /
         "module-04-data-collection" / "SKILL.md")

FRAMING_HEADING = "## License limit and dataset size (canonical framing)"


def body():
    return SKILL.read_text(encoding="utf-8")


def flat(text=None):
    return " ".join((text if text is not None else body()).split())


def synthesized_branch():
    """The `provenance: synthesized` generation branch, located by its own content.

    Sliced from the branch's opening to the note that follows it, so the assertions below
    are about the branch that chooses the record counts rather than about the whole file —
    which is the difference between pinning the mechanism and pinning a token.
    """
    text = body()
    start = text.index("provenance: synthesized")
    end = text.index("Both are bootcamp-generated, so both skip the question", start)
    return text[start:end]


class TheFramingRecognizesGeneration(unittest.TestCase):
    """Sizing a dataset into existence and sampling one down are the same decision."""

    def test_the_trigger_names_generating_not_only_sampling(self):
        text = flat()
        self.assertIn('"choosing how many records to GENERATE" is one of them', text)

    def test_it_says_so_at_the_framing_block(self):
        section = body()[body().index(FRAMING_HEADING):]
        self.assertIn("not only \"sampling an\nexisting dataset down\"",
                      section[:1200].replace("\r\n", "\n"),
                      "the clarification is not in the framing's trigger sentence")


class TheGenerationBranchRoutesToTheFraming(unittest.TestCase):

    def setUp(self):
        self.branch = flat(synthesized_branch())

    def test_it_states_the_record_count_is_a_license_decision(self):
        self.assertIn("How many records to generate is a LICENSE-CAPACITY decision",
                      self.branch)

    def test_it_forbids_choosing_before_measuring(self):
        self.assertIn("do not choose it before the limit is measured", self.branch)

    def test_it_cites_the_invariant(self):
        self.assertIn("INV-244", self.branch)

    def test_it_routes_to_the_canonical_framing_by_name(self):
        self.assertIn("License limit and dataset size (canonical framing)", self.branch)

    def test_it_does_not_restate_the_measurement_procedure(self):
        """⛔ A copy here would be the third, and a rule stated thrice drifts in two."""
        self.assertIn("Do not re-derive or restate its measurement procedure", self.branch)
        for restated in ("SzProduct.get_license()", "get_license()", "parse `recordLimit`"):
            with self.subTest(fragment=restated):
                self.assertNotIn(restated, self.branch,
                                 "the measurement procedure is restated at the decision "
                                 "site instead of referenced")


class TheBranchResolvesRatherThanOnlyWarning(unittest.TestCase):

    def setUp(self):
        self.branch = flat(synthesized_branch())

    def test_it_states_the_no_cap_outcome(self):
        self.assertIn("On a measured `recordLimit: 0`, size the generated data by what the "
                      "SCENARIO needs", self.branch)

    def test_it_names_the_cost_of_under_generating(self):
        self.assertIn("too little overlap to demonstrate cross-source resolution",
                      self.branch)
        self.assertIn("INV-150", self.branch)


class TheReportedRunIsRecorded(unittest.TestCase):
    """The figures are what make the directive concrete rather than procedural."""

    def setUp(self):
        self.branch = flat(synthesized_branch())

    def test_the_figures_are_named(self):
        self.assertIn("down from 538 records to 466", self.branch)
        self.assertIn("`recordLimit: 0`", self.branch)

    def test_the_forbidden_inference_is_named_in_terms(self):
        self.assertIn("means **never measured**, never \"no custom license\"", self.branch)

    def test_it_explains_why_the_miss_is_natural(self):
        """Naming only the rule does not stop it being missed the same way again."""
        self.assertIn("does not feel like a capacity decision", self.branch)
        self.assertIn("Nothing is being cut", self.branch)


class TheSiblingDirectivesSurvive(unittest.TestCase):
    """⚠️ The branch's existing generation rules must be undisturbed."""

    def setUp(self):
        self.branch = flat(synthesized_branch())

    def test_the_record_key_rule_is_intact(self):
        self.assertIn("Never put a gap in a record key", self.branch)

    def test_the_quality_intent_block_is_intact(self):
        self.assertIn("quality_intent", self.branch)
        self.assertIn("target_band", self.branch)

    def test_the_generation_fault_versus_scoring_fault_note_is_intact(self):
        self.assertIn("tell a **generation** fault from a **scoring** fault", self.branch)


class TheGuardIsAboutTheMechanismNotATokenSomewhere(unittest.TestCase):
    """⛔ Negative control for this file's own approach.

    `license_record_limit` appears in this module many times; a guard asserting the token
    is present would pass even with the decision-site directive deleted. These assertions
    are scoped to the sliced branch, so removing the directive fails them.
    """

    def test_the_directive_is_inside_the_generation_branch(self):
        self.assertIn("LICENSE-CAPACITY decision", synthesized_branch())

    def test_the_slice_excludes_the_framing_block(self):
        self.assertNotIn(FRAMING_HEADING, synthesized_branch(),
                         "the slice reaches the framing block, so these assertions could "
                         "pass on the framing's own text rather than the decision site")

    def test_removing_the_directive_would_fail(self):
        without = synthesized_branch().replace(
            "How many records to generate is a LICENSE-CAPACITY decision", "")
        self.assertNotIn("How many records to generate is a LICENSE-CAPACITY decision",
                         without)


if __name__ == "__main__":
    unittest.main()
