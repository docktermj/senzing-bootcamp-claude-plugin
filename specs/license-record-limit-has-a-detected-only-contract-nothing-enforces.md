# `license_record_limit` has a detected-only contract that nothing enforces, and Module 2 treats its presence as proof a license was configured

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`license_record_limit` in `config/bootcamp_progress.json` is the field INV-244 makes authoritative
**because it is measured**. Its contract is stated descriptively in two places and enforced in
neither, so a value that was never measured can occupy it and be believed downstream.

**Observed 2026-08-25.** The Bootcamper said their POC license allows 100,000 records. The guide
wrote `license_record_limit: 100000` on the strength of that statement. In SDK setup, running the
authoritative `GetLicense` snippet against the freshly installed SDK returned `recordLimit: 500`
with `licenseType: "EVAL (Solely for non-productive use)"` — the built-in evaluation license. The
POC key had never been applied to this install. The value was withdrawn and replaced with the
measured 500.

**The two sites, and what each does wrong:**

1. `module-01-business-problem/phase1-discovery.md:275-277` states the contract correctly —
   *"`license_record_limit` is written only by Module 4's Step 8a gate … its absence here means
   **not yet measured** — not **no custom license**"* — but states it as an **explanation of the
   absent case**, not as a prohibition on writing. Nothing in Module 1 says "do not write this
   field."
2. `module-02-sdk-setup/SKILL.md:1030-1035` (**Step 5a, already-licensed guard**) then *infers from
   presence*: *"If a `license_record_limit` field is present, a custom license has already been
   configured (its limit **was detected earlier**, this session or a prior one)."* The parenthetical
   asserts detection that nothing established. On this run it would have presented **100,000** as
   "the authoritative limit" and skipped the evaluation-license note, on an install capped at 500.

⛔ **The consequence is a suppressed warning, not a wrong number.** A `license_record_limit` above
the dataset size **suppresses** Module 4's Step 8a License Key gate — the single volume-gated prompt
in the whole bootcamp, and the one thing that warns a Bootcamper before they hit the cap mid-load.
A fabricated 100,000 against a real 500, on a ~94,000-record scenario, removes the warning entirely.
This is the same failure shape INV-244 was written for, reached from the opposite direction: INV-244
guards against reading *absence* as "no license"; nothing guards against reading a *present but
unmeasured* value as a measurement.

⚠️ **There is nowhere to record what the Bootcamper actually said.** The run invented
`license_stated_poc_limit` on the spot. No such key exists in the plugin (`grep` for
`license_stated` across `plugins/` returns nothing), so a stated-but-unapplied entitlement has no
home and naturally lands in the one field that looks right and is not.

## Root cause

The field's name says what it holds and not where it may come from, and its provenance rule lives in
prose that explains a *different* branch. Module 1 reads the field and explains why it is absent;
Module 2 reads the field and explains what its presence means. Neither owns the write, so no step is
positioned to forbid one — and Module 4's Step 8a, the only legitimate writer, runs after both.

## Proposed change

1. **State the write rule as a prohibition, at the sites that read it.** `license_record_limit` is
   written **only** from a measured license — the `getLicense`/`get_license` record limit — and
   **never** from a Bootcamper statement, a scenario assumption or recall. Say it where a guide is
   holding a number and deciding where to put it (Module 1's Step 5a comparison), not only where the
   absent branch is explained.
2. **Give a stated entitlement its own key** — e.g. `license_stated_limit` — so a Bootcamper's claim
   can be recorded without being mistaken for a measurement. Name it where the claim is likely to
   arrive (Module 1), and state that it is **never** read by a gate.
3. **Stop inferring detection from presence** at `module-02-sdk-setup/SKILL.md:1030-1035`. Either
   the guard reconciles the recorded value against a measurement before presenting it as
   authoritative, or it presents it as recorded-not-verified. ⚠️ **Prefer reconciliation:** SDK setup
   is the first point where the SDK exists and `getLicense` can actually run, which is what made the
   contradiction visible on this run at all.
4. ⛔ **Do not add a license prompt to Module 1.** INV-093 permits exactly one volume-gated License
   Key prompt, at Module 4. This spec adds a provenance rule and a second key, never a question.

## Acceptance criteria

- [ ] A shipped site states that `license_record_limit` is written only from a measured license and
      never from a Bootcamper statement, phrased as a prohibition rather than as an explanation of
      the absent branch.
- [ ] A separate key exists for a stated-but-unapplied entitlement, and shipped text says no gate
      reads it.
- [ ] `module-02-sdk-setup/SKILL.md` Step 5a no longer asserts that a present
      `license_record_limit` **was detected**; it either reconciles against a measurement or says
      the value is recorded rather than verified.
- [ ] No new 👉 question is added to Module 1 (INV-093, INV-251).
- [ ] A test asserts the prohibition and the second key both appear, and that Step 5a's guard no
      longer claims detection from presence alone. Stdlib only, no `plugins/` import (INV-108).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — the write
  prohibition and the stated-entitlement key, near `:248` and `:275-277`
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 5a's already-licensed guard
  at `:1030-1035`
- `tests/` — a guard for the prohibition, the second key, and the corrected inference

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: license_record_limit was recorded
  from a bootcamper statement rather than a measurement" (2026-08-25, Module: SDK setup, Priority:
  Medium; `Source: self-observed (assistant retrospective)`). Filed by the guide against its own
  earlier write, after the measurement contradicted it — the reversal class a Bootcamper cannot
  report, because on screen the first number looked like a fact.
- Priority: **Medium**, as filed. Not High because the run caught it at SDK setup and withdrew it;
  the ceiling on severity is only that the measurement happens to come a module later.
- MCP re-check: **server 1.33.0, 2026-08-28 — confirmed, with one correction to what may be
  asserted.** `get_sdk_reference(topic='response_schemas', filter='getLicense', language='java')`
  returns the method — `SzProduct.getLicense() -> String` — and an **empty** `data` array, so the
  server documents the call and **not** the JSON shape it returns. The field names `recordLimit` and
  `licenseType` in the report are therefore **observation-only** from a live engine (INV-080,
  INV-149) and are written that way here, not laundered into an MCP-sourced claim. The built-in
  500-record limit is separately confirmed by `sdk_guide(topic='load', language='java',
  record_count=1000)`, whose `compatibility_notes` state *"exceeds the default Senzing license limit
  of 500"* (server 1.33.0, 2026-08-28).
- Upstream: not applicable — the defect is this plugin's field contract, not server behavior.
- Related specs: `specs/scenario-generation-has-no-size-cap-or-load-time-warning.md` (the same
  session's other half — the 94,000-record scenario sized against the entitlement this field
  wrongly held); `specs/license-limit-assumed-when-it-could-be-measured.md` and
  `specs/inv244-absent-license-branch-exists-in-module-4-too.md` (the INV-244 lineage, both about
  the *absent* branch this spec's mirror image);
  `specs/step1-license-framing-ignores-the-measured-record-limit.md` (a reader of the same field,
  implemented 2026-08-28)
