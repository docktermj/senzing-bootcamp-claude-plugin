# Add an end-of-module recap to Bootcamp preparation

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Bootcamp preparation ends by handing off to the first content module without giving
the bootcamper any recap of what was decided during preparation (path, module
selection, verbosity, programming language, integration/deployment targets, git).
Every other module produces a recap; the bootcamper wants preparation to also close
with a recap of the setup choices rather than silently persisting them.

## Root cause

`plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md:266-277`
(`## 7. Hand off to the first selected content module`) invokes the next module
directly, with no recap and no end-of-module summary. The apparatus exemption is
explicit at `:24-29` ("Bootcamp preparation is a **lightweight setup module** …
exempt from the per-module completion apparatus").

**Invariant conflict (do not silently override):** this conflicts with **INV-075**
(prep exempt from a `docs/bootcamp_recap.md` section and not added to
`modules_completed`) and directly with **INV-092** ("Bootcamp preparation stays
fully exempt and is never added to `modules_completed`"). It also engages **INV-032**
(end-of-module summary) and **INV-048/INV-085** (recap sections). Precedent:
`capture-entity-resolution-concepts-in-recap` applied this recap pattern to Module 0
but deliberately withheld it from preparation.

## Proposed change

Two options for the maintainer:

- **(a) Bootcamper-facing recap only (recommended).** At the end of §7, before
  handoff, present a recap of the preparation choices (read from the consolidated
  preference write) in a style similar to a per-module recap — **without** adding
  preparation to `modules_completed` and **without** appending a
  `docs/bootcamp_recap.md` section. This satisfies the "summarize my choices back to
  me" request while preserving INV-092's "never in `modules_completed`" guarantee; it
  relaxes only the "no bootcamper-facing recap" part of INV-075.
- **(b) Full parity.** Append a name-based recap section and add preparation to
  `modules_completed` like a first-class module — this requires amending INV-092 and
  INV-075 and recording the change in `INVARIANTS.md`.

Whichever is chosen, honor verbosity (suppress/shorten under the `minimal` preset)
and state the invariant reconciliation explicitly in the implementation.

## Acceptance criteria

- [ ] At the end of Bootcamp preparation, before handoff, the bootcamper sees a recap of their preparation choices (path, selected modules, verbosity, programming language, integration/deployment targets, git status).
- [ ] Under option (a): preparation is still NOT added to `modules_completed` and no `docs/bootcamp_recap.md` section is written (INV-092/INV-075 preserved). Under option (b): INV-092 and INV-075 are amended and recorded in `INVARIANTS.md`.
- [ ] The recap respects the active verbosity preset (INV-011/INV-012).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — add the recap at the end of §7 (`:266-277`); reconcile the exemption note (`:24-29`).
- `specs/INVARIANTS.md` — amend INV-075/INV-092 only if option (b) is chosen.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Add an end-of-module recap to Bootcamp preparation" (2026-07-22, Module Bootcamp preparation)
- Priority: Medium
- Related specs: `specs/capture-entity-resolution-concepts-in-recap.md` (INV-092, the precedent that excluded preparation); INV-075
