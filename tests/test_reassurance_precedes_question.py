"""Anything meant to inform an answer is written BEFORE its 👉 question, never after.

Two reasons, the first mechanical: nothing may follow the 👉, because it ends the turn — so
text placed after it is either never delivered or delivered a turn late. The second is that a
caveat arriving after the answer cannot inform the choice it exists to inform.

Bootcamp preparation Step 3 states this correctly and gives the reason. Two other sites did
not, and both were resolved only by a guide importing the reasoning from a different file:

1. **Module 1 Phase 2 Step 10a** printed `Reassure: "We'll develop everything locally first…"`
   *after* the pinned deployment-target question AND after `*(Internal: end the turn and
   wait.)*`. That reassurance is what makes "4. Not sure yet" a comfortable answer rather than
   a guess.
2. **The visualization teardown gate** said "Tell the bootcamper what they are consenting to
   **before they answer**" — in a paragraph placed *below* the gate. Found by sweeping for this
   spec rather than by the walk that motivated it, and it is the worse of the two: the consent
   authorizes an irreversible teardown, and the file's own next sentence is "A yes given
   without that is not an informed yes."

The general guard here keys on that second shape, because it is **self-contradicting in its own
words** and therefore mechanically decidable: an instruction saying to do something *before they
answer*, positioned after the question, cannot be followed as written. A broader "no prose after
a 👉" sweep is not viable — these are skill files written for the guide, so answer-handling
instructions ("on yes, …") legitimately and frequently follow a question. Surveyed before
writing this: five speech-cue lines follow a 👉 across all skills, and three are legitimate
answer handling. Guarding the decidable shape beats a broad rule with three standing exceptions.

Enforces **INV-211**.

Run:  python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
GROUND_RULES = SKILLS / "bootcamp-onboarding" / "ground-rules.md"
STEP_10A = SKILLS / "module-01-business-problem" / "phase2-document-confirm.md"
TEARDOWN = SKILLS / "module-03b-truthset-visualization" / "visualization-api-reference.md"
PREP = SKILLS / "bootcamp-preparation" / "SKILL.md"

POINTER = "\U0001f449"
#: Self-contradicting when it appears after a 👉: an instruction to act before the answer.
BEFORE_ANSWERING = re.compile(r"(?i)before (?:they|you) answer|before answering|before the answer")


def sections(text):
    """[(heading, [lines])] — split on Markdown headings, which bound a step."""
    out, head, buf = [], "(top)", []
    for line in text.splitlines():
        if line.startswith("#"):
            out.append((head, buf))
            head, buf = line.strip(), []
        else:
            buf.append(line)
    out.append((head, buf))
    return out


def misplaced_before_answer_instructions():
    """[(relpath, heading, line)] for a 'before they answer' cue following a 👉 in one section."""
    bad = []
    for path in sorted(SKILLS.rglob("*.md")):
        for head, lines in sections(path.read_text(encoding="utf-8")):
            seen_pointer = False
            for line in lines:
                if POINTER in line:
                    seen_pointer = True
                    continue
                if seen_pointer and BEFORE_ANSWERING.search(line):
                    bad.append((str(path.relative_to(REPO_ROOT)), head, line.strip()[:120]))
    return bad


def index_of(lines, predicate):
    for i, line in enumerate(lines):
        if predicate(line):
            return i
    return -1


class TheRuleIsStatedOnce(unittest.TestCase):
    def test_ground_rules_states_the_ordering_rule_in_the_pointer_protocol(self):
        text = GROUND_RULES.read_text(encoding="utf-8")
        start = text.index("## Conversation protocol")
        end = text.index("\n## ", start)
        protocol = text[start:end]
        self.assertRegex(
            protocol,
            r"(?i)before the .?\U0001f449|goes BEFORE",
            "ground-rules' 👉 protocol must state that anything informing the answer precedes "
            "the question. Stated only inside one step, it did not propagate to two others.",
        )
        self.assertRegex(
            protocol,
            r"(?i)ends the turn|nothing may follow",
            "the rule must carry its mechanical reason — nothing may follow the 👉 — or it "
            "reads as a style preference and gets 'tidied' back.",
        )
        self.assertRegex(
            protocol,
            r"(?i)answer.handling|on yes",
            "the rule must carve out answer-handling instructions, which legitimately follow "
            "a question; without that it over-reaches and will be ignored.",
        )


class NoInstructionSaysBeforeTheAnswerAfterTheQuestion(unittest.TestCase):
    def test_no_skill_places_a_before_they_answer_cue_after_its_pointer(self):
        bad = misplaced_before_answer_instructions()
        self.assertEqual(
            [], bad,
            "an instruction to do something 'before they answer' is positioned AFTER the 👉, "
            "which cannot be followed as written — nothing may follow the 👉:\n  "
            + "\n  ".join(f"{p} [{h}] {ln}" for p, h, ln in bad),
        )

    def test_the_detector_finds_the_shape_it_guards(self):
        """Non-vacuity: the scan must fire on the historical arrangement."""
        historical = [
            "- teardown gate. → \U0001f449 **Ready for me to stop the server?**",
            "",
            "Tell the bootcamper what they are consenting to before they answer: the URL dies.",
        ]
        seen, hits = False, []
        for line in historical:
            if POINTER in line:
                seen = True
                continue
            if seen and BEFORE_ANSWERING.search(line):
                hits.append(line)
        self.assertEqual(1, len(hits), "the detector must fire on the shape it was built for")

    def test_the_detector_ignores_answer_handling_that_follows_a_question(self):
        """Answer handling after a 👉 is correct and must not be flagged."""
        ok = [
            "\U0001f449 **Will your results interface with other software?**",
            "",
            "On **yes**, ask one follow-up on the next turn and hold the named systems.",
            "If the bootcamper skips, default to verbose, persist it, and say so.",
        ]
        seen, hits = False, []
        for line in ok:
            if POINTER in line:
                seen = True
                continue
            if seen and BEFORE_ANSWERING.search(line):
                hits.append(line)
        self.assertEqual([], hits, "answer-handling instructions must not trip the scan")


class TheTwoFixedSitesStayFixed(unittest.TestCase):
    def test_step_10a_reassurance_precedes_the_deployment_question(self):
        lines = STEP_10A.read_text(encoding="utf-8").splitlines()
        q = index_of(lines, lambda l: POINTER in l and "Where do you plan to deploy" in l)
        r = index_of(lines, lambda l: "Reassure them first" in l)
        self.assertNotEqual(-1, q, "the deployment-target question moved — retarget this test")
        self.assertNotEqual(-1, r, "Step 10a must reassure before asking")
        self.assertLess(
            r, q,
            "the reassurance must appear BEFORE the deployment-target question; it is what "
            "makes 'Not sure yet' a comfortable answer rather than a guess",
        )

    def test_the_teardown_consent_disclosure_precedes_the_gate(self):
        lines = TEARDOWN.read_text(encoding="utf-8").splitlines()
        gate = index_of(lines, lambda l: POINTER in l and "stop the visualization server" in l)
        disclosure = index_of(lines, lambda l: "state what they are consenting to" in l)
        self.assertNotEqual(-1, gate, "the teardown gate moved — retarget this test")
        self.assertNotEqual(-1, disclosure, "the consent disclosure must be present")
        self.assertLess(
            disclosure, gate,
            "the consent disclosure must precede the teardown gate — the consent authorizes "
            "an irreversible teardown, so a disclosure after the answer is worth nothing",
        )

    def test_bootcamp_preparation_step_3_still_models_the_pattern(self):
        """The one site that always had it right — keep it as the reference example."""
        lines = PREP.read_text(encoding="utf-8").splitlines()
        q = index_of(lines, lambda l: POINTER in l and "How much detail" in l)
        r = index_of(lines, lambda l: "tell them the choice is not permanent" in l)
        self.assertNotEqual(-1, q)
        self.assertNotEqual(-1, r)
        self.assertLess(r, q)


if __name__ == "__main__":
    unittest.main()
