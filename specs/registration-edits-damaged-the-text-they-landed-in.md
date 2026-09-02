# Registration edits damaged the text they landed in

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Three of the twenty-four citation insertions made on 2026-09-02 while registering
INV-285–INV-295 broke the structure of the prose they were inserted into. Each was made by
anchoring on a prefix and appending, without accounting for what followed the anchor.

Nothing is factually wrong; the damage is structural, and two of the three change what a
rule appears to govern.

## Root cause

1. **`module-03b-truthset-visualization/phase1-visualization.md:208-219`** — the INV-289
   scope note was inserted as a nested bullet after *"…so it never queries the database
   directly."*, which was **mid-sentence-group**. The parent bullet's remaining sentence —
   *"Get the exact SDK method, flag, and attribute names from the Senzing MCP tools
   (`sdk_guide` / …), never from training data (INV-080)"* — now begins inside the nested
   bullet at 4-space indent (line 218, **163 characters**) and continues at the parent's
   2-space indent (line 219). One sentence split across two list levels, and an **INV-080**
   sourcing rule now reads as part of a Truth-Set-scope note it has nothing to do with.

2. **`module-03b-truthset-visualization/phase1-visualization.md`, the INV-292 bullets** —
   the two inserted `- ⛔` sub-bullets are followed by the pre-existing
   *"⚠️ **The two responses use the name `download_url` for different hosts**"* continuation
   at the same indent, so that note now attaches to the User-Agent sub-bullet rather than
   to the parent fetch bullet it explains.

3. **`graduation/SKILL.md`** — the INV-287 note ran into the pre-existing *"Give the
   reason, because it is what makes the item non-obvious: …"* with no line break, producing
   a **159-character** line that joins two separate thoughts.

The class: **an insertion anchored on a prefix, appended without reading the following
line.** A `.replace(anchor, anchor + new)` cannot see what it now sits in front of, and the
suite has no line-length or list-structure check on shipped markdown, so all three passed
3,989 green tests.

## Proposed change

1. Re-wrap all three so the inserted note is a complete block and the text it landed in
   front of returns to the bullet it belongs to.
2. In (1), the INV-080 sentence goes back to the **parent** bullet, before the nested note.
3. In (2), move the `download_url`-hosts ⚠️ above the inserted sub-bullets, so it stays
   attached to the fetch instruction.
4. Consider a guard: no shipped markdown line exceeds a stated width. The repo wraps at
   ~100; two lines at 159 and 163 are the only ones the diff added, so the rule is already
   observed everywhere else and a guard would be cheap. ⚠️ Decide whether this is worth a
   test or is style — it caught nothing a reader would call a defect until an insertion
   split a sentence across list levels.

## Acceptance criteria

- [ ] The INV-080 sourcing sentence is part of the parent bullet, not the INV-289 note.
- [ ] The `download_url`-hosts note attaches to the fetch bullet, not the User-Agent one.
- [ ] No line the 2026-09-02 registrations added to shipped markdown exceeds the width the
      surrounding file uses.
- [ ] Rendered structure is checked, not just line length — a nested bullet followed by a
      dedented continuation is the defect, and a width check alone would miss (2).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md`
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md`

## Source

- Feedback: none — found by `production-readiness-audit` on 2026-09-02, auditing the same
  day's invariant registrations (`Source: self-observed (assistant retrospective)`).
- Priority: Medium — no rule is wrong, but two rules now appear to govern text they do not,
  and mis-attribution is the INV-076/INV-077 defect class this repo has paid for twice.
- MCP re-check: n/a (no Senzing fact) — markdown structure in shipped guidance.
- Upstream: not applicable.
- Related specs: none.
