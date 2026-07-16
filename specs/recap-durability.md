# Persist the recap for partially-completed modules (quit / compaction / new session)

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The recap trophy (`docs/bootcamp_recap.md`, rendered to the graduation PDF) is
only appended at module **completion**. If the bootcamper quits mid-module, the
session is compacted mid-module, or a new session starts mid-module, that
module's in-progress recap narrative is not persisted — only
`config/bootcamp_progress.json` (step position) survives. Mid-module progress
detail can therefore be lost from the trophy. Cross-session *resume* of step
position already works; the gap is specifically the recap narrative for a
partially-completed module.

## Root cause

- `plugins/senzing-bootcamp/hooks/hooks.json:1-49` wires `SessionStart`,
  `UserPromptSubmit`, `PreToolUse` (Write|Edit), and `Stop` — but **no**
  `PreCompact` hook and **no** `SessionEnd` hook.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:26-92`
  (Step 2) appends the recap **only at module completion**; its "verify it
  landed" re-append safety (2c) also runs only at completion.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md:48-55` reconciles missing
  sections at graduation, but only for modules already in `modules_completed`.

Nothing flushes an in-progress module's recap before a compaction or exit.

## Proposed change

Close the recap-narrative gap while respecting INV-052 (all hooks are Python 3,
exec-form, `python3`-only dependency, gated on active-bootcamp state). Any of
these, or a combination:

1. **`PreCompact` + `SessionEnd` hooks** (Python, exec form) that, when a bootcamp
   is active (`config/bootcamp_progress.json` present), flush an in-progress recap
   checkpoint (or a scratch journal under `docs/`) before context is summarized /
   on exit.
2. **Per-step recap checkpoint** — have the module skills append an in-progress
   recap checkpoint at each numbered step, not only at module completion.
3. **Fold on resume** — `session-start.py` merges any checkpoint into
   `docs/bootcamp_recap.md` when the bootcamp resumes.

## Acceptance criteria

- [ ] Quitting or compacting mid-module preserves that module's in-progress recap content (a checkpoint exists and is folded into `docs/bootcamp_recap.md` on resume/graduation).
- [ ] Completed-module recap behavior is unchanged (append-only, existing sections never rewritten).
- [ ] Any new hook is a Python 3 exec-form hook gated on active-bootcamp state (INV-052); no new runtime dependency beyond `python3`.
- [ ] The `docs/`/`src/` placement rules (INV-017/INV-050) still hold for any checkpoint file.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/hooks/hooks.json` — register `PreCompact` and `SessionEnd`.
- `plugins/senzing-bootcamp/scripts/*.py` — new hook script(s) for the flush.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` and/or the module skills — per-step checkpoint (if chosen).
- `plugins/senzing-bootcamp/scripts/session-start.py` — fold checkpoint on resume.
- `plugins/senzing-bootcamp/hooks/README.md` — document the new hooks.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "No durability for the recap on quit / compaction / new session mid-module" (2026-07-16, Module 1 → Module 2)
- Priority: Medium
- Related specs: `cross-platform-hook-execution.md` (INV-052); `enrich-feedback-context.md`

## Invariants introduced

- `INV-059` — The in-progress module recap MUST be checkpointed to `docs/progress/recap_checkpoint.md` at step boundaries and folded (append-only, idempotently, never rewriting a completed `## Module N:` section) into `docs/bootcamp_recap.md` by the `PreCompact`, `SessionEnd`, and `SessionStart` hooks (recorded in `specs/INVARIANTS.md`).
