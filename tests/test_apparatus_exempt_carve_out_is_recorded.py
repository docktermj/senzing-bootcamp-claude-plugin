"""Every "each module" outcome invariant records the apparatus-exempt carve-out.

INV-029, INV-030, INV-031 and INV-032 each said the apparatus is presented at "the beginning
of **each** module" with no exemption recorded, while two shipped modules deliberately present
none of it and say so:

  plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md   -- "otherwise exempt from the
      per-module completion apparatus (no journey map, no before/after framing, ...)"
  plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md -- "no journey
      map of its own, no before/after framing, no step overview, and no bootcamper-facing
      end-of-module summary"

So the ruleset asserted a guarantee stronger than the plugin makes. The carve-out existed only
on the invariants that CREATE the exemption (INV-075, INV-078, INV-092), never on the ones
exempted -- a one-directional link that breaks the file's own convention, since INV-013,
INV-014, INV-028, INV-038 and INV-040-043 all carry the pointer on the *narrowed* invariant.

⚠️ **The plugin was correct; the ruleset was what overstated.** The risk this guards is a
future implementer reading INV-031 literally, adding a step overview to Bootcamp preparation,
and thereby breaching INV-075. Nothing caught it: INV-029-032 are cited by no test
(`coverage_reports.py invariants` routes them to `dry-run` phase 3 as bootcamp-outcome
invariants), and `citations.py verify` proves only that IDs resolve, never that a rule's scope
matches the plugin's.

⛔ **This guard asserts the RULESET records the exemption. It cannot assert the two modules
actually omit the apparatus at runtime** -- that is a live-turn property (INV-029-INV-032 are
conversational outcomes) and belongs to `dry-run` phase 3. A clean run here means the rule is
written down correctly, not that the flow obeys it.

Per **INV-246** the invariant set is derived by scanning INVARIANTS.md for the "each module"
phrasing rather than hardcoding four IDs, so an outcome invariant added later in the same form
is covered without editing this file.

Source spec: `specs/per-module-outcome-invariants-omit-the-apparatus-exempt-carve-out.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
PREPARATION = PLUGIN / "skills" / "bootcamp-preparation" / "SKILL.md"
MODULE_ZERO = PLUGIN / "skills" / "module-00-entity-resolution-concepts" / "SKILL.md"

#: An invariant stating a per-module apparatus outcome, i.e. one the setup modules are exempt
#: from. Derived by phrasing, never by ID list (INV-246).
EACH_MODULE = re.compile(
    r"^- \*\*(INV-\d{3})\*\* — At the (?:beginning|end) of each module,(.*)$", re.M)

#: The two invariants that create the exemption. A carve-out note must name at least one, and
#: the pair is what makes the note resolvable rather than a bare assertion.
EXEMPTING = ("INV-075", "INV-078")


def read(path):
    return path.read_text(encoding="utf-8")


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_each_module_invariants_are_found(self):
        found = EACH_MODULE.findall(read(INVARIANTS))
        self.assertGreaterEqual(
            len(found), 4,
            "the 'At the beginning/end of each module' phrasing no longer matches any "
            "invariant — this guard is inspecting an empty set and would pass forever")


class EveryEachModuleInvariantRecordsTheCarveOut(unittest.TestCase):
    def setUp(self):
        self.found = EACH_MODULE.findall(read(INVARIANTS))

    def test_each_one_states_its_disposition_for_the_setup_modules(self):
        """Either carved out, or explicitly NOT carved out — never silent.

        Silence is what the defect was. INV-028 is the case that proves the rule matters in
        both directions: the setup modules each present their own banner, so it is genuinely
        not exempt — and sitting mute above four invariants that ARE exempt, it read as though
        it were. A guard demanding only the exemption note would have forced a false one.
        """
        for ident, body in self.found:
            with self.subTest(invariant=ident):
                self.assertRegex(
                    body, r"(?i)apparatus-exempt setup modules|setup modules are NOT exempt",
                    "%s says 'each module' and states nothing about the apparatus-exempt setup "
                    "modules. If they are exempt, a reader auditing this against Bootcamp "
                    "preparation finds a violation that is not one — or 'fixes' that module and "
                    "breaches INV-075. If they are not, say so: silence beside carved-out "
                    "neighbours reads as the same carve-out" % ident)

    def test_each_one_cites_the_invariants_that_create_the_exemption(self):
        for ident, body in self.found:
            with self.subTest(invariant=ident):
                for exempting in EXEMPTING:
                    self.assertIn(
                        exempting, body,
                        "%s notes the exemption without citing %s, so the claim cannot be "
                        "looked up at the point it is read (INV-183)" % (ident, exempting))

    def test_each_one_is_marked_as_a_clarification_not_a_meaning_change(self):
        """INVARIANTS.md rule 2 permits in-place edits only to clarify without changing meaning."""
        for ident, body in self.found:
            with self.subTest(invariant=ident):
                self.assertRegex(
                    body, r"Clarified \d{4}-\d{2}-\d{2}, no meaning change",
                    "%s's carve-out note carries no dated no-meaning-change marker, so a "
                    "later reader cannot tell a clarification from a rewritten rule" % ident)

    def test_the_end_of_module_one_preserves_module_zero_s_recap_duty(self):
        """Module 0 is exempt from the SUMMARY and not from the RECAP — the easy thing to lose."""
        body = dict(self.found).get("INV-032", "")
        self.assertIn(
            "INV-092", body,
            "INV-032's carve-out does not cite INV-092, so it reads as exempting Module 0 "
            "from the recap section and `modules_completed` entry that INV-092 requires — "
            "the opposite of what INV-092 says")


class TheShippedModulesStillClaimTheExemption(unittest.TestCase):
    """If a module stopped being exempt, the carve-out notes would become the false premise."""

    def test_bootcamp_preparation_still_declares_itself_exempt(self):
        self.assertRegex(
            re.sub(r"\s+", " ", read(PREPARATION)),
            r"(?i)exempt from the per-module completion apparatus",
            "Bootcamp preparation no longer declares the exemption the INV-029–INV-032 notes "
            "now assert; the ruleset and the module have swapped which one is wrong")

    def test_module_zero_still_declares_itself_exempt(self):
        flat = re.sub(r"\s+", " ", read(MODULE_ZERO))
        self.assertRegex(
            flat, r"(?i)no before/after framing, no step overview",
            "Module 0 no longer declares the apparatus exemption the INV-029–INV-032 notes "
            "assert")
        self.assertRegex(
            flat, r"(?i)But it IS captured in the recap",
            "Module 0 no longer declares the INV-092 recap duty that INV-032's carve-out "
            "explicitly preserves")


if __name__ == "__main__":
    unittest.main()
