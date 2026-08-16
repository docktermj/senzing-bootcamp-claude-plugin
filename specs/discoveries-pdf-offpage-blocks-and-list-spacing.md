# Fix the discoveries PDF's off-page blocks, squeezed labeled bullets, and list spacing

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The bootcamper asked for a blank line between the elements of every bulleted list in
`docs/bootcamp_data_discoveries.pdf`, and for a re-render to inspect. Rasterizing the result to
check the spacing had landed exposed **three pre-existing layout defects** in the same document.
All three were confirmed present in a render from the unmodified plugin script, so none was
introduced by the spacing change. After the fixes the bootcamper confirmed the document looks
great.

**(a) The entire match-key table was drawn off the page and did not appear — silent content loss.**
`pdftotext` found zero occurrences of "Match key pattern"; the page showed a blank gap with a stray
`| Mat` fragment clipped at the right edge. The generator meanwhile printed
`PDF generated: … content retained: 98%` and exited **0**.

**(b) The cover subtitle "What Senzing found in your data" was clipped off-page**, leaving only
"Wha" visible at the right edge.

**(c) A bullet with a long bold label crammed its body into a narrow right-hand column.** A label
such as `ABC AUTOMOTIVE INVESTMENTS pair (entities 300099, 300054):` leaves roughly 60 mm of a
190 mm line, and every wrapped line then stacks in that narrow column beside a large empty gutter.
On one page two relationship-network bullets were reduced to a ribbon of text about a third of the
page wide.

This document is the one deliverable produced on **every** path through Module 7 — explicitly so
that a bootcamper who declines the Discover walkthrough still leaves knowing what Senzing found in
their data. Defect (a) removed the quantitative heart of it with no signal at all, and (c) made the
qualitative findings hard to read. A bootcamper would reasonably conclude the report was thin, when
the content was present in the Markdown the whole time.

### Reproduced in this repository

Rendering the test suite's own `GOOD_DOC` fixture through the **unmodified** shipped script
(`plugins/senzing-bootcamp/scripts/generate_discoveries_pdf.py`, fpdf2 2.8.5):

```text
PDF generated: docs/bootcamp_data_discoveries.pdf (renderer: fpdf2, content retained: 95%)
exit=0
$ pdftotext … | grep -c "Match key"      → 0
$ pdftotext … | grep -c "NAME+ADDRESS"   → 0
$ pdftotext … | grep -o "Wha"            → Wha
```

The fixture's table (`tests/test_discoveries_pdf.py:52-54`) is entirely absent from the output and
the subtitle is clipped to "Wha", exactly as reported — while the generator reports success.

Cursor measurement confirming the mechanism, same fpdf2 version:

```text
page w=210.0  l_margin=10.0  epw=190.0
x before multi_cell: 10.0
x after  multi_cell: 200.0   ← right margin
x after  ln():       10.0    ← reset
```

**`tests/test_discoveries_pdf.py` passes (16 passed, 12 subtests) on that same broken output.**
Its `test_pdf_carries_the_findings` probes `pdftotext` for six strings, none of which is table
content — so the suite's one positive-presence test cannot see the missing table.

## Root cause

**(a) and (b) share one cause.** In this fpdf2 version `multi_cell` defaults to `new_x=RIGHT`,
leaving the cursor at the right margin (measured: x = 200 mm on a 210 mm page after a full-width
call). Any subsequent `multi_cell(epw, …)` without an x reset therefore draws from 200 mm across
190 mm — entirely off-sheet, rendering as blank space.

In `generate_discoveries_pdf.py`, the affected sites are:

- `:318` — the cover subtitle, immediately after the title's `multi_cell` at `:315`, no reset.
- `:323-324` — the metadata loop; the first line is safe (the `pdf.ln(2)` at `:319` resets x) but
  every line after the first draws from the right margin.
- `:361` — the `code` branch of `_render_block_fpdf2`.
- `:365` — the `table` branch.

Why only those: the `h2`/`h3` branches call `pdf.ln()` first (`:341`, `:351`), which resets x; the
generic bullet/text path calls `pdf.set_x()` (`:375`). **Only the two branches that do neither were
affected** — which is exactly why the bug survived, since most content rendered fine.

**(c)** `generate_discoveries_pdf.py:384-385`:

```python
remaining = epw - (pdf.get_x() - pdf.l_margin)
if remaining < 20:
```

The break-to-new-line guard is an order of magnitude too low: 60 mm of usable width is comfortably
past a 20 mm threshold, so a long label never triggers a break and its body wraps in the remaining
sliver.

`generate_recap_pdf.py:1124-1125` carries the **identical guard** and therefore the same defect
class.

**The requested spacing** simply does not exist: `:389` ends each bullet with `multi_cell` and no
trailing gap.

**Audit result for the sibling generator.** `generate_recap_pdf.py` was audited for the (a)/(b)
pattern as the feedback recommended. All six of its `multi_cell` calls are safe — `:712` (preceded
by `set_x` at `:704`), `:765` (`set_xy` at `:762`), `:946` (`set_xy` at `:943`), `:1033` (`ln(9)` at
`:1027`), `:1078` (`set_x` at `:1077`), `:1129` (`set_x` at `:1115`). It needs the (c) fix only.

**Also confirmed: an INV-111 violation.** `generate_discoveries_pdf.py:86` falls back from
`brand_tokens` to an inlined palette under a bare `except Exception:` with **no stderr message**.
INV-111 requires a bundled generator to state on stderr when it falls back from an optional
dependency to a lesser path. Nothing renders wrong today — the inlined values are deliberately equal
to the tokens, and `tests/test_brand_sync.py` asserts that — but the degradation is invisible, which
is precisely what INV-111 forbids.

## Proposed change

**1. Stop relying on the ambient cursor (the silent-loss fix).**

Reset x before every full-width `multi_cell`. Apply at the five sites above. The durable fix is not
five `set_x()` calls: either pass `new_x="LMARGIN"` explicitly on every `multi_cell`, **or** route
all full-width text through one small helper that resets x first — so a new block kind cannot be
added without inheriting the correct behavior. Prefer the helper; the defect's whole shape was "two
branches out of five forgot".

**2. Break to a new line when a bold label has consumed most of the width.**

Change the guard from `remaining < 20` to `remaining < max(20, epw * 0.5)`, continuing at a modest
hanging indent (`indent + 6`). Short labels still render inline, which reads well; only genuinely
long ones break. Apply in **both** `generate_discoveries_pdf.py:384-385` and
`generate_recap_pdf.py:1124-1125`.

**3. Space consecutive list items (the original request).**

A 2.4 mm gap after a `bullet`/`subbullet` block when the following block is also one, via a
`_needs_item_gap(blocks, i)` helper, so the gap falls strictly between items and never after the
last. Mirror it in the stdlib fallback renderer (`:392-440`) at 3 pt so the two paths do not drift.
Unlike the recap, **every** bullet list is spaced here, as asked — this document has no Q/R pairing
to preserve.

**4. Report the `brand_tokens` fallback on stderr (INV-111).**

Replace the silent `except Exception:` at `:86` with a message distinguishing "not importable from
this directory" from "present but unusable", matching how `:300-305` already reports the fpdf2
fallback. Also note in the module docstring that `brand_tokens.py` must sit beside a copied
generator — `generate_discoveries_pdf.py` imports shared helpers from `generate_recap_pdf.py`
"expected next to this script" (`:61-77`) and imports `brand_tokens` separately, so a project-local
copy of one without the other silently used fallback colors until `brand_tokens.py` was copied
alongside.

**5. Close the test gap that let (a) ship.**

Extend `test_pdf_carries_the_findings` to probe for **table content** from the fixture
(`Match key`, `+NAME+ADDRESS`, `1042`) and for the cover subtitle in full. A positive test for
content known to be in the source is the only thing that catches off-page rendering — the retention
percentage structurally cannot, because the text *is* in the content stream, merely positioned
outside the page box.

**Known limitation, deliberately not changed.** The generator renders Markdown tables as their
verbatim source — monospaced pipe-delimited rows — which is its documented design, not a defect. So
the match-key table appears as readable raw Markdown rather than a drawn table with ruled cells.
Drawing real tables would be a genuine enhancement but is a larger change than a layout fix. Flagged
so the choice stays visible rather than assumed.

## Acceptance criteria

- [ ] Rendering the test suite's `GOOD_DOC` fixture yields a PDF whose extracted text contains the
      table's content (`Match key`, `+NAME+ADDRESS`, `1042`) — currently zero hits.
- [ ] The cover subtitle extracts and **rasterizes** as the full "What Senzing found in your data",
      not "Wha".
- [ ] Every metadata line on the cover renders inside the page margins, not just the first.
- [ ] A `code` block and a `table` block each render from the left margin at full width, whatever
      block precedes them.
- [ ] A new block kind added to `_render_block_fpdf2` inherits correct x behavior without its author
      remembering to reset (helper or explicit `new_x`), and no full-width `multi_cell` in the file
      depends on the ambient cursor.
- [ ] A bullet with a ~60-character bold label puts the label on its own line and its body at full
      width; a short-labeled bullet still renders inline. Verified in **both**
      `generate_discoveries_pdf.py` and `generate_recap_pdf.py`.
- [ ] Consecutive bullets and sub-bullets are visibly separated, with no gap after the last item of
      a list, in both the fpdf2 and stdlib renderers.
- [ ] A `brand_tokens` import failure prints a stderr line naming which case occurred (INV-111);
      the fallback still proceeds and still renders identical colors (`tests/test_brand_sync.py`
      passes).
- [ ] `tests/test_discoveries_pdf.py` passes and now **fails** against the pre-fix script — the
      table and subtitle probes must be able to detect the original defect.
- [ ] The INV-110 guard is unchanged: retention is still reported, a structurally wrong document
      still writes no file and exits non-zero, and a recognizable-but-incomplete one still warns and
      exits 0.
- [ ] All six required findings sections are present in the rendered PDF after the change.
- [ ] Verified by rasterizing every affected page, not by exit code or retention percentage.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_discoveries_pdf.py` — x-reset helper / explicit
  `new_x` at `:315`, `:318`, `:324`, `:361`, `:365`; long-label guard at `:384-385`;
  `_needs_item_gap()` for `:368-389` and the stdlib renderer `:392-440`; INV-111 stderr message at
  `:86`; docstring note about `brand_tokens.py` placement.
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — long-label guard at `:1124-1125` only
  (audited clean for the x-reset defect).
- `tests/test_discoveries_pdf.py` — probe table content and the full subtitle in
  `test_pdf_carries_the_findings`; add a long-bold-label case.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Space bullet lists in the discoveries PDF —
  and fix three layout defects found doing it, one of which silently dropped the match-key table off
  the page" (2026-07-26, Module Query, Visualize and Discover (deliverable), surfaced at Graduation;
  `Source: bootcamper-reported`)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Positive feedback — the improved discoveries
  PDF, with the full implementation record for porting upstream" (2026-07-26, same module;
  `Source: bootcamper-reported`) — the port-ready record for the four changes above.
- Priority: High (one of the four changes is a silent-content-loss fix, not a cosmetic one)
- Related specs: `specs/always-produce-data-discoveries-document.md` (established this
  deliverable), `specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (INV-110/INV-111 — the
  guard this defect slipped past, and the invariant `:86` violates),
  `specs/recap-pdf-certificate-version-and-list-spacing.md` (sibling generator; shares the
  long-label fix), `specs/final-review-doc-coherence.md` (prior brand-fallback sync finding),
  `specs/apply-senzing-style-guide-to-deliverables.md`,
  `specs/artifact-level-verification-for-deliverables.md` (the general lesson).

## Invariants introduced

- `INV-121` — A bundled generator rendering a bootcamper-facing deliverable MUST NOT depend on
  the ambient cursor position for full-width text; verification MUST be positional, not a
  text-extraction presence check (recorded in `specs/INVARIANTS.md`).
