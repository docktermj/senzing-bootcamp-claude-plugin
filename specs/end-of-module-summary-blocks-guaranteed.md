# Guarantee the End-of-Module Summary's three labeled blocks reach the recap PDF

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Reported from a bootcamp run: `docs/bootcamp_recap.pdf` rendered its per-module
**End-of-Module Summary** without **What you accomplished**, **Files produced**, or
**Why it matters**. The subsection heading was there; the three blocks it exists to carry
were not.

INV-103 has required exactly those blocks since 2026-07-23, and says in the same sentence
that `generate_recap_pdf.py` "MUST render it and its `--check` MUST validate it". Nothing
validated anything below the heading, so the failure was invisible at every layer that
looks for it:

- `--check` reported `Recap complete: all module sections carry the required subsections.`
- The render printed `PDF generated:` with ~100% content retention — truthfully, because
  the prose that *was* written did reach the page.
- The page looked finished: a heading with a paragraph under it.

A keepsake that silently omits required content is the failure nobody notices, and this one
is permanent — the bootcamper's copy is the only copy.

## Root cause

Three layers each assumed another was checking:

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `ModuleSection.missing_required`
  compares H3 *headings* against `REQUIRED_SECTIONS`; nothing inspects a subsection's body.
  `verify_recap` (the `--check` contract) therefore cannot see a summary with no labels, and
  `_render_subsection` renders the lines it is given, so an absent block simply is not drawn.
  `_block_label` exists but only switches list spacing on, and only for a strictly canonical
  `**Label:**` line.
- `skills/bootcamp-onboarding/module-completion.md` — shows the three labels in its recap
  template and calls them "the same content" as the Step 3 epilog, but states no requirement
  that they be written *as labeled blocks*, and its Step 2c verify re-reads the recap only to
  confirm the `## {Name}` heading landed.
- `skills/graduation/SKILL.md` — Step 1a reconciles missing *sections*, screenshots, the
  completion date and the environment block, and has no notion of a section that is present
  but hollow.

## Proposed change

Close it at all three layers, since any one alone still leaves a hole:

- **Detect.** `--check` and the pre-render audit report, per module, which of the three blocks
  a present End-of-Module Summary does not carry — INV-103's own unenforced clause. Stays
  non-blocking at render time (warn, render, exit 0) per INV-110/INV-048.
- **Render.** Both renderers (INV-066) draw every required block: recorded content where the
  recap has it, `(not recorded)` where it does not. The generator cannot invent
  accomplishments, but it must refuse to let an absence look like completeness.
- **Tolerate.** Detection accepts the forms a live recap actually produces —
  `**Files produced**:`, `- **Files produced:**`, a bare `Files produced:` — because a false
  "missing" sends graduation off to backfill content that is already there, or to rewrite a
  finished section (INV-085). Legacy `### Journal` sections stay exempt, as INV-103 tolerates.
- **Author.** `module-completion.md` requires the three labels explicitly and verifies them in
  the Step 2c read it already performs — the cheapest place to catch it, while the module's own
  work is still in context.
- **Backfill.** Graduation Step 1a repairs a gap before rendering, from the module's own
  recorded content (Actions Taken, the paths it names, the module's purpose) and never by
  inventing.

## Acceptance criteria

- [ ] A summary written as prose with none of the three labels fails `--check` naming each missing block, and warns (never fails) at render time while still producing the PDF.
- [ ] A summary missing exactly one block names that one and not the others.
- [ ] Every required block appears in the rendered PDF — with its content when recorded, `(not recorded)` when not — in both the fpdf2 renderer and the stdlib fallback (INV-066), verified from the rendered page.
- [ ] A block that is present but written as `**Label**:`, `- **Label:**` or `Label:` is never reported missing.
- [ ] A legacy `### Journal` section still passes `--check` and is not annotated (INV-103).
- [ ] A wholly missing End-of-Module Summary is reported once, as a missing subsection, not twice.
- [ ] `module-completion.md` requires the labeled blocks and verifies them at Step 2c; graduation Step 1a backfills them before rendering and never invents content to fill a label.
- [ ] The shipped example recap (INV-065) carries all three in every module and passes clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `END_SUMMARY_BLOCKS`, `ModuleSection.missing_summary_blocks`, `_summary_block_label`, `_is_legacy_journal`, `verify_recap`, `_render_subsection`, `_stdlib_subsection`.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — require the labeled blocks; verify them in Step 2c.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1a backfill; `--check` description.
- `tests/test_recap_summary_blocks.py` — new.
- `tests/test_recap_pdf_guard.py` — its `GOOD_RECAP` fixture was itself an example of the defect.
- `specs/INVARIANTS.md` — the render-every-block guarantee.

## Source

- Maintainer report (2026-07-28): "during a bootcamp, the `bootcamp_recap.pdf`'s 'End-of-module Summary' did not contain: 'What you accomplished', 'Files produced', nor 'Why it matters'. Guarantee that these sections show up in `bootcamp_recap.pdf`."
- Priority: High — a silent content loss in the terminal deliverable.
- Related specs: `consolidate-recap-per-module-summary.md` (established INV-103), `recap-pdf-generator-fail-loudly-on-content-loss.md`, `artifact-level-verification-for-deliverables.md`; INV-103, INV-032, INV-048, INV-066, INV-085, INV-110

## Invariants introduced

- `INV-157` — Every block INV-103 requires inside the End-of-Module Summary is validated by `--check`, reported by the pre-render audit, and *rendered* by both renderers — as `(not recorded)` when the recap does not carry it — so an absent block can never be mistaken for a complete page (recorded in `specs/INVARIANTS.md`).
