"""An affirmative transition answer is acknowledged BEFORE the skill invocation it triggers.

`ground-rules.md`'s acknowledge clause has always required the bootcamper's answer to be
acknowledged "before proceeding". That is satisfiable by one combined reply everywhere the next
step is **composed** -- and not where the next step must first be **loaded**. At a module
transition the next module's step list does not exist until its skill is invoked and its phase
files are read, and none of that emits anything the bootcamper can see.

⛔ **The observed cost, 2026-08-25:** a bootcamper answered the Module 7 transition question, saw
nothing across a skill invocation and two file reads, interrupted, and answered a second time --
*"I lost my place and had to re-confirm"*. The rule was followed; it did not reach far enough.

⚠️ **What this guard can and cannot check.** It asserts the ordering rule SHIPS -- in
`ground-rules.md` where the clause is defined, and at every shipped site that acts on an
affirmative transition answer. Whether a given run actually *emits* the acknowledgment before its
first tool call is a property of the conversation, not of the files, and is not statically
testable at all; `dry-run` phase 3 owns that observation. A green run here means the instruction is
present and reachable, nothing more.

Per **INV-246** the site set is derived by scanning for the rule's subject -- prose that acts on an
affirmative reply -- never by listing known paths. That is not a formality here: the source spec
named ONE phase file, and the scan found THREE more, one of them the graduation gate, where the
same skill-invocation interval is the last thing that happens in the bootcamp.

Source spec: `specs/the-acknowledge-rule-does-not-reach-across-the-module-transition.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
GROUND_RULES = SKILLS / "bootcamp-onboarding" / "ground-rules.md"

#: The rule's subject: shipped prose that acts on an affirmative reply. Every such site either
#: proceeds by LOADING (a skill invocation) or is the clause that governs them.
AFFIRMATIVE_SITE = re.compile(r"(?i)on an affirmative reply")

#: Whether a site proceeds by LOADING rather than composing. Deliberately keyed on text that is
#: present WHETHER OR NOT the fix is applied: the next module's start banner and the graduation
#: skill both come from a skill that must be invoked first. An earlier version of this guard keyed
#: on the words "skill"/"invoke", which the fix itself introduces -- so it only ever checked sites
#: that already carried the fix, and reverting a site to its unfixed wording went undetected.
PROCEEDS_BY_LOADING = re.compile(
    r"(?i)next module's start banner"
    r"|start banner, journey map"
    r"|invoke the `graduation` skill"
    r"|invok(?:e|ing) (?:its|that module's|the `graduation`) skill")

#: How the acknowledgment-first requirement reads wherever it is stated.
ACK_FIRST = re.compile(
    r"(?i)acknowledge it in one short visible line"
    r"|acknowledgment (?:goes out first|is emitted \*\*first)")

WINDOW = 700


def flat(text):
    return " ".join(text.split())


def affirmative_sites():
    """(path, window) for each shipped site acting on an affirmative reply.

    ⚠️ The file is flattened BEFORE scanning, not after. These phrases wrap across lines in
    shipped markdown -- `phase2-close.md` carries "on an\n   affirmative reply" -- and an
    unflattened scan silently missed that whole site, so its assertions passed vacuously in
    both directions. Reverting it to the defective wording went undetected because of it.
    """
    out = []
    for path in sorted(SKILLS.glob("**/*.md")):
        text = flat(path.read_text(encoding="utf-8"))
        for match in AFFIRMATIVE_SITE.finditer(text):
            out.append((path, text[match.start():match.start() + WINDOW]))
    return out


class TheScanFindsTheSites(unittest.TestCase):
    def test_several_sites_act_on_an_affirmative_reply(self):
        found = affirmative_sites()
        self.assertGreaterEqual(
            len(found), 5,
            "fewer affirmative-reply sites than the five this rule was written against — the scan "
            "pattern has drifted, so the per-site assertions below are checking less than they "
            f"appear to (found {len(found)})",
        )


class TheClauseItselfCarriesTheOrdering(unittest.TestCase):
    """The rule is defined once, in the file that owns acknowledgment (INV-179)."""

    def setUp(self):
        self.text = GROUND_RULES.read_text(encoding="utf-8")

    def test_the_acknowledge_clause_states_the_ordering(self):
        self.assertRegex(
            flat(self.text),
            r"(?i)acknowledgment goes out first .{0,120}before the first tool call",
            "ground-rules.md's acknowledge clause does not say the acknowledgment precedes the "
            "first tool call, so 'before proceeding' still reads as satisfiable by one combined "
            "reply after the loading",
        )

    def test_it_names_why_the_interval_is_invisible(self):
        self.assertRegex(
            flat(self.text),
            r"(?i)no\*?\*? bootcamper-visible output|produces \*\*no\*\* bootcamper-visible",
            "the clause states the ordering without saying why it matters — that tool calls emit "
            "nothing the bootcamper sees — so it reads as a style preference",
        )

    def test_it_forbids_turning_the_acknowledgment_into_a_question(self):
        """INV-005-INV-009/INV-006 — the fix must not add a gate or re-ask anything."""
        flattened = flat(self.text)
        self.assertRegex(
            flattened, r"(?i)statement, not a turn boundary",
            "the clause does not say the acknowledgment is a statement rather than a turn "
            "boundary, which is what keeps this from becoming a second question",
        )
        self.assertRegex(flattened, r"INV-006",
                         "the clause does not cite the asked-once invariant it must not breach")


class EverySiteThatProceedsByLoadingCarriesTheRule(unittest.TestCase):
    """Including the graduation gate, which the source spec did not name."""

    def test_each_affirmative_site_acknowledges_before_invoking(self):
        for path, window in affirmative_sites():
            if not PROCEEDS_BY_LOADING.search(window):
                continue  # a site that proceeds by composing, not loading
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertRegex(
                    window, ACK_FIRST,
                    f"{path.relative_to(REPO_ROOT)} acts on an affirmative reply by invoking a "
                    "skill without acknowledging the answer first, so the bootcamper's answer "
                    "looks unregistered across the whole load",
                )

    def test_the_added_line_is_not_a_question(self):
        """A dead-end acknowledgment is already a violation; a second 👉 would be worse."""
        for path, window in affirmative_sites():
            if not ACK_FIRST.search(window):
                continue
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                head = window[:window.lower().find("then ") + 5] if "then " in window.lower() else window
                self.assertNotIn(
                    "👉", head,
                    "the acknowledgment instruction introduces a 👉 question, which would make the "
                    "transition two questions instead of one (INV-006)",
                )

    def test_it_does_not_duplicate_the_module_start_apparatus(self):
        """One line, a receipt for the answer -- not a preview of the banner."""
        for path, window in affirmative_sites():
            if not ACK_FIRST.search(window):
                continue
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertRegex(
                    window, r"(?i)one short visible line|one line",
                    "the acknowledgment is not bounded to one short line, so it can grow into a "
                    "second copy of the start banner",
                )


class ThePhaseFilesPointAtTheSharedRuleRatherThanRestatingIt(unittest.TestCase):
    """INV-179 — the ordering is defined once and referenced, not re-specified per module."""

    def test_each_pointing_site_names_the_owning_file(self):
        for path, window in affirmative_sites():
            if not ACK_FIRST.search(window):
                continue
            if path == SKILLS / "bootcamp-onboarding" / "module-completion.md":
                continue  # this file IS an owner
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                # `module-completion.md` specifically: the trailing "per the ground rules" that
                # every transition already carries would otherwise satisfy this on its own.
                self.assertIn(
                    "module-completion.md", window,
                    "the site states the ordering without naming the file that defines it, so the "
                    "two can drift independently (a bare 'per the ground rules' does not locate "
                    "the Step 4 instruction)",
                )


if __name__ == "__main__":
    unittest.main()
