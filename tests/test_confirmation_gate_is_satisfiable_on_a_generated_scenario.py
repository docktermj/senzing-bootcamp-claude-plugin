"""Module 1's confirmation gate can be followed on the generated-scenario path.

Step 15 opened with a hard rule -- "Present the document with BOTH versions visible" --
written for the path where the ``> "…"`` blockquotes exist. On the Business Case Offer
path they never do: all five quote-carrying sections are selections or bootcamp-authored,
and Step 11's own rule ("Where an answer was a selection rather than prose, OMIT the
quote -- never manufacture one") strips every one of them. The document correctly carries
ZERO quote lines, and the gate then asked for both versions of a document that has one.

⚠️ This is the *unsatisfiable-instruction* class, not a wrong instruction. The likely
responses are both bad: skip a ⛔ because it does not fit, or invent the quotes Step 11
forbids -- and INV-275 says an invented "verbatim" line is worse than none, because it
looks like evidence.

The risk INV-275 exists to catch is still live on the generated path: a bare option reply
("1 and 3") rendered as ``Master list`` instead of ``Master list and Reports`` narrows a
requirement that Module 7 step 1 reads as input, with nothing in the document to settle it.
So the branch must still name a comparison target, not merely excuse the missing quotes.

Observed live on 2026-08-31 during a `/dry-run` walk that accepted the Business Case Offer.

⚠️ The site set is DERIVED BY SCANNING shipped markdown for the both-versions
instruction, never hardcoded (INV-246): a guard listing the one path its author noticed
certifies that path and is blind to the one that matters.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "plugins" / "senzing-bootcamp" / "skills"
GATE = SKILLS / "module-01-business-problem" / "phase2-document-confirm.md"

PINNED = "👉 **Does this accurately capture your problem and approach?**"


def flat(s):
    return re.sub(r"\s+", " ", s)


def gates_demanding_both_versions():
    """Every gate SECTION instructing the guide to show BOTH versions of an artifact.

    Derived by scan so a second such gate cannot be added without this guard seeing it
    (INV-246), and returned as ``(file, section)`` rather than as a file.

    ⚠️ Returning the file was not enough, and the negative control proved it: with Step
    15's branch deleted, a file-level check still passed because Step 11 -- a different
    step in the same file -- carries its own "Generated scenario (Business Case Offer
    accepted)" block. The guard would have certified that the gate branches on the
    strength of prose 90 lines above it. Scope to the enclosing ``## `` section so the
    branch has to be where the instruction is.
    """
    hits = []
    for md in sorted(SKILLS.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for m in re.finditer(r"(?i)with\s+BOTH\s+versions\s+visible", flat(text)):
            # locate the instruction in the unflattened text, then its enclosing section
            probe = re.search(r"(?i)with\s+BOTH\s+versions\s+visible", text)
            if probe is None:
                continue
            starts = [h.start() for h in re.finditer(r"(?m)^## ", text) if h.start() <= probe.start()]
            start = starts[-1] if starts else 0
            nxt = re.search(r"(?m)^## ", text[start + 1:])
            end = start + 1 + nxt.start() if nxt else len(text)
            hits.append((md, text[start:end]))
            break
    return hits


def step_15():
    text = GATE.read_text(encoding="utf-8")
    start = text.find("## 15. Get confirmation")
    assert start != -1, "Step 15 was not found -- has it been renamed?"
    nxt = text.find("\n## 16.", start)
    return text[start: nxt if nxt != -1 else len(text)]


class EveryBothVersionsGateBranchesForTheGeneratedPath(unittest.TestCase):
    """The scan-derived site set, each site checked for the branch."""

    def test_the_scan_finds_the_known_gate(self):
        """A scan that matches nothing would make every other test vacuously pass."""
        found = [md for md, _ in gates_demanding_both_versions()]
        self.assertIn(
            GATE, found,
            "The both-versions scan no longer matches Module 1's Step 15. Either the "
            "instruction was reworded -- in which case update this matcher -- or the gate "
            "was removed. A scan matching nothing turns this whole guard into a no-op.",
        )

    def test_each_such_gate_names_the_generated_scenario_path(self):
        for md, section in gates_demanding_both_versions():
            with self.subTest(file=md.relative_to(REPO)):
                self.assertRegex(
                    flat(section),
                    r"(?i)generated scenario \(business case offer accepted\)",
                    f"{md.relative_to(REPO)} instructs a gate to present BOTH versions but "
                    "that gate's own section carries no generated-scenario branch. On that "
                    "path Step 11 strips every quote line, so the instruction cannot be "
                    "followed as written. A branch elsewhere in the file does not count -- "
                    "the guide reads the step it is on.",
                )


class TheGeneratedBranchIsFollowable(unittest.TestCase):
    def setUp(self):
        self.section = step_15()
        self.flat = flat(self.section)

    def test_step_15_branches_by_path(self):
        self.assertRegex(
            self.flat, r"(?i)###\s*15a\.",
            "Step 15 must branch the way Steps 9 and 11 already do, so the both-versions "
            "rule is scoped to the path that has both versions.",
        )
        self.assertRegex(
            self.flat, r"(?i)###\s*15b\.",
            "Step 15 must carry a generated-scenario branch.",
        )

    def test_zero_quote_lines_is_stated_as_correct(self):
        """Without this, the likely repair is to invent the quotes Step 11 forbids.

        ⚠️ Asserts the INSTRUCTION -- that zero is the *expected result* -- rather than
        matching the word "zero", which the neighboring Step 11 prose also carries.
        """
        self.assertRegex(
            self.flat,
            r"(?i)zero\b[^.]{0,60}(is the expected result|expected result)",
            "The generated branch must say outright that a document with no quote lines is "
            "the EXPECTED result on this path. Naming it as merely permitted still reads as "
            "a defect to repair, and the cheapest repair is a manufactured quote.",
        )

    def test_manufacturing_quotes_is_forbidden_in_the_branch(self):
        self.assertRegex(
            self.flat, r"(?i)never\s+manufacture\s+one",
            "The generated branch must forbid manufacturing a quote to satisfy the gate. "
            "INV-275: an invented 'verbatim' line is worse than none, because it looks like "
            "evidence of something the Bootcamper never said.",
        )

    def test_the_branch_names_a_concrete_comparison_target(self):
        """A branch that only excuses the missing quotes drops the gate's actual question.

        ⚠️ Both targets are asserted separately. The Step 6a summary is the only point on
        this path where the Bootcamper approved the scenario's CONTENT, and the persisted
        answer is the only one whose drift is mechanically checkable (INV-097/INV-275).
        """
        self.assertRegex(
            self.flat, r"(?i)step 6a summary",
            "The generated branch must name the Step 6a summary as what the document is "
            "checked against -- otherwise the gate asks 'does this sound right?', which is "
            "the failure INV-275 exists to prevent, reached by a different route.",
        )
        self.assertRegex(
            self.flat, r"integration_targets",
            "The branch must name the persisted answer as the second comparison target. It "
            "is the one field on this path whose drift can be checked against a file rather "
            "than against memory of the conversation.",
        )

    def test_the_derived_fields_are_called_out_by_name(self):
        """The bare-reply fields are where the narrowing risk actually lives."""
        for field in ("6b", "6d", "Module 7"):
            self.assertIn(
                field, self.section,
                "The branch must point at the fields derived from bare option replies and at "
                "the module that consumes them. 'Check it against what was agreed' without "
                "naming where drift is likely is advice, not an instruction.",
            )


class TheBootcamperDescribedPathAndThePinnedQuestionAreUntouched(unittest.TestCase):
    """The spec's fifth and fourth criteria: change the framing, nothing else."""

    def setUp(self):
        self.section = step_15()

    def test_the_pinned_question_is_verbatim_and_appears_once(self):
        self.assertEqual(
            self.section.count(PINNED), 1,
            "Step 15's question is pinned verbatim (INV-056) and must appear exactly once. "
            "Branching the framing above it must not duplicate it into each branch -- two "
            "copies is how a pinned question drifts, since only one of them gets edited.",
        )

    def test_the_both_versions_rule_survives_on_the_described_path(self):
        self.assertRegex(
            flat(self.section),
            r"(?i)present the document with BOTH versions visible",
            "Scoping the rule to 15a must not weaken it. The Bootcamper-described path is "
            "where the 2026-08-25 substituted adjective got through, and that rule is the "
            "only thing standing in front of it there.",
        )


if __name__ == "__main__":
    unittest.main()
