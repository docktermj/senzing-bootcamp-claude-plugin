"""Feedback is triaged plugin-vs-MCP-server, recorded locally either way, and only
forwarded upstream on an explicit yes.

A bootcamper reports a symptom; identifying which component owns it is the plugin's job.
Two of the defects filed during development were upstream — `mapping_workflow` returning a
truncated validation error, `get_sdk_reference` not covering parameter shapes — and a report
that sits only in the local file reaches the wrong maintainer and gets fixed nowhere.

Three properties this pins, because getting any of them wrong is worse than not triaging:

* **Local capture is unconditional (INV-015).** The routing verdict decides whether an
  *additional* upstream submission is offered — never whether the entry is saved. Routing
  exclusively would breach INV-015 and would also lose the bootcamper their own record.
* **Nothing leaves the machine without an explicit yes.** `submit_feedback` publishes
  externally and its own contract requires showing the exact message and confirming first;
  submissions are anonymous, so a bootcamper who says yes gets no reply channel and must be
  told that before answering.
* **The bootcamper's data never leaves as part of a bug report.** Entity names and record
  IDs are theirs (INV-065) — an upstream message describes the shape of a problem, never the
  content of their records.

Run:  python3 -m unittest discover -s tests
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
FEEDBACK = PLUGIN / "skills" / "bootcamp-onboarding" / "feedback.md"
COMMAND = PLUGIN / "commands" / "bootcamp-feedback.md"
HOOK = PLUGIN / "scripts" / "feedback-capture.py"
GRADUATION = PLUGIN / "skills" / "graduation" / "SKILL.md"

FEEDBACK_PATH = "docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md"
VERDICTS = ("plugin", "mcp-server", "both", "unclear")


def read(path):
    return Path(path).read_text()


def plain(text):
    return re.sub(r"\s+", " ", text.replace("**", ""))


def triage_step():
    t = read(FEEDBACK)
    return t[t.index("## Step 2b: Triage") : t.index("## Step 3: Append")]


def forward_step():
    t = read(FEEDBACK)
    return t[t.index("## Step 3c: Offer to forward") : t.index("## Step 4: Confirm")]


def hook_context(prompt, active=True):
    """Run the UserPromptSubmit hook. It is deliberately inert outside an active bootcamp,
    so the activation marker must exist for it to fire at all."""
    cwd = tempfile.mkdtemp()
    if active:
        os.makedirs(os.path.join(cwd, "config"), exist_ok=True)
        with open(os.path.join(cwd, "config", "bootcamp_progress.json"), "w") as fh:
            fh.write("{}")
    proc = subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps({"prompt": prompt}),
        capture_output=True, text=True, cwd=cwd,
    )
    if not proc.stdout.strip():
        return ""
    return json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]


class TriageStepExists(unittest.TestCase):
    def test_workflow_has_a_triage_step(self):
        self.assertIn("## Step 2b: Triage", read(FEEDBACK))

    def test_all_four_verdicts_are_defined(self):
        step = triage_step()
        for verdict in VERDICTS:
            with self.subTest(verdict=verdict):
                self.assertIn(f"`{verdict}`", step)

    def test_triage_is_silent_not_a_question(self):
        """The bootcamper reported a symptom; naming the component is not their job."""
        step = triage_step()
        self.assertIn("no 👉 question", step)
        posed = [l for l in step.splitlines() if l.lstrip().startswith("👉")]
        self.assertEqual([], posed, "triage must not pose a question to the bootcamper")

    def test_the_discriminating_test_is_stated_both_ways(self):
        squashed = plain(triage_step())
        self.assertIn("Would this still happen if the bootcamp plugin were perfect?", squashed)
        self.assertIn("Would this still happen if the Senzing MCP server were perfect?", squashed)

    def test_each_verdict_carries_concrete_examples(self):
        """Criteria without examples get applied inconsistently."""
        step = triage_step()
        for probe in ("mapping_workflow", "get_sdk_reference", "PDF generator", "flag documented"):
            with self.subTest(probe=probe):
                self.assertIn(probe, step)

    def test_misfiling_toward_plugin_is_called_out(self):
        self.assertIn("Do not soften an", plain(triage_step()))


class LocalCaptureIsUnconditional(unittest.TestCase):
    """INV-015 has no exception clause."""

    def test_triage_step_says_the_verdict_never_changes_local_recording(self):
        squashed = plain(triage_step())
        self.assertIn("The verdict never changes whether the entry is recorded locally", squashed)
        self.assertIn("INV-015", triage_step())

    def test_entry_template_carries_routing_and_upstream_fields(self):
        t = read(FEEDBACK)
        self.assertIn("**Routing:**", t)
        self.assertIn("**Upstream:**", t)

    def test_upstream_field_can_record_every_outcome(self):
        t = read(FEEDBACK)
        for outcome in ("not applicable", "offered, declined", "submitted", "submission failed"):
            with self.subTest(outcome=outcome):
                self.assertIn(outcome, t)

    def test_forward_step_runs_only_after_the_local_entry_is_confirmed(self):
        """Ordering matters: a failed send must never cost the bootcamper their record."""
        t = read(FEEDBACK)
        self.assertLess(
            t.index("## Step 3b: Verify it landed"),
            t.index("## Step 3c: Offer to forward"),
            "the durability check must precede any upstream offer",
        )
        self.assertIn("after Step 3b has confirmed", plain(forward_step()))

    def test_shipped_file_header_states_the_local_always_guarantee(self):
        """The artifact itself should tell the bootcamper what happened to their report."""
        t = read(FEEDBACK)
        header = t[t.index("# Senzing Bootcamp Plugin Feedback") :][:600]
        self.assertIn("Every entry is saved here", header)
        self.assertIn("only ever with your explicit yes", header)


class NothingLeavesWithoutConsent(unittest.TestCase):
    def setUp(self):
        self.step = forward_step()

    def test_offer_is_gated_on_the_verdict(self):
        squashed = plain(self.step)
        self.assertIn("Only when Step 2b's verdict is", squashed)
        self.assertIn("For `plugin` or `unclear`, skip this step entirely", squashed)

    def test_the_question_is_pinned_and_numbered(self):
        self.assertIn(
            "👉 **This looks like an issue in the Senzing MCP server rather than the bootcamp. "
            "Send the report above to Senzing? Reply with a number:**",
            self.step,
        )
        self.assertIn("1. **Yes, send it**", self.step)
        self.assertIn("2. **No, keep it local**", self.step)

    def test_exact_message_is_shown_before_asking(self):
        """The submit_feedback tool's own contract requires this."""
        squashed = plain(self.step)
        self.assertIn("Show the exact message and ask", squashed)
        self.assertIn("requires showing the", squashed)

    def test_anonymity_is_disclosed_before_the_bootcamper_answers(self):
        squashed = plain(self.step)
        self.assertIn("anonymous", squashed)
        self.assertIn("support@senzing.com", squashed)

    def test_asked_once(self):
        self.assertIn("INV-006", self.step)
        self.assertIn("do not re-offer", plain(self.step))

    def test_declining_is_free_and_failure_never_blocks(self):
        squashed = plain(self.step)
        self.assertIn("Saying no costs them nothing", squashed)
        self.assertIn("never blocks anything", squashed)

    def test_no_blanket_prohibition_remains_that_would_forbid_the_new_path(self):
        """The old rule said never submit externally; it must now point at the one sanctioned path."""
        t = read(FEEDBACK)
        self.assertNotIn(
            "Do NOT submit feedback to the Senzing MCP server or anywhere external unless", t
        )
        self.assertIn("The only sanctioned external path is Step 3c", plain(t))


class BootcamperDataNeverLeaves(unittest.TestCase):
    def test_identifying_details_must_be_stripped(self):
        squashed = plain(forward_step())
        for probe in ("hostname", "username", "IP\naddress".replace("\n", " "), "email"):
            with self.subTest(probe=probe):
                self.assertIn(probe, squashed)
        self.assertIn("INV-065", forward_step())

    def test_record_content_is_explicitly_out_of_scope(self):
        squashed = plain(forward_step())
        self.assertIn("describe the shape of the problem, never the", squashed)
        self.assertRegex(squashed, r"Entity names\s*and record IDs from their data are theirs")

    def test_message_must_be_self_contained(self):
        """The upstream reader cannot see this bootcamp."""
        squashed = plain(forward_step())
        self.assertIn("the recipient cannot see this bootcamp", squashed)
        self.assertIn("tool name", squashed)
        self.assertIn("SDK version", squashed)

    def test_category_mapping_is_specified(self):
        squashed = plain(forward_step())
        self.assertIn("`category` = `bug`", squashed.replace("**", ""))
        self.assertIn("`feature`", squashed)

    def test_server_response_is_relayed_verbatim(self):
        """It carries the anonymity notice and the only follow-up route."""
        self.assertIn("verbatim", plain(forward_step()))


class EveryEntryPointDescribesTheRouting(unittest.TestCase):
    """Three surfaces describe this flow; all must agree (INV-003)."""

    def test_slash_command_describes_triage_and_the_consent_gate(self):
        t = plain(read(COMMAND))
        self.assertIn("triage whether the issue is in this plugin or in the Senzing MCP server", t)
        self.assertIn("Every entry is recorded locally whatever the triage says", t)
        self.assertIn("never send anything external without that yes", t)

    def test_hook_injects_the_routing_instruction(self):
        ctx = hook_context("bootcamp feedback: a tool returned a truncated error")
        self.assertTrue(ctx, "the hook must recognise a feedback prompt")
        for probe in ("Triage", "Routing", "submit_feedback", "INV-015", "INV-065",
                      "showing the exact message"):
            with self.subTest(probe=probe):
                self.assertIn(probe, ctx)

    def test_hook_still_ignores_unrelated_prompts(self):
        self.assertEqual("", hook_context("what is entity resolution?"))

    def test_graduation_retrospective_triages_too(self):
        """Self-observed findings skew upstream — a tool behaving differently than documented
        is exactly what a bootcamper cannot report."""
        t = read(GRADUATION)
        start = t.index("## Step 0: Session retrospective")
        section = t[start : start + 4000]
        self.assertIn("**`Routing:`**", section)
        self.assertIn("**`Upstream:`**", section)
        self.assertIn("rather than defaulting it to `plugin`", plain(section))

    def test_retrospective_batches_the_offer(self):
        """One question for all findings, so the retrospective stays a single non-blocking step."""
        t = read(GRADUATION)
        start = t.index("## Step 0: Session retrospective")
        self.assertIn("Batch the offer", plain(t[start : start + 4000]))

    def test_retrospective_stays_non_blocking(self):
        t = read(GRADUATION)
        start = t.index("## Step 0: Session retrospective")
        section = t[start : start + 4500]
        self.assertIn("Non-blocking", section)
        self.assertIn("INV-015", section)


if __name__ == "__main__":
    unittest.main()
