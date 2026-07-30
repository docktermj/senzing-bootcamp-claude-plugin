"""`INVARIANTS.md`'s topical index stays complete and truthful.

The 142 development rules (INV-051 onward) live in one flat, append-ordered section, and
they are what a developer consults for what to do, what not to do, and how to handle an
ambiguous case. Append order is correct — IDs are permanent addresses cited 4,614 times in
live files and 753 times in commit messages — so the index, not the ordering, is the way
in.

An index that silently rots is worse than none, because it will be trusted: a developer
who does not find a rule under its subject concludes no such rule exists. So both
directions are enforced here. Every invariant is indexed, and every indexed ID is real.

The first 50 are deliberately out of scope: they are the bootcamp's own outcomes (median
15 words, 8 of 50 stating a MUST) and are already grouped into their own sections.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"

#: Below this ID the entries are bootcamp outcomes, grouped in their own sections.
FIRST_DEV_RULE = 51

DEFINITION = re.compile(r"(?m)^- \*\*INV-(\d{3})\*\*")
GROUP_LINE = re.compile(r"(?m)^- \*\*(?P<name>[^*]+)\*\* — [^\n]*\n\s+(?P<ids>INV-\d{3}(?:, INV-\d{3})*)")


def text():
    return INVARIANTS.read_text(encoding="utf-8")


def defined_ids():
    return {int(n) for n in DEFINITION.findall(text())}


def index_section():
    body = text()
    start = body.find("### Index by subject")
    if start < 0:
        return ""
    end = body.find("<!-- New invariants go directly below this line.", start)
    return body[start:end if end > start else len(body)]


def indexed_groups():
    """{group name: [invariant numbers]} as the index actually reads."""
    out = {}
    for match in GROUP_LINE.finditer(index_section()):
        out[match.group("name").strip()] = [
            int(i[4:]) for i in match.group("ids").split(", ")
        ]
    return out


class TheIndexExists(unittest.TestCase):
    def test_it_is_present_and_placed_before_the_append_marker(self):
        body = text()
        self.assertIn("### Index by subject", body)
        self.assertLess(
            body.find("### Index by subject"),
            body.find("<!-- New invariants go directly below this line."),
            "the index must sit above the append marker, or appended invariants land inside it",
        )

    def test_it_parses_into_groups(self):
        groups = indexed_groups()
        self.assertGreaterEqual(len(groups), 5, "index did not parse; the format has drifted")

    def test_the_scan_is_not_vacuous(self):
        """A regex that stops matching would make every check below pass silently."""
        self.assertGreater(len(defined_ids()), 100)
        self.assertGreater(sum(len(v) for v in indexed_groups().values()), 100)


class EveryDevelopmentRuleIsIndexed(unittest.TestCase):
    """The direction that matters when someone appends a rule and forgets the index."""

    def test_no_invariant_is_missing_from_the_index(self):
        expected = {n for n in defined_ids() if n >= FIRST_DEV_RULE}
        listed = {n for ids in indexed_groups().values() for n in ids}
        missing = sorted(expected - listed)
        self.assertEqual(
            [], missing,
            "invariant(s) defined but not indexed — add each to its group in "
            "`### Index by subject`, in the same edit that appends it:\n  "
            + "  ".join("INV-%03d" % n for n in missing),
        )

    def test_each_appears_in_exactly_one_group(self):
        seen = {}
        for name, ids in indexed_groups().items():
            for n in ids:
                seen.setdefault(n, []).append(name)
        multiple = {n: g for n, g in seen.items() if len(g) > 1}
        self.assertEqual(
            {}, multiple,
            "invariant(s) in more than one group — a rule with two homes is found by "
            "neither reader reliably: %s" % multiple,
        )


class TheIndexNamesNothingImaginary(unittest.TestCase):
    """The direction that matters after a merge or a supersede."""

    def test_every_indexed_id_is_defined(self):
        defined = defined_ids()
        listed = {n for ids in indexed_groups().values() for n in ids}
        unknown = sorted(listed - defined)
        self.assertEqual(
            [], unknown,
            "index names invariant(s) that do not exist: "
            + "  ".join("INV-%03d" % n for n in unknown),
        )

    def test_the_bootcamp_outcomes_are_not_indexed_here(self):
        """INV-001..050 are a different genre with their own sections; mixing them in
        would bury the development rules this index exists to surface."""
        listed = {n for ids in indexed_groups().values() for n in ids}
        early = sorted(n for n in listed if n < FIRST_DEV_RULE)
        self.assertEqual([], early, "bootcamp-outcome invariants leaked into the index: %s" % early)


class TheMaintenanceRuleTellsAppendersAboutIt(unittest.TestCase):
    """A guard nobody knows about gets tripped rather than followed."""

    def test_adding_an_invariant_says_to_update_the_index(self):
        body = text()
        rule = body[body.find("## Maintaining this file"):body.find("## INV-001")]
        self.assertIn("Index by subject", rule)
        self.assertRegex(rule, r"(?i)same edit")


if __name__ == "__main__":
    unittest.main()
