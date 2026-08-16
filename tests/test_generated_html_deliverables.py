"""Every step that generates bootcamper-facing HTML states the rules that bind it.

`module5-quality-pages-are-branded-visual-deliverables`. Data Quality, Mapping, and
Transformation offers the bootcamper two web pages and saves both under
`docs/visualizations/`. Both instructions were one sentence long:

    If the bootcamper accepts, generate a self-contained HTML page and save it to
    `docs/visualizations/`.

That sentence carries none of the rules binding every *other* bootcamper-facing visual the
plugin produces, and the rules were unreachable from there:

- **INV-081** binds the pages by its own terms ("any future generated charts/dashboards/HTML
  /PDF ... MUST take its palette and typography from the shared Senzing brand tokens ... and
  MUST keep rendering offline"), yet `brand_tokens` was cited in modules 3b and 7 and **never**
  in module 5.
- The only governing text softened that MUST into "should ... where appropriate", with a
  carve-out a reader could apply to a keepsake.
- **INV-106**'s escaping requirement was stated only inside the Truth Set app's contract, which
  neither offer cites — so a page whose entire content is the bootcamper's own field names and
  sample values had no escaping rule.

The concrete failure is silent: a "coverage charts" page that reaches for a CDN chart library
renders blank on an air-gapped workstation — which Senzing evaluations frequently are — with no
error anywhere.

This is the shape INV-164 named: a defect reaches generated output "precisely because it lived
in the reference implementation and in no written rule". Here the rule existed but lived in a
file the generating step never opens. So what is pinned is **reachability**: the step that tells
the guide to generate HTML must itself name the rules, because that is the only text the guide
is certainly reading at that moment.

Written as a sweep rather than two assertions, so the *next* ad-hoc HTML offer is caught too.

Enforces **INV-183** (a step that generates a bootcamper-facing artifact must name, at that
step, every rule governing how it is produced) for generated HTML. INV-183 names this file
as its enforcer and is deliberately broader than this test: the next such artifact may not
be HTML.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
SKILLS = PLUGIN / "skills"
GROUND_RULES = SKILLS / "bootcamp-onboarding" / "ground-rules.md"
MODULE_COMPLETION = SKILLS / "bootcamp-onboarding" / "module-completion.md"

# A step that instructs generating a saved HTML page for the bootcamper.
GENERATES_HTML = re.compile(r"generate a self-contained HTML page", re.I)

# Each rule, and the evidence that the step (or a block it points at) states it. Matching is
# on flattened text, since every one of these lands mid-paragraph in wrapped prose.
REQUIRED_RULES = {
    "brand tokens (INV-081)": ("brand_tokens",),
    "offline rendering (INV-081/INV-091)": ("no cdn", "renders offline", "render offline"),
    # Cite the invariant, not just the word: mutation-testing showed a bare "escape" probe
    # passing on the surviving phrase "`\uXXXX` escapes" after the actual rule was deleted.
    # The citation is also what makes the rule reachable — it is how a reader gets to the
    # statement of record in the visualization contract.
    "escaping data-sourced strings (INV-106)": ("inv-106",),
    "artifact verification (INV-129)": ("inv-129",),
}

# The tabbed apps, whose own module files carry these rules already and are not ad hoc offers.
TABBED_APP_FILES = {
    "phase1-visualization.md",
    "visualization-api-reference.md",
    "phase1-query-visualize.md",
}


def flatten(text):
    return re.sub(r"\s+", " ", text).lower()


def html_generating_files():
    """Skill files that instruct generating a self-contained HTML page."""
    out = []
    for path in sorted(SKILLS.rglob("*.md")):
        if path.name in TABBED_APP_FILES:
            continue
        if GENERATES_HTML.search(path.read_text(encoding="utf-8")):
            out.append(path)
    return out


class EveryHtmlOfferNamesItsRules(unittest.TestCase):
    def test_the_sweep_finds_the_known_offers(self):
        """If this finds nothing, the sweep has drifted and everything below is vacuous."""
        names = {p.name for p in html_generating_files()}
        self.assertIn("phase1-quality-assessment.md", names)
        self.assertIn("phase2-data-mapping.md", names)

    def test_each_offer_states_every_rule(self):
        missing = []
        for path in html_generating_files():
            flat = flatten(path.read_text(encoding="utf-8"))
            for rule, probes in REQUIRED_RULES.items():
                if not any(p in flat for p in probes):
                    missing.append(f"{path.name}: does not state {rule}")
        self.assertEqual(
            [],
            missing,
            "a step generating bootcamper-facing HTML does not name a rule that binds it "
            "— the rule exists but is unreachable from where the page is authored:\n  "
            + "\n  ".join(missing),
        )

    def test_each_offer_keeps_the_page_under_docs_visualizations(self):
        """INV-070, and what makes these pages bootcamper-facing deliverables at all."""
        for path in html_generating_files():
            self.assertIn(
                "docs/visualizations/",
                path.read_text(encoding="utf-8"),
                f"{path.name} generates HTML but does not place it under docs/visualizations/",
            )


class GroundRulesStateTheBrandRuleAsAMust(unittest.TestCase):
    """INV-081 says MUST; the global statement said "should ... where appropriate"."""

    def test_the_brand_rule_is_a_must(self):
        flat = flatten(GROUND_RULES.read_text(encoding="utf-8"))
        section = flat[flat.index("visual deliverables (senzing brand)"):]
        section = section[: section.index("## progress and state")]
        self.assertIn(
            "must",
            section,
            "the brand rule must be stated as a MUST for bootcamper-facing deliverables "
            "(INV-081), not as a preference",
        )
        self.assertNotIn(
            "should follow the",
            section,
            'the softened "should follow the ... style guide" wording is back; INV-081 says MUST',
        )

    def test_the_carve_out_is_about_which_artifacts_not_whether_to_brand(self):
        flat = flatten(GROUND_RULES.read_text(encoding="utf-8"))
        self.assertIn(
            "plain functional/dev output",
            flat,
            "the carve-out must stay scoped to non-kept output",
        )
        self.assertTrue(
            "saved and handed to them" in flat or "saved and shared" in flat,
            "the carve-out needs a stated test for what counts as bootcamper-facing, or "
            '"where appropriate" becomes an exemption again',
        )

    def test_escaping_is_stated_for_any_generated_page(self):
        flat = flatten(GROUND_RULES.read_text(encoding="utf-8"))
        self.assertIn(
            "inv-106",
            flat,
            "ground-rules must state the escaping rule, since it was reachable only from the "
            "Truth Set app's contract",
        )


class CaptureProcedureNamesItsScope(unittest.TestCase):
    """A tab-based procedure pointed at a single-page deliverable captures nothing."""

    def test_the_capture_section_distinguishes_tabbed_from_single_page(self):
        flat = flatten(MODULE_COMPLETION.read_text(encoding="utf-8"))
        self.assertIn(
            "single-page",
            flat,
            "the screenshot procedure triggers on any HTML page under docs/visualizations/ but "
            "is written for the tabbed app — it must say what to do with a single-page page",
        )
        self.assertIn(
            "one image",
            flat,
            "a single-page deliverable is captured as one image, with no --tabs argument",
        )
