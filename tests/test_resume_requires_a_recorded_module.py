""""A bootcamp is underway" must mean the progress file RECORDS a module, not that it exists.

The onboarding preface creates `config/bootcamp_progress.json` empty during its silent project
setup, and nothing writes a `current_module` until Bootcamp preparation's final consolidated
write. That window spans the whole preface plus all of Bootcamp preparation — the
Core/Customized gate, module selection, verbosity, the programming-language gate — so any quit
inside it produced, on the next session:

    A Senzing bootcamp is in progress. Read config/bootcamp_progress.json and offer
    to resume from the last recorded module before doing anything else.

…on a project with no recorded module. The guide was told to do something impossible, on a
project whose correct behaviour was to run onboarding from the top.

Every resume decision tested the file's **existence** while
`recap_checkpoint.current_module()` already returned `None` for a contentless file — the
distinction the callers needed was computed and then unused. Fixing the shared predicate is
cheaper than fixing four call sites, which is what the spec asked for.

The four callers were checked before tightening it, and none loses anything in that window:
`session-end`/`precompact-recap` have no module recap to fold and no container to stop (containers
start in SDK setup, well after the first write), and `checkpoint-tick`'s scaffold-only case is one
it already skips.

⛔ The hooks are run as **subprocesses** with real stdin and a real working directory, because
they act at import time.

Enforces **INV-227** — a resume decision is made on recorded progress content, never on the progress file's existence.

Source spec: `specs/empty-progress-file-makes-resume-unsatisfiable.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts"
SESSION_START = SCRIPTS / "session-start.py"
ONBOARDING_SKILL = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
                    / "bootcamp-onboarding" / "SKILL.md")
START_COMMAND = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "commands"
                 / "start-bootcamp.md")

#: Progress-file contents that record NO module. Each must read as a fresh start, and none
#: may raise (INV-048).
CONTENTLESS = (
    ("empty object", "{}"),
    ("empty file", ""),
    ("whitespace only", "   \n"),
    ("not an object", "[1, 2, 3]"),
    ("malformed json", '{"current_module": '),
    ("module null", '{"current_module": null}'),
    ("module empty string", '{"current_module": ""}'),
    ("module blank", '{"current_module": "   "}'),
    ("other keys only", '{"os": "linux", "git_init": true}'),
)

RESUMABLE = (
    ("a module name", '{"current_module": "module_4_data_collection"}'),
    ("module plus step", '{"current_module": "sdk_setup", "current_step": 7}'),
)


def load_recap_checkpoint():
    spec = importlib.util.spec_from_file_location(
        "recap_checkpoint_resume_test", SCRIPTS / "recap_checkpoint.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ProjectDir:
    """A scratch project with a given progress-file content (or none)."""

    def __init__(self, contents=None):
        self.contents = contents
        self.tmp = tempfile.TemporaryDirectory()

    def __enter__(self):
        root = Path(self.tmp.name)
        if self.contents is not None:
            (root / "config").mkdir()
            (root / "config" / "bootcamp_progress.json").write_text(
                self.contents, encoding="utf-8")
        return root

    def __exit__(self, *exc):
        self.tmp.cleanup()


def predicate_in(root):
    """`bootcamp_active()` as evaluated from `root` — it reads a relative path."""
    code = (
        "import sys; sys.path.insert(0, %r);\n"
        "import recap_checkpoint as r;\n"
        "print('ACTIVE' if r.bootcamp_active() else 'INACTIVE')\n" % str(SCRIPTS)
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                          cwd=str(root), timeout=60)
    return proc.returncode, proc.stdout.strip(), proc.stderr


def session_start_in(root):
    proc = subprocess.run([sys.executable, str(SESSION_START)], input="{}",
                          capture_output=True, text=True, cwd=str(root), timeout=60)
    return proc.returncode, proc.stdout


class TheFixtureIsSound(unittest.TestCase):
    def test_the_scripts_exist(self):
        for path in (SCRIPTS / "recap_checkpoint.py", SESSION_START):
            with self.subTest(file=path.name):
                self.assertTrue(path.is_file(), "%s moved" % path)

    def test_a_resumable_project_is_active(self):
        """If this fails, every "inactive" assertion below could be vacuous."""
        with ProjectDir('{"current_module": "sdk_setup"}') as root:
            code, out, err = predicate_in(root)
            self.assertEqual(0, code, err)
            self.assertEqual("ACTIVE", out)


class AContentlessProgressFileIsNotAnActiveBootcamp(unittest.TestCase):
    def test_the_predicate_is_false_and_never_raises(self):
        for label, contents in CONTENTLESS:
            with self.subTest(case=label):
                with ProjectDir(contents) as root:
                    code, out, err = predicate_in(root)
                    self.assertEqual(0, code,
                                     "bootcamp_active() raised on %s (INV-048): %s"
                                     % (label, err))
                    self.assertEqual("INACTIVE", out,
                                     "%s reads as an active bootcamp, so the guide is "
                                     "told to resume from a module that is not there"
                                     % label)

    def test_session_start_prints_nothing(self):
        for label, contents in CONTENTLESS:
            with self.subTest(case=label):
                with ProjectDir(contents) as root:
                    code, out = session_start_in(root)
                    self.assertEqual(0, code)
                    self.assertEqual("", out.strip(),
                                     "session-start announced a resume for %s" % label)

    def test_a_missing_file_is_also_inactive(self):
        with ProjectDir(None) as root:
            _code, out, _err = predicate_in(root)
            self.assertEqual("INACTIVE", out)
            _code, printed = session_start_in(root)
            self.assertEqual("", printed.strip())


class ARecordedModuleStillResumes(unittest.TestCase):
    def test_the_predicate_is_true(self):
        for label, contents in RESUMABLE:
            with self.subTest(case=label):
                with ProjectDir(contents) as root:
                    _code, out, _err = predicate_in(root)
                    self.assertEqual("ACTIVE", out,
                                     "%s must still resume" % label)

    def test_the_resume_message_is_unchanged(self):
        with ProjectDir('{"current_module": "sdk_setup"}') as root:
            _code, out = session_start_in(root)
            self.assertIn("A Senzing bootcamp is in progress.", out,
                          "the resume message changed or disappeared")
            self.assertIn("offer to resume from the last recorded module", out)


class ThePredicateReadsContentNotExistence(unittest.TestCase):
    """Pins the mechanism, so a revert to `isfile` is caught even if a caller is rewritten."""

    def test_it_delegates_to_current_module(self):
        source = (SCRIPTS / "recap_checkpoint.py").read_text(encoding="utf-8")
        start = source.index("def bootcamp_active")
        body = source[start:source.index("\ndef ", start + 10)]
        self.assertIn("current_module() is not None", body,
                      "bootcamp_active() no longer tests for a recorded module")
        self.assertNotIn("os.path.isfile(PROGRESS)", body,
                         "bootcamp_active() is back to testing the file's existence")

    def test_current_module_still_absorbs_a_broken_file(self):
        """bootcamp_active() now depends on that contract, so it must stay documented."""
        module = load_recap_checkpoint()
        self.assertIsNotNone(module.current_module.__doc__,
                             "current_module() lost its docstring")
        self.assertIn("Never raises", module.current_module.__doc__,
                      "current_module()'s never-raises contract (INV-048) is undocumented, "
                      "and bootcamp_active() now depends on it")


class TheProseStatesTheThreeWayBranch(unittest.TestCase):
    def flat(self, path):
        import re
        return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))

    def test_the_onboarding_skill_states_all_three_cases(self):
        flat = self.flat(ONBOARDING_SKILL)
        self.assertRegex(
            flat, r"(?i)decided by the progress file's CONTENT, not its existence",
            "the skill still branches on existence")
        self.assertRegex(flat, r"(?i)\*\*Missing\*\* -> this is a fresh bootcamp")
        self.assertRegex(
            flat, r"(?i)\*\*Present but recording no module\*\*",
            "the middle case — the one that was missing — is still absent")
        self.assertRegex(flat, r"(?i)\*\*Present with a `current_module`\*\* -> a bootcamp is "
                               r"already underway")

    def test_the_onboarding_skill_says_it_is_not_a_corruption(self):
        flat = self.flat(ONBOARDING_SKILL)
        self.assertRegex(
            flat, r"(?i)this is the \*?normal\*? state, not a corruption",
            "without this a guide reports the empty file to the bootcamper, which is the "
            "output INV-012 suppresses")
        self.assertRegex(flat, r"(?i)Never announce a resume you cannot perform",
                         "the rule the defect broke is not stated")

    def test_the_start_command_states_all_three_cases(self):
        flat = self.flat(START_COMMAND)
        self.assertRegex(
            flat, r"(?i)what `config/bootcamp_progress\.json` \*\*contains\*\*, not by whether "
                  r"it exists",
            "the slash command still branches on existence")
        for case in (r"\*\*No file\*\*", r"\*\*A file recording no module\*\*",
                     r"\*\*A file with a `current_module`\*\*"):
            with self.subTest(case=case):
                self.assertRegex(flat, case, "the command omits a case")


if __name__ == "__main__":
    unittest.main()
