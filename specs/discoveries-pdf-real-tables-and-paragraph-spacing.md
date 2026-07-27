# Render the discoveries PDF's Markdown tables as a real grid, space its paragraphs, and land the working-tree fix

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Three defects in the two bundled PDF generators, all reported by the bootcamper at graduation, all
already **fixed in the working tree but uncommitted**. This spec is the record of what they are, why
they matter, and what still has to happen before the change is trustworthy.

**(a) Markdown tables printed as raw pipe source.** `docs/bootcamp_data_discoveries.md` uses tables
for its most information-dense content: the headline numbers, the match-key frequency list, the
review-queue denial counts, the worked example's feature scores, the relationship-network cluster,
and the source-pair overlap comparison. Every one of them appeared in the rendered PDF as literal
Markdown:

```text
| Measure | Value |
|---|---|
| Records loaded | 4,966 |
```

**61 raw pipe lines** in the extracted text. The discoveries document is one of two keepsake
deliverables and is explicitly meant to be shareable, so the least readable part of the PDF was the
part carrying the most information — and raw pipe syntax reads as unfinished, making a generated
deliverable look like a draft.

**(b) No blank line between paragraphs, or around lists.** Consecutive paragraphs ran together, so a
section read as one wall of text. List items were separated by only 2.4 mm, and only when the *next*
block was also a list item — nothing between a paragraph and an adjacent list, nothing after a list's
final item. Paragraph breaks are structure, not decoration: this document alternates claim, evidence,
caveat, and running those together changes how the text reads.

**(c) `↔` and `⚠️` rendered as `?` in both PDFs.** Pre-existing and unreported, found while verifying
(a). The source-pair table read `GLEIF ? OPEN-OWNERSHIP` and every `⚠️` caveat began `??`.

Every one of these shipped under a green signal: the generator printed `PDF generated:` with 100%
content retention and exited 0. Retention cannot see this class of defect — the text *is* in the
content stream, just formatted as garbage. The same blindness produced two regressions during the fix
itself (below), both caught only by rasterizing pages.

## Root cause

**(a) Tables were verbatim text by design.** In
`plugins/senzing-bootcamp/scripts/generate_discoveries_pdf.py`, `parse_discoveries` emitted one
`Block("table", …)` per **row**, and both `_render_block_fpdf2` and the stdlib renderer printed each
row's source line in a monospace font. The module docstring said so outright: tables are "table rows
(rendered as their source text)". Not an oversight —
`specs/discoveries-pdf-offpage-blocks-and-list-spacing.md` names it explicitly under **"Known
limitation, deliberately not changed"**, deferring real tables as "a genuine enhancement but a larger
change than a layout fix". This spec is that deferred enhancement, now that a bootcamper has hit it.

**(b) The only inter-block gap was gated on both neighbours being list items.** `_needs_item_gap()`
returned true only when the current *and* next block were `bullet`/`subbullet`, with
`ITEM_GAP_MM = 2.4` / `ITEM_GAP_PT = 3.0`. `text` blocks received no trailing space at all. That
helper came from the same prior spec, which asked only for "a blank line between the elements of
every bulleted list" — so it was built to the letter of that request and never generalised to
paragraphs.

**(c) `_UNICODE_MAP` in `generate_recap_pdf.py` (`:594-600`) had no entry for `↔`, `⚠`, or the emoji
variation selector**, so `_safe()` reduced them to `?`. `generate_discoveries_pdf.py` imports these
helpers from its sibling, so one missing entry degrades **both** deliverables. Confirmed pre-existing:
a PDF rendered before any of this work contains zero `<->` and zero `↔`.

The test suite could not have caught (c): `tests/test_recap_pdf_font_safety.py:112` asserts `_safe`
reduces the non-ASCII characters **the plugin's own recap templates use**. `↔` and `⚠️` come from
bootcamper-authored discoveries content, which no test's character inventory covers.

## Proposed change

The work below is already applied to the working tree (branch `1-docktermj-9`, 2 files, +200/-17,
uncommitted — `git diff` shows all of it and `git checkout` discards it). Review and land it, then
close the gaps it left.

**1. Tables as a real grid** (`generate_discoveries_pdf.py`)

- `parse_discoveries`: consecutive `|…|` rows accumulate into **one** `Block("table", …)` instead of
  one per row. A `prev_was_table` flag resets at the top of each iteration and is re-armed only by
  the table branch, so a blank line correctly separates two adjacent tables.
- New `parse_table(text) -> (header, rows)`: splits into cells, drops the `|---|---|` alignment row,
  and pads or truncates ragged rows to the header's column count so a malformed row cannot
  desynchronise the grid.
- New `_render_table_fpdf2()`: bordered grid, shaded header, wrapped multi-line cells, column widths
  proportional to the longest cell per column (floor 6, cap 60 characters), header repeated when a
  table splits across a page.
- stdlib fallback: space-padded monospace columns with a rule under the header — not raw pipes — so
  the two renderers do not drift (INV-066).
- New `TABLE_HEAD_FILL` derived from `WARM_LINE`, keeping the grid inside the brand palette (INV-081).
- Module docstring corrected; it advertised the behaviour being removed.

**2. Paragraph and list spacing** (`generate_discoveries_pdf.py`)

- `_needs_item_gap()` generalised from "both neighbours are list items" to a block-boundary rule
  covering prose→prose, prose→list, list→list, and around code and table blocks. Headings are
  excluded — they already bring their own leading space.
- `ITEM_GAP_MM` 2.4 → 3.6, `ITEM_GAP_PT` 3.0 → 5.0, so the gap reads as a paragraph break rather than
  padding.
- `label` blocks take **no** trailing gap. A soft-wrapped `**Label:** text …` paragraph parses as a
  `label` block plus a continuation `text` block, and gapping uniformly inserted a blank line
  mid-sentence. Targeted fix; see remaining issue 1.

**3. Unicode map** (`generate_recap_pdf.py`, affects both PDFs)

- Add `↔` → `<->`, `⚠` → `!`, and U+FE0F (variation selector-16) → `""` to `_UNICODE_MAP`.

**4. Close the test gaps the change exposes**

- Assert the rendered discoveries PDF contains **zero** raw pipe lines and that a fixture table's
  header and cells extract as separate content — the positive-presence check that would have caught
  (a).
- Assert a paragraph boundary produces vertical separation, and that a `**Label:**` continuation does
  **not**.
- Extend the font-safety character inventory beyond the plugin's own templates to the characters
  bootcamper-authored deliverables realistically carry, so a `?` substitution fails a test rather
  than shipping.
- Add a regression test for the bold-header-after-page-break case (below).

**5. Regressions found during the work — both fixed, both must stay fixed.** Recorded because each
was invisible to every success signal; each render printed `PDF generated:` with 100% retention while
the output was wrong, and both were caught only by rasterizing pages (INV-129).

- **Bold first body row after a page break.** The repeated-header emit left the font bold, so the
  first data row on each continuation page rendered as a second header. Fixed by restoring the row's
  own font after the recursive header emit.
- **Blank line mid-sentence after a `**Label:**` line.** Fixed by exempting `label` blocks from the
  trailing gap.

**6. Known remaining issues — decide, don't inherit silently.**

1. *The parser splits soft-wrapped label paragraphs.* `**Label:** text` plus a continuation line
   becomes two blocks; the gap exemption hides the symptom rather than fixing the cause. The parser
   could absorb continuation lines into the label block. Preferred, but a parser change with wider
   blast radius than the exemption.
2. *Empty leading table column.* A source table written `| | Entity | Name |` renders a real but
   empty first column. Faithful to the source; arguably the renderer should drop wholly empty leading
   columns.

## Acceptance criteria

- [ ] The rendered `docs/bootcamp_data_discoveries.pdf` contains **zero** raw pipe lines (was 61), and
      every source table appears as a bordered grid with a shaded header.
- [ ] A table spanning a page break repeats its header, and the first body row on the continuation
      page renders in the body font, not bold.
- [ ] A ragged or malformed source row does not desynchronise the grid or lose a cell.
- [ ] The stdlib fallback renderer emits aligned columns, not pipe source, so both renderers produce a
      readable table (INV-066), and the fallback still announces itself on stderr (INV-111).
- [ ] Consecutive paragraphs, and paragraph/list boundaries, are visibly separated in both renderers;
      a soft-wrapped `**Label:**` paragraph has **no** break mid-sentence.
- [ ] `↔` and `⚠️` render as `<->` and `!` in **both** PDFs; no `?` substitution remains for any
      character the deliverables carry.
- [ ] Content retention stays 100% and the INV-110 guard is unchanged: a structurally wrong document
      still writes no file and exits non-zero; a recognisable-but-incomplete one still warns and
      exits 0.
- [ ] Verified by **rasterizing** the affected pages, not by exit code, retention, or text extraction
      (INV-129) — the defects and both regressions were invisible to all three.
- [ ] The new tests fail against the pre-change scripts: the pipe-count, table-structure and
      font-safety probes must be able to detect the original defects.
- [ ] The full plugin test suite passes (437 passed / 214 subtests at time of writing).
- [ ] Each remaining issue above is either fixed or recorded as an accepted limitation with its
      reason — not left implicit.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      generators are bundled Python operating on Markdown, independent of the bootcamper's language.

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_discoveries_pdf.py` — `parse_discoveries` table
  accumulation; new `parse_table` and `_render_table_fpdf2`; `TABLE_HEAD_FILL`; generalised
  `_needs_item_gap` with `ITEM_GAP_MM` 3.6 / `ITEM_GAP_PT` 5.0 and the `label` exemption; stdlib
  table rendering; module docstring.
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `_UNICODE_MAP` (`:594-600`): `↔`, `⚠`,
  U+FE0F.
- `tests/test_discoveries_pdf.py` — zero-pipe assertion, table header/cell extraction, paragraph-gap
  and label-continuation cases, page-break header regression.
- `tests/test_recap_pdf_font_safety.py` — widen the character inventory beyond the plugin's own
  templates (`:112`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Markdown tables in the discoveries PDF rendered
  as raw pipe source instead of rows and columns" (2026-07-26, Module Query, Visualize and Discover
  (deliverable rendered at Graduation); `Source: bootcamper-reported`; `Routing: plugin`)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "no blank line between paragraphs or between list
  items in the discoveries PDF" (2026-07-26, same module; `Source: bootcamper-reported`;
  `Routing: plugin`)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "IMPLEMENTATION REPORT — deliverable-rendering
  fixes applied during this session" (2026-07-26, Module Graduation (deliverable rendering);
  `Source: bootcamper-reported (confirmation) with assistant-implemented changes`) — the hand-off
  record for the uncommitted diff, the two regressions, and the remaining issues.
- Priority: High (the implementation report's own priority; the two defect entries are Medium)
- Related specs: `specs/discoveries-pdf-offpage-blocks-and-list-spacing.md` (INV-121 — deferred real
  tables as a known limitation and introduced `_needs_item_gap`),
  `specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (INV-110/INV-111),
  `specs/artifact-level-verification-for-deliverables.md` (INV-129 — why rasterizing is the
  verification), `specs/always-produce-data-discoveries-document.md` (established this deliverable),
  `specs/recap-pdf-certificate-version-and-list-spacing.md` (sibling generator),
  `specs/apply-senzing-style-guide-to-deliverables.md` (INV-081 brand palette)

## Invariants introduced

- `INV-142` — A bundled generator MUST render a Markdown construct as that construct, never as its
  source text; tables are drawn as a grid, with a repeated header across page breaks that does not
  leave the following body row bold, ragged rows normalised, and adjacent tables visibly separated
  (recorded in `specs/INVARIANTS.md`).
- `INV-143` — Character sanitisation MUST NOT substitute `?` for an unencodable character, and the
  inventory under test MUST cover what generated deliverables carry, not only what the plugin's own
  templates emit (recorded in `specs/INVARIANTS.md`).

## Resolution of the known remaining issues

1. **Parser splits soft-wrapped label paragraphs — FIXED at the cause.** `parse_discoveries` now
   absorbs a plain line following a `**Label:**` line into that label's block, so the paragraph
   reflows as one. The `_needs_item_gap` carve-out that suppressed the gap after a `label` block was
   removed with it: a `text` block after a label is now a genuinely new paragraph and takes a normal
   gap, which the workaround had been hiding.
2. **Empty leading table column — ACCEPTED, not fixed.** A table written `| | Entity | Name |` has a
   blank *header* over a real row-label column; dropping the column would delete the values beneath
   it. Only a *wholly* empty column is safely droppable, and distinguishing the two requires scanning
   every row to discard something whose worst case is one narrow empty cell — a poor trade against
   silently losing a column that carries data. Reasoned in `parse_table`'s docstring so it is not
   "fixed" later by mistake.
