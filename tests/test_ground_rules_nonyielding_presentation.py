"""A step that presents results is still non-yielding, and must say so.

INV-225 makes a step with no 👉 non-yielding: it shares a turn with the next step that
asks. `ground-rules.md` states that, anticipates *runs* of such steps, and illustrates
them — but every illustration is a low-output step (a privacy reminder, a set of checks,
a generated scenario). The rule is a property of the **step** (does it ask?); nothing
addressed the property of the **output** (does it look finished?).

So the guide stopped where the output concluded something. On one dry-run walk
(2026-08-14) the same failure occurred three times, always ending a turn with **zero**
👉 questions:

    Phase C steps 17-20   -> ended on the orchestration summary and record counts
    Phase D steps 21-24   -> ended on validation results and evidence tables
    Module 7 steps 2-3a   -> ended on the five business answers

Twice the Bootcamper had to ask which question was pending. The `Stop` hook that would
catch this (INV-005) does not fire during a walk, so in a real bootcamp the hook would
paper over the prompt weakness and it would never be observed — only its symptom.

These tests pin the clause and the three site pointers, so a later consolidation cannot
drop them. The clause is asserted by its **requirement** — that a presentation-shaped
output is named as the likeliest false ending, and that the check before ending a turn
is stated — rather than by one exact sentence, so rewording that keeps the rule passes.

⚠️ Evidence caveat, carried from the spec: this is **one walk and one guide**, and
`phase3-conversational.md` is explicit that the assistant's own compliance is not
evidence. What raises it above a single slip is three recurrences with one structural
signature, in the two phases with the longest presentation-only runs in the plugin.

Source spec: `specs/results-presentation-turns-end-with-zero-questions.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
GROUND_RULES = SKILLS / "bootcamp-onboarding" / "ground-rules.md"
PHASE_C = SKILLS / "module-06-data-processing" / "phaseC-multi-source.md"
PHASE_D = SKILLS / "module-06-data-processing" / "phaseD-validation.md"
M7_PHASE1 = SKILLS / "module-07-query-visualize-discover" / "phase1-query-visualize.md"

SITES = [
    (PHASE_C, "17–20"),
    (PHASE_D, "21–24"),
    (M7_PHASE1, "2–3a"),
]


def squash(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


def nonyielding_section():
    """The 👉-protocol section that owns the non-yielding contract.

    Bounded so a clause landing somewhere else in the file cannot satisfy these
    assertions: the rule has to be reachable where the contract is stated (INV-183).
    """
    text = GROUND_RULES.read_text(encoding="utf-8")
    start = text.index("A step with no \U0001f449 question is NON-YIELDING")
    end = text.index("Anything meant to inform the answer goes BEFORE", start)
    return re.sub(r"\s+", " ", text[start:end])


class TheClauseIsStatedInTheProtocol(unittest.TestCase):
    def test_a_results_presentation_is_named_as_not_a_turn_ending(self):
        self.assertIn("results presentation is not a turn ending", nonyielding_section())

    def test_the_three_presentation_shapes_are_named(self):
        """Naming the shapes is what lets a guide recognise the case it is in."""
        section = nonyielding_section()
        for shape in ("summary", "evidence table", "set of answers"):
            self.assertIn(shape, section, "%r not named as a presentation shape" % shape)

    def test_it_says_the_rule_is_about_the_step_not_the_output(self):
        """The root cause: the guide read 'looks finished' as 'is finished'."""
        section = nonyielding_section()
        self.assertRegex(section, r"property of the \*\*step\*\*")
        self.assertRegex(section, r"never of the \*\*output\*\*")

    def test_the_check_before_ending_a_turn_is_stated_with_its_invariant(self):
        """A rule with no action is advice; the action is 'count the 👉 first'."""
        section = nonyielding_section()
        self.assertIn("exactly one \U0001f449", section)
        self.assertIn("INV-005", section)

    def test_the_clause_sits_inside_the_nonyielding_contract(self):
        """Reachable at the rule it qualifies, not filed elsewhere in the file."""
        section = nonyielding_section()
        self.assertLess(
            section.index("run of them is the same case"),
            section.index("results presentation is not a turn ending"),
            "the clause must follow the run-of-them bullet it extends",
        )


class TheSurroundingContractIsUnchanged(unittest.TestCase):
    """The clause is additive; the rules it sits between must survive it."""

    def test_the_existing_bullets_still_stand(self):
        section = nonyielding_section()
        for phrase in (
            "A run of them is the same case, not a worse one.",
            "Checkpoint boundaries are step boundaries, not turn boundaries.",
            "Report what happened, not each step.",
        ):
            self.assertIn(phrase, section, "%r was displaced" % phrase)

    def test_the_named_examples_survive(self):
        """The low-output examples are what the new clause contrasts against."""
        section = nonyielding_section()
        self.assertIn("the whole of System verification", section)
        self.assertIn("generated-scenario path", section)


class EachSiteCarriesAPointer(unittest.TestCase):
    """Criterion 2 — the rule is reinforced where it actually broke."""

    def test_each_phase_file_points_at_the_ground_rule(self):
        for path, _ in SITES:
            with self.subTest(path.name):
                self.assertIn(
                    "results presentation is not a turn ending",
                    squash(path),
                    "%s does not cross-reference the ground rule" % path.name,
                )

    def test_each_pointer_names_the_step_run_that_asks_nothing(self):
        """A pointer that does not say *which* steps cannot be checked against the file."""
        for path, steps in SITES:
            with self.subTest(path.name):
                self.assertIn("Steps %s ask nothing" % steps, squash(path))

    def test_each_pointer_says_the_turn_continues(self):
        for path, _ in SITES:
            with self.subTest(path.name):
                self.assertIn("this turn does not end here", squash(path))

    def test_no_pointer_restates_the_rule_instead_of_citing_it(self):
        """Restating drifts. The spec asks for a one-line cross-reference, not a copy."""
        for path, _ in SITES:
            with self.subTest(path.name):
                text = squash(path)
                self.assertNotIn("property of the **step**", text)
                self.assertNotIn("INV-225", text)


if __name__ == "__main__":
    unittest.main()
