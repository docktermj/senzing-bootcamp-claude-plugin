# The Stop hook ran bare `python3`, which executed the hook payload as Python source

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A bootcamper in Module 1 (Discover the Business Problem) saw this repeatedly, non-blocking, on
plugin 0.5.1:

```text
Stop hook error: Failed with non-blocking status code: Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'false' is not defined. Did you mean: 'False'?
```

Nothing else in their session appeared to fail, so the visible cost was distraction — they
reported it as "makes the bootcamper think something is broken when, from their point of view,
nothing else is failing". The invisible cost is the subject of this spec: whatever the Stop hook
was supposed to do, it did not do.

## Root cause

**The traceback is reproduced exactly by feeding a Stop hook payload to `python3` with no script
argument.** Run on this machine, 2026-08-17:

```bash
printf '%s' '{"session_id":"abc","transcript_path":"/x/y.jsonl","hook_event_name":"Stop","stop_hook_active":false}' | python3
```

```text
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'false' is not defined. Did you mean: 'False'?
```

Byte-for-byte the reported error. The mechanism is three facts composing:

1. `python3` with **no** script argument reads its program from **stdin**.
2. A `type: command` hook's stdin is the **event payload JSON**.
3. A **Stop** payload carries `stop_hook_active`, whose value is the JSON literal `false` — which
   is not a Python name. `<stdin>`, line 1 is the payload's only line.

So the failing process was `python3` **with the script path missing**, and it parsed the payload it
was given as source code. `plugins/senzing-bootcamp/hooks/hooks.json:38-47` declares the Stop hook
in exactly the shape that degrades to that when the arguments are dropped:

```json
{
  "type": "command",
  "command": "python3",
  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/stop-nudge.py"]
}
```

**This is not a bug in `stop-nudge.py` — that script never ran.** The entry's own hypothesis (*"a
hook script passing a JSON-formatted value directly into a Python `eval`/`-c` context"*) does not
hold either: no script under `plugins/senzing-bootcamp/scripts/` spawns `python3 -c`, `eval` or
`exec` (swept 2026-08-17), so there is no such site to fix.

**The split shape is deliberate and mandated.** INV-052 requires "Claude Code exec form
(`command: "python3"` plus the script path in `args`)" so hook execution has no shell dependency on
any platform, and **all seven** hooks in `hooks.json` use it — `SessionStart`,
`UserPromptSubmit` (×2), `PreToolUse`, `Stop`, `PreCompact`, `SessionEnd`. If `args` is not being
applied, the same degradation applies to every one of them, and Stop is simply the event whose
non-blocking error the host surfaces to the bootcamper. That would mean the write gate is not
gating and feedback capture is not capturing — which is why this is worth more than the annoyance
it was filed as.

⚠️ **The scope is a hypothesis, not an established fact, and two things must be settled before any
edit.**

1. **Whether the current Claude Code hook schema honors `args` for `type: command` at all.** If it
   does not, the exec form has never executed and INV-052 has been prescribing a shape that
   silently no-ops. If it does, something narrower explains this one host.
2. **Which Stop hook produced the error.** Any Stop hook whose command resolves to bare `python3`
   yields this traceback; the bootcamper's own settings could hold one. The routing in the entry
   attributes it to the bootcamp, on the reasonable but unverified ground that the bootcamp is what
   was running.

**Why neither could be settled at triage.** The plugin is not enabled on the maintainer's machine
(`~/.claude/settings.json` → `enabledPlugins` lists only the two official LSP plugins), so its
hooks cannot be observed firing here, and the reporting workstation is a different machine
(Linux 6.8.0-136-generic; this one is 7.0.0-28-generic). The bootcamper reported **only** the Stop
error — not six others — which is weak evidence against the all-hooks-broken reading and is equally
consistent with Stop being the only event whose failures are shown.

## Proposed change

1. **Settle the schema question first, against the installed Claude Code.** Determine whether a
   `type: command` hook honors `command` + `args`, or requires the script path inside a single
   `command` string. Record the answer with the CLI version that established it — this is a host
   fact, so it dates like a Senzing fact does.
2. **If `args` is not honored, move the script path into `command`** for all seven hooks, and
   **amend INV-052** rather than leaving it prescribing a form that does not run. INV-052's reason
   — no shell dependency on Windows — must be re-examined rather than discarded: check whether a
   single `command` string is shell-interpreted, and if it is, whether
   `${CLAUDE_PLUGIN_ROOT}` expanding to a path containing spaces needs quoting. A fix that trades a
   silent no-op for a Windows-only breakage is not a fix.
3. **If `args` is honored, reproduce the bootcamper's host condition before changing anything** and
   spec that instead. Do not edit `hooks.json` on a hypothesis; a shape that works everywhere else
   is not improved by being rewritten blind.
4. **Guard the shape, whichever it is.** A test asserting that every entry in `hooks.json` matches
   the form the host actually executes, and that no entry names an interpreter without also naming
   the script it must run. The current suite cannot see this defect: `hooks.json` is valid JSON and
   valid against INV-052, and the failure lives entirely in how the host launches it.
5. **Do not attempt to suppress the traceback.** The plugin does not control how the host reports a
   non-blocking hook failure, and a hook that cannot launch has nothing to catch the error with. The
   fix is for the hook to run.

## Acceptance criteria

- [ ] The hook-invocation shape in `hooks.json` is verified to execute against the installed Claude
      Code, with the CLI version and date recorded — not inferred from the schema's shape.
- [ ] All seven hooks in `hooks.json` use the verified shape, and each is observed to run its script
      (a side effect, not an absence of errors — an absence of errors is what this defect looked
      like for six of the seven).
- [ ] Piping a Stop payload into the configured hook command runs `stop-nudge.py`; it does not
      produce `NameError: name 'false' is not defined`.
- [ ] INV-052 either still describes the executing form, or is amended with the reason its original
      form was wrong and how the Windows shell-dependency concern is now met.
- [ ] A test asserts the shape, and fails if any hook entry names an interpreter with no script —
      negative-controlled by removing an `args`/path and confirming the mutation lands.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the hook
      form is the cross-platform contract INV-052 exists for, so the verification must cover a path
      containing a space.

## Affected files

- `plugins/senzing-bootcamp/hooks/hooks.json` — all seven hook entries, if the shape must change.
- `specs/INVARIANTS.md` — INV-052, if its prescribed form is what does not execute.
- `tests/` — the new shape guard.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Stop hook throws NameError: name 'false' is not
  defined" (2026-08-17, Module Discover the Business Problem; `Source: bootcamper-reported`)
- Priority: **Medium as filed, potentially High.** Medium as a visible annoyance; high if the
  invocation shape is what fails, because then no plugin hook runs — including the `PreToolUse`
  write gate and `UserPromptSubmit` feedback capture.
- MCP re-check: n/a (no Senzing fact) — the defect is in hook invocation, not in anything Senzing
  serves.
- Upstream: **not applicable.** `submit_feedback` reaches Senzing, which does not ship the Claude
  Code harness; if the schema turns out to be the host's side, that finding has no channel through
  this tool.
- Related specs: `specs/cross-platform-hook-execution.md` (established INV-052 and the exec form
  this spec questions), `specs/stop-nudge-partial-flush.md`, `specs/stop-hook-false-positive.md` and
  `specs/stop-hook-issue.md` (both about what the nudge *says* once it runs — neither about the hook
  failing to launch).
