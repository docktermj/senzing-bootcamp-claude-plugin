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
   `_ITEM_GAP_MM` machinery and its never-after-the-last-item behaviour.
2. **Space "Questions & Responses" top-level bullets only** — apply the gap when the current
   line is a top-level `- ` bullet and the next content-bearing line is also top-level,
   leaving indented `- **R:**` sub-bullets tight against their question. This satisfies the
   request without the regression the original exclusion guarded against.
3. **Invert the default (the durable half).** Make spacing apply to every bullet list with an
   explicit **opt-out** list, rather than an opt-in list of three names. The current shape is
   why this was missed, and it will miss the next list added for the same reason.
4. **Correct the comment block and the originating spec.** Update "Deliberately NOT spaced"
   to match the new behaviour, and append a dated note to
   `specs/recap-pdf-certificate-version-and-list-spacing.md` recording that its
   "short reference list of paths" characterisation was measured false — items run 8–12
   wrapped entries because the template mandates a gloss. Do not rewrite that spec's original
   reasoning; it was correct given what it assumed, and the correction is the record.

## Acceptance criteria

- [ ] "Files produced" bullets carry `_ITEM_GAP_MM` between items, and no gap after the last.
- [ ] "Questions & Responses" top-level bullets are spaced; indented `- **R:**` sub-bullets
      remain tight against their question — verified positionally, not by eye (INV-142/INV-129).
- [ ] Spacing is opt-out by default: a bullet list added later is spaced without being named.
- [ ] Both renderers satisfy this (INV-066) — the stdlib fallback may achieve separation
      differently but must not run items together.
- [ ] The "Deliberately NOT spaced" comment reflects actual behaviour.
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
