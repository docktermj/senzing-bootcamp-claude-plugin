"""Module 0's suggested `search_docs` queries are measured artifacts, not composed phrases.

``concepts.md`` ships six suggested queries and vouches for them as a set: *"these are phrased
the way the indexed documentation is"*. Two of the six were not, and both were found only by
**running** them against the live index on 2026-09-01 (server 1.35.3, docs index 2026-09-01
11:58 UTC):

    "entity resolution ambiguous match possible match"
        -> 3/3 Entity-Centric-Learning chunks; no ambiguous-match material at all
    "entity resolution pipeline standardization blocking scoring clustering"
        -> rank 1 a customer case study, rank 2 the MCP server's own page; no pipeline material

⚠️ Neither was findable by reading. Both are well-formed, on-topic, and use the right technical
vocabulary — which is the whole problem: under BM25 a composed phrase loses to chunks with a
denser concentration of its common terms, and a query that misses is indistinguishable from
documentation that does not cover the topic. `concepts.md` warns about exactly that two
paragraphs above the list, and then shipped two instances of it.

⛔ **This guard is offline (INV-108), so it asserts the SHIPPED TEXT, never the live ranking.**
It cannot tell you a query still works; it can only tell you that the two known-bad phrasings
have not come back and that the list still claims a measurement with a date attached. Re-running
the six against the server is `/dry-run` phase 1's job, and the dated note is what tells that
run whether the claim is stale.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONCEPTS = (REPO / "plugins" / "senzing-bootcamp" / "skills" /
            "module-00-entity-resolution-concepts" / "concepts.md")

#: The phrasings measured as NOT reaching their material. Fixtures, so a regression is named.
KNOWN_BAD = (
    "entity resolution ambiguous match possible match",
    "entity resolution pipeline standardization blocking scoring clustering",
)


def text():
    return CONCEPTS.read_text(encoding="utf-8")


def suggested_queries():
    """The quoted entries in the suggested-query list, in order.

    ⚠️ Terminated by the first line that is not a quoted entry, NOT by the measurement note's
    wording. Anchoring the end on the note made the whole class ERROR when a control deleted
    the note — so a mutation that removes the note took down the list assertions too, which
    say nothing about the note and should still have passed. A parser that depends on the
    thing under test cannot report cleanly on it.
    """
    body = text()
    start = body.index("Suggested queries:")
    out = []
    for line in body[start:].split("\n")[1:]:
        m = re.match(r'^- "([^"]+)"\s*$', line)
        if m:
            out.append(m.group(1))
        elif out:
            break
    return out


class TheKnownBadPhrasingsAreGone(unittest.TestCase):
    def test_neither_measured_miss_is_still_shipped(self):
        listed = suggested_queries()
        for bad in KNOWN_BAD:
            with self.subTest(query=bad):
                self.assertNotIn(
                    bad, listed,
                    "A query measured as NOT reaching its material is back in the suggested "
                    "list. It reads correctly and returns the wrong documents; that is why it "
                    "is pinned here by its exact text rather than left to review.",
                )

    def test_the_list_still_has_six_entries(self):
        self.assertEqual(
            6, len(suggested_queries()),
            "The suggested-query list should carry six entries. This fix replaced two of them "
            "and removed none — if the count moved, the list and the note that describes it "
            "have diverged. Found: %r" % (suggested_queries(),),
        )

    def test_the_ambiguous_match_topic_is_still_covered(self):
        """Replacing the phrasing must not drop the topic — the entry belongs in the list."""
        self.assertIn(
            "ambiguous matches invisible false positives", suggested_queries(),
            "The ambiguous-match topic must still have an entry. The defect was the phrasing, "
            "not the topic; deleting it would leave Module 0's follow-up gates with no route "
            "to the material at all.",
        )

    def test_the_pipeline_topic_is_still_covered(self):
        self.assertIn(
            "How does entity resolution work steps process", suggested_queries(),
            "The pipeline topic must still have an entry that reaches the numbered stages.",
        )


class TheListDeclaresItselfMeasured(unittest.TestCase):
    def setUp(self):
        self.flat = re.sub(r"\s+", " ", text())

    def test_the_note_says_the_entries_were_run(self):
        self.assertRegex(
            self.flat, r"(?i)All six were MEASURED",
            "The list must state that its entries were measured, so the next editor treats it "
            "as a verified artifact rather than a set of plausible phrases to extend by feel.",
        )

    def test_the_note_carries_a_server_version_and_index_date(self):
        """A measurement claim with no date cannot be re-checked when the index moves."""
        self.assertRegex(
            self.flat, r"MCP server 1\.35\.\d",
            "The measurement must name the server version it was taken against (INV-080).",
        )
        self.assertRegex(
            self.flat, r"docs index 20\d\d-\d\d-\d\d",
            "The measurement must name the docs index date — BM25 ranking is a property of the "
            "index, so the index date is what actually dates this claim.",
        )

    def test_it_tells_the_next_editor_to_run_a_new_entry(self):
        self.assertRegex(
            self.flat, r"(?i)if you change an entry here, \*\*run it first\*\*",
            "The note must instruct running a new entry before shipping it. Both defects were "
            "introduced by composing a phrase that reads correctly, so 'review it' is exactly "
            "the check that already failed twice.",
        )

    def test_both_misses_are_recorded_with_what_they_returned(self):
        """A replaced query with no record of why invites the next editor to restore it."""
        self.assertRegex(
            self.flat, r"(?i)Entity-Centric-Learning chunks",
            "The note must record what the ambiguous-match query actually returned.",
        )
        self.assertRegex(
            self.flat, r"(?i)rank 1 was a customer case study",
            "The note must record what the pipeline query actually returned.",
        )


class TheExistingCrossReferencesStillResolve(unittest.TestCase):
    """The spec's third criterion: do not silently re-route material already routed correctly."""

    def test_the_failure_modes_bullet_points_at_a_query_still_in_the_list(self):
        body = text()
        self.assertRegex(
            re.sub(r"\s+", " ", body), r"Reached by the false-positives query above",
            "The failure-modes bullet's cross-reference must survive — it is the path a guide "
            "teaching the primer top-to-bottom actually takes to this material.",
        )
        self.assertIn(
            "entity resolution false positives false negatives accuracy", suggested_queries(),
            "The failure-modes bullet cites 'the false-positives query above'; if that entry "
            "left the list the cross-reference would dangle, which is the drift this asserts "
            "against.",
        )

    def test_the_lists_own_vouching_sentence_survives(self):
        self.assertRegex(
            re.sub(r"\s+", " ", text()),
            r"(?i)phrased the way the indexed documentation is",
            "The file's stated criterion for the list is what makes a mis-phrased entry a "
            "defect rather than a preference. It must survive the fix that enforces it.",
        )


if __name__ == "__main__":
    unittest.main()
