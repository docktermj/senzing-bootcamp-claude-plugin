"""The Senzing license env var is SENZING_LICENSE_FILE; SENZING_LICENSE_PATH is a confabulation.

Only ONE MCP route returns the correct name: the `compatibility_notes` of
`sdk_guide(topic='load', language=..., record_count=<above the default limit>)`, which tell a
licensed user to "place the license file at the path specified by SENZING_LICENSE_FILE or in the
etc/ directory". Verified on server 1.32.9, 2026-08-13 at (python, 1000) and (java, 600) --
language-independent, and present only when the count exceeds the limit.

`SENZING_LICENSE_PATH` is returned by nothing and shipped in graduation's `.env.example` for a
time. That is the real defect this file guards: a fabricated variable in a deliverable the
bootcamper carries into production, where setting it licenses nothing and the failure surfaces much
later as `SENZ9000|LIMIT` with nothing pointing back at the unread variable.

⚠️ **This test previously asserted the opposite and was wrong.** Its first version banned the whole
`SENZING_LICENSE_` prefix on the premise that Senzing reads no license environment variable at all.
That premise came from asking the wrong tools -- `sdk_guide(topic='configure')` returns only
`LD_LIBRARY_PATH`/`PYTHONPATH`, `sdk_guide(topic='install')` shows only the `PIPELINE` keys, and
`search_docs` returns no variable name -- and concluding absence from their silence. That is exactly
the **INV-194** failure mode: an empty or absent field in one tool's response is NOT evidence the
server lacks the fact, and the tool that owns the fact must be asked before recording a negative.
The prefix ban was therefore banning the correct name, and the module-02 note it "corrected" had
been right all along.

The lesson is why the ban is now a single exact spelling rather than a family: a prefix ban is only
sound when every member really is wrong, and establishing *that* requires the same
ask-the-owning-tool discipline the original version skipped.

Enforces **INV-208**. Complements INV-080 (Senzing facts route through the MCP server) and INV-194
(one tool's silence is not absence) -- and stands as the worked example of INV-194 costing a shipped
invariant, caught the same day by a phase-3 dry-run walk that happened to call the owning route for
an unrelated reason.

Run:  python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
GRADUATION = PLUGIN / "skills" / "graduation" / "SKILL.md"
MODULE_02 = PLUGIN / "skills" / "module-02-sdk-setup" / "SKILL.md"

# The confabulated spelling. Word-boundary-anchored and case-sensitive (env vars are uppercase).
BAD_SPELLING = re.compile(r"\bSENZING_LICENSE_PATH\b")
# The correct spelling, per sdk_guide(topic='load', record_count > default limit).
GOOD_SPELLING = "SENZING_LICENSE_FILE"
# The PIPELINE keys, the other supported route.
PIPELINE_KEYS = ("LICENSEFILE", "LICENSESTRINGBASE64")

# Files permitted to quote the bad spelling, because their subject IS the bad spelling.
# Both must also state that it is wrong, which is asserted below.
ALLOWED_TO_NAME_BAD = {GRADUATION, MODULE_02}


def plugin_text_files():
    """Every Markdown and script file that ships in the plugin."""
    for path in sorted(PLUGIN.rglob("*")):
        if path.is_file() and path.suffix in {".md", ".py", ".sh", ".json", ".yaml", ".yml"}:
            yield path


class TheConfabulatedSpellingIsNeverUsedAsAVariable(unittest.TestCase):
    def test_no_file_uses_the_bad_spelling_except_to_warn_against_it(self):
        """SENZING_LICENSE_PATH appears only in the two notes whose subject is that it is wrong."""
        offenders = []
        for path in plugin_text_files():
            if path in ALLOWED_TO_NAME_BAD:
                continue
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), start=1):
                if BAD_SPELLING.search(line):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()[:110]}")
        self.assertEqual(
            [],
            offenders,
            "SENZING_LICENSE_PATH is returned by no MCP tool (server 1.32.9, 2026-08-13). The "
            f"correct spelling is {GOOD_SPELLING}, from sdk_guide(topic='load', record_count above "
            "the default limit):\n  " + "\n  ".join(offenders),
        )

    def test_each_file_that_names_the_bad_spelling_marks_it_as_wrong(self):
        """Quoting it is allowed only alongside a statement that it must not be used."""
        for path in sorted(ALLOWED_TO_NAME_BAD):
            text = path.read_text(encoding="utf-8")
            if not BAD_SPELLING.search(text):
                continue  # not quoting it at all is fine
            self.assertRegex(
                text,
                r"(?s)SENZING_LICENSE_PATH.{0,200}?(confabulation|never use|no MCP tool|not\b)",
                f"{path.relative_to(REPO_ROOT)} names SENZING_LICENSE_PATH without marking it "
                "wrong nearby. An unmarked mention is liftable by a guide skimming the file.",
            )


class TheCorrectSpellingAndItsRouteAreRecorded(unittest.TestCase):
    def test_graduation_env_example_uses_the_correct_spelling(self):
        text = GRADUATION.read_text(encoding="utf-8")
        self.assertIn(".env.example", text, "retarget this test: graduation no longer describes it.")
        start = text.index(".env.example")
        block = text[start : start + 1400]
        self.assertIn(
            GOOD_SPELLING,
            block,
            f"graduation's .env.example must name {GOOD_SPELLING} -- the spelling the MCP server "
            "actually returns -- rather than omitting the variable or inventing one.",
        )
        self.assertNotRegex(
            block,
            r"no license-path environment variable",
            "graduation must not assert that no license environment variable exists: "
            f"sdk_guide(topic='load', record_count>limit) returns {GOOD_SPELLING} (INV-194).",
        )

    def test_module_02_names_the_single_route_that_returns_it(self):
        """The name is only reachable via one topic, so the note must say which."""
        text = MODULE_02.read_text(encoding="utf-8")
        self.assertIn(GOOD_SPELLING, text, f"module-02 Step 5 must name {GOOD_SPELLING}.")
        self.assertNotRegex(
            text,
            r"There is no license-path environment variable",
            "module-02 must not assert the variable does not exist -- the earlier version of this "
            "guard enshrined that false premise (INV-194).",
        )
        self.assertRegex(
            text,
            r"record_count",
            "module-02 must name the route that returns the variable: sdk_guide(topic='load', "
            "language=..., record_count=<above the default limit>). Without the record_count "
            "condition the note sends the reader to a call that omits the name.",
        )
        self.assertTrue(
            any(key in text for key in PIPELINE_KEYS),
            "module-02 must still name the PIPELINE route as the other supported option.",
        )


class TheOwningToolMustBeAskedBeforeRecordingAnAbsence(unittest.TestCase):
    """Pins the INV-194 lesson in the place that got it wrong, so it cannot regress quietly."""

    def test_module_02_records_why_the_absence_conclusion_was_wrong(self):
        text = MODULE_02.read_text(encoding="utf-8")
        self.assertRegex(
            text,
            r"(?i)do not conclude|not evidence|silence",
            "module-02's license note must keep the warning that the topics which omit "
            f"{GOOD_SPELLING} (configure, install, search_docs) are not evidence it does not "
            "exist. That inference is what produced a false invariant and a guard that banned the "
            "correct name.",
        )


if __name__ == "__main__":
    unittest.main()
