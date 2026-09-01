"""The screenshot-embed rule names a moment both capturing modules can actually reach.

`module-completion.md`'s "Visualization screenshots" bullet required every captured image to
be added to the module's **Actions Taken** *"in the same turn the capture ran"*. In both
modules that capture, the capture and the recap append are separated by **two deliberate 👉
gates**:

    capture (phase1 Step 2.4)
      -> 👉 guided tour: "Are you ready to continue?"
      -> 👉 teardown consent: "Ready for me to stop the visualization server...?"
    recap section appended (phase2 close -> module completion)

At capture time the module's `## {Name}` recap section does not exist, so there is no Actions
Taken to write into. Observed live 2026-08-31: six captures written against a running server,
recap section created two gates later. No previous phase-3 walk had reached a capture.

⚠️ The *unsatisfiable-instruction* class again. The section's own next sentence already
supplied the operational answer ("record it at the step checkpoint"), so a careful reader
landed correctly — but the two clauses were in tension and the emphatic one was the impossible
one. The cost is not lost images; it is teaching that these rules are approximate.

⛔ The force of the requirement must not soften. It is emphatic because a previous run captured
images and never embedded them, and graduation had to backfill.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "plugins" / "senzing-bootcamp" / "skills"
COMPLETION = SKILLS / "bootcamp-onboarding" / "module-completion.md"


def flat(s):
    return re.sub(r"\s+", " ", s)


def screenshot_bullet():
    text = COMPLETION.read_text(encoding="utf-8")
    start = text.index("- **Visualization screenshots:**")
    end = text.index("\n  ```markdown", start)
    return text[start:end]


class TheImpossibleTimingIsGone(unittest.TestCase):
    def test_no_rule_requires_the_embed_in_the_capture_turn(self):
        """Pinned by its exact historical wording: it reads correct and cannot be obeyed."""
        self.assertNotRegex(
            flat(COMPLETION.read_text(encoding="utf-8")),
            r"(?i)in the same turn the capture ran, in the app's tab order",
            "The embed must not be required in the capture's own turn. Both capturing modules "
            "put two deliberate 👉 gates between the capture and the recap append, so at "
            "capture time there is no Actions Taken section to write into.",
        )

    def test_the_two_moments_are_named_separately(self):
        self.assertRegex(
            flat(screenshot_bullet()), r"(?i)two moments, not one",
            "The rule must separate recording from embedding. Collapsing them is what made it "
            "unsatisfiable, and a reader who notices the impossibility has no sanctioned "
            "alternative to fall back on.",
        )

    def test_the_checkpoint_is_named_as_the_carrier(self):
        """The spec's third criterion — the mechanism, not just the corrected timing."""
        self.assertRegex(
            flat(screenshot_bullet()),
            r"(?i)checkpoint is what carries the capture across",
            "The step checkpoint must be named as what carries the capture across the turn "
            "boundaries. Without the mechanism, 'embed later' is an instruction with no state "
            "behind it — and the failure it replaces was a capture recorded nowhere.",
        )

    def test_the_embed_happens_where_the_section_exists(self):
        self.assertRegex(
            flat(screenshot_bullet()),
            r"(?i)when this module's Actions Taken is written, at module close",
            "The embed must be tied to the moment the section is written. That is the first "
            "turn in which the target of the instruction exists.",
        )


class TheRequirementKeepsItsForce(unittest.TestCase):
    """⛔ Fixing the timing must not soften what the rule demands."""

    def setUp(self):
        self.bullet = flat(screenshot_bullet())

    def test_embedding_is_still_required_and_uncapped(self):
        self.assertRegex(
            self.bullet, r"(?i)embedding every screenshot it produced is required",
            "The embed must remain required, not optional (INV-146).",
        )
        self.assertRegex(
            self.bullet, r"(?i)no count cap applies",
            "The no-count-cap clause must survive — it is what stops a guide embedding two of "
            "six and calling it done.",
        )

    def test_the_backfill_history_is_kept_as_the_reason(self):
        self.assertRegex(
            self.bullet, r"(?i)graduation has to backfill",
            "The reason the rule is emphatic must survive the rewrite: a previous run captured "
            "images, embedded none, and graduation backfilled. A rule whose reason is deleted "
            "is one the next editor relaxes.",
        )

    def test_the_tab_order_requirement_survives(self):
        self.assertRegex(
            self.bullet, r"(?i)in the app's tab order",
            "Tab order must survive — it is what makes the recap's images legible as a tour "
            "rather than an unordered dump.",
        )


class TheSurroundingRulesAreUntouched(unittest.TestCase):
    """The spec says explicitly to leave the rest of the section alone."""

    def setUp(self):
        self.text = flat(COMPLETION.read_text(encoding="utf-8"))

    def test_the_relative_path_rule_survives(self):
        self.assertRegex(
            self.text, r"(?i)never `docs/visualizations/…`",
            "INV-161's relative-path rule must survive — a `docs/`-prefixed path resolves to "
            "`docs/docs/…` and drops the image from both the Markdown and the PDF.",
        )

    def test_the_own_line_block_form_survives(self):
        self.assertRegex(
            self.text, r"(?i)Each image goes on a line of its own",
            "INV-242's own-line block form must survive.",
        )

    def test_the_artifact_verification_rule_survives(self):
        self.assertRegex(
            self.text, r"(?i)verify the artifact itself, not the exit code",
            "The verify-the-artifact rule must survive — it is what catches a capture helper "
            "that exits 0 having written three images of the same tab.",
        )


if __name__ == "__main__":
    unittest.main()
