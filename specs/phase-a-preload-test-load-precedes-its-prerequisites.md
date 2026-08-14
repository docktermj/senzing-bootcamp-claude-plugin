# Phase A's pre-load test-load step precedes both of its prerequisites

## Problem

`module-06-data-processing/phaseA-build-loading.md` opens with a "Before Loading: pre-load checks"
section whose first line is:

> Complete these three checks before starting step 1.

The first of those checks (`phaseA-build-loading.md:11-21`, "Conditional workflow, check Phase 3
status") reads `test_load_status` per source and, when it is **`skipped` or missing**, instructs:

> include a brief test-load step: run a quick load of 10–100 records to verify the data loads
> before production concerns, then set `test_load_status: complete`.

Positioned before step 1, that instruction is **unexecutable**, for two independent reasons:

1. **No loading program exists yet.** The loader is built at step 3
   (`phaseA-build-loading.md:123`), from a scaffold selected by the volume tier captured at step 1.
   At the pre-load checks there is nothing to run.
2. **No `DATA_SOURCE` code is registered yet.** Step 4a
   (`phaseA-build-loading.md:238-271`) registers the codes and states its own reason: so the first
   load "does not fail with `SENZ2207: Data source code [...] does not exist`". A test load run
   before step 4a hits exactly that error — the one step 4a exists to prevent.

`test_load_status` is missing on every source whenever Module 5 Phase 3 (the optional sandbox test
load) was skipped, which `module-05-data-quality-mapping/SKILL.md:111` marks **Optional** and which
the `mapping_workflow` step-5 `skip` branch makes the cheap default. So this is the common path,
not an edge case.

Observed on a `/dry-run` phase 3 walk, 2026-08-14: three synthesized sources, all with no
`test_load_status`, entering Phase A on a freshly seeded datastore whose config knew none of the
three data source codes.

## Root cause

The pre-load checks section was written as a *gating* preamble ("complete these before step 1"), but
one of its three checks prescribes an *action* whose prerequisites are produced by steps 1–4a. The
other two checks (CORD freshness, anti-pattern lookup) are genuinely preamble-safe, which is
probably why the placement was never questioned.

**The action already has a correct home.** `phaseB-load-first-source.md:9-22` is
"**5. Test with sample data (if Phase 3 was skipped)**" — the same test load, on the same condition,
positioned after step 4a's registration where it can actually run. So Phase A's copy is not merely
mis-ordered, it is a **duplicate** of a step that already exists downstream, and the two are gated on
the same condition. A guide that obeys both runs the test load twice; a guide that obeys Phase A's
placement runs it before it can work.

## Proposed change

Delete the action from Phase A. Phase B step 5 already carries it.

1. In `phaseA-build-loading.md`, under "Conditional workflow, check Phase 3 status", change the
   `skipped`-or-missing branch from prescribing a load to **recording the need** and naming where it
   happens — e.g. "note that a brief test load is owed; Phase B step 5 runs it, after the data
   source codes are registered."
2. In `phaseB-load-first-source.md:9-22`, add the `test_load_status: complete` write on success —
   Phase A's copy is the only place that currently mentions setting it, so deleting Phase A's action
   without this would lose the write entirely.
3. State the ordering reason inline at Phase B step 5, so the two halves cannot drift apart again:
   the test load needs the loader from step 3 and the registered codes from step 4a.

## Acceptance criteria

- `phaseA-build-loading.md`'s pre-load checks contain no instruction to execute a load.
- The `skipped`-or-missing branch defers the test load and names Phase B step 5 as where it happens.
- `phaseB-load-first-source.md` step 5 sets `test_load_status: complete` on success.
- A test asserts that no text under `phaseA-build-loading.md`'s "Before Loading" section instructs
  running a load, and that `phaseB-load-first-source.md` mentions `test_load_status`.

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md`
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md`
- `tests/test_module06_phase_ordering.py` (new)

## Source

`/dry-run` phase 3, 2026-08-14. Analysis started at Data processing; modules 1–8 fast-forwarded.
Senzing MCP server 1.32.9, docs indexed 2026-08-11 20:52 UTC. SENZ2207 is quoted from the plugin's
own step 4a text, not re-verified against the live engine on this walk.

## Deviations from this spec, and why (2026-08-14)

Implemented as proposed — all three changes, all four criteria. Four things to record.

1. **SENZ2207 was re-verified, and the spec flags it as unverified.** The spec's Source section
   says the code is "quoted from the plugin's own step 4a text, not re-verified against the live
   engine on this walk". Asked directly: `explain_error_code('SENZ2207')` on server 1.32.9
   (2026-08-14) returns `EAS_ERR_DATA_SOURCE_CODE_DOES_NOT_EXIST: Data source code [{0}] does not
   exist.` The quote is accurate and the root cause stands. The citation now shipped at Phase B
   step 5 carries the tool, the server version and the date, so the next reader is not re-verifying
   a fact laundered through a spec file (INV-080).

2. **The deletion and the write are one change, not two.** Phase A's copy was the **only** place
   in the module that set `test_load_status: complete`. Doing step 1 without step 2 would have
   left the field never written, so Phase A's own check would request the test load again on every
   resumed session — converting a mis-ordered instruction into a silent infinite re-request. The
   guard class `TheWriteSurvivedTheMove` exists for exactly this, and asserts the module now has
   **exactly one** writer of the field.

3. **A first version of one guard was wrong and would have failed on correct content.** It
   asserted the "10–100 records" test load appears in exactly one file module-wide; `phaseC` step
   18 tests the *orchestrator* across sources with the same record range, which is a different
   action on a different trigger. The assertion was narrowed to Phase A specifically, plus a
   separate check that only Phase B *acts* on the Phase-3-skipped condition. A uniqueness claim
   that conflates two actions is a guard that punishes correct work.

4. **No invariant minted — recorded as a stop-marker instead.** The candidate is: *a section gated
   "complete these before step N" MUST contain only actions executable before step N.* It is a
   real rule and this is **instance 1**. Following the threshold discipline this repo already
   applies to widening rules and to local markings, it is written down here rather than registered,
   so a later run finds the tally instead of re-deriving the argument. Register at instance 2 if
   the same shape appears in another module's preamble — or sooner if the maintainer judges an
   ordering rule worth stating up front. ⚠️ This is the one candidate in this session's unattended
   run where minting was available under standing authorization and was **not** used; the
   reasoning is recorded so the choice is reviewable rather than invisible.
