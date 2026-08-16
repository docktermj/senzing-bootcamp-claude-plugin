# "Files produced" was excluded from bullet spacing as "a short reference list of paths" — the recap template makes that false

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A Bootcamper asked that bulleted lists in `docs/bootcamp_recap.pdf` carry visible separation
between items. The generator already implements exactly that, and applies it to three of the
five bullet lists in a module section. Confirmed in code 2026-07-31:

```text
generate_recap_pdf.py:267  _ITEM_GAP_MM = 2.4
generate_recap_pdf.py:271  _SPACED_SUBSECTIONS = ("information shared", "actions taken")
generate_recap_pdf.py:276  _SPACED_LABELS = ("what you accomplished",)
generate_recap_pdf.py:2174 if _is_bullet(line) and (spaced_section or active_label in _SPACED_LABELS):
```

⚠️ **The two exclusions are deliberate decisions from an implemented spec**, not oversights.
`specs/recap-pdf-certificate-version-and-list-spacing.md:92` excludes "Files produced" as "a
short reference list of paths", and its line 101 excludes "Questions & Responses" because its
responses are indented sub-bullets and spacing every bullet would separate each answer from
its question. This spec reverses the first and narrows the second, on evidence the original
did not have.

**The "short reference list of paths" premise is false**, because
`bootcamp-onboarding/module-completion.md` requires each entry to be a path **plus a short
"- what it is" gloss**. Measured in the reporting run's recap:

| Section | Items | Longest item | Items likely to wrap |
|---|---|---|---|
| Truth Set visualization | 12 | 110 chars | ~2 |
| Query, Visualize and Discover | 11 | 188 chars | ~4 |
| Data Quality, Mapping, and Transformation | 8 | 147 chars | ~4 |
| Data processing | 8 | 121 chars | ~3 |
| Data collection | 5 | 145 chars | ~4 |

Neither short nor one line per item, in any section.

**The generator's own comment states why that matters**: "a bullet ends with a `multi_cell`
at line height 5.5 and no trailing gap, so the space between two separate items equals the
space between a wrapped item's own lines, and multi-line items run together." That condition
holds in "Files produced" in seven of nine sections — and it is the one list where the fix is
switched off.

**The "Questions & Responses" rationale is sound but over-broad.** It argues correctly
against spacing the indented `- **R:**` sub-bullets. It does not argue against spacing the
top-level `- **Q:**` items, which run 4–14 lines per section with no separation between one
question-and-answer pair and the next.

**Why it matters.** "Files produced" is the recap's index — the list a reader uses to find
what the bootcamp built — so it is the worst one to render as an undifferentiated block. And
the fix is written, tested and in use three lines away.

## Root cause

The spacing is **opt-in by name**: a tuple of three subsection/label strings. Any list added
or renamed later is unspaced by default, and the decision to exclude a list was made from its
*title* ("Files produced" sounds like short paths) rather than from what the template
requires its items to contain. That is why the exclusion looked right when written and is
wrong in every real recap.

## Proposed change

1. **Add `"files produced"` to `_SPACED_LABELS`.** A one-token change reusing the existing
   `_ITEM_GAP_MM` machinery and its never-after-the-last-item behavior.
2. **Space "Questions & Responses" top-level bullets only** — apply the gap when the current
   line is a top-level `- ` bullet and the next content-bearing line is also top-level,
   leaving indented `- **R:**` sub-bullets tight against their question. This satisfies the
   request without the regression the original exclusion guarded against.
3. **Invert the default (the durable half).** Make spacing apply to every bullet list with an
   explicit **opt-out** list, rather than an opt-in list of three names. The current shape is
   why this was missed, and it will miss the next list added for the same reason.
4. **Correct the comment block and the originating spec.** Update "Deliberately NOT spaced"
   to match the new behavior, and append a dated note to
   `specs/recap-pdf-certificate-version-and-list-spacing.md` recording that its
   "short reference list of paths" characterization was measured false — items run 8–12
   wrapped entries because the template mandates a gloss. Do not rewrite that spec's original
   reasoning; it was correct given what it assumed, and the correction is the record.

## Acceptance criteria

- [ ] "Files produced" bullets carry `_ITEM_GAP_MM` between items, and no gap after the last.
- [ ] "Questions & Responses" top-level bullets are spaced; indented `- **R:**` sub-bullets
      remain tight against their question — verified positionally, not by eye (INV-142/INV-129).
- [ ] Spacing is opt-out by default: a bullet list added later is spaced without being named.
- [ ] Both renderers satisfy this (INV-066) — the stdlib fallback may achieve separation
      differently but must not run items together.
- [ ] The "Deliberately NOT spaced" comment reflects actual behavior.
- [ ] `specs/recap-pdf-certificate-version-and-list-spacing.md` carries a dated note that its
      "short list of paths" premise was measured false; its original reasoning is left intact.
- [ ] A test asserts a wrapped multi-line "Files produced" item is separated from the next
      item by more than its own internal line spacing — the exact condition the generator's
      comment describes, which is what makes the failure invisible to a character count.
- [ ] `tests/test_new_line_labels.py` and `tests/test_recap_pdf_certificate.py` pass.
- [ ] MCP re-check: n/a — `generate_recap_pdf.py` is plugin-bundled; no Senzing tool involved.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `_SPACED_LABELS` (276), `_SPACED_SUBSECTIONS` (271), the bullet loop (~2174), the comment block.
- `specs/recap-pdf-certificate-version-and-list-spacing.md` — dated correction.
- `tests/test_new_line_labels.py` — the wrapped-item separation test.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "recap PDF bullet lists need inter-item
  spacing everywhere - \"Files produced\" and \"Questions & Responses\" are excluded and run
  together" (2026-07-31, Module: Graduation; `Source: bootcamper-reported`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact). Code claims verified 2026-07-31 at the lines quoted.
- Upstream: not applicable.
- Related specs: `specs/recap-pdf-certificate-version-and-list-spacing.md` (**this reverses
  one of its deliberate exclusions and narrows the other**),
  `specs/discoveries-pdf-offpage-blocks-and-list-spacing.md` (the same spacing machinery in
  the sibling generator — check whether it carries the same opt-in shape).

## Deviations from this spec, and why (2026-07-31)

All four proposed changes shipped, plus a defect the spec did not know about. Six differences:

1. **The opt-out is structural, and the name lists ship empty.** The spec asks for "an
   explicit **opt-out** list". Both of its exclusions turn out to be one rule: *emit the gap
   when the next content-bearing bullet is top-level*. That keeps an indented `- **R:**` with
   its question **and** separates one Q/R pair from the next, so neither exclusion needs a
   name. `_UNSPACED_SUBSECTIONS` and `_UNSPACED_LABELS` still exist as the escape hatch the
   spec wanted, deliberately empty — and **tested live** rather than left as dead code:
   populating either must actually suppress the gap, or the next maintainer who needs a tight
   list adds a name, sees no effect, and hard-codes something.

2. **A latent pre-existing defect, found while proving criterion 7.** The gap was decided on
   the *bullet* line, asking "is the next **source** line another item?" For a bullet whose
   Markdown wraps across two source lines the answer is no — it is that item's own
   continuation — so **such an item received no gap at all, in either renderer**. Unrelated to
   the exclusions and present since the gap was introduced; invisible because the shipped
   example recap writes every entry as one long source line and lets the renderer wrap it, so
   no fixture had the shape. Fixed via `_still_in_list_item`, so the gap lands after an item's
   *last* source line.

3. **The required test's first draft passed vacuously, and the spec's wording is why it was
   caught.** Comparing item 1's first line to item 2's first line clears any fixed threshold
   whenever item 1 wraps — 31 pt against a 17 pt bar — with the gap switched off. The
   criterion says "more than **its own internal line spacing**", which is the non-vacuous
   comparison: last line of item 1 → first line of item 2, measured against the item's own
   wrapped-line spacing from the same render. Corrected before it shipped.

4. **The spacing indent threshold deliberately differs from the drawing threshold.** Both
   renderers give a bullet its extra visual indent only at `>= 4` leading spaces; spacing
   treats **any** indentation as a continuation. `module-completion.md:72` mandates four
   spaces for a response, but a recap written with two would otherwise have every answer torn
   away from its question — the exact regression the original blanket exclusion existed to
   prevent. A genuine top-level item never carries leading whitespace, so tolerance costs
   nothing. Documented at the helper so the three thresholds are not "unified" by mistake.

5. **The test fixture carried the false premise too.** `SPACING_RECAP`'s "Files produced"
   entries were bare paths with no gloss — a shape `module-completion.md` does not permit — so
   the old test proved tightness on data the plugin never produces. Now glossed and long
   enough to render-wrap, matching both the template and the shipped example recap.

6. **Sibling generator checked, not changed** (the spec's related-specs note asks whether it
   carries the same opt-in shape). It does not: `generate_discoveries_pdf.py` decides spacing
   with `_needs_item_gap(blocks, index)` over typed blocks and is already spaced-by-default,
   with no name list. Worth noting for a future reader that its `_LIST_KINDS` includes
   `subbullet`, so it *would* space between a bullet and its sub-bullet — harmless there,
   because the discoveries document has no Q/R structure, but not a rule to copy into the
   recap.

**Tests changed rather than added:** `test_files_produced_list_stays_tight` asserted the
premise this spec reverses and is now `test_files_produced_wrapped_items_are_separated`;
`test_action_taken_singular_is_covered` asserted membership in a constant that no longer
exists, and its real guarantee — that the singular and plural forms normalize alike, so an
opt-out written either way matches — is asserted directly instead. `test_new_line_labels.py`
and `test_recap_pdf_certificate.py` both pass unchanged, as the spec requires.

## Invariants introduced

- None. Inverting a default and replacing a name list with a structural rule adds no standing
  constraint that is not already enforced by the tests here, and INV-066 already binds the
  two renderers not to drift. The durable half of this change lives in the mechanism itself:
  a list added or renamed later is spaced without anyone remembering to name it.
