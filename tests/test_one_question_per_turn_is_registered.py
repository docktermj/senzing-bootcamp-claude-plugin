"""The one-👉-per-turn rule is registered, and nothing cites the wrong invariant for it.

For the plugin's whole history until 2026-08-15 the rule `ground-rules.md` calls **"the #1
bootcamper complaint"** was stated in 13 shipped places, enforced with zero-tolerance
framing, checked at runtime by `auto-test`'s transcript linter — and registered in no
invariant. Six sites cited an authority and every one was wrong:

* **INV-005** is the 👉 *marker* rule in full — *"Each question to the Bootcamper is preceded
  by 👉."* A turn ending on three 👉-prefixed questions satisfies it completely.
* **INV-008** governs ambiguity ("not ambiguous with respect to a Yes or No answer").
* **INV-009** governs complexity ("not 'complex'. The use of 'or' is discouraged").

All 249 invariant entries were parsed and searched: four mentioned a per-turn count and all
four were **scoped** — INV-063 (model/effort switch), INV-064 (accepted-switch continuation),
INV-135 (licence-request flow), INV-225 (an observation). None stated the general rule.
(`specs/the-one-question-per-turn-rule-is-registered-nowhere.md`)

Enforces **INV-251**. Its companion is **INV-225**, which forbids the *zero* case; the two
together fix the count at exactly one, and INV-251 deliberately does not restate INV-225's
clause — duplicating a clause across two IDs is how they drift apart.

⛔ **WHAT THIS GUARD CANNOT SEE.** Whether a guide actually ends a turn on one question is a
live-turn property. Reading files cannot establish it, and an offline suite (INV-108) never
will. The only mechanism that checks the **behaviour** is
`.claude/skills/auto-test/transcript_lint.py`, against real transcripts, and `dry-run` phase 3
is where a live turn is judged. A clean run here means the rule is *registered and correctly
cited* — never that it is obeyed.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"
LINTER = REPO_ROOT / ".claude" / "skills" / "auto-test" / "transcript_lint.py"

#: Invariants that are ABOUT questions but do not govern the count. Citing one of these on a
#: line that states the count is the defect this guard exists for.
NOT_THE_COUNT = ("INV-005", "INV-008", "INV-009")

#: A line stating the per-turn count rule, in any of the phrasings the corpus actually uses.
#: ⚠️ Derived deliberately broad: the first sweep for this defect required "per turn" near
#: "one" and MISSED three files, which is how the finding's own site list was undercounted.
COUNT_RULE = re.compile(
    r"(?i)(exactly one \U0001F449|one \U0001F449 question per turn|one question per turn|"
    r"turn carries exactly one|ends? (?:the|each) (?:yielding )?turn on (?:exactly )?one|"
    r"two or more \U0001F449|ends the turn on two \U0001F449|end the turn on two \U0001F449)")


def squash(text):
    return re.sub(r"\s+", " ", text)


def shipped_markdown():
    """Every shipped Markdown file, discovered rather than listed (INV-246)."""
    return sorted(PLUGIN.rglob("*.md"))


def count_rule_lines():
    """Every shipped line stating the count rule, DERIVED not listed (INV-246)."""
    hits = []
    for path in shipped_markdown():
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if COUNT_RULE.search(line):
                hits.append((path, i, line))
    return hits


class TheInvariantIsRegistered(unittest.TestCase):
    def setUp(self):
        self.text = INVARIANTS.read_text(encoding="utf-8")

    def test_inv251_states_the_two_or_more_prohibition(self):
        self.assertRegex(
            squash(self.text),
            r"\*\*INV-251\*\* — A turn presented to the Bootcamper MUST NOT contain "
            r"\*\*two or more\*\* 👉 questions",
            "INV-251 no longer states the prohibition that was registered nowhere until "
            "2026-08-15")

    def test_inv251_is_in_the_index(self):
        """INVARIANTS.md rule 3: the index entry ships in the same edit as the invariant."""
        start = self.text.index("### Index by subject")
        end = self.text.index("<!-- New invariants", start)
        index = self.text[start:end]
        self.assertGreater(len(index), 500,
                           "the index slice collapsed; this assertion would pass vacuously")
        self.assertIn("INV-251", index,
                      "INV-251 is defined but missing from the subject index (rule 3)")

    def test_inv251_defers_the_zero_case_to_inv225(self):
        """The two must not both state the zero clause, or they can drift apart."""
        #: Sliced to the INV-251 ENTRY rather than distance-matched across the whole file:
        #: a bounded `.{0,3000}` regex over a 250-entry document is a coin toss about
        #: formatting, not an assertion about INV-251.
        entry = self.text[self.text.index("**INV-251**"):]
        entry = entry[:entry.index("(Source:") + 60]
        self.assertIn(
            "The zero case is INV-225", entry,
            "INV-251 no longer points at INV-225 for the zero case, so a reader cannot tell "
            "the two rules compose into 'exactly one'")


class NoSiteCitesTheWrongInvariantForTheCount(unittest.TestCase):
    """The wrong-citation half, swept across shipped Markdown rather than a path list."""

    def test_the_corpus_is_actually_scanned(self):
        self.assertGreater(len(shipped_markdown()), 20,
                           "the shipped-Markdown scan collapsed; assertions below would "
                           "pass vacuously")

    def test_the_rule_is_stated_somewhere(self):
        """Non-vacuity: if the phrasings changed, the sweep below would silently pass."""
        self.assertGreaterEqual(
            len(count_rule_lines()), 8,
            "the count rule is stated in far fewer places than expected — either the corpus "
            "changed or COUNT_RULE no longer matches how it is phrased")

    def test_no_count_line_cites_a_question_invariant_that_is_not_the_count(self):
        offenders = []
        for path, i, line in count_rule_lines():
            cited = set(re.findall(r"INV-\d{3}", line))
            wrong = cited & set(NOT_THE_COUNT)
            # A line may legitimately name them while SAYING they are not the count.
            if wrong and "not the count" not in line and "marker" not in line.lower():
                offenders.append("%s:%d cites %s" % (path.relative_to(REPO_ROOT), i,
                                                     ",".join(sorted(wrong))))
        self.assertEqual(
            [], offenders,
            "INV-005 is the 👉 marker rule, INV-008 governs ambiguity and INV-009 "
            "complexity — none states the per-turn count, which is INV-251:\n  "
            + "\n  ".join(offenders))

    def test_the_canonical_statement_carries_the_id(self):
        """ground-rules.md's own 'One question per turn' bullet is where a reader looks first."""
        gr = (PLUGIN / "skills" / "bootcamp-onboarding" / "ground-rules.md").read_text(
            encoding="utf-8")
        self.assertRegex(
            squash(gr), r"\*\*One question per turn \(INV-251\)\.\*\*",
            "the canonical statement of the rule ships without its invariant ID, so a later "
            "editor cannot look it up (INV-183)")


class TheRuntimeCheckIsLabelledCorrectly(unittest.TestCase):
    """`auto-test`'s linter is the only thing that checks the BEHAVIOUR; its label must be right.

    Its finding code is what a maintainer reads in an auto-test report. While it was
    ``INV-005-multi-question`` every caught breach pointed at a one-line marker rule.
    """

    def setUp(self):
        self.text = LINTER.read_text(encoding="utf-8")

    def test_the_linter_exists(self):
        self.assertTrue(LINTER.is_file(),
                        "the transcript linter moved; this guard's premise is stale")

    def test_the_finding_code_names_the_right_invariant(self):
        self.assertIn('"INV-251-multi-question"', self.text,
                      "the multi-question finding code no longer names INV-251")
        self.assertNotIn('"INV-005-multi-question"', self.text,
                         "the finding code still names INV-005, so every auto-test report "
                         "points the maintainer at the 👉 marker rule instead of the count")

    def test_the_counting_logic_is_unchanged(self):
        """The check was always correct — only its label was wrong. Guard against a 'fix'
        that rewrites the logic while relabelling it."""
        self.assertRegex(
            squash(self.text), r"count = text\.count\(POINTER\).{0,80}if count > 1",
            "the per-turn counting logic changed; the 2026-08-15 correction was a RELABEL "
            "and must not have altered what the check counts")


if __name__ == "__main__":
    unittest.main()
