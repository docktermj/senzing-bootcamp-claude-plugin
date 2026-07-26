"""INV-133 must cover every setup preference, not just the one that motivated it.

INV-133 is phrased generally: "A setup preference already recorded in
`config/bootcamp_preferences.yaml` MUST be honored and its capture question MUST NOT
be asked." It arrived via the `skip-model-guidance-question` spec, and only
`model_guidance` ever got the read-first check. Steps 1 (path), 3 (verbosity) and 4
(programming language) asked unconditionally, so a returning bootcamper who had saved
`verbosity: minimal` was asked for it again — exactly what the invariant forbids.

(`model_guidance` itself was retired by INV-137 shortly afterwards — the question is no
longer asked at all — so the registry below covers the three preferences that remain.)

Reading the file suggested it; the phase-3 conversational dry run confirmed it, because
walking the steps in order shows there is simply no instruction to check.

What this pins, per preference that has a capture question:

* the preference is listed in Bootcamp preparation's Step 0 honor-first table, and
* its own step carries a skip instruction, so the rule is enforced where the question
  lives rather than only in a preamble someone can skip past.

Detected values (`name`, `os`/`arch`, `git_init`) are deliberately excluded: they have
no capture question to suppress (INV-134/INV-061/INV-095).

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PREP = (
    REPO_ROOT
    / "plugins"
    / "senzing-bootcamp"
    / "skills"
    / "bootcamp-preparation"
    / "SKILL.md"
)
ONBOARDING = (
    REPO_ROOT
    / "plugins"
    / "senzing-bootcamp"
    / "skills"
    / "bootcamp-onboarding"
    / "onboarding-flow.md"
)

# (preference key, the step heading whose question it suppresses)
ASKED_PREFERENCES = (
    ("path", "## 1."),
    ("verbosity", "## 3."),
    ("programming_language", "## 4."),
)

# Detected, never asked — no question to suppress.
DETECTED_ONLY = ("name", "os", "arch", "git_init")


def prep_text():
    return PREP.read_text(encoding="utf-8")


def step_body(text, heading):
    """The text of one '## ' step, up to the next '## ' heading."""
    start = text.find(heading)
    if start == -1:
        return ""
    nxt = text.find("\n## ", start + len(heading))
    return text[start : nxt if nxt != -1 else len(text)]


class TestStepZeroExists(unittest.TestCase):
    """A single place stating the general rule, so steps can point at it."""

    def test_there_is_an_honor_first_step_before_step_one(self):
        text = prep_text()
        self.assertIn("## 0.", text, "Bootcamp preparation has no Step 0 honor-first step")
        self.assertLess(
            text.find("## 0."),
            text.find("## 1."),
            "the honor-first step must come before the first capture question",
        )

    def test_step_zero_cites_the_invariant_and_forbids_overwriting(self):
        body = step_body(prep_text(), "## 0.")
        self.assertIn("INV-133", body)
        self.assertRegex(
            body,
            r"MUST NOT be asked",
            "Step 0 should state the rule it enforces, not merely imply it",
        )
        self.assertRegex(
            body,
            r"NEVER be overwritten|never overwrite",
            "INV-133 also forbids overwriting a saved value with a recommended default",
        )


class TestEveryAskedPreferenceIsCovered(unittest.TestCase):

    def test_each_is_listed_in_the_step_zero_table(self):
        body = step_body(prep_text(), "## 0.")
        missing = [key for key, _ in ASKED_PREFERENCES if f"`{key}`" not in body]
        self.assertEqual(
            [],
            missing,
            f"preference(s) absent from Step 0's honor-first table: {missing}. INV-133 "
            "applies to every setup preference, not only the one that motivated it.",
        )

    def test_each_step_carries_its_own_skip_instruction(self):
        text = prep_text()
        offenders = []
        for key, heading in ASKED_PREFERENCES:
            body = step_body(text, heading)
            self.assertTrue(body, f"step {heading} not found")
            if not re.search(r"[Ss]kip (this step|the)", body):
                offenders.append(f"{heading} ({key})")
        self.assertEqual(
            [],
            offenders,
            "step(s) with a capture question but no skip-if-saved instruction: "
            f"{offenders}. A rule stated only in a preamble is one an agent reading "
            "just the step will miss.",
        )

    def test_the_recap_marks_honored_values_as_saved(self):
        """A silently-honored preference looks like a question that was forgotten."""
        text = prep_text()
        self.assertGreaterEqual(
            text.count("from your saved preferences"),
            2,
            "the Step 7 recap should mark each honorable preference's line as coming "
            "from the saved file when its question was suppressed (INV-133)",
        )

    def test_detected_values_are_not_treated_as_questions(self):
        body = step_body(prep_text(), "## 0.")
        for key in DETECTED_ONLY:
            with self.subTest(key=key):
                self.assertNotRegex(
                    body,
                    rf"`{key}`[^\n|]*\|\s*Step \d",
                    f"{key} is detected, not asked — it has no capture question to "
                    "suppress (INV-134/INV-061/INV-095)",
                )


class TestHealthProbeIsCheap(unittest.TestCase):
    """The preface should make one MCP call, not two, and not a heavyweight one."""

    def test_the_probe_is_the_call_ground_rules_already_requires(self):
        body = step_body(ONBOARDING.read_text(encoding="utf-8"), "## 0b.")
        self.assertTrue(body, "the MCP health-check step is missing")
        self.assertIn(
            "get_capabilities",
            body,
            "the health probe should reuse get_capabilities, which ground-rules "
            "already requires once before any other Senzing MCP call",
        )

    def test_search_docs_is_not_described_as_a_lightweight_probe(self):
        body = step_body(ONBOARDING.read_text(encoding="utf-8"), "## 0b.")
        self.assertNotRegex(
            body,
            r"lightweight call such as `search_docs",
            "search_docs(query='health check') returns a multi-page FAQ article; it is "
            "not a lightweight liveness probe",
        )


if __name__ == "__main__":
    unittest.main()
