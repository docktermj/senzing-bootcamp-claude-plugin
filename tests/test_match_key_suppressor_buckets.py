"""Tests that the match-key audit separates per-record from relationship suppressors.

The audit reads match keys from **two** response paths and used to prescribe **one** axis of
separation (single- vs cross-source). A `-FEATURE` means the opposite thing in each:

* on `RESOLVED_ENTITY.RECORDS[].MATCH_KEY` the records merged **despite** the feature
  disagreeing — an over-merge signal, and the mapping concern the audit exists to surface;
* on `RELATED_ENTITIES[].MATCH_KEY` Senzing **declined to merge** those entities *because* it
  disagreed — the engine exercising restraint, which on ambiguous data is the correct outcome.

Pooled into one share, a large number is neither. Observed live on 2026-09-02 (SDK 4.4.0,
build 4.4.0.26242, 10,000 records / 3 sources): pooled `-DOB 1,758 = 19.5%`; split, **zero**
per-record and **57.4%** of relationships. On the pooled figure the iterate-vs-proceed gate took
its `UAT <80%` branch and recommended returning to Data Quality, Mapping, and Transformation —
while a ten-entity spot-check of merged entities was 10 of 10 clean. The gate routed on a number
that meant nothing and produced the opposite of the correct recommendation, in the direction that
costs the Bootcamper work.

The server draws the same line, via
`get_sdk_reference(topic='response_schemas', filter='get_entity_by_entity_id', language='java')`
on server **1.36.0**, 2026-09-02: `RELATED_ENTITIES[]` is documented as *"Entities related to but
not resolved into this one"*, `RESOLVED_ENTITY.RECORDS[].MATCH_KEY` as *"Features that matched:
+ means contributed, - means detracted"*, and `RELATED_ENTITIES[].MATCH_KEY` only as *"Features
that matched/did not match"*.

⛔ **The site set is SCANNED, not hardcoded (INV-246).** The originating spec named one skill file;
the sweep found a second that quoted the changed heading verbatim. A test pinning the paths its
author already knew about is blind to exactly the site that matters, so every cross-reference to
the audit's step-4 rule is discovered by scanning the shipped tree.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")
PHASE_D = os.path.join(
    PLUGIN, "skills", "module-06-data-processing", "phaseD-validation.md"
)

# The step-4 heading as it now reads. Any shipped file quoting the OLD heading is a dangling
# citation, which is what the sweep caught.
STEP_4_HEADING = "Report a high-share suppressor as a FINDING, never a pass/fail"
RETIRED_HEADING = "Report a high-share cross-source suppressor as a FINDING"


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def shipped_markdown():
    """Every shipped .md — the scan that replaces a hardcoded site list (INV-246)."""
    out = []
    for root, _dirs, files in os.walk(PLUGIN):
        if "__pycache__" in root:
            continue
        for name in files:
            if name.endswith(".md"):
                out.append(os.path.join(root, name))
    return sorted(out)


class TheAuditSeparatesTheTwoReads(unittest.TestCase):
    def setUp(self):
        self.text = read(PHASE_D)

    def test_it_names_three_buckets(self):
        for bucket in (
            "single-source per-record",
            "cross-source per-record",
            "relationship",
        ):
            self.assertIn(
                bucket,
                self.text,
                "the audit must tabulate %r as its own bucket — pooling the per-record and "
                "relationship reads yields a share that means neither" % bucket,
            )

    def test_each_bucket_states_what_a_suppressor_there_means(self):
        """Merged-despite vs declined-because, at the point of output."""
        self.assertRegex(
            self.text,
            r"(?s)merged \*\*despite\*\*.{0,400}declined to merge\*\* these entities \*\*because\*\*",
            "each bucket must say whether the feature disagreed on records that MERGED or on "
            "entities that were NOT merged; the share alone cannot distinguish them",
        )

    def test_it_forbids_pooling_and_says_why(self):
        self.assertRegex(
            self.text,
            r"mean OPPOSITE things,\s+so pooling them\s+yields a number that is neither",
            "the ⛔ against pooling must be explicit — this is the defect, not a nuance",
        )

    def test_each_bucket_is_reported_against_its_own_denominator(self):
        self.assertIn(
            "Report each bucket against its own total",
            self.text,
            "mixed denominators are how 57.4%-of-relationships presented as 19.5% of everything",
        )

    def test_the_relationship_bucket_is_deduplicated(self):
        self.assertRegex(
            self.text,
            r"(?s)Deduplicate the relationship bucket.{0,200}min_id, max_id",
            "every relationship appears in both entities' RELATED_ENTITIES, so an "
            "un-deduplicated count double-counts each one and inflates the share",
        )

    def test_the_server_is_cited_for_the_asymmetry(self):
        """The distinction is documented, not inferred — cite it (INV-080)."""
        self.assertIn(
            "not resolved into",
            self.text,
            "RELATED_ENTITIES[] is documented as 'Entities related to but not resolved into "
            "this one'; cite the server rather than asserting the asymmetry",
        )
        self.assertRegex(
            self.text,
            r"server \*\*1\.36\.0\*\*",
            "a Senzing fact written into the plugin carries its server version (INV-080)",
        )


class Step4AsksTheQuestionThatFitsTheBucket(unittest.TestCase):
    def setUp(self):
        self.text = read(PHASE_D)

    def test_the_per_record_question_keeps_its_original_wording(self):
        self.assertIn(
            "genuinely measure the\n     same thing",
            self.text,
            "the measure-the-same-thing question is correct for the per-record bucket and must "
            "survive verbatim",
        )

    def test_the_relationship_bucket_gets_a_different_question(self):
        self.assertRegex(
            self.text,
            r"Do \*\*not\*\* ask the\s+measure-the-same-thing question here",
            "asking it of a relationship suppressor asks what is mis-mapped about the engine "
            "refusing a conflict — nothing is",
        )
        self.assertRegex(
            self.text,
            r"(?s)which feature raised these pairs as\s+candidates",
            "the relationship bucket's useful question is which feature is being treated as "
            "more identifying than it is",
        )


class TheGateRoutesOnThePerRecordBucket(unittest.TestCase):
    def setUp(self):
        self.text = read(PHASE_D)

    def test_it_routes_match_accuracy_on_the_per_record_bucket(self):
        self.assertRegex(
            self.text,
            r"Route match accuracy on the PER-RECORD bucket only",
            "the gate must not route on the pooled figure — that is what produced the wrong "
            "recommendation",
        )

    def test_a_relationship_share_cannot_lower_the_gate_by_itself(self):
        self.assertRegex(
            self.text,
            r"relationship-bucket share,\s*\n?\s*however\s+large, MUST NOT by itself push the "
            r"gate\s+below the ≥90% branch",
            "a high relationship share means the engine declined to merge on a conflict, which "
            "is the outcome the Bootcamper wants",
        )

    def test_the_gate_rule_cites_inv_264(self):
        """INV-183: a rule binding a step must be reachable AT that step."""
        self.assertRegex(
            self.text,
            r"⛔ \*\*\(INV-264\) Route match accuracy on the PER-RECORD bucket only",
            "the gate rule is INV-264 reaching the gate rather than the report, and must carry "
            "the ID so a later editor can look it up",
        )

    def test_the_zero_per_record_high_relationship_case_lands_in_the_strong_branch(self):
        """The fixture case from the acceptance criteria, asserted on the routing text."""
        self.assertRegex(
            self.text,
            r"(?s)zero per-record bucket with a large\s+relationship bucket lands here",
            "the ≥90% branch must name this case as intended routing, not leave it to inference",
        )

    def test_the_strong_branch_still_reports_the_finding(self):
        self.assertRegex(
            self.text,
            r"(?s)If the audit produced a finding, say so in the same breath",
            "strong numbers must not suppress the finding — reporting it alongside is the point",
        )

    def test_the_finding_outcome_names_its_bucket(self):
        self.assertRegex(
            self.text,
            r"name the suppressing feature, its share, and \*\*which bucket\*\*",
            "a share without its bucket cannot be acted on",
        )


class EveryCrossReferenceQuotesTheCurrentHeading(unittest.TestCase):
    """INV-246: derive the site set by scanning, never by listing paths."""

    def test_no_shipped_file_quotes_the_retired_heading(self):
        stale = []
        for path in shipped_markdown():
            if RETIRED_HEADING in read(path):
                stale.append(os.path.relpath(path, REPO_ROOT))
        self.assertEqual(
            [],
            stale,
            "these files quote the step-4 heading as it read before the buckets were split, so "
            "the citation no longer resolves:\n  " + "\n  ".join(stale),
        )

    def test_files_citing_step_4_use_the_current_heading(self):
        citing = [
            p
            for p in shipped_markdown()
            if "phaseD-validation.md" not in p
            and re.search(r"suppressor as a FINDING", read(p))
        ]
        self.assertTrue(
            citing,
            "expected at least one cross-reference to the audit's step-4 rule; if none remains, "
            "this scan has stopped testing anything and should be removed or re-aimed",
        )
        for path in citing:
            self.assertIn(
                STEP_4_HEADING,
                read(path),
                "%s cites step 4 but not by its current heading"
                % os.path.relpath(path, REPO_ROOT),
            )

    def test_the_deliverable_carries_the_bucket_forward(self):
        """A keepsake recording the share without the bucket cannot be acted on later."""
        module7 = os.path.join(
            PLUGIN,
            "skills",
            "module-07-query-visualize-discover",
            "phase1-query-visualize.md",
        )
        self.assertRegex(
            read(module7),
            r"(?s)suppressor findings belong here.{0,120}carrying the bucket they came from",
            "the data-discoveries deliverable must carry the bucket, not just the share",
        )


if __name__ == "__main__":
    unittest.main()
