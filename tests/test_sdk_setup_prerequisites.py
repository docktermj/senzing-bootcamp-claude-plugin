"""Two prerequisite gaps in SDK setup, both on paths the module recommends or predicts.

**SQLite said "no additional setup needed".** It is option 1, *recommended for learning and
evaluation*, so essentially every bootcamper takes it — and the database file is not
auto-created and its schema is not auto-applied. The step created `database/`, named the path,
and stopped. A bootcamper following it reached Step 9 with no database at all and got
`SENZ1001|Critical Database Error '(14:unable to open database file)'`. The plugin already did
this correctly for PostgreSQL, which states outright that the SDK does not auto-create the
schema; the recommended branch had no equivalent rung. Step 8a then compounded it, since its
premise is "a datastore you just schema-created" — a state the SQLite path never reached.
(`specs/sqlite-branch-says-no-additional-setup-but-the-schema-is-required.md`)

**Skipping Step 3 on an existing install skipped the env script.** Step 3 is titled "Install
Senzing SDK" and does two jobs: it installs, and it writes `src/scripts/senzing-env.sh`. Only
the first is redundant when Senzing is already installed; the second is the thing an existing
install is most likely to be missing. Step 1 itself predicts that state — its filesystem
fallback exists because the import check fails with `PYTHONPATH` unset on a working install —
and then routed past the step that would have fixed it.
(`specs/skipping-step-3-on-an-existing-install-skips-the-env-script.md`)

Both facts are the server's: `sdk_guide(topic='install', platform='linux_apt',
language='python')` returns the schema requirement in `install.platform.post_install[]` and
`install.engine_config_notes[]`, and the two environment variables in
`install.platform.env_vars` (re-verified MCP server 1.32.9, 2026-08-14).

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_02 = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" / "module-02-sdk-setup"
             / "SKILL.md")


def read():
    return MODULE_02.read_text(encoding="utf-8")


def squash(text):
    """Whitespace-collapsed, with blockquote markers stripped first.

    The required-stops list is a blockquote, so a wrapped sentence inside it reads as
    "… because no > install ran …" once whitespace alone is collapsed — `>` is not
    whitespace. Strip the line-leading markers before collapsing, or every assertion
    about that list has to encode the wrapping.
    """
    return re.sub(r"\s+", " ", re.sub(r"^[ \t]*>[ \t]?", "", text, flags=re.M))


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_module_exists(self):
        self.assertTrue(MODULE_02.is_file(), "module-02 SKILL.md moved")

    def test_the_database_question_is_still_there(self):
        self.assertIn("👉 **Which database would you like to use? Reply with a number:**", read(),
                      "Step 7's database gate moved; the SQLite branch may have too")


class TheSqliteBranchStatesItsThreeRungs(unittest.TestCase):
    def setUp(self):
        self.text = read()
        self.flat = squash(self.text)

    def test_the_no_setup_claim_is_gone(self):
        self.assertNotIn("No additional setup needed: SQLite is built in", self.flat,
                         "the SQLite branch still claims it needs no setup")
        self.assertRegex(
            self.flat, r"(?i)SQLite is not \"no setup\"",
            "nothing contradicts the claim the branch used to make")

    def test_it_requires_the_schema(self):
        self.assertRegex(
            self.flat, r"(?i)\*\*Apply the Senzing schema\*\* to `database/G2C\.db`",
            "the schema rung is missing")
        self.assertRegex(
            self.flat, r"(?i)required\*?\*? when using `senzingsdk-setup`",
            "the server's condition on the schema step is not relayed, so a reader may "
            "think the poc package's behaviour applies")

    def test_the_schema_path_comes_from_the_server(self):
        self.assertRegex(
            self.flat,
            r"(?i)Get the schema file's path from\s*`sdk_guide\(topic='install', platform="
            r"'<platform>'\)` rather than hardcoding it \(INV-080\)",
            "the schema path is hardcoded rather than routed through sdk_guide")

    def test_the_schema_is_applied_through_python_not_a_cli(self):
        """INV-001: Windows ships no sqlite3 binary; Python 3 is already required."""
        self.assertIn("import sqlite3,sys;", self.text,
                      "the cross-platform Python form is missing")
        self.assertRegex(
            self.flat, r"(?i)Apply it with Python, not the `sqlite3` CLI",
            "nothing says not to use the CLI the server illustrates")
        self.assertRegex(
            self.flat, r"(?i)Windows is a supported platform \(INV-001\) and\s*ships no `sqlite3`",
            "the reason the CLI is unsuitable is not given")

    def test_the_path_stays_in_the_project(self):
        """INV-200: never the server's /tmp/sqlite/G2C.db."""
        self.assertRegex(
            self.flat, r"(?i)override the path to `database/G2C\.db`",
            "the /tmp override rule was lost")
        self.assertRegex(
            self.flat, r"(?i)\*\*including in the schema command\s*above\*\*",
            "the override is not extended to the schema command, which is where the "
            "server's /tmp example would otherwise be copied")

    def test_the_connection_string_must_be_absolute(self):
        self.assertRegex(
            self.flat, r"(?i)The `SQL\.CONNECTION` path must be ABSOLUTE",
            "the absolute-path requirement is missing")
        self.assertRegex(
            self.flat, r"(?i)from any working directory, including the project root",
            "a reader could still think a cd fixes it")
        self.assertRegex(
            self.flat, r"(?i)it tries to open\s*\*\*`/G2C\.db`\*\*",
            "the mechanism is not given, so the rule reads as folklore")
        self.assertRegex(
            self.flat, r"(?i)INV-200-compatible",
            "the apparent tension with INV-200 is not resolved")

    def test_the_two_error_codes_are_distinguished(self):
        self.assertRegex(
            self.flat,
            r"(?i)SENZ7220\|No engine configuration registered in datastore",
            "the post-schema state is not named")
        self.assertRegex(
            self.flat,
            r"(?i)`SENZ1001 \(14: unable to open database file\)` means rung 2 has \*\*not\*\* "
            r"been done",
            "SENZ1001 is not tied to the missing schema, so it gets diagnosed as "
            "permissions or path")


class StepEightAAppliesToBothBranches(unittest.TestCase):
    def setUp(self):
        self.flat = squash(read())

    def test_it_says_schema_created_covers_sqlite(self):
        self.assertRegex(
            self.flat,
            r'(?i)"Schema-created" is true of BOTH database branches',
            "Step 8a's premise still only holds for PostgreSQL")
        self.assertRegex(
            self.flat, r"szcore-schema-sqlite-create\.sql",
            "the SQLite schema file is never named in the module")

    def test_it_routes_an_unschemaed_arrival_back(self):
        self.assertRegex(
            self.flat, r"(?i)this step cannot help — go back and apply it",
            "arriving at 8a without the schema is not handled, and 8a cannot fix it")


class TheEnvScriptSurvivesTheSkip(unittest.TestCase):
    def setUp(self):
        self.text = read()
        self.flat = squash(self.text)

    def test_step_1_no_longer_skips_step_3_entirely(self):
        self.assertNotIn("- Skip Steps 2 and 3 entirely.", self.text,
                         "the skip instruction still discards Step 3's environment work")

    def test_step_1_names_installation_as_what_is_skipped(self):
        self.assertRegex(
            self.flat,
            r"(?i)Skip the \*?\*?installation\*?\*? — Step 2, and Step 3's install commands",
            "the skip instruction does not say what is being skipped")
        self.assertRegex(
            self.flat, r"(?i)Not Step 3 entirely",
            "nothing contradicts the old reading")

    def test_step_1_directs_the_env_script_work(self):
        self.assertRegex(
            self.flat, r"(?i)Still do Step 3's environment-script work",
            "the skip path never reaches the env script")

    def test_the_required_stops_list_names_it(self):
        self.assertRegex(
            self.flat,
            r"(?i)\*\*Step 3's environment script\*\* \(`src/scripts/senzing-env\.sh`, or "
            r"`senzing-env\.bat` on Windows\)",
            "the required-stops list still names only Step 4 and Step 5")
        self.assertRegex(
            self.flat, r"(?i)the single most likely thing an existing install is missing",
            "the list entry does not say why it is there")

    def test_the_deferred_failure_is_named(self):
        self.assertRegex(
            self.flat, r"(?i)libSz\.so: cannot open shared object file",
            "the symptom is not named, so the cost of skipping reads as bookkeeping")
        self.assertRegex(
            self.flat, r"(?i)Step 1's own fallback predicts exactly this state",
            "the irony that Step 1 predicts the state it causes is the argument, and it "
            "is unstated")

    def test_the_values_come_from_the_server_on_the_skip_path(self):
        self.assertRegex(
            self.flat,
            r"(?i)rather than from an install transcript, because no\s*install ran \(INV-080\)",
            "the skip path does not say where the variable values come from")

    def test_it_reuses_one_implementation(self):
        self.assertRegex(
            self.flat,
            r"(?i)the zsh/bash path-resolution idiom, the fail-loudly root check, and the "
            r"empty-value guard",
            "the skip path may grow a second, weaker env-script implementation")
        self.assertRegex(self.flat, r"(?i)One implementation, not two",
                         "nothing forbids a divergent copy")

    def test_the_required_stops_still_name_steps_4_and_5(self):
        for step in (r"\*\*Step 4\*\* \(Verify Installation\)", r"\*\*Step 5\*\* \(License\)"):
            with self.subTest(step=step):
                self.assertRegex(self.flat, step,
                                 "an existing required stop was lost while adding one")


class TheTroubleshootingNoteHandlesAnAbsentScript(unittest.TestCase):
    def setUp(self):
        self.flat = squash(read())

    def test_it_checks_existence_before_sourcing(self):
        self.assertRegex(
            self.flat,
            r"(?i)\*\*First check whether\s*the script exists at all\*\*",
            "the note still asks whether an absent file was sourced")

    def test_it_says_what_to_do_when_absent(self):
        self.assertRegex(
            self.flat, r"(?i)that \*\*is\*\* the finding: write it now per Step 3's",
            "an absent script is detected but not remedied")

    def test_the_zsh_advice_survives(self):
        self.assertRegex(
            self.flat, r"(?i)a `\$\{BASH_SOURCE\[0\]\}`-based script computes the wrong root",
            "the original zsh finding was lost while adding the existence check")


if __name__ == "__main__":
    unittest.main()
