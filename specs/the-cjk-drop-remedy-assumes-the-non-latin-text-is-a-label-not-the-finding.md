# The dropped-character warning's remedy assumes the non-Latin text is a name; followed literally on a finding whose evidence IS the non-Latin text, it deletes the finding

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`bootcamp_data_discoveries.pdf` dropped 38 CJK characters, and the generator correctly said so.
Its remedy was:

> "To fix: use each entity's verified Latin-script name or alias instead of its non-Latin primary
> name (especially inside fenced/monospace blocks), and use ASCII connectors (| and v) in ASCII
> diagrams. Never substitute a guess for a name you have not verified."

That is right for a non-Latin **entity name**. It is wrong for this document, where the finding was
*about* Japanese text wrongly stored in a `PASSPORT_NUMBER` field. The CJK string was the
**evidence**, not a label. There is no Latin-script alias for an issuance note, and there is nothing
to substitute — **following the advice literally would have deleted the finding.**

The document was fixed by describing each value in ASCII alongside the verbatim form, which keeps
the evidence in both the Markdown and the PDF. That generalizes; the warning does not offer it.

**The warning itself is good and stays.** Silent character loss in a keepsake is the defect
INV-143's drop-and-warn contract exists to prevent, and it worked. Only the remedy is
under-specified, and the cost of that is the one outcome the warning was built to avoid: content
that should have survived, removed on the generator's advice.

## Root cause

`plugins/senzing-bootcamp/scripts/generate_recap_pdf.py:1486-1491` composes a single remedy
sentence for every drop, and it is written for one case:

```python
f"otherwise intact, but those characters are GONE from it: check the page before "
f"sharing it. To fix: use each entity's verified Latin-script name or alias instead "
f"of its non-Latin primary name (especially inside fenced/monospace blocks), and use "
f"ASCII connectors (| and v) in ASCII diagrams. Never substitute a guess for a name "
f"you have not verified.\n"
```

The warning is emitted for **any** dropped character, from any passage — prose, table cell, or
fenced block — but the remedy names exactly two situations: a non-Latin entity name, and Unicode
box-drawing connectors. A dropped character that is neither has no prescription, and the reader
takes the nearest one, which is *replace it with a Latin name*.

**The reach is all three PDF generators, from one string.** `generate_document_pdf.py` is a thin
alias — it does `from generate_discoveries_pdf import main` (`:41`) and nothing else — and
`generate_discoveries_pdf.py` imports the folding and warning machinery from
`generate_recap_pdf.py`. So the Bootcamper's report against `generate_document_pdf.py` is accurate
through that chain, and fixing the one string fixes every caller.

Nothing in the drop path knows whether a passage is a label or a subject, and it cannot be made to
know. The fix is to state the second case in the remedy, not to classify passages.

## Proposed change

1. **Extend the remedy with the subject case.** After the entity-name clause, state the case where
   the non-Latin text is the *subject* of the passage rather than a label for something else: keep
   the verbatim value and add an ASCII description of it beside it, so the PDF carries the meaning
   even though the glyphs are gone. That is what the Bootcamper's fix did and it is the general
   answer.

2. **Make the two cases distinguishable by the reader, since the generator cannot distinguish
   them.** The remedy should read as a short branch — if the dropped text *names* an entity, use its
   verified Latin-script name or alias; if the dropped text *is* what the passage is about, describe
   it in ASCII next to the verbatim form. The existing "never substitute a guess for a name you have
   not verified" applies to the first branch only and must not read as forbidding the second.

3. **Keep the message one warning, not a taxonomy.** It already carries the count, the affected
   passage count, the character names and the first affected passage; the fix is one added clause,
   not a longer message. It is printed to stderr while the PDF still ships (INV-048/INV-052/INV-066)
   and must stay readable at that length.

4. **Leave the drop behavior alone.** INV-143 requires dropping over substituting `?`, the
   non-transliteration reasoning at `_fold_to_latin1` (`:1495-1510`) is sound, and none of it changes
   here.

## Acceptance criteria

- [ ] The dropped-character warning offers a remedy for the case where the non-Latin text is the
      subject of the passage: keep it verbatim and describe it in ASCII alongside.
- [ ] The two remedies are distinguishable, and the "never substitute a guess" caution is scoped to
      the entity-name branch.
- [ ] The warning still reports the character count, passage count, character names and first
      affected passage, and still exits 0 with the PDF written (INV-048/INV-052/INV-066).
- [ ] The change reaches all three generators — verified by running `generate_document_pdf.py`,
      `generate_discoveries_pdf.py` and `generate_recap_pdf.py` over a fixture whose only non-Latin
      content is a field value under discussion, not a name.
- [ ] `_fold_to_latin1`'s drop-not-substitute behavior is unchanged (INV-143).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — the remedy string at `:1486-1491`
- `tests/` — a fixture where the dropped text is the subject rather than a label, asserting the
  warning names the describe-in-ASCII remedy

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Joel.md` → "Improvement: the PDF renderer's
  CJK-dropping advice does not fit a finding whose evidence IS non-Latin" (2026-08-18, Module Query,
  Visualize and Discover; `Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: n/a (no Senzing fact) — the defect is entirely in the plugin's own generator
  wording. Reported against the stdlib renderer with no fpdf2 installed and Latin-1 core fonts; the
  remedy string is renderer-independent.
- Upstream: not applicable
- Related specs: `specs/generators-warn-on-dropped-unencodable-characters.md`,
  `specs/stdlib-pdf-writer-substitutes-question-marks.md`,
  `specs/recap-pdf-generator-fail-loudly-on-content-loss.md`
