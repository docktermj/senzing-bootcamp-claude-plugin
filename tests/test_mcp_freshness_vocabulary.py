"""The MCP freshness requirement must be one rule with one name, not two vocabularies.

The plugin stated it both ways and reconciled neither. Read as "this turn", a long module
re-issues identical queries on every turn a Senzing name appears — waste, against a rule
claiming ⛔-gate precedence, so not one a careful guide economizes on. Read as "this
session", the guide presents Senzing content on a turn with no MCP call, which the
pre-response checklist in every skill file forbids and which makes that turn's "via the
Senzing MCP server" attribution untrue.

Most "this session" uses were compatible — they set a **floor on provenance** ("do not
trust the literal in this file, go ask") rather than a ceiling on caching. One was not:
`module-01-business-problem/phase1-discovery.md` said to fill the pattern gallery from
"`search_docs` content returned this session", which a prior turn's results satisfy while
the checklist forbids presenting them.

So: both rules are named and defined once in the ground rules, the floor is stated not to
relax the freshness rule, and "this session" no longer appears anywhere under `plugins/` as
a freshness claim. Uses of the phrase in its ordinary sense — ask-once scope, what to review
at graduation, when a platform was detected — are allowlisted **by their exact wording**, so
the allowlist cannot silently absorb a new freshness claim.

Source spec: `specs/mcp-freshness-contract-says-this-turn-and-this-session.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
GROUND_RULES = PLUGIN / "skills" / "bootcamp-onboarding" / "ground-rules.md"
DISCOVERY = PLUGIN / "skills" / "module-01-business-problem" / "phase1-discovery.md"

#: Words that make a nearby "this session" a claim about MCP sourcing or freshness.
MCP_VOCAB = (r"MCP|search_docs|sdk_guide|get_capabilities|get_sdk_reference|reporting_guide"
             r"|find_examples|get_sample_data|mapping_workflow|explain_error_code")

#: "this session" preceded by MCP vocabulary within one sentence.
SUSPECT = re.compile(r"(?:%s)[^.!?]{0,120}?this session" % MCP_VOCAB)

#: Ordinary-sense uses, quoted exactly. Each must still be present (see the vacuity test),
#: so a stale entry is a failure rather than dead cover for something new.
ALLOWED = (
    "do not ask again** this session or the next (INV-006)",
    "was detected earlier, this session or a prior one)",
    "tripped us up this session, so the bootcamp itself improves",
    "Review **this session** for four categories",
)


def shipped_markdown():
    return sorted(PLUGIN.rglob("*.md"))


def read(path):
    return path.read_text(encoding="utf-8")


def squash(text):
    return re.sub(r"\s+", " ", text)


def freshness_claims():
    """Every 'this session' that reads as an MCP sourcing/freshness claim."""
    found = []
    for path in shipped_markdown():
        flat = squash(read(path))
        for match in re.finditer(r"this session", flat):
            window = flat[max(0, match.start() - 130):match.end() + 60]
            if any(squash(allowed) in window for allowed in ALLOWED):
                continue
            if SUSPECT.search(window):
                found.append("%s: …%s…" % (path.relative_to(REPO_ROOT), window))
    return found


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_corpus_is_found(self):
        self.assertGreater(len(shipped_markdown()), 30,
                           "the shipped markdown corpus was not found")

    def test_the_pattern_matches_the_wording_that_shipped(self):
        """The exact sentence this spec removed must still trip the scanner."""
        regressed = squash(
            "Fill those four from **`search_docs` content returned this session** — never "
            "from memory.")
        self.assertIsNotNone(
            SUSPECT.search(regressed),
            "the scanner does not recognize the phrasing it exists to catch, so a clean "
            "run proves nothing")

    def test_every_allowlisted_phrase_is_still_present_somewhere(self):
        corpus = " ".join(squash(read(p)) for p in shipped_markdown())
        for allowed in ALLOWED:
            with self.subTest(phrase=allowed[:40]):
                self.assertIn(squash(allowed), corpus,
                              "an allowlisted ordinary-sense phrase no longer exists; "
                              "remove it rather than leaving it as cover for new text")


class NoFileUsesThisSessionAsAFreshnessClaim(unittest.TestCase):
    def test_the_scan_is_clean(self):
        found = freshness_claims()
        self.assertEqual(
            [], found,
            "a shipped file ties an MCP tool to 'this session'. Presentation freshness is "
            "per TURN; a sourcing floor is stated as 'from the server, not from this "
            "file'. 'This session' is neither, and reads as permission to present an "
            "earlier turn's result:\n  " + "\n  ".join(found))


class TheGroundRulesDefineBothTerms(unittest.TestCase):
    def setUp(self):
        self.flat = squash(read(GROUND_RULES))

    def test_presentation_freshness_is_named_and_turn_scoped(self):
        self.assertIn("**Presentation freshness — \"this turn\".**", self.flat,
                      "presentation freshness is not defined as a named rule")
        self.assertRegex(
            self.flat, r"(?i)on the turn that reply is sent",
            "the freshness rule does not say which turn it means")

    def test_the_sourcing_floor_is_named(self):
        self.assertRegex(
            self.flat,
            r"\*\*Sourcing floor — \"from the server, not from this file\"\.\*\*",
            "the sourcing floor is not defined as a named rule, so the nine sites that "
            "mean it have no term to use")
        self.assertRegex(self.flat, r"(?i)floor on provenance",
                         "the floor is not distinguished from a caching allowance")

    def test_the_floor_is_stated_not_to_relax_the_freshness_rule(self):
        self.assertRegex(
            self.flat, r"(?i)a sourcing floor never relaxes presentation freshness",
            "nothing states the relationship between the two rules, which is the whole "
            "reconciliation this spec asked for")
        self.assertRegex(
            self.flat, r"(?i)both apply and\s*the stricter one governs",
            "no tie-break is given, so a conflict is resolved by whichever rule the "
            "reader happened to read")

    def test_the_attribution_rule_points_back_at_the_definition(self):
        self.assertRegex(
            self.flat,
            r"(?i)same \*?\*?presentation freshness\*?\*? rule defined in",
            "the attribution rule still states the turn requirement independently, which "
            "is how two vocabularies grew in the first place")


class TheGalleryIsFilledOnTheTurnItIsPresented(unittest.TestCase):
    def setUp(self):
        self.flat = squash(read(DISCOVERY))

    def test_the_permission_shaped_wording_is_gone(self):
        self.assertNotIn("content returned this session", self.flat,
                         "the gallery may still be filled from an earlier turn's results")

    def test_it_names_the_turn_and_forbids_an_earlier_one(self):
        self.assertRegex(
            self.flat, r"(?i)returned on the turn the gallery is presented",
            "the step does not say which turn the content must come from")
        self.assertRegex(
            self.flat, r"(?i)never from an earlier turn's results",
            "the step does not close the earlier-turn reading it permitted")

    def test_it_cites_the_defined_rule_and_the_attribution_reason(self):
        self.assertRegex(self.flat, r"(?i)presentation freshness",
                         "the step does not use the defined term")
        self.assertRegex(
            self.flat, r"(?i)attribution is only truthful for what a tool produced this turn",
            "the reason the rule exists here — the step's own MCP attribution line — is "
            "not stated, leaving it looking like arbitrary strictness")


if __name__ == "__main__":
    unittest.main()
