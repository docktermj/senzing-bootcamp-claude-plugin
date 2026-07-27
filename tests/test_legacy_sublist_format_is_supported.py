"""The per-feature sub-list format is supported, and the guidance must say so.

`sz_json_analyzer.py` returns exit 1 with hundreds of "Missing or non-array
FEATURES" errors against a source in the older per-feature sub-list shape
(`NAMES`, `ADDRESSES`, `IDENTIFIERS` as separate root lists). The Senzing Entity
Specification, § "Recommended JSON schema", says of that shape: "While we still
support that, we now recommend ...". An empirical A/B in the reported session
confirmed it: both formats loaded into a purged database produced identical
resolution — 2 entities, largest 17 records, same three sources.

The analyzer is not lying; it measures conformance to the *recommended* schema,
whose validation rules do say `FEATURES (required, array)`. Both statements are
true and they answer different questions. What made this expensive is that three
separate files told the bootcamper to act on the conformance answer as though it
were the loadability answer:

* `phase2-data-mapping.md` — "use its result as the authoritative check"
* `phase3-test-load.md` — named the flat format a structural error to "fix ... in
  the transformation program"
* `phase1-quality-assessment.md` — the CORD fast-path readiness check required a
  `FEATURES` array, so every sub-list CORD source was classified not-ready

That is the whole defect: hand-writing five mappers to convert data that already
loads and resolves perfectly. These tests hold the corrected guidance in place.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULE5 = os.path.join(
    REPO_ROOT, "plugins", "senzing-bootcamp", "skills", "module-05-data-quality-mapping"
)
PHASE1 = os.path.join(MODULE5, "phase1-quality-assessment.md")
PHASE2 = os.path.join(MODULE5, "phase2-data-mapping.md")
PHASE3 = os.path.join(MODULE5, "phase3-test-load.md")


def flat(path):
    """File text with runs of whitespace collapsed — these are wrapped prose.

    A phrase assertion against the raw text is really an assertion about where
    the line breaks fall, so re-flowing a paragraph would fail it.
    """
    with open(path, encoding="utf-8") as handle:
        return re.sub(r"\s+", " ", handle.read())


class TheGuidanceNamesTheFormatAsSupported(unittest.TestCase):

    def test_phase2_quotes_the_specification(self):
        text = flat(PHASE2)
        self.assertIn(
            "While we still support that", text,
            "phase2 must quote the Entity Specification's own statement — it is the "
            "authority that settles the analyzer's verdict",
        )
        self.assertRegex(
            text,
            r"sub-list.{0,400}(still support|supported)|still support.{0,400}sub-list",
            "the quote must be attached to the sub-list format it licenses",
        )

    def test_every_file_that_judges_the_format_calls_it_supported(self):
        for path in (PHASE1, PHASE2, PHASE3):
            with self.subTest(file=os.path.basename(path)):
                self.assertRegex(
                    flat(path),
                    r"still support|still-supported",
                    "this file gates on record shape, so it must state that the "
                    "sub-list format is supported",
                )

    def test_the_claim_is_marked_for_mcp_reconfirmation(self):
        """INV-080: a Senzing fact is re-confirmed, never carried from a plugin file."""
        for path in (PHASE1, PHASE2):
            with self.subTest(file=os.path.basename(path)):
                self.assertRegex(
                    flat(path),
                    r"INV-080|re-confirm|Re-confirm|Confirm the still-supported",
                    "the supported-format claim must be marked for re-confirmation "
                    "from the MCP server rather than trusted from this file",
                )


class ConformanceFindingsDoNotTriggerARewrite(unittest.TestCase):

    def test_phase3_no_longer_calls_the_flat_format_a_structural_error_to_fix(self):
        text = flat(PHASE3)
        self.assertNotRegex(
            text,
            r"Structural errors from `analyze_record` \(e\.g\., flat format instead of a "
            r"FEATURES array[^)]*\)[^.]*\. [^.]*\. [^.]*\. Fix the structural errors",
            "phase3 must not instruct fixing the flat format in the transformation "
            "program — that is the five-mapper rewrite this spec exists to prevent",
        )
        self.assertRegex(
            text,
            r"[Dd]o \*\*not\*\* rewrite the transformation program|"
            r"never as remediation|not a reason to remap",
            "phase3 must say plainly that the conformance finding is not remapped away",
        )

    def test_phase2_forbids_remapping_to_clear_a_conformance_finding(self):
        self.assertRegex(
            flat(PHASE2),
            r"Never hand-write a mapper to convert a supported format",
            "phase2 must forbid the rewrite outright, not merely permit continuing",
        )

    def test_the_two_finding_classes_are_distinguished(self):
        text = flat(PHASE2)
        for needle in ("Structural invalidity", "Conformance to the recommended schema"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_the_exit_code_alone_is_not_the_gate(self):
        self.assertRegex(
            flat(PHASE2),
            r"exit code alone is NOT the gate|exit code is not the gate",
            "a non-zero analyzer exit must not by itself block Module 5",
        )


class TheMisleadingWarningIsExplained(unittest.TestCase):

    def test_no_name_features_found_is_documented_as_an_artefact(self):
        text = flat(PHASE2)
        self.assertIn("No NAME features found", text)
        self.assertRegex(
            text,
            r"does not mean the names are missing|not.{0,40}evidence that names are absent",
            "the warning must be explained: a bootcamper cannot otherwise tell "
            "'the analyzer did not look there' from 'there are no names'",
        )

    def test_phase3_carries_the_same_reading(self):
        self.assertRegex(
            flat(PHASE3),
            r"No NAME features found",
            "phase3 shows the analyzer's output too, so it needs the same caution",
        )


class AnEmpiricalProbeSettlesTheDisagreement(unittest.TestCase):

    def test_phase2_requires_loading_one_record_as_the_arbiter(self):
        text = flat(PHASE2)
        self.assertRegex(
            text,
            r"[Ll]oad \*\*one\*\* unmodified record|load one unmodified record",
            "the tiebreaker is an observation, not a choice between two documents",
        )

    def test_the_probe_result_is_recorded(self):
        self.assertRegex(
            flat(PHASE2),
            r"mapping_state_\[datasource\]\.json|INV-125",
            "INV-125 requires the concluded cause be recorded, not just acted on",
        )


class TheCordFastPathAcceptsBothShapes(unittest.TestCase):
    """Every CORD source is in the sub-list shape, so this gate decided them all."""

    def test_readiness_accepts_the_legacy_flat_shape_as_well_as_a_features_array(self):
        text = flat(PHASE1)
        self.assertRegex(
            text,
            r"[Tt]reat \*\*both\*\* forms as Senzing-ready|both forms as Senzing-ready",
            "requiring a FEATURES array classifies every legacy-shaped CORD source as "
            "not-ready and sends loadable data through a mapping phase it does not need",
        )
        self.assertRegex(text, r"NAMES.{0,60}ADDRESSES", "name the sub-list keys concretely")

    def test_the_legacy_shape_is_not_described_as_sub_lists_alone(self):
        """A source with no repeating feature is flat with NO sub-list at all.

        Las Vegas/PPP_LOANS is exactly that — root-level BUSINESS_NAME_ORG and
        RECORD_TYPE, no FEATURES and no sub-lists — so a readiness check keyed on
        sub-lists would still misjudge it. The specification's own wording is "a
        flat JSON structure WITH a separate sub-list for each feature that had
        multiple values": the sub-lists are a part of the shape, not the whole.
        """
        for path in (PHASE1, PHASE2, PHASE3):
            with self.subTest(file=os.path.basename(path)):
                self.assertRegex(
                    flat(path),
                    r"flat.{0,120}root|root.{0,120}sub-list|feature attributes at the record root",
                    "the legacy shape must be described as flat root attributes with "
                    "sub-lists where a feature repeats, not as sub-lists alone",
                )

    def test_cord_is_not_assumed_to_use_one_shape(self):
        """Verified against the MCP server: CORD ships both forms."""
        for path in (PHASE1, PHASE2):
            with self.subTest(file=os.path.basename(path)):
                self.assertRegex(
                    flat(path),
                    r"CORD ships both|both forms|Do not assume a source's shape",
                    "London/GLOBALDATA returns a FEATURES array and Las Vegas/PPP_LOANS "
                    "returns flat root attributes — provenance does not imply shape",
                )


if __name__ == "__main__":
    unittest.main()
