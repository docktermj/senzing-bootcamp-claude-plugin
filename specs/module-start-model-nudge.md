# Encourage the best-value `/model` + `/effort` at the start of each module

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`skill-model-selection` established that different modules are best served by
different models and efforts, and that the **session** model/effort — not
turn-scoped skill frontmatter — is the reliable lever. But the plugin cannot set
the session itself, and today nothing tells the bootcamper to align their session
to each module's best-value model/effort. So a bootcamper either **overpays**
(Opus 4.8 + high effort through the light conversational modules) or
**underpowers** the heavy ones (staying on a light model through SDK setup,
mapping, and graduation). The per-module recommendations live only in
`docs/model-selection.md`, a maintainer doc the bootcamper never sees.

## Root cause

The module-start sequence — `ground-rules.md` → "Module start banners and
transitions" (`ground-rules.md:162-178`), honored by every module's `**First:**`
step (`module-0N/SKILL.md`) — renders the banner, journey map, before/after
framing, step overview, and Step 1, but **no** model/effort guidance. The levers
exist and are user-runnable mid-session (verified against Claude Code
`model-config` docs):

- `/model <alias|id>` (e.g. `/model opus`, `/model claude-sonnet-5`) switches the
  session model immediately and **persists for the rest of the session**.
- `/effort <level>` (`low`/`medium`/`high`/`xhigh`/`max`, or `/effort auto` to
  reset to the model default) sets the reasoning effort mid-session.

The prior spec deliberately left the session-model note passive — `ground-rules.md`
Session-start "Model tuning (informational) … Mention this only if the bootcamper
asks … otherwise stay silent" — so the value split is never proactively realized.

## Proposed change

Add a brief, **non-blocking** "best-value setup" nudge to the start of each module
(and to graduation), encouraging the bootcamper to run `/model` + `/effort` for
that stage's recommended model/effort.

- **Behavior** (in `ground-rules.md` → "Module start banners and transitions"):
  after the step overview and **before** Step 1, surface **one concise line** with
  the module's recommended model + effort and the exact commands. It is a
  **statement** — never a 👉 question, never an ⛔ gate, never blocks progress,
  never repeated mid-module. Actively encourage the switch **only when the
  recommendation changes** from the module just completed (a heavier module → "for
  best value, switch up"); when it is **unchanged**, keep it to a one-line reminder
  or omit it (INV-012). Always frame switching as optional — running one model for
  everything (Opus 4.8) stays valid (the README "simplest" option).

- **Per-module mapping** (single runtime source of truth, co-located in
  `ground-rules.md` and cross-referenced to `docs/model-selection.md`), derived
  from the `skill-model-selection` evaluation:

  | Stage | Recommended | Commands |
  |---|---|---|
  | Onboarding, Modules 1, 3, 4, 7 | Sonnet 5, medium effort | `/model sonnet` · `/effort medium` |
  | Modules 2, 5 | Opus 4.8, high effort | `/model opus` · `/effort high` |
  | Module 6 | Sonnet 5, high effort (Opus if bespoke load code) | `/model sonnet` · `/effort high` |
  | Graduation | Opus 4.8, high effort | `/model opus` · `/effort high` |

- **Graduation** (`graduation/SKILL.md`): add the same non-blocking nudge
  (`/model opus` + `/effort high`) at the graduation banner step, since graduation
  has its own banner-first flow and does not pass through the module-start section.

- **Extend `docs/model-selection.md`** with the per-module `/model` + `/effort`
  commands (add the effort recommendation and a "module-start commands" reference)
  so the maintainer doc and the runtime nudge stay in sync.

- **Update the existing `ground-rules.md` Session-start "Model tuning" note**:
  replace the "mention only if asked / stay silent" stance with a pointer to the
  new proactive module-start nudge.

## Acceptance criteria

- [ ] At every module start, the guide surfaces the module's recommended model + effort with the exact `/model` and `/effort` commands, as a non-blocking statement (not a 👉 question, not a gate), before Step 1.
- [ ] The switch is actively encouraged when the recommendation changes from the prior module, and kept minimal (or omitted) when unchanged (INV-012); it is never repeated mid-module.
- [ ] Graduation start carries the same nudge (`/model opus` + `/effort high`).
- [ ] The per-module model/effort mapping is consistent with `docs/model-selection.md`, which is extended with the per-module commands and effort.
- [ ] The nudge never adds a second 👉 question to a turn and never blocks progress; switching stays optional (running Opus 4.8 for everything is still valid).
- [ ] The commands are real and current (`/model <alias|id>`, `/effort <level>`), matching the Claude Code `model-config` docs.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — add the module-start nudge behavior + per-module mapping; update the Session-start "Model tuning" note from passive to proactive.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — add the graduation-start nudge.
- `plugins/senzing-bootcamp/docs/model-selection.md` — add per-module `/model` + `/effort` commands and the effort recommendation; cross-link the module-start nudge.
- (optional) `plugins/senzing-bootcamp/skills/module-0N/SKILL.md` — a per-module one-line "Recommended model/effort" field, if the maintainer prefers module-owned recommendations over the central mapping.

## Source

- Maintainer request (2026-07-16): encourage the bootcamper to run `/model [best-model-for-module]` and set the appropriate effort at the start of each module, for best value in models and efforts.
- Priority: Medium (operationalizes the `skill-model-selection` value split; user-visible, but non-blocking).
- Related specs: `skill-model-selection.md` (the evaluation and `docs/model-selection.md` this builds on), `defer-commonmark-to-graduation.md`.

## Invariants introduced

- `INV-062` (behavior-level) — At every module start, and at graduation start, the guide MUST surface the recommended session model and reasoning effort as a concise, **non-blocking** suggestion carrying the exact `/model` and `/effort` commands — never as a 👉 question or ⛔ gate, and never blocking progress. The specific per-module model/effort values are advisory (maintained in `docs/model-selection.md`) and are **not** part of the invariant (recorded in `specs/INVARIANTS.md`). (Assigned INV-062 at implementation — INV-061 went to `auto-detect-platform`.) **Later superseded by `INV-063`** (`model-effort-change-prompt`), which changes the nudge from a non-blocking statement to a change-triggered 👉 switch question.
