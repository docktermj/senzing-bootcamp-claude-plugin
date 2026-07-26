"""Model/effort guidance is unconditional — no question, no preference, no modes.

Renamed from `test_model_guidance_modes.py` on 2026-07-26, because the modes it was
written to protect are gone and a test file named after them would mislead.

**This design has now swung four times**, every swing a deliberate decision:

| | Behavior |
|---|---|
| INV-062 | non-blocking suggestion |
| INV-063 | blocking switch question when the recommendation changes |
| INV-069 | plus a second confirmation gate |
| INV-119/INV-120 | all of it conditional on an `advisory`/`off`/`prompt` preference |
| **INV-137** | unconditional again; the preference and its question retired |

So the risk this file guards is specific and has materialised before: a future edit
quietly reinstating one of the retired shapes, or a stale `model_guidance` read
surviving in a file nobody thought to check. What must hold now:

1. The capture question exists **nowhere**.
2. No shipped skill instructs the guide to read, honor or persist `model_guidance`.
3. The done-modifying gate lives in exactly two files and is scoped to **no** mode.
4. The requirements INV-137 explicitly retains from INV-120 — separate dials,
   changeable at any time, a below-current recommendation flagged as a downgrade —
   still appear, now on the recommendation-unchanged statement.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")
GROUND_RULES = os.path.join(PLUGIN, "skills", "bootcamp-onboarding", "ground-rules.md")
GRADUATION = os.path.join(PLUGIN, "skills", "graduation", "SKILL.md")
PREPARATION = os.path.join(PLUGIN, "skills", "bootcamp-preparation", "SKILL.md")
MODEL_SELECTION = os.path.join(PLUGIN, "docs", "model-selection.md")

QUESTION = "How would you like model guidance handled?"
DONE_GATE = "Are you done modifying the model and effort?"
SWITCH_QUESTION = "Would you like to switch to"

# Phrasings that would mean a file is treating the retired preference as live.
LIVE_PREFERENCE_USE = re.compile(
    r"(Read|read|honou?r|Honou?r|persist|Persist|carry)\s+[^.\n]{0,40}`model_guidance`"
    r"|`model_guidance`[^.\n]{0,30}(from|to)\s+`config/bootcamp_preferences\.yaml`",
)

# Mode-gated phrasings retired by INV-137.
RETIRED_MODE_PHRASINGS = (
    "belongs to `prompt` alone",
    "Under `advisory`",
    "treat as `advisory`",
    "`advisory` (the default)",
    "absent-means-`advisory`",
    "The three modes",
)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def shipped_markdown():
    for dirpath, dirnames, filenames in os.walk(PLUGIN):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def skill_markdown():
    root = os.path.join(PLUGIN, "skills")
    return [p for p in shipped_markdown() if os.path.abspath(p).startswith(os.path.abspath(root))]


class TestTheQuestionIsGone(unittest.TestCase):

    def test_no_shipped_file_asks_it(self):
        offenders = [
            os.path.relpath(p, REPO_ROOT) for p in shipped_markdown() if QUESTION in read(p)
        ]
        self.assertEqual(
            [],
            offenders,
            f"the retired model-guidance question is asked in: {offenders}. INV-137 "
            "removes it entirely — the choice is not the Bootcamper's to make.",
        )

    def test_preparation_records_that_it_is_retired(self):
        """A note in its place, so a future edit does not silently re-add it."""
        text = read(PREPARATION)
        self.assertRegex(
            text,
            r"no `model_guidance` preference|model[- ]guidance question.{0,40}retired"
            r"|retired.{0,60}model.guidance",
            "Bootcamp preparation should state that the question is retired, so the "
            "absence is deliberate rather than looking like an omission.",
        )

    def test_the_consolidated_write_does_not_persist_it(self):
        text = read(PREPARATION)
        write_step = text[text.index("## 6.") : text.index("## 7.")]
        self.assertNotRegex(
            write_step,
            r"`model_guidance`\s*\(",
            "Step 6 must not persist model_guidance — the key is retired (INV-137)",
        )


class TestNoFileTreatsThePreferenceAsLive(unittest.TestCase):

    def test_no_skill_reads_or_honors_it(self):
        offenders = []
        for path in skill_markdown():
            for n, line in enumerate(read(path).splitlines(), 1):
                if LIVE_PREFERENCE_USE.search(line):
                    offenders.append(f"{os.path.relpath(path, REPO_ROOT)}:{n}")
        self.assertEqual(
            [],
            offenders,
            f"file(s) still instruct reading/honoring `model_guidance`: {offenders}. "
            "INV-137 retires the key; a stale value must not be honored.",
        )

    def test_no_retired_mode_phrasing_survives(self):
        offenders = []
        for path in shipped_markdown():
            text = read(path)
            for phrase in RETIRED_MODE_PHRASINGS:
                if phrase in text:
                    offenders.append(f"{os.path.relpath(path, REPO_ROOT)}: {phrase!r}")
        self.assertEqual(
            [],
            offenders,
            f"mode-gated phrasing retired by INV-137 survives: {offenders}",
        )


class TestTheUnconditionalFlowIsIntact(unittest.TestCase):
    """The behavior INV-137 restores must actually be described."""

    def test_both_nudge_readers_carry_the_switch_question(self):
        for path in (GROUND_RULES, GRADUATION):
            with self.subTest(path=os.path.basename(path)):
                self.assertIn(SWITCH_QUESTION, read(path))

    def test_the_gate_lives_in_exactly_the_two_nudge_skills(self):
        expected = {os.path.abspath(GROUND_RULES), os.path.abspath(GRADUATION)}
        found = {os.path.abspath(p) for p in skill_markdown() if DONE_GATE in read(p)}
        self.assertEqual(
            expected,
            found,
            "the done-modifying gate must live only in ground-rules.md and "
            "graduation/SKILL.md",
        )

    def test_the_gate_follows_a_yes_and_nothing_else(self):
        for path in (GROUND_RULES, GRADUATION):
            with self.subTest(path=os.path.basename(path)):
                self.assertRegex(
                    read(path),
                    r"follows a \*\*yes\*\* to the switch and nothing else",
                    "each nudge reader must state that the confirmation gate follows a "
                    "yes to the switch only — never a decline (INV-137)",
                )

    def test_ground_rules_states_it_is_unconditional(self):
        self.assertRegex(
            read(GROUND_RULES),
            r"unconditional",
            "ground-rules must say the behavior is unconditional, since the previous "
            "design made it conditional and the distinction is the whole change",
        )


class TestRetainedInv120Content(unittest.TestCase):
    """INV-137 keeps these requirements; only their host sentence moved."""

    def setUp(self):
        self.text = read(GROUND_RULES)

    def test_separate_dials(self):
        self.assertRegex(self.text, r"separate dials|independent dials")

    def test_changeable_at_any_time(self):
        self.assertIn("changed at any time", self.text)

    def test_a_downgrade_is_flagged(self):
        self.assertIn("advice to downgrade", self.text)


class TestMaintainerDocMatches(unittest.TestCase):

    def test_it_documents_the_unconditional_behavior(self):
        text = read(MODEL_SELECTION)
        self.assertRegex(
            text,
            r"not configurable|unconditional",
            "docs/model-selection.md must describe guidance as unconditional (INV-137)",
        )
        self.assertIn("INV-137", text)

    def test_it_does_not_present_the_modes_as_live(self):
        text = read(MODEL_SELECTION)
        self.assertNotRegex(
            text,
            r"\| `advisory` \*\(default\)\*",
            "the three-mode table is retired; keep only the historical note",
        )


if __name__ == "__main__":
    unittest.main()
