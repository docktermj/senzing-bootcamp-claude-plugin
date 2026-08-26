"""The documented slash-command set equals the shipped one, in both directions.

`plugins/senzing-bootcamp/commands/` is the shipped set — Claude Code discovers `commands/*.md`
by convention, and `.claude-plugin/plugin.json` correctly does not enumerate them. The documented
set is a hand-maintained table in `docs/README.md`. Nothing compared them, so they drifted:

    docs/README.md:76  "The plugin ships three slash commands."   <- five ship
    docs/README.md      table lists 3                              <- /bootcamp-note and
                                                                      /package-bootcamp absent
    README.md:92        "See [Bootcamp commands] for the other two."

⛔ **A prior audit already found and fixed this class** — *"two of three shipped slash commands
documented nowhere"*. It recurred because that fix wrote the missing rows instead of pinning the
set. So this test compares sets, and pins nothing else.

⛔ **No count is asserted anywhere in this file, deliberately.** A test that pins "five commands"
fails on the next legitimate addition and teaches whoever fixes it to bump a number — reproducing
the defect inside the guard. The two sets are derived and compared; their size is not the subject.

⚠️ **Both directions matter.** A documented command that no longer ships is equally wrong, and it
is the direction a delete-and-forget produces — the reader is told to run something that does not
exist.

Stdlib only; the commands directory listed and the docs read as text (INV-108).

Source spec: `specs/the-documented-command-set-has-drifted-from-the-shipped-one.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = REPO_ROOT / "plugins" / "senzing-bootcamp" / "commands"
USER_DOCS = REPO_ROOT / "docs" / "README.md"
TOP_README = REPO_ROOT / "README.md"

#: A table row's command cell: `| `/name` | … |`
ROW = re.compile(r"^\|\s*`(/[a-z0-9-]+)`\s*\|", re.M)

#: Prose asserting how many commands there are. The habit that produced two stale counts.
COUNT_CLAIM = re.compile(
    r"(?i)ships\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+slash\s+commands"
    r"|for the other\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b")


def shipped_commands():
    return {"/" + path.stem for path in COMMANDS_DIR.glob("*.md")}


def documented_commands():
    return set(ROW.findall(USER_DOCS.read_text(encoding="utf-8")))


class NeitherSetIsEmpty(unittest.TestCase):
    """INV-265 — a set comparison is satisfied trivially when both sides are empty."""

    def test_commands_were_found_on_disk(self):
        shipped = shipped_commands()
        self.assertGreaterEqual(
            len(shipped), 3,
            "fewer than three command files were found in %s; the glob has drifted and the "
            "comparison below proves nothing" % COMMANDS_DIR)
        self.assertIn("/start-bootcamp", shipped,
                      "the command glob is missing one certainly present; the pattern is wrong")

    def test_the_table_parsed(self):
        documented = documented_commands()
        self.assertGreaterEqual(
            len(documented), 3,
            "the command table in docs/README.md parsed to fewer than three rows; the row "
            "pattern has drifted from the table's shape")
        self.assertIn("/start-bootcamp", documented)


class TheTwoSetsAgree(unittest.TestCase):
    def test_every_shipped_command_is_documented(self):
        missing = sorted(shipped_commands() - documented_commands())
        self.assertEqual(
            [], missing,
            "shipped slash command(s) absent from docs/README.md's table: %s. A Bootcamper "
            "reading the documentation cannot discover them" % ", ".join(missing))

    def test_every_documented_command_ships(self):
        """The delete-and-forget direction: the reader told to run something that is gone."""
        phantom = sorted(documented_commands() - shipped_commands())
        self.assertEqual(
            [], phantom,
            "docs/README.md documents command(s) that do not ship: %s" % ", ".join(phantom))


class NoDocumentStatesACount(unittest.TestCase):
    """A count in prose is a positive false statement the moment a command is added."""

    def test_the_user_docs_state_no_count(self):
        hit = COUNT_CLAIM.search(USER_DOCS.read_text(encoding="utf-8"))
        self.assertIsNone(
            hit, "docs/README.md states a number of slash commands (%r); state the set, not a "
                 "count -- the number goes stale silently while reading authoritative"
                 % (hit.group(0) if hit else ""))

    def test_the_top_readme_states_no_count(self):
        hit = COUNT_CLAIM.search(TOP_README.read_text(encoding="utf-8"))
        self.assertIsNone(
            hit, "README.md states a number of slash commands (%r)"
                 % (hit.group(0) if hit else ""))


if __name__ == "__main__":
    unittest.main()
