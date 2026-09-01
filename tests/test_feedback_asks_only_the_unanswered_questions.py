"""The feedback flow asks only what the Bootcamper's message has not already answered.

Step 2 lists five questions and named exactly one shortcut: "If the bootcamper gives
everything in one message, do not re-ask". Real feedback usually arrives *partially*
complete -- one sentence naming the subject, what happened, and often a suggested fix,
leaving why-it-matters and priority open. That case fell between the two the step
covered, and the literal reading re-asks three questions the Bootcamper just answered.

INV-006 forbids exactly that, and the flow is where it costs most: someone reporting a
defect is already spending goodwill. The sibling any-time control gets it right and
states the rule outright -- ``notes.md`` Step 2: "If the triggering message already
carries the note, take it from the message and do not ask."

Observed live on 2026-08-31 during a `/dry-run` walk, when a Bootcamper opened with a
message answering questions 1, 2 and 4.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ONBOARDING = REPO / "plugins" / "senzing-bootcamp" / "skills" / "bootcamp-onboarding"
FEEDBACK = ONBOARDING / "feedback.md"
NOTES = ONBOARDING / "notes.md"


def step_2():
    text = FEEDBACK.read_text(encoding="utf-8")
    start = text.find("## Step 2:")
    assert start != -1, "feedback.md Step 2 was not found -- has it been renamed?"
    nxt = text.find("\n## ", start + 1)
    return text[start: nxt if nxt != -1 else len(text)]


class OnlyUnansweredQuestionsAreAsked(unittest.TestCase):
    def setUp(self):
        self.section = step_2()
        self.flat = re.sub(r"\s+", " ", self.section)

    def test_the_rule_covers_a_partially_answered_message(self):
        """The general rule, not the all-or-nothing special case."""
        self.assertRegex(
            self.flat,
            r"(?i)(only the questions|only the gaps|not already answered|has not already answered)",
            "Step 2 must instruct asking only the questions the message has not already answered. "
            "An all-or-nothing shortcut leaves the partial case -- the common one -- to be resolved "
            "either by re-asking (an INV-006 violation) or by improvisation.",
        )

    def test_partial_supply_is_named_explicitly(self):
        """'Gives everything' must read as an instance of the rule, not as the rule."""
        self.assertRegex(
            self.flat, r"(?i)(in whole or in part|partial)",
            "Step 2 must name the partially-answered message. Without it a reader applies the "
            "shortcut only to a message that answers all five, which is the rarer shape.",
        )

    def test_the_all_or_nothing_shortcut_is_no_longer_the_only_guidance(self):
        """Negative form: the old sentence alone must not be what the step says.

        ⚠️ Asserts the INSTRUCTION rather than a keyword. Three guards in this
        session passed against the defect they were written for because neighboring
        prose satisfied a vocabulary match, so this checks that the general rule is
        present and NOT merely that the words appear somewhere in the section.
        """
        has_general = re.search(
            r"(?i)ask only the questions[^.]{0,80}not already answered", self.flat)
        self.assertIsNotNone(
            has_general,
            "Step 2's guidance must lead with the general rule -- ask only what is unanswered. "
            "The 'gives everything' case is one instance of it and cannot stand alone.",
        )

    def test_no_question_in_step_2_was_pinned_by_this_change(self):
        """The spec's third criterion: these questions are not INV-056 pinned today."""
        self.assertNotIn(
            "INV-056", self.section,
            "Step 2's questions are not pinned verbatim, and this change must not make them so. "
            "Pinning wording nobody reviewed for pinning is a larger commitment than the fix.",
        )


class TheSiblingControlStatesTheSameRule(unittest.TestCase):
    """The two any-time controls must not disagree about re-asking."""

    def test_notes_still_forbids_re_asking_what_was_already_said(self):
        """Asserts notes.md's INSTRUCTION, quoted from the file rather than paraphrased.

        ⚠️ The first version of this assertion pinned a paraphrase -- "do not ask
        what they want to note when they already said it" -- which appears nowhere in
        notes.md. It failed against a correct fix, and had the paraphrase happened to
        match some neighboring prose it would have passed while checking nothing. A
        precedent is cited by its text, not by a remembered gist of it.
        """
        self.assertRegex(
            re.sub(r"\s+", " ", NOTES.read_text(encoding="utf-8")),
            r"(?i)already carries the note[^.]{0,80}do not ask",
            "notes.md is the precedent this fix follows -- the same rule for the sibling any-time "
            "control. If it changes, the two controls have drifted and feedback.md should be "
            "re-checked against it rather than silently diverging.",
        )


if __name__ == "__main__":
    unittest.main()
