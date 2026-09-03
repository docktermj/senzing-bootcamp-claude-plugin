# INV-300 is drafted from the pointer side and is now cited at owner-side declarations

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-300 governs a single-statement ownership claim, and its obligations are written for the
site that **points**:

> …that claim MUST name the **owning file or step** and the invariant that makes
> single-statement authoritative, and **the pointing site** MUST carry no second copy of the
> rule it points at.

The discipline has two sides, and only one is described. The other is the **owner**, which
declares itself:

- `module-02-sdk-setup/SKILL.md:718` — *"This is the canonical statement of the rule; other
  modules link here rather than restating it (INV-300)."*
- `module-04-data-collection/SKILL.md:488` — *"**This is the canonical statement; do not restate
  it elsewhere (INV-300).**"*
- `module-04-data-collection/SKILL.md:1116` — *"…is the canonical statement; do not restate it
  here (INV-300)."*

At those three sites the citation was added by the 2026-09-03 sweep, and INV-300's obligations
read oddly or vacuously: *"name the owning file or step"* is trivially satisfied because the
owner is the passage itself, and *"carry no second copy of the rule it points at"* has no
referent, since an owner points nowhere.

**Measured while auditing:** of **42** ownership claims in shipped markdown, **41** name an
owner in their passage. The single exception is `module-04-data-collection/SKILL.md:488` — an
owner-side declaration, i.e. the exception is the wording gap rather than a violation.

## Root cause

The invariant was drafted from the finding, and the finding was about pointer sites: twenty-seven
of them cited no invariant. The owner side never came up, because an owner-side declaration
carries no citation problem — it is not pointing anywhere. The 2026-09-03 sweep then derived its
site set **by scanning** the ownership vocabulary (INV-246, correctly), and *"This is the
canonical statement"* is in that vocabulary — so three owner-side sites received a citation for
an invariant whose obligations do not describe them.

⚠️ **This is the "amend before minting" class caught one step late.** On 2026-09-02 the
maintainer scoped INV-291 and INV-295 before minting, because each bound a class wider than its
evidence and would have made correct sites read as violations. Here the mismatch is the mirror:
the invariant is *narrower in description* than the class its own vocabulary selects.

## Proposed change

1. **Append a dated clarification to INV-300** distinguishing the two sides, changing no rule:
   - **The pointer side** — what the current text describes: name the owner, cite the
     authority, carry no second copy.
   - **The owner side** — a passage declaring *"this is the canonical statement"* MUST carry the
     rule in full, and MUST cite the same authority so a reader arriving at either side can
     look the discipline up. It names no owner because it *is* the owner.

   ⛔ Append-only: `INVARIANTS.md` rule 2 forbids changing an invariant's meaning in place, and
   this note adds a distinction the rule already implied rather than a new requirement.
2. **Keep all three owner-side citations.** Removing them would leave the two halves of one
   discipline discoverable from only one side, which is the drift the invariant exists to
   prevent.
3. **Give the guard the distinction**, so the owner-naming assertion proposed in
   `specs/the-inv-300-guard-checks-one-of-the-invariants-three-obligations.md` applies to
   pointer sites and exempts owner-side declarations **by their own wording** (a
   self-declaration of canonical status), not by a hardcoded list of the three sites known
   today (INV-246).

## Acceptance criteria

- [ ] INV-300 carries a dated note distinguishing pointer-side from owner-side obligations; the
      rule is unchanged, not deleted, not renumbered.
- [ ] All three owner-side declarations keep their INV-300 citation.
- [ ] The owner-side exemption in the guard is derived from the declaration's wording, not from
      a list of paths, and is negative-controlled by planting a pointer site with no owner.
- [ ] The three sites are named in the ledger entry so a later audit does not re-derive whether
      they were a mis-citation.
- [ ] Full suite green; `citations.py verify` clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-300's dated two-sides note
- `tests/test_a_single_statement_claim_names_its_authority.py` — the owner-side exemption, once
  the sibling spec adds the owner assertion

## Source

- Feedback: none — self-observed during `production-readiness-audit-2026-09-03f`
  (`Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: **n/a (no Senzing fact).** The subject is the wording of one of the plugin's own
  invariants (INV-080).
- Upstream: not applicable
- Related specs: `specs/the-inv-300-guard-checks-one-of-the-invariants-three-obligations.md`,
  `specs/the-no-fork-discipline-is-registered-only-inside-inv-183s-artifact-scope.md`

## Invariants introduced

- **None.** This spec amends INV-300 rather than registering a new invariant: the two-sides
  note was approved by the maintainer on 2026-09-03 and appended to INV-300 in place, changing
  no obligation on the pointing side.

## Deviations from this spec, and why (2026-09-03)

- **Proposed change 3 — the wording-based owner-side exemption — had already shipped**, in
  `the-inv-300-guard-checks-one-of-the-invariants-three-obligations` (`1db616d`). It could not
  wait for this spec: that spec's owner-naming assertion would have failed on
  `module-04-data-collection/SKILL.md:488` and left the suite red between two commits. So this
  spec's contribution to the guard is the **other** half — that an owner-side declaration owes
  the citation — which the approved note added and which nothing asserted before.
- **The new clause is asserted in halves, deliberately.** *Cite this invariant* is checked;
  *carry the rule in full* is not, and the note says so, for the same reason as obligation (c):
  judging whether a passage states a rule **completely** is semantic. Shipping a guard that
  claimed the whole clause would be the defect the sibling spec exists to record.
- ⚠️ **A line-level grep said only two of the three owner-side declarations cite INV-300.**
  That was the grep's unit, not the truth: `module-04:488`'s citation sits on line 489, where
  the sweep moved it so it would not break the exact phrase `test_cord_fetch_integrity` and
  `test_sampling_and_validation_routing` pin. Verified per site over the passage before
  believing the count — the same line-versus-passage error that produced a retracted audit
  finding on 2026-09-03.
