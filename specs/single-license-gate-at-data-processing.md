# Consolidate the Senzing License Key prompt into a single gate where the bootcamper's data is processed

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The Senzing License Key question is asked during SDK setup (Module 2, Step 5), with
license handling also present in Discover the Business Problem (Module 1, Steps
5a-5e). The bootcamper finds SDK setup an unnatural place to ask — the license only
matters once *their* data is processed at volume — and the split logic risks being
asked in more than one place. They want the prompt consolidated to **at most once**,
placed where their own data first gets processed. The built-in 500-record evaluation
license already covers System verification and Truth Set visualization (small
synthetic/Truth-Set data), so no key is needed before Data collection.

## Root cause

License logic lives in three places, all keyed off the persisted
`license_record_limit`:

- **Module 2, Step 5 (unconditional ask):** `module-02-sdk-setup/SKILL.md` — declared
  mandatory always-run (`:87`, `:323`); the ask is at `:415`/`:424`. It has skip-guards
  that read a persisted result (`:338`, `:400-403`) but is otherwise **not**
  volume-gated — it asks even when the built-in eval license suffices. This is the
  unnatural SDK-setup prompt the bootcamper objects to.
- **Module 1, Step 5a (already volume-gated):** `module-01-business-problem/phase1-discovery.md:111-124`
  — computes the total record count, reads the limit, and asks only if the total
  exceeds it (`:114` handles the ≤-limit skip; ask at `:124`).
- **Module 4, Step 8a (volume-gated back-fill):** `module-04-data-collection/SKILL.md:52-58`,
  `:372-383` — reads the limit and surfaces Module 1's guidance only if the collected
  total exceeds the eval limit.

So the persistence, read-back, and the "volume ≤ limit ⇒ don't ask" behavior already
exist in Modules 1 and 4. The gap: Module 2 Step 5's unconditional ask, and Module 4
is only a *back-fill*, not the primary single gate.

**Invariant note (do not silently override):** **INV-036** currently establishes the
license under **Module 2**; relocating the primary ask to Module 4 changes where
INV-036 is satisfied and requires rewording it. **INV-006** (each question asked once)
is the existing basis the guards already cite and supports "at most once." Requires
amending INV-036.

## Proposed change

1. **Make the single canonical license gate live at the start of Data collection
   (Module 4)** — after the bootcamper's data sources/volume are known but before any
   load — reusing the existing Module 4 (Gate C) plumbing.
2. **Reduce Module 2 Step 5 to a one-line statement** that the built-in 500-record
   evaluation license is active and a key will be requested later if needed — remove
   the prompt.
3. **Keep the volume-skip:** if the chosen data volume ≤ the active limit, do not ask
   at all (as this run's ~450 records already demonstrate).
4. **Every other module reads the persisted result** (`license_record_limit` /
   `license`) instead of re-asking (INV-006). Reconcile Module 1's conditional gate:
   either fold it into the Module 4 gate, or make Module 1 compute-only (no ask) and
   Module 4 the sole ask.
5. Amend INV-036 to reflect the relocated gate.

## Acceptance criteria

- [ ] The License Key is prompted at most once across the entire bootcamp.
- [ ] SDK setup (Module 2) no longer prompts for a license key; it only states the built-in eval license is active.
- [ ] The single gate is at the start of Data collection (Module 4), before any load, driven by the persisted `license_record_limit`.
- [ ] If the chosen data volume ≤ the active limit, no key is requested.
- [ ] All later modules read the persisted result instead of re-asking (INV-006).
- [ ] System verification and Truth Set visualization (between Modules 2 and 4) still run on the built-in eval license, unaffected.
- [ ] `INVARIANTS.md` is updated to amend INV-036 (license gate relocated to Module 4).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 5 (`:323`, `:400-424`): replace the prompt with a one-line eval-license statement.
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — promote the Step 8a region (`:372-383`) to the primary single gate, asked before load.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — Steps 5a-5e (`:111-124`): reconcile to compute-only or remove the ask.
- `specs/INVARIANTS.md` — amend INV-036.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Ask for the Senzing License Key once, at the natural point where the bootcamper's own data is processed (not in SDK setup)" (2026-07-22, Module SDK setup → Data collection)
- Priority: High
- Related specs: `specs/module2-license-clarity.md`, `specs/module1-license-flow-parity.md`, `specs/license-request-option.md`; INV-036, INV-006
