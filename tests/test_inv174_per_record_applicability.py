"""INV-174: completeness is measured per record against that record's kind, never per feature.

INV-174 was the single highest-risk invariant in the repo by two combined measures on 2026-08-13: it
**enumerates** (four separately-breakable lists) and **no test cited it**. Only three invariants sat
in that intersection; the other two were checked by the 2026-08-13 production-readiness audit and hold.
⚠️ Their IDs are deliberately NOT written here: `coverage_reports.py invariants` greps `tests/` for
an ID, so naming them as rationale would score them "covered" while nothing asserts them — the
over-report failure that file documents (one invariant was named by five test files, every one of
them as rationale, none of them its enforcer). INV-174 was disclosed as unchecked, because verifying
it means reading the guidance that authors the
completeness helper rather than a shipped implementation (`module-05-data-quality-mapping/SKILL.md`
says the helper is "authored fresh each run until that guide is ported").

That is exactly what makes it fragile: it constrains code the plugin **describes** rather than
ships, so conformance depends on the guidance stating the rule completely enough that a fresh
implementation gets it right every run — INV-002's boundary test.

What the invariant costs when broken is recorded in its own text and in the guidance: a sanctions
list with NAME and ADDRESS on 100% of records scored **52% completeness / 69% overall** and would
have been sent for remediation, because person-oriented features were averaged across a source where
most records are organizations. Rescoring per record gave **97%**. It fails toward false alarm, so a
Bootcamper is actively misdirected rather than merely under-served.

⚠️ **These assertions deliberately pin STRUCTURE, not the Entity Specification's wording (INV-219).**
The guidance's feature→type table quotes the specification, and those quotes are the server's to
change; pinning "Person date of birth" here would fail whoever corrects the table after the spec is
reworded, with a message asserting the opposite of what the server says. So this asserts that the
table exists, that it maps features to PERSON / ORGANIZATION / either, that shared fields are marked
not-to-exclude, and that the reader is told to re-read rather than trust it — all of which stay true
however the specification is worded.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE1 = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
          / "module-05-data-quality-mapping" / "phase1-quality-assessment.md")


def text():
    return PHASE1.read_text(encoding="utf-8")


def flat():
    return re.sub(r"\s+", " ", text())


class CompletenessIsMeasuredPerRecord(unittest.TestCase):
    """INV-174, requirement 1: per record against its kind, aggregated — never per feature."""

    def test_the_rule_is_stated_as_a_hard_requirement(self):
        self.assertRegex(
            flat(),
            r"(?i)PER RECORD against the features that apply to that record's\s*`?RECORD_TYPE`?",
            "the per-record rule must be stated where the helper is authored (INV-183), not "
            "implied by the metric's definition",
        )

    def test_the_per_feature_average_is_explicitly_forbidden(self):
        """The defect is not omission — it is the obvious wrong implementation."""
        self.assertRegex(flat(), r"(?i)never as one average per feature across the whole source")

    def test_the_metric_definition_itself_cites_the_invariant(self):
        """A rule stated once and contradicted by the definition above it would still ship."""
        self.assertRegex(flat(), r"(?i)per-`?RECORD_TYPE`? applicability \(INV-174\)")

    def test_the_failure_it_prevents_is_recorded_with_its_numbers(self):
        """⛔ Never cut rationale. This narrative is what stops the rule being re-argued."""
        body = flat()
        self.assertRegex(body, r"(?i)sanctions list", "the worked failure must survive")
        self.assertRegex(body, r"\b52%|\b69%", "the wrong score it produced")
        self.assertRegex(body, r"\b97%", "the score a correct per-record measurement gives")


class ApplicabilityComesFromTheSpecificationNotTheFile(unittest.TestCase):
    """INV-174, requirement 2: derive it from the authority, never from a hardcoded list."""

    def test_the_derive_rule_is_stated(self):
        self.assertRegex(
            flat(),
            r"(?i)Derive applicability from the Entity Specification, not from a list in this file",
        )

    def test_the_route_that_answers_it_is_named(self):
        """A rule with no route is a rule the guide has to improvise (INV-212's principle)."""
        self.assertRegex(flat(), r"search_docs\(query='what features to map'")
        self.assertRegex(flat(), r"category='data_mapping'")

    def test_the_table_maps_features_to_a_kind(self):
        """Structure, not the specification's wording (INV-219)."""
        body = flat()
        for kind in ("PERSON", "ORGANIZATION"):
            with self.subTest(kind=kind):
                self.assertIn(kind, body)

    def test_the_table_is_marked_partial_and_re_read_rather_than_trusted(self):
        """This is a worked illustration of a METHOD, not a cached authority (INV-080)."""
        body = flat()
        self.assertRegex(body, r"(?i)re-read it for the source you are assessing")
        self.assertRegex(body, r"(?i)deliberately partial")
        self.assertRegex(body, r"(?i)not a substitute for asking")


class SharedAndUnknownKindsAreHandled(unittest.TestCase):
    """INV-174, requirements 3 and 4 — the two halves most likely to be dropped."""

    def test_kind_independent_fields_are_marked_not_to_exclude(self):
        """Excluding them is the over-correction that follows from fixing requirement 1."""
        self.assertRegex(flat(), r"(?i)do not exclude these")

    def test_a_record_with_no_type_is_scored_against_any_type_features(self):
        self.assertRegex(
            flat(),
            r"(?i)Score those against the features that apply to \*?\*?any\*?\*? type",
        )

    def test_the_count_scored_that_way_must_be_reported(self):
        """An unreported subset is the aggregate hiding exactly what the reader needs."""
        body = flat()
        self.assertRegex(body, r"(?i)report how many records were\s*\*?\*?scored that way")
        self.assertRegex(body, r"(?i)must not be hidden inside an aggregate")

    def test_a_missing_record_type_is_itself_raised_as_a_finding(self):
        self.assertRegex(flat(), r"(?i)is itself a finding worth\s*raising")


if __name__ == "__main__":
    unittest.main()
