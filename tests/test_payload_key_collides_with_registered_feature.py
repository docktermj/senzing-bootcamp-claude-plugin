"""A payload routing answer must be honored in effect, not only in form.

MCP-NEGATIVE-SCAN: ignore-file — this file asserts the marker FORMAT (that the shipped
marker names its owning route and carries a server version and date). The token below is a
`startswith` needle in a test body, not a dated claim about the current server, and the
scanner would otherwise report it as a malformed marker.

A Bootcamper was asked how to route a field and answered **payload**. The mapper kept the
key under its own name at the record root — where that name is a *registered feature
attribute* — so Senzing extracted it as a feature anyway. Their explicit answer was
silently not honored. The same field also went through a list-joining payload route, so
**13,803 of 19,050 records** carried `"XXX; VGB; GBR"` as one literal value.

⛔ **Every static gate passed.** The analyzer, the verbatim check and the routing report each
confirm the output matches the plan and the plan is faithful to the source. None of them
confirms the plan does what the Bootcamper asked, so an answer selecting a *behavior*
rather than a *value* is unverified by construction. That general shape is the finding; the
collision is one instance of it.

⚠️ **The analyzer already knew** — its SCHEMA warning fired and cleared on the rename. The
check was in the wrong place in the flow, not missing, which is why the remedy moves it to
the mapping gate rather than inventing a new instrument.

⛔ **The precedence mechanism is OBSERVATION-ONLY and these tests pin that framing**, not
just the guidance. One run, one SDK build, the analyzer as corroborating instrument. The
Entity Specification distinguishes payload from registered features and says choosing
between them is a mapping decision, but states no precedence for a colliding root-level key
— re-confirmed via `search_docs(category='data_mapping')` on server 1.32.9, 2026-08-17, and
carried as an `MCP-NEGATIVE` marker with its owning route so a dry run re-asks it
(INV-080/INV-149/INV-194).

Source spec: `specs/routing-a-registered-feature-attribute-to-payload-is-silently-a-no-op.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE5 = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" /
           "module-05-data-quality-mapping")
PHASE2 = MODULE5 / "phase2-data-mapping.md"
PHASE3 = MODULE5 / "phase3-test-load.md"


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class TheCollisionIsCaughtAtTheMappingGate(unittest.TestCase):

    def test_the_rule_is_stated_at_the_mapping_step(self):
        self.assertIn(
            "a root-level `payload` key MUST NOT be a registered feature attribute name",
            flat(PHASE2))

    def test_it_runs_before_the_plan_is_accepted(self):
        text = flat(PHASE2)
        self.assertIn("Before accepting the plan", text)
        self.assertIn("not after the output is analyzed", text)

    def test_it_reuses_the_catalog_lookup_the_module_already_makes(self):
        self.assertIn("the same lookup, asked of the other disposition", flat(PHASE2))


class TheBootcampersAnswerIsNotOverridden(unittest.TestCase):
    """INV-006 — their intent is achievable; only the key name is wrong."""

    def test_silent_re_routing_is_forbidden(self):
        self.assertIn("do NOT silently re-route or override the answer", flat(PHASE2))

    def test_the_collision_offers_a_rename_as_a_pinned_question(self):
        text = PHASE2.read_text(encoding="utf-8")
        question = [l for l in text.splitlines()
                    if l.lstrip().startswith("> 👉") and "registered Senzing feature" in l]
        self.assertEqual(1, len(question), "the collision has no single pinned question")
        self.assertIn("Shall I store it as", question[0])
        self.assertTrue(question[0].rstrip().endswith("(respond yes or no)"),
                        "the collision question is not answerable yes/no (INV-008)")

    def test_it_says_what_senzing_will_actually_do(self):
        self.assertIn("Senzing will resolve on it anyway", flat(PHASE2))

    def test_both_answers_are_recorded(self):
        text = flat(PHASE2)
        self.assertIn("never leave the collision unrecorded either way", text)


class AListValuedPayloadRouteIsWarned(unittest.TestCase):

    def test_the_join_behavior_is_stated_with_its_signature(self):
        text = flat(PHASE2)
        self.assertIn("joined into ONE literal value", text)
        self.assertIn("13,803 of 19,050 records", text)


class TheAnalyzerWarningMovesForward(unittest.TestCase):

    def test_phase_two_reads_the_schema_warnings_at_the_gate(self):
        self.assertIn("Surface the analyzer's SCHEMA warnings here", flat(PHASE2))

    def test_phase_three_routes_this_finding_back_rather_than_absorbing_it(self):
        """⛔ It must not be filed under the recommended-vs-flat conformance split."""
        text = flat(PHASE3)
        self.assertIn("One SCHEMA finding is NOT a conformance notice", text)
        self.assertIn("step 11's collision check did not run", text)


class TheGeneralShapeIsNamed(unittest.TestCase):
    """What the gates structurally cannot see."""

    def test_it_says_the_gates_check_the_plan_not_the_request(self):
        text = flat(PHASE2)
        self.assertIn("None of them confirms the plan does what the Bootcamper **asked "
                      "for**", text)

    def test_it_generalizes_to_any_behavior_selecting_answer(self):
        self.assertIn("Wherever a question's answer chooses a behavior", flat(PHASE2))


class ThePrecedenceMechanismIsMarkedObservationOnly(unittest.TestCase):
    """⛔ INV-080/INV-149 — never presented as MCP-sourced."""

    def test_it_is_labeled_observation_only_with_its_date_and_instrument(self):
        text = flat(PHASE2)
        self.assertIn("This mechanism is OBSERVATION-ONLY", text)
        self.assertIn("2026-08-17", text)
        self.assertIn("analyzer's own SCHEMA warning as the corroborating instrument", text)

    def test_it_tells_the_reader_to_re_confirm_before_relying_on_it(self):
        self.assertIn("re-confirm before relying on it", flat(PHASE2))

    def test_the_absence_carries_a_well_formed_negative_marker(self):
        """INV-194 — a negative with no owning route does not parse and is not evidence."""
        lines = [l for l in PHASE2.read_text(encoding="utf-8").splitlines()
                 if l.startswith("MCP-NEGATIVE:")]
        self.assertEqual(1, len(lines), "expected exactly one marker in this file")
        marker = lines[0]
        self.assertIn("owner:", marker, "the marker names no owning route")
        self.assertIn("absence negative", marker)
        self.assertRegex(marker, r"server \d+\.\d+\.\d+, \d{4}-\d{2}-\d{2}$")

    def test_the_rule_is_not_claimed_as_documented(self):
        text = flat(PHASE2)
        self.assertIn("not as a documented rule", text)


class TheCheckIsNotABlanketObjectionToPayload(unittest.TestCase):
    """Negative control: payload routing itself must stay ordinary and unobstructed."""

    def test_the_rule_is_scoped_to_registered_attribute_names(self):
        """A payload key that is not a registered attribute is untouched by the rule."""
        text = flat(PHASE2)
        self.assertIn("MUST NOT be a registered feature attribute name", text)
        self.assertNotIn("payload routing is discouraged", text)
        self.assertNotIn("avoid payload", text)

    def test_payload_remains_an_offered_disposition(self):
        self.assertIn("`feature`, `payload`, `ignore`, `derived`, or `extract`",
                      flat(PHASE2))

    def test_the_existing_rule_against_downgrading_to_payload_survives(self):
        self.assertIn("Never silently downgrade a bootcamper's choice to `payload`",
                      flat(PHASE2))


class TheGuidanceIsBehaviorNotAHelper(unittest.TestCase):
    """INV-002 — the catalog lookup is a data question, not a Python one."""

    def test_the_new_block_names_no_language_specific_helper(self):
        text = PHASE2.read_text(encoding="utf-8")
        start = text.index("Before accepting the plan")
        end = text.index("something must check the behavior was actually obtained.", start)
        block = text[start:end]
        for token in ("def ", "import ", "python3 "):
            with self.subTest(token=token):
                self.assertNotIn(token, block,
                                 "the rule is stated as code rather than as behavior")


if __name__ == "__main__":
    unittest.main()
