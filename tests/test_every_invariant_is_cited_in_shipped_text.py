"""Every invariant that binds a shipped artifact is cited by shipped text.

This is `coverage_reports.py shipped` promoted from a **report** to a **guard**, which only became
possible on 2026-08-14 when it first read zero. Until then it could not be a test, because a hit was
usually legitimate.

⛔ **The rule it holds is that minting an invariant is not the last action — citing it is.** On
2026-08-14 all eight invariants registered that day (INV-222–INV-229) were cited by no file under
`plugins/`, one day after `aa013dc` had fixed thirteen of the same class by hand. Every rule was
already stated in shipped prose; what was missing was the id, and a rule with no id is one a later
editor cannot look up and will "tidy" away — `deep-dive-audit-2026-07-28b` records a corrected
example being helpfully corrected *back* to the broken form for exactly that reason.

Two mechanisms let it happen, and both are now closed. `implement-spec` ran the three coverage
reports that look at `tests/` and never the one that looks at `plugins/`. And the batch had **queued**
its invariants for maintainer approval, so the prose shipped while the ids did not yet exist — the
citation was un-writable at the moment it was needed, and nothing sent anyone back once the ids were
minted. A citation that cannot be written when the prose is written will not be written at all
unless something asks for it. This asks.

⚠️ **Why this file naming an id does not defeat itself.** The sibling `invariants` report scans
`tests/`, so a test naming an ID makes the report stop listing it — which destroyed the first
version of that assertion. `shipped` scans **`plugins/` only**, so nothing written here can satisfy
it. That asymmetry is what makes this guard possible at all, and it is why the failure message names
the ids rather than hiding them.

The maintainer chose this over registering a second invariant (2026-08-14): the rule would largely
restate INV-183 for a new moment in time, and a mechanical check over the whole class is worth more
than another sentence.

Enforces the shipped half of **INV-183** — a rule binding a step must be reachable AT that step.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / ".claude" / "skills" / "dry-run" / "coverage_reports.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


reports = load(SCRIPT, "coverage_reports_shipped_guard")


class EveryBindingInvariantIsCited(unittest.TestCase):
    def setUp(self):
        self.hits, self.ungrouped = reports.find_uncited_in_shipped(str(REPO_ROOT))

    def test_no_invariant_naming_a_shipped_artifact_is_uncited(self):
        named = ["%s (%s…)" % (i, t[:60].rstrip()) for i, t in self.hits]
        self.assertEqual(
            [], named,
            "%d invariant(s) name a shipped artifact and no file under plugins/ cites them. Add "
            "the id at the site that states the rule — not to a test, which this report cannot "
            "see by design:\n  %s" % (len(named), "\n  ".join(named)))

    def test_no_invariant_is_missing_from_the_subject_index(self):
        """An unindexed invariant would slip past the check above by being unclassifiable."""
        self.assertEqual(
            [], self.ungrouped,
            "%d invariant(s) are in no `Index by subject` group, so the development-rule "
            "exemption cannot classify them and they silently escape the citation check: %s"
            % (len(self.ungrouped), ", ".join(self.ungrouped)))

    def test_the_check_is_not_vacuous(self):
        """It must be reading real invariants, not an empty parse of a moved file."""
        inv = (REPO_ROOT / "specs" / "INVARIANTS.md").read_text(encoding="utf-8")
        import re
        defined = set(re.findall(r"(?m)^- \*\*(INV-\d{3})\*\* — ", inv))
        self.assertGreater(
            len(defined), 200,
            "only %d invariants parsed from INVARIANTS.md — this guard would pass on an empty "
            "set, which is how an absence test certifies nothing" % len(defined))
        self.assertGreater(
            len(reports.module_display_names(str(REPO_ROOT))), 10,
            "the artifact filter's display-name half is nearly empty, so the check above would "
            "pass by seeing no artifacts rather than by finding every rule cited")

    def test_the_filter_still_recognises_a_display_name(self):
        """⚠️ Added after a negative control escaped: parsing the names is not using them.

        Emptying the display-name half of `shipped_artifact_re` left `module_display_names`
        returning all eleven, so the assertion above still passed while the filter had gone back
        to seeing only paths — the same narrow-guard class this whole guard exists to catch. So
        assert the composed regex matches text that the static half alone cannot.
        """
        artifact_re = reports.shipped_artifact_re(str(REPO_ROOT))
        for phrase in ("Truth Set visualization's close MUST record the module.",
                       "The System-verification checks MUST be reported separately."):
            with self.subTest(phrase=phrase):
                self.assertFalse(
                    __import__("re").search(reports.STATIC_ARTIFACT, phrase),
                    "this phrase is meant to be invisible to the STATIC half, or it proves "
                    "nothing about the display-name half")
                self.assertTrue(
                    artifact_re.search(phrase),
                    "the composed filter no longer recognises a module by its display name, so "
                    "every display-name invariant is invisible to the check above")


if __name__ == "__main__":
    unittest.main()
