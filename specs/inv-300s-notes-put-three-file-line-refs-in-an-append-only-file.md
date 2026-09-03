# INV-300's notes put three file:line refs in an append-only file and made it 59% notes

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two notes were appended to INV-300 on 2026-09-03, hours after it was registered. Measured
after them:

- **INV-300 is 4,789 characters — the second-longest of 299 invariants**, against a median of
  1,099. Only INV-244 is longer, and INV-244 is the entry this same session had to correct for
  a premise that had gone stale inside it.
- **59% of the entry is notes appended after the rule.** The governing sentence plus its
  `Source:` clause is 1,979 characters; the two notes are 2,810.
- **INV-300 has joined the enumeration surface** — `conformance.py enumerations` went **47 →
  48 of 299** and reports it as `[closed list, comma series]`. The list it found is three
  `file:line` references the two-sides note names:
  `module-02-sdk-setup/SKILL.md:718`, `module-04-data-collection/SKILL.md:488` and `:1116`.

⛔ **Line numbers are the most fragile enumeration this repo can write, and `INVARIANTS.md` is
append-only.** Every edit above those lines moves them, nothing recomputes them, and the
correction mechanism for a wrong invariant is a *further* note — so a stale `file:line` in a
ruleset entry cannot be quietly repaired, only annotated. The plugin already learned this
shape twice: INV-244's writer count (three wrong versions, then a `SUPERSEDED-COUNT:` note)
and INV-107's two-generator list (superseded in practice, kept with a pointer note).

⚠️ **This is not an argument for deleting the notes.** Both record something a reader needs:
what the enforcer does and does not establish, and that the discipline has an owner side. The
defect is the **form** — line numbers where a section name would do, and length that pushes the
rule's own sentence away from where a reader lands.

## Root cause

Both notes were written to be *complete*, in a file whose convention rewards narrative, and
neither was measured against the entry afterwards. The `file:line` references came from the
audit that produced them, where line numbers were the right currency; they were carried into
the ruleset unchanged, where they are not — a ledger entry is dated and frozen, an invariant is
consulted indefinitely.

The enumeration scan is what makes this objective rather than a matter of taste: the repo's own
tooling now classes INV-300 as stale-risk, and that scan exists because *"an invariant stating a
property survives change; one listing members breaks the moment a member moves, and it breaks
silently because the list still reads authoritative."*

## Proposed change

1. **Replace the three `file:line` references with file plus section names** — the same
   identification a reader can still follow after any edit (e.g. *"module-02's env-script
   path-resolution rule"*, *"module-04's overlap-preserving sampling rule and its Step-8b
   sample gate"*). Verify afterwards that `enumerations` no longer reports INV-300, or that
   what it reports is a property rather than a member list.
2. **Move the enforcer-coverage detail to the guard, keep the verdict in the invariant.** The
   per-obligation table already lives in
   `tests/test_a_single_statement_claim_names_its_authority.py`'s docstring; the invariant needs
   only the conclusion — which obligations are asserted, which is not assertable, and why —
   with the measurement kept where it was taken (the ledger entry). ⛔ **Do not cut the reason
   clauses**: this is a move, not a deletion, and the audit skill forbids trading rationale for
   length.
3. **State the target as findability, not brevity.** The test is whether a reader arriving at
   INV-300 reaches the rule before the notes, which is the Goldilocks principle the audit skill
   states: *"the target is not shorter — it is findable at the moment of use."*
4. ⚠️ **Do not extend this to INV-244 or the other long entries** unless a run measures the same
   problem there. This spec is scoped to the entry two notes made second-longest in one day.

## Acceptance criteria

- [ ] INV-300 names no `file:line` reference; the three sites are identified by file and
      section in a way that survives an edit above them.
- [ ] `conformance.py enumerations` no longer reports INV-300, or reports it for something that
      is genuinely a closed set of the rule's own vocabulary rather than a site list.
- [ ] The rule's own statement is reachable before the appended notes; the entry is materially
      shorter than 4,789 characters while every reason clause survives somewhere — the guard's
      docstring or the ledger entry — with a pointer from the invariant.
- [ ] Nothing is deleted from `specs/INVARIANTS.md`'s history: this is a rewording of notes
      added the same day, not a change to the rule, and the two `Source:` attributions remain.
- [ ] Full suite green; `citations.py verify` clean; enforcer pairs unchanged at 114.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-300's two appended notes
- `tests/test_a_single_statement_claim_names_its_authority.py` — receives any coverage detail
  moved out of the invariant

## Source

- Feedback: none — self-observed during `production-readiness-audit-2026-09-03g`, cycle 1 of the
  second unattended loop (`Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: **n/a (no Senzing fact).** The subject is the length and form of one of the
  plugin's own invariant entries (INV-080).
- Upstream: not applicable
- Related specs: `specs/inv-244-still-carries-the-writer-count-its-own-guard-rejects.md`,
  `specs/the-inv-300-guard-checks-one-of-the-invariants-three-obligations.md`,
  `specs/inv-300-is-drafted-from-the-pointer-side-and-cited-at-owner-side-declarations.md`
