# The audit skill's own required reading and every measured baseline in it are stale, so Step 1 sends a run to the six oldest records and past the twenty-five newest

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`production-readiness-audit/SKILL.md` Step 1 instructs:

> **Read the six `deep-dive-audit-*` ledger entries** in `specs/IMPLEMENTED.md`. … **They are the
> only record of what this audit actually finds**, and re-deriving their findings is the most common
> way to waste a run.

There are now **thirty-one** prior runs of this audit in the ledger: the six `deep-dive-audit-*`
entries from 2026-07-26 to -30, and **twenty-five** `production-readiness-audit-*` entries from
2026-08-11 to 2026-08-17. The instruction names the six oldest and calls them the only record.

A run that follows Step 1 literally reads records three-and-a-half weeks old and never opens the most
recent — which, on 2026-08-17, found the reverse-contract defect **specifically produced by an
unattended implement run**, added the `implement-spec` guardrail that a later run is supposed to
follow, and left three drafted invariants awaiting sign-off. That is the single most relevant entry
for any run that follows an unattended session, and Step 1 routes around it.

**Every measured figure in the file is superseded**, all dated 2026-07-31:

| Stated in the skill | Measured 2026-08-21 |
|---|---|
| 162 hard-rule lines, **16** in a section citing no invariant, across 11 files | **347** lines, **1** uncited, across **1** file |
| **24 of 194** invariants enumerate something | **45 of 260** |
| **42** shipped markdown files, **114,576** words | **44** files, **165,299** words |
| **130** repeated passages across **91** file pairs | **157** across **98** |
| "194 invariants, and the per-module outcome blocks…" (Step 2) | **260** invariants |

## Root cause

**The file records measurements as prose and nothing re-measures them.** Each figure was true when
written and is presented as a current baseline — *"Measured 2026-07-31: …"* — which is honest about
its date and still misleading in use, because the surrounding sentences reason from the number ("*24
of 194 invariants enumerate something*" frames enumeration as a minority concern; at 45 of 260 the
proportion has grown by half).

This is **Step 7's own class 4** — *a stale enumeration inside an invariant* — applied to the skill
that hunts it. The file even anticipates the possibility in its closing guardrail: *"Apply the
Goldilocks Principle to this file too. If a future run finds this skill has grown a section nobody
reads, cutting it is in scope."* What it did not anticipate is the counts going stale while the
sections stay useful.

⚠️ **The required-reading instruction is the higher-severity half**, because a wrong count wastes
attention while a wrong reading list changes what a run knows. The six oldest entries describe a
plugin with 194 invariants and no `production-readiness-audit-*` history; the twenty-five newer ones
describe the recurring classes as they are now, including two — the reverse-contract defect after an
unattended run, and the section-scoped blind spot in the `rules` check — that are live today.

## Proposed change

1. **Replace the fixed reading list with a rule that cannot go stale.** Something of the form: *read
   the most recent five audit entries, plus any entry whose findings the generators point at today.*
   ⛔ Do not enumerate the entries by name or count — that is the defect being fixed. Keep the reason
   the instruction exists (re-deriving a fixed defect wastes the run) and drop the fixed set.
2. **Move the measured baselines out of the prose and into the generators.** Each figure exists
   because a run wants to know *whether the number moved*. Have `conformance.py` print the previous
   run's value alongside the current one — from a small committed baseline file it updates — so the
   comparison is mechanical and cannot rot. Failing that, mark every figure in the skill as
   *illustrative of the shape, not a current baseline* and stop reasoning from the proportions.
3. **Fix the two stale invariant counts in Step 2**, which are load-bearing for how a run scopes its
   sweep: "194 invariants" and "24 of 194 … enumerate". At 260, sweeping every invariant one by one is
   a materially larger job than the file implies, and the most recent audit already recorded that it
   *"did not sweep the 257 invariants one by one"* — an honest disclosure that the file's own framing
   makes look like a shortfall rather than a scoping decision.
4. **Say plainly that a full forward sweep is no longer feasible in one run, and how to scope one.**
   The file's Step 2 reads as though every invariant is checked each time. Thirty-one runs of evidence
   say otherwise. Prescribing the scoping — the generators' hits, the diff since the last audit, the
   enumerating subset — turns an implied-but-unmet expectation into a method.
5. **Leave the six `deep-dive-audit-*` entries cited as the origin**, with their findings summarized,
   since they are where the defect classes in Step 7 come from. Their value is historical, not
   current, and the file should say which it is.

⛔ **Change no invariant here.** This spec is about a maintainer-side skill file; `INVARIANTS.md` is
untouched.

## Acceptance criteria

- [ ] Step 1's required reading is expressed as a rule over the most recent entries, naming no fixed
      count or set.
- [ ] No measured figure in the skill is presented as a current baseline unless a generator produces
      it; any figure kept as illustration says so.
- [ ] Step 2's invariant count is either correct or replaced by a reference to the file.
- [ ] The file states how to scope a forward sweep, rather than implying all invariants are checked
      each run.
- [ ] The six `deep-dive-audit-*` entries remain cited, marked as the origin of the Step 7 classes.
- [ ] A guard asserts the skill states no invariant count that disagrees with `INVARIANTS.md`, and no
      audit-entry count that disagrees with the ledger — negative-controlled by reintroducing a stale
      figure.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      maintainer-side markdown; `.claude/` does not ship (`propagate.sh` mirrors `plugins/`,
      `.claude-plugin/`, `docs/` and `README.md` only).

## Affected files

- `.claude/skills/production-readiness-audit/SKILL.md` — Step 1's reading list, Step 2's counts,
  Step 6's size and duplication figures, Step 3's `rules` measurement.
- `.claude/skills/production-readiness-audit/conformance.py` — the previous-value comparison, if
  change 2 is taken mechanically.
- `tests/` — the staleness guard.

## Source

- Audit: `production-readiness-audit`, 2026-08-21 — found in Step 1, by counting the audit entries the
  step told me to read.
- Priority: **Medium.** Nothing bootcamper-facing is wrong. But it degrades every future run of the
  one skill that enforces INV-003 and INV-004, and it does so silently: a run that reads the six
  oldest entries has no way to notice the twenty-five it did not open.
- MCP re-check: n/a (no Senzing fact) — the subject is a maintainer skill file and the repository's
  own counts.
- Upstream: not applicable.
- Related specs: `specs/guards-pinning-a-dated-negative-outlive-it.md`,
  `specs/refresh-reverified-provenance-stamps.md`,
  `specs/scaffold-snippet-count-and-group-list-are-stale.md`

## Deviations from this spec, and why (2026-08-21)

**Two figures in this spec are themselves wrong**, which is the defect it describes occurring in
its own text:

- *"There are now thirty-one prior runs"* → measured from the ledger, **32** across the two
  series (7 `deep-dive-audit-*` + 25 `production-readiness-audit-*`, the latter running
  2026-08-11 to 2026-08-21 inclusive).
- *"the six `deep-dive-audit-*` entries"* → there are **seven**. The skill's header list omitted
  `deep-dive-audit-2026-07-29-minor-fixes`, so the required-reading list was not merely stale, it
  was **incomplete on the day it was written** and no reader could have known. That strengthens
  change 1 rather than weakening it: a fixed set in prose is unverifiable by construction.

**Change 2 was implemented as the stated fallback, not the preferred mechanism.** The spec
prefers having `conformance.py` print the previous run's value from a committed baseline file.
Instead every figure was **removed**, with each scan's own output made the authority and the
surrounding sentences rewritten to stop reasoning from proportions. Reasons, recorded so the
choice can be revisited:

- A baseline file is a second source of truth for numbers the scans already compute, and it goes
  stale the moment a run forgets to update it — reintroducing the class one level down.
- Removal makes the staleness **unrepresentable** rather than **detected**, which is the stronger
  fix for a defect whose whole character is reading authoritative while wrong.
- The guard (`tests/test_audit_skill_states_no_stale_count.py`) asserts *agreement*, not absence,
  so a future run may state a count if it is correct. Nothing is foreclosed.

The `conformance.py rules` baseline named in change 2 was already removed while implementing
`conformance-rules-cannot-see-a-new-rule-beside-an-old-citation`; the rest went here.
