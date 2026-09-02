"""A `DEFERRED INVARIANT` block quotes its rules verbatim from the shipping file.

The blocks are what the maintainer approves an invariant FROM. They are written by
copying the rule out of the file it ships in, and on 2026-09-01 seven of them had been
copied through something that truncates at ~110 characters -- the same cut
`conformance.py since` applies to its own display. What landed in the ledger read as a
complete rule and stopped mid-sentence:

    "The `_measured_at` marker is not bookkeeping -- it is what lets a later step tell a
     complete -- in `module-02-sdk-setup/SKILL.md`, Step 5a sub-step 3."

with the bold left unterminated, so the markdown after it rendered wrong too. One was
worse than truncated: the `get_license()` bullet had "resolves the license **against the
engine configuration**", a phrase that appears nowhere in the source, which says "from
the settings it is handed, and the settings here do not yet carry `CONFIGPATH`". A
paraphrase in a quotation slot is the failure this guards -- the maintainer approving
from it would be approving wording the plugin does not ship.

⚠️ This checks the QUOTE against the SOURCE, not the drafted invariant wording against
anything. The drafted wording is new text and has nothing to be verbatim against.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "plugins" / "senzing-bootcamp"
LEDGER = REPO / "specs" / "IMPLEMENTED.md"

# `⛔ **<quote>** ... — in `<path>`` -- the shape every deferral rule bullet uses.
#
# ⚠️ The `.*?` between the quote and `— in` is load-bearing. Without it this pattern
# required the path to follow the closing `**` immediately, so it silently skipped every
# bullet that explains itself before naming its file -- 3 of 17, including the one for
# INV-285, which went unchecked through its own registration. A guard that skips what it
# cannot parse reports a clean run over the subset it happened to match.
RULE = re.compile(r"⛔ \*\*(.+?)\*\*.*?—\s*in `([^`]+)`")

#: A rule gains `(INV-NNN)` at its line when the deferral is approved, so the shipped text
#: legitimately differs from the quote by exactly that. Normalize it off BOTH sides rather
#: than re-editing every quote at mint time -- ten deferrals are still pending.
CITATION = re.compile(r"\(INV-\d{3}\)\s*")


def flat(s):
    """Collapse whitespace and drop `(INV-NNN)` citations, so a minted rule still matches.

    The source wraps these rules across lines and the ledger does not, and an approved rule
    carries a citation the deferral's quote predates. Neither difference is a misquote.
    """
    return CITATION.sub("", re.sub(r"\s+", " ", s)).strip()


def resolve(loc):
    """Resolve a ledger location to a real file, by PATH not basename.

    ⚠️ The first version of this check keyed a corpus on `path.name`, so every
    `module-NN.../SKILL.md` collapsed onto one entry and each quote was compared against
    whichever module happened to be read last. It reported six false mismatches on
    already-correct lines. The location is a path; resolve it as one.
    """
    for base in (PLUGIN / "skills", PLUGIN / "scripts", PLUGIN):
        candidate = base / loc
        if candidate.is_file():
            return candidate
    return None


def quoted_rules():
    """Yield (line_no, quote, location, path) for each rule bullet naming a real file."""
    for i, line in enumerate(LEDGER.read_text(encoding="utf-8").splitlines(), 1):
        if not line.lstrip().startswith("- "):
            continue
        m = RULE.search(line)
        if not m:
            continue
        loc = m.group(2)
        path = resolve(loc)
        if path is not None:          # a location naming a command, not a file, is not a quote
            yield i, flat(m.group(1)), loc, path


class DeferralQuotesAreVerbatim(unittest.TestCase):
    def setUp(self):
        self.cache = {}

    def source(self, path):
        if path not in self.cache:
            self.cache[path] = flat(path.read_text(encoding="utf-8"))
        return self.cache[path]

    def test_the_scan_finds_the_quotes(self):
        """A guard that silently matches nothing certifies nothing."""
        found = list(quoted_rules())
        # Every bullet that names a file must be PARSED, not just some of them -- the
        # skip-what-you-cannot-parse gap this guard shipped with on 2026-09-01.
        naming_a_file = [
            l for l in LEDGER.read_text(encoding="utf-8").splitlines()
            if l.lstrip().startswith("- ") and "⛔ **" in l and "— in `" in l
        ]
        self.assertEqual(
            len(naming_a_file), len(found),
            f"{len(naming_a_file) - len(found)} rule bullet(s) name a file but were not "
            "parsed, so their quotes are unchecked while this guard reports a clean run.",
        )
        self.assertGreaterEqual(
            len(found), 10,
            "the rule-bullet pattern matched almost nothing — the ledger's deferral shape "
            "has changed and this guard is no longer reading it.",
        )

    def test_every_quoted_rule_appears_verbatim_in_the_file_it_names(self):
        wrong = []
        for line_no, quote, loc, path in quoted_rules():
            if quote not in self.source(path):
                wrong.append(f"IMPLEMENTED.md:{line_no} quotes {loc} as:\n      {quote[:150]}")
        self.assertEqual(
            [], wrong,
            "a DEFERRED INVARIANT block quotes a rule that its named file does not contain "
            "verbatim — the quote is truncated, paraphrased, or the rule has since been "
            "reworded:\n  " + "\n  ".join(wrong),
        )

    def test_no_quoted_rule_leaves_its_bold_unterminated(self):
        """The truncation's visible symptom, caught even if the text were to match."""
        odd = [
            f"IMPLEMENTED.md:{i}"
            for i, line in enumerate(LEDGER.read_text(encoding="utf-8").splitlines(), 1)
            if line.lstrip().startswith("- ⛔ **") and line.count("**") % 2
        ]
        self.assertEqual(
            [], odd,
            f"a rule bullet opens bold and never closes it: {odd}. That is the signature of "
            "a quote cut off mid-sentence, and it corrupts the markdown after it.",
        )


if __name__ == "__main__":
    unittest.main()
