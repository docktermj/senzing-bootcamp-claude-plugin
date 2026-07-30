"""A lookup that succeeds but stops short, and the half-populated row it causes.

INV-115 sends the guide to `get_sdk_reference(topic='response_schemas')` before
parsing. For the graph methods that lookup **succeeds and is still not enough**:
verified 2026-07-26, `filter='find_network'` returns an entry documenting
`ENTITY_PATHS[]`, `ENTITIES[]` and `ENTITY_NETWORK_LINKS[]` — and nothing about
the fields inside a link element. `get_version` and `get_license` return an empty
`data` array outright. Neither case is a failed call, and a reader who treats it
as one retries instead of dumping the response.

The failure that follows is the nastier half. A reported session parsed link
endpoints under the `ENTITY_ID` / `RELATED_ENTITY_ID` names used elsewhere and
got `None` for both, while `MATCH_KEY` rendered correctly — a row that reads as a
relationship Senzing could not fully describe rather than as a parsing bug. An
all-blank row invites suspicion; a half-populated one does not, because the
fields that did populate signal the parse worked.

The endpoint keys were first confirmed by a live dump on SDK 4.3.3 (2026-07-28):
`MIN_ENTITY_ID` / `MAX_ENTITY_ID`, alongside `MATCH_LEVEL_CODE`, `MATCH_KEY`,
`ERRULE_CODE`, `IS_DISCLOSED`, `IS_AMBIGUOUS`.

**Those keys are now MCP-sourced, and this docstring said otherwise until
2026-07-29.** When first recorded they were dump-only, so the contract carried
them as an unverified caution rather than as names to code against — INV-080
forbids shipping an unverified Senzing fact as the name to code against, and this
repo has twice had to retract an over-generalized claim (`SZ_EXPORT_ALL_FLAGS does
not exist`, and phase D's export/`RELATED_ENTITIES` absolute — INV-169). The
contract and the assertions below were corrected in place under INV-149 once
`get_sdk_reference(topic='response_schemas', filter='find_network')` began
returning the element fields itself; re-confirmed on server 1.32.2, 2026-07-29,
which returns all seven. This prose lagged that correction and contradicted
`test_the_keys_are_no_longer_marked_unconfirmable` in the same file — the small,
ordinary way a stale premise survives its own fix.

What has NOT changed is the discipline the tests actually pin: run the lookup,
then dump the element before parsing. The keys tell a reader what to *expect*;
the dump still decides.

What these tests assert is therefore both halves: the *discipline* (dump the
element, treat a blank field as a wrong name, never present an unconfirmed name as
authoritative) and the *record* (the dump-marked key list, and the `JSON_DATA`
trap where the authoritative reference is itself what misleads).

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")
CONTRACT = os.path.join(
    PLUGIN, "skills", "module-03b-truthset-visualization", "visualization-api-reference.md"
)
DISCOVER = os.path.join(
    PLUGIN, "skills", "module-07-query-visualize-discover", "phase2b-discover.md"
)
COLLECTION = os.path.join(PLUGIN, "skills", "module-04-data-collection", "SKILL.md")


def flat(path):
    """Whitespace-collapsed text, with Markdown blockquote markers stripped.

    Most of the response-shape guidance lives inside a `>` blockquote, so a
    wrapped sentence carries a `>` at each line start. Collapsing whitespace
    alone leaves those markers mid-phrase ("Dump one raw link > element"), which
    fails a phrase assertion for a purely typographic reason.
    """
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    return re.sub(r"\s+", " ", text)


class AnEmptyOrShallowLookupIsExpectedNotAFailure(unittest.TestCase):

    def test_the_contract_still_requires_the_lookup_and_the_dump(self):
        """The rule survives the server's coverage improving.

        This test used to require the contract say the `find_network` entry carries "no
        element fields". That was true on 2026-07-26 and is false on 1.32.1 — the entry now
        documents them (INV-149, corrected in place 2026-07-29) — so the old assertion
        pinned a stale premise and made it load-bearing. What must hold is the discipline,
        not the observation: run the lookup, then dump before parsing.
        """
        text = flat(CONTRACT)
        self.assertRegex(text, r"(?i)Run the lookup anyway|Do the lookup anyway")
        self.assertRegex(text, r"(?i)dump one element and use what is actually there")

    def test_both_call_sites_send_the_reader_to_a_raw_dump(self):
        for path in (CONTRACT, DISCOVER):
            with self.subTest(file=os.path.basename(path)):
                self.assertRegex(
                    flat(path),
                    r"[Dd]ump one raw link element",
                    "the fallback must be stated where the lookup is performed",
                )

    def test_an_empty_result_is_not_treated_as_a_failed_call(self):
        for path in (CONTRACT, DISCOVER, COLLECTION):
            with self.subTest(file=os.path.basename(path)):
                self.assertRegex(
                    flat(path),
                    r"not (an error to retry|a failed (call|lookup))|"
                    r"expected (outcome|result) for those|That is coverage, not a failed call",
                    "an absent entry is coverage, not an error — otherwise the reader "
                    "retries a call that will never return more",
                )

    def test_get_version_and_get_license_are_named(self):
        self.assertRegex(flat(CONTRACT), r"`get_version` and `get_license`")


class ThePartialRowRuleIsStated(unittest.TestCase):

    def test_both_call_sites_carry_the_partial_row_rule(self):
        for path in (CONTRACT, DISCOVER):
            with self.subTest(file=os.path.basename(path)):
                self.assertRegex(
                    flat(path),
                    r"partially populated row is a wrong field name|"
                    r"suspect the blank ones' names",
                    "INV-115 covers a blank field; the partial case needs saying because "
                    "the populated fields make the row look real",
                )

    def test_the_reason_is_recorded_not_just_the_rule(self):
        self.assertRegex(
            flat(CONTRACT),
            r"[Aa]n all-blank row invites suspicion; a half-populated one does not",
            "without the reason, a future edit trims this as redundant with INV-115",
        )


class NoUnverifiedFieldNameIsShipped(unittest.TestCase):
    """INV-080: the endpoint keys are a session observation, not a Senzing fact."""

    def test_the_endpoint_keys_carry_their_current_provenance(self):
        """They are MCP-confirmed now; the requirement is accurate provenance, not caution.

        INV-080 forbids shipping a Senzing fact without saying where it came from — it does
        not require understating what the server confirms. Once `response_schemas` returned
        these fields, "not MCP-confirmable" became the false claim.
        """
        text = flat(CONTRACT)
        self.assertIn("MIN_ENTITY_ID", text)
        self.assertRegex(text, r"(?i)now (documented by|MCP-confirmed)")
        self.assertRegex(text, r"1\.32\.2, 2026-07-30")
        self.assertNotRegex(
            text,
            r"(?i)(still )?not MCP-confirmable",
            "response_schemas documents these fields as of 1.32.1 — the negative claim is stale",
        )

    def test_the_wrong_pairing_is_still_named_as_the_trap(self):
        """The durable half: endpoints may not use the pairing you expect.

        Reworded 2026-07-29. The contract no longer frames the keys as "a warning about
        where to look" — `response_schemas` documents them, so they are names to use. What
        must survive is the trap itself: `ENTITY_ID` / `RELATED_ENTITY_ID` is the pairing a
        reader reaches for, and it yields two blank endpoints while `MATCH_KEY` renders
        (INV-148).
        """
        text = flat(CONTRACT)
        self.assertRegex(text, r"ENTITY_ID` / `RELATED_ENTITY_ID")
        self.assertRegex(text, r"(?i)yields `None` for \*\*both\*\* endpoints|blank")

    def test_the_reader_is_told_to_use_what_is_actually_there(self):
        self.assertRegex(flat(CONTRACT), r"use what is actually there")




class TheDumpConfirmedLinkKeysAreRecorded(unittest.TestCase):
    """Closing the criterion `network-link-fields-...` deliberately left open.

    That spec shipped the defence without the datum, because its implementation
    environment had no loaded engine, and said so: "someone with a loaded engine
    should dump one link element, confirm the keys, and promote the caution to a
    documented field list marked verified-when." That dump has now happened.
    """

    def test_the_element_key_set_is_documented(self):
        text = flat(CONTRACT)
        for key in (
            "MIN_ENTITY_ID",
            "MAX_ENTITY_ID",
            "MATCH_LEVEL_CODE",
            "MATCH_KEY",
            "ERRULE_CODE",
            "IS_DISCLOSED",
            "IS_AMBIGUOUS",
        ):
            with self.subTest(key=key):
                self.assertIn(key, text)

    def test_the_keys_carry_both_sources_with_dates(self):
        """Provenance must name what established the fact, and when — INV-080.

        Both are kept deliberately: `response_schemas` is now the authority, and the
        2026-07-28 dump on SDK 4.3.3 is corroboration. Dropping the dump would lose the
        record of how the names were found before the server documented them.
        """
        text = flat(CONTRACT)
        self.assertRegex(text, r"dump on SDK 4\.3\.3, 2026-07-28|dump-confirmed on SDK 4\.3\.3")
        self.assertRegex(text, r"MCP server 1\.32\.2, 2026-07-30")

    def test_the_keys_are_no_longer_marked_unconfirmable(self):
        """The negative claim went stale when the server started documenting them.

        Reversed on 2026-07-29 (dry run, phase 1). It previously asserted the contract keep
        saying "NOT in `response_schemas`" — which the live server contradicts, so the test
        was holding a false premise in place. INV-080 requires accurate provenance, not
        permanent caution.
        """
        self.assertNotRegex(
            flat(CONTRACT),
            r"NOT in `response_schemas`|not MCP-confirmable",
            "response_schemas documents these fields on 1.32.1",
        )

    def test_the_dump_requirement_survives_the_documentation(self):
        """Documented keys are an expectation to check, not a licence to skip the dump."""
        self.assertRegex(
            flat(CONTRACT), r"(?i)dump one element and use what is actually there"
        )

    def test_a_mismatch_is_reported_rather_than_coded_around(self):
        self.assertRegex(flat(CONTRACT), r"the table is stale|report it rather than coding")

    def test_the_discover_step_points_at_the_recorded_keys(self):
        text = flat(DISCOVER)
        self.assertIn("MIN_ENTITY_ID", text)
        self.assertRegex(text, r"(?i)MCP-confirmed names rather than an unverified caution")
        self.assertRegex(text, r"(?i)Run the lookup and dump anyway")


class TheJsonDataTrapIsRecorded(unittest.TestCase):
    """A documented path the documented method cannot return.

    `response_schemas` for get_entity lists `RECORDS[].JSON_DATA.*`, but the flag
    that produces `JSON_DATA` reports `applies_to: ["get_record"]` — so a viewer
    built on the documented paths renders blank for every record, against a loaded
    database. Both halves re-verified against the live server 2026-07-28.
    """

    def test_the_contract_states_json_data_is_get_record_only(self):
        self.assertRegex(
            flat(CONTRACT),
            r"`JSON_DATA` is `get_record`-only",
            "the trap must be stated where a reader looks up response shapes",
        )

    def test_the_producing_flag_and_its_applies_to_are_named(self):
        text = flat(CONTRACT)
        self.assertIn("SZ_ENTITY_INCLUDE_RECORD_JSON_DATA", text)
        self.assertRegex(text, r'applies_to: \["get_record"\]')

    def test_the_contract_warns_the_reference_itself_misleads(self):
        """The point of the entry: the authoritative source is the wrong one here."""
        self.assertRegex(
            flat(CONTRACT),
            r"reference is the thing that misleads|lists per-record source-value paths",
        )

    def test_the_obtainable_alternative_is_named_with_its_flag(self):
        text = flat(CONTRACT)
        self.assertRegex(text, r"RECORDS\[\]\.FEATURES\.<TYPE>\[\]\.ATTRIBUTES")
        self.assertIn("SZ_ENTITY_INCLUDE_RECORD_FEATURE_DETAILS", text)

    def test_the_alternative_is_not_claimed_to_be_identical_to_json_data(self):
        """ATTRIBUTES are mapped feature values; JSON_DATA is the raw loaded record."""
        self.assertRegex(
            flat(CONTRACT),
            r"mapped\*\* attributes per feature, not the raw record as loaded",
        )

    def test_the_per_record_cost_is_stated(self):
        self.assertRegex(flat(CONTRACT), r"one extra SDK call \*\*per record\*\*")

    def test_the_discover_step_carries_the_trap(self):
        text = flat(DISCOVER)
        self.assertRegex(text, r"JSON_DATA")
        self.assertIn("SZ_ENTITY_INCLUDE_RECORD_FEATURE_DETAILS", text)


if __name__ == "__main__":
    unittest.main()
