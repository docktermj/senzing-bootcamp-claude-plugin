"""An empty Truth Set visualization is a reported failure, not a passing verification.

**INV-077 fully superseded INV-038 and dropped a clause.** INV-038 said the Bootcamper
"ALWAYS sees a dynamic web-app visualization of the Truth Set **to verify that Senzing
works** on the Bootcamper's workstation." INV-077 replaced it with a delivery-and-selection
rule — *which* module produces the visualization and *when* — under which **an empty graph
complies completely**. Between that supersession and 2026-08-15 nothing on the books made a
blank render a failure, while `ground-rules.md` cited INV-077 as though it did:

    (the blank-render failure INV-077 exists to prevent)

⛔ **`citations.py verify` cannot see this class.** INV-077 exists, so the reference resolves
and the suite stays green; only reading shows the clause relied on is not in it. That is the
INV-134/INV-155 shape — a guarantee that exists in the product and nowhere in the ruleset.
(`specs/inv077-supersession-dropped-the-visualization-verification-guarantee.md`)

Enforces **INV-250**, which restores the dropped clause as a testable condition. Scope was a
maintainer decision, 2026-08-15: it binds the **step's reporting**, not a detection mechanism,
because a detect-and-confirm form is unverifiable offline (INV-108) and a criterion nobody can
run is worse than a narrower rule that holds.

⛔ **WHAT THIS GUARD CANNOT SEE.** It asserts the rule ships and is cited where it binds. It
does **not** assert that a live render is non-empty — that needs `libSz.so` and loaded data,
absent from the offline suite — and it cannot establish that a guide *acts* on the rule in a
live turn, which is `dry-run` territory. A clean run means the rule is reachable, never that a
bootcamper saw a populated graph.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"
GROUND_RULES = PLUGIN / "skills" / "bootcamp-onboarding" / "ground-rules.md"


def squash(text):
    return re.sub(r"\s+", " ", text)


def shipped_markdown():
    """Every shipped Markdown file, discovered rather than listed (INV-246)."""
    return sorted(PLUGIN.rglob("*.md"))


class TheInvariantIsRegistered(unittest.TestCase):
    def setUp(self):
        self.text = INVARIANTS.read_text(encoding="utf-8")

    def test_inv250_exists_and_states_the_condition(self):
        self.assertRegex(
            squash(self.text),
            r"\*\*INV-250\*\* — The Truth Set visualization step MUST NOT present an "
            r"\*\*empty\*\* visualization as the workstation-verification step passing",
            "INV-250 no longer states the condition INV-077's supersession dropped")

    def test_inv250_is_in_the_index(self):
        """INVARIANTS.md rule 3: the index entry ships in the same edit as the invariant.

        The slice is derived from the heading and the next `## ` after it — an earlier version
        pinned a literal boundary that did not exist, so the slice came out EMPTY and the
        assertion failed for the wrong reason. A slice that can silently be empty is the
        vacuity this repo's guards keep tripping over.
        """
        start = self.text.index("### Index by subject")
        end = self.text.index("<!-- New invariants", start)
        index = self.text[start:end]
        self.assertGreater(len(index), 500,
                           "the index slice collapsed; this assertion would pass vacuously")
        self.assertIn("INV-250", index,
                      "INV-250 is defined but missing from the subject index (rule 3)")

    def test_inv038_is_still_marked_superseded(self):
        """The remedy was a NEW id, never reviving the retired one (append-only)."""
        self.assertRegex(
            squash(self.text), r"\*\*INV-038\*\*.{0,400}?\(Superseded by INV-077",
            "INV-038's supersession marker was removed — the fix must add a live invariant, "
            "not un-supersede a retired one")


class TheRuleShipsWhereItBinds(unittest.TestCase):
    """INV-183: reachable AT the step that performs the verification."""

    def test_the_verification_step_states_it(self):
        phase1 = (PLUGIN / "skills" / "module-03b-truthset-visualization"
                  / "phase1-visualization.md").read_text(encoding="utf-8")
        step = phase1[phase1.index("### 2.4 Verify the endpoints"):
                      phase1.index("### 2.4b")]
        self.assertRegex(
            squash(step), r"(?i)empty visualization is a FAILED verification",
            "the endpoint-verification step no longer says an empty visualization is a "
            "failure, so the rule is reachable only from INVARIANTS.md (INV-183)")
        self.assertIn("INV-250", step,
                      "the rule ships at the step without its invariant ID, so a later "
                      "editor cannot look it up")

    def test_the_step_names_the_likely_cause(self):
        """A failure with no cause named is the silence this invariant exists to break."""
        phase1 = (PLUGIN / "skills" / "module-03b-truthset-visualization"
                  / "phase1-visualization.md").read_text(encoding="utf-8")
        step = squash(phase1[phase1.index("### 2.4 Verify the endpoints"):
                             phase1.index("### 2.4b")])
        self.assertRegex(
            step, r"(?i)not persistent and shareable\s*across processes \(INV-231\)",
            "the step reports the failure without naming its cause — the observed path, "
            "where the loader and this server address different datastores, every load "
            "reports success, and nothing fails until this page comes up blank")


class NoShippedTextAttributesTheGuaranteeToINV077(unittest.TestCase):
    """The wrong-citation half. Derived across shipped Markdown, never a path list (INV-246)."""

    #: Sentences that assign the blank-render guarantee to an invariant. The defect was one
    #: such sentence naming INV-077; a second site would be the same defect, so the scan is
    #: over the corpus rather than the one file it was found in.
    BLANK_RENDER = re.compile(
        r"(?i)blank-render failure (INV-\d{3})")

    def test_the_corpus_is_actually_scanned(self):
        self.assertGreater(len(shipped_markdown()), 20,
                           "the shipped-Markdown scan collapsed; every assertion below "
                           "would pass vacuously")

    def test_no_site_attributes_it_to_inv077(self):
        offenders = []
        for path in shipped_markdown():
            for m in self.BLANK_RENDER.finditer(squash(path.read_text(encoding="utf-8"))):
                if m.group(1) == "INV-077":
                    offenders.append(path.relative_to(REPO_ROOT))
        self.assertEqual(
            [], offenders,
            "INV-077 governs WHICH module produces the visualization and WHEN — an empty "
            "graph satisfies it completely. The blank-render guarantee is INV-250. Sites: "
            "%s" % offenders)

    def test_the_guarantee_is_attributed_to_something(self):
        """Non-vacuity: if the sentence were deleted the test above would pass emptily."""
        found = [p.relative_to(REPO_ROOT) for p in shipped_markdown()
                 if self.BLANK_RENDER.search(squash(p.read_text(encoding="utf-8")))]
        self.assertTrue(
            found,
            "no shipped file attributes the blank-render failure to any invariant, so "
            "test_no_site_attributes_it_to_inv077 is now vacuous")

    def test_ground_rules_distinguishes_the_two_invariants(self):
        text = squash(GROUND_RULES.read_text(encoding="utf-8"))
        self.assertRegex(
            text, r"INV-077\s*\n?\s*governs \*which\* module produces that visualization, "
                  r"not what it must contain".replace("\n", ""),
            "ground-rules.md no longer says what INV-077 actually governs, so the "
            "correction can be re-derived as a mistake and reverted")


if __name__ == "__main__":
    unittest.main()
