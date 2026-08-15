# The absent-licence branch INV-244 forbids exists in Module 4 as well, upstream of both fixed sites

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`license-limit-assumed-when-it-could-be-measured` was implemented on 2026-08-14 (`6eda9e0`),
correcting the absent/null branch of the `license_record_limit` reconciliation in Module 6 Phase A
and Phase B, and registering **INV-244** — *where a bootcamp state field is written only
conditionally, a step branching on it MUST NOT read that field's absence as a measured finding.*

That spec's closing section is titled **"The same branch exists twice."** It exists **three** times.
The third is `module-04-data-collection/SKILL.md:87-96`, which was never touched:

> - **Absent or null** (no custom license detected yet): fall back to the **built-in evaluation
>   license** the bootcamper already has by default, whose capacity is confirmed via the Senzing
>   MCP server at request time (never a hardcoded or remembered figure).

"no custom license detected yet" is precisely the inference INV-244 forbids. The field's only
writer is that same module's Step 8a gate, which is **volume-gated by design** — so on a small
dataset it never fires, and absence reports nothing about the installed licence.

**This is the worst of the three placements, not the least.** The two that were fixed sit in
Module 6, after loading has begun. This one governs the paragraph that opens *"Before any
license-based capacity or sampling decision"* — it is where the sampling decision is actually
made, in the module that collects the data. A bootcamper whose licence has no cap can be steered
to a smaller dataset here, before Modules 6 and 7 ever run, which is the same harm INV-244 records
and one module earlier.

## Root cause

Two compounding causes, and the second is the more useful one.

1. **The site was never swept.** `module-04-data-collection/SKILL.md:94` reads
   `license_record_limit` and branches on its absence, exactly as the two Module 6 sites did.
2. **The implementation trusted the spec's enumeration instead of checking it.** The spec said the
   branch exists twice and named the two files; the implementer honoured that count and swept no
   further. This is the `production-readiness-audit` skill's defect class 1 — *a rule applied to
   some of the sites it binds* — reached through a **stale enumeration inside a spec** rather than
   inside an invariant (class 4). A spec's site list is a claim like any other and is not evidence.

⚠️ Module 4's text is **less** wrong than the two that were fixed: it does not hardcode 500, and it
routes the fallback capacity through the MCP server at request time. That is why it reads as
acceptable on a skim, and it is still an INV-244 breach — it concludes *"no custom license
detected"* from silence and falls back, where the value is one `SzProduct.getLicense()` call away
and Step 8a's own procedure for measuring it lives in the same file.

## Proposed change

1. In `module-04-data-collection/SKILL.md`, change the **Absent or null** branch from *fall back to
   the evaluation licence* to *measure, then re-enter the three branches* — the same shape now used
   in Phase A, and citing **INV-244**. Step 8a's procedure is in this same file, so the branch
   routes to it rather than restating it.
2. Persist the measured value to `license_record_limit`, so Modules 6 A and B find a detected value
   and their own absent branches are not reached at all.
3. Keep the evaluation-licence fallback for the case where the measurement **fails**, stated as an
   assumption, preserving the existing "confirmed via the MCP server at request time, never a
   hardcoded figure" requirement, which is correct and must survive.
4. Extend `tests/test_module06_license_reconciliation.py` (or add a sibling) to sweep **every** file
   that branches on `license_record_limit`, so a fourth site cannot appear unguarded. Derive the
   file list by scanning for the branch, not by listing paths — a hardcoded list reproduces the
   defect this spec exists for.

## Acceptance criteria

- [ ] `module-04-data-collection/SKILL.md`'s absent/null branch instructs measuring before falling
      back, names `SzProduct.get_license()` / `recordLimit` via Step 8a's procedure, and cites INV-244.
- [ ] The measured value is persisted to `license_record_limit`.
- [ ] The evaluation-licence fallback survives only as the measurement-failure path, is stated as an
      assumption, and keeps its "confirmed via the MCP server at request time" requirement.
- [ ] A test asserts that **no** file branching on `license_record_limit` reads absence as a
      finding, with the file set **derived** rather than hardcoded, and it fails if the Module 4
      branch is reverted.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — the absent/null branch at
  `:94`, and the surrounding capacity-decision preamble at `:87-96`.
- `tests/test_module06_license_reconciliation.py` — widen the sweep from a named pair to a derived set.

## Source

- Feedback: `production-readiness-audit-2026-08-14b` (self-observed; found by the forward invariant
  sweep, Step 2 — "what is the full set of sites it binds?")
- Priority: High
- MCP re-check: **n/a (no Senzing fact re-asked for this finding).** It is internal consistency
  between INV-244 and the plugin's own files. The Senzing facts the fix will need —
  `SzProduct.getLicense()`'s signature and the `recordLimit` field — were re-verified on server
  **1.32.9, 2026-08-14** during the original implementation and must be re-asked at implementation
  time per INV-080 rather than carried from here.
- Upstream: not applicable
- Related specs: `specs/license-limit-assumed-when-it-could-be-measured.md` (the implementation this
  completes; its "The same branch exists twice" section is the stale enumeration)
