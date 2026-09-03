"""A negative marker's rationale must not rest on a count, or on an enumerated name-list.

MCP-NEGATIVE-SCAN: ignore-file — the marker strings below are synthetic scratch-tree
fixtures for the reporter, not claims about any server. They are written as concatenated
Python literals, so the token lands on a line whose `owner:` clause is on the next one, and
the scanner correctly reads that as a MALFORMED marker — which is how this was found, by
the very guard the fixtures exercise. Same route as `tests/test_coverage_reports.py`.

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


class TheEnumerationDetectorFlagsANameList(unittest.TestCase):
    """The shape a numeral cannot express, and which `find_census_rationales` cannot see.

    An enumerated name-list expires for exactly the reason a count does -- a rename, a drop
    or an addition falsifies it server-side, silently, because phase 1 re-asks the CLAIM and
    never the rationale. It was named as an observed drift cause in the detector's own comment
    on 2026-08-31 and left unimplemented; on 2026-09-02 it drifted again undetected.
    """

    def setUp(self):
        self.reports = load_reports()

    def test_the_shipped_drifted_phrasing_is_flagged(self):
        """`phase2-data-mapping.md:719`, verbatim -- the instance that went undetected.

        On server 1.36.0, 2026-09-02 that route returns *Payload attributes (optional)*,
        *Attributes for the record key* and *Attribute reference*. There is no
        *Mapping identifiers* section in the response at all.
        """
        owner = (
            "search_docs over the Entity Specification IS the route that would carry such a "
            "precedence rule, and it returned the *Payload attributes (optional)* and "
            "*Mapping identifiers* sections, which establish that payload and registered "
            "features are distinct categories (absence negative)"
        )
        self.assertTrue(
            self.reports.find_enumeration_rationales([row("no such rule", owner=owner)]),
            "A rationale naming the sections the route returned must be flagged. This exact "
            "text cited a section the server does not return, while the claim above it stayed "
            "true and the date certified the whole comment as checked.",
        )

    def test_the_property_shaped_rewrite_is_not_flagged(self):
        """What the correction must look like -- and why re-listing is not a fix.

        Replacing one section name with the currently-returned three would leave the rationale
        flagged, correctly: the next server-side rename breaks it again. The discriminating
        property is what the enumeration was standing in for.
        """
        owner = (
            "search_docs over the Entity Specification IS the route that would carry such a "
            "precedence rule; its payload and feature-attribute sections establish that the "
            "two are distinct categories and that choosing between them is a mapping "
            "decision, but none states a precedence for a colliding root-level key "
            "(absence negative)"
        )
        self.assertFalse(
            self.reports.find_enumeration_rationales([row("no such rule", owner=owner)]),
            "A rationale stating the PROPERTY the list stood in for must not be flagged -- "
            "otherwise the report gives the fixer nowhere to land.",
        )

    def test_a_corrected_enumeration_is_still_flagged(self):
        """Re-listing the current sections is a re-date in disguise, and must still report."""
        owner = (
            "search_docs IS the route, and it returned the *Payload attributes (optional)*, "
            "*Attributes for the record key* and *Attribute reference* sections "
            "(absence negative)"
        )
        self.assertTrue(
            self.reports.find_enumeration_rationales([row("no such rule", owner=owner)]),
            "Swapping today's section names in keeps the liability: the rationale is still "
            "falsified by the next rename. The report must not go quiet on it.",
        )

    def test_the_noun_may_govern_from_either_side(self):
        for owner in (
            "the response carries the fields `file_path` and `raw_url` (routing negative)",
            "it returned the *Alpha* and *Beta* sections (absence negative)",
        ):
            with self.subTest(owner=owner[:40]):
                self.assertTrue(
                    self.reports.find_enumeration_rationales([row("x", owner=owner)]),
                    "Both phrasings ship; a matcher that reads only one direction misses half.",
                )


class TheEnumerationDetectorLeavesLegitimateListsAlone(unittest.TestCase):
    """⛔ Three of the four enumerations in the corpus on 2026-09-02 were LEGITIMATE.

    An exhaustive list IS the discriminating fact of an absence claim -- "no `brew upgrade`
    anywhere; what it does carry is ..." -- so this half of the discrimination carries more
    weight here than for the count matcher. INV-282's lesson: every construction the detector
    must NOT flag is pinned beside the ones it must, so a later widening fails here rather
    than being absorbed as a louder report.
    """

    def setUp(self):
        self.reports = load_reports()

    def test_a_property_with_examples_is_not_flagged(self):
        """`module-02-sdk-setup/SKILL.md:387`, verbatim. The spec names this must-not-flag.

        ⚠️ It has the verb, and a coordinated snake_case run, and an element noun in the
        clause -- so a presence-in-clause test flags it, which the first implementation did.
        `entry` governs `upgrade`, in a different conjunct; the run is examples under the
        property word `material`. That is why `_governing_noun` tests the gap for a
        coordinator rather than only its width.
        """
        claim = (
            "no 4.x-to-4.y update procedure anywhere; every hit is V3-to-V4 migration "
            "material (sz_dbupgrade, sz_configupgrade, breaking-changes, Migration.md) "
            "and the topic list carries no upgrade entry"
        )
        self.assertFalse(
            self.reports.find_enumeration_rationales([row(claim)]),
            "A property over whatever came back, with examples, must not be flagged. It "
            "survives a rebuild, which is the whole distinction this report is drawing.",
        )

    def test_the_exhaustive_command_lists_are_not_flagged(self):
        """`SKILL.md:252` (brew) and `:278` (scoop), verbatim -- the legitimate use.

        The list is the discriminating fact of the absence: no version-management command
        anywhere, and here is what the response does carry instead. Both reproduced exactly
        on server 1.36.0, 2026-09-02.
        """
        shipped = [
            "no brew outdated, brew info or brew upgrade anywhere in the response; the brew "
            "commands it does carry are tap, trust, install --cask, uninstall --cask, untap, "
            "install/link libpq, and --prefix",
            "no scoop status, scoop info or scoop update anywhere in the response; the scoop "
            "commands it does carry are bucket add, install, and config (for the EULA variable)",
        ]
        for claim in shipped:
            with self.subTest(claim=claim[:48]):
                self.assertFalse(
                    self.reports.find_enumeration_rationales([row(claim)]),
                    "An exhaustive list of bare command words is the fact itself. Flagging "
                    "it trains the reader to skip the report.",
                )

    def test_a_trailing_field_noun_is_not_treated_as_governing(self):
        """`phase1-verification.md:251`, verbatim -- and the detector's known blind spot.

        ⚠️ This one is honestly uncomfortable: it IS an exhaustive field list, the shape the
        comment names as a 2026-08-31 drift cause, and it reproduced exactly on 1.36.0. It is
        left unflagged because `field` trails in a separate conjunct, the same structure that
        keeps `:387` out. The trade is stated in `find_enumeration_rationales`' docstring
        rather than left for a reader to infer from silence.
        """
        claim = (
            "its snippets[] carry file_path, source_url, repo, raw_url, size_bytes and "
            "line_count with no content field at all"
        )
        self.assertFalse(
            self.reports.find_enumeration_rationales([row(claim)]),
            "Pinned as the CURRENT behavior, not as an endorsement. If this phrasing drifts, "
            "widen _governing_noun -- do not drop the coordinator test.",
        )

    def test_a_tool_calls_own_parameters_are_not_an_enumeration(self):
        """⚠️ The claim half INCLUDES the invocation, so this would flag nearly every marker.

        `search_docs(query='...', category='data_mapping')` hands the matcher two snake_case
        tokens and, with a `section` noun anywhere nearby, a hit -- for free, on every marker
        that happens to be a `search_docs` negative. Found while designing the matcher; the
        report would have been useless on its first run.
        """
        claim = (
            "search_docs(query='payload attribute precedence', category='data_mapping') "
            "— no indexed section states what happens at the record root"
        )
        self.assertFalse(
            self.reports.find_enumeration_rationales([row(claim)]),
            "A call's own parameters enumerate nothing about the response.",
        )

    def test_all_caps_prose_is_not_a_pair_of_named_elements(self):
        self.assertFalse(
            self.reports.find_enumeration_rationales(
                [row("the response MUST and NEVER carry a section key", owner="whatever")]
            ),
            "ALL-CAPS prose words are not response elements; counting them manufactures a "
            "coordinated pair out of emphasis.",
        )


class TheTwoReportersStayDistinct(unittest.TestCase):
    """Neither block may absorb the other's hits, or the report double-counts."""

    def setUp(self):
        self.reports = load_reports()

    def test_a_count_is_not_reported_as_an_enumeration(self):
        self.assertFalse(
            self.reports.find_enumeration_rationales([row("both results are SDK examples")]),
            "A count belongs under the census label, which prescribes a different fix.",
        )

    def test_an_enumeration_is_not_reported_as_a_count(self):
        owner = "it returned the *Alpha* and *Beta* sections (absence negative)"
        self.assertFalse(
            self.reports.find_census_rationales([row("x", owner=owner)]),
            "An enumeration carries no numeral; if the census matcher claims it, the count "
            "report stops meaning what its own preamble says.",
        )


class TheReportSeparatesTheTwoShapes(unittest.TestCase):
    """Criterion 3, asserted against real output on a SYNTHETIC tree.

    ⚠️ Driven from fixtures rather than the live repo on purpose. The first version of this
    class read the shipped tree, which made it assert a CONTINGENT fact -- that hits exist --
    so it would have failed the moment `restamp-27-mcp-negatives-to-server-1-36-0` corrected
    the last enumeration, for a good reason and with a bad message. "Both labels appear when
    both shapes are present" is the durable property; "the tree currently has a hit" is a
    separate claim, below, and is marked as expected to invert.
    """

    MARKERS = (
        "<!-- MCP-NEGATIVE: search_docs(query='a') — no such thing; both results are SDK "
        "examples — owner: search_docs IS the route (absence negative) — server 1.36.0, "
        "2026-09-02 -->\n"
        "<!-- MCP-NEGATIVE: search_docs(query='b') — no such rule — owner: search_docs IS "
        "the route, and it returned the *Alpha* and *Beta* sections (absence negative) — "
        "server 1.36.0, 2026-09-02 -->\n"
    )

    def _report(self, text):
        import contextlib
        import io
        import tempfile

        reports = load_reports()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "plugins"
            root.mkdir()
            (root / "fixture.md").write_text(text, encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                reports.report_negatives(tmp, None)
            return buf.getvalue()

    def test_both_labels_and_both_judgment_notes_are_printed(self):
        out = self._report(self.MARKERS)
        self.assertIn("CENSUS-SHAPED rationales", out)
        self.assertIn("ENUMERATION-SHAPED rationales", out)
        self.assertEqual(
            2, out.count("A hit needs judgment"),
            "Each block carries its own judgment note. One shared note lets a reader apply "
            "the count block's reasoning to an enumeration, where the legitimate-use rate "
            "is much higher -- three of four in the corpus on 2026-09-02.",
        )

    def test_each_shape_is_listed_under_its_own_label_only(self):
        """A hit under the wrong label prescribes the wrong fix: re-describe vs re-ask."""
        out = self._report(self.MARKERS)
        census = out.split("CENSUS-SHAPED rationales", 1)[1].split("ENUMERATION-SHAPED", 1)[0]
        # ⚠️ Bound the tail at the marker listing. Without this the block runs to end of
        # output and picks up both markers' verbatim text from the listing below, which
        # made this assertion pass-by-accident in one direction and fail in the other.
        enumerated = out.split("ENUMERATION-SHAPED rationales", 1)[1].split("\nmarkers:", 1)[0]
        self.assertIn("'both results'", census)
        self.assertNotIn("Alpha", census)
        self.assertIn("*Alpha* and *Beta*", enumerated)
        self.assertNotIn("both results", enumerated)

    def test_the_report_stays_quiet_when_no_rationale_has_either_shape(self):
        """Neither block may print on a clean tree, or the labels stop carrying information."""
        clean = (
            "<!-- MCP-NEGATIVE: search_docs(query='c') — the topic list carries no upgrade "
            "entry — owner: search_docs IS the corpus route and it is empty (absence "
            "negative) — server 1.36.0, 2026-09-02 -->\n"
        )
        out = self._report(clean)
        self.assertNotIn("CENSUS-SHAPED", out)
        self.assertNotIn("ENUMERATION-SHAPED", out)


class NoShippedMarkerPinsAnEnumeration(unittest.TestCase):
    """The state `restamp-27-mcp-negatives-to-server-1-36-0` established, asserted against the tree.

    ⛔ **This class REPLACED an inverted one, and the replacement is the point.** While the drift
    was live, `TheDriftedSiteIsFlaggedUntilItIsCorrected` asserted that
    `phase2-data-mapping.md:719` WAS flagged -- criterion 1's first half. Its failure message named
    the two causes a later silence could have (rationale corrected, or matcher regressed) and said
    to flip it once the first applied. On 2026-09-02 the restamp corrected that rationale, the guard
    failed with exactly that message, and the detector returned an empty list while all twenty
    fixture-driven assertions still passed -- which is what distinguished (a) from (b). Flipped.

    ⚠️ Scoped to ``plugins/`` for the same reason `NoShippedMarkerPinsACount` is: ``specs/DECLINED.md``
    carries a marker and is a RECORD of a decision already taken, so rewriting its evidence is the
    maintainer's call rather than a guard's. Its census WAS corrected in the same change and it is
    clean today; the report still lists it, and this test still does not.
    """

    def test_no_marker_under_plugins_pins_an_enumeration(self):
        reports = load_reports()
        found = [r for r in reports.find_negatives(str(REPO)) if r[5].startswith("plugins")]
        self.assertTrue(found, "No markers found under plugins/ -- has the scan broken?")
        flagged = reports.find_enumeration_rationales(found)
        self.assertEqual(
            [], flagged,
            "A shipped marker's rationale enumerates named response elements as what the route "
            "returned. Re-ask the owning route and replace the list with the PROPERTY it stands "
            "in for -- re-listing today's names is a re-date in disguise and keeps the liability, "
            "because the next server-side rename falsifies it again:\n  "
            + "\n  ".join("%s:%d — %r" % f for f in flagged),
        )


if __name__ == "__main__":
    unittest.main()
