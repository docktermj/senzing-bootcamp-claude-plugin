"""INV-017's Markdown-placement exceptions match the rule the plugin actually ships.

INV-017 says every `.md` lives under `docs/`, and until 2026-07-31 it admitted exactly one
exception: the generated `production/` project. That forbade a file the invariant set has
required from the start —

- **INV-050**'s layout tree places `README.md` at the project root, separately from
  `docs/README.md`;
- `ground-rules.md`'s placement rule already stated *both* exceptions;
- `ground-rules.md`'s project-root whitelist names `README.md` explicitly and then bans every
  *other* root `.md`;
- Module 1 Phase 2 has a step headed "Update README.md".

So four shipped sites agreed and the invariant alone disagreed. Nothing could catch it: the
guidance is correct, so no bootcamp run misbehaves, and no test compared the invariant's
exception list against the ground rules'. It is visible only by reading the two invariants
against each other.

These assert the *agreement*, not a phrase — the point is that INV-017 and `ground-rules.md`
cannot drift apart again, in either direction.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
GROUND_RULES = PLUGIN / "skills" / "bootcamp-onboarding" / "ground-rules.md"
MODULE_1_PHASE_2 = PLUGIN / "skills" / "module-01-business-problem" / "phase2-document-confirm.md"


def flat(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


def inv_017():
    m = re.search(r"- \*\*INV-017\*\* — (.+?)(?=\n- \*\*INV-|\n##|\Z)",
                  INVARIANTS.read_text(encoding="utf-8"), re.S)
    assert m, "INV-017 not found — the invariant parser has drifted"
    return re.sub(r"\s+", " ", m.group(1).replace("**", ""))


class TheScanIsNotVacuous(unittest.TestCase):
    def test_every_file_this_compares_exists(self):
        for path in (INVARIANTS, GROUND_RULES, MODULE_1_PHASE_2):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file(), "missing: %s" % path)

    def test_inv017_parses_and_states_its_rule(self):
        self.assertRegex(inv_017(), r"(?i)Markdown files.{0,40}kept in appropriate places")


class Inv017AdmitsBothExceptions(unittest.TestCase):
    def test_it_names_the_root_readme(self):
        self.assertRegex(inv_017(), r"(?i)root `?README\.md`?",
                         "INV-017 must except the project's own root README.md")

    def test_it_names_the_production_deliverable(self):
        self.assertRegex(inv_017(), r"(?i)`?production/`?")

    def test_it_says_there_are_two_exceptions_not_one(self):
        """The defect was a singular "Exception:" that read as the complete set."""
        self.assertRegex(inv_017(), r"(?i)two exceptions")

    def test_it_cites_the_invariant_that_requires_the_root_readme(self):
        self.assertIn("INV-050", inv_017())


class TheGroundRulesStateTheSameRule(unittest.TestCase):
    """`ground-rules.md` is the copy the guide actually reads at module start."""

    def test_its_placement_rule_excepts_both(self):
        text = flat(GROUND_RULES)
        # Bounded `.` rather than `[^.]`: the filenames being matched contain dots, so a
        # dot-excluding class stops inside "README.md" and the assertion fails on correct text.
        m = re.search(r"docs and all `?\*?\.?md`?.{0,200}", text, re.I)
        self.assertIsNotNone(m, "the placement rule's wording has drifted")
        clause = m.group(0)
        self.assertRegex(clause, r"(?i)README\.md")
        self.assertRegex(clause, r"(?i)production/")

    def test_the_root_whitelist_names_readme(self):
        self.assertRegex(flat(GROUND_RULES), r"(?i)root whitelist.{0,200}`README\.md`")

    def test_the_whitelist_still_bans_every_other_root_markdown(self):
        """The exception is one file, not a licence for root `.md` generally."""
        self.assertRegex(flat(GROUND_RULES), r"(?i)`?\.md`?\s*\(except README\)")


class TheTwoAgree(unittest.TestCase):
    """The property that matters: neither may drift without the other."""

    EXCEPTIONS = ("README.md", "production/")

    def test_both_documents_except_the_same_things(self):
        invariant, ground = inv_017(), flat(GROUND_RULES)
        for token in self.EXCEPTIONS:
            with self.subTest(exception=token):
                self.assertIn(token, invariant,
                              "INV-017 does not except %s" % token)
                self.assertIn(token, ground,
                              "ground-rules.md does not except %s" % token)

    def test_module_1_still_updates_the_root_readme(self):
        """A criterion naming a second consumer is checked against that file (INV-182) —
        this is the site that proves the exception is load-bearing, not theoretical."""
        self.assertRegex(flat(MODULE_1_PHASE_2), r"(?i)update README\.md")

    def test_the_layout_tree_still_places_a_readme_at_the_project_root(self):
        """Read from INV-050's fenced tree: a root-level entry, not a `docs/` one."""
        body = INVARIANTS.read_text(encoding="utf-8")
        tree = re.search(r"- \*\*INV-050\*\*.*?```text\n(.*?)\n\s*```", body, re.S)
        self.assertIsNotNone(tree, "INV-050's layout tree could not be located")
        root_entries = [
            line for line in tree.group(1).splitlines()
            if re.match(r"\s*[├└]── \S", line) and "README.md" in line
        ]
        self.assertTrue(root_entries,
                        "INV-050's tree no longer places README.md at the project root, so "
                        "INV-017's exception has lost its justification")


if __name__ == "__main__":
    unittest.main()
