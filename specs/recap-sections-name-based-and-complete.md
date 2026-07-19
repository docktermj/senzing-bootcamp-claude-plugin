# Recap sections: drop the module number, follow experienced order, and cover every completed module

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

In `docs/bootcamp_recap.md` (and the rendered `docs/bootcamp_recap.pdf`), each section
header carries the catalog module number — "## Module 1: Business problem". Since the
bootcamp lets a bootcamper pick and choose which modules to run (Customized path), a fixed
catalog number no longer reflects what was actually experienced. Separately, in the
reported session `truthset_visualization` was in `modules_completed` but had **no**
corresponding section in the recap at all — so the graduation PDF did not fully represent
everything the bootcamper did. The bootcamper asked to:

1. drop the module number from recap/PDF section headers (e.g. "## Business problem");
2. order sections by the order modules were actually experienced, not by catalog number;
3. ensure every module in `modules_completed` gets a section (add the missing
   `truthset_visualization` section before rendering the PDF).

## Root cause

The recap section is templated as a numbered header, and the PDF renderer parses that
number:

- **Template:** `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:57`
  — "## Module N: {Name} — {ISO 8601 timestamp}" (guidance `:51-52`, verify `:89-96`).
- **Graduation reconciliation:** `plugins/senzing-bootcamp/skills/graduation/SKILL.md:83-89`
  confirms a `## Module N:` section per module in `modules_completed`, appending any
  missing one.
- **PDF renderer** expects the number:
  `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py:136`
  (`module_re = re.compile(r"^##\s+Module\s+(\d+)\s*[:\-—]?\s*(.*)$", …)`), and
  `:164-165`, `:222`, `:226` build labels from that captured number. A numberless header
  would currently fail to parse as a module section.
- **Ordering:** sections are appended in module-completion order (which *is* experienced
  order) by `module-completion.md` Step 2b, so ordering is largely already correct — the
  problem is the numeric label *implies* a fixed catalog sequence that can contradict the
  experienced order.
- **Missing section:** `system_verification` and `truthset_visualization` are separate
  `modules_completed` entries but share the `module-03-system-verification` skill, which
  runs `module-completion` once — so only one `## Module N:` section is appended, leaving
  `truthset_visualization` without one. Graduation Step 1a's reconciliation keys on
  `## Module N:` headings and did not (in the reported run) synthesize the missing section.

## Conflict with invariants (reconcile, don't silently override)

- **INV-079** established name-based module referencing for banners/transitions/completion
  lines but **explicitly scoped the recap `## Module N:` headings out** ("recap-heading
  `## Module N:` templates that index the recap file are out of scope"; "Internal
  references … recap `## Module N:` headings … may still use numbers"). This spec extends
  name-based referencing *into* the recap headers — a deliberate change to INV-079's
  scope. The implementing session must amend/extend INV-079 (or record a new invariant)
  so the recap header is name-based, and reconcile the "internal references may still use
  numbers" clause.

## Proposed change

1. **Numberless recap headers.** Change the section template
   (`module-completion.md:57`) to "## {Name} — {ISO 8601 timestamp}" (no "Module N:").
   Update the verify/reconcile references (`module-completion.md:89-96`,
   `graduation/SKILL.md:83-109`) to key on the module **name** rather than "Module N:".
2. **PDF renderer.** Update `generate_recap_pdf.py` to parse numberless headers — match
   `^##\s+(.*?)\s*[—-]\s*…` for the section title (still tolerating legacy
   "Module N: Title" headers for older recaps), and build labels from the title, not the
   number (`:136`, `:164-165`, `:222`, `:226`). `--check` must still validate the four
   subsections per section.
3. **Experienced order.** Confirm sections render in `modules_completed` / append order
   (experienced order); do not sort by catalog number. (Largely already true — the fix is
   removing the number so nothing implies catalog order.)
4. **Cover every completed module.** Make graduation Step 1a reconcile against the full
   `modules_completed` list by module **name**, synthesizing a section for any completed
   module without one — including `truthset_visualization` when its skill shares a
   directory with `system_verification`. Ensure a module that ran (e.g.
   `truthset_visualization`) gets its own recap section.

## Acceptance criteria

- [ ] Recap section headers use the module name with no catalog number ("## Business problem …"), in both `docs/bootcamp_recap.md` and the rendered PDF.
- [ ] Sections appear in the order the bootcamper experienced the modules (append/`modules_completed` order), never re-sorted by catalog number.
- [ ] Every module in `modules_completed` has a recap section before the PDF renders — including `truthset_visualization`; graduation Step 1a synthesizes any missing one by name.
- [ ] `generate_recap_pdf.py` parses numberless headers (and still tolerates legacy numbered ones), and `--check` still enforces the four labeled subsections.
- [ ] INV-079 is reconciled (recap headers are name-based; the "recap headings may still use numbers" clause is amended).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — recap section template + verify (`:56-76`, `:89-96`).
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — reconciliation keyed on name, cover every `modules_completed` entry (`:81-110`).
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — numberless header parsing and labels (`:136`, `:164-165`, `:222`, `:226`), legacy tolerance, `--check`.
- `specs/INVARIANTS.md` — amend/extend INV-079 for name-based recap headers.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Recap sections shouldn't use module numbers, should follow experienced order, and must cover every completed module" (2026-07-19, Module: graduation).
- Priority: Medium.
- Related specs: `module-references-by-name-not-number.md` (INV-079 — this extends its scope into recap headers), `recap-durability.md` (INV-059 recap reconciliation), `defer-commonmark-to-graduation.md` / `recap-pdf-professional-design.md` (recap normalization/rendering), `module3-synthetic-verification-data.md` (the `system_verification` / `truthset_visualization` split that surfaced the missing section).

## Invariants introduced

- `INV-085` — Recap section headers are name-based (`## {Module name} — {timestamp}`, no catalog number), in experienced order, with a section for every `modules_completed` entry by graduation; the PDF renderer parses name-based headers and tolerates legacy numbered ones. Amends the recap-heading clause of INV-079 (recorded in `specs/INVARIANTS.md`).
