"""A results mismatch must be diagnosed, not reported as the bootcamper's system failing.

System verification's Step 2 asks the guide to invent synthetic records and **predict how Senzing
will resolve them**, from its own reasoning. Step 7 then grades the engine against that prediction
and writes a pass/fail check. So a miscalibrated prediction reports a **verification failure on a
healthy install** — at the end of the module whose entire purpose is to tell the bootcamper their
install works.

Observed on a real walk (Senzing 4.3.4, 2026-08-13): three records for one person with the first
name varied `Marisol` / `Mari` / `Marisol` and one record missing its phone resolved to **3
entities** and Step 7 reported FAILED; the same three with the name identical and only formatting
varied resolved to **2 entities** and passed. The engine was right both times. `Mari` is a nickname
variant and that record carried one fewer corroborating feature, so declining to merge is
defensible — arguably correct.

Two causes compound, and the fix has to address both:

* **"Trivial variation" carried all the load and was undefined.** The two attempts differ *only* in
  how that phrase was read.
* **Nothing could distinguish a wrong prediction from an engine fault**, so every mismatch read as
  the latter.

⛔ This is also the one place the module asks the guide to assert engine behaviour unaided — the
class of claim INV-080 exists to prevent. The remedy is not to fetch the prediction from somewhere
(there is nowhere) but to make the construction unambiguous and then let the engine explain itself
when the outcome differs.

Source spec: `specs/verification-grades-the-engine-against-the-guides-own-prediction.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
M3 = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" / "module-03-system-verification"
PHASE1 = M3 / "phase1-verification.md"
SKILL = M3 / "SKILL.md"


def squash(text):
    return re.sub(r"\s+", " ", re.sub(r"^[ \t]*>[ \t]?", "", text, flags=re.M))


def section(path, start, end):
    text = path.read_text(encoding="utf-8")
    i = text.index(start)
    j = text.find(end, i + len(start))
    return squash(text[i:j if j != -1 else len(text)])


def step_2():
    return section(PHASE1, "### Step 2: Generate Synthetic Verification Records", "### Step 3")


def step_7():
    return section(PHASE1, "### Step 7: Deterministic Results Validation", "### Step 8")


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_files_exist(self):
        for path in (PHASE1, SKILL):
            with self.subTest(file=path.name):
                self.assertTrue(path.is_file(), "%s moved" % path)

    def test_both_steps_are_locatable(self):
        self.assertIn("merge cluster", step_2(), "Step 2 was not located")
        self.assertIn("Entity count", step_7(), "Step 7 was not located")


class TheMergeClusterIsUnambiguousByConstruction(unittest.TestCase):
    def setUp(self):
        self.step = step_2()

    def test_the_undefined_phrase_is_gone(self):
        self.assertNotRegex(
            self.step,
            r"(?i)sharing enough features\s*\(matching full name \+ date of birth \+ address, with "
            r"only trivial variation\)",
            "the phrase that produced two opposite verdicts is still doing all the work")

    def test_it_says_construction_not_judgement(self):
        self.assertRegex(
            self.step, r"(?i)Make this unambiguous by construction, not by judgement",
            "nothing states the principle the constraints below implement")

    def test_the_sameness_constraints_are_explicit(self):
        for required in (r"`NAME_FIRST`, `NAME_LAST`, and `NAME_MIDDLE` wherever present",
                         r"`DATE_OF_BIRTH`",
                         r"(?i)address \*\*content\*\*",
                         r"(?i)the same feature \*set\*"):
            with self.subTest(constraint=required[:40]):
                self.assertRegex(self.step, required,
                                 "a sameness constraint is missing")

    def test_the_permitted_variation_is_an_explicit_allowlist(self):
        self.assertRegex(self.step, r"(?i)May vary — formatting only",
                         "what may vary is not enumerated")
        for allowed in ("Punctuation and spacing", "Phone-number formatting",
                        "abbreviated to its initial"):
            with self.subTest(allowed=allowed):
                self.assertIn(allowed, self.step, "a permitted variation is missing")

    def test_the_three_disqualifying_variations_are_named(self):
        self.assertRegex(
            self.step, r"(?i)These are NOT trivial variation",
            "nothing rules out the variations that caused the false failure")
        for banned in (r"(?i)\*\*nickname\*\*", r"(?i)\*\*initial in place of a first name\*\*",
                       r"(?i)\*\*omitted feature\*\*"):
            with self.subTest(banned=banned):
                self.assertRegex(self.step, banned, "a disqualifying variation is unnamed")

    def test_it_says_why_they_disqualify(self):
        self.assertRegex(
            self.step, r"(?i)reduces corroboration",
            "the ban is stated without its mechanism, so it reads as arbitrary")
        self.assertRegex(
            self.step, r"(?i)defensible resolution decision, not a fault",
            "nothing says the engine declining to merge is correct behaviour")

    def test_the_worked_counter_example_is_present(self):
        """The spec's fourth proposal: a real case makes 'trivial' concrete."""
        self.assertRegex(self.step, r"(?i)Worked counter-example",
                         "the counter-example is missing")
        for detail in ("Marisol", "Mari", "3 entities", "2 entities"):
            with self.subTest(detail=detail):
                self.assertIn(detail, self.step,
                              "the counter-example lost a load-bearing detail")
        self.assertRegex(
            self.step, r"(?i)The engine was right both times",
            "the counter-example does not state its conclusion")

    def test_the_observation_is_marked_as_an_observation(self):
        """INV-080/INV-149: engine behaviour seen on one install is not an MCP claim."""
        self.assertRegex(
            self.step,
            r"(?i)observation of this\s*install's behaviour, not an MCP claim",
            "a measured engine behaviour is stated without being marked observation-only")


class AMismatchIsDiagnosed(unittest.TestCase):
    def setUp(self):
        self.step = step_7()

    def test_a_failure_is_framed_as_a_diagnostic(self):
        self.assertRegex(
            self.step,
            r"(?i)this is a DIAGNOSTIC, not a verdict on the install",
            "a failing check still reads as a verdict on the bootcamper's system")
        self.assertRegex(
            self.step, r"(?i)two\s*candidate explanations",
            "the two causes are not named, so there is nothing to tell apart")

    def test_it_says_why_this_check_is_different(self):
        self.assertRegex(
            self.step,
            r"(?i)compares the engine against \*\*a prediction the guide made\*\*",
            "the reason this check is unlike the other seven is unstated")

    def test_it_asks_the_engine_why(self):
        self.assertRegex(self.step, r"(?i)Ask the engine why, before concluding anything",
                         "no lookup is triggered on a mismatch")
        self.assertIn("why_records", self.step, "why_records is not called")
        self.assertIn("why_entities", self.step, "why_entities is not called")
        self.assertRegex(
            self.step, r"(?i)get_sdk_reference` \+\s*`sdk_guide` — never from memory",
            "the why_* call is not routed through the MCP tools (INV-080)")

    def test_it_reports_the_match_key_and_feature_scores(self):
        self.assertRegex(
            self.step, r"(?i)\*\*match key\*\* and the \*\*feature scores\*\*",
            "the engine's explanation is requested but its content is not reported")

    def test_a_coherent_explanation_does_not_fail_the_system(self):
        self.assertRegex(
            self.step,
            r"(?i)the expectation was\s*wrong, and the install is fine",
            "an explained mismatch still reports the install as broken")
        self.assertRegex(
            self.step, r"(?i)Do not report the system as having failed verification",
            "nothing forbids the false report this spec exists to stop")
        self.assertRegex(
            self.step, r"(?i)do not tell the\s*bootcamper to re-run the load",
            "the old remedy — re-run the load — is still offered for a case where "
            "nothing is wrong with the load")

    def test_an_unexplained_mismatch_still_fails(self):
        self.assertRegex(
            self.step,
            r"(?i)does not account for the difference",
            "the real-finding branch is gone, so the check can no longer fail at all")
        self.assertRegex(
            self.step, r"(?i)this is a real finding",
            "the second branch does not say it is a genuine failure")

    def test_the_check_is_reported_separately(self):
        self.assertRegex(
            self.step,
            r"(?i)reported separately from the other seven",
            "a mismatch can still turn the module's overall result into a failure")

    def test_the_four_checks_still_exist(self):
        for check in ("Entity count", "Merge cluster resolves to one entity",
                      "Cross-record resolution", "Distractor stays a singleton"):
            with self.subTest(check=check):
                self.assertIn(check, self.step, "a validation check was lost")


class TheSuccessIndicatorDistinguishesTheChecks(unittest.TestCase):
    def setUp(self):
        self.flat = squash(SKILL.read_text(encoding="utf-8"))

    def test_it_no_longer_lumps_all_eight_together(self):
        self.assertNotRegex(
            self.flat,
            r'(?i)✅ All 8 System Verification checks report "passed"',
            "the success indicator still gives the bootcamper no way to tell an install "
            "failure from a wrong prediction")

    def test_it_names_the_seven_install_checks(self):
        self.assertRegex(
            self.flat, r"(?i)\*\*7 installation checks\*\*",
            "the install checks are not counted separately")
        for check in ("MCP connectivity", "engine initialization", "SDK initialization",
                      "code generation", "build", "data-source registration", "loading"):
            with self.subTest(check=check):
                self.assertIn(check, self.flat, "an install check is unnamed")

    def test_it_marks_results_validation_as_separate(self):
        self.assertRegex(
            self.flat,
            r"(?i)\*\*results validation\*\*, which is reported separately",
            "results validation is not distinguished in the success indicator")
        self.assertRegex(
            self.flat, r"(?i)Results validation is kept separate on purpose",
            "the separation is done without its reason, so a later editor will merge it "
            "back for tidiness")

    def test_it_forbids_the_false_report_here_too(self):
        self.assertRegex(
            self.flat,
            r"(?i)is an expectation mismatch, \*\*not\*\* a failed verification",
            "the rule is stated only in phase 1; the success indicator is where a reader "
            "decides what to tell the bootcamper")


if __name__ == "__main__":
    unittest.main()
