# Data collection's generated-scenario path is entirely non-yielding and unmarked

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

On the **generated-scenario path** — the one a Bootcamper who accepted the Business Case Offer in
Discover the Business Problem takes — Data collection contains **no 👉 question at all** until its
Step 9 transition question. Every step in between is non-yielding:

| Step | Why it asks nothing on this path |
|---|---|
| 1 Review sources | statement |
| 2 Collect the data | the marker/provenance guard **skips the provision question** and generates the files |
| 3 Verify data received | statement |
| 4 Document locations | statement (checklist is created without asking — INV-012) |
| 5 Sensitive data | statement |
| 6 Sample files | not triggered below the effective limit |
| 7 Verify quality | reads the registry |
| 8 Update tracking | statement |
| 8a License gate | **volume-skip** when the collected total is within the limit — "the common case", per the step's own words |
| 8b Load-time warning | says nothing when the loadable total is below the threshold |

So a faithful walk generates three files, validates them, writes four documents and a `.gitignore`,
and runs two gate checks inside the single turn that ends on Step 9's question.

That is correct behaviour under INV-225. The problem is that **nothing in this module says so**,
while the module the plugin holds up as the example of this shape says it twice.
`ground-rules.md` → the 👉 protocol names the shape and its instances explicitly:

> **A run of them is the same case, not a worse one.** Non-yielding steps often come several in a
> row — Module 1 Phase 1's 4a/4b/5/5a, SDK setup's 1b/4/5/6, and **the whole of System
> verification**, which contains exactly one 👉 …

Data collection's generated-scenario path is a **fourth instance of that same run** and is not
named there or marked locally. `module-03-system-verification/SKILL.md` carries a ⚠️ ("This module
has exactly one 👉 question — the module-transition question at the end of
`phase2-report-close.md`. Every other step is **non-yielding** …") and
`phase1-verification.md` opens with a ⛔ saying every step in the phase is non-yielding. Data
collection carries neither, so a guide reading `module-04-data-collection/SKILL.md` step by step
has nothing local telling it that Step 3 must not end a turn.

**Observed live, phase-3 dry run, 2026-08-14.** The walk reached Data collection with a
bootcamp-generated three-source scenario (`provenance: synthesized`), 36 collected records against
the 500-record evaluation limit, and `database_type: sqlite`. Steps 1 through 8b produced zero 👉
questions, exactly as the file requires. The guard worked; the marking is what is missing.

### Why this is worth fixing rather than leaving to the general rule

INV-225 is general and does cover it, so this is a **documentation gap, not a contradiction** —
and that is precisely the failure mode INV-225's own spec described: two rules in separate sections
is how the non-yielding case became unfollowable in the first place. A guide that has just been
told "Execute every numbered step one at a time, in order. Never skip, combine, or abbreviate a
step containing a 👉 question" (this module's header) and then meets nine steps with no question
has to reach for a rule in another file to know what to do. System verification was given a local
marking for exactly that reason; the same reasoning applies here and the module is otherwise
identical in shape.

The conditional nature is the only real difference, and it cuts the other way: System verification
is *always* non-yielding, so a reader discovers it once. Data collection is non-yielding **only on
the generated-scenario path**, which means a reader who learned the module on the
bring-your-own-data path (where Step 2 does ask) will meet the run of nine unexpectedly.

## Root cause

`plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — the module header states the
one-step-at-a-time rule and the ⛔ gate precedence, but never states which of its steps ask
anything, and never names the generated-scenario path as the non-yielding run it is. The step
bodies that *become* non-yielding (2's guard, 8a's volume-skip, 8b's silence) each describe their
own branch correctly in isolation; nothing composes them.

`ground-rules.md`'s instance list is also now stale by one: it enumerates three runs and this is a
fourth.

## Proposed change

1. **Add a ⚠️ to `module-04-data-collection/SKILL.md`**, next to the existing header rules, stating
   that on the generated-scenario path this module contains **exactly one** 👉 question — the Step 9
   transition — and that Steps 1–8b are therefore non-yielding and share the turn that ends on it.
   Say which branches produce that (Step 2's marker/provenance guard, Step 8a's volume-skip, Step
   8b's below-threshold silence), and say plainly that the bring-your-own-data path *does* ask at
   Step 2, so the run is path-dependent rather than fixed. Point at `ground-rules.md` → the 👉
   protocol for the rule itself rather than restating it (INV-225 is stated once, there).

2. **Add the fourth instance to `ground-rules.md`'s run list** — "…and Data collection's
   generated-scenario path, whose Steps 1–8b ask nothing" — so the enumeration stays complete. This
   is the same one-line maintenance the list already invites by naming instances at all.

3. **State the single-write consequence locally**, as System verification's Agent Rule 10 does: the
   nine steps' checkpoints collapse into **one** write at the end of the shared turn carrying the
   last completed step, not nine writes inside it, with the partial-turn fallback (write what
   completed before stopping, so resume lands on the right step).

⚠️ **Scope note:** no step's behaviour changes. This adds the marking that makes the existing
behaviour followable from inside the module.

## Acceptance criteria

1. `module-04-data-collection/SKILL.md` states that the generated-scenario path carries exactly one
   👉 question (Step 9's transition), names the three branches that make Steps 1–8b non-yielding,
   and states that the bring-your-own-data path asks at Step 2.
2. It states the checkpoint consequence — one write at the end of the shared turn carrying the last
   completed step, with the partial-turn fallback — and does **not** restate INV-225 itself, citing
   `ground-rules.md` → the 👉 protocol instead.
3. `ground-rules.md`'s non-yielding-run instance list names Data collection's generated-scenario
   path alongside the three it already lists.
4. A test asserts both: that the module carries the marking, and that the ground-rules instance
   list names it — negative-controlled by removing each independently.
5. No step's questions, pinned wording, or branching change; the Step 2 guard, Step 8a gate and
   Step 8b warning are asserted unchanged.
6. Cross-platform, language-agnostic.

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md`
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`
- `tests/test_data_collection_non_yielding_run.py` (new)
- `specs/IMPLEMENTED.md`

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-14 by walking Data collection with a
  bootcamp-generated three-source scenario and observing that Steps 1–8b produced no 👉 question
  (`Source: self-observed (assistant retrospective)`).
- Priority: **Low.** Nothing is broken and the general rule covers the behaviour; this closes a
  marking gap in the one module that reaches System verification's shape without System
  verification's warnings. It is the cheapest kind of fix and the kind that stops a future guide
  ending a turn on Step 3 with zero 👉.
- MCP re-check: n/a (no Senzing fact). Server version this session is **1.32.9**
  (`get_capabilities`, 2026-08-14).
