# Reconcile the Advanced Topics track (Modules 8–11) with what actually ships

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

INV-013 requires all modules to run in order `1 → 2 → … → 11`, and INV-049 /
INV-050 reference production hardening in Modules 8–11. But Modules 8–11 do not
exist. The Advanced Topics track (performance, security, monitoring, deployment)
is **offered and sold** at onboarding, then silently collapses to graduation after
Module 7 — so an Advanced-track Bootcamper is promised scope the plugin cannot
deliver, and INV-013's "…→ 8 → 9 → 10 → 11" tail is unreachable in any track.

## Root cause (confirmed)

- Only `plugins/senzing-bootcamp/skills/module-01-…` through `module-07-…` skill
  directories exist; there are no `module-08`–`module-11` skills.
- The Advanced track is offered at onboarding
  (`skills/bootcamp-onboarding/onboarding-flow.md:112,149-152`,
  `skills/bootcamp-onboarding/SKILL.md:36`) as "Modules 1-11 … performance,
  security, monitoring, deployment."
- The flow openly admits the gap: `skills/module-07-query-visualize-discover/phase1-query-visualize.md:253-255`
  — "The advanced modules (8-11) are a later porting phase; until they land, offer
  graduation as the close-out for both tracks."
- Graduation even ships a migration-checklist warning that these topics "were not
  covered" (`skills/graduation/SKILL.md:206`).
- The per-stage model/effort tables cover only Onboarding, Modules 1–7, and
  Graduation (`skills/bootcamp-onboarding/ground-rules.md:195-200`,
  `docs/model-selection.md:91-96`) — no rows for 8–11.

## Proposed change

Pick one of two directions (maintainer decision — this spec captures both):

1. **Build Modules 8–11.** Add `module-08`…`module-11` skills (performance,
   security, monitoring, deployment) following the established module structure
   (SKILL.md + phase files, banners/journey/before-after/step-overview per
   INV-028–032, module-end summary per INV-032), add their model/effort rows to
   `ground-rules.md` and `docs/model-selection.md`, and wire the Module 7 → 8 → …
   → 11 → graduation transitions. This makes INV-013 literally true.
2. **Reframe the scope** so the promise matches the deliverable: present the
   Advanced Topics as post-bootcamp/production follow-ups (already partly done via
   the graduation `MIGRATION_CHECKLIST.md`) rather than as numbered in-bootcamp
   Modules 8–11, and clarify INV-013 (in-place wording, no meaning change) so the
   ordered-module guarantee is scoped to the modules that ship. Remove or soften
   the "Modules 1-11" framing at `onboarding-flow.md:149-152`.

Whichever is chosen, the onboarding offer, INV-013's wording, and the graduation
close-out must agree (INV-003).

## Acceptance criteria

- [ ] The Advanced Topics track no longer promises scope the plugin cannot deliver: either Modules 8–11 exist and run in order (Option 1), or the offering and INV-013 are reframed to match what ships (Option 2).
- [ ] Onboarding (`onboarding-flow.md`), INV-013 in `specs/INVARIANTS.md`, and the graduation close-out describe the same module scope (INV-003).
- [ ] If Option 1: Modules 8–11 satisfy the per-module invariants (INV-028–032) and have model/effort rows in `ground-rules.md` and `docs/model-selection.md`; the "later porting phase" note at `module-07-…/phase1-query-visualize.md:253-255` is removed.
- [ ] If Option 2: no plugin text advertises numbered Modules 8–11 as part of the bootcamp; INV-013's ordered-module range is clarified in place (no meaning change beyond scoping to shipped modules).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — the track offer / "Modules 1-11" framing.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/SKILL.md` — track description.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — the "later porting phase" close-out note.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the not-covered migration-checklist note.
- `plugins/senzing-bootcamp/skills/module-08…11-*` — **new** (Option 1 only).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`, `plugins/senzing-bootcamp/docs/model-selection.md` — model/effort rows (Option 1 only).
- `specs/INVARIANTS.md` — INV-013 wording clarification (Option 2 only; in-place, no meaning change).

## Source

- Invariant audit, 2026-07-17 (deep-dive over the plugin), INV-013 completeness finding — no `module-08`–`module-11` skills exist while the Advanced track is offered.
- Priority: Medium-High (advertised scope vs. deliverable scope mismatch).
- Related specs: none. Bears on INV-013, INV-049, INV-050, INV-028–032, INV-063.
