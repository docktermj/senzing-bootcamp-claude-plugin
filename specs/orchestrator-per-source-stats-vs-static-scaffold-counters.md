# Phase C's orchestrator requires per-source statistics from a scaffold whose counters are process-global

## Problem

`module-06-data-processing/phaseC-multi-source.md:104-124` (step 17, "Create orchestrator program")
tells the guide to build the orchestrator from
`generate_scaffold(language=…, workflow='add_records')` and requires it to handle, among other
things:

> per-source progress/error tracking with error isolation, statistics aggregation, and a
> completion summary

The loading program it orchestrates comes from the same tool family — `sdk_guide(topic='load')`
returns `senzing/code-snippets-v4` `java/snippets/loading/LoadViaFutures.java` for any
`record_count` above 500 (server 1.32.9, 2026-08-14). That snippet keeps its counters as
**process-global static state**:

```java
private static int errorCount = 0;
private static int successCount = 0;
private static int retryCount = 0;
```

So the obvious orchestrator — the one the step's own "the Module 6 loading program works as a
template" framing invites (`phaseC-multi-source.md:100`), reusing the Phase B loader in-process per
source — produces **cumulative** counters rather than per-source ones. Each source's completion
summary reports every record loaded so far.

Observed on this walk, three sources of 10 / 10 / 8 records:

```
MERIDIAN_CRM      Records attempted : 10   (correct)
AURORA_MARKETING  Records attempted : 20   (should be 10)
SUMMIT_BILLING    Records attempted : 28   (should be 8)
```

The load itself is correct — 28 records, 0 errors, and the datastore holds exactly what it should.
Only the *reporting* is wrong, which is what makes it dangerous: the numbers are plausible,
monotonic, and sum to the right total, so nothing looks broken. A bootcamper reading them concludes
Summit Billing has 28 records. The same arithmetic hides a real per-source failure — a source that
loaded 0 of 8 still shows a rising "successfully added" count inherited from its predecessors.

This is the failure shape the plugin already guards against elsewhere: a wrong field name that
"yields `None`, which renders as blank text … so nobody reports it"
(`ground-rules.md`, Response structures / INV-115). Here it yields a *number*, which is worse.

## Root cause

Step 17 specifies the orchestrator's required behaviour without saying anything about the state
model of the program it orchestrates. Both halves come from MCP scaffolds, and the loading scaffold
is written to be a standalone `main()` — process-global statics are correct for that shape and wrong
the moment it is called more than once in a process.

## Proposed change

Add one paragraph to `phaseC-multi-source.md` step 17, immediately after the per-source-tracking
requirement:

- Name the hazard: the loading scaffold's counters are process-global (`static` in Java, module-level
  in Python), so reusing it in-process per source accumulates them across sources.
- Give the two acceptable resolutions, language-agnostically (INV-002): either **reset or scope the
  counters per source** (make them instance state the orchestrator owns), or **run each source's load
  in its own process** so the statics start clean.
- Require the orchestrator to **verify its own per-source numbers before reporting them** — the
  per-source totals must sum to the aggregate, and each must match that source's input record count.
  A summary that cannot be reconciled against the input files is not a summary.

## Acceptance criteria

- `phaseC-multi-source.md` step 17 names the process-global-counter hazard and both resolutions.
- It requires the per-source figures to be reconciled against per-source input counts before they
  are shown.
- A test asserts step 17's text mentions per-source counter scoping (or an equivalent term) so the
  guidance cannot be dropped silently.

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md`
- `tests/test_module06_orchestrator_guidance.py` (new)

## Source

`/dry-run` phase 3, 2026-08-14. Reproduced on the walk's own orchestrator, built as step 17
describes from the MCP-supplied `LoadViaFutures.java`. Senzing MCP server 1.32.9, docs indexed
2026-08-11 20:52 UTC; Java binding, SDK 4.3.4.

## Invariants introduced

- `INV-243` — A **per-source figure reported to the Bootcamper** MUST be reconciled against that
  source's own input count before it is shown; an unreconciled or mismatching figure MUST NOT be
  printed as a result (recorded in `specs/INVARIANTS.md`, indexed under *Data quality, mapping and
  validation gates*; enforced by `tests/test_module06_orchestrator_guidance.py`). It **generalises
  INV-228**, which requires the same per-source count check and stop-on-mismatch for a dataset
  *written* from the MCP server; a dated forward pointer was added to INV-228 accordingly.
  ✅ **Approved by the maintainer on 2026-08-14**, on review of the wording as registered. Originally minted under the standing authorization given before that unattended run.

## Deviations from this spec, and why (2026-08-14)

Implemented as proposed; all three criteria hold. Both Senzing facts re-verified and both
**confirmed**, plus one the spec did not have.

1. **Both facts confirmed verbatim.** `sdk_guide(topic='load', language='java',
   record_count=1000)` on server 1.32.9 (2026-08-14) returns `senzing/code-snippets-v4`
   `java/snippets/loading/LoadViaFutures.java`, and that snippet does declare
   `private static int errorCount = 0; private static int successCount = 0; private static int
   retryCount = 0;`. The spec's diagnosis is exactly right.

2. **The retry file is static too, which the spec did not note.** The same declaration block ends
   `private static File retryFile = null; private static PrintWriter retryWriter = null;`, and the
   handler only creates the file when `retryFile == null`. So under in-process reuse the retry
   records of every source accumulate into the **first** source's temp file — the same defect in a
   second place, and one that survives fixing only the three integer counters. The shipped text
   says "and a `static` retry file besides" so a guide scoping counters does not stop at the
   integers.

3. **A resolution the spec listed was strengthened, not changed.** Running each source in its own
   process is presented as also satisfying the error-isolation requirement step 17 already states,
   so the two options differ in what else they buy rather than reading as arbitrary alternatives.

4. **The reconciliation requirement carries its own justification**, because it is the half that
   catches the defect at runtime and the half most likely to be trimmed as verbose: every check
   that looks only at the aggregate **passes**, since the accumulating counters sum to the correct
   total. A test asserts that sentence is present for exactly that reason.

## INV-243 split on review (2026-08-14)

On maintainer review, INV-243 was found to state **two** conditions where the file's convention is
one — *reconcile the per-source figure before showing it*, and *do not print an unreconciled or
mismatching figure*. The second was extracted to **INV-245**:

> A value that failed its own verification check MUST NOT be presented to the Bootcamper as a
> result; the discrepancy is reported in its place.

The two are genuinely different subjects: INV-243 governs whether the check happens, INV-245
governs what happens after it disagrees. A step can reconcile diligently and still print the number
it just disproved — the worst of both, since the artifact then carries a figure the run itself knows
to be wrong while looking verified.

**INV-243's text was not cut down.** `INVARIANTS.md` rule 1 forbids deleting an invariant's text and
rule 2 permits editing only for meaning-preserving wording, so the clause stays in place under a
dated forward pointer naming INV-245 as canonical for it — the same shape as the INV-234 → INV-240
split. INV-245 is indexed beside INV-243 under *Data quality, mapping and validation gates*, cited
at the stop-on-mismatch rule in `phaseC-multi-source.md` step 17, and shares INV-243's enforcer
(`tests/test_module06_orchestrator_guidance.py`), which already asserted both halves — the "one test
named by several invariants" case the pinned pair count exists for. Pair count re-derived 56 → 57.

INV-245 is deliberately broader than the per-source-count case that produced it: it is the
positive-value counterpart of the ground rules' *"Never present a blank value as a real result"*
under INV-115 — that governs a value that never arrived, this one governs a value that arrived and
failed its check.
