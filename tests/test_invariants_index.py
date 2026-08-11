"""`INVARIANTS.md`'s topical index stays complete and truthful.

The development rules (INV-051 onward) live in one flat, append-ordered section, and they
are what a developer consults for what to do, what not to do, and how to handle an
ambiguous case. Append order is correct — IDs are permanent addresses, cited in thousands of
live files and in commit messages that cannot be edited — so the index, not the ordering, is
the way in.

Counts are deliberately absent from this docstring and from the index prose. Earlier versions
carried them ("142 development rules", "4,614 citations", "22 superseded") and every one had
drifted by 2026-07-31, because nothing couples a sentence to an append while the checks below
couple the ID list to every one. Derive a figure when you need it; do not pin one here.

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
#: A group is a `- **Name** — gloss.` line followed by one or more indented ID lines: the
#: live rules, and optionally a second line of superseded ones. Both count as indexed —
#: a retired rule still needs a home, or the "exactly one group" check cannot be total.
GROUP_BLOCK = re.compile(r"(?m)^- \*\*(?P<name>[^*]+)\*\* — .*?(?=^- \*\*|\Z)", re.DOTALL)


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


def ids_in(fragment):
    """Invariant numbers *listed* in an index fragment, ignoring parentheticals.

    A supersession note names the ID that replaced the rule — "INV-104 (its tab enumeration
    only -> INV-155)". Those are references, not entries: counting them puts INV-155 in a
    group it does not belong to and breaks the exactly-one-group check. So parentheticals are
    stripped before the IDs are read.
    """
    return [int(n) for n in re.findall(r"INV-(\d{3})", re.sub(r"\([^)]*\)", " ", fragment))]


def indexed_groups():
    """{group name: [invariant numbers]} as the index actually reads.

    Live, fully-superseded and partly-superseded IDs are all collected: a retired rule still
    occupies a group, so the completeness check stays total and a supersession cannot quietly
    drop a rule out of the index.
    """
    return {
        match.group("name").strip(): ids_in(match.group(0))
        for match in GROUP_BLOCK.finditer(index_section())
    }


#: The index's two supersession sublists. The distinction is the whole point: a fully
#: superseded rule may be skipped, a partly superseded one may not, and for several of the
#: latter the invariant is still the only statement of what it requires.
FULL_LABEL = "*Fully superseded"
PART_LABEL = "*Partly superseded"


def _sublist(label):
    """{group name: [invariant numbers]} for one supersession sublist."""
    out = {}
    for match in GROUP_BLOCK.finditer(index_section()):
        for line in match.group(0).splitlines():
            if line.strip().startswith(label):
                out.setdefault(match.group("name").strip(), []).extend(ids_in(line))
    return out


def fully_superseded_in_index():
    return _sublist(FULL_LABEL)


def partly_superseded_in_index():
    return _sublist(PART_LABEL)


#: Any supersession claim at all, in the invariant's own text.
ANY_SUPERSESSION = re.compile(r"superseded by INV", re.I)

#: The invariant says only *part* of it was replaced, or that a later rule brought it back.
#: Both mean a reader must not skip it. Sourced from the six real cases as at 2026-07-31:
#: a named scope noun before the supersession (INV-079 "heading clause", INV-086 "framing",
#: INV-104 "tab enumeration", INV-137 "Trigger"), an explicit stands-otherwise clause, or a
#: restoration (INV-063/INV-069, both reinstated by INV-137).
PARTIAL_SUPERSESSION = re.compile(
    r"\b(?:clause|framing|trigger|enumeration)\b[^.)]{0,70}superseded by INV"
    r"|otherwise stands"
    r"|stands unchanged"
    r"|everything else in this invariant"
    r"|every other guarantee here stands"
    r"|restores this"
    r"|once again the behaviou?r",
    re.I,
)


def _invariant_bodies():
    """{number: single-line body}, emphasis stripped so `**superseded by**` still matches."""
    pairs = re.findall(r"^- \*\*INV-(\d{3})\*\* — (.+?)(?=\n- \*\*INV-|\n##|\Z)",
                       text(), re.M | re.S)
    return {int(n): re.sub(r"\s+", " ", body.replace("**", "")) for n, body in pairs}


def classify_from_the_invariants():
    """(fully, partly) as the invariants describe *themselves*, for development rules."""
    full, part = set(), set()
    for number, body in _invariant_bodies().items():
        if number < FIRST_DEV_RULE or not ANY_SUPERSESSION.search(body):
            continue
        (part if PARTIAL_SUPERSESSION.search(body) else full).add(number)
    return full, part


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


class SupersessionIsMarkedByDegreeNotAsABinary(unittest.TestCase):
    """Marking superseded rules is the compaction: the text stays, the reading path shrinks.

    But "superseded" is not one state, and treating it as one is how the index came to tell
    readers to **skip five invariants that still bind** (found 2026-07-31). INV-079, INV-086
    and INV-137 each had a single clause replaced — INV-138 says outright that "every other
    part of INV-137 is unchanged and still binding" — and INV-063/INV-069 were superseded and
    then *restored* by INV-137, with INV-098 and INV-114 citing both as live authority. All
    five sat under "Superseded — skip these", and for three of them the invariant is the only
    statement of what it requires.

    The previous version of this class could not see it: `actual()` matched any occurrence of
    "superseded by INV" in an invariant's body, so a partial supersession and a total one were
    indistinguishable and the misclassification passed. The binary model was in the guard as
    well as in the index, which is why the defect survived a test written to catch exactly it.
    """

    def marked_full(self):
        return {n for ids in fully_superseded_in_index().values() for n in ids}

    def marked_part(self):
        return {n for ids in partly_superseded_in_index().values() for n in ids}

    def test_every_supersession_claim_is_marked_somewhere(self):
        full, part = classify_from_the_invariants()
        missing = sorted((full | part) - (self.marked_full() | self.marked_part()))
        self.assertEqual(
            [], missing,
            "the invariant claims a supersession but the index marks none — a reader meets a "
            "retired or partly-retired rule with no warning: "
            + "  ".join("INV-%03d" % n for n in missing),
        )

    def test_nothing_is_marked_fully_superseded_that_is_only_partly(self):
        """The defect this class exists for: a "skip this" on a rule that still binds."""
        _full, part = classify_from_the_invariants()
        wrong = sorted(self.marked_full() & part)
        self.assertEqual(
            [], wrong,
            "marked fully superseded, but the invariant says only part of it was replaced or "
            "that it was restored — the index is telling readers to skip a binding rule: "
            + "  ".join("INV-%03d" % n for n in wrong),
        )

    def test_a_generalised_invariant_points_forward_to_the_rule_that_generalised_it(self):
        """A one-sided generalisation leaves the older rule reading as complete.

        Added 2026-08-11 (`compact-dev-environment`). Three invariants were found declaring
        "Generalises INV-NNN" with the older invariant saying nothing back: INV-195→INV-101,
        INV-089→INV-083, INV-183→INV-164. INV-101 was the costly one — a reader following it
        alone writes Docker-only lifecycle dispatch, which INV-195 forbids.

        No existing check could see it. `ANY_SUPERSESSION` matches only the passive
        "superseded by INV", so an active "Generalises INV-101" in the *newer* invariant
        registers nothing against the older one. This is INV-104's failure shape one level
        up: the index was truthful about every rule it knew was superseded, and silent about
        a rule whose scope had been overtaken in the other direction.

        Deliberately scoped to **generalisation only**. Measured the same day: 4 Generalises
        pairs (all now closed) against 39 Extends/Hardens/Complements pairs, none of which
        point back — and none of which needs to. Those add to a rule that stays correct
        standalone; a generalisation overtakes the older rule's scope, which is what makes
        reading it alone actively wrong. Requiring bidirectionality on all 39 would put seven
        forward pointers on INV-115 and buy nothing.
        """
        bodies = _invariant_bodies()
        pairs = [
            (newer, older)
            for newer, body in bodies.items()
            for older in {int(x) for x in re.findall(r"Generali[sz]e?s?\s+INV-(\d{3})", body, re.I)}
        ]
        self.assertGreaterEqual(
            len(pairs), 4,
            "the generalisation scan found almost nothing — the wording or regex has drifted "
            "and this check would pass vacuously",
        )
        missing = sorted(
            (older, newer) for newer, older in pairs
            if older in bodies and "INV-%03d" % newer not in bodies[older]
        )
        self.assertEqual(
            [], missing,
            "an invariant is generalised by a later one but says nothing about it, so it "
            "reads as complete: "
            + "  ".join("INV-%03d (generalised by INV-%03d)" % (o, n) for o, n in missing),
        )

    def test_the_full_list_matches_what_the_invariants_declare(self):
        full, _part = classify_from_the_invariants()
        self.assertEqual(
            sorted(full), sorted(self.marked_full()),
            "the fully-superseded sublist disagrees with the invariants' own text",
        )

    def test_the_partial_list_matches_what_the_invariants_declare(self):
        _full, part = classify_from_the_invariants()
        self.assertEqual(
            sorted(part), sorted(self.marked_part()),
            "the partly-superseded sublist disagrees with the invariants' own text",
        )

    def test_a_partly_superseded_rule_is_never_also_listed_as_live(self):
        """INV-104's failure mode, the mirror image: listed live, so its dead tab
        enumeration reads as authoritative."""
        for number in sorted(self.marked_part()):
            with self.subTest(invariant="INV-%03d" % number):
                for name, ids in indexed_groups().items():
                    block = next(m.group(0) for m in GROUP_BLOCK.finditer(index_section())
                                 if m.group("name").strip() == name)
                    live_ids = [n for l in block.splitlines()
                                if "INV-" in l and not l.strip().startswith("*")
                                for n in ids_in(l)]
                    self.assertNotIn(
                        number, live_ids,
                        "%s is partly superseded but also listed as live in %r" % (
                            "INV-%03d" % number, name),
                    )

    def test_the_two_labels_give_opposite_instructions(self):
        """A reader acts on the label, not on this test — so the words must differ.

        Every occurrence is checked, not the first: the labels repeat once per group, and a
        version of this test using `next()` missed a "skip" injected into the third partly-
        superseded line because it only ever read the first.
        """
        lines = index_section().splitlines()
        full_lines = [l for l in lines if l.strip().startswith(FULL_LABEL)]
        part_lines = [l for l in lines if l.strip().startswith(PART_LABEL)]
        self.assertTrue(full_lines and part_lines, "one of the two sublists has vanished")
        for line in full_lines:
            with self.subTest(label="full", line=line.strip()[:60]):
                self.assertIn("skip", line.lower())
        for line in part_lines:
            with self.subTest(label="partly", line=line.strip()[:60]):
                self.assertNotIn("skip", line.lower(),
                                 "a partly-superseded rule must never be labelled skippable")
                self.assertIn("read", line.lower())

    def test_the_marking_is_not_vacuous(self):
        self.assertGreater(len(self.marked_full()), 3,
                           "no fully-superseded rules marked; the format has drifted")
        self.assertGreater(len(self.marked_part()), 3,
                           "no partly-superseded rules marked; the format has drifted")

    def test_no_count_is_pinned_in_the_index_prose(self):
        """Every count this file and the index carried had drifted by 2026-07-31, because
        nothing couples a sentence to an append. Removing them is the fix; this keeps them
        from coming back."""
        section = index_section()
        # The prose is everything before the first indented ID line — i.e. before the groups.
        # `[ \t]+` not `\s+`: `\s` spans newlines, so `\s+` matched the blank line before the
        # "INV-001 – INV-050 are not indexed here" paragraph and sliced the prose away.
        first_id_line = re.search(r"(?m)^[ \t]+INV-\d{3}", section)
        head = section[:first_id_line.start()] if first_id_line else section
        self.assertIn("Superseded rules are listed separately", head,
                      "the prose region was sliced wrongly; this check would be vacuous")
        # Neither an invariant ID nor an ISO date is a count; both are required to appear.
        head = re.sub(r"INV-\d{3}|\d{4}-\d{2}-\d{2}", " ", head)
        self.assertNotRegex(
            head, r"\b\d{2,}\b",
            "a count reappeared in the index prose; it has nothing coupling it to an append "
            "and will drift silently",
        )


class TheMaintenanceRuleTellsAppendersAboutIt(unittest.TestCase):
    """A guard nobody knows about gets tripped rather than followed."""

    def test_adding_an_invariant_says_to_update_the_index(self):
        body = text()
        rule = body[body.find("## Maintaining this file"):body.find("## INV-001")]
        self.assertIn("Index by subject", rule)
        self.assertRegex(rule, r"(?i)same edit")


if __name__ == "__main__":
    unittest.main()
