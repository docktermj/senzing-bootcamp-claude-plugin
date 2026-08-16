"""The feedback hook must catch the ways people actually write the request — and no more.

`feedback-capture.py` exists so a bootcamper's "I want to give feedback" is handled the same
way **anywhere** in the bootcamp: it injects the pinned entry/exit banners, the INV-067
append-and-verify rule, the INV-015 save-locally-whatever-the-verdict rule, and the INV-065
show-and-consent gate before anything leaves the machine. Its trigger was a literal alternation
of eight fixed collocations, and ten of thirteen natural paraphrases missed. The one-word gap
between `I have feedback` (hit) and `I have some feedback about module 5` (miss) is the shape of
it: the pair had to be adjacent.

⛔ **The asymmetry is the point, and it is what this file mainly protects.** Modules 5–7 have
the bootcamper writing and debugging their own loader, mapper and query, so `I found a bug`,
`something is broken` and `this step is wrong` overwhelmingly mean *their* code. Injecting the
feedback workflow there prepends banner-and-gather instructions onto a turn where they want a
traceback explained — a derailed debugging turn, where a missed capture would merely have sent
them via `/bootcamp-feedback`. So bare fault language must stay quiet, and the same words with a
bootcamp/plugin/module referent must fire.

The hook is exercised as a **subprocess with real stdin**, in a temporary directory, because it
reads stdin and checks for `config/bootcamp_progress.json` at import time — importing it would
test something else.

Source spec: `specs/feedback-capture-misses-natural-phrasings.md`.

Run:  python3 -m unittest discover -s tests
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts" / "feedback-capture.py"

#: Must inject the feedback workflow. Every one names feedback, frames an explicit report,
#: or blames the bootcamp/plugin/module by name.
HITS = (
    "Bootcamp feedback: the banner was wrong",
    "I have feedback",
    "I have feedback on the mapping step",
    "I have some feedback about module 5",
    "I have a bit of feedback",
    "I'd like to give feedback",
    "can I give you some feedback",
    "let me give you some quick feedback",
    "sharing feedback now",
    "submit feedback",
    "provide feedback",
    "feedback about the bootcamp",
    "report a bug",
    "report an issue",
    "I want to report a problem",
    "I found a bug in the bootcamp",
    "something is broken in this bootcamp",
    "something is broken in this plugin",
    "this plugin is broken",
)

#: Must stay quiet: bare fault language with no bootcamp/plugin/module referent, plus
#: ordinary bootcamp conversation.
MISSES = (
    "I found a bug",
    "something is broken",
    "this step is wrong",
    "my loader is broken",
    "there is a bug in my mapper",
    "why is my query wrong",
    "the traceback says something is wrong",
    "load the truth set",
    "what is entity resolution",
    "show me the entity graph",
)

VERBOSITY_HITS = (
    "change verbosity",
    "can you be less wordy",
    "be more concise",
    "please be more detailed",
    "keep it brief",
    "shorter answers please",
    "too verbose",
    "more detail",
)


def run_hook(prompt, in_bootcamp=True):
    """Return the hook's stdout for `prompt`, run in a scratch project directory."""
    with tempfile.TemporaryDirectory() as tmp:
        if in_bootcamp:
            config = Path(tmp) / "config"
            config.mkdir()
            (config / "bootcamp_progress.json").write_text("{}\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps({"prompt": prompt}),
            capture_output=True, text=True, cwd=tmp, timeout=60,
        )
    return proc.returncode, proc.stdout


class TheHookRuns(unittest.TestCase):
    def test_the_hook_exists(self):
        self.assertTrue(HOOK.is_file(), "feedback-capture.py moved")

    def test_a_plain_feedback_prompt_injects_something(self):
        """Fixture check: if this fails, every HIT assertion below is meaningless."""
        code, out = run_hook("Bootcamp feedback: the banner was wrong")
        self.assertEqual(0, code)
        self.assertGreater(len(out.strip()), 100,
                           "the hook injected nothing for an unambiguous feedback prompt")

    def test_it_stays_silent_outside_a_bootcamp(self):
        """The property that keeps the plugin out of unrelated Claude Code sessions."""
        code, out = run_hook("Bootcamp feedback: something is wrong", in_bootcamp=False)
        self.assertEqual(0, code)
        self.assertEqual("", out.strip(),
                         "the hook spoke with no config/bootcamp_progress.json present")


class TheUnambiguousHalfIsCaught(unittest.TestCase):
    def test_every_feedback_phrasing_injects_the_workflow(self):
        for prompt in HITS:
            with self.subTest(prompt=prompt):
                _code, out = run_hook(prompt)
                self.assertIn("bootcamp feedback workflow", out.lower(),
                              "no feedback workflow injected for %r" % prompt)

    def test_the_injection_carries_its_guarantees(self):
        """A hit that omits the guarantees is the same loss as a miss."""
        _code, out = run_hook("I'd like to give feedback")
        for needle in ("INV-067", "INV-015", "APPEND"):
            with self.subTest(needle=needle):
                self.assertIn(needle, out,
                              "the injected guidance dropped %s" % needle)


class TheAmbiguousHalfStaysQuiet(unittest.TestCase):
    """⛔ Widening this pattern past here derails Modules 5–7."""

    def test_bare_fault_language_does_not_inject(self):
        for prompt in MISSES:
            with self.subTest(prompt=prompt):
                _code, out = run_hook(prompt)
                self.assertNotIn("bootcamp feedback workflow", out.lower(),
                                 "%r triggered the feedback workflow; in Modules 5-7 this "
                                 "is the bootcamper's own code and the injection derails "
                                 "the debugging turn" % prompt)

    def test_the_same_words_with_a_referent_do_inject(self):
        """The pair that proves the distinction is a distinction and not a gap."""
        for bare, attributed in (
            ("I found a bug", "I found a bug in the bootcamp"),
            ("something is broken", "something is broken in this plugin"),
        ):
            with self.subTest(pair=bare):
                _c, quiet = run_hook(bare)
                _c, loud = run_hook(attributed)
                self.assertNotIn("bootcamp feedback workflow", quiet.lower())
                self.assertIn("bootcamp feedback workflow", loud.lower(),
                              "%r did not trigger, so the attributed half is missing "
                              "rather than the bare half being excluded" % attributed)


class TheVerbosityBranchToleratesQualifiers(unittest.TestCase):
    def test_natural_verbosity_requests_are_caught(self):
        for prompt in VERBOSITY_HITS:
            with self.subTest(prompt=prompt):
                _code, out = run_hook(prompt)
                self.assertIn("verbosity", out.lower(),
                              "no verbosity guidance injected for %r" % prompt)


class TheReasoningIsRecordedAtThePattern(unittest.TestCase):
    """The regex will be edited again; the reasoning will not be rediscovered."""

    def setUp(self):
        self.source = HOOK.read_text(encoding="utf-8")

    def test_the_asymmetry_is_explained(self):
        self.assertIn("THE TWO HALVES OF THIS VOCABULARY ARE NOT SYMMETRIC", self.source,
                      "the comment explaining why bare fault language is excluded is gone")
        self.assertIn("missed capture is far cheaper than a spurious one",
                      self.source.replace("\n#", "").replace("\n", " "),
                      "the trade-off is not stated, so a future reader reads the gap as "
                      "an oversight")

    def test_it_forbids_deleting_the_distinction(self):
        flat = self.source.replace("\n#", " ").replace("\n", " ")
        self.assertIn('Do not "fix" a miss by deleting that distinction', flat,
                      "nothing warns the next editor off the obvious wrong fix")

    def test_the_excluded_referents_are_explained(self):
        flat = self.source.replace("\n#", " ").replace("\n", " ")
        self.assertIn('Deliberately does NOT include "this step"', flat,
                      "the narrowest and least obvious choice — excluding 'this step' — "
                      "has no reason recorded beside it")


if __name__ == "__main__":
    unittest.main()
