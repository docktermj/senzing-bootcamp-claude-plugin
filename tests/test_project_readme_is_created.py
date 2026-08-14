"""A step that says "update README.md" needs a step that creates it.

Module 1 Phase 2 Step 12 said to "**Update** `README.md`. Fill the Overview and Business
Problem sections" — and nothing created the file, nor defined those sections. Project setup
created `src/`, `data/`, `docs/`, `config/`, `database/` and the two `config/` files; Bootcamp
preparation wrote only the two `config/` files; the ground rules' root whitelist *permits* a
`README.md`, which is a permission and not a creation. So on every fresh bootcamp the step was
an instruction to edit a file that did not exist, in a shape nobody specified — a guide writes
one rather than stalling, differently each run.

Same class as `specs/nothing-owns-creating-the-recap-header.md`: a step updates an artifact
whose creation no step owns.

Source spec: `specs/project-readme-is-updated-but-never-created.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
ONBOARDING = SKILLS / "bootcamp-onboarding" / "onboarding-flow.md"
GROUND_RULES = SKILLS / "bootcamp-onboarding" / "ground-rules.md"
STEP_12 = SKILLS / "module-01-business-problem" / "phase2-document-confirm.md"

HEADINGS = ("## Overview", "## Business Problem")


def read(path):
    return path.read_text(encoding="utf-8")


def squash(text):
    return re.sub(r"\s+", " ", text)


def project_setup_section():
    """The '1. Project setup' section only — the step that must own the creation."""
    text = read(ONBOARDING)
    start = text.index("## 1. Project setup")
    end = text.index("## 2. Prerequisite check", start)
    return text[start:end]


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_files_exist(self):
        for path in (ONBOARDING, GROUND_RULES, STEP_12):
            with self.subTest(file=path.name):
                self.assertTrue(path.is_file(), "%s moved" % path)

    def test_the_project_setup_section_is_locatable(self):
        section = project_setup_section()
        self.assertIn("config/bootcamp_preferences.yaml", section,
                      "the located section is not the one that creates the scaffold")


class ProjectSetupCreatesTheReadme(unittest.TestCase):
    def setUp(self):
        self.section = project_setup_section()

    def test_it_creates_the_file(self):
        self.assertRegex(
            squash(self.section),
            r"(?i)Create the project `README\.md` if it does not exist",
            "project setup still creates the directories and the two config files but no "
            "README, so Step 12's 'update' has nothing to update")

    def test_it_defines_both_headings(self):
        for heading in HEADINGS:
            with self.subTest(heading=heading):
                self.assertIn(heading, self.section,
                              "the section Step 12 fills is not created here, so its shape "
                              "is still whatever the guide invents")

    def test_it_is_created_silently(self):
        """INV-012: the rest of project setup is administrative and unnarrated."""
        self.assertIn("Do this silently:", self.section)
        self.assertRegex(squash(self.section), r"(?i)written silently, like the rest of this step",
                         "nothing says the README write is administrative too")

    def test_it_says_nothing_else_belongs_in_the_file(self):
        """The spec's third item: define the rest of the file, or say there is no rest."""
        self.assertRegex(
            squash(self.section), r"(?i)Nothing else belongs in this file",
            "the two sections are created and the rest of the README is left undefined, "
            "which is half the original ambiguity")

    def test_it_does_not_authorise_other_root_markdown(self):
        self.assertRegex(
            squash(self.section),
            r"(?i)only\*?\*? `?\.md`? permitted at the project\s*root|only\*?\*? `\.md` permitted",
            "creating a root .md without restating the INV-017 restriction invites more")


class StepTwelveFillsRatherThanAssumes(unittest.TestCase):
    def setUp(self):
        self.text = read(STEP_12)
        self.flat = squash(self.text)

    def test_it_points_at_where_the_sections_come_from(self):
        self.assertRegex(
            self.flat,
            r"(?i)sections \*?\*?created at project setup\*?\*?",
            "Step 12 does not say where the sections it fills came from, so the coupling "
            "is invisible from this end")

    def test_it_creates_the_file_when_absent(self):
        self.assertRegex(
            self.flat, r"(?i)If `README\.md` is absent, create it first",
            "a resumed project, or one whose setup predates this, still hits a missing file")
        self.assertRegex(
            self.flat, r"(?i)Do not stall on the missing file",
            "the fallback exists but does not say the step must still complete")

    def test_it_bounds_what_it_writes(self):
        self.assertRegex(
            self.flat, r"(?i)Those two sections are the whole of this step",
            "Step 12 may still grow sections that belong under docs/ (INV-017)")

    def test_the_heading_still_reads_as_an_update(self):
        """The file IS pre-created now, so 'Update' is finally accurate."""
        self.assertIn("## 12. Update README.md", self.text,
                      "the step heading moved; it should now be true rather than reworded")


class TheRootStaysWhitelisted(unittest.TestCase):
    def test_the_ground_rules_still_permit_only_the_readme(self):
        flat = squash(read(GROUND_RULES))
        self.assertIn("README.md", flat, "the root whitelist no longer names README.md")

    def test_no_other_root_markdown_is_introduced(self):
        """Whatever the plugin tells the bootcamp to create at the root, it is this one file."""
        created = re.findall(r"Create the project `([^`]+)`", squash(read(ONBOARDING)))
        self.assertEqual(["README.md"], created,
                         "project setup creates a root file other than README.md: %r"
                         % created)


if __name__ == "__main__":
    unittest.main()
