"""A module that starts a visualization server must be able to name the process it started.

Truth Set visualization started a background server in Phase 1 and terminated it in Phase 2,
and nothing in between recorded *which process*. The port was recorded (INV-172); the pid was
not. With no handle, the obvious identification is a command-line match:

    pkill -f senzing_viz_server.py

which matches the **matching command's own** command line and so signals the invoking shell.
On a dry run (2026-08-13) that killed the shell with exit code 144 part-way through teardown,
leaving the Truth Set records loaded and the purge — explicitly the last, irreversible action
of the module — unrun. The failure presented as the purge crashing.

A name-based match is also wrong in principle here: the server is built in the Bootcamper's
chosen language (INV-090/INV-002), so in the general case there is no script name to match.
The handle must be the process id.

So this file asserts the contract states the rule as **behaviour** (not as a Python detail),
that both modules that start a server carry it, and that no shipped instruction teaches the
command-line match except to forbid it.

Enforces **INV-223** — a module starting a background server records its pid beside its port and terminates by pid, never by a command-line match.

Source spec: `specs/visualization-server-teardown-does-not-record-a-pid.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
M3B = SKILLS / "module-03b-truthset-visualization"
CONTRACT = M3B / "visualization-api-reference.md"
PHASE1 = M3B / "phase1-visualization.md"
PHASE2 = M3B / "phase2-close.md"
M7_PHASE1 = SKILLS / "module-07-query-visualize-discover" / "phase1-query-visualize.md"


def read(path):
    return path.read_text(encoding="utf-8")


def squash(text):
    """Whitespace-collapsed, so an assertion survives a re-wrap of the paragraph."""
    return re.sub(r"\s+", " ", text)


class TheScanIsNotVacuous(unittest.TestCase):
    def test_every_file_this_guard_reads_exists(self):
        for path in (CONTRACT, PHASE1, PHASE2, M7_PHASE1):
            with self.subTest(file=path.name):
                self.assertTrue(path.is_file(), "%s moved" % path.relative_to(REPO_ROOT))


class TheContractOwnsTheRule(unittest.TestCase):
    """One statement, in the file every language builds from (INV-090)."""

    def setUp(self):
        self.text = read(CONTRACT)
        self.flat = squash(self.text)

    def test_it_lives_under_server_lifetime(self):
        lifetime = self.text.find("## Server lifetime")
        section = self.text.find("### Identifying the server process")
        self.assertNotEqual(-1, lifetime, "the Server lifetime section moved")
        self.assertNotEqual(-1, section,
                            "the contract does not carry an 'Identifying the server process' "
                            "section — the pid rule has no home that every module reads")
        self.assertGreater(section, lifetime,
                           "the process-handle rule must sit inside Server lifetime, which is "
                           "the section modules are required to honour")

    def test_the_pid_is_captured_at_launch_and_recorded_with_the_port(self):
        self.assertRegex(self.flat, r"(?i)capture the server's process id at launch")
        self.assertRegex(self.flat, r"(?i)record the pid in the same checkpoint")

    def test_both_platform_handles_are_named(self):
        """INV-001: Linux, macOS and Windows. A POSIX-only rule strands Windows."""
        self.assertIn("`$!`", self.flat, "the POSIX handle ($!) is not named")
        self.assertIn("$proc.Id", self.flat, "the PowerShell handle ($proc.Id) is not named")
        self.assertIn("-PassThru", self.flat,
                      "PowerShell's Start-Process needs -PassThru to yield a process object")

    def test_the_command_line_match_is_forbidden_with_its_reason(self):
        self.assertRegex(
            self.flat, r"(?i)never identify the server by matching its command line",
            "the contract does not forbid the command-line match")
        self.assertRegex(
            self.flat, r"(?i)appears in the \*?matching command's own\*? command line",
            "the ban is stated without the reason it exists — the reason is the whole "
            "value, since the failure does not look like a wrong kill target")

    def test_the_fallback_is_the_port_not_the_name(self):
        self.assertIn("lsof -ti:", self.flat, "the POSIX port-based fallback is not named")
        self.assertIn("Get-NetTCPConnection", self.flat,
                      "the PowerShell port-based fallback is not named")

    def test_the_exit_condition_is_the_port_being_free(self):
        self.assertRegex(self.flat, r"(?i)confirm the port is free")
        self.assertRegex(
            self.flat, r"(?i)rather than waiting a fixed interval|a sleep asserts nothing",
            "waiting is not the same as verifying; the contract must say which one is "
            "required or the 5-second wait reads as sufficient")

    def test_the_rule_is_behaviour_not_a_python_identifier(self):
        """INV-002/INV-090: a requirement expressed only as a Python name never reaches a
        Java, C#, Rust or TypeScript bootcamp.

        The one permitted mention of the reference server's filename is inside the
        prohibition, where it is the recorded evidence for what went wrong."""
        start = self.text.find("### Identifying the server process")
        end = self.text.find("\n**The teardown gate.**", start)
        section = self.text[start:end if end != -1 else len(self.text)]
        without_evidence = re.sub(r"pkill\s+-f\s+senzing_viz_server\.py", "", squash(section))
        self.assertNotIn(
            "senzing_viz_server.py", without_evidence,
            "the rule leans on the Python reference server's filename outside the "
            "prohibition, so a non-Python bootcamp receives a rule it cannot apply")
        self.assertIn(
            "chosen language (INV-090)", without_evidence,
            "the section does not say why a script name is the wrong handle in general")


class Module03bCarriesIt(unittest.TestCase):
    def test_phase1_captures_the_pid_at_launch(self):
        text = read(PHASE1)
        self.assertRegex(squash(text), r"(?i)record the process id along with the port",
                         "2.3 starts the server without recording its pid")
        self.assertIn("VIZ_PID=$!", text,
                      "the start command does not show the handle being captured")

    def test_phase1_checkpoints_the_pid_beside_the_port(self):
        text = read(PHASE1)
        self.assertRegex(
            text, r'"web_service":\s*\{[^}]*"pid"',
            "the web_service checkpoint records no pid — the field the teardown reads")

    def test_phase2_terminates_by_the_recorded_pid(self):
        flat = squash(read(PHASE2))
        self.assertRegex(flat, r"(?i)pid recorded in Phase 1",
                         "teardown does not name the recorded pid as its target")
        self.assertIn("truthset_visualization.checks.web_service.pid", flat,
                      "teardown does not say where the pid is read from")

    def test_phase2_documents_the_port_fallback(self):
        flat = squash(read(PHASE2))
        self.assertIn("lsof -ti:", flat, "no POSIX fallback for a missing pid")
        self.assertIn("Get-NetTCPConnection", flat, "no Windows fallback for a missing pid")

    def test_phase2_names_the_unsafe_match_and_why(self):
        flat = squash(read(PHASE2))
        self.assertRegex(flat, r"(?i)never `?pkill -f",
                         "teardown does not warn against the command-line match")
        self.assertRegex(
            flat, r"(?i)signals the invoking shell",
            "the warning omits its reason; 'pkill -f is unsafe' without the mechanism "
            "reads as style advice")

    def test_the_purge_waits_on_a_confirmed_free_port(self):
        """The purge is irreversible and order-sensitive; it must not run on an assumption."""
        flat = squash(read(PHASE2))
        self.assertRegex(flat, r"(?i)confirm the port is free",
                         "teardown asserts nothing about whether the server actually stopped")
        self.assertRegex(
            flat, r"(?i)do not start step 4 until the port is confirmed free",
            "nothing orders the purge after a verified teardown")


class Module07CarriesIt(unittest.TestCase):
    """Same server, re-pointed at the bootcamper's data — same failure available."""

    def test_it_states_the_pid_rule(self):
        flat = squash(read(M7_PHASE1))
        self.assertRegex(flat, r"(?i)stop it by the pid captured when it was started",
                         "module 7 stops its server with no handle rule")
        self.assertIn("$proc.Id", flat, "module 7 omits the Windows handle")

    def test_it_checkpoints_the_pid_and_port(self):
        flat = squash(read(M7_PHASE1))
        self.assertRegex(
            flat, r"recording `m7_visualizations`[^.]*?\bpid\b",
            "the m7_visualizations checkpoint instruction records no pid")
        self.assertRegex(
            flat, r'"port": <port>, "pid": <pid>',
            "the m7_visualizations example shows neither the port nor the pid to fall "
            "back to")


class NoInstructionTeachesTheUnsafeMatch(unittest.TestCase):
    """A ban in one file is undone by a recipe in another."""

    #: Words that make an occurrence a prohibition rather than an instruction.
    FORBIDDING = re.compile(r"(?i)never|⛔|unsafe|do not|must not")

    def test_every_pkill_mention_is_a_prohibition(self):
        for path in sorted(SKILLS.rglob("*.md")):
            text = read(path)
            for match in re.finditer(r"pkill", text):
                line_no = text[:match.start()].count("\n") + 1
                window = text[max(0, match.start() - 400):match.start()]
                with self.subTest(file=path.name, line=line_no):
                    self.assertRegex(
                        window, self.FORBIDDING,
                        "%s:%d mentions pkill with nothing nearby forbidding it — a "
                        "command-line match signals the invoking shell"
                        % (path.relative_to(REPO_ROOT), line_no))


if __name__ == "__main__":
    unittest.main()
