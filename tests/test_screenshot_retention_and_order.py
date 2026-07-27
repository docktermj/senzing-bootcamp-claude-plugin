"""Every captured tab reaches the recap, in the app's tab order.

Two bootcamper-reported defects in one instruction block.

**The count cap outlived its reason.** When `capture_screenshots.py` produced
three *viewport variants of one tab*, "keep the 2-3 most representative (delete
the rest)" was sound — two of the three were redundant. `INV-122` replaced that
with one image per tab, which makes every capture a distinct view, but only the
caption half of that sentence was rewritten. The count half survived and could
then only delete unique content: a six-tab app shipped three tabs, the same three
in both visualization sections, and the three that were dropped — Merge
Statistics, Match Keys, Feature Scores — are the analytical ones, because
"representative" pulls toward the visually striking.

**Nothing specified an order**, so images landed in filename-discovery order.
The recap is a walkthrough of the app, and its images ran Entity Graph →
Cross-Source → Search/Probe → Merge Statistics → Match Keys → Feature Scores
against an interface whose tabs run in a different order.

The tab table in `visualization-api-reference.md` is the single source for both
the tab set and their order; these tests assert both call sites defer to it.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")
MODULE_COMPLETION = os.path.join(
    PLUGIN, "skills", "bootcamp-onboarding", "module-completion.md"
)
GRADUATION = os.path.join(PLUGIN, "skills", "graduation", "SKILL.md")
CONTRACT = os.path.join(
    PLUGIN, "skills", "module-03b-truthset-visualization", "visualization-api-reference.md"
)
EXAMPLE_RECAP = os.path.join(PLUGIN, "docs", "examples", "bootcamp_recap.example.md")

# The two files that decide which screenshots reach the recap and in what order.
CALL_SITES = (MODULE_COMPLETION, GRADUATION)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def flat(path):
    """Whitespace-collapsed text — these are wrapped prose, so a phrase
    assertion on the raw text is really an assertion about line breaks."""
    return re.sub(r"\s+", " ", read(path))


def shipped_markdown():
    for dirpath, dirnames, filenames in os.walk(PLUGIN):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


class NoCountCapSurvives(unittest.TestCase):

    def test_no_shipped_file_asks_for_the_most_representative(self):
        offenders = [
            os.path.relpath(p, REPO_ROOT)
            for p in shipped_markdown()
            if "most representative" in read(p)
        ]
        self.assertEqual(
            [], offenders,
            f"'most representative' selection survives in: {offenders}. Every capture "
            "is a distinct tab (INV-122), so selecting among them can only drop unique "
            "content — and it drops the analytical tabs first.",
        )

    def test_no_shipped_file_caps_the_number_kept(self):
        # Scoped by shape, not by the exact adjective, and swept across EVERY
        # shipped file rather than the two call sites.
        #
        # Both narrowings let real caps ship. The adjective list ("most"|"best")
        # missed `module-completion.md`'s surviving "embedding the 2-3 **curated**
        # screenshots is required" — in the very file whose ⛔ block says keep every
        # tab. The two-file scope missed the operative instruction at each capture
        # point: `module-03b/phase1-visualization.md` ("keep the 2-3 best") and
        # `module-07/phase1-query-visualize.md` ("embed the 2-3 best"), which is what
        # the agent actually reads when the screenshots are taken.
        pattern = re.compile(r"\b\d\s*-\s*\d\b\s+\w+\s+(?:screenshots?|images?)"
                             r"|\b\d\s*-\s*\d\b\s+(?:most|best|curated)"
                             r"|delete the rest")
        offenders = []
        for path in shipped_markdown():
            hit = pattern.search(flat(path))
            if hit:
                offenders.append(f"{os.path.relpath(path, REPO_ROOT)}: {hit.group(0)!r}")
        self.assertEqual(
            [], offenders,
            "a count cap deletes unique content now that capture is per-tab "
            f"(INV-146): {offenders}",
        )

    def test_module_completion_says_keep_every_tab(self):
        self.assertRegex(
            flat(MODULE_COMPLETION),
            r"[Kk]eep every captured tab",
            "the instruction must be to retain, not to select",
        )

    def test_graduation_backfills_all_not_a_best_few(self):
        self.assertRegex(
            flat(GRADUATION),
            r"\*\*all\*\* of them, not a \"best\" few|all of them, not a best few",
            "the backfill is the safety net for a missed embed — capping it means it "
            "cannot restore what the capture step dropped",
        )

    def test_the_example_recap_does_not_model_pruning(self):
        """A sample deliverable is guidance by demonstration."""
        self.assertNotIn("most representative", read(EXAMPLE_RECAP))


class TabOrderIsSpecifiedAndSourcedFromTheContract(unittest.TestCase):

    def test_the_contract_declares_its_row_order_is_the_embed_order(self):
        self.assertRegex(
            flat(CONTRACT),
            r"row order below is also the order the app presents its tabs",
            "the tab table must state that it is the ordering authority, or the two "
            "call sites have nothing to cite",
        )

    def test_both_call_sites_require_tab_order(self):
        for path in CALL_SITES:
            with self.subTest(file=os.path.basename(path)):
                self.assertRegex(
                    flat(path),
                    r"tab order",
                    "capture-time embedding and graduation's backfill both need the rule "
                    "— the backfill appends by directory scan without it",
                )

    def test_both_call_sites_forbid_append_or_discovery_order(self):
        for path in CALL_SITES:
            with self.subTest(file=os.path.basename(path)):
                self.assertRegex(
                    flat(path),
                    r"never in capture or append order|not in filename-discovery order",
                    "naming the wrong orders explicitly is what makes the rule checkable",
                )

    def test_neither_call_site_restates_the_tab_list(self):
        """Restating it forks the order; both must cite the table instead."""
        for path in CALL_SITES:
            with self.subTest(file=os.path.basename(path)):
                text = flat(path)
                self.assertIn("visualization-api-reference.md", text)
                self.assertNotRegex(
                    text,
                    r"Entity Graph, Merge Statistics, Match Keys, Feature Scores, "
                    r"Cross-Source, Search ?/ ?Probe",
                    "the ordered tab list is restated here; cite the contract table so "
                    "a tab change updates one file",
                )


class TheAnalyticalTabsAreNamedAsWhatWasLost(unittest.TestCase):
    """Without the reason recorded, a future edit re-adds the cap as a tidy-up."""

    def test_module_completion_records_which_tabs_the_cap_dropped(self):
        text = flat(MODULE_COMPLETION)
        for tab in ("Merge Statistics", "Match Keys", "Feature Scores"):
            with self.subTest(tab=tab):
                self.assertIn(tab, text)


if __name__ == "__main__":
    unittest.main()
