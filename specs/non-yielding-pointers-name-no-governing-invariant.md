# The non-yielding-run pointers name no governing invariant, and a test forbids adding one

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`results-presentation-turns-end-with-zero-questions` (implemented 2026-08-14, `4e90e66`) added a
hard rule at three steps, one per site where a turn had ended with zero 👉 questions:

```
module-06-data-processing/phaseC-multi-source.md:208   ⛔ **Steps 17–20 ask nothing, so this turn does not end here**
module-06-data-processing/phaseD-validation.md:96      ⛔ **Steps 21–24 ask nothing, so this turn does not end here**
module-07-query-visualize-discover/phase1-query-visualize.md  ⛔ **Steps 2–3a ask nothing, …**
```

Each cross-references `ground-rules.md` by **prose title** — *"A results presentation is not a turn
ending"* — and names **no invariant**, although the behavior is governed by **INV-225** (a step
with no 👉 is non-yielding and must not end a turn) and **INV-005** (exactly one 👉 per yielding turn).

`conformance.py rules` flags `phaseD-validation.md:96` as one of only **2** hard-rule lines in the
whole plugin whose section cites no invariant. The other two sites are the same defect and escaped
the scan only by accident: `phaseC`'s enclosing section happens to cite INV-151 for an unrelated
redo rule, and `phase1`'s cites others nearby. So the scan under-reports the class by two thirds,
and the real count is three.

INV-183 requires a rule binding a step to be reachable **at** that step. A ⛔ with no ID is one a
later editor cannot look up — and these three are precisely the rules a later editor is most likely
to read as local advice and tidy away, since each looks like a note about one phase.

## Root cause

**A guard I wrote forbids the fix.** `tests/test_ground_rules_nonyielding_presentation.py:143-149`:

```python
def test_no_pointer_restates_the_rule_instead_of_citing_it(self):
    """Restating drifts. The spec asks for a one-line cross-reference, not a copy."""
    for path, _ in SITES:
        text = squash(path)
        self.assertNotIn("property of the **step**", text)
        self.assertNotIn("INV-225", text)
```

The spec asked for "one line each, cross-referencing the ground rule rather than restating it", and
the implementation collapsed two different things into one assertion:

- **restating the rule** — copying the reasoning into three files, which does drift, and which the
  first assertion correctly forbids; and
- **citing the invariant ID** — three characters plus a number, which cannot drift, and which
  INV-183 requires.

The second assertion bans the citation as though it were the restatement. It is also scoped to the
**whole file**, not to the pointer, so it forbids `INV-225` appearing anywhere in any of the three
files for any reason at all.

This is the audit's defect class 3 inverted: not a guard narrower than the invariant it enforces,
but a guard that **contradicts a different invariant** while looking like it enforces the spec.

## Proposed change

1. Add the governing citation to all three pointers — `(INV-225)` for the non-yielding contract,
   alongside the existing prose cross-reference to `ground-rules.md`, which stays: the title tells
   the reader *what* the rule says, the ID lets them look it up.
2. Replace the over-broad assertion with one that forbids the **restatement** and requires the
   **citation** — the two are separable and the test should say so. Keep the first assertion
   (`"property of the **step**"`) unchanged: that is the real anti-drift check.
3. Note in the test's docstring why the distinction matters, so the next editor does not re-collapse
   them.

## Acceptance criteria

- [ ] All three pointers cite INV-225 and keep their prose cross-reference to `ground-rules.md`.
- [ ] No pointer restates the rule's reasoning; the existing anti-restatement assertion still passes.
- [ ] The test requires the citation rather than forbidding it, and fails if any one pointer drops it.
- [ ] `conformance.py rules` no longer reports `phaseD-validation.md:96`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md` — pointer at `:208`.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — pointer at `:96`.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — the step-3a pointer.
- `tests/test_ground_rules_nonyielding_presentation.py` — `:143-149`, invert the citation assertion.

## Source

- Feedback: `production-readiness-audit-2026-08-14b` (self-observed; `conformance.py rules` flagged
  one of the three, and the reverse sweep found the other two)
- Priority: Medium
- MCP re-check: **n/a (no Senzing fact).** A conversational-protocol citation gap, internal to the
  plugin's own ruleset.
- Upstream: not applicable
- Related specs: `specs/results-presentation-turns-end-with-zero-questions.md` (the implementation
  that introduced both the pointers and the assertion forbidding their citation)

## Deviations from this spec, and why (2026-08-14)

Implemented as proposed; all five criteria hold. Two notes.

1. **The assertion was split, not deleted.** The spec asks to "replace the over-broad assertion with
   one that forbids the **restatement** and requires the **citation**". Both now exist as separate
   tests — `test_no_pointer_restates_the_rule` (the real anti-drift check, unchanged in substance)
   and `test_every_pointer_cites_the_invariant_that_governs_it` — plus a third,
   `test_the_pointers_keep_the_prose_cross_reference_too`, because the title and the ID do different
   jobs: the title tells the reader *what* the rule says, the ID lets them look it up. A fix that
   swapped one for the other would have satisfied INV-183 and lost the readable half. The mutation
   that removes the prose title fails **2** tests, which is what pins that.

2. **The docstring records why the two were ever conflated**, since the next editor's most likely
   move is to re-collapse them. The original assertion read as a faithful reading of the spec's
   "cross-reference rather than restate" — it is only wrong once you notice that an invariant ID
   cannot drift, which is precisely the property that makes INV-183 cheap to satisfy.

**Verified against the detector that found it:** `conformance.py rules` reported
`phaseD-validation.md:96` as one of two hard-rule lines plugin-wide whose section cited no
invariant. It now reports **1**, and the remaining hit (`phaseB-load-first-source.md:23`) is the
local-instruction case this spec's own audit classified as out of scope, whose durable candidate is
recorded as a stop-marker in `specs/phase-a-preload-test-load-precedes-its-prerequisites.md`.

**Mutation-tested: 4 mutations, all caught** — dropping the ID from either of two pointers, adding
the rule's reasoning back into a third, and replacing the prose cross-reference with the bare ID.
Files restored from in-script copies and verified equal.
