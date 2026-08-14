"""A why demonstration must parse the field a why response actually carries.

Module 7 step 4b.3 told the guide to pass `SZ_INCLUDE_MATCH_KEY_DETAILS` and explained it as
"the match key Senzing used to decide these records belong together". A why response carries
no `MATCH_KEY_DETAILS`. The breakdown of the why key lives at

    WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS

confirmed on MCP server 1.32.9 (2026-08-14) via
`get_sdk_reference(topic='response_schemas', filter='why_records')`.

The flag is not simply misnamed — it is a different surface. `topic='flags'` reports
`SZ_INCLUDE_MATCH_KEY_DETAILS` with `response_paths: RELATED_ENTITIES[]` and `depends_on` one
of the five relations flags, so what it populates is a `MATCH_KEY_DETAILS` object on each
*related entity*. The why methods accept it; on a why call it has nothing to attach to.

That is the silent-blank failure `ground-rules.md` → "Defensive parsing" exists for: a parser
written for the wrong field name yields None and renders as empty text, with no error raised.
The step's own prose was what pointed at the wrong name.

So this file asserts the step names the real path, that the only surviving mention of
`MATCH_KEY_DETAILS` is the one forbidding it here (with the reason that makes the ban
checkable, not a bare prohibition), that the composite-vs-member type hazard is stated, and
that the pre-existing `response_schemas`-before-parsing instruction survived the edit.

Source spec: `specs/why-response-carries-why-key-details-not-match-key-details.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE2 = (
    REPO_ROOT
    / "plugins"
    / "senzing-bootcamp"
    / "skills"
    / "module-07-query-visualize-discover"
    / "phase2-discover.md"
)


def read():
    return PHASE2.read_text(encoding="utf-8")


def squash(text):
    """Collapse newlines and runs of spaces so wrapped prose matches as one line."""
    return re.sub(r"\s+", " ", text)


def step_4b3(text):
    """The body of step 4b.3, where the flag guidance lives."""
    start = text.index("3. **SDK flags and response shape:**")
    end = text.index("4. **Plain-language explanation", start)
    return text[start:end]


def prohibition_bullet(text):
    """The single ⛔ bullet that forbids SZ_INCLUDE_MATCH_KEY_DETAILS on a why call.

    Spans from its ⛔ marker to the start of the next sibling bullet, so a mention that
    drifts out of the ban and back into prescription falls outside it.
    """
    body = step_4b3(text)
    start = body.index("⛔ **Do not reach for")
    nxt = re.search(r"\n   - ", body[start:])
    return body[start:start + nxt.start()] if nxt else body[start:]


class WhyKeyDetailsIsTheParsedField(unittest.TestCase):
    def test_step_4b3_names_the_full_why_key_details_path(self):
        """Naming the leaf alone would let a parser guess the wrong parent."""
        self.assertIn(
            "WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS", squash(step_4b3(read()))
        )

    def test_the_why_key_details_shape_is_described_for_the_parser(self):
        """CONFIRMATIONS[] is what the step goes on to present; the schema names it."""
        body = squash(step_4b3(read()))
        self.assertIn("CONFIRMATIONS[]", body)
        for field in ("FTYPE_CODE", "TOKEN", "SCORE_BUCKET"):
            self.assertIn(field, body, f"{field} missing from the WHY_KEY_DETAILS shape")

    def test_step_5_reads_the_why_key_from_its_documented_path(self):
        """Step 5 presents the key; an unnamed 'match-key string' is the guessable part."""
        text = read()
        start = text.index("5. **Match-key breakdown:**")
        step5 = squash(text[start:text.index("6. **Practical use cases:**", start)])
        self.assertIn("WHY_RESULTS[].MATCH_INFO.WHY_KEY", step5)
        self.assertIn("WHY_KEY_DETAILS", step5)


class MatchKeyDetailsIsNotPrescribedForAWhyCall(unittest.TestCase):
    def test_every_match_key_details_mention_sits_inside_the_prohibition(self):
        """The criterion: the file must not instruct parsing it out of a why response.

        Asserted by span, not by counting: a new prescription anywhere else in the file
        lands outside the ⛔ bullet and fails, which a bare 'the token appears' check or a
        fixed occurrence count would both miss.
        """
        text = read()
        ban = prohibition_bullet(text)
        offsets = [m.start() for m in re.finditer(r"MATCH_KEY_DETAILS", text)]
        self.assertTrue(offsets, "MATCH_KEY_DETAILS vanished; the ban states the reason")
        ban_start = text.index(ban)
        ban_end = ban_start + len(ban)
        stray = [o for o in offsets if not ban_start <= o < ban_end]
        self.assertEqual(
            [],
            stray,
            "MATCH_KEY_DETAILS mentioned outside the prohibition, at offsets "
            f"{stray} — a why demonstration must not prescribe or parse it",
        )

    def test_the_ban_carries_the_reason_that_makes_it_checkable(self):
        """A bare ban is unmaintainable: the next editor cannot tell whether it still holds.

        Both halves are load-bearing — the surface it populates, and the dependency that
        keeps it empty on a why call.
        """
        ban = squash(prohibition_bullet(read()))
        self.assertIn("RELATED_ENTITIES[]", ban)
        self.assertIn("depends_on", ban)
        self.assertIn("relations flag", ban)

    def test_the_ban_names_where_the_flag_does_belong(self):
        """Routing the reader onward is what stops the ban reading as 'never use this flag'."""
        self.assertIn("step 4d", squash(prohibition_bullet(read())))


class FlagTypesAreConfirmedNotOnlyNames(unittest.TestCase):
    def test_the_composite_member_hazard_is_stated_in_the_flag_guidance(self):
        """A composite need not share the element type of a flag *collection* argument."""
        body = squash(step_4b3(read()))
        self.assertIn("composite_members", body)
        self.assertIn("topic='parameters'", body)

    def test_the_hazard_is_stated_once(self):
        """'Stated once' is the acceptance criterion; twice is drift waiting to disagree."""
        self.assertEqual(1, squash(read()).count("composite_members"))


class ThePreExistingSchemaInstructionSurvived(unittest.TestCase):
    def test_response_schemas_is_still_consulted_before_parsing(self):
        """Following this instruction is what surfaces the wrong field name (INV-115)."""
        body = squash(step_4b3(read()))
        self.assertIn("topic='response_schemas', filter='why_records'", body)
        self.assertIn("INV-115", body)

    def test_feature_scores_is_still_prescribed_with_its_explanation(self):
        """The other half of the original 'BOTH flags' pair is correct and must remain."""
        body = squash(step_4b3(read()))
        self.assertIn("SZ_INCLUDE_FEATURE_SCORES", body)
        self.assertIn("numeric similarity scores", body)


if __name__ == "__main__":
    unittest.main()
