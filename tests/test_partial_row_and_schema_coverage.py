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

⛔ These tests deliberately do NOT assert any specific endpoint field name. The
normalized low-to-high keys reported in that session are not in
`response_schemas` and not in the indexed docs, so the plugin must not code
against them — INV-080 forbids shipping an unverified Senzing fact, and this repo
has already had to correct a spec that asserted one (`SZ_EXPORT_ALL_FLAGS does
not exist`). What is asserted here is the *discipline*: dump the element, and
treat a blank field as a wrong name.

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

    def test_the_contract_says_the_graph_entry_stops_at_the_top_level(self):
        self.assertRegex(
            flat(CONTRACT),
            r"documents only the three arrays above|no element fields",
            "the entry exists but does not reach the link element's fields — a reader "
            "who does not know that thinks the lookup answered the question",
        )

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

    def test_the_endpoint_keys_are_not_presented_as_the_names_to_use(self):
        text = flat(CONTRACT)
        if "MIN_ENTITY_ID" in text:
            self.assertRegex(
                text,
                r"not MCP-confirmable|never as the field names to code against",
                "if the reported keys are named at all they must be marked unverified, "
                "never given as the names to parse with",
            )

    def test_the_caution_is_framed_as_where_to_look(self):
        self.assertRegex(
            flat(CONTRACT),
            r"warning about where to look",
            "the value of the report is that endpoints may not use the pairing you "
            "expect — not the specific keys, which were never confirmed",
        )

    def test_the_reader_is_told_to_use_what_is_actually_there(self):
        self.assertRegex(flat(CONTRACT), r"use what is actually there")


if __name__ == "__main__":
    unittest.main()
