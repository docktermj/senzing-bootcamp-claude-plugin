# Bootcamp hooks

The plugin ships these hooks (registered in `hooks.json`). Following the bootcamp
convention, each hook's purpose is phrased beginning with the word "to", from the
bootcamper's point of view. In the Kiro Power these were named hook files
(e.g. "to review what you said"); in the Claude plugin they are `command`-type
hooks wired to small scripts under `../scripts/`.

Every hook is gated on an active bootcamp. Each script no-ops unless a
`config/bootcamp_progress.json` file exists in the working directory, so the
plugin never alters unrelated Claude Code sessions.

| Event | Script | Purpose |
|-------|--------|---------|
| `SessionStart` | `scripts/session-start.sh` | to resume an in-progress bootcamp (offers to continue from the last recorded module). |
| `UserPromptSubmit` | `scripts/feedback-capture.sh` | to capture bootcamp feedback and verbosity changes at any time (routes "bootcamp feedback" and "change verbosity" requests to the right workflow). |
| `PreToolUse` (Write, Edit) | `scripts/write-gate.sh` | to keep your files in the project (blocks writes to system temp / Downloads and obvious hardcoded secrets during a bootcamp). |
| `Stop` | `scripts/stop-nudge.sh` | to review what you said and end each turn with one leading question (a loop-safe safety net for the closing 👉 question). |

## Design notes

- **Deterministic gates, not model judgment.** The `Stop` and `PreToolUse` hooks
  are `command` scripts that decide behavior from the on-disk bootcamp-active
  signal, so they never fire in non-bootcamp sessions.
- **Non-blocking by default.** The write-gate can block a tool call (exit 2), and only
  for stray paths or obvious secrets during a bootcamp. The `Stop` hook can block a turn
  from ending (`decision: block`) to request the one forgotten closing 👉 question, but
  only once: it returns success whenever `stop_hook_active` is true, so it can never loop
  on its own continuation, and it stays silent when a 👉 question is already pending or the
  session is not a bootcamp. The `UserPromptSubmit` hook injects guidance via
  `additionalContext`; `SessionStart` emits resume context. Everything else emits nothing.
- **Hooks ship with the plugin.** There is no hook-install step (this replaces the
  Kiro `install_hooks.py` / `.kiro/hooks/` workflow).
