"""Tests that model/effort guidance honors the `model_guidance` preference.

INV-119 replaced an unconditional blocking nudge with a mode the bootcamper picks
once: `advisory` (default, zero extra turns), `off` (silent), or `prompt` (the
former INV-063/INV-069 two-gate flow). The design has already oscillated twice —
INV-062 was non-blocking, INV-063 made it blocking, INV-069 added a second gate,
and INV-119 makes all of that conditional. Each swing was a bootcamper request,
so the risk is not that someone disagrees; it is that a future edit quietly
restores one mode's behavior as the universal one.

These tests pin the parts that must not drift back:

1. The preference is asked once, in Bootcamp preparation, with all three modes.
2. Every reader defaults to `advisory` when the preference is missing.
3. The "Are you done modifying the model and effort?" gate is scoped to `prompt`
   in every file that contains it.
4. The advisory line carries what INV-120 requires it to say.

Run:  python3 -m unittest discover -s tests
"""
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")
GROUND_RULES = os.path.join(PLUGIN, "skills", "bootcamp-onboarding", "ground-rules.md")
GRADUATION = os.path.join(PLUGIN, "skills", "graduation", "SKILL.md")
PREPARATION = os.path.join(PLUGIN, "skills", "bootcamp-preparation", "SKILL.md")
MODEL_SELECTION = os.path.join(PLUGIN, "docs", "model-selection.md")

# The gate INV-119 confines to `prompt`. Any file that still contains it must
# also say which mode it belongs to.
DONE_GATE = "Are you done modifying the model and effort?"

# Files that surface the nudge and therefore must read the preference.
NUDGE_READERS = [GROUND_RULES, GRADUATION]


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def shipped_markdown():
    for dirpath, dirnames, filenames in os.walk(PLUGIN):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


class TestPreferenceIsAskedOnce(unittest.TestCase):
    def test_preparation_asks_the_question(self):
        text = read(PREPARATION)
        self.assertIn(
            "How would you like model guidance handled?",
            text,
            "Bootcamp preparation must ask the model_guidance question (INV-119).",
        )

    def test_all_three_modes_are_offered(self):
        text = read(PREPARATION)
        for mode in ("advisory", "off", "prompt"):
            self.assertIn(
                mode,
                text,
                f"Bootcamp preparation must name the `{mode}` mode (INV-119).",
            )

    def test_preference_is_persisted_in_the_consolidated_write(self):
        text = read(PREPARATION)
        self.assertIn(
            "`model_guidance`",
            text,
            "model_guidance must be listed in the consolidated preference write "
            "(INV-058/INV-119).",
        )

    def test_asked_only_once(self):
        """The question belongs to preparation alone — not repeated per module."""
        offenders = [
            path
            for path in shipped_markdown()
            if "How would you like model guidance handled?" in read(path)
            and os.path.abspath(path) != os.path.abspath(PREPARATION)
        ]
        self.assertEqual(
            [],
            offenders,
            "The model_guidance question must be asked once in Bootcamp "
            f"preparation (INV-006/INV-119); also found in: {offenders}",
        )


class TestReadersDefaultToAdvisory(unittest.TestCase):
    def test_each_reader_reads_the_preference(self):
        for path in NUDGE_READERS:
            with self.subTest(path=os.path.relpath(path, REPO_ROOT)):
                self.assertIn(
                    "model_guidance",
                    read(path),
                    "A file that surfaces the nudge must read the "
                    "model_guidance preference (INV-119).",
                )

    def test_each_reader_defaults_to_advisory(self):
        for path in NUDGE_READERS:
            with self.subTest(path=os.path.relpath(path, REPO_ROOT)):
                text = read(path)
                self.assertIn(
                    "treat as `advisory`",
                    text,
                    "A missing or unreadable model_guidance must fall back to "
                    "`advisory`, never to silence or to a gate (INV-119).",
                )


class TestDoneGateIsScopedToPrompt(unittest.TestCase):
    def test_every_file_with_the_gate_scopes_it(self):
        """The gate may exist, but only as the `prompt` mode's behavior."""
        for path in shipped_markdown():
            text = read(path)
            if DONE_GATE not in text:
                continue
            with self.subTest(path=os.path.relpath(path, REPO_ROOT)):
                self.assertIn(
                    "`prompt`",
                    text,
                    f"{DONE_GATE!r} appears here without naming the `prompt` "
                    "mode it belongs to — under `advisory`/`off` there is "
                    "nothing to wait for (INV-119).",
                )

    def test_gate_is_confined_to_the_two_known_skills(self):
        """A new skill growing this gate is a regression worth catching.

        Scoped to `skills/` — the files the guide actually loads. `docs/` may
        quote the gate while describing the `prompt` mode; that is a maintainer
        reference, not a place the question gets asked.
        """
        skills_root = os.path.join(PLUGIN, "skills")
        expected = {os.path.abspath(GROUND_RULES), os.path.abspath(GRADUATION)}
        found = {
            os.path.abspath(path)
            for path in shipped_markdown()
            if os.path.abspath(path).startswith(os.path.abspath(skills_root))
            and DONE_GATE in read(path)
        }
        self.assertEqual(
            expected,
            found,
            "The done-modifying gate must live only in ground-rules.md and "
            "graduation/SKILL.md, both scoped to `prompt` (INV-119).",
        )


class TestAdvisoryLineContent(unittest.TestCase):
    """INV-120: what the advisory line must say."""

    def test_names_the_current_setting(self):
        self.assertIn(
            "current model and effort",
            read(GROUND_RULES),
            "The advisory line must name the bootcamper's current model and "
            "effort beside the recommendation (INV-120).",
        )

    def test_treats_model_and_effort_as_separate_dials(self):
        self.assertIn(
            "independent dials",
            read(GROUND_RULES),
            "Model and effort must be named as separate dials (INV-120).",
        )

    def test_states_change_anytime(self):
        self.assertIn(
            "changed at any time",
            read(GROUND_RULES),
            "The advisory line must say either dial can change at any time "
            "(INV-120).",
        )

    def test_flags_a_downgrade(self):
        self.assertIn(
            "advice to downgrade",
            read(GROUND_RULES),
            "A recommendation below the current setting must be flagged as a "
            "downgrade (INV-120).",
        )

    def test_documented_for_maintainers(self):
        text = read(MODEL_SELECTION)
        for mode in ("`advisory`", "`off`", "`prompt`"):
            self.assertIn(
                mode,
                text,
                f"docs/model-selection.md must document the {mode} mode "
                "(INV-119).",
            )


if __name__ == "__main__":
    unittest.main()
