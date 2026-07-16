# Bootcamp hooks

The plugin ships these hooks (registered in `hooks.json`). Following the bootcamp
convention, each hook's purpose is phrased beginning with the word "to", from the
bootcamper's point of view. In the Kiro Power these were named hook files
(e.g. "to review what you said"); in the Claude plugin they are `command`-type
hooks wired to small **Python** scripts under `../scripts/`, invoked in exec form
(`python3 <script>`) so no shell is required on any platform.

Every hook is gated on an active bootcamp. Each script no-ops unless a
`config/bootcamp_progress.json` file exists in the working directory, so the
plugin never alters unrelated Claude Code sessions.

| Event | Script | Purpose |
|-------|--------|---------|
| `SessionStart` | `scripts/session-start.py` | to resume an in-progress bootcamp (offers to continue from the last recorded module). |
| `UserPromptSubmit` | `scripts/feedback-capture.py` | to capture bootcamp feedback and verbosity changes at any time (routes "bootcamp feedback" and "change verbosity" requests to the right workflow). |
| `PreToolUse` (Write, Edit) | `scripts/write-gate.py` | to keep your files in the project (blocks writes to system temp / Downloads and obvious hardcoded secrets during a bootcamp). |
| `Stop` | `scripts/stop-nudge.py` | to review what you said and end each turn with one leading question (a loop-safe safety net for the closing 👉 question). |

**Convention (INV-016 interpretation):** the "begin with the word 'to'" rule applies
to each hook's **documented purpose** — the Purpose column above — not to the runtime
text a hook emits (block reasons, injected context, resume notes), which is written
for clarity and is delivered to Claude rather than shown directly to the bootcamper.
Every hook MUST carry a "to …" purpose entry in this table, and new hooks follow the
same rule. This is the settled reading of INV-016 (whose own examples — "to process
your request", "to review what you said" — are purposes), resolving the earlier
ambiguity between the purpose-phrasing and emitted-message readings.

## Runtime prerequisites (per platform)

The hooks are **Python 3** scripts, invoked in Claude Code **exec form**
(`{"command": "python3", "args": ["…/scripts/<hook>.py"]}`). Exec form spawns the
interpreter directly with **no shell involved on any platform** (documented Claude
Code behavior), so the hooks do **not** depend on `bash`, Git Bash, or WSL — even on
Windows.

The only requirement is a `python3` on `PATH`, and it is **not a new dependency** —
the bootcamp already requires `python3` for the Module 3 visualization server
(`scripts/senzing_viz_server.py`) and the graduation recap PDF
(`scripts/generate_recap_pdf.py`), so any machine that can run the bootcamp can run
the hooks.

| Platform | Requirement | Notes |
|----------|-------------|-------|
| Linux | `python3` on `PATH` | Already required by the bootcamp. |
| macOS | `python3` on `PATH` | Already required by the bootcamp. The per-user temp dir under `$TMPDIR` is handled by the write-gate. |
| Windows | `python3` on `PATH` | No shell (Git Bash/WSL) required — exec form spawns Python directly. The command name must be `python3` (the name the rest of the plugin already uses); if only `python`/`py` is installed, add a `python3` entry to `PATH`. |

Environment-variable substitution (`${CLAUDE_PLUGIN_ROOT}`) is performed by Claude
Code identically on all three platforms, including inside `args`.

## Design notes

- **Deterministic gates, not model judgment.** The `Stop` and `PreToolUse` hooks
  are `command` scripts that decide behavior from the on-disk bootcamp-active
  signal, so they never fire in non-bootcamp sessions.
- **Non-blocking by default.** The write-gate can block a tool call (exit 2), and only
  for stray paths or obvious secrets during a bootcamp. The `Stop` hook can block a turn
  from ending (`decision: block`) to request the one forgotten closing 👉 question, but
  only once: it returns success whenever `stop_hook_active` is true, so it can never loop
  on its own continuation, and it stays silent when the session is not a bootcamp, when
  the nudge is disabled (see [Disabling / quieting the Stop-hook nudge](#disabling--quieting-the-stop-hook-nudge)),
  or when the current turn already ends with a 👉 question. Detection scans the whole
  current turn and biases toward silence if the turn's text is not yet on disk, and the
  block reason tells the model to repeat nothing it has already asked — so a false block
  can never surface as a duplicate question. The `UserPromptSubmit` hook injects guidance via
  `additionalContext`; `SessionStart` emits resume context. Everything else emits nothing.
- **Hooks ship with the plugin.** There is no hook-install step (this replaces the
  Kiro `install_hooks.py` / `.kiro/hooks/` workflow).

## Disabling / quieting the Stop-hook nudge

The `Stop` hook (`scripts/stop-nudge.py`) is a safety net for the single closing
👉 question. It stays silent whenever the current turn already ends with a 👉
question, and it biases toward silence when the transcript cannot be read
decisively — a missed nudge is far cheaper than a duplicated question. If you still
want to turn it off, there are two documented, opt-out switches (either one works;
both are read cross-platform with no shell and no extra dependency):

| Switch | Where | Effect |
|--------|-------|--------|
| `SENZING_BOOTCAMP_DISABLE_STOP_NUDGE` | environment variable | Set to `1`/`true`/`yes`/`on` to disable the nudge for the session. |
| `disable_stop_nudge: true` | top-level key in `config/bootcamp_preferences.yaml` | Disables the nudge for the project. |

When either switch is on, the hook returns success immediately (exit 0, no block),
so a turn can never be re-opened to re-ask a closing question. Remove the env var or
set `disable_stop_nudge: false` to re-enable it.
