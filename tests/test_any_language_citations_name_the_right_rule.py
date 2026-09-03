"""An "this binds every language" claim must cite the invariant that says so.

``visualization-api-reference.md`` cited **INV-124** four times as the authority for "this rule
binds a server in any language". INV-124 governs the **tab hooks the recap capture depends on** --
``tab-<id>`` sections, ``navbtn-<id>`` buttons, a page-scope ``activate()``, and ``?tab=``/``?q=``
deep-linking. Its *"in whichever language it is generated"* clause scopes **its own** subject; it
is not a general statement about the contract. A reader following the citation to learn why a
*rendering* rule binds their Java implementation landed on a rule about tab ids.

The invariants that carry it are **INV-002** (the SBCP is language-agnostic) and **INV-090** (the
visualization server is built in the Bootcamper's chosen language, *modeled on the shipped
reference and the* ``visualization-api-reference.md`` *contract* -- which is what makes a rule
written in that contract binding). INV-104 is a defensible secondary, since it names the contract
as the source the app is built from.

⛔ **`citations.py verify` is structurally blind to this.** The ID resolves, the section cites an
invariant, and `conformance.py rules` counts it as covered. Only reading the invariant proves it
is the *right* one -- which is why this is the INV-076/INV-134 class: INV-076, an invariant about
the Core-vs-Customized path choice, was cited as the authority for the name-detection rule.

⚠️ **The root cause was a stock phrase in three SPEC bodies**, copied into shipped text by
implementing them, so the mis-citation reproduced itself once per implementation. All three now
carry a dated citation-correction note. This guard scans for the *shape* rather than pinning the
four lines that happened to be found (INV-246) -- but only in shipped text. See the comment
above ``TheCorrectInv124CitationSurvives`` for why a spec-side scan was written and abandoned.

⚠️ **One INV-124 citation is correct and must survive** -- ``docs/model-selection.md`` cites it
for "tab ids and deep-linking", which is precisely its subject. A guard that banned INV-124 near
any language word would delete a correct citation, so the assertion is narrowed to the
any-language *claim*.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).

Run:  python3 -m unittest discover -s tests
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins")

#: The claim: prose asserting a rule reaches implementations beyond the reference one.
ANY_LANGUAGE_CLAIM = re.compile(
    r"binds? (?:a server in|every|any)\s+\*{0,2}(?:any|every)?\*{0,2}\s*language"
    r"|in whatever language|in whichever language it is (?:generated|written)"
    r"|contract binds \*\*every\*\* language",
    re.IGNORECASE,
)
#: Characters either side of the claim in which its citations are looked for.
WINDOW = 260


def markdown_under(root):
    out = []
    for base, _dirs, files in os.walk(root):
        if "__pycache__" in base:
            continue
        for name in files:
            if name.endswith(".md"):
                out.append(os.path.join(base, name))
    return sorted(out)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


#: ⛔ **INV-124 near an any-language claim is not always wrong — it is wrong OFF its subject.**
#: INV-124 really does bind the tab hooks "in whichever language it is generated"; that is its own
#: wording. So the defect is an any-language claim citing INV-124 about something *other* than the
#: hooks. Found the hard way: the corrected tab-hook table states exactly that claim, correctly,
#: and tripped the first version of this scan. The exemption below is the same discriminator
#: `TheCorrectInv124CitationSurvives` applies from the other direction, which is why the two
#: assertions agree instead of fighting.
TAB_HOOK_SUBJECT = re.compile(r"(?i)tab id|section id|nav button|navbtn|deep-link|activate\(")


def mis_cited_claims(paths):
    """[(relpath, line, claim)] where an any-language claim cites INV-124 OFF its subject."""
    bad = []
    for path in paths:
        text = read(path)
        for m in ANY_LANGUAGE_CLAIM.finditer(text):
            window = text[max(0, m.start() - WINDOW):m.end() + WINDOW]
            if "INV-124" not in window:
                continue
            if TAB_HOOK_SUBJECT.search(window):
                continue            # INV-124's own subject — the citation governs here
            bad.append((os.path.relpath(path, REPO_ROOT),
                        text.count("\n", 0, m.start()) + 1,
                        re.sub(r"\s+", " ", m.group(0))))
    return bad


class NoShippedAnyLanguageClaimCitesInv124(unittest.TestCase):
    def test_shipped_text_does_not_cite_inv_124_for_an_any_language_claim(self):
        bad = mis_cited_claims(markdown_under(PLUGIN))
        self.assertEqual(
            [], bad,
            "An 'this binds every language' claim cites INV-124, which governs the recap "
            "capture's tab hooks — tab-<id> sections, navbtn-<id> buttons, activate(), "
            "deep-linking — and says nothing about rules binding other languages. Cite INV-002 "
            "(language-agnostic) and INV-090 (the server is built in the chosen language, "
            "modeled on this contract) instead. A reader who follows the wrong ID reaches a "
            "rule that does not answer them, and nothing else catches it: the ID resolves, so "
            "citations.py verify and conformance.py rules both read it as covered:\n  "
            + "\n  ".join("%s:%d — %r" % b for b in bad),
        )

    def test_the_claim_pattern_actually_matches_the_shipped_claims(self):
        """⚠️ A scan that matches nothing passes for the wrong reason.

        The floor is 2, measured: the contract states the claim at two places and
        ``module-04-data-collection/SKILL.md`` at one more. The first version of this asserted
        ``> 2`` on the assumption the claim was common, and failed on a correct tree — a
        threshold guessed rather than measured is a guard that reports the wrong thing on day
        one.
        """
        hits = 0
        for path in markdown_under(PLUGIN):
            hits += len(ANY_LANGUAGE_CLAIM.findall(read(path)))
        self.assertGreaterEqual(
            hits, 2,
            "The any-language claim pattern now matches fewer than two places in shipped text, "
            "so the assertion above can no longer fail whatever the citations say. The contract "
            "states this claim deliberately — a rule living only in the Python reference reaches "
            "no generated server — so if the phrasing changed, fix the pattern rather than "
            "lowering this floor.",
        )


# ⛔ **There is deliberately NO spec-side scan, and the reason is worth more than the scan.**
# The stock phrase reproduced from three spec bodies, so scanning `specs/` for an any-language
# claim near INV-124 looks like the obvious complement to the shipped assertion. It was written,
# run, and abandoned: it flagged **19** sites, and every one was legitimate.
#   - `specs/INVARIANTS.md` — INV-124's OWN text contains "in whichever language it is generated".
#   - `specs/IMPLEMENTED.md` — ledger entries quoting the finding.
#   - `specs/inv-124-is-cited-as-the-any-language-rule-it-is-not.md` — the spec that documents the
#     defect must state it to describe it.
#   - the three corrected specs — their dated citation-correction notes explain what INV-124 does
#     and does not govern, which necessarily puts the two next to each other.
# Four distinct legitimate shapes, all indistinguishable from the defect by proximity. A scan
# needing to exempt each of them measures nothing, and the exemption list would be the
# hardcoded-site-list antipattern (INV-246) wearing a different hat. The spec bodies are handled
# where they should be: corrected in place, each with a dated note saying why. What is guardable
# is the SHIPPED text, which is what a Bootcamper's guide actually reads.


class TheCorrectInv124CitationSurvives(unittest.TestCase):
    """⛔ Not every INV-124 citation is wrong, and a ban would have deleted the right one."""

    def test_inv_124_is_still_cited_for_its_own_subject(self):
        cited = [p for p in markdown_under(PLUGIN) if "INV-124" in read(p)]
        self.assertTrue(
            cited,
            "INV-124 is cited nowhere in shipped text. It governs the tab hooks the recap "
            "capture depends on, and `coverage_reports.py shipped` requires an invariant naming "
            "a shipped artifact to be citable at the step it binds (INV-183). Correcting the "
            "any-language citations must not have removed the correct one in "
            "docs/model-selection.md.",
        )

    def test_the_surviving_citations_are_about_tab_hooks(self):
        for path in markdown_under(PLUGIN):
            text = read(path)
            for m in re.finditer(r"INV-124", text):
                window = text[max(0, m.start() - 400):m.end() + 400]
                with self.subTest(path=os.path.relpath(path, REPO_ROOT)):
                    self.assertRegex(
                        window, r"(?i)tab id|deep-link|navbtn|activate\(",
                        "every surviving INV-124 citation must sit beside the tab-hook subject "
                        "it governs. One that does not is either the any-language defect again "
                        "or a new mis-citation on a third subject.",
                    )


if __name__ == "__main__":
    unittest.main()
