"""The fast-path coverage check decides sub-lists by their contents, not their shape.

Module 5's Step 5a gates the fast-path offer -- the offer to skip the whole mapping
module -- on whether every field of a CORD source has been dispositioned. Its
coverage check partitioned only ROOT KEYS, and listed the structural set as
``DATA_SOURCE, RECORD_ID, RECORD_TYPE, FEATURES`` plus "the legacy per-feature root
sub-lists (NAMES, ADDRESSES, IDENTIFIERS, ...)".

On the legacy-flat shape the dispositionable content lives one level down, and that
trailing ellipsis invites membership by resemblance: plural, uppercase, an array of
objects. Measured on MCP server 1.35.1, 2026-09-01, ``las-vegas / GLEIF`` has four
root arrays that look alike -- ``COUNTRIES``, ``DATES`` and ``RELATIONSHIPS`` hold
spec attributes, while ``RISKS`` holds ``TOPIC``, which appears in no feature table
of the Entity Specification, on 547 of the source's 1,952 records.

Filed as structural, its contents are invisible, and a source whose only unmapped
content sits inside such an array is offered the fast path with real fields
undecided -- which is what the step's own stop sign already forbids at the leaf
("do not resolve by exact string match"), reached one level up at the container.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STEP_5A = (REPO / "plugins" / "senzing-bootcamp" / "skills" /
           "module-05-data-quality-mapping" / "phase1-quality-assessment.md")


def coverage_check_section():
    """Step 5a's coverage check, from its partition sentence to the next numbered step."""
    text = STEP_5A.read_text(encoding="utf-8")
    start = text.find("partition every root key")
    assert start != -1, "Step 5a's coverage check was not found -- has the step been renamed?"
    nxt = text.find("\n## ", start)
    return text[start: nxt if nxt != -1 else len(text)]


class TheStructuralSetIsDecidedByContentsNotByShape(unittest.TestCase):
    def setUp(self):
        self.section = coverage_check_section()

    def test_the_structural_set_names_the_contents_test(self):
        """A bare list of example sub-lists is what invited membership by resemblance."""
        self.assertRegex(
            self.section, r"(?i)whose contents resolve",
            "The structural set must state that a root sub-list qualifies only when its CONTENTS "
            "resolve to Entity Specification attributes. Listing example names and an ellipsis "
            "lets any plural uppercase array of objects be filed as structure.",
        )

    def test_the_partition_recurses_one_level(self):
        """Root-key-only partitioning cannot see undispositioned nested content.

        ⚠️ Asserts the INSTRUCTION, not its vocabulary. An earlier version matched
        ``one level|contained keys`` and passed with the recursion sentence deleted,
        because the unrecognized-keys bullet three lines above also says "contained
        keys". An assertion a neighboring bullet can satisfy is not an assertion
        about the claim -- the same shape that weakened two guards earlier in this
        run.
        """
        self.assertRegex(
            self.section,
            r"(?i)(partition one level down|same three-way test on the contained)",
            "The coverage check must INSTRUCT running the same three-way test on the contained "
            "keys of root arrays -- not merely mention them. On the legacy-flat shape that is "
            "where the dispositionable content lives, so a root-only partition answers a "
            "different question from the one the fast path is gated on.",
        )

    def test_the_discriminator_is_stated_not_merely_implied(self):
        """The rule is one sentence; the defect was that nobody wrote it down."""
        flat = re.sub(r"\s+", " ", self.section).lower()
        self.assertTrue(
            "never by the key's shape" in flat or "not by the key's shape" in flat,
            "The step must say outright that shape does not decide membership. Without it a "
            "reader applies the examples by analogy, which is how RISKS was filed as structure.",
        )


class TheWorkedCaseIsRecordedWithItsProvenance(unittest.TestCase):
    """A measured counter-example is what keeps the rule from reading as pedantry."""

    def setUp(self):
        self.section = coverage_check_section()

    def test_the_non_resolving_array_is_named(self):
        self.assertIn(
            "RISKS", self.section,
            "The step should name the measured counter-example. An abstract rule about 'arrays "
            "whose contents do not resolve' is much harder to apply than one naming the array "
            "that actually broke it.",
        )

    def test_the_measurement_carries_a_server_version_and_date(self):
        """A Senzing claim without provenance cannot be re-checked when the server moves."""
        self.assertRegex(
            self.section, r"1\.35\.1",
            "The GLEIF shape claim must carry the MCP server version it was verified against "
            "(INV-080), so a later reader can tell a stale claim from a current one.",
        )
        self.assertRegex(
            self.section, r"20\d\d-\d\d-\d\d",
            "The claim must carry the date it was verified.",
        )

    def test_the_genuine_sublists_are_distinguished_from_the_impostor(self):
        """Naming only the failure teaches the wrong lesson -- that arrays are suspect."""
        for genuine in ("COUNTRIES", "DATES", "RELATIONSHIPS"):
            self.assertIn(
                genuine, self.section,
                "The step must show the arrays that DO resolve alongside the one that does not; "
                "otherwise the rule reads as 'distrust root arrays' rather than 'look inside'.",
            )


if __name__ == "__main__":
    unittest.main()
