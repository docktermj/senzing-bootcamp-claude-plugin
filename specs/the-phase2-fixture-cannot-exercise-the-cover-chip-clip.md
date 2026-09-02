# Phase 2's long-module fixture cannot exercise the cover-chip clip as instructed

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`scaffold_project.py`'s banner tells a phase-2 run how to exercise the recap PDF's
46-character cover-chip clip:

> `docs/progress/recap_checkpoint.md` — an UNFINALIZED block → fold idempotency, run it 3x
> (INV-059); **its '— in progress' heading is the only chip long enough to reach the PDF
> cover's 46-char clip, so FOLD FIRST, then render (INV-048)**

Following that instruction does **not** exercise the clip. Folding places the heading
inside a `<!-- RECAP-CHECKPOINT:START/END -->` fence, and `generate_recap_pdf.py` strips
that fence before module parsing — so the long chip never reaches the cover at all.

A run that follows the instruction sees a PDF with one module chip ("Data collection", 15
characters), reports phase 2 complete, and has tested nothing about the clip.

## Root cause

Measured on 2026-09-02 against the shipped scaffold and generator:

- After `precompact-recap` × 3, `docs/bootcamp_recap.md` carries two `## ` sections:
  `Data collection` and `Data Quality, Mapping, and Transformation — in progress`.
- `pdftotext` on the rendered PDF shows **only** `Data collection` on the cover and in the
  contents. The folded section is absent, and `audit_recap` correctly warns that a module
  "was folded by the durability hooks but never finalized".
- Removing the two fence markers — what module-completion step 2d does — and re-rendering
  puts `Data Quality, Mapping, and Transformation` on the cover, in the contents, and in the
  body. **41 characters, under the 46 clip, rendered whole, no artifact.**

So the generator is correct and the clip behaves; the *instruction* is what cannot reach it.
The scaffold banner predates the fence-stripping behavior the parse path now has
(`_strip_discarded_fences`, and `DISCARDED_FENCES` naming the checkpoint pair).

⚠️ **The fixture is still right; only the recipe is wrong.** An unfinalized block is exactly
what phase 2 needs for the INV-059 idempotency check, which it does exercise correctly.

## Proposed change

Correct the banner line to say the clip needs a **finalized** section, and give the step:
fold three times for INV-059, then remove the fence markers, then render. Or have the
scaffold write a second, already-finalized long-named section so both checks run without a
manual edit — a cleaner fixture, at the cost of one more module in the recap.

⛔ **Do not remove the unfinalized block to make the clip reachable.** It is the only
fixture exercising INV-059 idempotency, which is the more valuable of the two.

## Acceptance criteria

- [ ] Following the scaffold's banner exercises the cover-chip clip, or the banner says
      plainly that it does not and what else is needed.
- [ ] The INV-059 idempotency fixture is unchanged and still exercised.
- [ ] The instruction names the fence-stripping behavior as the reason, so a later editor
      does not "simplify" it back.
- [ ] Verified by rendering and reading the PDF text, not by exit code (INV-129).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/dry-run/scaffold_project.py` — the fixture banner.
- `.claude/skills/dry-run/phase2-hooks-and-scripts.md` — if the recipe moves there.

## Source

- Feedback: none — found by `/dry-run` phase 2 on 2026-09-02
  (`Source: self-observed (assistant retrospective)`), by rendering the PDF and reading its
  text rather than trusting the fixture's stated purpose.
- Priority: Low — maintainer-side tooling; no Bootcamper is affected. It matters because a
  phase-2 run that follows it believes it checked the cover clip and did not, which is the
  guard-certifies-what-it-never-tested shape one level up from a test.
- MCP re-check: n/a (no Senzing fact) — a fixture banner and a Markdown fence.
- Upstream: not applicable.
- Related specs: `a-stray-fence-marker-silently-deletes-finalized-recap-modules` (which
  established the fence-stripping behavior this banner predates).
