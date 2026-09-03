# The INV-300 guard checks one of the invariant's three obligations and does not say so

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-300 states **three** obligations:

> …that claim MUST **(a)** name the owning file or step **and (b)** the invariant that makes
> single-statement authoritative, and **(c)** the pointing site MUST carry no second copy of
> the rule it points at.

`tests/test_a_single_statement_claim_names_its_authority.py` — which INV-300 names in its own
`Enforced by` clause — checks **(b) only**. Its four tests are a corpus floor, an
exemption-freshness check, "an invariant is cited in the passage", and "INV-300 is cited in at
least 15 shipped files". Nothing looks for the owner, and nothing looks for a second copy.

⛔ **The `Enforced by` clause is what makes this a defect rather than a gap.** A reader — or a
later audit — takes *"Enforced by `tests/…py`"* as meaning the invariant is guarded, and
`tests/test_invariant_enforcer_citations.py` confirms only that the named test **cites the
invariant back**, never that it asserts what the invariant says. This is Step 7 class 3, *a
guard narrower than the invariant it claims to enforce* — the class that produced the INV-146
finding, where a regex requiring `"most"|"best"` after `2-3` passed while three violations
shipped.

## Root cause

The guard was written from the finding rather than from the invariant. The finding was
*"twenty-seven claims cite no invariant"*, so the guard checks citations; obligations (a) and
(c) entered the invariant's wording during drafting and no one went back to the guard.

**Obligation (a) is mechanically checkable, and was measured on 2026-09-03:** of the **42**
ownership claims in shipped markdown, **41** name an owner in their passage — a file path, a
quoted section title, or a step reference. The one that does not is
`module-04-data-collection/SKILL.md:488`, and it is not a violation: it is an **owner-side**
declaration (*"This is the canonical statement"*), where the owner is the passage itself. That
distinction is its own finding — see
`specs/inv-300-is-drafted-from-the-pointer-side-and-cited-at-owner-side-declarations.md`.

**Obligation (c) is not checkable in general, and the invariant says why:** the duplication
scan reports *exact* repeats, so a copy that has drifted is precisely what it cannot see.
Detecting "carries a second copy of the rule it points at" needs a semantic comparison between
a pointer site and its target.

## Proposed change

1. **Add the owner-naming assertion** — obligation (a), for pointer sites: the passage must
   name a file, a quoted section, or a step. Measured baseline: 41 of 42 pass, the exception
   being the owner-side case, which the sibling spec settles.
2. **State the coverage in the guard's docstring, per obligation**, so a reader sees which of
   the three it holds: (a) asserted for pointer sites, (b) asserted, (c) **not asserted, and
   not assertable** — with the invariant's own reason quoted.
3. **Say the same thing in INV-300's `Enforced by` clause**, as a dated note: the named test
   asserts the citation and the owner reference, and no test establishes the no-second-copy
   clause, which needs a person reading a pointer against its target. ⛔ `INVARIANTS.md` is
   append-only — this is a clarifying note, never a rewrite of the rule.
4. ⛔ **Do not "fix" (c) with a similarity scan.** The plugin already measured that path on
   2026-09-03: a near-duplicate scan over hard-rule lines reports 18 pairs at a 0.82 floor of
   which 15 are phase-header boilerplate, and the disjoint-citation variant that *was* kept
   catches a restated rule only when the wording still matches. A guard reporting middling hits
   trains its reader to skip it.

## Acceptance criteria

- [ ] The guard asserts the owner-naming obligation for pointer sites and is negative-controlled
      by stripping the owner reference from one passage.
- [ ] The guard's docstring maps each of INV-300's three obligations to *asserted* or *not
      asserted*, and says why (c) cannot be.
- [ ] INV-300 carries a dated note saying what its enforcer does and does not establish; the
      rule itself is unchanged, and the invariant is neither deleted nor renumbered.
- [ ] `tests/test_invariant_enforcer_citations.py` stays green with `EXPECTED_PAIRS` re-derived
      by running its extractor, never incremented.
- [ ] Full suite green; `citations.py verify` clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `tests/test_a_single_statement_claim_names_its_authority.py` — the owner assertion and the
  per-obligation coverage statement
- `specs/INVARIANTS.md` — INV-300's dated `Enforced by` note

## Source

- Feedback: none — self-observed during `production-readiness-audit-2026-09-03f`
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: **n/a (no Senzing fact).** The subject is what one of the plugin's own guards
  asserts about one of its own invariants (INV-080).
- Upstream: not applicable
- Related specs: `specs/the-no-fork-discipline-is-registered-only-inside-inv-183s-artifact-scope.md`,
  `specs/inv-300-is-drafted-from-the-pointer-side-and-cited-at-owner-side-declarations.md`,
  `specs/a-check-whose-scope-is-wider-than-its-claim-passes-without-establishing-it.md`
