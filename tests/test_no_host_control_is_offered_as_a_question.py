"""No 👉 question offers a session- or host-level control, and the rule that says so ships.

A bootcamper on plugin 0.5.0 was asked about "auto-mode for the bootcamp" during the
onboarding preface, with `👉 Do you have any questions before we get started?` pending and
unanswered. No file in the plugin asks that — a repo-wide search for `auto-mode`, `auto mode`,
`auto-accept`, `permission mode`, `plan mode`, `fast mode` and `bypass permissions` across
`plugins/`, `.claude/` and `tests/` returned zero matches. The question came from outside the
bootcamp's scripted flow, and nothing on the books forbade it: the 👉 protocol governed a
question's count (INV-005), shape (INV-008/INV-009/INV-051), placement (INV-211/INV-224) and,
for pinned gates, verbatim wording (INV-056) — never its provenance.

One thing also made such a question look native. The bootcamp already asks the bootcamper to
operate `/model` and `/effort` at module start (INV-063/INV-098/INV-158/INV-236) and named no
boundary, so a bootcamper who has been asked *"Would you like to switch to `/model …` +
`/effort …` for this module?"* had no way to tell an "auto-mode?" question from bootcamp
content.

Enforces **INV-247** — every 👉 question traces to a step in a shipped skill file, and no
session- or host-level control other than the model/effort switch is presented as a bootcamp
question.

⛔ **THIS GUARD CANNOT DETECT THE REPORTED SYMPTOM, AND A CLEAN RUN IS NOT EVIDENCE IT IS
GONE.** The defect was a question improvised at runtime that exists in **no file**; this test
reads files. What it does cover is the other direction, which is real but narrower: it keeps
the rule shipped in `ground-rules.md`, and it fails if a future module adds a second
interface question by accident. Do not read a green run as "the bootcamp can no longer ask
about auto mode" — that half is unreachable from a static check, and claiming otherwise is
the pattern `specs/coverage-reports-count-known-non-defects-as-hits.md` exists to stop.

Per **INV-246** the site set is derived by scanning every shipped Markdown file under
`plugins/senzing-bootcamp/`, never from a hardcoded list — a listed guard would certify the
files the author already thought of and miss a module added later, which is the only site
that matters.

Source spec: `specs/a-question-with-no-origin-in-a-skill-file-reached-the-bootcamper.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
GROUND_RULES = PLUGIN / "skills" / "bootcamp-onboarding" / "ground-rules.md"

# A pinned 👉 question: the pointer immediately followed by the bold question text. Prose that
# *talks about* 👉 questions (including the rule below) does not match, because there the
# pointer sits inside a sentence rather than ahead of a bolded question.
PINNED_QUESTION = re.compile("\U0001F449" + r"\s*\*\*")

# Session- or host-level controls: the bootcamper's Claude interface, not the bootcamp's to
# offer. `/model` and `/effort` are deliberately absent — they are the sole exception.
HOST_CONTROL = re.compile(
    r"(?i)auto[-\s]?mode"
    r"|auto[-\s]?accept"
    r"|permission[-\s]mode"
    r"|plan[-\s]mode"
    r"|fast[-\s]mode"
    r"|bypass[-\s]permission"
    r"|background[-\s]task"
    r"|/compact\b"
    r"|/loop\b"
)

# An affirmative claim that the plugin removes a host control. It cannot: a plugin ships
# skills, hooks and commands, and none of those reach the host's own affordances. Writing the
# claim anyway would paper over the scope change this spec had to make.
SUPPRESSION_CLAIM = re.compile(
    r"(?i)\b(?:the\s+)?(?:bootcamp|plugin|we)\s+(?:can\s+)?"
    r"(?:suppress(?:es)?|disable[sd]?|turn(?:s)?\s+off|hide[sd]?|override[sd]?)\s+"
    r"(?:the\s+)?(?:auto|permission|plan|fast|host)"
)


def shipped_markdown():
    """Every shipped Markdown file, discovered rather than listed (INV-246)."""
    return sorted(PLUGIN.rglob("*.md"))


def read(path):
    return path.read_text(encoding="utf-8")


def squash(text):
    return re.sub(r"\s+", " ", text)


def section(text, heading):
    """The body of one `## ` section, so a rule can be required WHERE it binds."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == heading:
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## "):
                    return squash("\n".join(lines[i:j]))
            return squash("\n".join(lines[i:]))
    raise AssertionError("heading not found in ground-rules.md: %r" % heading)


class NoShippedQuestionOffersAHostControl(unittest.TestCase):
    def test_the_corpus_is_actually_being_scanned(self):
        """A guard that silently matched nothing would pass forever."""
        files = shipped_markdown()
        self.assertGreater(len(files), 20,
                           "the shipped Markdown sweep found almost nothing — the corpus "
                           "moved and this guard is now inspecting an empty set")
        questions = [(p, n, line)
                     for p in files
                     for n, line in enumerate(read(p).splitlines(), 1)
                     if PINNED_QUESTION.search(line)]
        self.assertGreater(len(questions), 50,
                           "the pinned-question pattern matched almost nothing — the 👉 "
                           "question form changed and this guard no longer sees questions")

    def test_no_pinned_question_names_a_session_or_host_control(self):
        offenders = []
        for path in shipped_markdown():
            for n, line in enumerate(read(path).splitlines(), 1):
                if PINNED_QUESTION.search(line) and HOST_CONTROL.search(line):
                    rel = path.relative_to(REPO_ROOT)
                    offenders.append("%s:%d: %s" % (rel, n, line.strip()[:140]))
        self.assertEqual(
            [], offenders,
            "a 👉 question offers a control that belongs to the bootcamper's Claude session, "
            "not to the bootcamp (INV-247). The model/effort switch is the only "
            "Claude-interface control the bootcamp asks them to operate:\n  "
            + "\n  ".join(offenders))

    def test_the_model_effort_switch_is_still_asked_as_a_question(self):
        """The exception must survive — otherwise this guard passes by deleting the rule's subject."""
        asked = [line
                 for path in shipped_markdown()
                 for line in read(path).splitlines()
                 if PINNED_QUESTION.search(line) and re.search(r"/model|/effort|reasoning effort", line)]
        self.assertTrue(asked,
                        "no 👉 question offers the model/effort switch any more; INV-247 names "
                        "it as the sole exception, so its disappearance means the exception or "
                        "the question form changed")

    def test_no_shipped_file_claims_the_plugin_suppresses_a_host_control(self):
        offenders = []
        for path in shipped_markdown():
            for n, line in enumerate(read(path).splitlines(), 1):
                if SUPPRESSION_CLAIM.search(line):
                    rel = path.relative_to(REPO_ROOT)
                    offenders.append("%s:%d: %s" % (rel, n, line.strip()[:140]))
        self.assertEqual(
            [], offenders,
            "a shipped file claims the bootcamp removes a host control. It cannot — a plugin "
            "ships skills, hooks and commands, none of which reach the host's own "
            "affordances — and the claim would hide the scope this spec had to narrow to:\n  "
            + "\n  ".join(offenders))


class TheRuleShipsWhereItBinds(unittest.TestCase):
    def setUp(self):
        self.text = read(GROUND_RULES)

    def test_the_protocol_closes_the_question_set(self):
        protocol = section(self.text, "## Conversation protocol (the 👉 rules)")
        self.assertRegex(
            protocol, r"(?i)traces to a step in a shipped skill file",
            "the 👉 protocol still governs only a question's count, shape and placement — "
            "nothing requires a question to come from a step in a skill file (INV-247)")
        self.assertRegex(
            protocol, r"(?i)never present a session- or host-level control as a bootcamp question",
            "the protocol does not name the class of question that produced this defect")
        self.assertRegex(
            protocol, r"INV-247",
            "the closed-question-set rule ships without its invariant ID, so a later editor "
            "cannot look up why it is there (INV-183)")

    def test_the_protocol_says_answering_a_bootcamper_question_is_not_originating_one(self):
        protocol = section(self.text, "## Conversation protocol (the 👉 rules)")
        self.assertRegex(
            protocol, r"(?i)answering a question the bootcamper asks is not originating one",
            "the rule reads as forbidding the guide to respond when a bootcamper raises a "
            "host control, which would strand them at a pending gate")

    def test_the_sole_exception_is_stated_where_the_precedent_is_set(self):
        """A limit stated only in the protocol is read by nobody writing a new nudge."""
        banners = section(self.text, "## Module start banners and transitions")
        self.assertRegex(
            banners, r"(?i)ONLY Claude-interface control the bootcamp asks the bootcamper to operate",
            "the model/effort section does not say it is the only Claude-interface control "
            "the bootcamp offers, so a reader adding a second one never meets the limit "
            "(INV-247)")
        self.assertRegex(
            banners, r"INV-247",
            "the sole-exception line ships without its invariant ID")

    def test_a_bootcamper_question_about_a_host_control_has_a_stated_answer(self):
        controls = section(self.text, "## Any-time bootcamper controls")
        self.assertRegex(
            controls, r"(?i)a question about a host control",
            "the any-time controls have no entry for a bootcamper asking about a host "
            "control, which is what happened here — at a pending gate (INV-247)")
        self.assertRegex(
            controls, r"(?i)one sentence",
            "the handling line does not bound the answer, so a session setting can grow into "
            "a detour of its own")
        self.assertRegex(
            controls, r"(?i)re-present the pending .{0,4} question verbatim",
            "the handling line does not return the bootcamper to the pending question, which "
            "is the half the reported run actually lost")


if __name__ == "__main__":
    unittest.main()
