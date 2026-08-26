"""A flow that claims hook-triggered dispatch names a vocabulary the hook actually carries.

`packaging.md` shipped this on 2026-08-26:

    Triggered by the `/package-bootcamp` command, or whenever the bootcamper says something
    like "back up the bootcamp", "archive this", "move this to another machine", …

The command half was real. **The phrase half was reached by nothing.** The plugin's
`UserPromptSubmit` hook runs `scripts/feedback-capture.py`, which dispatches on the feedback and
note vocabularies only; no pattern anywhere matched "back up", "archive", "zip" or "transfer".

⛔ **The wording was templated from a sibling that HAS the hook, which is what made it
misleading.** `notes.md` reads *"Triggered by the plugin's `UserPromptSubmit` hook, by the
`/bootcamp-note` command, or whenever the bootcamper says something like…"* — three routes, the
first genuinely implemented. Dropping the hook clause and keeping the phrase clause left a
sentence that reads as the same guarantee with one route fewer, rather than as a guarantee that
was never built.

Nothing was broken by it: the command works, so the feature is reachable. What is wrong is a
claim about machinery that does not exist — the class that survives review by reading as prose.

Per **INV-246** the site set is derived by scanning shipped any-time flows for the
trigger-sentence shape, never by naming the two known files: a third any-time flow inherits the
same trap, and the template it would copy is the one that caused this.

⚠️ **This guard checks correspondence, not the absence of a hook.** A flow may legitimately gain
a hook later; what it may not do is claim one it lacks. So a flow claiming hook dispatch must
name a vocabulary `feedback-capture.py` carries, and a flow with no hook must say so.

Stdlib only; shipped markdown and the hook script read as text (INV-108).

Source spec: `specs/packaging-claims-natural-language-triggers-nothing-routes.md`.

Run:  python3 -m unittest discover -s tests
"""
import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
ONBOARDING = PLUGIN / "skills" / "bootcamp-onboarding"
HOOKS_JSON = PLUGIN / "hooks" / "hooks.json"
DISPATCHER = PLUGIN / "scripts" / "feedback-capture.py"

#: An any-time flow: a shipped file whose title says so. That phrase is the INV-254 marker and
#: is present whether or not the flow claims a hook, so the scan cannot miss a defective flow
#: by keying on the defect.
ANY_TIME_TITLE = re.compile(r"(?im)^#\s+.*\(available at any time\)")

#: A claim that the UserPromptSubmit hook routes prompts into this flow.
CLAIMS_HOOK = re.compile(r"(?i)Triggered by the plugin's `UserPromptSubmit` hook")

#: An explicit statement that no hook routes this flow.
DISCLAIMS_HOOK = re.compile(r"(?i)There is no hook for this flow")


def flat(text):
    return " ".join(text.split())


def any_time_flows():
    """(path, text) for every shipped any-time flow."""
    out = []
    for path in sorted(PLUGIN.glob("skills/**/*.md")):
        text = path.read_text(encoding="utf-8")
        if ANY_TIME_TITLE.search(text):
            out.append((path, text))
    return out


class TheScanFindsTheAnyTimeFlows(unittest.TestCase):
    def test_both_known_flows_are_found(self):
        names = {path.name for path, _ in any_time_flows()}
        self.assertIn("notes.md", names)
        self.assertIn("packaging.md", names)
        self.assertGreaterEqual(
            len(names), 2,
            "fewer than the two shipped any-time flows were found; the '(available at any "
            "time)' title marker has drifted and every assertion below is vacuous",
        )


class TheDispatcherIsWiredWhereItIsClaimed(unittest.TestCase):
    def test_the_user_prompt_submit_hook_runs_the_dispatcher(self):
        """Anti-vacuity: the correspondence checks below assume this wiring exists."""
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        entries = data.get("hooks", data).get("UserPromptSubmit", [])
        commands = [h.get("command", "") for e in entries for h in e.get("hooks", [])]
        self.assertTrue(
            any("feedback-capture.py" in c for c in commands),
            "UserPromptSubmit no longer runs feedback-capture.py; the flows that claim hook "
            "dispatch are now claiming something with no implementation at all",
        )

    def test_the_dispatcher_carries_the_note_vocabulary(self):
        """`notes.md`'s hook claim is TRUE, and must keep being checkable."""
        source = DISPATCHER.read_text(encoding="utf-8")
        self.assertRegex(
            source, r"(?i)\bnote\b",
            "feedback-capture.py no longer mentions the note vocabulary, so notes.md's "
            "UserPromptSubmit claim would now be as unfounded as packaging.md's was",
        )

    def test_the_dispatcher_carries_no_packaging_vocabulary(self):
        """The premise of the fix: adding one is a separate, deliberate decision.

        ⚠️ If a packaging vocabulary is ever added, this test SHOULD fail — and the correct
        response is to restore packaging.md's hook claim, not to weaken this assertion. The
        precedence question that addition raises ("back up my notes" is ambiguous between two
        of three vocabularies) is why it was deferred rather than done.
        """
        source = DISPATCHER.read_text(encoding="utf-8").lower()
        for term in ("archive", "zip it", "package the bootcamp"):
            with self.subTest(term=term):
                self.assertNotIn(term, source)


class EveryFlowsTriggerClaimMatchesReality(unittest.TestCase):
    def test_a_flow_claiming_the_hook_names_a_carried_vocabulary(self):
        source = DISPATCHER.read_text(encoding="utf-8").lower()
        for path, text in any_time_flows():
            if not CLAIMS_HOOK.search(text):
                continue
            with self.subTest(path=path.name):
                # The only vocabularies the dispatcher carries today.
                self.assertTrue(
                    any(v in source for v in ("note", "feedback")),
                    "%s claims UserPromptSubmit dispatch but the dispatcher carries neither "
                    "vocabulary" % path.name,
                )

    def test_a_flow_with_no_hook_says_so(self):
        """The finding, stated as the rule: silence is what made the claim misleading."""
        for path, text in any_time_flows():
            if CLAIMS_HOOK.search(text):
                continue  # it claims one; the test above checks the claim
            with self.subTest(path=path.name):
                self.assertTrue(
                    DISCLAIMS_HOOK.search(text),
                    "%s is an any-time flow that neither claims the UserPromptSubmit hook nor "
                    "states that no hook routes it. If it lists phrasings as triggers, a reader "
                    "takes them for intercepted prompts -- the packaging.md defect of "
                    "2026-08-26" % path.name,
                )

    def test_a_flow_with_no_hook_still_tells_the_guide_to_recognize_the_phrasings(self):
        """Disclaiming the hook must not throw away the useful half."""
        for path, text in any_time_flows():
            if CLAIMS_HOOK.search(text) or not DISCLAIMS_HOOK.search(text):
                continue
            with self.subTest(path=path.name):
                self.assertRegex(
                    flat(text), r"(?i)recognize these as a request for it",
                    "%s says there is no hook but does not tell the guide to recognize the "
                    "phrasings itself, so the correction removed a real capability" % path.name,
                )


class TheSiblingsClaimIsUnchanged(unittest.TestCase):
    """`notes.md`'s hook clause is accurate; harmonizing the two must not overwrite it."""

    def test_notes_still_claims_the_hook(self):
        text = (ONBOARDING / "notes.md").read_text(encoding="utf-8")
        self.assertTrue(
            CLAIMS_HOOK.search(text),
            "notes.md's UserPromptSubmit clause was removed. It is TRUE -- the hook runs "
            "feedback-capture.py, which carries the note vocabulary -- and deleting it to "
            "match packaging.md's corrected wording would lose a real route",
        )


if __name__ == "__main__":
    unittest.main()
