# The embedded-master check belongs at plan time; Module 5 documents only the `back` recovery

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`phase2-data-mapping.md:232-288` now documents `embedded_master` — landed 2026-08-12 by
`module5-cannot-honor-an-embedded-entity-discovered-at-step-3`. It frames the discovery as a
**step-3 event** and prescribes `action='back'` as the route:

> ⛔ **The timing is a trap, and going `back` is the sanctioned fix.** An embedded master is
> **declared at step 2** (`plan_entity_structure`) but is usually only **discoverable at step 3**,
> when you finally look at the values. (`:249-251`)

**The premise is wrong for this workflow: the evidence arrives at step 1.** All three signals the
section names are in the profiler's own output, which the guide reads at module step 9 and plans from
at module step 10 — *before* the step-2 advance. Verified live this session on server **1.32.9**
(2026-08-12), profiling the CORD `ppp_loans` source with the tool's own `sz_schema_generator.py`:

```text
| # | Field Name | Type | Records | Pop % | Unique | Unique % | Sample 1 | Sample 2 …
| 18 | Lender    | str  | 3488    | 100.0%| 239    | 6.9%     | Zions Bank, A Division of (527) | Western Alliance Bank (395) …
```

That single row carries every signal the section asks for: **many distinct real-world names** (239
unique), the name **repeats across records** (top value 527 times), and the values are visibly bank
names rather than categories. Nothing about the discovery required reaching step 3.

**And the tool asks for it at step 2, in the step the plugin leaves silent.** The
`plan_entity_structure` response says (verbatim, server 1.32.9, 2026-08-12):

> Step 1 — IDENTIFY MASTERS: … **Also identify embedded masters** — fields within another schema that
> represent a distinct secondary entity (e.g., employer name/address on employee records).

and enumerates `embedded_master` in its `SCHEMA DISPOSITIONS` block ahead of `child`, `relationship`
and `lookup`.

**Module 5's step 10 (Plan) says nothing about it.** `phase2-data-mapping.md:413-430` reads:

> ### 10. Plan
> Identify entity type (person/org/both), structure (flat/nested), relationships. Advance workflow
> step 2 with `action='advance'`, carrying `master_schemas` … and `support_schemas` … Tell the user:
> explain the entity type decision, which fields map vs. skip and why.

`grep -n -i "embedded\|secondary"` over lines 413-432 returns nothing, and **`embedded` appears
nowhere in the file after line 288** — so neither step 10 nor step 11 cross-references the section
that explains it. A guide working the numbered steps in order reaches the plan advance with the
profile in hand, is told to identify "relationships" but not embedded masters, and commits a plan
that omits one.

**The cost is a wholly avoidable round trip, on the required path.** Caught at step 10 it is one
extra entry in the step-2 payload. Missed there, honoring it costs `back` → re-plan → re-advance,
*and* dropping from the tool's preferred typed `payload` to the legacy `entity_plan` shape (the
constraint `:263-275` documents) — a materially harder path that the same section correctly warns is
"a trap". The plugin documents the recovery from a miss and never documents avoiding the miss.

**This was observed by walking it, not by reading it.** A fresh session following the numbered steps
advanced the `ppp_loans` plan with `master_schemas` only, no `support_schemas`, no embedded master —
exactly what step 10 as written produces — despite the `Lender` row being visible in the profile
report the same session had just generated.

## Root cause

**The originating spec generalized from the turn it was found on, not from where the evidence lives.**

The defect was discovered *at* step 3 in the 2026-08-12 walk, because that is where the previous
session happened to be looking closely at values. The fix documented the situation as encountered —
"discoverable at step 3, go `back`" — and inherited a premise that the walk's timing made feel
structural. It is not: `profile_report.md` carries per-field unique counts and frequency-annotated
samples from step 1 onward.

The second half is placement. The section sits at `:232`, **above** `## Workflow (per data source)`
(`:290`), so it reads as preamble to the whole workflow while every numbered step below it is silent
about it. That is the failure mode **INV-183** names — a rule must be reachable at the step that
needs it — and the same concern `inv205-covers-whether-to-ask-but-not-how` cited one commit earlier.

## Proposed change

1. **Add the embedded-master check to step 10 (Plan)** as a plan-time obligation: before advancing
   workflow step 2, scan the profile report for the three signals and declare any embedded master in
   the step-2 payload. Cross-reference the `:232` section rather than restating it — the section stays
   the single statement of record.

2. **Reframe `:249-251` from "discoverable at step 3" to "confirmable at step 1, declarable at
   step 2, recoverable via `back`."** Keep the `back` route exactly as it is — it is correct and
   necessary — but demote it to the fallback it should be, and say plainly what the profile columns
   to read are (`Unique`, `Unique %`, and the frequency-annotated `Sample` columns).

3. **Name the tool's own step-2 instruction** ("Also identify embedded masters") in the section, so a
   guide sees that the plugin and the tool agree on where the declaration belongs. This is a Senzing
   fact from a live response and carries its dated provenance.

4. **Do not remove or weaken the step-3 offer.** The bootcamper-facing *decision* still belongs at
   step 3 where the values are in front of them, and the ⛔ against silently downgrading to `payload`
   is unchanged. What moves earlier is the guide's **detection**, not the bootcamper's choice.

## Acceptance criteria

- [ ] Step 10 (Plan) states the embedded-master check as a plan-time obligation and cross-references
      the `:232` section by name. Verified by opening `phase2-data-mapping.md`.
- [ ] The section no longer asserts the discovery is "usually only discoverable at step 3"; it names
      the profile-report columns that carry the signals at step 1.
- [ ] The `action='back'` route survives verbatim in substance, framed as the fallback for a miss.
- [ ] The step-3 offer, the both-directions trade-off, and the ⛔ silent-downgrade prohibition are
      **unchanged** — verified by `git diff` showing none of them in the removed lines.
- [ ] A test asserts step 10 carries the check and points at the section, **and** that the `back`
      route is still present. **Not vacuous:** it extracts the step-10 section and fails if the
      reference is removed from it — asserting the token appears *somewhere* in the file is
      precisely the defect the previous spec's mutation caught.
- [ ] **Negative-controlled, mutation verified to land:** deleting the step-10 sentence fails the
      first assertion; deleting the `back` route fails the second. Revert both.
- [ ] Full suite passes (baseline **1792 passed, 3 skipped**). Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
- `tests/test_tool_directives_do_not_override_interaction.py` — or a sibling guard; the existing
  embedded-master class is the natural home.

## Source

- Dry run, **phase 3**, 2026-08-12, fresh session, maintainer answering as the Bootcamper, walking
  `mapping_workflow` from `start` to **step 3** with the embedded-master route newly available.
- **MCP:** server **1.32.9**, 2026-08-12. The step-2 "Also identify embedded masters" instruction and
  the `SCHEMA DISPOSITIONS` block are verbatim from a live response; the `Lender` profile row is from
  `sz_schema_generator.py` run locally on the CORD `ppp_loans` source (3,488 records, 19 fields).
- Evidence established by reading and by walking: `embedded` absent from `phase2-data-mapping.md`
  after `:288`; step 10 (`:413-430`) silent; the plan advanced without an embedded master when the
  numbered steps were followed as written.
- Priority: **Medium.** Not a wrong statement — an incomplete route on the required path. The
  documented fix works; it is just the expensive half of the answer, and the cheap half is missing.
- Related: `module5-cannot-honor-an-embedded-entity-discovered-at-step-3` (the spec this refines —
  its route is correct, its premise about *when* is not), INV-183 (reachable at the step that needs
  it), INV-136 (the `back` action), INV-007 (the bootcamper's choice is theirs).

## Deviations from this spec, and why (2026-08-13)

**⚠️ One of the new assertions was vacuous when written, and its own negative control caught it.**
`test_step_ten_carries_the_plan_time_check` originally asserted that step 10 matches
`(?i)A second entity hiding in a column` — intended to prove step 10 *points at* the section. But that
phrase also occurs in step 10's own new instruction sentence ("check the profile for a second entity
hiding in a column"), so **deleting the cross-reference outright still passed.** Rewritten to match the
heading's distinctive tail (`and when to go \`back\``), which appears nowhere else in the file.

This is the **fifth** instance in two days of the same error — asserting a token appears *somewhere*
rather than that the claim holds *where it is made* — and the first where the vacuous assertion was in
brand-new code written by an author who had just documented the pattern twice. Care is not the control;
the mutation is.

**Two mutations were themselves defective before they proved anything.** One replaced only one of two
statements of the same claim (`back` preserves the plan), so the surviving copy correctly kept the
guard green; one used stale text ("sits in `state`" where the file says "is still sitting in `state`")
and silently matched nothing of the second occurrence. Both replaced with definitive whole-claim
mutations. Recorded because a mutation that fails to mutate reads exactly like a guard that works.

**A guard shipped beyond the criteria:** `test_step_ten_points_at_the_section_instead_of_forking_it`
asserts step 10 does **not** restate `entity_plan`, `embedded_in` or `RECORD_HASH`. The spec asked for a
cross-reference "rather than restating it"; nothing would have caught a later edit that helpfully
inlined the payload contract, creating the second statement of record this file warns about elsewhere.

**The spec's line references are pre-`INV-206` positions.** `:249-251` and `:413-430` shifted when
`embedded-master-legacy-payload-example-is-not-runnable` landed earlier the same session; the section is
now at `:249` and step 10 at `:457`. Content unchanged, addresses moved.

**Baseline:** the spec predicted "full suite passes (baseline 1792 passed, 3 skipped)". Actual before
this change was **1795 passed, 3 skipped**; after, **1799 passed, 3 skipped** (+4, exactly the tests
added). The 1792 figure is the stale one recorded in
`proving-an-id-is-unused-by-writing-it-cites-it`, not a regression here.

**No other deviation.** All four proposed changes shipped, and the protected content is untouched:
`git diff` shows seven removed lines, all of them the reframed ⛔ header and its old premise. The
three-step `back` sequence, the step-3 offer, the both-directions trade-off and the silent-downgrade ⛔
appear in no removed line.

## Invariants introduced

**None proposed.** INV-183 already covers reachability; this is an unapplied instance of it. A rule
of the shape *every tool-side obligation stated in a step's response must be reachable from the
module step that calls it* would be a real generalization, and it is deliberately not smuggled in
here — it would need its own instance threshold.
