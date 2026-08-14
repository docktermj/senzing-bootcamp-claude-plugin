"""Creating the recap header must be owned by a step, not assumed by two.

On a Core run no module was instructed to create `docs/bootcamp_recap.md`'s preamble, and the
one file that said who created it named a module exempt from writing it at all:

* `module-00-entity-resolution-concepts/SKILL.md` cited module-completion "Step 2 (2b/2c)".
  Step **2a** — create the recap on first module completion — is the substep that applies, and
  it was the one omitted. In a Core run Module 0 is the *first* module to append a recap
  section, because Bootcamp preparation is recap-exempt (INV-092), so Module 0 is exactly the
  module that hits the does-not-exist case. Following its own SKILL literally appended a
  `## Entity Resolution Concepts` section to a file with no preamble.
* `graduation/SKILL.md` said the `**Bootcamper:**` line was one "which **Bootcamp preparation
  wrote at the start of the run**". Bootcamp preparation writes no recap and says so twice.

The failure is late and lands on the keepsake: the certificate prints a placeholder, and
graduation's completion-date insertion and `**Plugin version:**` amendment are anchored to a
header nobody wrote.

The remedy removes the class rather than patching two sites — a citation naming specific
substeps is the hazard — so this file scans **every** skill file for a narrowed Step 2 citation,
not just the one that regressed.

Enforces **INV-226** — a step that updates a shared artifact is reached only through a citation covering the substep that creates it.

Source spec: `specs/nothing-owns-creating-the-recap-header.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
SKILLS = PLUGIN / "skills"
MODULE_COMPLETION = SKILLS / "bootcamp-onboarding" / "module-completion.md"
MODULE_00 = SKILLS / "module-00-entity-resolution-concepts" / "SKILL.md"
GRADUATION = SKILLS / "graduation" / "SKILL.md"

PREAMBLE_LINES = ("**Bootcamper:**", "**Started:**", "**Programming language:**",
                  "**Path:**", "**Plugin version:**")

#: A citation that enumerates Step 2's substeps. `Step 2 in full`, bare `Step 2`, and a
#: single-substep reference (`Step 2a`, `Step 2c`) are all fine — the hazard is a LIST that
#: leaves 2a out, because that reads as the complete set of substeps to run.
SUBSTEP_CITATION = re.compile(r"Step 2 \(([^)]*)\)")


def read(path):
    return path.read_text(encoding="utf-8")


def squash(text):
    return re.sub(r"\s+", " ", text)


def load_recap_generator():
    """The generator must be in `sys.modules` before it executes.

    It defines `@dataclass` types, and dataclasses resolves annotations through
    `sys.modules[cls.__module__]` — absent, that raises during import rather than at use.
    """
    spec = importlib.util.spec_from_file_location(
        "recap_pdf_for_header_test", PLUGIN / "scripts" / "generate_recap_pdf.py")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(PLUGIN / "scripts"))
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_files_exist(self):
        for path in (MODULE_COMPLETION, MODULE_00, GRADUATION):
            with self.subTest(file=path.name):
                self.assertTrue(path.is_file(), "%s moved" % path)

    def test_the_corpus_reaches_every_skill(self):
        files = sorted(SKILLS.rglob("*.md"))
        self.assertGreater(len(files), 20, "the skill corpus was not found")

    def test_the_pattern_matches_the_citation_that_shipped(self):
        self.assertIsNotNone(
            SUBSTEP_CITATION.search(
                "per `../bootcamp-onboarding/module-completion.md` Step 2 (2b/2c):"),
            "the scanner does not recognise the citation it exists to catch")


class NoSkillNarrowsStepTwoPastItsCreateSubstep(unittest.TestCase):
    def test_every_substep_citation_includes_2a(self):
        offences = []
        for path in sorted(SKILLS.rglob("*.md")):
            flat = squash(read(path))
            for match in SUBSTEP_CITATION.finditer(flat):
                listed = match.group(1)
                if "2a" in listed:
                    continue
                before = flat[max(0, match.start() - 170):match.start()]
                # Only module-completion's Step 2 has substeps. Module 3 has a "Step 2"
                # of its own, and citing it with a parenthetical is not this defect.
                if "module-completion.md" not in before:
                    continue
                # The prohibition in module-completion.md quotes the bad citation in
                # order to forbid it; quoting a defect is not committing it.
                if re.search(r"(?i)may narrow|that cites|forbid", before):
                    continue
                offences.append("%s: Step 2 (%s)"
                                % (path.relative_to(REPO_ROOT), listed))
        self.assertEqual(
            [], offences,
            "a skill cites module-completion Step 2 with a substep list that omits 2a — "
            "the substep that CREATES the recap header. Whichever module appends first "
            "owns the creation, and a narrowed citation is how it gets skipped:\n  "
            + "\n  ".join(offences))

    def test_module_00_no_longer_narrows_it(self):
        """Named explicitly: a corpus scan passes if the file is simply renamed."""
        flat = squash(read(MODULE_00))
        self.assertNotIn("Step 2 (2b/2c)", flat,
                         "Module 0 still cites Step 2 as (2b/2c)")
        self.assertIn("**Step 2 in full**", flat,
                      "Module 0 does not cite Step 2 whole")


class StepTwoAIsUnconditional(unittest.TestCase):
    def setUp(self):
        self.flat = squash(read(MODULE_COMPLETION))

    def test_it_says_so_in_module_completion(self):
        self.assertRegex(
            self.flat,
            r"(?i)This substep is UNCONDITIONAL at any module whose append finds no file",
            "2a does not state that it applies at any module, so a narrowed citation "
            "elsewhere can still skip it")

    def test_it_forbids_a_narrowing_citation(self):
        self.assertRegex(
            self.flat,
            r"(?i)no citation elsewhere may narrow Step 2 in a way that omits it",
            "the hazard — a citation that names substeps — is not named")

    def test_it_says_nothing_else_creates_the_header(self):
        self.assertRegex(
            self.flat, r"(?i)not Bootcamp preparation \(which\s*is recap-exempt",
            "2a does not say that Bootcamp preparation writes no recap, which is the "
            "false belief the graduation file encoded")

    def test_it_names_the_consequence(self):
        self.assertRegex(
            self.flat, r"(?i)certificate prints a\s*placeholder name",
            "the cost of skipping 2a is unstated, so it reads as bookkeeping")

    def test_the_header_still_carries_all_five_lines(self):
        for line in PREAMBLE_LINES:
            with self.subTest(line=line):
                self.assertIn(line, read(MODULE_COMPLETION),
                              "the header template lost a preamble line")


class ModuleZeroKnowsItCreatesTheHeader(unittest.TestCase):
    def setUp(self):
        self.flat = squash(read(MODULE_00))

    def test_it_states_it_is_first_on_a_core_run(self):
        self.assertRegex(
            self.flat,
            r"(?i)On a Core run this is the FIRST module to append a recap section, so 2a "
            r"applies and creates\s*the header",
            "Module 0 does not say that 2a applies to it")

    def test_it_names_the_five_preamble_lines(self):
        for line in PREAMBLE_LINES:
            with self.subTest(line=line):
                self.assertIn(line, read(MODULE_00),
                              "Module 0 does not say which lines the header carries, so a "
                              "partial header still reads as done")

    def test_it_runs_2d_as_well(self):
        self.assertRegex(
            self.flat, r"(?i)Run \*?\*?2d\*?\*? as well",
            "2d was omitted from the same citation and is still omitted")

    def test_the_step_3_exemption_is_unchanged(self):
        self.assertRegex(
            self.flat,
            r"(?i)does \*?\*?not\*?\*? present the\s*bootcamper-facing end-of-module summary",
            "Module 0's Step 3 exemption (INV-078/INV-092) was lost while widening its "
            "Step 2 citation")


class GraduationAttributesTheLineCorrectly(unittest.TestCase):
    def setUp(self):
        self.flat = squash(read(GRADUATION))

    def test_the_false_provenance_is_gone(self):
        self.assertNotRegex(
            self.flat,
            r"which Bootcamp\s*preparation wrote at the \*\*start\*\* of the run",
            "graduation still attributes the **Bootcamper:** line to a module that "
            "writes no recap")

    def test_it_names_the_real_writer(self):
        self.assertRegex(
            self.flat,
            r"(?i)written by\s*\*\*module-completion Step 2a, at the first module that appends "
            r"a recap section\*\*",
            "the corrected provenance is missing")
        self.assertRegex(
            self.flat, r"(?i)Entity\s*Resolution Concepts when it is selected, otherwise Discover "
                       r"the Business Problem",
            "the provenance does not say which module that is on each path")

    def test_it_states_that_preparation_writes_no_recap(self):
        self.assertRegex(
            self.flat, r"(?i)Bootcamp preparation itself writes \*?\*?no\*?\*? recap",
            "the false belief is corrected in one place and left implicit here")

    def test_it_writes_the_line_when_absent(self):
        self.assertRegex(
            self.flat,
            r"(?i)If the `\*\*Bootcamper:\*\*` line is absent, WRITE it — do not assume an "
            r"edit target",
            "graduation still amends a line that may not exist")
        self.assertRegex(
            self.flat, r"(?i)note the recovery",
            "a header written at graduation means a module skipped 2a; recovering "
            "silently hides that")

    def test_the_both_not_either_rule_survives(self):
        self.assertRegex(
            self.flat, r"(?i)\*\*Both, not either\.\*\*",
            "the rule that the name is persisted in both places was lost")


class TheGeneratorAcceptsAHeaderBuiltToTwoA(unittest.TestCase):
    """Criterion 5: the "no bootcamper name found" warning must not fire.

    Built exactly as Step 2a prescribes, plus one Module 0 section as 2b prescribes — the
    shortest walk that produces a recap (Bootcamp preparation → Entity Resolution Concepts).
    """

    RECAP = """# Senzing Bootcamp Recap

**Bootcamper:** Ada Lovelace
**Started:** 2026-08-14T09:00:00-07:00
**Programming language:** Python
**Path:** Core
**Plugin version:** 1.0.0

---

## Entity Resolution Concepts — 2026-08-14T09:20:00-07:00

**Information Shared:**

- What entity resolution is.

**Questions & Responses:**

- Knowledge check offered: yes; declined.

**Actions Taken:**

- Presented the primer. (no files — conceptual primer)

**End-of-Module Summary:**

**What you accomplished:** A grounding in entity resolution.
**Files produced:** (no files — conceptual primer)
**Why it matters:** The rest of the bootcamp builds on it.
"""

    def setUp(self):
        self.gen = load_recap_generator()

    def test_the_name_is_found(self):
        recap = self.gen.parse_recap(self.RECAP)
        self.gen.set_certificate_name_override("")
        self.assertEqual("Ada Lovelace", self.gen.recap_certificate_name(recap))
        self.assertFalse(
            self.gen.recap_missing_certificate_name(recap),
            "the generator would warn and print a placeholder on the certificate for a "
            "recap whose header was built exactly as Step 2a prescribes")

    def test_a_header_less_recap_is_what_used_to_warn(self):
        """The control: without 2a, the warning fires. Proves the test above is not vacuous."""
        without_header = self.RECAP.split("---\n", 1)[1]
        recap = self.gen.parse_recap(without_header)
        self.gen.set_certificate_name_override("")
        self.assertTrue(
            self.gen.recap_missing_certificate_name(recap),
            "a recap with no preamble did NOT trigger the warning, so this pair proves "
            "nothing about 2a")

    def test_every_preamble_line_survives_parsing(self):
        recap = self.gen.parse_recap(self.RECAP)
        keys = {key.strip().lower().rstrip(":") for key, _val in recap.meta}
        for line in PREAMBLE_LINES:
            label = line.strip("*:").lower()
            with self.subTest(line=line):
                self.assertIn(label, keys,
                              "the generator does not parse the %r line the header "
                              "template writes" % label)


if __name__ == "__main__":
    unittest.main()
