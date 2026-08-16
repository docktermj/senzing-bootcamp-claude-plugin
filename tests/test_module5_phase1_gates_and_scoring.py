"""Module 5 Phase 1: the score is computable, the gate is satisfiable, Step 2 verifies.

Three defects found in one dry-run walk on 2026-08-12, all in
`phase1-quality-assessment.md`, all invisible to a prose read because each is wrong only
*relative to something else in the same file*:

* **Step 2 asked for data the module's own prerequisite says is already there.** SKILL.md
  states "Module 4 complete (data sources collected, files in `data/raw/`)"; Step 2 said
  "ask the user to place sample files". Confirmed behaviorally in the walk — the answer was
  a bare "yes", which cannot distinguish "I placed files" from "they were already there", so
  the question could not detect the state it existed to establish.
* **The quality score had precise bands and no formula.** Step 6 named three dimensions,
  defined the presence test exhaustively, and never said how they combine into the number
  that routes a gate banded to the percentage point.
* **The gate ordered "exactly one 👉" and its ≥80% branch supplied none** — the common
  branch for curated data, leaving the guide to fabricate a question (breaching INV-056) or
  disobey the header.

Each assertion below targets the *claim*, not a phrase, so a rewording that keeps the
substance passes. Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE1 = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
          / "module-05-data-quality-mapping" / "phase1-quality-assessment.md")


def body():
    return PHASE1.read_text(encoding="utf-8")


def section(heading, stop="\n## "):
    """The text of one `## ` step, from its heading to the next one."""
    text = body()
    start = text.index(heading)
    end = text.find(stop, start + len(heading))
    return text[start:end if end != -1 else len(text)]


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_file_and_its_steps_are_found(self):
        self.assertTrue(PHASE1.is_file(), "phase1-quality-assessment.md moved")
        for heading in ("## 1. ", "## 2. ", "## 6. ", "### Quality gate"):
            with self.subTest(heading=heading):
                self.assertIn(heading, body(), "step %r is gone — re-point this guard" % heading)


class StepTwoVerifiesRatherThanRequests(unittest.TestCase):
    def setUp(self):
        self.step = section("## 2. ")

    def test_it_reads_the_registry_before_asking(self):
        self.assertIn("config/data_sources.yaml", self.step,
                      "Step 2 must verify against the registry Data collection wrote, not "
                      "ask the bootcamper for files it already fetched")

    def test_the_ask_is_conditional_not_the_default(self):
        """The whole defect was an unconditional instruction to ask."""
        flat = re.sub(r"\s+", " ", self.step).replace("**", "")
        self.assertRegex(
            flat, r"(?i)ask only|only .{0,40}(missing|empty)",
            "the request for files is not visibly guarded by a missing-file/empty-registry "
            "condition; an unconditional ask is the defect this guards")

    def test_the_bring_your_own_data_path_survives(self):
        """The fix re-frames the default branch; it must not remove the capability."""
        flat = re.sub(r"\s+", " ", self.step).replace("**", "")
        self.assertRegex(flat, r"(?i)registry is empty|empty .{0,30}registry",
                         "the no-data path must remain reachable for a bootcamper whose "
                         "data cannot leave their machine")

    def test_step_one_takes_its_list_from_the_registry(self):
        step1 = section("## 1. ")
        self.assertIn("config/data_sources.yaml", step1,
                      "Step 1 must recap what was collected, not what was discussed")
        self.assertIn("business_problem", step1,
                      "Step 1 should still use the business-problem doc — for the why")
        flat = re.sub(r"\s+", " ", step1).replace("**", "")
        self.assertRegex(flat, r"(?i)differ",
                         "Step 1 must say what to do when the collected and discussed "
                         "lists differ; they routinely do")


class TheQualityScoreIsComputable(unittest.TestCase):
    def setUp(self):
        self.step = section("## 6. ")

    def test_a_formula_is_given(self):
        self.assertRegex(
            self.step, r"quality_score\s*=",
            "Step 6 names three dimensions but gives no arithmetic; the score routes a gate "
            "banded to the percentage point, so it must be reproducible by a second guide")

    def test_every_named_dimension_is_defined(self):
        for dimension in ("completeness", "format_consistency", "duplicate_rate"):
            with self.subTest(dimension=dimension):
                self.assertIn(dimension, self.step,
                              "%r appears in the formula but is never defined" % dimension)

    def test_the_duplicate_dimension_uses_record_identity(self):
        """INV-180: a record's identity is (DATA_SOURCE, RECORD_ID), not the whole row."""
        flat = re.sub(r"\s+", " ", self.step)
        self.assertIn("DATA_SOURCE", flat)
        self.assertIn("RECORD_ID", flat)
        self.assertIn("INV-180", flat,
                      "the duplicate dimension must cite INV-180, which is why row-level "
                      "duplicate counting measures something Senzing does not do")

    def test_which_fields_enter_completeness_is_stated(self):
        flat = re.sub(r"\s+", " ", self.step).replace("**", "")
        self.assertRegex(
            flat, r"(?i)which fields count|fields .{0,40}enter",
            "the choice of which fields count toward completeness is consequential and must "
            "be stated, not left to the implementer")

    def test_a_worked_example_shows_the_arithmetic(self):
        self.assertRegex(self.step, r"(?i)worked example",
                         "a formula stated but never exercised is still ambiguous")


class TheGateIsSatisfiableInEveryBranch(unittest.TestCase):
    def setUp(self):
        self.gate = section("### Quality gate", stop="\n## ")

    def test_the_one_question_rule_is_scoped_to_the_gating_branches(self):
        """Assert the scope sits ON the instruction, not merely somewhere in the section.

        The first version searched the whole section for a scoping phrase, and passed on a
        mutation that restored the unconditional header — because the closing internal note
        happens to say "gating branches" too. A guard a restored defect satisfies is no guard.
        """
        flat = re.sub(r"\s+", " ", self.gate).replace("**", "")
        instructions = [s for s in re.split(r"(?<=[.)]) ", flat) if "exactly one 👉" in s]
        self.assertTrue(instructions,
                        "the 'exactly one 👉' instruction is gone — re-point this guard")
        for sentence in instructions:
            with self.subTest(sentence=sentence[:60]):
                self.assertRegex(
                    sentence, r"(?i)where the score gates|gating branches|70-79|below 70",
                    "this sentence orders exactly one 👉 without naming which branches it "
                    "applies to. Unscoped, it demands a question the >=80%% branch does not "
                    "supply, so the guide must fabricate one (INV-056) or disobey: %r"
                    % sentence[:120])

    def test_the_strong_branch_carries_no_question(self):
        strong = self.gate[self.gate.index("Quality ≥80%"):]
        strong = strong[:strong.index("Quality 70-79%")]
        # Match a 👉 *question* — the house idiom `👉 **…**` — not the bare glyph. The branch
        # legitimately mentions 👉 in prose saying it has none ("statement, no 👉"), and the
        # first version of this assertion flagged exactly that annotation.
        self.assertIsNone(
            re.search(r"👉\s*\*\*", strong),
            "a 👉 question was added to the ≥80% branch. That is the wrong fix: 'your data "
            "is fine, shall we continue?' is the pointless question INV-012 forbids, and "
            "improvising its wording breaches INV-056. Scope the header instead.")

    def test_the_strong_branch_says_what_happens_next(self):
        flat = re.sub(r"\s+", " ", self.gate).replace("**", "")
        self.assertRegex(
            flat, r"(?i)continue .{0,30}Phase 2|into Phase 2",
            "with no question, the ≥80% branch must say the turn continues into Phase 2, or "
            "the turn's end is undefined")

    def test_the_two_gating_questions_are_still_pinned(self):
        """INV-056: these two are the pinned wording and must survive the header fix."""
        for band in ("acceptable but has some gaps", "needs attention before mapping"):
            with self.subTest(band=band):
                self.assertRegex(
                    self.gate, r"👉 \*\*[^\n]*" + re.escape(band),
                    "the pinned gate question for this band was altered or removed")


if __name__ == "__main__":
    unittest.main()
