"""Every path the dry-run scaffold fabricates must be a path the plugin actually uses.

The scaffold builds a mid-bootcamp fixture tree so phase 2 can run the hooks and bundled
scripts against something realistic. A fixture at a filename the plugin never reads is
worse than no fixture: it looks like coverage. `--explain` says so itself — "Every fixture
is here because a naive one hid a defect".

One had drifted. The scaffold wrote `src/system_verification/records.jsonl`; System
verification Step 2 writes `src/system_verification/verification_data.jsonl`, and that is
the only spelling `plugins/` contains. So a mid-bootcamp dry run started *without* the file
the plugin looks for, and the fixture that exists to catch resume defects could not.

Nothing caught it because the scaffold is a maintainer tool under `.claude/` while the
repo's tests cover `plugins/`. This file closes that specific gap in the general form: a
project-relative path named in `FIXTURE_MAP` must appear somewhere under `plugins/`.

Stdlib only, and it never imports from `plugins/` (INV-108); the scaffold is loaded by
file path because `.claude/skills/dry-run` is not an importable package.

Source spec: `specs/dry-run-scaffold-uses-a-verification-filename-the-plugin-never-writes.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = REPO_ROOT / ".claude" / "skills" / "dry-run" / "scaffold_project.py"
PLUGINS = REPO_ROOT / "plugins"

#: Directories whose contents are build artifacts, not plugin sources.
SKIP_DIRS = {"__pycache__", ".pytest_cache"}


def load_scaffold():
    spec = importlib.util.spec_from_file_location("dry_run_scaffold", SCAFFOLD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plugin_corpus():
    """Every readable file under `plugins/`, concatenated. Big, but read once."""
    chunks = []
    for path in sorted(PLUGINS.rglob("*")):
        if not path.is_file() or SKIP_DIRS & set(path.parts):
            continue
        try:
            chunks.append(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, OSError):
            continue          # binary asset; it cannot name a path
    return "\n".join(chunks)


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_scaffold_is_where_this_test_thinks_it_is(self):
        self.assertTrue(SCAFFOLD.is_file(), "scaffold_project.py moved")

    def test_the_fixture_map_is_populated(self):
        rows = load_scaffold().FIXTURE_MAP
        self.assertGreater(len(rows), 5, "FIXTURE_MAP looks empty — did its shape change?")

    def test_the_corpus_is_real(self):
        corpus = plugin_corpus()
        self.assertGreater(len(corpus), 100_000,
                           "the plugins/ corpus came back tiny; a path check against it "
                           "would pass by finding nothing to contradict")


class EveryFixturePathIsAPathThePluginUses(unittest.TestCase):
    def setUp(self):
        self.rows = load_scaffold().FIXTURE_MAP
        self.corpus = plugin_corpus()

    def test_each_path_appears_somewhere_under_plugins(self):
        checked = 0
        for display, path, modes, _why in self.rows:
            if path is None:
                continue          # a row annotating a key inside another fixture
            checked += 1
            with self.subTest(path=path):
                self.assertIn(
                    path, self.corpus,
                    "the scaffold writes %r (row %r, modes %s) and no file under "
                    "plugins/ names that path — the fixture exercises something the "
                    "plugin never touches" % (path, display, sorted(modes)))
        self.assertGreater(checked, 5, "almost no rows carried a path to check")

    def test_the_verification_records_fixture_uses_the_plugins_spelling(self):
        """The specific drift, named, so a revert is unambiguous rather than generic."""
        paths = {row[1] for row in self.rows if row[1]}
        self.assertIn("src/system_verification/verification_data.jsonl", paths,
                      "the System verification fixture is not at the filename Step 2 writes")
        self.assertNotIn("src/system_verification/records.jsonl", paths,
                         "records.jsonl is a filename the plugin never uses")


class TheFixtureMatchesWhatStepTwoAsksFor(unittest.TestCase):
    """A right filename holding the wrong shape resumes into different nonsense."""

    def setUp(self):
        import json
        self.records = [json.loads(line)
                        for line in load_scaffold().RECORDS.splitlines() if line.strip()]

    def test_at_least_four_records(self):
        self.assertGreaterEqual(len(self.records), 4,
                                "Step 2 requires at least 4 records")

    def test_every_record_is_the_verify_source_with_a_unique_id(self):
        self.assertEqual({"VERIFY"}, {r["DATA_SOURCE"] for r in self.records},
                         "Step 2 gives every record a DATA_SOURCE of VERIFY")
        ids = [r["RECORD_ID"] for r in self.records]
        self.assertEqual(len(ids), len(set(ids)), "RECORD_IDs must be unique")

    def test_there_is_a_merge_cluster_and_a_distractor(self):
        names = [f["NAME_FULL"]
                 for r in self.records for f in r["FEATURES"] if "NAME_FULL" in f]
        self.assertEqual(len(self.records), len(names), "every record needs a name")
        surnames = [n.rsplit(" ", 1)[-1] for n in names]
        biggest = max(surnames.count(s) for s in set(surnames))
        self.assertGreaterEqual(biggest, 2,
                                "no merge cluster: no two records share a surname")
        self.assertGreaterEqual(len(set(surnames)), 2,
                                "no distractor: every record is the same person, so "
                                "nothing has to stay a singleton")

    def test_features_are_nested_and_addresses_are_not_mixed(self):
        """Entity Specification: features live in FEATURES; ADDR_FULL is never mixed with
        parsed ADDR_* fields in the same object (server 1.32.9, 2026-08-14)."""
        for record in self.records:
            with self.subTest(record_id=record["RECORD_ID"]):
                self.assertIsInstance(record.get("FEATURES"), list)
                for feature in record["FEATURES"]:
                    if "ADDR_FULL" in feature:
                        parsed = [k for k in feature
                                  if k.startswith("ADDR_") and k not in ("ADDR_FULL",
                                                                         "ADDR_TYPE")]
                        self.assertEqual([], parsed,
                                         "ADDR_FULL mixed with parsed address fields")

    def test_the_records_carry_no_root_level_features(self):
        """The old fixture put PRIMARY_NAME_FULL/ADDR_FULL at the record root."""
        for record in self.records:
            with self.subTest(record_id=record["RECORD_ID"]):
                self.assertEqual({"DATA_SOURCE", "RECORD_ID", "FEATURES"},
                                 set(record),
                                 "features belong in FEATURES, not at the record root")


if __name__ == "__main__":
    unittest.main()
