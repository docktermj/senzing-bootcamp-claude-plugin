"""The onboarding overview's verbosity treatment must not state a bullet count.

`bootcamp-onboarding/onboarding-flow.md` step 3 governs its overview with a verbosity
treatment table. The `standard` / `detailed` row read **"all ten, as written"** and the
paragraph below it repeated **"so all ten are shown"** -- while the list they govern had
**eleven** bullets. `1b42648` appended the "make a note" bullet and made it verbosity-aware
but left both literals as they were.

A guide following the file literally then has a count that disagrees with the list in front
of it, and both available readings are wrong: present ten and silently drop a bullet -- the
note bullet is the newest and likeliest casualty, which would defeat INV-254, since an
any-time control nobody is told about is an any-time control nobody uses -- or notice the
mismatch and treat the surrounding stop-sign instructions as approximate.

The fix is not a fresher number. A count carries no information the reader does not already
have from the list directly beneath it; its only effect is to disagree with the list
eventually. So both sites now refer to the list itself, and this guard fails if a count comes
back.

⛔ **This checks the treatment table's wording, not the overview as delivered.** Whether a
`standard` run actually presents every bullet is a conversational outcome and belongs to
`dry-run` phase 3. A clean run here means the instruction cannot disagree with its own list.

Per **INV-246** the bullet set is derived by scanning the overview block rather than pinning a
number anywhere in this file -- pinning one here would reproduce the defect in the guard.

Source spec: `specs/overview-bullet-count-is-stale-after-the-note-bullet.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ONBOARDING_FLOW = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" /
                   "bootcamp-onboarding" / "onboarding-flow.md")

#: The treatment table's rows, keyed by the preset column. Matched on the leading pipe so a
#: row is found wherever the table sits in the file.
TREATMENT_ROW = re.compile(r"^\|\s*(`[^|]+?`(?:\s*/\s*`[^|]+?`)?)\s*\|(.+?)\|\s*$", re.M)

#: The paragraph explaining what a fresh bootcamp shows. Located by its own subject rather
#: than by line number.
FRESH_PARAGRAPH = re.compile(
    r"\*\*fresh\*\* bootcamp no preset exists yet,[^.]*\.", re.S)

#: The overview bullets themselves: top-level list items between the treatment paragraph and
#: the note-bullet commentary that closes the block.
OVERVIEW_BULLET = re.compile(r"^- (?!\*\*Probe)", re.M)

_CARDINAL = (r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
             r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty")

#: A cardinal used AS A BULLET COUNT, in the two shapes that actually go stale: "all ten" /
#: "all 10", and "ten bullets" / "11 bullets".
#:
#: Deliberately narrower than "any number in the cell". A first draft forbade every cardinal
#: and immediately flagged the `concise` row's "each trimmed to **one** line" — a count of
#: lines per bullet, which is content guidance and cannot go stale when a bullet is added. A
#: guard that fails on correct prose gets loosened by whoever hits it next, so it is scoped to
#: the construction under repair. "all bullets" (no number) passes, which is the point.
#:
#: `INV-\d{3}` tokens are stripped before this runs, so an invariant citation is never read as
#: a count.
BULLET_COUNT = re.compile(
    r"\ball\s+(?:%s)\b|\b(?:%s)\s+bullets?\b" % (_CARDINAL, _CARDINAL), re.I)

#: Content words that show a row names its bullets rather than counting them.
BY_CONTENT = ("module list", "how-long-it-takes", "guided discovery", "unfamiliar terms",
              "bullet")


def read(path):
    return path.read_text(encoding="utf-8")


def strip_invariant_ids(text):
    return re.sub(r"INV-\d{3}", "INV", text)


def treatment_rows():
    """The treatment table as {preset cell: treatment cell}, header row excluded."""
    rows = {}
    for preset, treatment in TREATMENT_ROW.findall(read(ONBOARDING_FLOW)):
        rows[preset.strip()] = treatment.strip()
    return rows


def overview_block():
    """The prose from the treatment table down to the end of the overview bullet list."""
    text = read(ONBOARDING_FLOW)
    start = text.index("| Preset | The overview is |")
    end = text.index("**The note bullet is verbosity-aware", start)
    return text[start:end]


class TheScanIsNotVacuous(unittest.TestCase):
    """Every assertion below is worthless if its input is empty. Prove it is not."""

    def test_the_treatment_table_is_found(self):
        rows = treatment_rows()
        self.assertIn(
            "`standard` / `detailed`", rows,
            "the verbosity treatment table no longer has a '`standard` / `detailed`' row — "
            "this guard is inspecting an empty set and would pass forever")

    def test_the_fresh_bootcamp_paragraph_is_found(self):
        self.assertRegex(
            read(ONBOARDING_FLOW), FRESH_PARAGRAPH,
            "the fresh-bootcamp paragraph no longer matches; the second half of this guard "
            "is inspecting nothing")

    def test_the_overview_still_has_a_substantial_bullet_list(self):
        """A floor, deliberately not the exact count — pinning one here is the defect."""
        found = OVERVIEW_BULLET.findall(overview_block())
        self.assertGreaterEqual(
            len(found), 10,
            "the overview bullet list has shrunk below 10 items (found %d). Either the block "
            "moved and this guard no longer reads it, or bullets were dropped" % len(found))


class TheStandardDetailedRowStatesNoCount(unittest.TestCase):
    def test_the_row_refers_to_the_list_rather_than_counting_it(self):
        row = treatment_rows()["`standard` / `detailed`"]
        found = BULLET_COUNT.findall(strip_invariant_ids(row))
        self.assertEqual(
            [], found,
            "the `standard` / `detailed` treatment states a count (%s). A count of the list "
            "printed directly beneath it adds nothing and goes stale the next time a bullet "
            "is added — which is exactly how 'all ten' outlived a list of eleven. Refer to "
            "the list instead: 'every bullet below, as written'" % ", ".join(found))

    def test_the_row_still_says_what_the_overview_is(self):
        """Removing the count must not have emptied the cell."""
        row = treatment_rows()["`standard` / `detailed`"]
        self.assertRegex(
            row, r"(?i)every bullet|all bullets",
            "the `standard` / `detailed` row no longer states that the whole list is shown, "
            "so dropping the count lost the rule instead of restating it")


class TheFreshBootcampParagraphStatesNoCount(unittest.TestCase):
    def test_the_paragraph_refers_to_the_list_rather_than_counting_it(self):
        match = FRESH_PARAGRAPH.search(read(ONBOARDING_FLOW))
        found = BULLET_COUNT.findall(strip_invariant_ids(match.group(0)))
        self.assertEqual(
            [], found,
            "the fresh-bootcamp paragraph states a count (%s). It is the second copy of the "
            "same fact and went stale alongside the table row; say 'every bullet is shown'"
            % ", ".join(found))


class TheReducedRowsAreUnchanged(unittest.TestCase):
    """The spec's third criterion: `minimal` and `concise` name their bullets by content.

    Neither ever counted, and neither should start. They are included because a future edit
    "harmonizing" the table is the plausible way a count gets reintroduced — into the rows
    that never had one.
    """

    def test_neither_reduced_row_states_a_count(self):
        rows = treatment_rows()
        for preset in ("`minimal`", "`concise`"):
            with self.subTest(preset=preset):
                self.assertIn(preset, rows, "the %s treatment row is gone" % preset)
                found = BULLET_COUNT.findall(strip_invariant_ids(rows[preset]))
                self.assertEqual(
                    [], found,
                    "the %s row now states a count (%s); it named its bullets by content "
                    "before" % (preset, ", ".join(found)))

    def test_each_reduced_row_names_its_bullets_by_content(self):
        rows = treatment_rows()
        for preset in ("`minimal`", "`concise`"):
            with self.subTest(preset=preset):
                lowered = rows[preset].lower()
                self.assertTrue(
                    any(word in lowered for word in BY_CONTENT),
                    "the %s row names none of its bullets by content, so a reader cannot "
                    "tell which bullets it means" % preset)


if __name__ == "__main__":
    unittest.main()
