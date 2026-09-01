"""A negative marker's rationale must not rest on a count.

An ``MCP-NEGATIVE`` marker has two halves that age at different rates: the **claim**
("tool X does not contain Y"), which `/dry-run` phase 1 re-asks, and the **rationale** --
the ``owner:`` clause plus the detail saying why the claim is the answer rather than a
miss. Nothing re-asks the rationale, so it can quietly stop describing the response while
the claim above it stays true and the date certifies the whole comment as checked.

On 2026-08-31 all 25 DUE claims still held and **three rationales did not reproduce**. Two
of the three had pinned a **count** -- "all four hits are …" (ten hits by then) and an
exhaustive field list (a field had since been added). A count is never the discriminating
fact; it is a stand-in for one. "No field names a binding type" says what the census was
standing in for, and does not expire when the index is rebuilt.

⚠️ This guard asserts the DETECTOR discriminates, not merely that it matches something:
census fixtures must be flagged AND property-shaped fixtures must not. A detector that
flags everything would satisfy a one-sided test while making the report useless.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPORTS = REPO / ".claude" / "skills" / "dry-run" / "coverage_reports.py"


def load_reports():
    spec = importlib.util.spec_from_file_location("coverage_reports", REPORTS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(claim, owner="whatever route (routing negative)"):
    """A find_negatives()-shaped row: (key, version, date, claim, owner, path, lineno)."""
    return ((1, 35, 3), "1.35.3", "2026-09-01", claim, owner, "fixture.md", 1)


class TheDetectorFlagsACensus(unittest.TestCase):
    """Every phrasing that has actually shipped is pinned here as a fixture."""

    def setUp(self):
        self.reports = load_reports()

    def test_the_historical_phrasings_are_flagged(self):
        shipped = [
            "no indexed document gives that file's path; all four hits are get_version() examples",
            "no 4.x-to-4.y procedure anywhere; all six hits are V3-to-V4",
            "returns no globalization content at all, all five hits being repo template files",
            "the corpus returns 10 hits and none of them names the file",
            "both results are SDK examples",
        ]
        for claim in shipped:
            with self.subTest(claim=claim[:48]):
                self.assertTrue(
                    self.reports.find_census_rationales([row(claim)]),
                    "A rationale pinning a count must be flagged for re-description. This is "
                    "the shape that stopped reproducing twice on 2026-08-31 while the claim "
                    "beside it stayed true.",
                )

    def test_a_census_in_the_owner_clause_is_flagged_too(self):
        """The owner clause is a rationale as well, and is the load-bearing half."""
        self.assertTrue(
            self.reports.find_census_rationales(
                [row("no such field", owner="the parameters topic, whose three rows all differ")]
            ),
            "A count in the `owner:` clause must be flagged. The owner clause is what a later "
            "reader acts on when deciding whether a routing conclusion still stands, so a stale "
            "census there costs more than one in the claim.",
        )


class TheDetectorLeavesAPropertyAlone(unittest.TestCase):
    """⚠️ The other half of the discrimination -- a detector that flags everything is noise.

    INV-282's lesson applied to this matcher: every construction it must NOT flag is
    pinned beside the ones it must, so a later widening that starts flagging correct
    rationales fails here rather than being absorbed as a louder report.
    """

    def setUp(self):
        self.reports = load_reports()

    def test_property_shaped_rationales_are_not_flagged(self):
        good = [
            "no field on any returned row names a binding or its argument types",
            "every hit is a version-READING example or a build document, none stating where "
            "the file lives",
            "the same document carries the renamed trio at WHY_RESULTS[].MATCH_INFO",
            "returns it, as \"Address matching examples > CJK+English cross-script matching\"",
            "the topic list carries no upgrade entry",
            "the response is byte-identical with and without the language argument",
        ]
        for claim in good:
            with self.subTest(claim=claim[:48]):
                self.assertFalse(
                    self.reports.find_census_rationales([row(claim)]),
                    "A rationale stating a discriminating PROPERTY must not be flagged. "
                    "Flagging correct prose trains the reader to skip the report, which "
                    "costs more than the census it was meant to catch.",
                )

    def test_document_as_a_verb_is_not_a_census(self):
        """A shipped marker says "both document installing only …" -- two routes, one verb.

        ⚠️ Found by negative control, not by review: the detector's first version flagged
        `module-02-sdk-setup/SKILL.md:207` because `both\\s+documents?` matched a verb. The
        same verb/noun collision had to be corrected in two other guards this session, so
        it is pinned here rather than left to the next author to rediscover.
        """
        self.assertFalse(
            self.reports.find_census_rationales(
                [row("both document installing only the runtime, never the SDK")]
            ),
            "`document` is a verb here. A matcher that reads it as a result noun flags "
            "correct prose, and a report that cries wolf is one nobody opens.",
        )

    def test_a_version_number_is_not_a_census(self):
        """`server 1.35.3` and `SDK 4.4` carry digits and enumerate nothing."""
        self.assertFalse(
            self.reports.find_census_rationales(
                [row("no 4.x-to-4.y update procedure exists in the 4 corpus")]
            ),
            "A version number is not an enumeration of results. Matching bare digits would "
            "flag every marker, since each carries a server version by construction.",
        )


class NoShippedMarkerPinsACount(unittest.TestCase):
    """The state this change establishes, asserted against the tree rather than a fixture.

    ⚠️ Scoped to ``plugins/`` deliberately. ``specs/DECLINED.md`` also carries a marker,
    and it is a RECORD of a decision already taken -- rewriting its evidence is the
    maintainer's call, not a guard's. The report still lists it; this test does not.
    """

    def test_no_marker_under_plugins_rests_on_a_count(self):
        reports = load_reports()
        found = [r for r in reports.find_negatives(str(REPO)) if r[5].startswith("plugins")]
        self.assertTrue(found, "No markers found under plugins/ -- has the scan broken?")
        flagged = reports.find_census_rationales(found)
        self.assertEqual(
            [], flagged,
            "A shipped marker's rationale pins a count. Re-ask the owning route and replace "
            "the census with the property it stands in for -- do NOT simply re-date it, which "
            "certifies text nobody re-read.",
        )


if __name__ == "__main__":
    unittest.main()
