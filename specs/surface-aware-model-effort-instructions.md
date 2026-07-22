# Make the model/effort switch instructions adapt to the Claude application

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

At every module start the model/effort nudge tells the bootcamper to run
`/model opus` and `/effort high`. These are Claude Code **CLI** slash commands. When
the bootcamper is running Claude Desktop, web, or an IDE extension, the steps to
change model and reasoning effort are different, so the CLI-specific instruction does
not apply cleanly — and the follow-up gate "Are you done modifying the model and
effort?" then reads oddly on those surfaces.

## Root cause

Everything is hardcoded to CLI syntax in
`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`:
session-start definition `:13-19`; the pinned switch question `:228`; the pinned
confirmation gate `:234`; the per-stage command table `:247-252` (every row is CLI
syntax, e.g. `:250`); and the transition sequence re-pinning the gate `:266`.
`docs/model-selection.md` mirrors the CLI table. Nothing branches on which Claude
application is in use.

**Invariant conflict (do not silently override):** **INV-063** mandates surfacing the
recommendation "with the exact `/model` and `/effort` commands"; **INV-069** pins the
gate wording verbatim (via INV-056). A surface-adaptive rewrite must reconcile these —
the "exact commands" clause has to become surface-conditional. Requires amending
INV-063 and INV-069.

## Proposed change

- **Detect the surface when the harness exposes it** and branch the nudge: on the CLI,
  show the `/model` and `/effort` commands verbatim (unchanged); on Desktop/web/IDE,
  show the equivalent UI path (model picker + effort/thinking control) phrased by
  intent.
- **When the surface is unknown, default to surface-agnostic phrasing**, e.g. "set
  your model to Opus 4.8 and reasoning effort to high, using whichever control your
  Claude app provides (the `/model` and `/effort` commands in the CLI, or the
  model/effort controls in Desktop and web)."
- **Make the confirmation gate wording match** whichever instruction form was shown,
  so it reads sensibly on every surface, and keep it pinned per the chosen form
  (INV-056).
- Keep the per-stage recommended values (advisory, in `docs/model-selection.md`)
  unchanged. Do **not** hardcode Desktop/web control labels that may drift — phrase by
  intent and verify against the current Claude UI before finalizing.
- Amend INV-063/INV-069 so the "exact commands" clause applies to the CLI surface and
  intent-based phrasing covers the others.

## Acceptance criteria

- [ ] On the CLI, the nudge still shows the exact `/model` and `/effort` commands (INV-063 behavior preserved for CLI).
- [ ] On non-CLI or unknown surfaces, the nudge is phrased by intent and does not present CLI-only commands as the sole instruction.
- [ ] The confirmation gate reads sensibly on every surface and stays pinned per the chosen form (INV-056).
- [ ] No hardcoded Desktop/web control label that would drift; wording verified against the current UI.
- [ ] `INVARIANTS.md` is updated to amend INV-063 and INV-069.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the model/effort definition (`:13-19`), switch question (`:228`), confirmation gate (`:234`), per-stage table (`:247-252`), transition sequence (`:266`).
- `docs/model-selection.md` — reframe the command table if it needs surface framing.
- `specs/INVARIANTS.md` — amend INV-063 and INV-069.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Make the model/effort 'switch' instructions adapt to the Claude application (CLI vs Desktop vs others)" (2026-07-22, Module SDK setup / all module-start nudges)
- Priority: Medium
- Related specs: `specs/module-start-model-nudge.md`, `specs/model-effort-change-prompt.md`, `specs/model-effort-switch-done-confirmation.md`, `specs/skill-model-selection.md`; INV-063, INV-069, INV-056

## Invariants introduced

- `INV-098` — The model/effort nudge adapts to the Claude application surface: exact `/model`/`/effort` commands on the CLI; intent-based phrasing (model + effort level, directed to the app's controls, no hardcoded labels) on Desktop/web/IDE or unknown surfaces; the pinned switch question and gate keep their surface-neutral core wording (recorded in `specs/INVARIANTS.md`; INV-063 annotated as qualified, INV-069 unchanged). Maintainer-approved wording.
