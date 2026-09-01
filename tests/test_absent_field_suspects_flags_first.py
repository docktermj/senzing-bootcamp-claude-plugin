"""An absent SDK field sends the reader to the flags, not to the schema alone.

``ground-rules.md``'s defensive-parsing rule said: when a field comes back null or blank,
treat it as a probable wrong field name and **verify against `response_schemas`**. For a
**flag-gated** field that route returns the wrong answer, because `requires_flags` is only
*selectively* populated and nothing distinguishes an unannotated field that is always
present from one that is gated.

Verified on MCP server **1.35.3, 2026-09-01** (and unchanged from 1.35.1, 2026-08-31):

    RESOLVED_ENTITY.RECORDS[].MATCH_KEY        no requires_flags
    RESOLVED_ENTITY.RECORDS[].ERRULE_CODE      no requires_flags
    RELATED_ENTITIES[].MATCH_KEY               no requires_flags
    RELATED_ENTITIES[].IS_DISCLOSED            no requires_flags
    RELATED_ENTITIES[].RECORDS[]               requires SZ_ENTITY_INCLUDE_RELATED_RECORD_DATA
    RELATED_ENTITIES[].MATCH_KEY_DETAILS       requires SZ_INCLUDE_MATCH_KEY_DETAILS

The last two are the positive controls: neighbors in the same arrays ARE annotated, which is
what makes the omission read as "unconditional" rather than "not recorded". `topic='flags'`
does not close it from the other side either -- the two `*_MATCHING_INFO` flags carry no
`response_paths` at all.

⚠️ Following the rule as written produced two wrong answers in one walk: a match-key audit
reporting 0 distinct keys against a true 16, and disclosed links reporting 0 against 556. The
rule's *second* remedy (dump a raw response) would have caught both; its first confirmed the
wrong conclusion.

⚠️ This is an ``mcp-server`` finding; the plugin's job is to relay it. The upstream report was
sent 2026-08-31 with the maintainer's approval.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GROUND_RULES = (REPO / "plugins" / "senzing-bootcamp" / "skills" /
                "bootcamp-onboarding" / "ground-rules.md")


def defensive_parsing_bullet():
    """From the Defensive-parsing bullet to the start of the next top-level bullet."""
    text = GROUND_RULES.read_text(encoding="utf-8")
    start = text.find("- **Defensive parsing.**")
    assert start != -1, "the defensive-parsing bullet was not found -- renamed?"
    nxt = text.find("\n- **", start + 1)
    return text[start: nxt if nxt != -1 else len(text)]


def flat(s):
    return re.sub(r"\s+", " ", s)


class TheAbsentFieldCaseIsDistinguished(unittest.TestCase):
    def setUp(self):
        self.bullet = flat(defensive_parsing_bullet())

    def test_absent_is_treated_differently_from_wrong(self):
        self.assertRegex(
            self.bullet,
            r"(?i)absent field[^.]{0,60}as opposed to a wrong value"
            r"|for an absent field[^.]{0,80}suspect the flags",
            "The rule must distinguish an ABSENT field from a WRONG value. They have "
            "different first checks, and collapsing them is what sent the guide to the "
            "schema for a question the schema cannot answer.",
        )

    def test_the_first_check_for_an_absent_field_is_re_issuing_with_flags(self):
        """⚠️ Asserts the INSTRUCTION, not the word 'flags' -- which the bullet above uses."""
        self.assertRegex(
            self.bullet,
            r"(?i)re-issue[^.]{0,80}flag"
            r"|with the matching `?\*?_?MATCHING_INFO`? flag added",
            "The absent-field branch must instruct re-issuing the same call with broader "
            "flags and comparing. Naming the hazard without the diagnostic leaves the reader "
            "exactly where they were.",
        )

    def test_it_says_the_annotation_is_incomplete(self):
        self.assertRegex(
            self.bullet, r"(?i)`?requires_flags`? annotation is \*\*incomplete\*\*"
                         r"|requires_flags[^.]{0,40}incomplete",
            "The rule must say outright that `requires_flags` is incomplete. Without that, a "
            "reader treats an unannotated path as proof it is unconditional -- which is the "
            "wrong conclusion this fix exists to prevent.",
        )

    def test_absence_of_the_annotation_is_named_as_non_evidence(self):
        self.assertRegex(
            self.bullet, r"(?i)not\*?\*? evidence that|is \*\*not\*\* evidence",
            "It must say the annotation's absence is not evidence of anything. That is the "
            "precise inference that failed, and stating the gap without stating the "
            "non-inference leaves the reader free to make it again.",
        )


class TheMeasuredExamplesCarryTheirProvenance(unittest.TestCase):
    def setUp(self):
        self.bullet = flat(defensive_parsing_bullet())

    def test_the_unannotated_paths_are_named(self):
        for path in ("RECORDS[].MATCH_KEY", "RECORDS[].ERRULE_CODE",
                     "RELATED_ENTITIES[].MATCH_KEY", "RELATED_ENTITIES[].IS_DISCLOSED"):
            with self.subTest(path=path):
                self.assertIn(
                    path, self.bullet,
                    "The measured unannotated paths must be named. An abstract warning that "
                    "'some fields are gated' is not actionable at the moment a parse returns "
                    "blank.",
                )

    def test_the_annotated_neighbors_are_named_too(self):
        """Without the positive controls the rule reads as 'the schema is unreliable'."""
        for path in ("RELATED_ENTITIES[].RECORDS[]", "MATCH_KEY_DETAILS"):
            with self.subTest(path=path):
                self.assertIn(
                    path, self.bullet,
                    "The annotated neighbors must be shown beside the unannotated paths. The "
                    "defect is the PARTIAL coverage -- annotated siblings are what make the "
                    "omission look like information rather than a gap.",
                )

    def test_the_claim_carries_a_server_version_and_date(self):
        self.assertRegex(
            self.bullet, r"1\.35\.\d",
            "The annotation claim must carry the MCP server version it was verified against "
            "(INV-080), so a later reader can tell whether it has been fixed upstream.",
        )
        self.assertRegex(self.bullet, r"20\d\d-\d\d-\d\d",
                         "The claim must carry its verification date.")

    def test_the_flag_gating_is_marked_observation_only(self):
        """INV-149: only a live engine can show it, so it may not read as MCP-sourced.

        ⚠️ Anchored to the paired-call evidence, not to the bullet. Checked against the
        whole bullet this passed with the marker deleted, because the pre-existing sentence
        below it already ends "...not a failed call (INV-149)". A marker 200 characters away
        from the claim it qualifies marks nothing -- the fifth time in this run that a guard
        was satisfied by neighboring prose.
        """
        m = re.search(r"differing only in flags", self.bullet)
        self.assertIsNotNone(
            m,
            "The paired-call evidence must be stated -- it is the only thing that shows the "
            "gating, and without it the claim rests on the schema that got it wrong.",
        )
        window = self.bullet[max(0, m.start() - 220): m.end() + 220]
        self.assertRegex(
            window, r"(?i)observation-only|INV-149",
            "The paired-call evidence must be marked observation-only AT THE CLAIM. No MCP "
            "route reports the gating; it was proven against a loaded repository on one "
            "machine, and a reader must be able to tell that from a documented fact.",
        )


class TheExistingGuidanceSurvives(unittest.TestCase):
    """The spec's third and fourth criteria."""

    def setUp(self):
        self.bullet = flat(defensive_parsing_bullet())

    def test_the_raw_dump_remedy_is_unchanged(self):
        self.assertRegex(
            self.bullet, r"(?i)raw dump stays the authority|dump one raw response",
            "The raw-dump remedy must survive -- it is the check that actually caught both "
            "wrong answers on the walk.",
        )

    def test_default_flags_are_not_recommended_for_production(self):
        self.assertRegex(
            self.bullet, r"(?i)diagnostic, not the shipped call"
            r"|narrow back to the flags",
            "Broadening the flags is a diagnostic step. Without saying so, this rule reads as "
            "advice to ship a DEFAULT composite, which `get_sdk_reference`'s own production "
            "caution argues against.",
        )


if __name__ == "__main__":
    unittest.main()
