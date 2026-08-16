"""The container lifecycle must act on the runtime that actually started the container.

These tests are the coverage for **INV-195**, which generalises INV-101 beyond Docker:
every container is recorded with the `runtime` that started it, every lifecycle action
dispatches on that recorded runtime, an entry with no `runtime` is treated as `docker`,
a runtime outside the recorded set is reported but never executed, and no
session-boundary message names a tool that did not start the container.

INV-101 requires every container the bootcamp starts to be recorded and acted on at
session boundaries. The first implementation assumed Docker in three places — the
availability probe, the stop command, and the resume message — so a bootcamp running
under Apple's ``container`` CLI (a reasonable macOS Apple Silicon choice, since Docker
Desktop needs interactive administrator privileges an agent cannot supply) got a
confidently-worded message naming the wrong tool at every session boundary:

    This bootcamp uses Docker container(s): senzing-bootcamp (unknown)

with a restart offer that would have called a binary not present on the machine.
``shutil.which("docker")`` returning None is indistinguishable, to the hook, from
"no containers to manage", so the failure was silent by construction.

What these tests pin:

1. A ``docker`` entry still dispatches to ``docker`` — the existing behaviour.
2. A non-``docker`` entry dispatches to its own CLI and is never described as Docker.
3. A legacy entry with no ``runtime`` (dict or bare string) is treated as ``docker``,
   so progress files written by earlier runs are unaffected.
4. An absent CLI runs no command at all and never blocks the hook (INV-101/INV-052).

Every test stubs the CLI lookup and the subprocess call. This must not be relaxed:
the development machine has a real ``docker``, and an unstubbed test would stop real
containers. The consequence is that dispatch to Apple's ``container`` is asserted at
the command-construction level rather than against the real binary, which is not
available on Linux.

Run:  python3 -m unittest discover -s tests
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp", "scripts")
SESSION_END = os.path.join(SCRIPTS, "session-end.py")
SESSION_START = os.path.join(SCRIPTS, "session-start.py")


def load_module():
    """Import docker_lifecycle the way the hooks do — by directory, not by package."""
    import importlib.util

    path = os.path.join(SCRIPTS, "docker_lifecycle.py")
    spec = importlib.util.spec_from_file_location("docker_lifecycle_under_test", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Project:
    """A temp directory shaped like an active bootcamp with recorded containers."""

    def __init__(self, containers, key="docker_containers"):
        self.containers = containers
        self.key = key

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, "config"))
        progress = {"current_module": "SDK Setup", self.key: self.containers}
        with open(
            os.path.join(self.root, "config", "bootcamp_progress.json"),
            "w",
            encoding="utf-8",
        ) as fh:
            json.dump(progress, fh)
        self.prev = os.getcwd()
        os.chdir(self.root)
        return self

    def __exit__(self, *exc):
        os.chdir(self.prev)
        self.tmp.cleanup()
        return False


class FakeCli:
    """Stub the CLI lookup and the subprocess call; record every command run."""

    def __init__(self, module, present=(), states=None):
        self.module = module
        self.present = set(present)
        self.states = states or {}
        self.commands = []

    def __enter__(self):
        self.real_which = self.module.shutil.which
        self.real_run = self.module.subprocess.run
        self.module.shutil.which = self._which
        self.module.subprocess.run = self._run
        return self

    def __exit__(self, *exc):
        self.module.shutil.which = self.real_which
        self.module.subprocess.run = self.real_run
        return False

    def _which(self, name):
        return "/usr/bin/" + name if name in self.present else None

    def _run(self, args, **kwargs):
        self.commands.append(list(args))

        class Result:
            returncode = 0
            stdout = ""

        result = Result()
        if len(args) > 1 and args[1] == "ps":
            name = [a for a in args if a.startswith("name=^")]
            target = name[0][len("name=^"):-1] if name else ""
            state = self.states.get(target)
            result.stdout = "%s\t%s\n" % (target, state) if state else ""
        return result

    def clis_used(self):
        return {os.path.basename(cmd[0]) for cmd in self.commands}


class DispatchesOnRecordedRuntime(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()

    def test_docker_entry_stops_with_docker(self):
        entry = {"name": "bootcamp-postgres", "runtime": "docker"}
        with Project([entry]), FakeCli(self.mod, present=["docker"]) as cli:
            stopped = self.mod.stop_started_containers()
        self.assertEqual(stopped, ["bootcamp-postgres"])
        self.assertEqual(
            cli.commands, [["/usr/bin/docker", "stop", "bootcamp-postgres"]]
        )

    def test_non_docker_entry_stops_with_its_own_cli(self):
        entry = {"name": "senzing-bootcamp", "runtime": "container"}
        with Project([entry]), FakeCli(self.mod, present=["container"]) as cli:
            stopped = self.mod.stop_started_containers()
        self.assertEqual(stopped, ["senzing-bootcamp"])
        self.assertEqual(
            cli.commands, [["/usr/bin/container", "stop", "senzing-bootcamp"]]
        )
        self.assertNotIn("docker", cli.clis_used())

    def test_mixed_runtimes_each_use_their_own_cli(self):
        entries = [
            {"name": "bootcamp-postgres", "runtime": "docker"},
            {"name": "senzing-bootcamp", "runtime": "container"},
        ]
        with Project(entries), FakeCli(self.mod, present=["docker", "container"]) as cli:
            stopped = self.mod.stop_started_containers()
        self.assertEqual(stopped, ["bootcamp-postgres", "senzing-bootcamp"])
        self.assertEqual(
            cli.commands,
            [
                ["/usr/bin/docker", "stop", "bootcamp-postgres"],
                ["/usr/bin/container", "stop", "senzing-bootcamp"],
            ],
        )

    def test_unknown_runtime_is_never_executed(self):
        """A runtime outside the closed set must not become a binary to invoke."""
        entry = {"name": "odd-one", "runtime": "rm -rf"}
        with Project([entry]), FakeCli(self.mod, present=["docker", "rm -rf"]) as cli:
            stopped = self.mod.stop_started_containers()
        self.assertEqual(stopped, [])
        self.assertEqual(cli.commands, [])


class LegacyEntriesStayDocker(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()

    def test_dict_entry_without_runtime_is_docker(self):
        with Project([{"name": "legacy"}]), FakeCli(self.mod, present=["docker"]) as cli:
            stopped = self.mod.stop_started_containers()
        self.assertEqual(stopped, ["legacy"])
        self.assertEqual(cli.commands, [["/usr/bin/docker", "stop", "legacy"]])

    def test_bare_string_entry_is_docker(self):
        with Project(["bare-name"]), FakeCli(self.mod, present=["docker"]) as cli:
            stopped = self.mod.stop_started_containers()
        self.assertEqual(stopped, ["bare-name"])
        self.assertEqual(cli.commands, [["/usr/bin/docker", "stop", "bare-name"]])

    def test_legacy_entry_resolves_to_docker_runtime(self):
        with Project([{"name": "legacy"}, "bare"]):
            tracked = self.mod.tracked_containers()
        self.assertEqual([c["runtime"] for c in tracked], ["docker", "docker"])

    def test_progress_key_is_still_docker_containers(self):
        """Renaming the key would break every in-flight bootcamp's progress file."""
        with Project([{"name": "x"}], key="containers"):
            self.assertEqual(self.mod.tracked_containers(), [])
        with Project([{"name": "x"}], key="docker_containers"):
            self.assertEqual(len(self.mod.tracked_containers()), 1)


class ResumeMessageNamesTheRealRuntime(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()

    def test_no_message_says_docker_for_a_non_docker_entry(self):
        entry = {"name": "senzing-bootcamp", "runtime": "container"}
        with Project([entry]), FakeCli(self.mod, present=["container"]):
            message = self.mod.resume_summary()
        self.assertIn("senzing-bootcamp", message)
        self.assertIn("`container`", message)
        self.assertNotIn("Docker", message)
        self.assertNotIn("docker", message)

    def test_docker_entry_reports_its_state(self):
        entry = {"name": "bootcamp-postgres", "runtime": "docker"}
        states = {"bootcamp-postgres": "running"}
        with Project([entry]), FakeCli(self.mod, present=["docker"], states=states):
            message = self.mod.resume_summary()
        self.assertIn("bootcamp-postgres (running)", message)
        self.assertIn("`docker`", message)

    def test_state_is_not_probed_for_a_runtime_without_a_verified_ps(self):
        """Apple's container CLI does not implement docker's ps interface, so the
        state is reported unknown rather than guessed at with a failing command."""
        entry = {"name": "senzing-bootcamp", "runtime": "container"}
        with Project([entry]), FakeCli(self.mod, present=["container"]) as cli:
            message = self.mod.resume_summary()
        self.assertIn("senzing-bootcamp (unknown)", message)
        self.assertEqual(cli.commands, [])

    def test_each_runtime_gets_its_own_clause(self):
        entries = [
            {"name": "bootcamp-postgres", "runtime": "docker"},
            {"name": "senzing-bootcamp", "runtime": "container"},
        ]
        states = {"bootcamp-postgres": "running"}
        with Project(entries), FakeCli(
            self.mod, present=["docker", "container"], states=states
        ):
            message = self.mod.resume_summary()
        self.assertIn("`docker`: bootcamp-postgres (running)", message)
        self.assertIn("`container`: senzing-bootcamp (unknown)", message)

    def test_no_containers_is_an_empty_message(self):
        with Project([]), FakeCli(self.mod, present=["docker"]):
            self.assertEqual(self.mod.resume_summary(), "")


class AbsentCliWarnsAndContinues(unittest.TestCase):
    """INV-101/INV-052: an unavailable CLI must never block a hook."""

    def setUp(self):
        self.mod = load_module()

    def test_absent_cli_runs_no_command_and_stops_nothing(self):
        entry = {"name": "senzing-bootcamp", "runtime": "container"}
        with Project([entry]), FakeCli(self.mod, present=[]) as cli:
            stopped = self.mod.stop_started_containers()
        self.assertEqual(stopped, [])
        self.assertEqual(cli.commands, [])

    def test_absent_cli_is_reported_by_name_in_the_resume_message(self):
        entry = {"name": "senzing-bootcamp", "runtime": "container"}
        with Project([entry]), FakeCli(self.mod, present=[]) as cli:
            message = self.mod.resume_summary()
        self.assertIn("senzing-bootcamp", message)
        self.assertIn("the `container` CLI is not available here", message)
        self.assertEqual(cli.commands, [])

    def test_absent_cli_for_one_runtime_does_not_stop_the_other(self):
        entries = [
            {"name": "bootcamp-postgres", "runtime": "docker"},
            {"name": "senzing-bootcamp", "runtime": "container"},
        ]
        with Project(entries), FakeCli(self.mod, present=["docker"]) as cli:
            stopped = self.mod.stop_started_containers()
        self.assertEqual(stopped, ["bootcamp-postgres"])
        self.assertEqual(cli.clis_used(), {"docker"})


class HooksExitCleanly(unittest.TestCase):
    """End-to-end, with a runtime whose CLI is genuinely absent on this machine, so
    no real container command can run."""

    ABSENT = "container"

    def setUp(self):
        if shutil.which(self.ABSENT) is not None:
            self.skipTest("%s CLI is present; this test needs an absent one" % self.ABSENT)

    def run_hook(self, hook, cwd):
        return subprocess.run(
            [sys.executable, hook],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_session_end_exits_zero_with_an_absent_runtime(self):
        entry = {"name": "senzing-bootcamp", "runtime": self.ABSENT}
        with Project([entry]) as project:
            result = self.run_hook(SESSION_END, project.root)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_session_start_exits_zero_and_names_the_runtime(self):
        entry = {"name": "senzing-bootcamp", "runtime": self.ABSENT}
        with Project([entry]) as project:
            result = self.run_hook(SESSION_START, project.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("senzing-bootcamp", result.stdout)
        self.assertIn("`container`", result.stdout)
        self.assertNotIn("Docker", result.stdout)


if __name__ == "__main__":
    unittest.main()
