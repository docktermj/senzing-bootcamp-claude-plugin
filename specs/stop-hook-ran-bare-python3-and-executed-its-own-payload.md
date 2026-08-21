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

## Deviations from this spec, and why (2026-08-21)

⛔ **This spec stays OPEN. Changes 1, 3, 4 and 5 are discharged; change 2's precondition was never
established, and one acceptance criterion cannot be satisfied without a live host.**

### What was settled

**The root-cause mechanism is confirmed, byte-for-byte, on Claude Code 2.1.238.** Both arms were
run 2026-08-21:

| Launched as | Result |
|---|---|
| `python3` with the argument dropped, Stop payload on stdin | `File "<stdin>", line 1` → `NameError: name 'false' is not defined` — the bootcamper's error exactly |
| `python3 <script>`, same payload | `stop-nudge.py` runs and emits its `{"decision": "block", …}` JSON |

⚠️ **The second arm needed a third attempt to mean anything.** The first two runs exited 0 with no
output, which is indistinguishable from a no-op — the ambiguity this repo's own tooling warns about.
`stop-nudge.py`'s gate 2 is *"no `config/bootcamp_progress.json` → not a bootcamp; never touch
unrelated projects"*, and the plugin's source tree is not a bootcamp project, so silence was correct
behavior. Satisfying the gate in a throwaway directory produced the decision JSON and proved
execution.

So **the configuration is correct** and the defect is located in how that one host launched it.

### What was not settled, and why change 2 does not apply

**Whether every host honors `command` + `args` for a `type: command` hook is still unestablished.**
The plugin is not enabled on this machine — `~/.claude/settings.json` → `enabledPlugins` lists only
the two official LSP plugins — so its hooks cannot be observed firing here. Change 2 is conditional
on `args` **not** being honored; that was not shown, so per change 3 — *"Do not edit `hooks.json` on
a hypothesis"* — **`hooks.json` is unedited**, and INV-052 is not amended.

⚠️ **Weak counter-evidence, recorded rather than leaned on.** The maintainer's own working hooks in
`~/.claude/settings.json` put the script path inside `command` with no `args` at all. That is a
statement about the shape they chose, not about what the schema honors, and it is not evidence for
either reading.

### Criteria status

- [x] **Criterion 3** — piping a Stop payload into the configured command runs `stop-nudge.py` and
      does not execute the payload as Python. Verified both arms above.
- [x] **Criterion 4** — INV-052 still describes the executing form, so it is not amended; a dated
      verification note recording the 2026-08-21 check was appended in place.
- [x] **Criterion 5** — `tests/test_hook_entries_name_a_script.py`, 4 tests, deriving the hook set
      from the file rather than listing events (INV-246). Negative-controlled with four mutations,
      all verified to land and all caught: dropping `args` from the Stop hook (**the reported
      defect**), a script path that does not resolve, a script with a syntax error, and gutting the
      file to one entry.
- [x] **Criterion 6** — cross-platform and language-agnostic: the guard reads JSON with the stdlib
      and imports nothing under `plugins/` (INV-108).
- [ ] **Criterion 1** — *partially.* The shape is verified to execute **when launched as
      configured**; that Claude Code itself launches it that way is not verified.
- [ ] **Criterion 2** — *first half only.* All seven hooks use the shape, now test-asserted. **None
      is observed to run its script**, which needs the plugin enabled in a live session.

⛔ **Both open criteria are live-observation work and belong to `dry-run` phase 3**, not to another
static pass. The stake is stated in the spec's own root cause and has not changed: if `args` is
being dropped host-wide, the write gate is not gating and feedback capture is not capturing.

## Change 2's precondition is now established — `args` is not in the schema (2026-08-21, `/dry-run` phase 2)

**`args` is not part of the `type: command` hook schema.** The evidence is documentary and
corpus-wide rather than a live observation, which is why the previous pass could not reach it:
it does not require the plugin to be enabled. Claude Code **2.1.239**.

**1. Anthropic's official documentation of the hook object says command hooks are shell commands.**
`~/.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/hook-development/SKILL.md:44-51`
— the `plugin-dev` plugin exists to teach plugin authors this exact file:

> ### Command Hooks
> Execute bash commands for deterministic checks:
> ```json
> { "type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh", "timeout": 60 }
> ```

`grep -rn '\bargs\b'` across that entire skill — `SKILL.md`, `references/patterns.md`,
`references/migration.md` — returns **no hits**. Roughly ten worked examples there and in
`plugin-structure/examples/standard-plugin.md`, every one with interpreter and script inside a
single `command` string.

**2. No plugin on this machine uses `args`, including the fixture that enumerates the schema.**
Seventeen `hooks.json` files across `claude-plugins-official`, `claude-code-plugins` and
`every-marketplace`: every `type: command` entry carries interpreter + script in one `command`
string; not one has an `args` key. Two are decisive on their own:

- `every-marketplace/tests/fixtures/sample-plugin/hooks/hooks.json` is a fixture whose purpose is to
  cover the schema surface — 15 events, plus the `prompt`, `agent`, `timeout`, `async`,
  `asyncRewake` and `if` variants — and it still passes arguments inside `command` (`echo before two`).
- `claude-plugins-official/plugins/security-guidance/hooks/hooks.json` passes a **second argument** to
  its script: `bash "${CLAUDE_PLUGIN_ROOT}/hooks/sg-python.sh" "${CLAUDE_PLUGIN_ROOT}/hooks/ensure_agent_sdk.py"`.
  An official plugin needing to pass an argument is precisely where `args` would appear if it existed.

**3. Every `"args"` key on this machine belongs to an `.mcp.json`,** the stdio MCP-server config where
`args` genuinely is the schema. That is the probable origin of the confusion: two adjacent plugin
config files, one of which takes `command` + `args`.

**4. The silent-failure mechanism, measured.** Bare `python3` fed each event's real payload:

| Event | Result |
|---|---|
| SessionStart, UserPromptSubmit, PreToolUse, PreCompact, SessionEnd | **exit 0, no output** |
| Stop | exit 1, `NameError: name 'false' is not defined` |

Six of the seven hooks are indistinguishable from `hooks/README.md:10`'s documented "no-ops unless a
`config/bootcamp_progress.json` file exists" — a valid Python expression on stdin evaluates and the
interpreter exits 0. Only `Stop` fails visibly, because `stop_hook_active`'s JSON `false` is the one
payload token that is not a Python name. **That asymmetry is why three audits and 3,277 tests never
saw it:** the defect's signature is silence, and silence is also the correct gated behavior.

**5. INV-052's premise is false.** It requires exec form "so hook execution has no shell dependency",
and `hooks/README.md:34-38` asserts exec form "spawns the interpreter directly with **no shell
involved on any platform** (documented Claude Code behavior)". The documented behavior is the
opposite — command hooks *are* shell commands. There is no shell-free hook form to choose, so INV-052
was protecting a property the host never offered.

### Why this is acted on now rather than held for a live observation

⛔ **The corrective change is safe under both hypotheses, which removes the reason to wait.** Moving
the script path into `command` is the form every official plugin ships and the official docs
prescribe, so it runs whether or not `args` is *additionally* honored. Leaving `args` only works if
it is. Change 3's *"do not edit `hooks.json` on a hypothesis"* was the right call when both readings
were open; it no longer applies to a change that is correct either way.

⚠️ **What is still not observed, stated plainly.** Claude Code has not been watched firing these
hooks — that needs the plugin in `enabledPlugins` and a new session, which is the maintainer's call,
not a dry run's. Criterion 2's second half stays open. **Windows is unverified** and cannot be
checked from this Linux machine; the mitigation carried into the fix is the official corpus's own —
quote `"${CLAUDE_PLUGIN_ROOT}/..."` so a path containing a space survives, which is the concrete
hazard change 2 named.
