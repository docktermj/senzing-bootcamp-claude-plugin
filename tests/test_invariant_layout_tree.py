"""INV-202: INV-050's layout tree must stay reachable — every entry produced, or annotated.

INV-050 states "The generated Bootcamp project MUST follow this layout" followed by a
fenced tree in `specs/INVARIANTS.md`. The tree is **correct today** — 24 file entries and
30 directory entries, none unaccounted — and until this file nothing checked that it stays
correct. No test parsed the tree; `tests/test_bundled_script_and_production_paths.py:14`
mentions INV-050 only in a docstring about `src/scripts/`.

The rule enforced here is **INV-202**: every leaf entry is either **referenced** somewhere
under `plugins/`, or **annotated** in its own comment as `reserved | superseded | legacy |
future`, and an unproduced entry gains the annotation rather than being deleted. It fails
on a future entry added without an annotation, and on an existing entry that quietly loses
its producer.

⚠️ **What this file must never assert.** A previous spec
(`specs/inv050-layout-tree-names-three-artifacts-nothing-produces.md`) claimed
`config/session_log.jsonl`, `config/visualization_tracker.json` and
`docs/completion_summary.md` were unproduced *and* unannotated, and therefore a defect.
That claim is false — all three carry `(reserved)`, added deliberately on 2026-07-17 via
`specs/layout-tree-reconciliation.md` (commit `cc46a55`). Those entries are **correctly
accounted for**, and a test encoding the opposite would re-enshrine the false claim.

That spec went wrong by running `line.split("#")[0]` before matching, which discards the
comment column — the only place the annotation lives. So the comment column is
**load-bearing data**, and `test_the_predicate_requires_the_comment_column` pins it
directly on the predicate rather than trusting the extractor to be read correctly.

Three parsing hazards are live in the current tree; each has its own test, because a
later simplification that drops one would otherwise pass silently:

1. The comment column must be kept (above).
2. `backups/` carries a **two-line** comment; the second line has no filename and must not
   become an entry.
3. `docs/stakeholder_summary_module{n}.md` is a **placeholder** — it never appears verbatim
   under `plugins/` (the real files are `stakeholder_summary_module1.md` and
   `_module6.md`), so it resolves on the prefix before `{`.

Stdlib-only and no `plugins/` import (INV-108). The extraction is pure text over
`specs/INVARIANTS.md` and the corpus is read with `pathlib`, so nothing shells out to
`grep` and nothing depends on the platform's path separator — the `/` inside a directory
probe is the tree's own textual convention, matched against file *content*, not a path.

Source: `specs/inv050-tree-has-no-reachability-guard.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"
PLUGINS = REPO_ROOT / "plugins"

TREE_HEADING = "## INV-050: Project layout"

# Box-drawing and whitespace that prefixes a tree entry's name.
BOX_CHARS = " \t│├└─"

# An entry the tree says is deliberately not produced.
ANNOTATION = re.compile(r"reserved|superseded|legacy|future", re.IGNORECASE)

# Derived 2026-08-11 by running extract_tree() against the tree as it then stood, NOT
# copied from any spec -- two specs disagree on this count (one says "53 entries / 23
# files") because they differ on what to include. What these numbers count:
#   * the root line (`senzing-bootcamp/`) is EXCLUDED -- it is the tree's root, not an entry
#   * continuation lines (comment-only, no name) are EXCLUDED from both, counted separately
#   * the placeholder entry `stakeholder_summary_module{n}.md` IS counted, as one file
EXPECTED_FILE_ENTRIES = 24
#: 30 -> 31 on 2026-08-26: `backups/packages/` was added as its own leaf when
#: `/package-bootcamp` began writing transferable archives there
#: (`specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md`). Given its own entry rather
#: than a comment on `backups/` because a comment-only continuation line is not an entry and this
#: is a real directory the plugin writes to -- which is also what keeps INV-202 satisfiable for it.
EXPECTED_DIR_ENTRIES = 31
EXPECTED_CONTINUATION_LINES = 1


class Entry:
    """One leaf of the tree, with its comment column intact."""

    def __init__(self, name, comment, line_number):
        self.name = name
        self.comment = comment
        self.line_number = line_number
        self.is_dir = name.endswith("/")

    @property
    def probe(self):
        """The literal string to look for under `plugins/`.

        A placeholder entry (`stakeholder_summary_module{n}.md`) never appears verbatim,
        so it resolves on the prefix before the brace.
        """
        return self.name.split("{")[0]

    def __repr__(self):
        return "%s (INVARIANTS.md:%d)" % (self.name, self.line_number)


def extract_tree():
    """Return (root_name, entries, continuation_line_count) from INV-050's fenced tree.

    Entries keep their comment. Names are NOT unique -- `data/backups/` and the
    top-level `backups/` both reduce to `backups/` -- so this returns a list and callers
    must never key a dict by name.
    """
    lines = INVARIANTS.read_text(encoding="utf-8").splitlines()
    try:
        heading = next(i for i, l in enumerate(lines) if l.strip() == TREE_HEADING)
    except StopIteration:
        raise AssertionError(
            "%r not found in specs/INVARIANTS.md — INV-050's section was renamed and this "
            "guard can no longer find its tree" % TREE_HEADING
        )
    opening = next(
        i for i in range(heading, len(lines)) if lines[i].strip().startswith("```text")
    )
    closing = next(i for i in range(opening + 1, len(lines)) if lines[i].strip() == "```")

    root, entries, continuations = None, [], 0
    for offset, line in enumerate(lines[opening + 1 : closing]):
        left, _, comment = line.partition("#")
        name = left.strip(BOX_CHARS).strip()
        if not name:
            # A comment-only continuation line (see `backups/`): no entry here.
            continuations += 1
            continue
        if offset == 0:
            root = name
            continue
        entries.append(Entry(name, comment, opening + 2 + offset))
    return root, entries, continuations


def plugin_corpus():
    """Every shipped plugin file's text, joined. Read, not grepped (INV-108)."""
    texts = []
    for path in sorted(PLUGINS.rglob("*")):
        if not path.is_file() or "pytest_cache" in path.parts:
            continue
        try:
            texts.append(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    return "\n".join(texts)


def is_annotated(entry):
    """The comment column says the entry is deliberately not produced."""
    return ANNOTATION.search(entry.comment) is not None


def is_accounted_for(entry, corpus):
    """Referenced under plugins/, OR annotated. Either arm satisfies INV-050."""
    return is_annotated(entry) or entry.probe in corpus


class TreeExtraction(unittest.TestCase):
    """The extractor itself, before anything is concluded from it."""

    def test_the_extraction_found_the_expected_number_of_entries(self):
        """Not vacuous: a parser that silently stops matching passes every other test."""
        _, entries, _ = extract_tree()
        files = [e for e in entries if not e.is_dir]
        dirs = [e for e in entries if e.is_dir]
        self.assertEqual(
            (EXPECTED_FILE_ENTRIES, EXPECTED_DIR_ENTRIES),
            (len(files), len(dirs)),
            "INV-050's tree no longer extracts to the pinned counts. If entries were "
            "genuinely added or removed, update the constants AND the comment saying what "
            "they count. If not, the parser has drifted and every other test in this file "
            "is now checking a shorter list than the tree actually holds.",
        )

    def test_the_root_line_is_not_an_entry(self):
        root, entries, _ = extract_tree()
        self.assertEqual("senzing-bootcamp/", root)
        self.assertNotIn(root, [e.name for e in entries])

    def test_the_continuation_line_is_not_an_entry(self):
        """Hazard 2: `backups/` has a two-line comment; line two has no filename.

        Counted, not merely skipped — if the tree gains a second wrapped comment the
        count changes and this fails, which is the prompt to look.
        """
        _, entries, continuations = extract_tree()
        self.assertEqual(
            EXPECTED_CONTINUATION_LINES,
            continuations,
            "the number of comment-only continuation lines in INV-050's tree changed",
        )
        self.assertEqual(
            [],
            [e for e in entries if "graduation revisit" in e.name],
            "a continuation line was parsed as an entry — its comment text became a name",
        )

    def test_entry_names_are_not_unique(self):
        """`data/backups/` and the top-level `backups/` share a name.

        Pinned so nobody 'simplifies' the extractor into a dict keyed by name: that would
        silently drop one of the two, and the two differ in exactly the way that matters —
        one is annotated `(reserved)`, the other is a real produced directory.
        """
        _, entries, _ = extract_tree()
        names = [e.name for e in entries]
        self.assertNotEqual(
            len(names), len(set(names)),
            "tree entry names are now unique; if that is a real change, this guard can be "
            "relaxed — but a name-keyed dict is still wrong if duplicates ever return",
        )


class AccountedForPredicate(unittest.TestCase):
    """The rule itself, unit-tested on synthetic entries.

    Deliberately independent of what the real tree currently holds, so these keep working
    whatever happens to any particular entry — and so the comment column's role is pinned
    without asserting anything about `session_log.jsonl` and friends.
    """

    def test_the_predicate_requires_the_comment_column(self):
        """Hazard 1: dropping the comment turns an annotated entry into a false defect.

        This is the exact error that produced a spec claiming three correctly-annotated
        entries were a defect: its scan ran `line.split("#")[0]` first.
        """
        corpus = "nothing here mentions the probe"
        unannotated = Entry("zzz_fictional_artifact.json", "", 0)
        annotated = Entry("zzz_fictional_artifact.json", " (reserved)", 0)
        self.assertFalse(
            is_accounted_for(unannotated, corpus),
            "an entry that is neither referenced nor annotated must NOT be accounted for, "
            "or the guard cannot fail on the case it exists for",
        )
        self.assertTrue(
            is_accounted_for(annotated, corpus),
            "an annotated entry must be accounted for even though nothing references it — "
            "if this fails, the comment column is being discarded",
        )

    def test_the_referenced_arm_works_without_an_annotation(self):
        entry = Entry("zzz_fictional_artifact.json", "", 0)
        self.assertTrue(is_accounted_for(entry, "see zzz_fictional_artifact.json here"))

    def test_a_placeholder_resolves_on_its_prefix(self):
        """Hazard 3: the literal name with `{n}` matches nothing."""
        entry = Entry("stakeholder_summary_module{n}.md", "", 0)
        self.assertEqual("stakeholder_summary_module", entry.probe)
        self.assertTrue(
            is_accounted_for(entry, "writes stakeholder_summary_module1.md at the end"),
            "a placeholder entry must resolve via its prefix; probing the literal name "
            "reports it unaccounted and invents a defect",
        )


class TreeIsFullyAccountedFor(unittest.TestCase):
    """INV-050 against what ships."""

    @classmethod
    def setUpClass(cls):
        cls.corpus = plugin_corpus()
        cls.entry_list = extract_tree()[1]

    def test_the_corpus_scan_is_not_vacuous(self):
        """An empty corpus would make every entry look unreferenced (or vice versa)."""
        self.assertGreater(
            len(self.corpus), 500_000,
            "the plugin corpus came back far too small; the glob has drifted and the "
            "referenced-arm of every check below is meaningless",
        )

    def test_every_entry_is_referenced_or_annotated(self):
        unaccounted = [
            e for e in self.entry_list if not is_accounted_for(e, self.corpus)
        ]
        self.assertEqual(
            [],
            unaccounted,
            "INV-050 lists artifact(s) that nothing under plugins/ produces or reads, and "
            "that carry no annotation saying so:\n  "
            + "\n  ".join(repr(e) for e in unaccounted)
            + "\nEither produce it, or annotate it in the tree with a dated reason "
            "(`# … (reserved)`) the way the existing unproduced entries are. Do not "
            "delete the entry: INV-050 is cited widely and quoted in audits.",
        )

    def test_the_placeholder_entry_is_still_a_placeholder(self):
        """Guard the guard: if the tree stops using `{n}`, hazard 3's test is theater."""
        placeholders = [e for e in self.entry_list if "{" in e.name]
        self.assertTrue(
            placeholders,
            "no placeholder entry remains in the tree; "
            "test_a_placeholder_resolves_on_its_prefix now proves nothing about it",
        )
        for entry in placeholders:
            with self.subTest(entry=entry.name):
                self.assertNotIn(
                    entry.name, self.corpus,
                    "the literal placeholder name now appears under plugins/, so the "
                    "prefix probe is no longer what makes this entry resolve",
                )
                self.assertIn(entry.probe, self.corpus)


if __name__ == "__main__":
    unittest.main()
