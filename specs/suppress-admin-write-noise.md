# Reduce administrative Write/Edit diff noise during the bootcamp

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Every progress/preference write and every `Write()` the guide performs renders the
full file content/diff inline (e.g. `Update(config/bootcamp_progress.json)`),
which is visual noise in a prose-driven guided experience. The onboarding flow
frames setup and progress tracking as silent/administrative
(`onboarding-flow.md:55-62`, "Do this silently"), but each small write surfaces a
diff, distracting from the teaching flow.

## Root cause

The Claude Code harness renders every Write/Edit tool result inline, and a
consulted `claude-code-guide` investigation (recorded in the feedback follow-up,
2026-07-16) confirmed **no** mechanism suppresses it: no `settings.json` setting,
no output style, no environment variable, no CLI flag, and no keyboard shortcut
collapses Write/Edit tool-result output. Full suppression is therefore not
achievable from the plugin.

The controllable factor is write **frequency and size**. The guide currently
writes config on many sub-steps — the onboarding preface persists preferences per
gate (`onboarding-flow.md:120-121`, `147-148`, `164-165`), and progress is
touched at each boundary (`module-completion.md:16-23`). Each write is a separate
rendered diff. This conflicts with the spirit of INV-012 (output not important to
the bootcamper is suppressed), even though the harness — not the plugin —
controls rendering.

## Proposed change

- **Batch** progress/preference updates to step/module boundaries rather than on
  every sub-step, so diffs appear rarely; keep the config files small; prefer
  minimal edits over full-file rewrites. Encode this as guidance in
  `ground-rules.md` and apply it in `onboarding-flow.md` (one consolidated
  preference write at the end of the preface instead of one per gate) and
  `module-completion.md` (a single batched progress update).
- **Document the finding** (in `hooks/README.md` or a docs note) that no harness
  mechanism collapses Write/Edit output today, so minimizing writes is the only
  lever, and point maintainers to file a Claude Code feature request via
  `/feedback` or <https://claude.com/feedback> — so this is not re-investigated.

## Acceptance criteria

- [ ] Progress/preference writes are batched to step/module boundaries; the onboarding preface performs materially fewer config writes (e.g. one consolidated write at the end of the preface rather than one per gate).
- [ ] Guidance to minimize/batch writes is recorded in `ground-rules.md`, referencing INV-012.
- [ ] The "no harness suppression exists" finding is documented so it is not re-investigated.
- [ ] Progress state stays accurate for cross-session resume, and the INV-050 project layout is unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — batching / minimize-writes guidance + INV-012 note.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — consolidate the per-gate preference writes.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — confirm a single batched progress update.
- `plugins/senzing-bootcamp/hooks/README.md` (or a docs note) — record the no-suppression finding.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Administrative config-file edit diffs are visible noise" and "Suppress the full Write() tool-output details during the bootcamp" (2026-07-16, Module 0)
- Priority: Medium
- Related specs: none

## Invariants introduced

- `INV-058` — Administrative config writes (progress and preferences) MUST be batched to step and module boundaries rather than performed on every sub-step, and the onboarding preface MUST persist all preface choices in one consolidated write (a hardening of INV-012) (recorded in `specs/INVARIANTS.md`).
