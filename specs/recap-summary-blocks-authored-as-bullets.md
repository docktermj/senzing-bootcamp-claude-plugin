# End-of-Module Summary blocks render unbulleted because the bundled example recap authors them inline, contradicting the authoring template

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

In the rendered `docs/bootcamp_recap.pdf`, within each module's **End-of-Module Summary**: the
`What you accomplished:` and `Files produced:` content did not render as bulleted lists.

The bootcamper's suggested fix was to change the renderer ("render as bulleted lists, one bullet
per line from the source Markdown"). **The renderer already does that.** Verified by rendering a
two-module probe recap through
`plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` (working tree, 2026-07-29) with the two
authoring shapes side by side and extracting the text with `pdftotext -layout`.

Authored as bullets — renders correctly:

```text
What you accomplished:
  ·   Bulleted accomplishment one.
  ·   Bulleted accomplishment two.

Files produced:
  ·   docs/a.md - first file.
  ·   docs/b.md - second file.
```

Authored inline after the label — renders as a wrapped paragraph, no bullets, continuation
hanging under wherever the label ended:

```text
What you accomplished: Inline prose accomplishment that was authored on the same line as the label, exactly
                       as the bundled example recap does it.

Files produced: docs/c.md, docs/d.md
```

So the defect is **not** in the renderer. It is that the plugin's own authorities disagree about
which shape to write, and the shape that reaches the PDF has no bullets to render.

## Root cause

Two plugin-side authorities contradict each other:

- **`plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:78-85`** — the
  authoring template — writes the first two blocks as **bulleted lists** and only
  `Why it matters:` inline:

  ```markdown
  **What you accomplished:**
  - {plain-language accomplishment 1}
  - {accomplishment 2}

  **Files produced:**
  - `{path}` — {what it is}

  **Why it matters:** {1-2 sentences tying this module's output to the bootcamper's goal}
  ```

- **`plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md:40-44, 77-81, 119-123`** —
  the bundled worked example, and the thing a guide is most likely to pattern-match on — writes
  **all three inline**:

  ```markdown
  **What you accomplished:** Introduced the core ideas of entity resolution — principle-based matching, …

  **Files produced:** (no files — conceptual primer)
  ```

  and `**Files produced:** docs/business_problem.md, config/data_sources.yaml, docs/data_flow.md, README.md, …`
  — a comma-joined run of five paths where the template calls for one bullet per file.

- **`plugins/senzing-bootcamp/skills/graduation/SKILL.md:275-284`** — graduation's Step 1a
  backfill — requires the three labels but specifies **no shape** for their content, so a
  backfilled block is written whichever way the guide infers.

Nothing checks the shape either: `--check` and `tests/test_recap_summary_blocks.py` validate that
the three **labels** are present (INV-103), not that list-shaped blocks are authored as lists.
So an inline-authored summary passes every gate and reaches the keepsake unbulleted.

## Proposed change

Make the bullet shape the single, stated convention, and align the example to it:

1. **Fix the bundled example** (`bootcamp_recap.example.md`): rewrite every module's
   `What you accomplished:` and `Files produced:` blocks into the bulleted form
   `module-completion.md` already prescribes — one bullet per accomplishment, one bullet per
   file with its "— what it is" gloss. Leave `Why it matters:` inline (the template's shape, and
   what the renderer's `_NEW_LINE_LABELS` handling now formats). Keep
   `(no files — conceptual primer)` as a single bullet or inline value, since it is one value,
   not a list.
2. **State the shape in graduation's backfill** (`SKILL.md` Step 1a): a backfilled
   `What you accomplished:` / `Files produced:` block is written as a bulleted list beneath its
   label, one item per line; `Why it matters:` stays inline after its label. Say why — the PDF
   renders bullets as bullets and inline text as a wrapped paragraph, so the shape chosen at
   authoring time is the shape the keepsake carries.
3. **Assert it**, so the two authorities cannot drift apart again: extend the recap tests to
   check that the bundled example authors both blocks as bullets, and add a render-level test
   that a bullet-authored block produces distinct bulleted items in the PDF text.

⚠️ Do **not** "fix" this by making the renderer split an inline comma-joined value into bullets.
That guesses at item boundaries in bootcamper-authored prose — `Files produced:` happens to be
comma-separable, `What you accomplished:` is not — and would fabricate list structure that the
source did not state (INV-085's principle: do not rewrite the bootcamper's prose).

## Acceptance criteria

- [ ] `bootcamp_recap.example.md` authors `What you accomplished:` and `Files produced:` as
      bulleted lists beneath their labels in **every** module section, matching
      `module-completion.md:78-85`; `Why it matters:` remains inline.
- [ ] `graduation/SKILL.md` Step 1a states the shape for backfilled blocks (bullets for the
      first two, inline for `Why it matters:`) and why it matters to the rendered PDF.
- [ ] A test asserts the bundled example uses the bulleted shape for both blocks, so the example
      and the template cannot drift apart again.
- [ ] A test renders a bullet-authored End-of-Module Summary and asserts the PDF text carries
      distinct bulleted items (not one wrapped paragraph).
- [ ] `tests/test_recap_summary_blocks.py` and the other recap PDF suites still pass — the
      inline shape must remain **parseable** (older recaps carry it, and INV-103's label check is
      shape-independent); this spec changes what the plugin *authors*, not what it *accepts*.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      change is Markdown authoring shape, unaffected by OS or the bootcamper's chosen language.

## Affected files

- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` — rewrite the two blocks in
  each module's End-of-Module Summary into bulleted form.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1a backfill (~lines 275-284):
  state the authoring shape.
- `tests/test_recap_summary_blocks.py` (or a sibling) — assert the example's shape and the
  render-level bullet outcome.
- Possibly `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — no shape
  change needed (it is already correct), but worth one line making the shape explicitly binding
  rather than merely illustrated by the template block.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "End-of-Module Summary blocks in bootcamp_recap.pdf are not formatted as bulleted lists / left-justified" (2026-07-29, Module Graduation; `Source: bootcamper-reported`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact — this is the plugin's own PDF authoring and rendering
  path). Server **1.32.2** was current at triage time, 2026-07-29.
- Upstream: not applicable.
- Related specs: `specs/end-of-module-summary-blocks-guaranteed.md` (INV-103's label
  requirement — this spec adds the *shape* the labels' content is written in),
  `specs/recap-pdf-professional-design.md`, `specs/example-recap-reference.md`,
  `specs/refresh-example-recap.md`,
  `specs/recap-new-line-labels-regression-tests.md` (the `Why it matters:` half of the same
  bootcamper report, already implemented but unasserted)

## Note on the rest of the reported entry

The entry's second half — *"the 'Why it matters:' text should appear beneath the label,
left-justified, but does not"* — **is already fixed** in the working tree
(`generate_recap_pdf.py`, `_NEW_LINE_LABELS = ("why it matters",)`), together with the follow-up
entry asking for a blank line and an indented text block. The probe render above confirms the
current behavior: label on its own line, a gap, then the body indented 12 mm to line up with
bullet text. That change is uncommitted and carries no regression test — see
`specs/recap-new-line-labels-regression-tests.md`.

## Deviations from this spec, and why (2026-07-29)

- **One file the spec did not list had to change: the committed example PDF.**
  `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf` was regenerated after
  editing the `.md`. INV-065 requires the shipped pair to remain regenerable, and
  `tests/test_example_recap_sync.py::TestPdfMatchesItsSource` asserts distinctive source
  lines appear in the committed PDF — so editing the Markdown alone would have failed the
  suite and left a stale keepsake reference. Regenerated from an unrelated working
  directory (per INV-161): `rendered 29079 of 29345 source characters (99%), embedded 1 of
  1 images`.
- **`module-completion.md` was changed, not merely considered.** The spec listed it as
  "possibly" needing a line. It got an explicit ⛔ bullet making the *shape* binding
  alongside the label, because the shape rule needs to be stated where the recap is
  written, and `test_the_shape_is_stated_where_the_recap_is_written` asserts it in both
  that file and `graduation/SKILL.md`.
- **The renderer was confirmed innocent, as the spec predicted.** No change was made to
  `generate_recap_pdf.py`. The probe render in the spec's Problem section was reproduced,
  and the bullet path renders correctly.
- **A suspected indent irregularity turned out not to exist.** `pdftotext -layout` output
  suggested the first bullet of each block sat at a different indent from the rest.
  Measuring the actual content stream showed every bullet marker at x=48.2 and every
  bullet text at x=65.2 — identical. The apparent difference was column snapping in the
  extraction tool, not rendering. Recorded so a future reader does not chase it.

## Invariants introduced

- `INV-176` — Every End-of-Module Summary block MUST be authored in its required **shape**, not
  merely carry its label: `**What you accomplished:**` and `**Files produced:**` are lists (label
  on its own line, one bullet per accomplishment, one bullet per file with a short "— what it is"
  gloss), while `**Why it matters:**` is prose that stays inline after its label. Binds what the
  plugin *authors* (the module-completion template, graduation's Step 1a backfill, and the shipped
  `bootcamp_recap.example.md`); MUST NOT be enforced on *parsing*, since existing recaps carry the
  inline shape and INV-103's presence check is deliberately shape-independent. Extends INV-103
  from which blocks are present to how they are written. (Recorded in `specs/INVARIANTS.md`,
  2026-07-29.)
