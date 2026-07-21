# Capture the Entity Resolution Concepts module (Module 0) in the recap

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The bootcamp recap must capture all nine modules the Bootcamper experiences, including the
**Entity Resolution Concepts** primer (Module 0). Today Module 0 is excluded from the recap by
design, and the Module 1 section is labeled with the short "Business problem" rather than the
module's full name.

## Root cause (confirmed)

- **Module 0 excluded:** `INV-072`/`INV-078` make Module 0 apparatus-exempt with, verbatim, "no
  `docs/bootcamp_recap.md` section … not added to `modules_completed`"
  (`skills/module-00-entity-resolution-concepts/SKILL.md:26-29`; `ground-rules.md:209-215`). The
  shipped example recap folded the ER-concepts content into the "Business problem" section instead
  of giving it its own section (`docs/examples/bootcamp_recap.example.md`).
- **Module 1 label:** the example recap named the section `## Business problem`, while the
  onboarding overview (the `INV-085` name source) and the maintainer's list use the full name
  **Discover the Business Problem** (`skills/bootcamp-onboarding/onboarding-flow.md:100`).

## Proposed change

Maintainer decision (2026-07-21): make Module 0 recap-captured, and use the full Module 1 name.

1. **Amend the Module-0 exemption** so that, when Module 0 runs, it adds
   `entity_resolution_concepts` to `modules_completed` and appends its own name-based recap section
   (`## Entity Resolution Concepts — {timestamp}`, four subsections) at its close — reconciled at
   graduation (`INV-085`) — while remaining exempt from the rest of the module-start apparatus (no
   journey map / before-after / step overview / bootcamper-facing end-of-module summary). Bootcamp
   preparation stays fully exempt.
2. **Update the module-00 skill** (`SKILL.md`) with a quiet recap-capture step at its close, and
   reconcile `ground-rules.md` (journey-map ✅ note and the lightweight-modules note).
3. **Update the shipped example recap** (`bootcamp_recap.example.md`): add the Entity Resolution
   Concepts section (moving the ER-concepts content out of the Business problem section), rename
   `## Business problem` → `## Discover the Business Problem`, and **regenerate the example PDF**
   (`INV-065`).

## Acceptance criteria

- [ ] When Module 0 runs, `entity_resolution_concepts` is added to `modules_completed` and a name-based `## Entity Resolution Concepts — {timestamp}` section (four subsections) is appended to `docs/bootcamp_recap.md` at its close; graduation reconcile guarantees it (INV-085).
- [ ] Module 0 stays lightweight — no journey map, before/after, step overview, or bootcamper-facing end-of-module summary; only the recap capture is added.
- [ ] The example recap (`bootcamp_recap.example.md`) contains all nine module sections in experienced order — Entity Resolution Concepts first, then Discover the Business Problem — and the regenerated `bootcamp_recap.example.pdf` renders them; `generate_recap_pdf.py --check` passes and no real PII is present (INV-065).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md` — exemption reworded; recap-capture step added at close.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — journey-map ✅ note and lightweight-modules note reconciled.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` + `.pdf` — ERC section added, Module 1 renamed, PDF regenerated.
- `specs/INVARIANTS.md` — INV-092 added; INV-078 marked amended.

## Source

- Maintainer request (2026-07-21): ensure the nine listed modules — Entity Resolution Concepts, Discover the Business Problem, SDK setup, System verification, Truth Set visualization, Data collection, Data quality & mapping, Data processing, Query, Visualize and Discover — are captured in `bootcamp_recap.md` and the PDF.
- Priority: Medium
- Related specs: `entity-resolution-module-zero.md` (INV-072/073 Module 0), `customizable-module-selection.md` (INV-078), `recap-sections-name-based-and-complete.md` (INV-085), `record-truthset-visualization-completion.md` / `truthset-visualization-full-apparatus.md` (INV-086 first-class-module precedent).

## Invariants introduced

- `INV-092` — When Module 0 runs it MUST add `entity_resolution_concepts` to `modules_completed` and append its own name-based recap section at close (captured in the recap, reconciled at graduation), while staying exempt from the rest of the module-start apparatus; amends INV-072/INV-078 (recorded in `specs/INVARIANTS.md`).
