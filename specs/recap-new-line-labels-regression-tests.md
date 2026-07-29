# The `_NEW_LINE_LABELS` label/gap/indent behavior is implemented in both PDF generators but asserted by no test

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two bootcamper-reported formatting defects were fixed in-session and **are already implemented**
in the working tree:

1. **`Why it matters:` in the recap PDF** — the label now renders on its own line, followed by a
   blank-line gap, with the value indented 12 mm beneath it (lining up with bullet text) rather
   than continuing inline and hanging-indenting under wherever the label happened to end. This
   covers both the original report and its follow-up asking for the gap and the indent.
2. **`generate_discoveries_pdf.py`'s long-label callouts** — the same hanging-indent defect on
   the `Near-miss (the one that teaches more):` and `Measurement:` callouts, fixed with the same
   mechanism.

Both are confirmed working. Rendering a probe recap through the working-tree generator
(2026-07-29) and extracting with `pdftotext -layout` gives:

```text
Why it matters:

       This is the reason it matters, spanning a sentence or two so we can see how the block wraps and where it
       sits.
```

**The problem is that nothing asserts it.** The behavior rests on a deliberately narrow
allowlist in each generator:

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py:283` —
  `_NEW_LINE_LABELS = ("why it matters",)`
- `plugins/senzing-bootcamp/scripts/generate_discoveries_pdf.py:225` —
  `_NEW_LINE_LABELS = ("near miss the one that teaches more", "measurement")`

and on a `force_new_line` guard that must also suppress the pre-existing hanging-indent branch
(`generate_recap_pdf.py:2290`, `generate_discoveries_pdf.py:658`: `if not force_new_line and
remaining < max(20.0, epw * 0.5)`). `grep -rl "_NEW_LINE_LABELS" tests/` returns **nothing**: no
test names the constant, the label-on-own-line outcome, the gap, or the indent, in either
generator.

That makes the fix silently regressible in three distinct ways, all of which restore the exact
defect the bootcamper reported:

- an entry dropped from or renamed in either allowlist (the keys are *normalized* forms —
  `"near miss the one that teaches more"` has no hyphen or parentheses — so a plausible-looking
  "tidy-up" to match the visible label text would break the match and produce no error);
- the `not force_new_line` guard removed, restoring the hanging indent on top of the new layout;
- the gap or indent constants (`_ITEM_GAP_MM * 2`, `+= 12`) changed while chasing an unrelated
  spacing issue.

The allowlist design is itself load-bearing and worth protecting: the discoveries generator's
comment records that a blanket "every `**Label:**` breaks to its own line" change **broke two
existing tests** (`test_consecutive_paragraphs_have_a_blank_line_between_them`,
`test_a_soft_wrapped_label_is_not_split_mid_sentence`), because short labels like
`Cross-source overlap:` are meant to stay inline with their wrapped continuation. A future
maintainer without a test for the allowlist has no signal that narrowness is the point.

## Root cause

The fixes were made directly in response to live bootcamper feedback during a graduation run and
landed as renderer changes only. No test accompanied either, and the existing suites pass either
way — `tests/test_recap_summary_blocks.py` and friends assert that the three End-of-Module Summary
**labels are present** (INV-103), which is shape-independent, so they pass identically whether
`Why it matters:` renders inline or on its own line.

Both changes are also currently **uncommitted** in the working tree, so nothing in git history
records the intent either.

## Proposed change

Add regression tests for the label/gap/indent behavior in both generators. No renderer change is
required — this spec is the guard, not the fix:

1. **Recap generator:** render a recap whose End-of-Module Summary carries a multi-sentence
   `**Why it matters:**` value, extract the text, and assert the label ends its own line with the
   value beginning on a later line — not on the same line as the label. Assert a short inline
   label (one not in the allowlist) still renders inline with its value, so the test pins
   *selectivity*, not just the new behavior.
2. **Discoveries generator:** the same, for `Near-miss (the one that teaches more):` and
   `Measurement:`, plus an assertion that a short label such as `Cross-source overlap:` stays
   inline — the case the allowlist exists to protect and the one a blanket change broke.
3. **Pin the allowlist keys to the normalization used to match them.** Assert that each configured
   key matches the label text it is meant to catch *through the same normalizer the renderer uses*
   (`_normalize_heading` in the recap generator, `_normalize` in the discoveries generator), so a
   key edited into a form that no longer matches fails loudly instead of silently disabling the
   fix.
4. **Assert the layout, not the millimetres.** Test that the value starts on a line after the
   label and is indented relative to it; do not hardcode `12` or `_ITEM_GAP_MM * 2`, so a
   deliberate design tweak stays possible while an accidental collapse back to inline fails.

## Acceptance criteria

- [ ] A test renders a recap with a multi-sentence `**Why it matters:**` value and asserts the
      value does not begin on the label's line, and is indented relative to the label.
- [ ] A test asserts a label **not** in `generate_recap_pdf.py`'s `_NEW_LINE_LABELS` still renders
      inline with its value.
- [ ] Equivalent tests exist for `generate_discoveries_pdf.py`'s
      `Near-miss (the one that teaches more):` and `Measurement:` callouts, plus one asserting a
      short label (e.g. `Cross-source overlap:`) stays inline.
- [ ] A test asserts every `_NEW_LINE_LABELS` key in each generator matches its intended label
      text through that generator's own normalizer, so a key edited into a non-matching form
      fails.
- [ ] The tests assert relative layout (later line, greater indent), not specific millimetre
      constants.
- [ ] The full existing suites still pass, including
      `test_consecutive_paragraphs_have_a_blank_line_between_them` and
      `test_a_soft_wrapped_label_is_not_split_mid_sentence`, which the allowlist exists to keep
      passing.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      tests drive the bundled Python generators and must not depend on a PDF text-extraction tool
      that is absent on some platforms (`pdftotext` is **not** a dependency; extract via the
      generators' own text path or the existing suites' extraction helper, per
      `specs/pdf-layout-verification-without-poppler.md`).

## Affected files

- `tests/test_recap_pdf_guard.py` (or a new sibling, e.g. `tests/test_new_line_labels.py`) — the
  recap-generator assertions.
- `tests/test_discoveries_pdf.py` — the discoveries-generator assertions.
- No change required to `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` or
  `plugins/senzing-bootcamp/scripts/generate_discoveries_pdf.py`; the behavior under test is
  already implemented there (currently uncommitted).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → two entries, both 2026-07-29:
  - "\"Why it matters:\" in bootcamp_recap.pdf needs a blank line and an indented text block"
    (Module Graduation; `Source: bootcamper-reported`; Priority Low)
  - "generate_discoveries_pdf.py had the same long-label hanging-indent issue as the recap
    generator" (Module Query, Visualize and Discover;
    `Source: self-observed (assistant retrospective)`; Priority Low)

  Grouped into one spec because both are the same fix mechanism (`_NEW_LINE_LABELS` +
  `force_new_line`) in two sibling files, and one test-shape covers both.
- Priority: Low
- MCP re-check: n/a (no Senzing fact — plugin PDF rendering only). Server **1.32.2** was current
  at triage time, 2026-07-29. Behavior verified by rendering probe documents against the
  working-tree generators instead.
- Upstream: not applicable.
- Related specs: `specs/recap-summary-blocks-authored-as-bullets.md` (the *other* half of the
  same bootcamper report — the bullets, which are **not** yet fixed),
  `specs/discoveries-pdf-real-tables-and-paragraph-spacing.md`,
  `specs/recap-pdf-professional-design.md`,
  `specs/pdf-layout-verification-without-poppler.md`

## Deviations from this spec, and why (2026-07-29)

- **The tests live in one new module, not split across two existing ones.** The spec's
  Affected files named `tests/test_recap_pdf_guard.py` (or a sibling) and
  `tests/test_discoveries_pdf.py`. Both generators' assertions were instead put in a single
  new `tests/test_new_line_labels.py`, because the contract under test is *shared* — the
  same `_NEW_LINE_LABELS` + `force_new_line` mechanism in two files — and a shared
  `LabelLayoutAssertions` base holds both generators to one relative-layout definition.
  Splitting them would have duplicated that definition and let the two halves drift, which
  is the failure this spec exists to prevent. `tests/test_discoveries_pdf.py` was therefore
  not modified.
- **One assertion beyond the acceptance criteria was added.**
  `TheHangingIndentBranchStaysSuppressed` asserts, on the source of both generators, that
  the `if not force_new_line and remaining <` guard is still present. The spec's Problem
  names this as regression route #2 but no criterion covered it, and it is invisible to a
  rendered assertion: with the guard removed the value still starts below its label, so
  every layout test above still passes while the hanging indent returns. Asserted on source
  rather than position because the resulting shift is a few millimetres, which would make a
  rendered assertion brittle — exactly what the spec's "assert the layout, not the
  millimetres" criterion warns against.
- **Each guard was mutation-tested rather than assumed.** Three mutations were applied to
  the working tree and reverted: emptying the recap allowlist (caught by the layout test and
  the key test), rewriting a discoveries key to its visible, non-normalized form
  `"near-miss (the one that teaches more)"` (caught by the layout test and both key tests),
  and removing the `not force_new_line` guard from both generators (caught by the source
  guard). The second is the regression the spec calls invisible; it is now the one most
  precisely caught.
