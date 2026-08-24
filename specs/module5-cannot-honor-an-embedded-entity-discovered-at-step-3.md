# A secondary entity is discovered at step 3 and can only be declared at step 2, and Module 5 never says so

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`mapping_workflow` treats a **secondary entity embedded in a source** — an employer on an employee
record, a lender on a loan record, a parent company on a subsidiary — as a first-class disposition,
`embedded_master`. Its step-3 response carries explicit rules for it (server **1.32.9**, 2026-08-12):

> **EMBEDDED MASTER RULES:** … the embedded_master schema's mapping must include derived attributes
> per the spec: Embedded master gets: derived RECORD_ID (deterministic hash of identifying features,
> e.g. hash(NAME_ORG + ADDR_FULL)), derived REL_ANCHOR (so parent can point to it), derived
> RECORD_TYPE. Parent master gets: derived REL_POINTER to the embedded master (DOMAIN, KEY, ROLE)

**`embedded_master` appears nowhere in Module 5.** A grep of `phase2-data-mapping.md` for
`embedded_master` / "embedded master" returns **nothing**.

**The timing is the trap.** An embedded entity is *declared* at **step 2** (`plan_entity_structure`,
whose instructions say "Also identify embedded masters"), but it is only *discoverable* at **step 3**
— you cannot tell that a `Lender` column holds 239 real banks until you look at the values, which is
what step 3 (`map_fields`) is for. Step 3's advance schema offers no way to introduce a new schema:
`schema_mappings` entries are keyed to schemas fixed at step 2, and the server validates
`FIELD INTEGRITY` and `COMPLETE MAPPING` against them.

So honoring the discovery requires **`action='back'`** to step 2, re-planning with the embedded
master, and re-advancing. `action='back'` **is** named in the plugin — `phase2-data-mapping.md:136`
lists all five valid actions — but **nothing anywhere says when to use it.** The only "go back"
guidance in the file concerns step 4's `rework_*` verdicts and the quality gate.

**The failure is silent, and it discards a bootcamper's decision.** A guide at step 3 that
recognizes the entity has two exits, and both are wrong:

- **Try to express it at step 3** → the server rejects it, and the rejection is about field
  integrity rather than about planning, so the cause is not obvious from the message.
- **Downgrade it to `payload`** → the mapping validates, step 3 advances, and the run completes.
  Nothing anywhere records that a secondary entity was found and dropped.

The second is the dangerous one. **Observed live**: in a phase-3 walk the bootcamper was shown the
choice for `Lender` — 239 distinct banks, *"Zions Bank"*, *"Western Alliance Bank"*, *"Bank of
America, National Association"* — and chose *"make each lender its own organization record"*. There
is no instruction in Module 5 that lets a guide carry that out, and the path of least resistance
silently converts it to `payload`, which is the answer the bootcamper explicitly did not pick. A
guide that assumes an answer the bootcamper gave differently is precisely what **INV-007** forbids.

**What is lost is the point of the product.** As `payload`, 3,488 loans carry a lender *string*.
As an embedded master, every borrower funded by the same bank links to one resolved lender entity,
and a later source naming those banks resolves against them. That is entity resolution; the
difference is not cosmetic.

## Root cause

**Module 5's mapping guidance is written as a forward-only pipeline, and the workflow is not one.**

`phase2-data-mapping.md`'s routing table maps each module step to a workflow step and the payload
that advances it — a clean one-way ladder. `back` is listed among the valid actions for
completeness (it is part of the enum INV-136 pins) and then never given a trigger. Every "go back"
the file *does* describe is a **quality** rework at step 4, never a **structural** revision of the
plan.

That is a reasonable model for a source whose structure is known up front, and wrong for the case
the tool itself calls out: planning commits to a structure before the data has been read closely
enough to know it. Nothing caught it because no test drives the workflow (INV-108 keeps the suite
offline), and a prose reader sees a complete, internally consistent ladder.

## Proposed change

1. **Document `embedded_master` in `phase2-data-mapping.md`** — what it is, the three signals that
   suggest one (a column holding many distinct real-world names; a name that repeats across records;
   a name a later source could also mention), and what the tool requires for it: derived
   `RECORD_ID`, `REL_ANCHOR` on the embedded master, `REL_POINTER` on the parent.

2. **Give `action='back'` a trigger.** State plainly: when step 3 reveals a secondary entity the
   step-2 plan does not carry, call `action='back'`, add it as an `embedded_master`, and re-advance.
   Name it as the sanctioned route, not a failure.

3. ⛔ **Forbid the silent downgrade.** A secondary entity that the bootcamper asked to model MUST
   NOT be quietly mapped to `payload`. If it will not be modeled — because the bootcamper declines,
   or because going back is not possible — say so and record it in the registry, so the decision is
   visible rather than inferred from its absence (INV-007, INV-012).

4. **Offer the choice where the evidence is.** The decision belongs at step 3, where the values are
   in front of the bootcamper, with the trade-off stated in both directions: resolvable entity and
   more records, versus a string that never matches.

## Acceptance criteria

- [ ] `phase2-data-mapping.md` documents `embedded_master`, its signals, and the derived attributes
      the tool requires (`RECORD_ID`, `REL_ANCHOR`, parent `REL_POINTER`). Verified by opening it.
- [ ] It states the `action='back'` trigger for a step-3 discovery, as the sanctioned route.
- [ ] It ⛔-forbids silently downgrading a bootcamper-chosen secondary entity to `payload`, and
      requires the outcome be recorded when it is not modeled.
- [ ] The trade-off is stated in both directions at the point the choice is offered.
- [ ] A test asserts all three: `embedded_master` is documented, `back` has a stated trigger, and the
      silent-downgrade prohibition is present. **Not vacuous:** it names the file and fails if any
      one is removed.
- [ ] **Negative-controlled, mutation verified to land:** deleting the `embedded_master` section
      fails the first; deleting the `back` trigger fails the second; deleting the ⛔ fails the third.
      Revert all three.
- [ ] The existing five-actions ⛔ at `:136` and the routing table are **unchanged** — this adds a
      trigger, it does not restate the action list. Verified by `git diff`.
- [ ] Full suite passes (baseline **1784 passed, 3 skipped**). Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108); language-agnostic.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
- `tests/` — one new guard.

## Source

- Dry run, **phase 3**, 2026-08-12, maintainer answering as the Bootcamper, at `mapping_workflow`
  **step 3** — the deepest any run has reached. The bootcamper chose to model lenders as entities and
  the module had no way to carry it out.
- **MCP:** server **1.32.9**, 2026-08-12. The EMBEDDED MASTER RULES and the step-3 advance schema
  are verbatim from live responses this session.
- Evidence established by reading, not inferred: `embedded_master` absent from `phase2-data-mapping.md`
  (grep returns nothing); `action='back'` present at `:136` with no trigger anywhere; the step-3
  advance schema admits no new schema; `Lender` holds 239 distinct bank names across 3,488 records.
- Priority: **Medium-high.** On the required path, and the failure mode silently discards an explicit
  bootcamper decision while every gate still passes — the shape that survives audits.
- Related: INV-007 (the guide never assumes an answer), INV-136 (the action enum this adds a trigger
  to), INV-012 (say what was decided), INV-205 (the adjacent tool-versus-bootcamp precedence rule).

## Invariants introduced

**None proposed.** INV-007 already forbids assuming an answer the bootcamper gave differently; this
is an unapplied instance plus missing routing. If the maintainer wants a general rule — *a
bootcamper's structural choice must be carried out or explicitly recorded as not carried out* —
that is worth its own discussion and is deliberately not smuggled in here.

## Verified live after filing — the route is narrower than this spec assumed (2026-08-12)

Two things were checked against the server rather than left inferred, and the second is worse than
the Problem section states.

**1. `action='back'` works.** Called from step 3 on server **1.32.9**: returns
`{"status":"ok","step":2,"step_name":"plan_entity_structure","message":"Moved back to step 2"}` with
the existing `schema_plan` preserved in state. So the remedy this spec proposes is real, not
hypothetical — the plugin simply never tells anyone to use it.

**2. ⚠️ `embedded_master` cannot be expressed through the tool's PREFERRED payload at all.** The
step-2 typed branch (`for_step 2`) defines:

```text
support_schemas.items.properties.disposition.enum = ["lookup", "relationship", "child"]
master_schemas.items                              → no `disposition` key ("the slot IS the master disposition")
additionalProperties: false                       → at the top level
```

**`embedded_master` is in neither slot**, and `additionalProperties: false` blocks smuggling it in.
The response says so itself, in a parenthesis:

> The legacy flat `{"entity_plan": [{"schema_name","disposition":"master|embedded_master|child|
> relationship|lookup",…}]}` shape is **also accepted for backward compatibility**.

So the only way to declare an embedded master is the **legacy untyped `entity_plan` shape sent as
`data`** — while the same response recommends the typed branch: *"To send it via the typed `payload`
argument (**preferred** — it drives constrained decoding)"*.

**A client that follows the tool's preferred path cannot model an embedded entity.** That is an
upstream defect on top of the plugin gap, and it makes the plugin-side fix strictly larger than
proposed above: honoring the bootcamper's choice requires **going back to step 2 *and* dropping to
the legacy payload shape**, neither of which Module 5 mentions. Add to the Proposed change:

5. **State that `embedded_master` requires the legacy `entity_plan` shape**, sent as `data` rather
   than the typed `payload`, with the dated reason (server 1.32.9, 2026-08-12) and the instruction
   to re-check it — if the typed branch gains the disposition, this note retires rather than
   inverts.
6. **Add a matching acceptance criterion**, and a test assertion that the legacy-shape instruction
   is present and names `entity_plan`.

**Not an upstream report yet.** Unlike `mapping-workflow-step1-prose-contradicts-its-own-advance-schema`
this one has no drafted text and was not sent — a dry run must not send, and whether to report the
typed branch's missing disposition is the maintainer's call.

## Deviations from this spec, and why (2026-08-12)

**The guard shipped larger than the criteria asked, and one assertion needed rework caught by its
own mutation.**

The criteria asked for a test asserting three things. What shipped is a five-test class plus a
`five-actions was not restated` check — that last one guards against *fixing* this by forking the
action list, which would create the second statement of record `phase2-data-mapping.md` already
warns about elsewhere.

⚠️ **One mutation escaped on the first attempt.** `test_the_legacy_entity_plan_requirement_is_stated`
asserted `"entity_plan" in <whole file>`. Deleting the entire legacy-shape ⛔ still **passed**,
because `entity_plan` also appears ~100 lines above, in the list of payload field names once
mistaken for action names. Fixed by extracting the embedded-master section and asserting the claim
*inside it*, plus a second assertion that the note says **why** the legacy shape is needed (the
typed/preferred branch cannot express it) — so a note that names the shape without the reason no
longer passes. Re-run: the mutation now fails.

This is the same shape as three other guard defects today: asserting a token appears *somewhere*
rather than that the claim holds *where it is made*. Worth stating plainly — it is the single
recurring error of the session, and every instance was caught by the mandatory negative control
rather than by review.

**Criterion coverage note:** the spec's Proposed change grew during the dry run (items 5 and 6 were
appended after `action='back'` and the typed-branch limitation were verified live). Both shipped:
the legacy `entity_plan` requirement is documented with its dated reason, and it carries its own
assertion.

**No other deviation.** The five-actions ⛔ at `:136` and the routing table are unchanged, verified
by `git diff` showing neither in the removed lines.
