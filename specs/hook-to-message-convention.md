# Hook messages: resolve the "begin with 'to'" convention

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The invariants state: "All hooks begin with the word 'to' (e.g. 'to process your
request', 'to review what you said')." Today the hook *purpose* descriptions in
`hooks/README.md` follow this ("to resume…", "to capture…", "to review…"), but the
messages the hooks actually emit to the bootcamper do **not** begin with "to".
The intent of the invariant is ambiguous — it may mean the hook's purpose phrasing
(already satisfied) or the emitted runtime message (not satisfied).

## Root cause

The Kiro Power expressed each hook's action as a "to …" purpose string. In this
plugin the runtime messages read as blunt status/error lines:

- `plugins/senzing-bootcamp/scripts/write-gate.sh:27` — "Write blocked: use a project-relative path…"
- `plugins/senzing-bootcamp/scripts/write-gate.sh:67` — "Write blocked: a possible hardcoded secret…"
- `plugins/senzing-bootcamp/scripts/stop-nudge.sh:71` — "Bootcamp is active and your last turn ended…"
- `plugins/senzing-bootcamp/scripts/session-start.sh:5` — "A Senzing bootcamp is in progress…"

## Proposed change

Decide the reading and make the plugin consistent with it:

- **Option A (purpose reading):** treat the invariant as "each hook's documented
  purpose begins with 'to'." Confirm `hooks/README.md` covers every hook with a
  "to …" purpose line, and add any missing ones. Lowest risk; no UX change.
- **Option B (message reading):** rephrase the emitted messages to begin with "to"
  (e.g. "to keep your files in the project, use a project-relative path…"). Verify
  the rephrasing does not degrade clarity of the block/nudge messages.

Pick one, apply it uniformly, and note the decision so the invariant is no longer
ambiguous.

## Acceptance criteria

- [ ] The chosen reading is applied to **every** hook consistently, with no hook left half-converted.
- [ ] If Option B: each emitted hook message begins with "to" and still communicates the block/nudge clearly; `write-gate.sh` and `stop-nudge.sh` still block/allow exactly as before (re-run their existing verification scenarios).
- [ ] The interpretation is recorded (in `hooks/README.md` or the invariants) so future hooks follow it.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/hooks/README.md` — purpose descriptions / recorded interpretation.
- `plugins/senzing-bootcamp/scripts/write-gate.sh`, `stop-nudge.sh`, `session-start.sh`, `feedback-capture.sh` — only if Option B is chosen.

## Source

- Audit: `migrate-kiro-power` verify/backfill audit (2026-07-15), invariant Q1.
- Priority: Low (needs a maintainer interpretation decision first).
- Related specs: `migrate-kiro-power.md`.
