"""`szBuildVersion.json`'s location is attributed per platform, never by one blanket caveat.

MCP-NEGATIVE-SCAN: ignore-file — this file quotes the `MCP-NEGATIVE:` token as a LOCATOR, to
find the real marker in module-02's SKILL.md and assert its `owner:` clause. Those string
literals are matchers, not dated claims, so the scanner would otherwise report them as
malformed markers. The absence claims in the docstring below are the same ones that marker
already carries, and it is the marker — not this test — that sits on the re-ask worklist.

Module 2 gives the fallback route for reading the SDK build version and then labels its own
provenance. The label was a single ⚠️ spanning all three platforms — *"environment
observations, not MCP-sourced facts"* — written 2026-08-13 against server 1.32.9, when no MCP
route carried any `szBuildVersion.json` location. It was accurate then.

The server has since gained the **Windows** path: `sdk_guide(topic='install',
platform='windows')` names `szBuildVersion.json` among the support data under
`<scoop-app-dir>\\data` (verified server 1.35.3, 2026-09-01). Because the caveat was phrased
per-paragraph rather than per-platform, there was no way for it to become half-true — it
simply became wrong for one platform while reading as though it had been reviewed.

⚠️ Why this matters more than a stale note usually would: INV-080 routes every Senzing fact
through the MCP server, and this ⚠️ is what tells a reader which side of that line a statement
sits on. Mislabeling a served fact as a local observation degrades both ways — a guide hitting
a mismatch has no reason to re-ask the server, and a reader who trusts the ⚠️ discounts a path
the server would confirm. This paragraph is the fallback reached *after* the SDK route fails,
so it is consulted exactly when the Bootcamper is already stuck.

Verified 2026-09-01, server 1.35.3, all three routes asked:
    windows    -> names szBuildVersion.json in gotchas[]            (MCP-sourced)
    linux_apt  -> names it nowhere; observed on-box at 4.4.0.26242  (observation)
    macos_arm  -> names it nowhere; support data listed without it  (unknown)

Enforces **INV-285** — a provenance label covering several independently-moving facts is
stated per fact, each with its own route and date.

⚠️ What this asserts is that the per-platform attribution **ships**, not that a live turn
obeys it. An ``Enforced by`` clause naming this file is a claim about the text, and the
guide's behavior at that step is `dry-run` phase 3's to observe.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = (REPO / "plugins" / "senzing-bootcamp" / "skills" /
         "module-02-sdk-setup" / "SKILL.md")


def provenance_block():
    """From the build-metadata sentence to the end of the per-platform list."""
    text = SKILL.read_text(encoding="utf-8")
    start = text.find("in `szBuildVersion.json`")
    assert start != -1, "the build-metadata paragraph was not found -- reworded?"
    end = text.find("<!-- MCP-NEGATIVE:", start)
    assert end != -1, "the MCP-NEGATIVE marker that follows the paragraph was not found"
    return text[start:end]


def flat(s):
    return re.sub(r"\s+", " ", s)


class ProvenanceIsStatedPerPlatform(unittest.TestCase):
    def setUp(self):
        self.block = flat(provenance_block())

    def test_the_three_platforms_are_attributed_separately(self):
        """The spec's fifth criterion, and the whole point: one blanket caveat cannot age well."""
        for platform in ("Windows", "Linux", "macOS"):
            with self.subTest(platform=platform):
                self.assertRegex(
                    self.block, r"\*\*%s —" % platform,
                    "Each platform must carry its own provenance. A single caveat spanning all "
                    "three has no way to become half-true: when the server gained the Windows "
                    "path, the note became wrong for one platform while still reading as "
                    "reviewed.",
                )

    def test_windows_is_attributed_to_the_mcp_route_that_serves_it(self):
        self.assertRegex(
            self.block,
            r"(?i)Windows — MCP-sourced",
            "Windows must no longer sit under 'environment observations'. The server states "
            "the path outright, and mislabeling a served fact as a local observation removes "
            "the reader's reason to re-ask the authority.",
        )
        self.assertRegex(
            self.block, r"sdk_guide\(topic='install', platform='windows'\)",
            "The Windows attribution must name the route that serves it, so a reader can "
            "re-ask it rather than trusting this file.",
        )

    def test_linux_stays_an_observation_and_says_so(self):
        self.assertRegex(
            self.block, r"(?i)Linux — environment observation",
            "Linux is still an observation — no MCP route states it — and must stay labeled "
            "as one (INV-149). Promoting it on the strength of the Windows change would be "
            "the same defect in the other direction.",
        )
        self.assertRegex(
            self.block, r"4\.4\.0\.\d+",
            "The Linux observation must name the build it was observed against; the previous "
            "note said only 'Linux observed 2026-08-13' with no version.",
        )

    def test_macos_stays_unknown_and_names_the_route_that_was_asked(self):
        self.assertRegex(
            self.block, r"(?i)macOS — unknown",
            "macOS must stay unknown — the route was asked and does not carry it.",
        )
        self.assertRegex(
            self.block, r"sdk_guide\(topic='install', platform='macos_arm'\)",
            "The macOS entry must name the route that was asked and came back without it, so "
            "the next reader does not re-ask the same question blind (INV-194).",
        )

    def test_every_platform_claim_carries_a_date(self):
        dates = re.findall(r"20\d\d-\d\d-\d\d", self.block)
        self.assertGreaterEqual(
            len(dates), 3,
            "Each platform's provenance must carry its own date. A shared date is how the "
            "Windows half stayed stamped with a review it never had. Found: %r" % (dates,),
        )

    def test_the_server_version_is_named(self):
        self.assertRegex(
            self.block, r"1\.35\.\d",
            "The MCP-sourced claims must name the server version they were verified against "
            "(INV-080).",
        )


class TheNegativeMarkerStillAssertsItsClaim(unittest.TestCase):
    """The spec's fourth criterion: extend the owner clause, never weaken the claim."""

    def setUp(self):
        text = SKILL.read_text(encoding="utf-8")
        i = text.index("<!-- MCP-NEGATIVE: search_docs(query='szBuildVersion.json")
        self.marker = flat(text[i: text.index("-->", i)])

    def test_the_search_docs_claim_is_unchanged(self):
        self.assertRegex(
            self.marker, r"(?i)no indexed document gives that file's path on any platform",
            "The `search_docs` claim still holds and must not be weakened. It is scoped to "
            "the corpus route, and the corpus still returns no file location — the Windows "
            "fact is served by a different tool.",
        )

    def test_the_owner_clause_records_the_route_that_does_serve_windows(self):
        self.assertRegex(
            self.marker, r"(?i)the Windows path IS served",
            "The owner clause must record that Windows is served elsewhere. Left as-is it is "
            "not wrong but INCOMPLETE, and an incomplete owner clause sends the next re-check "
            "to conclude the fact is unavailable on every platform.",
        )
        self.assertRegex(
            self.marker, r"platform='windows'",
            "The owner clause must name the serving route, not merely allude to it.",
        )


if __name__ == "__main__":
    unittest.main()
