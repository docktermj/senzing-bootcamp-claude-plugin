"""A rate-limited CORD download was saved as the source's data file.

Fetching the four sources of a generated `las-vegas` scenario back to back trips a rate
limit on the download endpoint, and the limit message arrives **as the response body** —
43 bytes of English prose written into the file being saved. Reproduced live twice in one
four-source fetch (server 1.32.9, 2026-08-12): `OPEN-OWNERSHIP` and `US-LABOR-VIOLATIONS`
each landed as a one-line file whose single line is prose, while `PPP_LOANS` and `GLEIF`
came back whole.

Two facts make the fix what it is, and both were established against the live server
rather than taken from the spec:

- The throttled response **does** carry HTTP **429**. It is machine-readable, so a status
  check is the decisive test — but `curl -sS -o file url` exits 0 and writes the prose body
  anyway, so it is caught only by asking for the status.
- `download_url` caps at `download_url_max_records` (10,000). `NOMINO-RISK`, whose MCP
  `record_count` is 14,119, returns exactly 10,000 records. So a bare equality check against
  `record_count` would fail 6 of the 11 `las-vegas` sources for no reason; the expected count
  is `min(record_count, cap)` for a `download_url` fetch and `record_count` exactly for a
  `source_download_url` fetch.

The condition itself needs the network, which no offline test has. What is pinned here is
the *instruction*: the count comparison, the 429/backoff handling, and the staging rule that
keeps an unverified fetch out of `data/raw/` under the source's final name.

Enforces **INV-203** (a fetched source reaches `data/raw/` under its final name only after
**both** a 2xx status and a measured record count equal to the expected one, with a
throttled response retried rather than saved as data), which names this file.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_04 = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" / "module-04-data-collection" / "SKILL.md"

ANCHOR = '<a id="cord-fetch-integrity"></a>'


def flat(path):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    return re.sub(r"\s+", " ", text)


def canonical_block():
    """The fetch-integrity block alone, so language-agnostic checks are scoped to it."""
    text = MODULE_04.read_text(encoding="utf-8")
    start = text.index(ANCHOR)
    end = text.index("**If the bootcamper declines CORD data**", start)
    return re.sub(r"\s+", " ", text[start:end])


class TheRuleHasOneCanonicalHome(unittest.TestCase):
    """This repo's convention: one anchored statement, referenced rather than restated."""

    def test_the_canonical_block_has_an_anchor(self):
        self.assertIn(ANCHOR, MODULE_04.read_text(encoding="utf-8"))

    def test_it_declares_itself_canonical(self):
        self.assertIn("canonical statement; do not restate it elsewhere", flat(MODULE_04))

    def test_the_consumers_reference_it_rather_than_restate(self):
        text = MODULE_04.read_text(encoding="utf-8")
        refs = text.count("(#cord-fetch-integrity)")
        self.assertGreaterEqual(
            refs,
            3,
            "the generated-scenario fetch path, the registry schema and Data File Validation must all link it",
        )


class TheRateLimitCaseIsNamedAndHandled(unittest.TestCase):
    """The plugin had no rate-limit awareness at all before this."""

    def test_the_throttled_body_is_quoted_verbatim(self):
        self.assertIn("Rate limit exceeded. Try again in 1 second.", flat(MODULE_04))

    def test_the_response_is_named_as_arriving_as_the_body(self):
        self.assertRegex(flat(MODULE_04), r"(?i)comes back \*\*as the response body\*\*")

    def test_the_429_status_is_the_decisive_check(self):
        block = canonical_block()
        self.assertRegex(block, r"HTTP \*\*429\*\*")
        self.assertRegex(block, r"(?i)Anything outside 2xx is a \*\*failed fetch\*\*")

    def test_the_silent_curl_trap_is_called_out(self):
        """A status check is only decisive if the reader knows it must be requested."""
        block = canonical_block()
        self.assertRegex(block, r"(?i)exits \*\*0\*\* and")
        self.assertRegex(block, r"--fail")

    def test_retry_with_backoff_is_instructed(self):
        self.assertRegex(canonical_block(), r"(?i)retry with a short backoff")

    def test_sequential_fetches_are_spaced(self):
        self.assertRegex(canonical_block(), r"(?i)pause between sequential source fetches")


class TheCountComparisonIsPrescribed(unittest.TestCase):
    """"Plausible record count" was a judgement; the decisive figure was already in hand."""

    def test_the_expected_count_comes_from_the_mcp_source_listing(self):
        self.assertRegex(canonical_block(), r"source='list'\)` returns `record_count` per source")

    def test_a_mismatch_fails_the_collection_rather_than_warning(self):
        self.assertRegex(canonical_block(), r"\*\*failed collection, not a warning\*\*")

    def test_the_capped_case_uses_min_rather_than_bare_equality(self):
        """A bare equality check would fail 6 of 11 las-vegas sources."""
        block = canonical_block()
        self.assertIn("min(record_count, download_url_max_records)", block)
        self.assertRegex(block, r"(?i)expect exactly `record_count`")

    def test_plausibility_is_explicitly_rejected(self):
        self.assertRegex(canonical_block(), r"(?i)\"plausible record count\" is a judgement")

    def test_data_file_validation_requires_a_match_not_a_plausibility_call(self):
        self.assertRegex(flat(MODULE_04), r"(?i)a record count that \*\*matches\*\* it rather than one that merely looks plausible")


class AnUnverifiedFetchNeverReachesItsFinalName(unittest.TestCase):
    def test_it_stages_inside_the_project(self):
        block = canonical_block()
        self.assertIn("data/temp/<source>.jsonl", block)
        self.assertIn("INV-200", block)

    def test_the_move_is_gated_on_the_checks(self):
        self.assertRegex(canonical_block(), r"(?i)only once checks 1 and 2 pass")

    def test_system_temp_is_refused(self):
        self.assertRegex(canonical_block(), r"(?i)never uses system temp")


class BothCountsAreRecorded(unittest.TestCase):
    """Step 7 can only confirm what the registry entry recorded."""

    def test_the_registry_schema_carries_the_expected_count(self):
        self.assertIn("`expected_record_count`", flat(MODULE_04))

    def test_the_measured_count_is_no_longer_optional(self):
        text = flat(MODULE_04)
        self.assertNotIn("`record_count` (if known, else null)", text)
        self.assertRegex(text, r"(?i)`record_count` \(the count you \*\*measured\*\*")

    def test_both_checks_are_named_for_validation_checks(self):
        block = canonical_block()
        self.assertIn("http_status_ok", block)
        self.assertIn("record_count_matches_expected", block)


class TheDownloadCapIsNotMisdescribed(unittest.TestCase):
    """`download_url` was presented as "the full JSONL file"; it is a 10,000-record slice."""

    def test_the_two_urls_are_distinguished(self):
        text = flat(MODULE_04)
        self.assertIn("`download_url_max_records`", text)
        self.assertIn("`source_download_url`", text)

    def test_the_cap_is_stated(self):
        self.assertRegex(flat(MODULE_04), r"at most `download_url_max_records` records per request — \*\*10,000\*\*")

    def test_download_url_is_not_called_the_full_file(self):
        text = flat(MODULE_04)
        self.assertNotIn("so the bootcamper can download the full JSONL file", text)
        self.assertIn('is **not** "the full file"', text)

    def test_the_measured_cap_case_is_cited(self):
        text = flat(MODULE_04)
        self.assertIn("14,119", text)
        self.assertRegex(text, r"returned exactly 10,000 records")


class TheCheckStaysLanguageAgnostic(unittest.TestCase):
    """INVARIANTS.md: language-agnostic. A count is not a shell idiom."""

    def test_no_shell_line_count_pipeline_is_prescribed(self):
        block = canonical_block()
        for idiom in ("wc -l", "wc -c", "| grep -c"):
            self.assertNotIn(idiom, block, f"{idiom} would make the count check shell-only")

    def test_it_says_the_count_is_language_neutral(self):
        self.assertRegex(canonical_block(), r"(?i)in whatever language the Bootcamper chose")

    def test_windows_is_covered_alongside_the_posix_route(self):
        self.assertIn("Invoke-WebRequest", canonical_block())


class TheProvenanceIsStamped(unittest.TestCase):
    """Any Senzing fact written into the plugin carries tool, version and date (INV-080)."""

    def test_the_server_version_and_date_accompany_the_facts(self):
        block = canonical_block()
        self.assertIn("1.32.9", block)
        self.assertIn("2026-08-12", block)

    def test_the_establishing_call_is_named_for_the_two_urls(self):
        self.assertRegex(flat(MODULE_04), r"get_sample_data\(dataset='las-vegas', source='GLEIF', limit=1\)")


if __name__ == "__main__":
    unittest.main()
