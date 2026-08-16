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


def enclosing_block(text, offset):
    """The paragraph or list item containing ``offset``.

    Bounded by a blank line either side rather than by a fixed window: the prose that
    qualifies a flag mention sits at the head of its own block, and a fixed window is
    the wrong length by construction — too short and it misses a qualifier three
    sentences up (which produced a false positive here), too long and it borrows a
    qualifier from an unrelated neighboring block.
    """
    start = text.rfind("\n\n", 0, offset)
    end = text.find("\n\n", offset)
    return text[(0 if start < 0 else start): (len(text) if end < 0 else end)]


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


class NoOtherSiteInTheModulePrescribesIt(unittest.TestCase):
    """The criterion named one file; the defect was in two.

    `phase1-query-visualize.md` step 3a carried the same instruction — "ensure the query
    was called with SZ_INCLUDE_FEATURE_SCORES and/or SZ_INCLUDE_MATCH_KEY_DETAILS" for
    the why_* methods — and was invisible to a guard scoped to `phase2-discover.md`.
    So this sweeps the module: a fix applied to one file is not a fix.
    """

    def test_the_flag_is_never_mentioned_without_its_dependency_or_its_ban(self):
        """Every mention carries what makes it checkable, in one of two shapes.

        The flag is legitimate for the methods that return related entities — a network
        visualization renders exactly the `RELATED_ENTITIES[]` it populates — so a blanket
        ban would be wrong and would have to be worked around. What is never optional is
        the reason it can silently do nothing: on a why call it has no surface (the ban),
        and anywhere else it needs a relations flag (`depends_on`). A mention carrying
        neither is the shape that produced this defect twice in one module.
        """
        for path in sorted(PHASE2.parent.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"SZ_INCLUDE_MATCH_KEY_DETAILS", text):
                with self.subTest(file=path.name, offset=match.start()):
                    block = squash(enclosing_block(text, match.start()))
                    self.assertTrue(
                        "Do not reach for" in block
                        or "not from a `MATCH_KEY_DETAILS`" in block
                        or "depends_on" in block,
                        "%s mentions SZ_INCLUDE_MATCH_KEY_DETAILS at offset %d with "
                        "neither its relations dependency nor the why-call prohibition"
                        % (path.name, match.start()),
                    )

    def test_phase1_names_the_why_key_details_path(self):
        """The reader of step 3a needs the right field, not merely the ban."""
        phase1 = squash((PHASE2.parent / "phase1-query-visualize.md").read_text(encoding="utf-8"))
        self.assertIn("WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS", phase1)
        self.assertIn("INV-179", phase1)

    def test_phase1_still_prescribes_feature_scores(self):
        """The correct half of the original instruction must survive the correction."""
        phase1 = squash((PHASE2.parent / "phase1-query-visualize.md").read_text(encoding="utf-8"))
        self.assertIn("SZ_INCLUDE_FEATURE_SCORES", phase1)


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
