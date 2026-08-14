"""A 👉 question's answer options render beneath it — including a runtime-generated list.

Bootcamp preparation's programming-language gate was the only ⛔ 👉 gate in the module whose
options were not written inside the pinned question, because they come from
`get_capabilities` at runtime and so cannot be pinned. The file split them: the numbered-list
instruction and the platform annotations, then the pinned question alone. Read top to bottom
that is list-then-question; read against Steps 1–3 it is question-then-list. Both are
defensible, so the same gate could render two ways between runs — and in the list-first form
the question says "reply with a number" while the numbers sit above it, separated on macOS
and Windows by several lines of per-language Docker routing.

The ground rules did not settle it either: they say numbered choices "that are part of the
question … are not 'after'" the 👉, which *permits* the options to follow but does not
*require* it, while the same paragraph's main rule pulls the other way for a reader who
treats a generated list as informational.

Source spec: `specs/language-gate-does-not-say-where-its-options-render.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
GROUND_RULES = PLUGIN / "skills" / "bootcamp-onboarding" / "ground-rules.md"
PREPARATION = PLUGIN / "skills" / "bootcamp-preparation" / "SKILL.md"

LANGUAGE_GATE = ("👉 **Which programming language would you like to use for the bootcamp? "
                 "Reply with a number:**")


def read(path):
    return path.read_text(encoding="utf-8")


def squash(text):
    return re.sub(r"\s+", " ", text)


class TheGeneralRuleIsStated(unittest.TestCase):
    def setUp(self):
        self.flat = squash(read(GROUND_RULES))

    def test_options_are_required_below_the_question_not_merely_permitted(self):
        self.assertRegex(
            self.flat,
            r"(?i)answer options render DIRECTLY BENEATH it",
            "the ground rules still only permit options to follow the 👉; nothing decides "
            "the rendering, so two runs of the same gate can differ")

    def test_it_covers_a_runtime_generated_list(self):
        self.assertRegex(
            self.flat, r"(?i)pinned or generated at\s*runtime",
            "the rule does not reach a list built at runtime, which is the only kind that "
            "was ambiguous")
        self.assertRegex(
            self.flat,
            r"(?i)being\s*unpinnable changes only whether the text is fixed, never where it sits",
            "nothing says why unpinnable options are still the question's options")

    def test_it_separates_informational_prose_from_per_option_annotation(self):
        self.assertRegex(
            self.flat, r"(?i)a per-option annotation is not informational",
            "the rule does not say where a per-option annotation goes, which is what put "
            "several lines of Docker routing between the numbers and the question")


class TheLanguageGateSaysWhereItsOptionsGo(unittest.TestCase):
    def setUp(self):
        self.text = read(PREPARATION)
        self.flat = squash(self.text)

    def test_the_pinned_question_is_unchanged(self):
        """INV-056. The fix is about placement, not wording."""
        self.assertIn(LANGUAGE_GATE, self.text, "the pinned question's wording moved")

    def test_the_pinned_question_appears_exactly_once(self):
        """A shape example that repeats the question reads as a second gate (INV-006)."""
        self.assertEqual(
            1, self.text.count(LANGUAGE_GATE),
            "the language gate's wording appears more than once, so a reader cannot tell "
            "whether it is asked twice")

    def test_step_4_states_the_placement(self):
        self.assertRegex(
            self.flat,
            r"(?i)rendered \*?\*?directly beneath the 👉\s*question, as part of it",
            "Step 4 does not say where the MCP-returned options render")
        self.assertRegex(
            self.flat, r"(?i)the same shape Steps 1–3 use",
            "Step 4 does not tie its shape to the steps it must match")

    def test_step_4_shows_the_resulting_shape(self):
        self.assertRegex(
            self.flat, r"(?i)the resulting shape",
            "Step 4 states the rule without showing it, which is what left two readings")
        self.assertIn("Detected platform: Linux (apt).", self.text,
                      "the shape example does not show the informational line above the 👉")

    def test_the_shape_example_does_not_duplicate_the_question(self):
        self.assertIn("<the pinned 👉 question below, verbatim>", self.text,
                      "the example should reference the pinned question rather than "
                      "restating it")

    def test_all_four_platform_cases_are_classified(self):
        """Criterion: platform-wide (before the 👉) vs per-option (on the option)."""
        cases = {
            "macOS Apple Silicon": "per-option",
            "macOS Intel": "platform-wide",
            "Windows": "per-option",
            "Linux": "platform-wide",
        }
        for platform, kind in cases.items():
            with self.subTest(platform=platform):
                pattern = r"\*\*%s:\*\* %s" % (re.escape(platform), kind)
                self.assertRegex(
                    self.flat, pattern,
                    "%s is not classified as %s, so a guide cannot tell whether its note "
                    "goes above the question or on an option" % (platform, kind))

    def test_the_platform_wide_cases_say_to_put_it_above_the_question(self):
        for phrase in ("Say it once, above the 👉", "Say that once above the"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.flat,
                              "a platform-wide statement is classified but not placed")

    def test_a_per_option_note_is_forbidden_above_the_question(self):
        self.assertRegex(
            self.flat,
            r"(?i)never hoisted\s*above the question",
            "nothing forbids hoisting a per-option annotation above the 👉, which is the "
            "rendering that separated the numbers from the instruction to use them")


if __name__ == "__main__":
    unittest.main()
