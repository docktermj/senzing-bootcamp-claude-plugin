"""`since --since-last-audit` must not start its range AT the work it exists to find.

The resolver takes the newest audit entry's ``Commit:`` field as the range start. That is
right only while an audit record is committed **before** the implementations answering it.
On 2026-09-03 a record was committed together with its two implementations (``ffa6a2f``) and
``since --since-last-audit`` reported ``0 hard-rule line(s) added`` while **six** had been.

⛔ **Zero is the one answer this view must never give wrongly.** It is indistinguishable from a
run that added no rules, which is exactly the state that lets a hard rule ship with no
invariant and no deferral — the 2026-08-17 reverse-contract defect. And everything downstream
inherits it: ``test_new_hard_rules_are_cited_or_deferred`` **skips** on "nothing added", so it
reports green by not running.

Built on a throwaway git repository rather than on this one, so the suspect case is exercised
directly instead of waiting for the mistake to recur here. Stdlib only; the maintainer script
is loaded by path, never imported as a package (INV-108).

Source spec: ``specs/since-last-audit-reports-zero-when-the-audit-record-shares-the-work-commit.md``.

Run:  python3 -m unittest discover -s tests
"""

import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFORMANCE = REPO_ROOT / ".claude" / "skills" / "production-readiness-audit" / "conformance.py"

LEDGER = """# Implemented Specs

<!-- New entries go directly below this line. -->

## production-readiness-audit-2026-01-02

- **Implemented:** 2026-01-02 (**0 findings; no file modified by this audit**)
- **Summary:** fixture.
- **Commit:** %s
"""


def load():
    spec = importlib.util.spec_from_file_location("conformance_under_test", CONFORMANCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["conformance_under_test"] = module
    spec.loader.exec_module(module)
    return module


def git(repo, *args):
    done = subprocess.run(["git"] + list(args), cwd=str(repo), capture_output=True, text=True)
    if done.returncode != 0:
        raise AssertionError("git %s failed in fixture: %s" % (" ".join(args), done.stderr))
    return done.stdout.strip()


@unittest.skipUnless(shutil.which("git"), "git is required to build the fixture repository")
class TheResolverReadsWhatTheRefActuallyTouches(unittest.TestCase):
    """Two commits: one audit-record-shaped, one carrying shipped work."""

    @classmethod
    def setUpClass(cls):
        cls.module = load()
        cls.tmp = tempfile.mkdtemp(prefix="since-ref-")
        repo = Path(cls.tmp)
        cls.repo = repo
        git(repo, "init", "--quiet", "--initial-branch", "main")
        git(repo, "config", "user.email", "fixture@example.invalid")
        git(repo, "config", "user.name", "fixture")
        git(repo, "config", "commit.gpgsign", "false")
        (repo / "specs").mkdir()
        (repo / "specs" / "IMPLEMENTED.md").write_text(LEDGER % "uncommitted", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "--quiet", "-m", "docs(specs): an audit record, specs/ only")
        cls.audit_only = git(repo, "rev-parse", "--short", "HEAD")

        shipped = repo / "plugins" / "senzing-bootcamp" / "skills" / "demo"
        shipped.mkdir(parents=True)
        (shipped / "SKILL.md").write_text(
            "- ⛔ **A hard rule that a range starting at this commit cannot see.**\n",
            encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "--quiet", "-m", "fix(demo): shipped work plus its record")
        cls.with_work = git(repo, "rev-parse", "--short", "HEAD")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def resolve(self, recorded):
        """last_audit_ref against a ledger whose newest entry records `recorded`."""
        (self.repo / "specs" / "IMPLEMENTED.md").write_text(
            LEDGER % recorded, encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ref = self.module.last_audit_ref(self.repo)
        return ref, out.getvalue()

    def test_the_fixture_commits_differ_in_what_they_touch(self):
        """⛔ A fixture that does not actually contain shipped work proves nothing."""
        names = git(self.repo, "show", "--name-only", "--format=", self.with_work).split()
        self.assertTrue(any(n.startswith("plugins/") for n in names), names)
        earlier = git(self.repo, "show", "--name-only", "--format=", self.audit_only).split()
        self.assertFalse(any(n.startswith("plugins/") for n in earlier), earlier)

    def test_a_work_commit_is_reported_and_the_range_widened(self):
        ref, printed = self.resolve(self.with_work)
        self.assertIn("SUSPECT-REF", printed,
                      "a recorded ref that carries shipped work must be reported, not used "
                      "silently — its own entry claims no shipped file was modified")
        self.assertIn("plugins/senzing-bootcamp/skills/demo/SKILL.md", printed,
                      "the warning must name the propagated files it found, so the reader can "
                      "check the claim rather than take the verdict")
        self.assertEqual(
            self.audit_only, ref,
            "the range must widen to the parent so the rules that commit added are in view; "
            "starting at it reports zero, which reads exactly like a clean run:\n" + printed)
        self.assertIn("WIDENED", printed, "the widening must be announced, never silent")

    def test_an_audit_only_commit_is_used_as_recorded(self):
        """The ordinary case must be untouched — a warning that cries wolf gets ignored."""
        ref, printed = self.resolve(self.audit_only)
        self.assertEqual(self.audit_only, ref, printed)
        self.assertNotIn("SUSPECT-REF", printed,
                         "an audit record that touches only specs/ is exactly what the "
                         "resolver expects; warning there would train the reader to skip it")
        self.assertIn("from ledger entry", printed,
                      "the provenance line must survive — it is how a reader checks the range")

    def test_the_propagated_set_is_the_one_propagate_sh_mirrors(self):
        """⛔ The detector's premise: these are the paths an audit record must not touch.

        Pinned against `propagate.sh` itself rather than a remembered list, so a change to
        what ships cannot leave the detector reasoning about the wrong tree.
        """
        script = (REPO_ROOT / ".claude" / "skills" / "propagate-to-public" / "propagate.sh")
        self.assertTrue(
            script.is_file(),
            "propagate.sh is what decides which paths ship; without it this detector's "
            "premise is unpinned. If it moved, point this at its new home rather than "
            "skipping — a skipped pin looks like a passing one in the run output.")
        text = script.read_text(encoding="utf-8")
        for prefix in self.module._PROPAGATED:
            with self.subTest(prefix=prefix):
                self.assertIn(prefix.rstrip("/"), text,
                              "the detector treats %r as propagated; propagate.sh does not "
                              "mention it, so one of the two is wrong" % prefix)


if __name__ == "__main__":
    unittest.main()
