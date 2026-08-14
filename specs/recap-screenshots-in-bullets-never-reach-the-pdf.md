# Screenshots embedded as instructed — inside Actions Taken bullets — never reach the recap PDF

## Problem

`bootcamp-onboarding/module-completion.md:110` tells the guide where to put visualization
screenshots:

> add them all to this module's **Actions Taken** as Markdown images —
> `![caption](visualizations/<name>-<tab-slug>.png)`

**Actions Taken is a bulleted list.** Its template (`module-completion.md:85-86`) is
`### Actions Taken` followed by `- {files created or modified, …}`, and the instruction says to add
the images *to* that section. Following it literally produces lines of the form:

```markdown
- ![Entity Graph — 12 resolved entities …](visualizations/results_visualization-entity-graph.png)
```

`scripts/generate_recap_pdf.py` cannot see those. Its detector is anchored to the start of the line
(`generate_recap_pdf.py:126`):

```python
IMAGE_LINE_RE = re.compile(r"^!\[(.*?)\]\((.+?)\)$")
```

and `recap_image_targets()` matches it against `line.strip()` — which removes surrounding whitespace
but not the `- ` list marker. Every bulleted image is therefore invisible to both the embedder and
the tab-coverage check.

**Measured on this walk (2026-08-14), 8 screenshots across three visualizations:**

```
# images written as Actions Taken bullets, exactly as instructed
PDF generated: docs/bootcamp_recap.pdf (rendered 99%, 0 of 8 captured tabs reached the recap)
INCOMPLETE: visualization 'results_visualization': 6 captured tab(s) are missing from the
            recap — entity-graph, merge-statistics, … (captured 6, referenced 0)

# same file, `- ` stripped from those lines only, nothing else changed
PDF generated: docs/bootcamp_recap.pdf (rendered 99%, embedded 8 of 8 images,
                                        8 of 8 captured tabs reached the recap)
```

So the keepsake the bootcamper takes away contains **none** of the screenshots they watched being
captured, and the recap's prose still describes them.

## Why this is worse than a cosmetic bug

1. **The instruction and the tool disagree, and the instruction loses silently.** A guide that
   follows `module-completion.md` correctly produces a PDF with no images, at exit 0.
2. **The `--check` message points away from the cause.** "captured 6, referenced 0" reads as *the
   guide forgot to embed them* — the one thing that did not happen. The images are in the recap; the
   detector cannot see them.
3. **INV-146 requires every captured screenshot to reach the recap**, and graduation's
   orphaned-screenshot backfill exists to catch omissions — but the backfill embeds images the recap
   "does not already reference", and by this detector's reckoning the recap references none. So the
   backfill's own view of the recap is the broken one too.
4. It defeats the artifact-verification discipline the plugin insists on elsewhere: the images were
   captured, opened, verified and captioned, and still did not ship.

## Root cause

Two authors, one contract, never tested together. `module-completion.md` describes *where* images go
in prose ("add them to Actions Taken"); `generate_recap_pdf.py` defines *what shape* an image line
must have (start of line, nothing before it). Nothing states the shape requirement where the images
are authored, and no test renders a recap whose images sit in a list.

## Proposed change

Fix the tool, and state the constraint where the images are written.

1. **`generate_recap_pdf.py`** — accept an image line that carries a list marker. Match
   `^(?:[-*+]\s+)?!\[(.*?)\]\((.+?)\)$` after stripping, and render it as an image either way. This
   is the half that makes existing recaps — including any already written — render correctly.
2. **`module-completion.md`** — say the shape explicitly at the embed instruction: the image goes on
   **its own line**, not as a bullet, and give one worked line. Keep it adjacent to the existing
   `visualizations/…`-not-`docs/visualizations/…` warning (INV-161), which is the same class of
   mistake — a path/shape detail that renders as silent absence.
3. Consider whether the `--check` message should name the shape when it finds captured-but-
   unreferenced images and the recap contains `![` at all: "6 captured tabs are not referenced —
   note that 8 image links were found inside list items, which are not rendered as images."

## Acceptance criteria

- A recap whose images are written as `- ![…](…)` bullets renders them into the PDF, and the
  tab-coverage check reports them as referenced.
- `module-completion.md`'s embed instruction states that the image must be on its own line.
- A test renders a recap fixture containing both bulleted and unbulleted image lines and asserts all
  of them are embedded, and that the tab-coverage check reports zero missing.

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py`
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md`
- `tests/test_recap_pdf_bulleted_images.py` (new)

## Source

`/dry-run` phase 3, 2026-08-14. Reproduced both ways on the walk's own recap: 8 captured
screenshots, `0 of 8` embedded as bullets, `8 of 8` after removing the `- ` markers and changing
nothing else. `fpdf2` renderer.

## Invariants introduced

- `INV-242` — Where shipped prose instructs the guide to author content that a **bundled script
  must parse**, that instruction MUST state the shape the script accepts (recorded in
  `specs/INVARIANTS.md`, indexed under *Generator behaviour: rendering, encoding, reporting*
  beside its sibling INV-161; enforced by `tests/test_recap_pdf_bulleted_images.py`).
  ⚠️ **Minted under the maintainer's standing authorization of 2026-08-14** (given before an
  unattended run), not under case-by-case sign-off — flagged for review.

## Deviations from this spec, and why (2026-08-14)

Implemented as specified, with one finding the spec did not have and one item deliberately
not built.

1. **The pattern existed twice, not once.** The spec locates the defect at
   `generate_recap_pdf.py:126` (`IMAGE_LINE_RE`, used by `recap_image_targets`). There was a
   **second, independent copy** inline in `_render_line` — `re.match(r"^!\[(.*?)\]\((.+?)\)$",
   stripped)` — so the counter and the renderer each decided separately what an image line is.
   Fixing only the constant, as proposed change 1 describes, would have made `--check` report
   the images as referenced while the renderer still embedded none: a worse failure than the
   reported one, because the check would then certify a PDF that was still empty. Both sites are
   now the single `IMAGE_LINE_RE`. `test_the_counter_and_the_renderer_agree` pins them together,
   and the mutation that restores the duplicate copy fails six tests.

2. **Proposed change 3 (the `--check` diagnostic) was not built**, and it is marked "Consider"
   in the spec rather than being an acceptance criterion. Its premise no longer holds: the
   message it proposes — "N image links were found inside list items, which are not rendered as
   images" — describes a state that can no longer occur, since list items now *are* rendered.
   Adding it would ship a diagnostic for a repaired defect, which INV-169's reasoning treats as
   worse than silence. Left unbuilt deliberately, not overlooked.

3. **The instruction's rationale was rewritten mid-implementation** because the first draft
   justified the own-line rule with a consequence the fix had just removed ("it reaches the
   keepsake as its caption text"). Shipping that would have been a dated claim that was false on
   the day it shipped. The rule now stands on the form itself, and names the leniency as a
   rescue for recaps already written as bullets rather than as a second supported style — which
   is the ⚠️ clause carried into INV-242.
