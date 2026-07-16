# Stop-nudge false-positive on tool-using turns (partial transcript flush)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

On nearly every **tool-using** turn, the Stop hook (`scripts/stop-nudge.py`)
surfaces its full reminder — "Bootcamp is active. Before doing anything else,
re-read your own most recent message…" — even though the guide's message already
ended with a single closing 👉 question. The reminder is long, appears after
almost every turn, clutters the transcript, and implies the guide erred when it
did not. This is the INV-054 duplicate-question failure mode resurfacing,
specifically on turns that call tools.

## Root cause (confirmed)

`stop-nudge.py:124-153` (`current_turn_text`) concatenates **all** assistant text
since the last real user prompt. Gate 4 (`:186-193`) then blocks when that text is
non-empty and lacks 👉, biasing to silence **only** for the fully-empty case
(`:192-193`).

On a tool-using turn, the pre-tool narration text is flushed to the transcript,
but the final assistant message carrying the 👉 closing question races and is not
yet written when the Stop hook reads. So `current_turn_text` returns non-empty text
**without** the pointer → Gate 4 blocks. The empty-turn guard (`:192-193`) does not
cover this **partial-flush** case (some text present, closing line missing), and
the parser does not detect that the turn's last record is a `tool_use`/`tool_result`
(turn still settling). This is the residual field failure that the implemented
`stop-hook-false-positive.md` (INV-054) did not close — INV-054 already requires
silence "whenever that determination is not decisive … the turn's assistant text is
not yet flushed," so the partial-flush case is in scope but unhandled.

## Proposed change

Extend Gate 4 to bias to silence in the partial-flush / tool-in-progress case:

1. **Detect an in-progress turn.** If the last record of the current turn is an
   assistant `tool_use` (or a `tool_result` carrier) with no subsequent final
   assistant text, treat the turn as still settling → stay silent.
2. **Prefer the final assistant text record over the concatenation.** Base the
   pointer check on the last assistant text block; an unflushed final line then
   reads as "no final text yet → silent" rather than "text without pointer →
   block."
3. Optionally add a short settle/retry read of the transcript before deciding.

Keep Gate 1 (loop breaker), Gates 2/3/3b, the string-or-list `message.content`
handling, and the block-reason wording intact.

## Acceptance criteria

- [ ] On a tool-using turn whose final (not-yet-flushed) message ends with a single 👉 question, the Stop hook stays silent (exit 0, no block) — verified against a captured transcript where the last record is a `tool_use`/`tool_result` and the pointer line is absent.
- [ ] A yielding turn that genuinely lacks a 👉 closing question still gets exactly one nudge and never loops (Gate 1 preserved).
- [ ] No bootcamper sees the same 👉 question twice due to the Stop hook (INV-054 upheld), the partial-flush case included.
- [ ] The hook stays a python3 exec-form hook with no shell dependency (INV-052); holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/stop-nudge.py` — `current_turn_text` / Gate 4: detect a trailing `tool_use`/`tool_result` and an unflushed final line, and bias to silence.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Stop-nudge hook misfires on tool-using turns, showing its reminder text repeatedly" (2026-07-16, Onboarding).
- Priority: Medium (bootcamper had to set `disable_stop_nudge` to quiet it; it is an INV-054 residual gap).
- Related specs: `stop-hook-false-positive.md` (INV-054, INV-055 — this closes the partial-flush residual), `stop-hook-issue.md` (the loop fix), `cross-platform-hook-execution.md` (INV-052).
