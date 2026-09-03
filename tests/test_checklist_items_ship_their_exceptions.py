"""A checklist item the Bootcamper works through unattended carries its own exception.

Enforces **INV-287** — where the SBCP ships a rule into an artifact the Bootcamper acts on
without the guide present, and that rule has a known site where following it is wrong, the
exception ships in the **same item** as the rule.

The instance: graduation writes `production/MIGRATION_CHECKLIST.md`, whose Performance
section tells the Bootcamper to replace ``*_DEFAULT_FLAGS`` composites in
``production/src/`` with explicit flags. On the **export call** that instruction is the
composition Module 6 observed returning rows with no ``RELATED_ENTITIES`` key at all and no
error — a graph with nodes and no edges.

⚠️ **What makes this checkable is WHERE the exception sits, not whether it exists.** The
guidance around the item is instruction to the guide and never travels; only the quoted
item text is copied into the Bootcamper's checklist. An exception in the surrounding prose
satisfies a reader of this file and reaches nobody ticking the box, which is exactly the
failure INV-287 names — so the assertions read the QUOTED ITEM, and the negative control
that matters moves the exception out of the quote into the prose beside it.

⚠️ **This guard asserts the INSTANCE, not the class.** INV-287 binds any unattended
artifact carrying a rule with a known wrong site; which rules have such a site is not
mechanically derivable, so no scan can enumerate them. The item itself is located by
scanning rather than by line number, so it survives being moved or renumbered.

Registered 2026-09-02 with no enforcer, which the invariant said outright. This closes
that, and it was not going to resurface on its own: `coverage_reports.py invariants`
counts any test mentioning an id as coverage, and a comment in
`test_invariant_enforcer_citations.py` names INV-287 to explain why it adds no pair — so
the one invariant with no guard was the one the gap report did not list.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GRADUATION = REPO / "plugins" / "senzing-bootcamp" / "skills" / "graduation" / "SKILL.md"

#: The quoted text of a MIGRATION_CHECKLIST item — the part copied into the Bootcamper's
#: file. Everything outside the quotes is guidance to the guide and does not travel.
# ⚠️ ``re.S`` is load-bearing: the item is hand-wrapped across five lines, so a pattern
# without it matches nothing and every assertion below goes vacuous behind a green run.
QUOTED_ITEM = re.compile(r'\*"(.+?)"\*', re.S)


def flat(text):
    return re.sub(r"\s+", " ", text).strip()


def default_flags_item():
    """The quoted checklist item about DEFAULT composites, located by scanning.

    Returns (quoted_text, surrounding_bullet). Hardcoding a line number would make this
    guard follow the file's shape rather than its content (INV-246).
    """
    text = GRADUATION.read_text(encoding="utf-8")
    for m in QUOTED_ITEM.finditer(text):
        quoted = flat(m.group(1))
        if "_DEFAULT_FLAGS" in quoted and "production/src/" in quoted:
            start = text.rfind("\n  - ", 0, m.start())
            end = text.find("\n  - ", m.end())
            return quoted, flat(text[start: end if end != -1 else len(text)])
    return None, None


class TheChecklistItemShipsItsException(unittest.TestCase):
    def setUp(self):
        self.quoted, self.bullet = default_flags_item()

    def test_the_item_is_found(self):
        """A scan matching nothing would make every assertion below vacuous."""
        self.assertIsNotNone(
            self.quoted,
            "no quoted MIGRATION_CHECKLIST item about replacing *_DEFAULT_FLAGS in "
            "production/src/ was found in graduation/SKILL.md. Either the item was removed "
            "— which INV-287's site would then no longer exist — or its shape changed and "
            "this guard has stopped reading it.",
        )

    def test_the_exception_is_inside_the_quoted_item(self):
        """⛔ The assertion INV-287 is actually about.

        Not "does the file mention the export call" — the file plainly does, in the ⛔
        beneath. The question is whether the Bootcamper, who receives only the quoted text,
        gets it.
        """
        self.assertRegex(
            self.quoted, r"(?i)except the export call",
            "the export-call exception is not inside the quoted checklist item. Only the "
            "quote is copied into production/MIGRATION_CHECKLIST.md; guidance around it "
            "reaches the guide and never the Bootcamper ticking the box. An exception "
            "recorded beside the item is not shipped with it (INV-287).",
        )

    def test_the_exception_names_the_consequence_not_just_the_carve_out(self):
        """A carve-out with no reason is one a later editor tidies away as noise."""
        self.assertRegex(
            self.quoted, r"(?i)RELATED_ENTITIES",
            "the exception must say what following the rule costs on the export call — "
            "dropping RELATED_ENTITIES entirely. 'except the export call' alone gives a "
            "reader nothing to weigh and reads as an arbitrary special case.",
        )

    def test_the_exception_says_the_failure_is_silent(self):
        self.assertRegex(
            self.quoted, r"(?i)with no error|no error is raised|silently",
            "the exception must say the failure is SILENT. A Bootcamper who expects an "
            "error will read an empty graph as empty data, which is the whole reason this "
            "cannot be left to be discovered at runtime.",
        )

    def test_the_item_still_states_the_general_rule_it_excepts(self):
        """The exception must qualify the rule, not replace it."""
        self.assertRegex(
            self.quoted, r"(?i)replace `?\*_DEFAULT_FLAGS",
            "the item must still carry the general instruction. An item reduced to its "
            "exception no longer tells the Bootcamper what to do everywhere else.",
        )


if __name__ == "__main__":
    unittest.main()
