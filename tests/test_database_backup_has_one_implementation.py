"""Graduation Step 6a and the packaging flow cite ONE database-backup procedure.

The `transfer` package profile needs a database backup. When `backups/revisit/` does not exist yet
-- and the packaging flow runs at any point in the bootcamp, so it can be reached long before
graduation -- something has to produce one.

⛔ **The wrong way to do that is a second SQLite-vs-PostgreSQL branch.** The branch is subtle: its
indeterminate-`database_type` case has to read the engine from `config/engine_config.json`'s
connection string rather than guess, and guessing wrong means either no backup at all or `pg_dump`
aimed at a SQLite file. INV-094 requires exactly one of the two branches to have run, so a second
copy that drifts is a bundle that silently satisfies nothing.

So Step 6a's procedure was factored into `skills/graduation/database-backup.md` and both callers
cite it. These tests pin that: the file exists, carries the whole procedure, and neither caller has
grown its own copy of the branch.

⚠️ **Graduation's behavior is unchanged by the factoring** -- Step 6a still names the same two
branches, the same do-not-guess rule and the same warn-and-continue outcome, by reference.

Stdlib only; shipped markdown read as text (INV-108).

Source spec: `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
SHARED = SKILLS / "graduation" / "database-backup.md"
GRADUATION = SKILLS / "graduation" / "SKILL.md"
PACKAGING = SKILLS / "bootcamp-onboarding" / "packaging.md"

#: The branch that must exist in exactly one place.
BRANCH_MARKERS = ("pg_dump", "SQLite")


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class TheSharedFileCarriesTheWholeProcedure(unittest.TestCase):
    def setUp(self):
        self.text = flat(SHARED)

    def test_it_exists_and_is_substantial(self):
        self.assertTrue(SHARED.exists(), "the shared procedure file is missing")
        self.assertGreater(len(self.text), 800,
                           "the shared file is too short to carry the procedure; the citations "
                           "below would point at nothing")

    def test_it_carries_both_engine_branches(self):
        for marker in BRANCH_MARKERS:
            with self.subTest(marker=marker):
                self.assertIn(marker, self.text)

    def test_it_carries_the_do_not_guess_rule(self):
        self.assertRegex(
            self.text, r"(?i)do not guess a branch",
            "the shared file omits the indeterminate-database_type rule, which is the subtle part "
            "and the whole reason there is one copy",
        )

    def test_it_carries_the_warn_and_continue_outcome(self):
        self.assertRegex(self.text, r"(?i)warn and continue")

    def test_it_carries_the_restore_commands(self):
        self.assertIn("pg_restore", self.text)

    def test_it_names_both_of_its_callers(self):
        """A shared file that does not say who shares it invites a third private copy."""
        self.assertIn("SKILL.md", self.text)
        self.assertIn("packaging.md", self.text)


class BothCallersCiteIt(unittest.TestCase):
    def test_graduation_step_6a_cites_it(self):
        self.assertIn("database-backup.md", flat(GRADUATION),
                      "graduation Step 6a does not cite the shared procedure")

    def test_the_packaging_flow_cites_it(self):
        self.assertIn("database-backup.md", flat(PACKAGING),
                      "the packaging flow does not cite the shared procedure, so its transfer "
                      "profile has nothing to produce a database backup with")

    def test_the_packaging_flow_forbids_a_second_branch(self):
        self.assertRegex(
            flat(PACKAGING), r"(?i)do NOT\s+write a second\s+SQLite-vs-PostgreSQL branch",
            "the packaging flow does not forbid growing its own branch, which is the specific "
            "drift this factoring exists to prevent",
        )


class NeitherCallerKeptACopyOfTheBranch(unittest.TestCase):
    """The point of factoring: the branch lives once."""

    def test_graduation_no_longer_spells_out_the_branch(self):
        text = flat(GRADUATION)
        # `pg_dump` may legitimately appear elsewhere in graduation (e.g. the return guide's
        # restore text); what must be gone is the Step 6a branch itself.
        step = self._step_6a(text)
        self.assertNotIn(
            "pg_dump", step,
            "graduation Step 6a still spells out the pg_dump branch; it should cite "
            "database-backup.md instead, or there are two copies to keep in step",
        )

    def test_the_packaging_flow_does_not_spell_out_the_branch(self):
        text = flat(PACKAGING)
        self.assertNotIn("pg_dump", text,
                         "the packaging flow spells out the pg_dump branch rather than citing the "
                         "shared procedure")

    @staticmethod
    def _step_6a(flat_text):
        start = flat_text.index("### 6a. Database backup")
        end = flat_text.index("### 6b.", start)
        return flat_text[start:end]

    def test_the_step_6a_extraction_is_not_vacuous(self):
        """INV-265 — an empty slice would satisfy the assertNotIn above."""
        step = self._step_6a(flat(GRADUATION))
        self.assertGreater(len(step), 200, "Step 6a extracted to almost nothing")
        self.assertIn("database-backup.md", step,
                      "the extracted Step 6a does not cite the shared file, so the assertion that "
                      "it dropped the branch proves nothing")


if __name__ == "__main__":
    unittest.main()
