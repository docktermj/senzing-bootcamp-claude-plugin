"""The `mapping_workflow` call contract states what a malformed advance costs.

`mapping_workflow` rejects a payload its published advance schema forbids with an
`ENFORCEMENT NOTICE` naming a machine-readable reason code, and states a budget in its own
words: *"This is grammar-impossible advance N of 5 before this workflow terminates."* The
plugin's call contract covered what a **correct** call looks like -- `workspace_dir` on `start`,
the five action names, the opaque `state` echo -- and said nothing about the budget, so a guide
who slipped had no way to know the run was on a clock. Module 5 runs one workflow per source, so
the exposure is per source.

⛔ **The spec that asked for this got the semantics BACKWARDS, and the correction is the point.**
It reported the count as *"cumulative and does not reset"*, on a 2026-08-22 observation. Re-run
end to end on **server 1.33.0, 2026-08-23**:

  1. a bad payload at step 2 -> *"advance 1 of 5"*, `grammar_violation_count: 1` in `state`
  2. the next VALID advance -> a `state` with the field **absent**
  3. a bad payload at step 3 -> *"advance 1 of 5"* again, `grammar_violation_count: 1` -- not 2

So from the caller's side it counts **consecutive** failures. Documenting the spec's version
would have shipped a fresh false Senzing fact with a spec file making it look reviewed (INV-080),
and it would have overstated the hazard: losing a run needs five misses in a row, not five across
a multi-source session.

⚠️ **Also established: not every payload the published schema fails to describe is refused.**
One such shape advanced with `status: ok` and no notice on the same server and date. So a
rejection is evidence about that payload, never a general map of what the tool tolerates -- and
neither is a silent acceptance a sanction. The shipped text says exactly that and deliberately
names **no example**: the concrete case is a step-1 shape whose accepted-ness contradicts a dated
caution elsewhere in the same file, and stating it beside that caution would read as licensing the
shape the step tells readers not to send. `TheGuidanceOnARejectionIsPresent` therefore also
asserts the paragraph restates the array rule. The contradiction itself is recorded in
`specs/todo.md` as a finding for the audit rather than fixed here.

⛔ **This asserts the plugin SAYS the right thing, not that the server still behaves this way.**
The suite is offline (INV-108); the version and date on the claim are what a later run re-asks.
Per `specs/guards-pinning-a-dated-negative-outlive-it.md` the assertion checks that a
well-formed version and date are present, never which -- a guard that fails when a claim is
honestly re-verified is a guard that gets worked around.

Source spec: `specs/mapping-workflow-terminates-after-five-grammar-violations.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" /
            "module-05-data-quality-mapping" / "phase2-data-mapping.md")

SECTION_HEADING = "## Calling `mapping_workflow` correctly"

#: A dated MCP provenance stamp in the convention this file's other claims use. Deliberately
#: not pinned to a version or date (see the module docstring).
DATED_CLAIM = re.compile(r"server\s+\*{0,2}1\.\d+\.\d+\*{0,2},\s*\d{4}-\d{2}-\d{2}")


def contract_section():
    """The call-contract section, heading to the next `## ` heading."""
    text = CONTRACT.read_text(encoding="utf-8")
    start = text.index(SECTION_HEADING)
    following = re.search(r"^## ", text[start + len(SECTION_HEADING):], re.M)
    end = (start + len(SECTION_HEADING) +
           (following.start() if following else len(text)))
    return text[start:end]


def flat():
    return re.sub(r"\s+", " ", contract_section())


def budget_rule():
    """Rule 4 only -- numbered item 4 up to the next unindented paragraph.

    ⚠️ **Scoped after two negative controls ESCAPED.** Both `grammar_violation_count` and the
    dated server stamp were asserted against the whole section, so deleting them from the
    normative rule still passed: the token survived in the surrounding narrative, and a
    neighboring MCP claim carried its own stamp. An assertion that the *section* mentions
    something says nothing about whether the *rule* does.
    """
    section = contract_section()
    start = section.index("4. \u26d4 ")
    following = re.search(r"^\*\*If a step", section[start:], re.M)
    end = start + (following.start() if following else len(section) - start)
    return re.sub(r"\s+", " ", section[start:end])


class TheSectionIsFound(unittest.TestCase):
    def test_the_call_contract_section_exists(self):
        self.assertIn(
            SECTION_HEADING, CONTRACT.read_text(encoding="utf-8"),
            "the call-contract section is gone; this guard is inspecting nothing")

    def test_it_still_carries_its_original_three_rules(self):
        """The budget rule is an addition, not a replacement."""
        section = flat()
        for fragment in ("`start` requires BOTH `file_paths` and `data.workspace_dir`",
                         "exactly five actions",
                         "Echo the returned `state` verbatim"):
            with self.subTest(rule=fragment):
                self.assertIn(
                    fragment, section,
                    "the call contract lost %r — the budget rule was added beside the three "
                    "must-not-break rules, not in place of one" % fragment)


class TheBudgetIsStated(unittest.TestCase):
    def setUp(self):
        self.flat = flat()

    def test_it_states_the_five_violation_budget(self):
        self.assertRegex(
            self.flat, r"(?i)grammar-impossible advance N of 5|one of five, and five ends",
            "the contract does not state the five-violation budget, so a guide who slips has "
            "no way to know the run is on a clock")

    def test_it_names_where_the_count_is_visible(self):
        self.assertIn(
            "grammar_violation_count", budget_rule(),
            "the budget RULE does not name `grammar_violation_count`, so the budget is stated "
            "with no way to read the current position. (Scoped to rule 4: asserting the "
            "section mentions the token passed while the rule had lost it.)\n"
            "⚠️ Known limit, accepted deliberately: this passes if the token appears anywhere "
            "in rule 4, so moving it from the normative sentence into the adjacent verification "
            "paragraph is not caught. That relocation leaves the fact in front of the reader, "
            "which is what the assertion is for — and pinning the exact sentence would make the "
            "guard fail on correct rewording, the failure mode that gets guards loosened.")

    def test_it_names_the_reason_code_shape(self):
        self.assertRegex(
            self.flat, r"step\d_[a-z_]+",
            "the contract does not show a reason code (e.g. `step2_missing_plan_key`), so a "
            "reader cannot recognize an enforcement notice when they get one")


class TheResetSemanticsAreStatedCorrectly(unittest.TestCase):
    """The half the source spec got backwards. Both directions are asserted."""

    def setUp(self):
        self.flat = flat()

    def test_it_says_a_successful_advance_clears_the_count(self):
        self.assertRegex(
            self.flat, r"(?i)A successful advance clears it",
            "the contract does not say a valid advance clears the count — the behavior "
            "measured on 1.33.0")

    def test_it_says_the_counting_is_consecutive(self):
        self.assertRegex(
            self.flat, r"(?i)\*\*consecutive\*\* failures|consecutive failures",
            "the contract does not say the counting is consecutive")

    def test_it_does_not_claim_the_count_is_cumulative(self):
        self.assertNotRegex(
            self.flat, r"(?i)cumulative and does not reset|is cumulative for the run",
            "the contract claims the count is cumulative — the source spec's reading, which "
            "1.33.0 contradicts. Writing it would be a fresh false Senzing fact (INV-080)")

    def test_it_records_that_the_reset_mechanism_is_not_observable(self):
        """Honesty about the limit of the measurement, not a claim about server internals."""
        self.assertRegex(
            self.flat, r"(?i)not observable from here",
            "the contract asserts a mechanism it cannot see. Whether the server resets a "
            "counter or rebuilds `state` per step is indistinguishable from the caller's "
            "side; say so rather than picking one")


class TheGuidanceOnARejectionIsPresent(unittest.TestCase):
    def setUp(self):
        self.flat = flat()

    def test_it_says_to_re_read_the_advance_schema(self):
        self.assertRegex(
            self.flat, r"(?i)re-read the response's `advance_schema`",
            "the contract does not tell the reader to re-read `advance_schema` on a rejection")

    def test_it_forbids_retrying_a_variant(self):
        self.assertRegex(
            self.flat, r"(?i)do not retry a variant",
            "the contract does not forbid guessing again — the behavior that spends a second "
            "violation")

    def test_it_states_the_per_source_exposure(self):
        self.assertRegex(
            self.flat, r"(?i)per source rather than per module",
            "the contract does not state that the budget is per workflow run while this "
            "module starts one run per source")

    def test_it_bounds_what_a_rejection_proves(self):
        self.assertRegex(
            self.flat, r"(?i)never a general map of what the tool tolerates",
            "the contract does not say a rejection is evidence about that payload only. Some "
            "payloads the published schema does not describe are accepted silently, so neither "
            "direction of inference is sound")

    def test_it_reaffirms_each_step_s_stated_shape(self):
        """The bound must not read as permission to send whatever is silently accepted.

        ⚠️ **This assertion exists because the first draft tripped an existing guard.**
        `test_tool_directives_do_not_override_interaction` forbids the phrase "object form
        advanced" in this file, and rightly: the step-1 caution's whole job is to send readers to
        the ARRAY form of `profile_summary`. Naming the accepted-but-undescribed shape as an
        example — even as a true observation — sat one sentence away from guidance that says the
        opposite, so the example was removed and the array rule is restated instead.
        """
        self.assertRegex(
            self.flat, r"(?i)Follow each step's stated shape regardless",
            "the rejection-bound paragraph does not reaffirm following each step's stated "
            "shape, so it reads as licensing whatever the server happens to accept")
        self.assertRegex(
            self.flat, r"(?i)\*\*array\*\* form of `profile_summary`",
            "the paragraph does not point back at the array form at step 1 — the one shape a "
            "reader must not be talked out of")


class TheClaimCarriesItsProvenance(unittest.TestCase):
    def test_the_budget_rule_is_dated_with_a_server_version(self):
        self.assertRegex(
            budget_rule(), DATED_CLAIM,
            "the budget claim carries no `server <version>, <date>` stamp, so a later reader "
            "cannot tell whether it still holds. The suite is offline (INV-108) — the date IS "
            "the re-check mechanism. (Scoped to rule 4: a neighboring MCP claim's own stamp "
            "made a section-wide assertion pass with this one deleted)")

    def test_the_dating_convention_matches_its_neighbors(self):
        """Anti-vacuity: the pattern above must match the section's pre-existing claims too."""
        self.assertGreaterEqual(
            len(DATED_CLAIM.findall(flat())), 1,
            "no dated server claim found in the section at all; the convention this asserts "
            "conformance to is not present")


if __name__ == "__main__":
    unittest.main()
