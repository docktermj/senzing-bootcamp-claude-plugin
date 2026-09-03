"""`README.md` must not tell the Bootcamper which Claude interfaces exist.

Before the 2026-08-26 fix, the install walkthrough opened with:

    Claude Code has two interfaces you can run it in.
    Pick either:
    - Claude Desktop …
    - Claude Code CLI …

**INV-098 handles four** — the Claude Code CLI, Claude Desktop, the Claude web app, and a Claude
IDE extension — so the plugin had interface-specific behavior for two contexts its own front door
said did not exist.

⛔ **The severity is that "pick either" is an INSTRUCTION, not a description.** A Bootcamper
running Claude Code in the web app or a VS Code / JetBrains extension read it, found neither
option described what they were using, and had no install path — while the bootcamp itself would
have adapted correctly once started.

⚠️ **The fix is scoping the sentence, not inventing install steps.** The walkthrough may
legitimately carry verified steps for two interfaces; what it may not do is assert that two is
all there are. Adding unverified instructions for the other two would be a new defect, so this
guard checks that the other contexts are **named and their install path disclosed as unverified**
— never that steps exist for them (INV-111/INV-163's disclose-rather-than-imply discipline).

⛔ **The context list is derived from INV-098's own text**, not hardcoded here, so this guard
cannot go stale the way the prose did. If INV-098 gains a fifth context, this test starts
requiring it.

Stdlib only; INVARIANTS.md and the READMEs read as text (INV-108).

Source spec: `specs/readme-claims-two-interfaces-while-inv098-handles-four.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOP_README = REPO_ROOT / "README.md"
USER_DOCS = REPO_ROOT / "docs" / "README.md"
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"

#: Prose asserting how many interfaces Claude Code has.
INTERFACE_COUNT = re.compile(
    r"(?i)Claude Code has\s+(one|two|three|four|five|\d+)\s+interfaces")

#: The contexts INV-098 enumerates, read out of the invariant itself.
CONTEXT_NAMES = ("Claude Code CLI", "Claude Desktop", "Claude web app", "Claude IDE extension")


def inv098_text():
    for line in INVARIANTS.read_text(encoding="utf-8").splitlines():
        if line.startswith("- **INV-098**"):
            return line
    raise AssertionError("INV-098 not found in INVARIANTS.md")


def contexts_from_inv098():
    """The interface contexts INV-098 actually names, derived rather than assumed."""
    text = inv098_text()
    return [name for name in CONTEXT_NAMES if name.lower() in text.lower()]


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class TheDerivationIsNotVacuous(unittest.TestCase):
    """INV-265 — an empty context list would satisfy every assertion below."""

    def test_inv098_still_enumerates_several_contexts(self):
        contexts = contexts_from_inv098()
        self.assertGreaterEqual(
            len(contexts), 3,
            "INV-098 now names fewer than three interface contexts (%s). Either the invariant "
            "changed -- in which case this guard's expectations should follow it -- or the "
            "derivation has drifted and the checks below are vacuous" % contexts)
        self.assertIn("Claude web app", contexts,
                      "INV-098 no longer names the Claude web app; if that is deliberate, this "
                      "test and README.md should both be revisited together")


class TheReadmeStatesNoInterfaceCount(unittest.TestCase):
    def test_no_count_of_interfaces(self):
        hit = INTERFACE_COUNT.search(TOP_README.read_text(encoding="utf-8"))
        self.assertIsNone(
            hit,
            "README.md asserts how many interfaces Claude Code has (%r). It is not the plugin's "
            "fact to state, it goes stale silently, and it made 'pick either' unanswerable for "
            "readers in the contexts it omitted" % (hit.group(0) if hit else ""))

    def test_it_does_not_tell_the_reader_to_pick_from_a_partial_set(self):
        self.assertNotIn(
            "interfaces you can run it in. Pick either", flat(TOP_README),
            "README.md still instructs the reader to pick from a two-item set presented as "
            "exhaustive")

    def test_it_says_the_plugin_works_wherever_claude_code_runs(self):
        """The replacement claim, which is true and does not need maintaining."""
        self.assertRegex(
            flat(TOP_README), r"(?i)works wherever Claude Code runs",
            "README.md no longer states that the plugin works wherever Claude Code runs, so "
            "scoping the walkthrough to two interfaces reads as a limitation of the plugin")


class EveryContextInv098HandlesIsNamed(unittest.TestCase):
    def test_each_context_appears_in_the_user_facing_docs(self):
        docs = flat(TOP_README) + " " + flat(USER_DOCS)
        for context in contexts_from_inv098():
            with self.subTest(context=context):
                # INV-098 says "a Claude IDE extension"; the README may pluralize.
                stem = context.replace("Claude IDE extension", "IDE extension")
                self.assertIn(
                    stem, docs,
                    "INV-098 adapts the bootcamp's behavior to '%s', and no user-facing document "
                    "mentions it -- so a Bootcamper there is not told the plugin supports them"
                    % context)

    def test_the_unverified_install_paths_are_disclosed_as_unverified(self):
        """Naming them must not imply steps were tested for them."""
        self.assertRegex(
            flat(TOP_README), r"(?i)no verified install steps for them",
            "README.md names the other contexts without disclosing that it has no verified "
            "install steps for them, which implies coverage it does not have")

    def test_it_tells_those_readers_what_to_do_instead(self):
        self.assertRegex(
            flat(TOP_README), r"(?i)install the plugin the way your client installs plugins",
            "README.md names the other contexts and disclaims steps for them without saying "
            "what those readers should do, which leaves 'pick either' unanswered by another route")


if __name__ == "__main__":
    unittest.main()
