# Give `INVARIANTS.md` a topical index, so the development rules can be found without reading all 142

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`specs/INVARIANTS.md` is 192 invariants and 21,270 words. Measured 2026-07-30, it holds
two clearly different kinds of content — and only one of them is organised.

**The first 50 are organised.** They sit in seven labelled sections
(`## INV-005 – INV-015: Whole-Bootcamp outcomes`, `## INV-033 – INV-046: Module-specific
outcomes`, and so on). They are short (median **15** words) and mostly not MUST
conditions at all (**8 of 50**) — they describe what the bootcamp *produces*: "The Senzing
SDK is installed.", "A banner is presented, 'GRADUATION'."

**The remaining 142 are not organised.** Every invariant from INV-051 onward lives in a
single flat section titled `## Invariants added from implemented specs`, in the order it
happened to be written. They are the development rules — median **166** words in the most
recent band, **100%** stating a MUST — and they are what a developer needs when asking
"what do I do here, what must I not do, how do I handle this ambiguity".

| Band | Count | Median words | State a MUST |
|---|---|---|---|
| INV-001..050 | 50 | 15 | 8 |
| INV-051..100 | 50 | 81 | 42 |
| INV-101..150 | 50 | 127 | 50 |
| INV-151..199 | 42 | 166 | 42 |

Three consequences, all of which slow development:

1. **You cannot find the rules on a subject without reading the whole section.** The rules
   governing (say) PDF generation, or MCP calls, or how questions are asked, are scattered
   across 142 chronological entries.
2. **Duplication is structurally invisible.** Two invariants about one subject, written
   three weeks apart, sit forty entries apart. No one can merge what they cannot see side
   by side — which is why a merge pass cannot responsibly come first.
3. **The file reads as undifferentiated bulk**, so the reasonable reaction is to skim it,
   and the reason each rule exists — the recorded defect that makes it stick — goes unread.

## Root cause

The append-only maintenance rule is correct and load-bearing: new invariants go beneath a
marker, IDs are never reused, so every citation stays valid. But append-only ordering was
never paired with any *other* way in. For the first 50 that did not matter — someone
grouped them by hand into sections. Nothing grouped the next 142, and each addition was
individually reasonable, so the drift was never anyone's problem.

## Proposed change

Add a **topical index** at the top of the append section. Do not reorder, renumber, merge,
or reword anything.

1. **An index mapping subject → invariant IDs**, placed directly under
   `## Invariants added from implemented specs`, before the append marker. Roughly:

   ```markdown
   ### Index by subject

   Every invariant below appears in exactly one group. The list stays in append order —
   IDs are permanent addresses (see "Maintaining this file") — so this index, not the
   ordering, is how you find the rules on a subject.

   - **Asking questions and gating** — INV-051, INV-056, …
   - **MCP sourcing and tool contracts** — INV-080, INV-125, INV-132, INV-136, INV-192, …
   - **Deliverables: PDFs, images, artifacts** — INV-048, INV-110, INV-129, INV-142, …
   - **Cross-platform and shell portability** — INV-166, INV-167, INV-175, …
   - **The development record itself** — INV-182, INV-191, …
   ```

   Group names are chosen from what the rules actually cover; the list above is
   illustrative, not prescriptive.

2. **A test that the index cannot go stale.** `tests/` asserts every invariant defined in
   the file appears in **exactly one** index group, and that every ID named in the index
   is defined. Without it the index rots on the first append and becomes worse than no
   index, because it will be trusted.

3. **One line in "Maintaining this file"** telling a future appender to add the new ID to
   its group in the same edit — the test will fail otherwise, so this is a pointer to the
   requirement rather than the requirement itself.

**What this deliberately does not do**, and why:

- **No renumbering.** `INV-NNN` is cited 4,614 times in live files and 753 times in commit
  messages that cannot be edited. Renumbering would silently repoint those at different
  real invariants.
- **No merging, yet.** Merging is the next pass and this one is its prerequisite: grouping
  is what makes duplicate rules visible. Merging before grouping means merging whatever
  happens to be noticed.
- **No trimming.** The word counts are high because each rule carries the defect that
  produced it. That is the part that stops it being re-argued.
- **No change to the first 50.** They are already sectioned and are a different genre
  (bootcamp outcomes, not development rules). The index makes that distinction navigable
  rather than restating it.

## Acceptance criteria

- [ ] `specs/INVARIANTS.md` carries an `### Index by subject` inside
      `## Invariants added from implemented specs`, above the append marker.
- [ ] Every invariant from INV-051 onward appears in **exactly one** group.
- [ ] Every ID named in the index is defined in the file — no forward references, no
      leftovers.
- [ ] No invariant's ID, text, or position changes: a diff shows additions only. Verify by
      extracting the ID sequence before and after and comparing for equality.
- [ ] A test enforces both directions (every invariant indexed; every indexed ID defined)
      and fails if an append skips the index.
- [ ] "Maintaining this file" tells an appender to update the index in the same edit.
- [ ] `python3 .claude/skills/compact-dev-environment/citations.py verify` stays clean.
- [ ] The full suite passes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — the index, and one line in "Maintaining this file".
- `tests/test_invariants_index.py` (new) — the staleness guard.

## Source

- Sweep: `compact-dev-environment`, 2026-07-30 (first pass).
- Baseline: 192 invariants, 21,270 words, 4,614 live citations, 753 commit-message
  citations; 26 invariants already marked superseded (9 of them in INV-001..050).
- Priority: Medium — nothing is wrong; the guidance is unfindable, which costs every
  future task a little and makes the merge pass impossible.
- MCP re-check: n/a — no Senzing fact is involved.
- Related: this is the prerequisite for a later invariant-merge pass.
