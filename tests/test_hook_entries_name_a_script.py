"""Every hook entry names a script, and the configured command runs it rather than its payload.

A bootcamper on plugin 0.5.1 saw this repeatedly in Module 1, non-blocking:

    Stop hook error: Failed with non-blocking status code: Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    NameError: name 'false' is not defined. Did you mean: 'False'?

Three facts compose into it: `python3` with **no script argument** reads its program from stdin; a
`type: command` hook's stdin is the event payload JSON; and a Stop payload carries
`stop_hook_active`, whose value is the JSON literal `false` — not a Python name. So the failing
process was the interpreter with the script path missing, parsing the payload it was handed as
source code. `stop-nudge.py` never ran, which is the invisible half: whatever the Stop hook was
for, it did not happen.

⛔ **What this file does NOT test, stated because the distinction is the whole finding.** It cannot
establish whether the host honors `command` + `args` for a `type: command` hook. That needs the
plugin enabled and its hooks observed firing, and on this machine `~/.claude/settings.json` →
`enabledPlugins` lists only the two official LSP plugins. Verified 2026-08-21 against Claude Code
**2.1.238**: the configured form runs the script when launched as configured, and the same payload
with the argument dropped reproduces the bootcamper's traceback byte-for-byte. Those two facts
together say the **configuration is correct** and locate the defect in how that host launched it —
they do not say the schema is honored everywhere, and `hooks.json` was deliberately left unedited
rather than rewritten on a hypothesis.

So what IS guarded here: a config regression that would make the defect reachable by construction —
an entry naming an interpreter with no script, a script path that does not resolve, or a script the
interpreter cannot run. Those are the failure modes the suite could not see before: `hooks.json` is
valid JSON and valid against INV-052, and the original failure lived entirely in the launch.

Run:  python3 -m unittest discover -s tests
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
HOOKS_JSON = PLUGIN / "hooks" / "hooks.json"

# Bare interpreters: naming one in `command` with no script is the defect's precondition.
INTERPRETERS = {
    "python", "python3", "py", "node", "deno", "bun", "ruby", "perl",
    "sh", "bash", "zsh", "dash", "pwsh", "powershell",
}


def hook_entries():
    """(event, entry) for every hook declaration, derived from the file.

    ⛔ Derived, never listed: a hardcoded event list certifies the hooks someone remembered and is
    blind to the next one added, which is the only one that matters (INV-246).
    """
    data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    table = data.get("hooks", data)
    out = []
    for event, entries in table.items():
        for entry in (entries if isinstance(entries, list) else [entries]):
            if not isinstance(entry, dict):
                continue
            for hook in (entry.get("hooks") or [entry]):
                if isinstance(hook, dict):
                    out.append((event, hook))
    return out


def resolved_args(hook):
    root = str(PLUGIN)
    return [a.replace("${CLAUDE_PLUGIN_ROOT}", root).replace("$CLAUDE_PLUGIN_ROOT", root)
            for a in (hook.get("args") or [])]


class TheScanReachesTheHooks(unittest.TestCase):
    def test_hooks_json_parses_and_declares_hooks(self):
        self.assertTrue(HOOKS_JSON.is_file(), "hooks.json is missing: %s" % HOOKS_JSON)
        entries = hook_entries()
        self.assertGreaterEqual(
            len(entries), 5,
            "only %d hook entries found; the scan is near-vacuous and would pass while the file "
            "was gutted" % len(entries))


class NoEntryNamesAnInterpreterWithNoScript(unittest.TestCase):
    """The defect's precondition, made unreachable by construction."""

    def test_every_interpreter_command_carries_a_script_argument(self):
        offenders = []
        for event, hook in hook_entries():
            command = (hook.get("command") or "").strip()
            if not command:
                continue
            base = os.path.basename(command).lower()
            if base not in INTERPRETERS:
                continue          # the script path is inside `command`; nothing to drop
            if not resolved_args(hook):
                offenders.append("%s: command=%r with no args" % (event, command))
        self.assertEqual(
            [], offenders,
            "a hook names a bare interpreter and no script. The interpreter then reads its program "
            "from stdin — which for a hook is the event payload — and a payload's JSON `false` is "
            "not a Python name. That is the 2026-08-17 Stop-hook traceback, and the script never "
            "runs:\n  %s" % "\n  ".join(offenders))

    def test_every_named_script_exists(self):
        missing = []
        for event, hook in hook_entries():
            for arg in resolved_args(hook):
                if arg.endswith((".py", ".js", ".sh", ".mjs")) and not Path(arg).is_file():
                    missing.append("%s: %s" % (event, arg))
        self.assertEqual([], missing,
                         "a hook names a script that does not exist, so the interpreter would "
                         "fail at launch:\n  %s" % "\n  ".join(missing))


class TheConfiguredCommandRunsTheScript(unittest.TestCase):
    """Behavioral, not structural — and narrower than it looks; see the module docstring.

    Launches each hook exactly as configured, with a payload containing the JSON literal `false`,
    and asserts the interpreter did not parse that payload as source. This cannot fail from the
    host dropping an argument (the test supplies them), and it is not written as though it could.
    It fails when a script has a syntax error, an unresolvable path, or an interpreter that is not
    installed — the config regressions that would make the original defect reachable.
    """

    def test_no_hook_parses_its_payload_as_source(self):
        offenders = []
        for event, hook in hook_entries():
            command = (hook.get("command") or "").strip()
            args = resolved_args(hook)
            if not command or not args:
                continue
            payload = json.dumps({
                "session_id": "test",
                "transcript_path": "/nonexistent/transcript.jsonl",
                "hook_event_name": event,
                # A JSON literal that is not a Python name — the tell for the whole defect.
                "stop_hook_active": False,
            })
            # A temp cwd with no config/bootcamp_progress.json, so every script takes its
            # "not a bootcamp — never touch unrelated projects" path and writes nothing.
            with tempfile.TemporaryDirectory() as cwd:
                try:
                    proc = subprocess.run([command] + args, input=payload, capture_output=True,
                                          text=True, cwd=cwd, timeout=30)
                except FileNotFoundError:
                    offenders.append("%s: interpreter %r not found" % (event, command))
                    continue
                except subprocess.TimeoutExpired:
                    offenders.append("%s: %r did not exit within 30s" % (event, command))
                    continue
            if 'File "<stdin>"' in proc.stderr:
                offenders.append("%s: parsed its PAYLOAD as source — %s"
                                 % (event, proc.stderr.strip().splitlines()[-1]))
            elif proc.returncode not in (0, 2):
                offenders.append("%s: exited %d — %s"
                                 % (event, proc.returncode, proc.stderr.strip()[:160]))
        self.assertEqual(
            [], offenders,
            "a hook did not run its script cleanly when launched exactly as configured:\n  %s"
            % "\n  ".join(offenders))


if __name__ == "__main__":
    unittest.main()
