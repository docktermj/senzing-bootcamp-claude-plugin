"""Module 7's quality gate routes to the tool that owns the material, and shows its evidence.

Two defects in Step 3b, found on 2026-08-12 against server 1.32.9.

**The supplementary lookup returned the wrong kind of "evaluation".** The step called
`reporting_guide(topic='quality', …)` — correct — and then
`search_docs(query='entity resolution quality evaluation')` "for additional context on
interpreting results". That query returns the *Entity Resolution Buyer's Guide* → "The Steps
To Evaluating Entity Resolution": a nine-step guide to evaluating an ER **vendor** (deployment
method, cloud vs on-prem, total cost of ownership, side-by-side comparison). BM25 matched
"evaluation" in the procurement sense. Meanwhile `reporting_guide(topic='evaluation')` — one
call the step never made — carries the 4-Point ER Evaluation Framework, the MATCH_LEVEL_CODE
reference, and the evidence rule below.

**The step's own "Acceptable" script was the server's canonical example of a bad assessment.**
`reporting_guide(topic='evaluation')` carries an Evidence Requirement section, described as its
hallucination-prevention mechanism, whose **Bad** example is "The resolution quality looks good
with reasonable compression rates." Step 3b prescribed, verbatim: *"Your entity resolution
quality looks good. Let's proceed to visualizations."* — reached from a table of three
aggregate indicators, and it is the branch that ends the quality gate and proceeds. Of the
three branches only Marginal showed the Bootcamper any records.

Both `reporting_guide` topics warn about exactly this, and the step already fetched one of
them: `quality` says "Aggregate stats (entity count, compression ratio) hide errors";
`evaluation` says "Never assess ER quality from aggregate statistics alone."

What is guarded here is the routing and the evidence requirement. Whether a *running* guide
actually shows records is not offline-checkable — but an instruction that never asks for them
guarantees it will not.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE1 = (
    REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
    / "module-07-query-visualize-discover" / "phase1-query-visualize.md"
)


def step_3b():
    """Step 3b only — the quality gate, bounded by its neighboring headings."""
    text = PHASE1.read_text(encoding="utf-8")
    start = text.index("### 3b. Quality evaluation")
    nxt = re.search(r"(?m)^#{2,4} (?!3b\.)", text[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(text)
    section = text[start:end]
    section = re.sub(r"(?m)^\s*>\s?", "", section)
    return re.sub(r"\s+", " ", section)


class TheGateIsFound(unittest.TestCase):
    def test_step_3b_parses(self):
        section = step_3b()
        self.assertIn("Quality evaluation", section)
        self.assertIn("Possible matches", section, "the indicator table should be inside 3b")


class QualityContextComesFromTheOwningTool(unittest.TestCase):
    def test_it_calls_both_reporting_guide_topics(self):
        section = step_3b()
        self.assertIn("reporting_guide(topic='quality'", section)
        self.assertIn("reporting_guide(topic='evaluation'", section)

    def test_it_does_not_prescribe_a_documentation_search_for_quality_context(self):
        """The defect: a composed query returning procurement guidance.

        The step has to NAME the query in order to forbid it — the ⛔ explaining why it
        returns vendor-selection material quotes it verbatim. So this checks that every
        occurrence sits inside a prohibition, not that the string is absent; the absent-string
        form failed against correct shipped text.
        """
        section = step_3b()
        needle = "search_docs(query='entity resolution quality evaluation'"
        prohibition = re.compile(r"(?i)do not reach for|used to add|must not|never")
        for match in re.finditer(re.escape(needle), section):
            context = section[max(0, match.start() - 220):match.start()]
            self.assertTrue(
                prohibition.search(context),
                "Step 3b prescribes a documentation search for quality interpretation; "
                "reporting_guide owns that material. Context: %r" % context[-160:],
            )

    def test_the_misroute_is_explained_so_it_is_not_reinstated(self):
        section = step_3b()
        self.assertRegex(section, r"(?i)Buyer's Guide")
        self.assertRegex(section, r"(?i)vendor")
        self.assertIn("1.32.9", section)

    def test_it_carries_a_requery_rule(self):
        section = step_3b()
        self.assertRegex(section, r"(?i)re-query")
        self.assertRegex(section, r"(?i)concepts\.md")


class EveryVerdictRequiresEvidence(unittest.TestCase):
    def test_the_evidence_requirement_is_relayed_with_provenance(self):
        section = step_3b()
        self.assertRegex(section, r"(?i)Every evaluation finding MUST be supported by specific evidence")
        self.assertRegex(section, r"(?i)hallucination-prevention")
        self.assertIn("2026-08-12", section)

    def test_the_retired_bare_verdict_is_gone(self):
        """The exact line that matched the server's 'Bad' example."""
        self.assertNotIn(
            'Your entity resolution quality looks good. Let\'s proceed to visualizations."',
            PHASE1.read_text(encoding="utf-8"),
        )

    def test_sampling_is_required_before_any_verdict(self):
        section = step_3b()
        self.assertRegex(section, r"(?i)Before stating any of the three verdicts, sample and show")
        self.assertRegex(section, r"(?i)why_entities")

    def test_the_requirement_names_the_acceptable_branch_explicitly(self):
        """Acceptable is the branch that proceeds, and the one least likely to be questioned."""
        section = step_3b()
        self.assertRegex(section, r"(?i)including the one that proceeds")

    def test_the_acceptable_branch_asks_for_entity_ids_and_match_keys(self):
        section = step_3b()
        acceptable = section[section.index("**Acceptable:**"):section.index("**Marginal:**")]
        self.assertRegex(acceptable, r"(?i)entities \[IDs\]")
        self.assertRegex(acceptable, r"(?i)match keys")

    def test_the_aggregate_statistics_anti_pattern_is_relayed(self):
        section = step_3b()
        self.assertRegex(section, r"(?i)Never assess ER quality from aggregate statistics alone")
        self.assertRegex(section, r"(?i)Aggregate stats .{0,40} hide errors")


class TheThresholdsAreUntouched(unittest.TestCase):
    """This spec changes what the guide must show, not where the bands sit."""

    def test_the_three_bands_keep_their_numbers(self):
        section = step_3b()
        self.assertRegex(section, r"possible matches < 5%")
        self.assertRegex(section, r"possible matches 5–15%")
        self.assertRegex(section, r"possible matches > 15%")

    def test_the_indicator_table_survives(self):
        section = step_3b()
        for indicator in ("Entity-to-record ratio", "Possible matches", "Cross-source match rate"):
            self.assertIn(indicator, section)


if __name__ == "__main__":
    unittest.main()
