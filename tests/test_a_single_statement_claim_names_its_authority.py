"""A claim that a rule is owned by one place must cite the invariant behind it (INV-300).

The plugin relies everywhere on *a procedure is stated once, and every other place points at
it rather than carrying a copy*. Measured 2026-09-03: the discipline is asserted at **42**
shipped sites — *"stated once"*, *"the canonical statement"*, *"do not restate it here"*, *"so
the two cannot drift apart"* — and before INV-300 was registered, **twenty-seven of them cited
no invariant at all**, while the eight that did cited **INV-183**, whose registered scope is
*"a step that instructs the guide to generate a bootcamper-facing artifact"*. The no-fork
clause lives inside that scope, so at a server launch, an SDK error branch or a pinned
question's wording it was cited for a clause whose scope did not reach it.

⛔ **The window is the unit, not the line.** A rule is routinely and correctly cited at its
bullet head several lines above the sentence that states it, and a line-level check reports
those as uncited — the 2026-09-03 audit had to retract a finding produced exactly that way.

⚠️ **What this guard does NOT establish, said plainly because its vocabulary is open-ended:**

- The claim vocabulary is a **phrase list**. A site that says the same thing in new words
  ("the wording lives in step 10", "one place owns this") is invisible here. A miss is weak
  evidence; a hit is worth reading.
- It checks that *an* invariant is cited in the window, not that it is the **right** one. That
  question needs a person: `inv-179-is-cited-as-a-state-it-once-rule-it-does-not-contain`
  records ten citations that resolved, passed every scan, and named the wrong rule.
- It reads shipped **markdown** only. The same phrases appear in bundled scripts about values
  and visuals not drifting, which are not rule-ownership claims at all.

Stdlib only; shipped files are read as text, never imported (INV-108).

Source spec: ``specs/the-no-fork-discipline-is-registered-only-inside-inv-183s-artifact-scope.md``.
Enforces: **INV-300**.

Run:  python3 -m unittest discover -s tests
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHIPPED = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")

#: The vocabulary a single-statement ownership claim is written in today.
CLAIM = re.compile(
    r"stated once|states it once|stays stated once|canonical statement|do not restate|"
    r"not restated here|rather than restating|rather than a copy here|not a copy of|"
    r"rather than re-deriving|cannot drift|point at it, do not restate|"
    r"cite it rather than|link here rather than|read it there rather than", re.I)

#: ⛔ **The authority must be THE single-statement invariant, not any nearby id.** This read
#: `INV-\d+` until its own negative control failed to fire: removing INV-300 from a claim left
#: the guard green, because a neighboring rule six lines away cited something unrelated. That
#: is proximity substituting for governance — the exact defect `conformance.py per-rule` is
#: criticized for, reproduced inside the guard written to prevent it. INV-183 is accepted
#: because it states the same clause for artifact-generating steps and continues to govern
#: there (INV-300's own text says so).
CITATION = re.compile(r"INV-(?:300|183)\b")

#: Lines above and below that count as "the passage". A rule cited at its bullet head sits
#: several lines up from the sentence stating it, which is why this is not a line check.
WINDOW = 6

#: ⛔ **Hits that are NOT ownership claims**, each with the reason. Every entry is asserted to
#: still exist below: an exemption for text that has since been reworded is a lie the next
#: reader inherits, and it silently widens as the corpus changes around it.
NOT_A_CLAIM = (
    ("restate this as a snippet count",
     "a different sense of restate — do not SUMMARIZE the scaffold inventory as a count"),
    ("Senzing owns the reason, so relay it",
     "MCP sourcing: the SERVER owns the fact, which is INV-080's subject, not this one"),
    ("rather than restating a remembered one",
     "forbids reciting a remembered figure — again INV-080, not rule ownership"),
    ("Reuse one reader across modules rather than re-deriving it",
     "code reuse; the rule it names is stated in that same list, so nothing is pointed at"),
    ("the legend and the edge styling cannot drift apart",
     "two code constructs sharing a closed value set, not two statements of one rule"),
    ("two statements of the same idea cannot drift apart",
     "an authoring note about aligned wording; it names no owner and points nowhere"),
)

#: Measured at 42 on 2026-09-03. A floor, not a pin — the corpus grows.
MIN_CLAIMS = 30


def shipped_markdown():
    for dirpath, _dirs, files in os.walk(SHIPPED):
        if "__pycache__" in dirpath or os.sep + "vendor" in dirpath:
            continue
        for name in sorted(files):
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def ownership_claims():
    """[(relpath, lineno, line, window)] for every claim that is not exempt."""
    found = []
    for path in shipped_markdown():
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().split("\n")
        for index, line in enumerate(lines):
            if not CLAIM.search(line):
                continue
            window = "\n".join(lines[max(0, index - WINDOW):index + WINDOW + 1])
            if any(phrase in window for phrase, _why in NOT_A_CLAIM):
                continue
            found.append(
                (os.path.relpath(path, REPO_ROOT), index + 1, line.strip(), window))
    return found


class TheScanSeesTheCorpus(unittest.TestCase):
    def test_enough_claims_are_found_to_be_checking_something(self):
        """⛔ A scan matching nothing would pass the class below vacuously."""
        claims = ownership_claims()
        self.assertGreaterEqual(
            len(claims), MIN_CLAIMS,
            "expected at least %d single-statement claims in shipped markdown, found %d. A "
            "drop this large means the vocabulary in CLAIM has stopped matching how the "
            "plugin writes, not that the claims are gone." % (MIN_CLAIMS, len(claims)))

    def test_every_exemption_still_matches_real_text(self):
        """An exemption for text that no longer exists silently widens as prose changes."""
        corpus = "\n".join(
            open(p, encoding="utf-8").read() for p in shipped_markdown())
        for phrase, why in NOT_A_CLAIM:
            with self.subTest(phrase=phrase[:40]):
                # ⚠️ `assertIn` against the corpus prints the whole haystack on failure —
                # 1.3 MB of shipped markdown, which buries the one line that matters. Assert
                # the boolean and say what is missing instead.
                self.assertTrue(
                    phrase in corpus,
                    "this exemption matches nothing in shipped markdown any more: %r (%s). "
                    "Either the passage was reworded — re-read it and decide again — or the "
                    "exemption was wrong to begin with." % (phrase, why))


class EveryClaimNamesAnAuthority(unittest.TestCase):
    def test_each_claim_has_an_invariant_in_its_passage(self):
        offenders = []
        for relpath, lineno, line, window in ownership_claims():
            if CITATION.search(window):
                continue
            offenders.append("  %s:%d — %s" % (relpath, lineno, line[:130]))
        self.assertEqual(
            [], offenders,
            "a site claims a rule is stated once elsewhere and names no invariant for that "
            "claim (INV-300). Cite INV-300 — or INV-183 where the step generates a "
            "bootcamper-facing artifact, which is the scope INV-183 covers. Without an id, "
            "nothing binds future work to the single-statement discipline and nothing notices "
            "when a later edit forks the rule into a second copy:\n" + "\n".join(offenders))

    def test_the_invariant_itself_is_reachable_from_the_claims(self):
        """⛔ INV-300 must actually be cited in shipped text, not only registered.

        An invariant nobody cites is one a later editor cannot look up and will tidy away —
        the INV-134 shape. This asserts the sweep reached shipped prose rather than stopping
        at `INVARIANTS.md`.
        """
        citing = [
            os.path.relpath(p, REPO_ROOT) for p in shipped_markdown()
            if "INV-300" in open(p, encoding="utf-8").read()
        ]
        self.assertGreaterEqual(
            len(citing), 15,
            "INV-300 is cited in only %d shipped file(s). It was swept across 18 on "
            "2026-09-03; a sharp drop means citations were removed rather than the claims "
            "themselves: %r" % (len(citing), citing))


if __name__ == "__main__":
    unittest.main()
