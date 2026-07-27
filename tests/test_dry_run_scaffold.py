"""The dry-run skill's scaffold must actually reach the paths it claims to.

`.claude/skills/dry-run/` documents a methodology, and its `scaffold_project.py`
builds the fixture that methodology depends on. A fixture that quietly stops
exercising a path turns the whole exercise into theatre — and that is not
hypothetical: the scaffold's **first version had exactly that bug**. Its recap's
longest module chip was 41 characters against a 46-character clip threshold, so it
reproduced the precise blind spot the skill documents as the reason a renderer crash
survived three audits. A comment claimed it was "deliberately longer". It was not.

So the one claim worth pinning in code is the numeric one: the in-progress heading
the scaffold writes must exceed the narrowest clip width the recap generator actually
uses, both read from source rather than hardcoded here. Shorten the heading, rename
the module, or change the generator's widths, and this fails.

The scaffold is a maintainer tool under `.claude/`, which `propagate.sh` never
mirrors, so nothing here ships to bootcampers (INV-108 keeps this test in the
repo-level `tests/`, stdlib only).

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = REPO_ROOT / ".claude" / "skills" / "dry-run" / "scaffold_project.py"
SKILL = REPO_ROOT / ".claude" / "skills" / "dry-run" / "SKILL.md"
GENERATOR = (
    REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts" / "generate_recap_pdf.py"
)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class TestScaffoldExists(unittest.TestCase):

    def test_the_skill_and_its_scaffold_are_present(self):
        for path in (SKILL, SCAFFOLD):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file(), f"missing: {path}")

    def test_the_skill_references_its_phase_files(self):
        text = SKILL.read_text(encoding="utf-8")
        for phase in (
            "phase1-mcp-contracts.md",
            "phase2-hooks-and-scripts.md",
            "phase3-conversational.md",
        ):
            with self.subTest(phase=phase):
                self.assertIn(phase, text)
                self.assertTrue((SKILL.parent / phase).is_file(), f"missing: {phase}")


class TestScaffoldReachesTheClipPath(unittest.TestCase):
    """The numeric claim, checked against both real sources."""

    def setUp(self):
        self.scaffold = load(SCAFFOLD, "_dryrun_scaffold")
        self.generator = load(GENERATOR, "_dryrun_recap_gen")

    def clip_widths(self):
        widths = {
            int(n)
            for n in re.findall(
                r"_clip\([^)]*?,\s*(\d+)\s*\)", GENERATOR.read_text(encoding="utf-8"), re.S
            )
        }
        self.assertTrue(widths, "no _clip(x, n) call sites parsed from the generator")
        return widths

    def test_the_in_progress_heading_exceeds_the_narrowest_clip_width(self):
        heading = self.scaffold.IN_PROGRESS_HEADING
        narrowest = min(self.clip_widths())
        self.assertGreater(
            len(heading),
            narrowest,
            f"the scaffold's in-progress heading is {len(heading)} characters against a "
            f"narrowest clip width of {narrowest}, so folding it no longer reaches the "
            "clip path — which is the blind spot the skill exists to avoid and the bug "
            "its own first version shipped",
        )

    def test_clipping_that_heading_still_yields_latin1(self):
        """The end the fixture serves: the clip path must survive the render."""
        clipped = self.generator._clip(
            self.generator._safe(self.scaffold.IN_PROGRESS_HEADING),
            min(self.clip_widths()),
        )
        self.assertNotEqual(clipped, self.scaffold.IN_PROGRESS_HEADING)
        try:
            clipped.encode("latin-1")
        except UnicodeEncodeError as exc:
            self.fail(f"clipped heading is not Latin-1 encodable: {exc}")

    def test_no_real_module_name_alone_would_reach_the_clip(self):
        """Documents *why* the fold is required to exercise this at all."""
        narrowest = min(self.clip_widths())
        self.assertLessEqual(
            len(self.scaffold.LONG_MODULE_NAME),
            narrowest,
            "a bare module name now exceeds the clip width, so the scaffold's comment "
            "explaining that the fold is what reaches the clip path is stale",
        )


class TestSeededModeExercisesTheHonorPath(unittest.TestCase):
    """A walk where everything was asked only tests the rule's inert direction."""

    def setUp(self):
        self.scaffold = load(SCAFFOLD, "_dryrun_scaffold_seed")

    def test_it_seeds_every_honorable_preference(self):
        seeded = self.scaffold.SEEDED_PREFERENCES
        for key in ("path:", "verbosity:", "programming_language:"):
            with self.subTest(key=key):
                self.assertIn(key, seeded)

    def test_it_does_not_seed_the_retired_preference(self):
        self.assertNotIn(
            "model_guidance",
            self.scaffold.SEEDED_PREFERENCES,
            "model_guidance was retired by INV-137; seeding it would test a path that "
            "no longer exists",
        )

    def test_the_seeded_verbosity_is_the_one_with_a_visible_effect(self):
        """`minimal` suppresses output, so honouring it wrongly is obvious in a walk."""
        self.assertIn("preset: minimal", self.scaffold.SEEDED_PREFERENCES)

    def test_the_phase_three_doc_prescribes_the_seeded_walk(self):
        doc = (SKILL.parent / "phase3-conversational.md").read_text(encoding="utf-8")
        self.assertIn("--seeded", doc)
        self.assertRegex(
            doc,
            r"inert direction",
            "the doc should say why one walk is not enough, not merely offer a flag",
        )

    def test_the_doc_lists_what_the_walk_cannot_test(self):
        doc = (SKILL.parent / "phase3-conversational.md").read_text(encoding="utf-8")
        self.assertRegex(doc, r"cannot test")
        for gap in ("write noise", "hooks do not fire", "own compliance"):
            with self.subTest(gap=gap):
                self.assertRegex(doc, gap.replace(" ", r"\s+"), f"missing: {gap}")


class TestScaffoldGuardrails(unittest.TestCase):
    """It must refuse to build somewhere that would damage the repo."""

    def run_scaffold(self, target):
        return subprocess.run(
            [sys.executable, str(SCAFFOLD), target],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )

    def test_it_refuses_to_build_inside_the_repo(self):
        result = self.run_scaffold("./scratch-should-be-refused")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("Refusing to build inside the repo", result.stderr)
        self.assertFalse((REPO_ROOT / "scratch-should-be-refused").exists())

    def test_it_refuses_to_build_under_tmp(self):
        result = self.run_scaffold("/tmp/dry-run-should-be-refused")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("Refusing to build under /tmp", result.stderr)

    def test_explain_writes_nothing(self):
        result = subprocess.run(
            [sys.executable, str(SCAFFOLD), "--explain"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("INV-059", result.stdout, "the fixture map should cite invariants")


if __name__ == "__main__":
    unittest.main()
