# Counting the writers of `license_record_limit` is the wrong shape: the count has been wrong twice in one day, while the property it stands in for is stable

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Three shipped files state how many steps write `license_record_limit`, as the premise for an
INV-244 absence branch. **The number has been wrong in every version it has had.**

- **Until 2026-08-28 it read "the only writer … is Module 4's Step 8a".** False: Module 4 itself
  has a *second* write at `module-04-data-collection/SKILL.md:110`, and Module 6's Phase A and
  Phase B absent branches each measure and persist too.
- **`sdk-setups-license-reconciliation-does-not-say-whether-to-persist` corrected it to "exactly
  two writers, and neither creates a value where none existed" (`885a992`).** Also false — and
  contradicted **four lines below itself**. `phaseA-build-loading.md:190` now says *"exactly two
  writers, and neither creates a value where none existed"*, and `:207`, in the same bullet, says
  *"**Persist it** as `license_record_limit` in `config/bootcamp_progress.json`"*. Phase B has the
  identical pair at `:107` and `:111`.

**The real set is five write sites across four steps**, all reached only after a measurement:

| Site | When it writes |
|---|---|
| `module-04-data-collection/SKILL.md:954` | Step 8a's gate, after measuring |
| `module-04-data-collection/SKILL.md:110` | Module 4's own absent branch, after measuring |
| `module-02-sdk-setup/SKILL.md:1043` | Step 5a reconciliation — **replaces** only, never creates |
| `module-06-data-processing/phaseA-build-loading.md:207` | Phase A's absent branch, after measuring |
| `module-06-data-processing/phaseB-load-first-source.md:111` | Phase B's absent branch, after measuring |

⛔ **The conclusion these sentences exist to support is still true, and it never needed a count.**
What makes absence informative is not *how many* steps write the field — it is that **no step
writes it without measuring it**. That property holds across all five sites, held before this
correction, and will hold when a sixth appears. The count is a proxy for it that has to be
re-derived every time the code moves, silently goes stale, and reads authoritative while wrong —
the exact failure mode `production-readiness-audit` names for enumerating invariants.

⚠️ **This is the same defect twice in one day, by the same mechanism.** The first version inherited
a stale count; the second **minted a fresh one** while fixing the first, in a spec whose whole
subject was that the writer set had changed. Replacing one enumeration with another enumeration is
not a fix, and the guard written alongside it (`test_license_limit_has_exactly_two_writers.py`)
pinned the new wrong number into the suite.

## Root cause

The absence branches need a reason, and "only Module 4 writes it" was the shortest true-sounding
one when there was one writer. Every subsequent change added a writer and left the sentence's
*shape* alone, so each correction was a new count rather than a move away from counting.

Nothing forced the shape to change, because a count is checkable-looking: it can be verified once,
at the moment of writing, and then it is a fact in a file with no mechanism behind it. The
property — *written only from a measurement* — is the thing the plugin actually guarantees, and it
is what INV-244's absence rule genuinely rests on.

## Proposed change

1. **Replace the count with the property at all three sites.** State that every step writing
   `license_record_limit` writes only a **measured** value — no step writes it from an assumption,
   a Bootcamper statement, or a default — so absence means *not yet measured* and a present value
   is always a measurement. ⛔ **Do not state how many writers there are, in any of the three
   places.**
2. **Keep SDK setup's replace-only clause**, which is a real distinction and not a count: the
   reconciliation is the one writer that never creates a value, and Module 1's absence reasoning
   uses that specifically.
3. **Rewrite the guard to assert the property, not the number.** `test_license_limit_has_exactly_two_writers.py`
   currently pins "exactly two". It should instead assert that no shipped file states a writer
   count for this field, and that every absence branch states the measured-only property. ⚠️ Rename
   it — a guard named for the wrong claim keeps the wrong claim alive in every future grep.
4. ⛔ **Do not "fix" this by updating the count to five.** That is the third wrong number waiting to
   happen, and the reason this spec exists rather than a one-line edit.

## Acceptance criteria

- [ ] No shipped file states how many steps write `license_record_limit`.
- [ ] All three absence branches state the measured-only property, each keeping its own phrasing of
      the conclusion.
- [ ] SDK setup's replace-only clause survives, and Module 1's absence reasoning still cites it.
- [ ] `test_license_limit_has_exactly_two_writers.py` is renamed and rewritten to assert the
      property and the absence of a count; its old "exactly two" assertions are gone.
- [ ] A test fails if any shipped file states a writer count for this field, deriving its site set
      by scanning (INV-246). Stdlib only, no `plugins/` import (INV-108).
- [ ] Negative-controlled: reintroducing "the only writer", "exactly two writers", or a count of
      five each fail; removing the measured-only property from any absence branch fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — `:312`
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — `:190`
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md` — `:107`
- `tests/test_license_limit_has_exactly_two_writers.py` — rename and rewrite

## Source

- Feedback: none — found by `/production-readiness-audit` on 2026-08-28, cycle 3 of the second
  unattended loop (`Source: self-observed (assistant retrospective)`). Found by tracing the license
  state machine end to end for the third consecutive cycle — the same rotation target that produced
  the previous two findings, revisited precisely because it had produced them.
- Priority: **Medium.** No bootcamper-visible behavior is wrong: every writer does measure first, so
  the conclusion each sentence draws is correct. It is filed at Medium rather than Low because the
  false premise is now **self-contradicted four lines later in two files**, which is the state most
  likely to make a later editor "fix" the wrong half — and because the same defect recurred within a
  day, which is evidence about the shape rather than the instance.
- MCP re-check: **n/a (no Senzing fact).** The subject is which of this plugin's own steps write one
  of its own state fields. `get_capabilities` was called this session to date the run: server
  **1.33.0**, 2026-08-28.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `specs/sdk-setups-license-reconciliation-does-not-say-whether-to-persist.md` (the
  fix that minted the second wrong count, `885a992`);
  `specs/license-record-limit-has-a-detected-only-contract-nothing-enforces.md` (`999bcdd`, where
  the measured-only property was first written down — as a prohibition on *writing*, which is the
  same property this spec asks the absence branches to state);
  `specs/inv244-absent-license-branch-exists-in-module-4-too.md` (the INV-244 lineage)
