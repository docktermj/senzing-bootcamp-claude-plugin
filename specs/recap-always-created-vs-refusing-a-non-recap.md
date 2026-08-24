# INV-048 says the recap PDF is *always* created; INV-110 requires writing no file on structural mismatch

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

**INV-048** (`specs/INVARIANTS.md:149`) is unconditional, and the file's preamble says
invariants are things that must **ALWAYS** be true:

> A recap PDF, `docs/bootcamp_recap.pdf`, is **always** created.

**INV-110** (`:386`) requires the opposite in one case:

> … on structural mismatch or retention below its stated minimum — write no output file,
> emit no success line, and exit non-zero.

INV-110 reconciles the *retention* half itself — *"A recognizable-but-incomplete input stays
non-blocking (warn, render, exit 0), so an imperfect recap still produces its PDF
(INV-066)"* — but says nothing about the **structural mismatch** half, which is the case
where no file is written. Neither invariant cites the other.

**The shipped behavior is INV-110's.** `generate_recap_pdf.py:3264` comments *"Audit BEFORE
rendering. A structurally wrong input must never reach the …"*, and
`tests/test_recap_pdf_guard.py:130` (`test_names_the_structural_mismatch`) pins it. So
INV-048's "always" is the text that does not match the code.

**Why the ambiguity is load-bearing rather than cosmetic.** INV-048 is cited elsewhere as a
*non-blocking* guarantee, not merely an existence one — INV-173 reads it that way (*"MUST NOT
block the flow (INV-048)"*), and so do INV-129, INV-157 and INV-163. A reader who takes
"always created" at face value has two wrong options: conclude the generator has a defect
because a malformed input produced no PDF, or "fix" INV-110's refusal so a structurally wrong
document renders anyway — which would ship a keepsake built from something that is not a
recap, the exact outcome INV-110 exists to prevent.

## Root cause

INV-048 is an original INV-001–050 bootcamp *outcome*: it states what a completed bootcamp
produces, and "always" was written to forbid the PDF being skipped or made optional. INV-110
is a later *generator contract*: it states how the tool must behave on bad input. The two
were never reconciled because they are about different subjects — the flow's deliverable
versus the tool's failure mode — and nothing in either says so.

The boundary is real but unwritten: INV-110's refusal case is reached only when the input is
**not a recap**, which in the bootcamp flow cannot happen, because graduation writes the
recap before rendering it. So the invariants conflict on a case the flow does not produce —
which is exactly why it survived: no run ever exercised the contradiction.

## Proposed change

1. **Annotate INV-048** with a dated note giving the boundary: the guarantee is that the
   bootcamp flow always produces the recap PDF and that its production is never optional,
   skipped, or gated; it is **not** a requirement that the generator emit a file for input
   that is not a recap. Cite INV-110 for that case.
2. **Annotate INV-110** reciprocally: name INV-048 and state that the structural-mismatch
   refusal is the one case where INV-048's "always" does not apply, and why — a PDF built
   from a non-recap is worse than no PDF, and the flow cannot reach this case because
   graduation authors the recap first.
3. **Keep both requirements intact.** INV-048 still forbids the recap being optional and
   still carries its non-blocking reading; INV-110 still refuses a structurally wrong input.
   Only the boundary between them becomes explicit.

Both are dated in-place clarifications recording a boundary the code has always implemented,
so no meaning changes and no new ID is needed under rule 2.

⚠️ **Do not resolve this by weakening INV-110 so that something always renders.** That
inverts the defect: INV-110's own text records 61 raw pipe lines and a 99%-retention figure
reaching a Bootcamper's PDF behind exit 0, and the structural gate is what stops a keepsake
being generated from a document that is not a recap.

⚠️ **Do not resolve it by deleting the word "always" from INV-048.** "Always" is doing real
work — it is what makes the recap non-optional and is relied on by INV-129, INV-157, INV-163
and INV-173. Scope it, do not remove it.

## Acceptance criteria

- [ ] INV-048 carries a dated note scoping "always" to the bootcamp flow's production of the
      recap, and pointing at INV-110 for the not-a-recap input case.
- [ ] INV-110 names INV-048 and states that its structural-mismatch refusal is the sole
      exception to it, with the reason.
- [ ] The cross-reference resolves in both directions.
- [ ] INV-048's non-blocking reading is preserved — the invariants that rely on it
      (INV-129, INV-157, INV-163, INV-173) still resolve to a true statement. Each is checked
      by opening it, not inferred (INV-182).
- [ ] The retention half is untouched: a recognizable-but-incomplete recap still warns,
      renders, and exits 0.
- [ ] No invariant is deleted or renumbered; both edits are dated in-place clarifications.
- [ ] `tests/test_recap_pdf_guard.py` still passes unchanged — this spec edits the ruleset,
      not the generator, and the criterion is proven by running the suite.
- [ ] `python3 .claude/skills/compact-dev-environment/citations.py verify` stays clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-048 (`:149`) and INV-110 (`:386`), boundary notes only.

## Source

- **Found by:** maintainer question — *"Are there any invariants in @specs/INVARIANTS.md
  that conflict with each other?"* — 2026-07-31.
- Priority: **Low-Medium.** No live defect and the flow cannot reach the contradictory case,
  but INV-048 is one of the most-cited invariants in the ruleset and its unqualified "always"
  invites a reader to weaken the guard that INV-110 exists to hold.
- MCP re-check: **n/a (no Senzing fact).** Both invariants govern the plugin's own recap
  generator; no MCP tool owns either claim and none was called.
- Upstream: not applicable.
- Related specs: `specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (INV-110/INV-111's
  source), `specs/drop-trophy-wording.md` (the last in-place clarification of INV-048).
