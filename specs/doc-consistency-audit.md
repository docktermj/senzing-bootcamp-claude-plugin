# Documentation consistency reconciliation

Maintain the invariant conditions in @invariants.md and fix the following issue:

## Problem

The SBCP must be consistent, coherent, and complete. Two documentation
inconsistencies remain, plus one rule that does not account for a real output
location:

1. Stale module-flow note contradicting the actual 1→2→…→7 ordering.
2. An invariants layout reference to a `_POWER_` feedback filename while the plugin
   uses `_PLUGIN_`.
3. The `.md`-under-`docs/` rule has no exception for the generated `production/`
   deliverable, which legitimately writes `.md` files outside `docs/`.

## Root cause

- `MIGRATION.md:479-481` still states "Module 1 transitions to Module 4" (later
  corrected at `MIGRATION.md:548-551`, so the doc contradicts itself).
- `specs/invariants.md:144` lists `docs/feedback/SENZING_BOOTCAMP_POWER_FEEDBACK.md`
  (POWER), whereas the plugin consistently reads/writes
  `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` (PLUGIN).
- `ground-rules.md:81` requires `.md` under `docs/`, but `graduation/SKILL.md:122-132`
  writes `production/README.md`, `production/MIGRATION_CHECKLIST.md`, and
  `production/GRADUATION_REPORT.md` — the intended production-project deliverable.

## Proposed change

- Fix the stale `MIGRATION.md` module-flow note so it matches the real ordering.
- Reconcile the feedback filename in `specs/invariants.md` to `_PLUGIN_`
  (confirm with the maintainer before editing the invariants ruleset).
- Add an explicit exception to the `.md`-location rule for the generated
  `production/` project deliverable (as already exists for the root `README.md`).

## Acceptance criteria

- [ ] `MIGRATION.md` no longer contains a module-flow statement that contradicts the 1→2→…→7 order.
- [ ] The feedback filename is consistent across `specs/invariants.md` and the plugin (all `_PLUGIN_`).
- [ ] `ground-rules.md` documents the `production/` `.md` files as a sanctioned exception to the docs/ rule.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @invariants.md).

## Affected files

- `MIGRATION.md` — stale module-flow note.
- `specs/invariants.md` — POWER→PLUGIN feedback filename (maintainer confirmation).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — production/ docs exception.

## Source

- Audit: `migrate-kiro-power` verify/backfill audit (2026-07-15), invariants T4 and Q2.
- Priority: Low.
- Related specs: `migrate-kiro-power.md`.
