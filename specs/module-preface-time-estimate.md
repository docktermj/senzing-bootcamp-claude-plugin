# Add an estimated time-to-complete to each module preface

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Each module preface (the "🚀 MODULE: xxxxx 🚀" banner, "Your journey:",
"Before / after:", "What we'll do here:") gives no sense of how long the module will
take. Knowing roughly how much time a module needs helps the bootcamper plan their
session before committing to it.

## Root cause

The module-start apparatus is fully specified in
`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`, section
"Module start banners and transitions" (`:194-269`): apparatus enumeration `:197-204`,
model/effort prompt as the last preface element `:222`, banner block `:254-260`,
transition assembly order `:263`. There is no time-estimate element anywhere in the
preface (a grep finds only an unrelated data-load "elapsed/estimated time" note at
`module-06-data-processing/phaseC-multi-source.md:108`).

**Invariant note:** additive to the module-start apparatus (INV-028–031 / INV-079).
It must honor verbosity (INV-011/INV-012): a time estimate is explanatory output, so
it is suppressed/shortened under the `minimal` preset (per `verbosity-minimal-preset`).
The apparatus-exempt setup modules — Bootcamp preparation (INV-075) and Module 0
(INV-078) — run no preface apparatus, so no estimate applies to them. A new invariant
would be established.

## Proposed change

In the "Module start banners and transitions" section of `ground-rules.md`, add an
"estimated time to complete" line near the end of the preface (after the step
overview / around the model/effort prompt). Requirements:

- **Honest and range-based** (e.g. "roughly 15–30 minutes, depending on
  download/install speed"), never a single precise figure.
- **Explicitly caveated** as varying with workstation power, business-scenario
  complexity, data volume, and how much must be downloaded/installed.
- **No fabricated numbers**: when a meaningful estimate is not possible, say plainly
  that it is hard to estimate for this module rather than invent one.
- **Suppressed or shortened under the `minimal` verbosity preset.**
- Applies only to the numbered content modules that run the preface apparatus, not the
  apparatus-exempt setup modules.

## Acceptance criteria

- [ ] Every content module's preface includes an honest, range-based, caveated time-to-complete, or an explicit "hard to estimate for this module" statement.
- [ ] No single precise number is presented without a range and caveat; no estimate is fabricated when it is genuinely unknowable.
- [ ] The estimate is suppressed/shortened under the `minimal` verbosity preset (INV-011/INV-012).
- [ ] Bootcamp preparation and Module 0 (apparatus-exempt) show no estimate.
- [ ] `INVARIANTS.md` records the new module-start apparatus element.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — "Module start banners and transitions" section (`:194-269`).
- `specs/INVARIANTS.md` — new invariant for the time-estimate apparatus element.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Add an estimated time-to-complete to each module preface" (2026-07-22, Module All modules / module-start banner)
- Priority: Medium
- Related specs: `specs/module-references-by-name-not-number.md`, `specs/module-step-overview.md`, `specs/verbosity-minimal-preset.md`; INV-079, INV-011, INV-012

## Invariants introduced

- `INV-096` — Every numbered content module's start apparatus includes an honest, range-based, caveated estimated time-to-complete (after the step overview, before the model/effort prompt), stated as "hard to estimate" rather than fabricated when unknowable; suppressed under `minimal` and one line under `concise`; not shown for the apparatus-exempt setup modules (recorded in `specs/INVARIANTS.md`). Maintainer-approved wording.
