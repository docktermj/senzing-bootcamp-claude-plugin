# INV-162 still requires the self-referential count INV-193 forbids as completeness evidence, and neither cites the other

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

**INV-162** (`specs/INVARIANTS.md:335`) requires the metric:

> … and MUST report an embedded-of-referenced count alongside any content-retention figure.

**INV-193** (`:288`), recorded five days later, forbids using exactly that metric as
completeness evidence, and its worked example **is** that metric:

> A count or percentage presented as evidence of **completeness** MUST derive its
> denominator from outside the artifact it measures. … Observed:
> `generate_recap_pdf.py`'s `embedded N of M images` took `M` from the count of `![](…)`
> links in the very recap it was rendering, so a recap that embedded only four of six
> captured tabs reported `embedded 4 of 4 images` — a perfect score against an incomplete
> set …

So one invariant mandates a figure the other says must not be cited as proof of
completeness, and **neither mentions the other** — verified: `INV-193` does not appear in
INV-162's text and `INV-162` does not appear in INV-193's. INV-193 names its neighbours
carefully (*"Distinct from INV-110 … Complements INV-110 and INV-163"*) and omits the one
invariant whose requirement it directly constrains.

**The code is already correct; the ruleset is not.** `generate_recap_pdf.py:808-812`
documents the hazard at the function that produces the string and routes the completeness
question elsewhere:

> ``embedded 4 of 4 images``. Use ``tab_coverage_note`` for the coverage question — it
> takes its denominator from capture's sidecar manifest, which is external.

So this is a documentation-coherence defect, not a live rendering defect. That is precisely
why it matters: the next person to read INV-162 on its own — to port the recap generator to
another language (INV-002/INV-090), or to add a second deliverable with the same reporting
contract — gets the pre-INV-193 requirement with no hint that a later rule constrains it, and
the constraint lives in code comments that a non-Python implementation never reads.

## Root cause

`embedded-image-count-needs-an-external-denominator` (implemented 2026-07-31) fixed the
defect in the generator and generalised the lesson into INV-193, but did not sweep the
existing invariants for the requirement it had just qualified. INV-162's text was left as the
unqualified mandate it had been since 2026-07-28.

This is the same shape INV-184 records against INV-107 — *"INV-107 named two generators; the
property belongs to the pattern"* — and the same shape INV-179 records against INV-115
(*"Extends INV-115, whose two-cause wording this corrects"*). In both of those the newer
invariant **named** the older one. Here it did not, so nothing links them.

## Proposed change

1. **Annotate INV-162** with a dated note that its embedded-of-referenced count is subject
   to INV-193: the count is still required as a *loss* signal (which is INV-162's actual
   purpose — it exists so a dropped asset is visible), but MUST NOT be presented as evidence
   of completeness, and where a completeness claim is needed the denominator comes from
   outside the artifact.
2. **Annotate INV-193** with the reciprocal reference — that it constrains INV-162's count —
   so its "Complements" list is complete and a reader arriving from either direction finds
   the other.
3. **State the division of labour once, in words a non-Python implementer can act on**:
   `embedded N of M` answers *"did anything referenced fail to embed?"*; the external
   manifest answers *"were all captured views referenced in the first place?"*. INV-162's
   note is the right home, since INV-183 requires a rule to be reachable where the artifact
   is produced and the any-language contract is built from the invariants rather than from
   the Python reference.

Both edits are dated in-place clarifications adding cross-references. Neither changes what
any implementation must do — the code already behaves this way — so rule 2 of "Maintaining
this file" is satisfied and no new ID is needed.

⚠️ **Do not resolve this by dropping INV-162's count.** It is the only signal that a
referenced asset failed to embed, and INV-193 does not ask for its removal — only that it not
be cited as completeness. Removing it would reopen the silent-asset-drop defect INV-162 was
written for, where a recap that lost all six screenshots reported 99% content retention and
exit 0.

## Acceptance criteria

- [ ] INV-162 carries a dated note that its embedded-of-referenced count is a loss signal
      subject to INV-193, and MUST NOT be presented as evidence of completeness.
- [ ] INV-193's cross-reference list names INV-162. The reference resolves in both directions.
- [ ] The note states, in language-agnostic terms, which question each count answers — the
      internal count for referenced-but-not-embedded, an external denominator for
      captured-but-not-referenced.
- [ ] Neither invariant's requirement is weakened: the count is still mandatory, and the
      external-denominator rule still applies to any completeness claim.
- [ ] No invariant is deleted or renumbered; both edits are recorded as dated in-place
      clarifications with no meaning change.
- [ ] `generate_recap_pdf.py` is confirmed unchanged in behaviour — this spec edits the
      ruleset only, and the criterion is checked by running the existing recap tests, not by
      inspecting the diff.
- [ ] A test asserts INV-162 and INV-193 reference each other, so the pair cannot drift apart
      again.
- [ ] `python3 .claude/skills/compact-dev-environment/citations.py verify` stays clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-162 (`:335`) and INV-193 (`:288`), cross-reference notes only.
- `tests/` — the reciprocal-reference assertion.

## Source

- **Found by:** maintainer question — *"Are there any invariants in @specs/INVARIANTS.md
  that conflict with each other?"* — 2026-07-31.
- Priority: **Medium.** No live defect: `generate_recap_pdf.py:808-812` already routes the
  completeness question to the external manifest. The risk is a second implementation — in
  another language, or for a future deliverable — reading INV-162 alone and reproducing the
  defect INV-193 was written to prevent.
- MCP re-check: **n/a (no Senzing fact).** Both invariants govern the plugin's own generator
  reporting; no MCP tool owns either claim and none was called.
- Upstream: not applicable.
- Related specs: `specs/embedded-image-count-needs-an-external-denominator.md` (INV-193's
  source — implemented, and correct; the gap is the missing link to INV-162),
  `specs/recap-pdf-images-resolve-against-recap-directory.md` (INV-162's source).
