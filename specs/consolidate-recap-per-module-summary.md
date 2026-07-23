# Persist the end-of-module summary into the recap and reconcile it with the redundant Journal

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Two linked issues about the per-module content of `docs/bootcamp_recap.md` and the rendered
`docs/bootcamp_recap.pdf`:

1. **The end-of-module epilog is not preserved.** Each module closes with a bootcamper-facing
   summary — "What you accomplished", "Files produced", "Why it matters", "What's next" — shown in
   chat but never written into the recap. The bootcamper saw it during the bootcamp and wants it in
   the permanent keepsake, not displayed transiently.
2. **Adding it duplicates the Journal.** The recap already carries a per-module **Journal**
   subsection (What we did / What was produced / Why it matters / Bootcamper's takeaway). Once the
   end-of-module summary is added, the two subsections convey essentially the same What/Produced/Why
   content, making the recap longer and repetitive. The bootcamper's stated preference is to keep
   the end-of-module summary and drop Journal (merging its one unique field, "Bootcamper's
   takeaway", into the summary).

## Root cause

The two blocks are authored separately and only one is persisted:

- **Recap subsections (Step 2b)** — `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:50-91`.
  The four subsections are Information Shared, Questions & Responses, Actions Taken, Journal. The
  **Journal** template (`:70-74`): "What we did / What was produced / Why it matters / Bootcamper's
  takeaway" (the takeaway line is omitted when empty per `omit-empty-recap-takeaway`).
- **End-of-module summary (Step 3)** — `module-completion.md:147-174` (template `:160-174`): "What
  you accomplished / Files produced / Why it matters / What's next". This is presented to the
  bootcamper but **not** written into the recap.

The Step 2b Journal and the Step 3 summary are near-duplicates (same accomplishment/artifacts/
rationale captured twice per module) — the redundancy the feedback flags.

The recap PDF generator is hard-coupled to exactly the four subsection names, including "Journal":

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py:53-58` — `REQUIRED_SECTIONS` lists the
  four names.
- `:282-286` — `_SECTION_ACCENT` hardcodes per-subsection colors (includes `"journal": NAVY`).
- `:683-691` — `_render_module` renders the four required subsections first, in fixed order, then
  extras; `:695-715` — `_render_subsection` fills a missing required subsection with "(not
  recorded)". Stdlib fallback mirrors this at `:903-909`.
- `:226-248` — `verify_recap` (`--check`) uses `missing_required()` (`:83-89`) against the same
  `REQUIRED_SECTIONS`, flagging any module section missing Journal.

## Conflict with invariants (reconcile, don't silently override)

- **Item 1 (add the summary to the recap) is additive** and does not conflict — it engages INV-032
  (the summary content) and INV-085 (name-based sections) but adds no violation.
- **Item 2 (drop/replace Journal) directly conflicts** with three invariants that name Journal as a
  required subsection: **INV-048** ("contains Information Shared, Questions & Responses, Actions
  Taken, and Journal"), **INV-085** (the four subsections per section), and **INV-092** (Module 0's
  section carries the same four). Removing or renaming Journal requires amending all three **and**
  updating `generate_recap_pdf.py` (`REQUIRED_SECTIONS`, the accent map, both renderers, and
  `--check`) — not just the Markdown. The implementing session must amend the invariants and record
  the change in `INVARIANTS.md` before dropping Journal.

## Proposed change

Consolidate to a single per-module summary that both persists the epilog and removes the
redundancy. Recommended approach (matches the bootcamper's stated preference):

1. **Persist the end-of-module summary into the recap.** In `module-completion.md`, have Step 2b
   write an "End-of-Module Summary" subsection carrying Step 3's content (What you accomplished /
   Files produced / Why it matters; "What's next" is transient chat and may be omitted from the
   recap or kept).
2. **Replace Journal with it.** Drop the Journal subsection and fold its one unique field —
   "Bootcamper's takeaway" — into the End-of-Module Summary (preserving the empty-takeaway omission
   from `omit-empty-recap-takeaway`). Update the recap subsection set from
   {Information Shared, Questions & Responses, Actions Taken, Journal} to
   {Information Shared, Questions & Responses, Actions Taken, End-of-Module Summary}.
3. **Update the renderer** (`generate_recap_pdf.py`): rename the fourth entry in `REQUIRED_SECTIONS`
   (`:53-58`), the accent map (`:282-286`), both renderers (`:683-691`, `:903-909`), and `--check`
   (`:226-248`/`:83-89`) — tolerating legacy recaps that still carry a "Journal" heading so old PDFs
   render.
4. **Amend the invariants**: INV-048, INV-085, INV-092 to name the consolidated subsection instead
   of Journal; record the amendment in `INVARIANTS.md`.

If the maintainer prefers not to amend invariants, the fallback is item 1 only (add the summary,
keep Journal) — but that leaves the redundancy the bootcamper flagged, so surface the choice
explicitly.

## Acceptance criteria

- [ ] Each module's recap section persists the end-of-module summary content (What you accomplished / Files produced / Why it matters) that was previously only shown in chat.
- [ ] The recap no longer carries two overlapping What/Produced/Why subsections per module; if Journal is dropped, "Bootcamper's takeaway" is preserved (merged in, still omitted when empty).
- [ ] `generate_recap_pdf.py` renders the consolidated subsection, still tolerates legacy "Journal" headings, and `--check` validates the new required-subsection set.
- [ ] INV-048, INV-085, and INV-092 are amended to name the consolidated subsection (recorded in `INVARIANTS.md`) — or, if the additive-only fallback is chosen, that choice and its residual redundancy are stated explicitly.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — persist Step 3's summary into the Step 2b recap subsections (`:50-91`, `:147-174`); drop/replace Journal (`:70-74`).
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — rename the required subsection in `REQUIRED_SECTIONS` (`:53-58`), `_SECTION_ACCENT` (`:282-286`), both renderers (`:683-691`, `:903-909`), and `--check` (`:83-89`, `:226-248`); tolerate legacy "Journal".
- `specs/INVARIANTS.md` — amend INV-048/INV-085/INV-092 for the consolidated subsection (only if Journal is dropped).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Recap should include each module's end-of-module epilog sections" and "Journal subsection is redundant once the End-of-Module Summary is added" (both 2026-07-23, Module: Graduation / recap generation)
- Priority: Medium
- Related specs: `omit-empty-recap-takeaway.md` (implemented — the "Bootcamper's takeaway" omit-when-empty behavior that must follow the takeaway to its new home), `recap-sections-name-based-and-complete.md` (INV-085 — name-based sections and the `--check` subsection validation), `capture-entity-resolution-concepts-in-recap.md` (INV-092 — Module 0's four subsections), `recap-pdf-professional-design.md`/`reconcile-action-taken-wording.md` (renderer and subsection wording).

## Invariants introduced

- `INV-103` — Per-module recap sections carry Information Shared / Questions & Responses / Actions Taken / **End-of-Module Summary** (What you accomplished / Files produced / Why it matters, plus an optional "Bootcamper's takeaway" omitted when empty), the End-of-Module Summary replacing the former Journal subsection; `generate_recap_pdf.py` renders and `--check`-validates it and tolerates legacy "Journal" as an alias. Supersedes the "Journal" subsection-naming clause of INV-048/INV-085/INV-092 (recorded in `specs/INVARIANTS.md`, maintainer-approved).
