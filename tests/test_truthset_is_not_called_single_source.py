"""The Truth Set has three data sources, and no shipped file may say otherwise.

`visualization-api-reference.md` told the implementer that the INV-270 encoding self-check
is unexercisable in the very module that builds the visualization app: *"it is the normal
Truth Set situation, and it is exactly why the module that builds this app cannot catch
the defect with its own data"*, closing with *"Say 'not exercised — one data source' and
move on."*

**The premise is false.** `get_sample_data(dataset='truthset', source='list')` returns
**three** sources — CUSTOMERS 120, REFERENCE 22, WATCHLIST 17, 159 records (server 1.33.0,
re-confirmed 2026-08-28) — and one full load emitted **7** distinct source-set keys, 4 of
them combinations, over 84 entities. The check is fully live on Truth Set data.

⛔ **The cost was not a wrong sentence, it was an instruction to stop looking.** The
paragraph's closing words were *"and move on"*. The INV-259 coloring defect INV-270 exists
to catch (294 of 5,619 cross-source entities rendered single-source in a generated Java
app) would have been caught by the Truth Set, one module earlier than the run that found
it.

⚠️ **The spec named ONE site. There were five** — the contract, the module-03b
walkthrough, module-07's step 3c, the docstring of the guard enforcing INV-270, and
INV-270's own text. That is why this guard **scans** for the claim instead of naming
files: a listed guard certifies the sites someone already thought of and is blind to the
one that matters (INV-246).

⚠️ What this does NOT establish: that the Truth Set exercises the check on any particular
run. It asserts what the plugin *claims* about the dataset, which is text. Whether a given
load emits two or more keys is a runtime property the offline suite cannot see (INV-108).

Enforces **INV-270** as corrected 2026-08-28 — the not-exercised rule below two keys
stands (INV-265); only the claim that the Truth Set lands in that state is withdrawn.

Source spec: `specs/the-truth-set-does-exercise-the-encoding-self-check.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"

#: Phrases asserting the Truth Set is single-source or cannot exercise the check. Each is
#: matched only when "truth set" appears within WINDOW characters, so the many legitimate
#: single-source passages (System verification's `VERIFY`, the generic INV-265 rule) pass.
CLAIMS = (
    r"normal truth ?set situation",
    r"cannot catch the defect with its own data",
    r"cannot provoke (?:it|the defect)",
    r"structurally cannot provoke",
    r"expected outcome whenever one data source is registered",
    r"almost always reports\s+`?not_exercised`?",
)
WINDOW = 600


def shipped_markdown():
    """Every markdown file that ships to bootcampers."""
    return sorted(p for p in PLUGIN.rglob("*.md") if "__pycache__" not in p.parts)


def flatten(text):
    return re.sub(r"\s+", " ", text).lower()


def offending(text):
    """[(claim, excerpt)] for each claim appearing near a Truth Set mention."""
    flat = flatten(text)
    hits = []
    for claim in CLAIMS:
        for m in re.finditer(claim, flat):
            lo, hi = max(0, m.start() - WINDOW), min(len(flat), m.end() + WINDOW)
            if "truth set" in flat[lo:hi] or "truthset" in flat[lo:hi]:
                hits.append((claim, flat[max(0, m.start() - 120):m.end() + 120]))
    return hits


class NoShippedFileCallsTheTruthSetSingleSource(unittest.TestCase):
    def test_no_shipped_markdown_makes_the_claim(self):
        bad = []
        for path in shipped_markdown():
            for claim, excerpt in offending(path.read_text(encoding="utf-8")):
                bad.append(f"{path.relative_to(REPO_ROOT)}: /{claim}/ near a Truth Set "
                           f"mention — ...{excerpt}...")
        self.assertEqual(
            [], bad,
            "the Truth Set registers THREE data sources (CUSTOMERS, REFERENCE, WATCHLIST), "
            "so the INV-270 encoding self-check IS exercised there. A shipped file says "
            "otherwise:\n  " + "\n  ".join(bad))

    def test_the_invariant_itself_does_not_make_the_claim(self):
        """INV-270 carried it too, which no scan of `plugins/` would have found."""
        withdrawn = flatten(INVARIANTS.read_text(encoding="utf-8"))
        self.assertIn("corrected 2026-08-28", withdrawn,
                      "INV-270's dated correction is gone; it withdrew the false premise")
        self.assertNotIn("the truth set structurally cannot provoke it** (nearly all",
                         withdrawn, "INV-270 states the withdrawn premise as live text")

    def test_the_scan_is_not_vacuous(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        files = shipped_markdown()
        # 45 shipped .md files on 2026-08-28; the floor is deliberately below that and far
        # above zero, so a collapsed glob fails here rather than passing vacuously.
        self.assertGreater(len(files), 40, "the shipped-markdown corpus went empty or tiny")
        planted = ("The Truth Set has one source, so this module "
                   "cannot catch the defect with its own data.")
        self.assertTrue(offending(planted), "the matcher no longer detects the claim it exists for")

    def test_a_genuine_single_source_passage_is_not_flagged(self):
        """System verification's VERIFY data really is one source — that must still be sayable."""
        ok = ("Give every record a DATA_SOURCE of VERIFY (one synthetic source code is enough). "
              "With one registered data source every key is that source, so report not exercised.")
        self.assertEqual([], offending(ok),
                         "the matcher flags a correct single-source statement, which would "
                         "push an editor toward deleting a true sentence")


class TheCorrectedClaimIsStated(unittest.TestCase):
    """Deleting the false sentence is not the fix — the true one has to be there."""

    def test_a_shipped_file_states_the_truth_set_source_count(self):
        stating = [p.relative_to(REPO_ROOT) for p in shipped_markdown()
                   if re.search(r"truth ?set registers \*\*three\*\* data sources",
                                flatten(p.read_text(encoding="utf-8")).replace("**", "**"))
                   or ("truth set registers **three** data sources"
                       in flatten(p.read_text(encoding="utf-8")))]
        self.assertTrue(
            stating,
            "no shipped file states that the Truth Set registers three data sources. The "
            "correction was to replace a false claim with a true one, not to delete it")

    def test_the_not_exercised_rule_survived(self):
        """⛔ INV-265 must not be weakened by this correction."""
        contract = [p for p in shipped_markdown()
                    if "encoding_check" in p.read_text(encoding="utf-8")]
        self.assertTrue(contract, "no shipped file defines encoding_check any more")
        joined = flatten("".join(p.read_text(encoding="utf-8") for p in contract))
        self.assertIn("not_exercised", joined)
        self.assertIn("inv-265", joined,
                      "the not-exercised rule lost its INV-265 citation (INV-183)")


if __name__ == "__main__":
    unittest.main()
