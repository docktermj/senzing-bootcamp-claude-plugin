# Stop-hook false-positive re-asks the closing question (reopen)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The Stop hook fires its blocking error even on turns that already ended with a
valid, bolded, single 👉 question:

```text
👉 Does this generated scenario work as your bootcamp project?

● Ran 1 stop hook
  ⎿  Stop hook feedback: Bootcamp is active and your last turn ended without a 👉 closing question…
```

Because a blocking Stop hook forces the guide to produce output again, the guide
re-emits the identical question, so the bootcamper sees the **same 👉 question
twice**. The bootcamper reported this occurred on essentially every yielding turn
of the session (Module 0 onboarding gate and Module 1 Step 5 scenario
confirmation) and asked: "Can the Senzing Bootcamp Claude Plugin only ask the
question once?" Per `ground-rules.md` this is the #1 complaint ("zero tolerance").
The bootcamper also asked for a documented way to disable or quiet the nudge.

## Root cause

Partially confirmed — the prior fix is present but ineffective in the field.

`specs/stop-hook-issue.md` (implemented, commit `9391bf1`) fixed the *loop* via
Gate 1 (`stop_hook_active`), but the *false-positive* persists. `plugin.json` is
`0.3.0`, and the version was set in that same commit `9391bf1`; the Python port
(`7e906e2`) followed. So the bootcamper's v0.3.0 ran essentially the current
`plugins/senzing-bootcamp/scripts/stop-nudge.py`.

Gate 3 (`stop-nudge.py:43-74`) reads `transcript_path`, iterates assistant
records, joins each assistant message's text blocks into `last_text`, and exits
silently when the pointer `U+1F449` is in `last_text`. Read statically this
*should* detect a 👉 question anywhere in the final assistant message (including
one followed by a numbered list). Yet the field reports it firing on nearly every
yielding turn, so the detection does **not** match the real Claude Code
transcript. Exact cause is unverified without a captured live transcript; the
concrete suspects:

1. **Flush/timing** — the final turn's assistant message is not yet written to
   the JSONL when the Stop hook reads it, so `last_text` reflects a *prior* turn
   that lacked a 👉 question.
2. **`content` shape** — the text-bearing record's `message.content` is a plain
   string, not a list, so the `isinstance(content, list)` branch
   (`stop-nudge.py:63`) skips it and `last_text` is stale/empty.
3. **Record shape** — the relevant message carries a `type`/structure the parser
   doesn't match (e.g. a sidechain/subagent record, or content blocks other than
   plain `"text"`).

## Proposed change

1. **Reproduce against a real transcript.** Capture `transcript_path` and the
   Stop payload on a turn that genuinely ends with a 👉 question, and confirm
   which assumption above breaks.
2. **Harden Gate 3 detection.** Handle `message.content` as a string *and* a
   list; robustly locate the final assistant message; and when the transcript
   cannot be parsed decisively, prefer staying **silent** if any recent assistant
   text contains 👉 — the bootcamp's zero-tolerance for duplicates makes a missed
   nudge far cheaper than a duplicate question.
3. **Make a single false block harmless.** Because a *blocking* Stop hook forces a
   new turn even when it fires once, evaluate whether the safety net should block
   at all, or instead inject non-blocking guidance, so one false-positive can
   never surface as a visible duplicate question.
4. **Add a disable/quiet switch** (bootcamper request): honor an explicit
   opt-out at a new Gate 0 — e.g. an env var (`SENZING_BOOTCAMP_DISABLE_STOP_NUDGE`)
   or a key in `config/bootcamp_preferences.yaml` — and document it in
   `hooks/README.md`.

## Acceptance criteria

- [ ] Against a **captured real transcript** whose final assistant message ends on exactly one bolded 👉 question (including when the 👉 line precedes a numbered option list), the Stop hook stays silent (exit 0, no block) — verified on a real transcript, not only a synthetic fixture.
- [ ] A yielding turn that genuinely lacks a closing 👉 question still gets exactly one nudge, and never loops (Gate 1 preserved).
- [ ] No bootcamper sees the same 👉 question twice as a result of the Stop hook.
- [ ] A documented switch disables/quiets the Stop-hook nudge (`hooks/README.md`).
- [ ] The hook stays a Python 3 exec-form hook with no shell dependency (INV-052), and holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/stop-nudge.py` — Gate 3 detection fix + new disable gate.
- `plugins/senzing-bootcamp/hooks/README.md` — document the disable/quiet switch.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Onboarding concepts gate question asked twice" and "Stop-hook nudge output is noisy and cannot be easily suppressed" (2026-07-16, Module 0 / Module 1)
- Priority: High (CONFIRMED root cause; #1 bootcamper complaint, zero tolerance)
- Related specs: `stop-hook-issue.md` (prior fix — resolved the *loop* only, not the false-positive detection); `cross-platform-hook-execution.md` (INV-052); `end-of-bootcamp-banner.md` (stand-down after the closing banner)

## Invariants introduced

- `INV-054` — The Stop-hook closing-question safety net MUST NEVER cause the Bootcamper to see the same 👉 question twice; it MUST block only when it can positively determine the current turn ended without a 👉 question, and MUST stay silent whenever that determination is not decisive (recorded in `specs/INVARIANTS.md`).
- `INV-055` — The Stop-hook nudge MUST be disableable via a documented opt-out (`SENZING_BOOTCAMP_DISABLE_STOP_NUDGE` env var or `disable_stop_nudge` in `config/bootcamp_preferences.yaml`) (recorded in `specs/INVARIANTS.md`).
