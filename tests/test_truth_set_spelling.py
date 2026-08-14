"""The dataset is spelled "Truth Set" in prose, and one word only inside an identifier.

The shipped plugin used both: 160 occurrences of "Truth Set" against 12 of "TruthSet", the
one-word form confined to three files and all of it agent-facing internal prose — a timeout list,
a source-precedence rule, a scope limit, an exclusion rule.
`module-03-system-verification/phase1-verification.md` carried **both spellings in one line**
("…web-service termination, TruthSet purge, and `## Truth Set…"), which is what makes it drift
rather than a deliberate distinction.

⛔ **Which spelling is canonical is a Senzing fact, not a repo preference** (INV-080), so it was
asked rather than chosen. Server **1.32.9, 2026-08-14**:

* `search_docs(query='truth set demo data customers reference watchlist quickstart')` returns the
  Senzing documentation page titled **"Truth Set Setup"**, whose prose reads "loading the Senzing
  **truth set** demo data" and "load the **truth set** data files" — two words throughout.
* The one-word form appears in that same corpus **only inside identifiers**: `truthset_config.g2c`,
  `truthset_demo.sh`, `actual_truthset_key.csv`, and the repo path `senzing/truth-sets`.
* `get_sample_data(dataset='list')` names the dataset key `truthset` with display name
  "Truthset CORD" — an identifier and its label, not prose.

So the rule this guard holds is the distinction the corpus itself draws: **prose gets two words,
identifiers keep whatever they are.** That is why the module directory
`module-03b-truthset-visualization`, the state token `truthset_visualization`, and the data file
`truthset_data.jsonl` are all untouched and must stay that way — renaming a skill directory would
break every relative cross-reference pointing at it.

Enforces **INV-230** — a Senzing dataset name in shipped prose uses the spelling Senzing's own
documentation uses, confirmed against the MCP server rather than chosen; the closed-up form is
reserved for identifiers, and an identifier is never rewritten to match prose.

⚠️ INV-230 is **not** INV-079, which governs **module names**: "Truth Set visualization" was correct
everywhere the module is named, so INV-079 was never violated here, and reading a dataset spelling
into it would have widened an invariant's meaning in place (`INVARIANTS.md` rule 2). INV-230 was
registered on 2026-08-14 with the maintainer's sign-off, after this guard already held the rule.

Source spec: `specs/truth-set-is-spelled-two-ways-in-shipped-prose.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS = REPO_ROOT / "plugins"

#: Bare prose "TruthSet" — not preceded or followed by an identifier character, so
#: `truthset_data.jsonl`, `module-03b-truthset-visualization` and `truthset_visualization` are
#: all excluded by construction rather than by an allowlist that would need maintaining.
PROSE_ONE_WORD = re.compile(r"(?<![\w/_.-])TruthSet(?![\w/_.-])")

TEXT_SUFFIXES = frozenset((".md", ".py", ".json", ".yaml", ".yml", ".sh", ".ps1", ".txt",
                           ".js", ".html", ".css"))


def shipped_text_files():
    for path in sorted(PLUGINS.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path


class TheProseSpellingIsConsistent(unittest.TestCase):
    def test_no_shipped_file_uses_the_one_word_form_in_prose(self):
        offenders = []
        for path in shipped_text_files():
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in PROSE_ONE_WORD.finditer(text):
                line = text[:match.start()].count("\n") + 1
                offenders.append("%s:%d" % (path.relative_to(REPO_ROOT), line))
        self.assertEqual(
            [], offenders,
            "the dataset is spelled one word in prose at %s — Senzing's own documentation "
            "titles the page \"Truth Set Setup\" and writes \"truth set\" in prose (server "
            "1.32.9, 2026-08-14); one word belongs only inside an identifier" % ", ".join(offenders))

    def test_the_two_word_form_is_actually_present(self):
        """Not-vacuous guard: a rename that removed the term entirely would pass the test above."""
        total = sum(len(re.findall(r"Truth Set", p.read_text(encoding="utf-8", errors="replace")))
                    for p in shipped_text_files())
        self.assertGreater(total, 100,
                           "only %d occurrences of the two-word form — this guard is asserting "
                           "the absence of a term the plugin no longer uses" % total)


class TheIdentifiersAreLeftAlone(unittest.TestCase):
    """A sweep that "fixed" these would break paths, state tokens and cross-references."""

    def test_the_module_directory_keeps_its_one_word_path(self):
        self.assertTrue(
            (PLUGINS / "senzing-bootcamp" / "skills" / "module-03b-truthset-visualization").is_dir(),
            "the module directory was renamed; every relative cross-reference to it is now broken")

    def test_the_state_token_and_data_file_keep_their_spelling(self):
        joined = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                           for p in shipped_text_files())
        for identifier in ("truthset_visualization", "truthset_data.jsonl"):
            with self.subTest(identifier=identifier):
                self.assertIn(identifier, joined,
                              "%s was rewritten as prose; it is an identifier" % identifier)

    def test_no_identifier_is_partially_renamed(self):
        """⚠️ Written after a negative control escaped.

        The presence check above is repo-wide, so renaming the token in ONE file left it present
        elsewhere and the assertion passed — a guard matching the wrong site, the same class this
        whole spec came from. A *partial* rename is the real damage: the progress file gets written
        under one spelling and read under another, silently. So assert the prose-ified forms exist
        nowhere, which no single-file mutation can satisfy.
        """
        offenders = []
        for path in shipped_text_files():
            text = path.read_text(encoding="utf-8", errors="replace")
            for wrong in ("truth_set_visualization", "truth_set_data",
                          "module-03b-truth-set-visualization"):
                if wrong in text:
                    offenders.append("%s → %s" % (path.relative_to(REPO_ROOT), wrong))
        self.assertEqual(
            [], offenders,
            "an identifier was rewritten in prose form at %s — the state token, data file and "
            "module directory are addresses, and a half-applied rename splits them in two"
            % ", ".join(offenders))


if __name__ == "__main__":
    unittest.main()
