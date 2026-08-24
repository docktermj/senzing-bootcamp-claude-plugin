"""The primer's teaching section must not carry an exemption-shaped label.

`module-00-entity-resolution-concepts/concepts.md` headed its core teaching material **"What to
teach (generic concept, plain language)"** and listed under it: what entity resolution is, the
two failure modes, the five-stage conceptual pipeline (ingestion/standardization -> candidate
selection -> comparison/scoring -> classification -> clustering), disclosed vs discovered
relationships, and the three outputs. Only the subsection beneath it -- "How Senzing handles it"
-- was marked "(pull specifics from MCP)".

`bootcamp-onboarding/ground-rules.md`'s MCP-first pre-response checklist requires an MCP call
**on that turn** for a reply containing entity-resolution technical details. Blocking, scoring,
classification and clustering are entity-resolution technical details. So two readings of the
same paragraph disagreed: the heading licensed the pipeline as generic prose, the checklist
required it be sourced.

⛔ **The two labels sit on different axes.** "Generic" is a real distinction for **attribution**
-- the material is not proprietary to Senzing -- and not the distinction the checklist draws,
which is about whether a claim is an entity-resolution technical detail. One label, two axes.

The failure it invited is quiet: a guide taking "generic" at face value presents the pipeline
from training data, and it will usually be roughly right, which is exactly why nobody notices
when it is not.

Nothing is lost by requiring the call -- the material is fully retrievable. Verified on **server
1.33.0, docs index 2026-08-20 17:33 UTC, 2026-08-23**:
``search_docs('entity resolution pipeline standardization blocking scoring clustering')`` reaches
*"What Is Entity Resolution? How It Works & Why It Matters."* -> "How Does Entity Resolution
Work?", whose five numbered steps match the file's list almost word for word, and
``search_docs('entity resolution false positives false negatives accuracy')`` reaches that same
document's "What Are Ambiguous Matches and Invisible False Positives?". ⚠️ For **both** queries
the on-topic section is not the top hit -- marketing pages outrank it -- which the file now says,
because "read the first row" is how a correct query still produces the wrong material.

⛔ **This checks the file's wording, not what a live turn actually does.** Whether the guide makes
the call is a conversational outcome and belongs to `dry-run` phase 3 (INV-005 and the MCP-first
rule are conversational invariants). A clean run here means the instruction no longer licenses
skipping it.

Source spec: `specs/generic-concept-label-collides-with-the-mcp-first-checklist.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONCEPTS = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" /
            "module-00-entity-resolution-concepts" / "concepts.md")

#: The teaching section's heading, located by its stable half so a retitle is still found.
TEACHING_HEADING = re.compile(r"^## What to teach\b.*$", re.M)

#: The suggested-query list: bullets of quoted queries under the hard-rule section.
SUGGESTED_QUERY = re.compile(r'^- "([^"]+)"$', re.M)

#: Words that, standing alone in the heading, say "this material is not Senzing's" -- and are
#: read as "this material needs no MCP call". `generic` is the one that shipped.
EXEMPTION_SHAPED = ("generic", "general knowledge", "common knowledge", "background",
                    "no mcp", "without mcp", "from memory")

#: The two queries the section's own material depends on. Asserted as *content*, not as exact
#: strings, so rephrasing a query for better retrieval does not fail this guard.
PIPELINE_TERMS = ("pipeline", "blocking", "clustering")
FAILURE_MODE_TERMS = ("false positive", "false negative")


def text():
    return CONCEPTS.read_text(encoding="utf-8")


def teaching_section():
    """The teaching section's body, heading to the next `## ` heading."""
    body = text()
    match = TEACHING_HEADING.search(body)
    assert match, "the teaching heading was not found"
    start = match.start()
    following = re.search(r"^## ", body[match.end():], re.M)
    end = match.end() + (following.start() if following else len(body))
    return body[start:end]


def suggested_queries():
    """Only the quoted-query bullets, which live above the teaching section."""
    body = text()
    head = body[:TEACHING_HEADING.search(body).start()]
    return SUGGESTED_QUERY.findall(head)


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_teaching_heading_is_found(self):
        self.assertIsNotNone(
            TEACHING_HEADING.search(text()),
            "no '## What to teach' heading in concepts.md — this guard is inspecting nothing")

    def test_the_teaching_section_still_has_content(self):
        self.assertGreater(
            len(teaching_section().splitlines()), 5,
            "the teaching section is nearly empty; either it moved or the primer lost its "
            "core material")

    def test_the_suggested_query_list_is_found(self):
        self.assertGreater(
            len(suggested_queries()), 3,
            "fewer than four suggested queries found (%r); the list this guard checks against "
            "is not being read" % suggested_queries())


class TheHeadingClaimsNoExemption(unittest.TestCase):
    def test_the_heading_carries_no_unqualified_exemption_shaped_word(self):
        heading = TEACHING_HEADING.search(text()).group(0).lower()
        for word in EXEMPTION_SHAPED:
            with self.subTest(word=word):
                self.assertNotIn(
                    word, heading,
                    "the teaching heading says %r, which reads as licensing this material to "
                    "be presented without an MCP call. It is an attribution word, not a "
                    "sourcing word, and the pre-response checklist draws the other axis: %r"
                    % (word, heading))

    def test_the_heading_says_the_material_is_still_mcp_sourced(self):
        heading = TEACHING_HEADING.search(text()).group(0)
        self.assertRegex(
            heading, r"(?i)MCP",
            "the heading no longer says the material is MCP-sourced. Removing the misleading "
            "word is only half the fix — the heading is where a reader decides whether to "
            "call, so it has to answer that")


class TheSectionStatesWhichAxisTheLabelIsOn(unittest.TestCase):
    def setUp(self):
        self.flat = re.sub(r"\s+", " ", teaching_section())

    def test_it_says_the_label_is_not_an_exemption(self):
        self.assertRegex(
            self.flat, r"(?i)never an exemption from the pre-response checklist",
            "the section does not state that its label is not an exemption from the checklist "
            "— the sentence that removes the collision")

    def test_the_rule_cites_the_invariant_that_governs_it(self):
        """INV-183: a rule binding a step must be lookup-able AT that step.

        `conformance.py rules` counts a hard rule whose section cites no invariant, and this
        section's stop sign was exactly that when it was first written.
        """
        self.assertRegex(
            self.flat, r"never an exemption from\s+the pre-response checklist \(INV-\d{3}\)",
            "the section's stop sign cites no invariant at the rule, so a later editor cannot "
            "look up why the label may not read as an exemption")
        self.assertIn(
            "INV-212", self.flat,
            "the section does not cite INV-212 beside its queries — the invariant requiring "
            "the retrieval strategy to travel with the requirement")

    def test_it_names_both_axes(self):
        for axis in ("attribution", "sourcing"):
            with self.subTest(axis=axis):
                self.assertIn(
                    axis, self.flat.lower(),
                    "the section does not name the %s axis, so a reader cannot see that two "
                    "different distinctions were sharing one label" % axis)

    def test_it_names_the_technical_details_that_trigger_the_rule(self):
        for term in ("blocking", "scoring", "clustering"):
            with self.subTest(term=term):
                self.assertIn(
                    term, self.flat.lower(),
                    "the section does not name %r as material the checklist covers, leaving "
                    "the reader to decide which of its bullets count" % term)


class TheQueriesForThisSectionsMaterialAreSuggested(unittest.TestCase):
    """Criterion 2 — and the point of INV-212: the requirement travels with its route."""

    def setUp(self):
        self.queries = [q.lower() for q in suggested_queries()]

    def test_a_pipeline_query_is_suggested(self):
        matching = [q for q in self.queries
                    if all(term in q for term in PIPELINE_TERMS)]
        self.assertTrue(
            matching,
            "no suggested query covers the pipeline stages the teaching section requires "
            "(looking for %r together). The requirement would then arrive without its route"
            % (PIPELINE_TERMS,))

    def test_a_failure_modes_query_is_suggested(self):
        matching = [q for q in self.queries
                    if all(term in q for term in FAILURE_MODE_TERMS)]
        self.assertTrue(
            matching,
            "no suggested query covers the two failure modes (looking for %r together)"
            % (FAILURE_MODE_TERMS,))

    def test_the_section_warns_that_the_on_topic_hit_is_not_first(self):
        self.assertRegex(
            re.sub(r"\s+", " ", teaching_section()),
            r"(?i)not\*{0,2} the top hit|outrank",
            "the section does not warn that these queries return the on-topic document below "
            "marketing pages — presenting the first row is how a correct query still yields "
            "the wrong material")


if __name__ == "__main__":
    unittest.main()
