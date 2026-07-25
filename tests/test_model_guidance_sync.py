"""Tests that the per-stage model/effort recommendation stays consistent.

The INV-063 module-start nudge names a recommended model in two places that must
agree: the operational table in `skills/bootcamp-onboarding/ground-rules.md` (the
file the guide actually loads at module start) and the maintainer reference in
`docs/model-selection.md`. `ground-rules.md` even carries a "keep in sync"
instruction — but nothing enforced it, and the pair drifted a full model
generation behind before a bootcamper reported it.

These tests are the enforcement:

1. No superseded model name or ID survives anywhere in the shipped plugin.
2. The two per-stage tables agree row for row.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")
GROUND_RULES = os.path.join(PLUGIN, "skills", "bootcamp-onboarding", "ground-rules.md")
MODEL_SELECTION = os.path.join(PLUGIN, "docs", "model-selection.md")

# Model names/IDs that have been superseded. A hit means the recommendation would
# tell a bootcamper to switch *down* from the current model — the defect this
# guards. Add a row whenever a model is superseded; the last element of each pair
# is the current replacement, quoted in the failure message.
SUPERSEDED = [
    ("Opus 4.8", "Opus 5"),
    ("claude-opus-4-8", "claude-opus-5"),
]

# The one file allowed to name a superseded model: the staleness note in
# docs/model-selection.md deliberately cites the prior model to explain that
# Opus 5 inherited its price. Scoped to that file so it can't become a loophole.
STALENESS_NOTE_FILE = os.path.join(PLUGIN, "docs", "model-selection.md")

TABLE_HEADER = "| Stage | Recommended | CLI commands |"


# Repo-level user-facing docs. Included because a rename or model refresh that
# lands only inside plugins/ leaves these contradicting it — the exact
# "renamed in one place" defect. `specs/`, `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_*.md`,
# and `specs/IMPLEMENTED.md` are deliberately NOT scanned: they are historical
# records and must keep naming what was true when written.
REPO_DOCS = [
    os.path.join(REPO_ROOT, "README.md"),
    os.path.join(REPO_ROOT, "docs", "README.md"),
]


def shipped_markdown():
    """Every Markdown file under the shipped plugin, plus repo-level user docs."""
    for dirpath, dirnames, filenames in os.walk(PLUGIN):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)
    for path in REPO_DOCS:
        if os.path.exists(path):
            yield path


def stage_table(path):
    """Extract the per-stage recommendation table as a list of cell-tuples.

    Tolerates leading indentation: the ground-rules copy is nested inside a
    bullet, the model-selection copy sits at column zero.
    """
    with open(path, encoding="utf-8") as fh:
        lines = [line.strip() for line in fh]
    if TABLE_HEADER not in lines:
        raise AssertionError(f"per-stage table header not found in {path}")
    start = lines.index(TABLE_HEADER)
    rows = []
    for line in lines[start + 2:]:  # skip header + separator
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        if set("".join(cells)) <= {"-", ":"}:  # a second separator row
            continue
        rows.append(tuple(cells))
    if not rows:
        raise AssertionError(f"per-stage table in {path} has no rows")
    return rows


class NoSupersededModelReferences(unittest.TestCase):
    """A superseded model name would recommend downgrading — never ship one."""

    def test_no_superseded_names_or_ids(self):
        offenders = []
        for path in shipped_markdown():
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for stale, current in SUPERSEDED:
                if stale not in text:
                    continue
                if path == STALENESS_NOTE_FILE:
                    continue  # documents the supersession on purpose
                rel = os.path.relpath(path, REPO_ROOT)
                offenders.append(f"{rel}: '{stale}' should be '{current}'")
        self.assertEqual(
            offenders, [], "superseded model references found:\n  " + "\n  ".join(offenders)
        )

    def test_switch_command_names_a_current_model(self):
        # The copy-pasteable switch command is a functional string: if the display
        # name moves without the ID, the pasted command selects the old model.
        with open(MODEL_SELECTION, encoding="utf-8") as fh:
            text = fh.read()
        for match in re.finditer(r"/model (claude-[a-z0-9-]+)", text):
            model_id = match.group(1)
            stale_ids = [stale for stale, _ in SUPERSEDED if stale == model_id]
            self.assertEqual(
                stale_ids, [], f"/model {model_id} names a superseded model"
            )


class StageTablesAgree(unittest.TestCase):
    """The operational table and the maintainer reference must not drift."""

    def test_tables_are_identical(self):
        self.assertEqual(
            stage_table(GROUND_RULES),
            stage_table(MODEL_SELECTION),
            "the per-stage model/effort tables in ground-rules.md and "
            "docs/model-selection.md have drifted — update both",
        )

    def test_every_row_names_a_model_and_an_effort(self):
        for stage, recommended, commands in stage_table(GROUND_RULES):
            self.assertTrue(stage, "a stage row has an empty stage name")
            self.assertIn("effort", recommended, f"{stage!r}: no effort named")
            self.assertIn("/model", commands, f"{stage!r}: no /model command")
            self.assertIn("/effort", commands, f"{stage!r}: no /effort command")


class StalenessNotePresent(unittest.TestCase):
    """Point-in-time data must say so, with the date it was checked."""

    def test_note_carries_a_verification_date(self):
        with open(MODEL_SELECTION, encoding="utf-8") as fh:
            text = fh.read()
        self.assertRegex(
            text,
            r"last verified \d{4}-\d{2}-\d{2}",
            "docs/model-selection.md must carry a dated 'last verified' note",
        )


if __name__ == "__main__":
    unittest.main()
