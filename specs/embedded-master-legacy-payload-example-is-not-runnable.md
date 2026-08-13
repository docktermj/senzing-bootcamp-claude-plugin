# Module 5's `embedded_master` payload example is rejected by the server, and omits a key the tool never documents

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`phase2-data-mapping.md:263-275` tells the guide to declare an embedded master through the legacy
`entity_plan` shape, and gives this payload:

```text
data={'entity_plan': [{'schema_name': …, 'disposition': 'embedded_master', 'data_source': …,
                       'record_type': 'ORGANIZATION', 'field_count': <fields belonging to it>}]}
```

**Sent as written, the server rejects it.** Verified live on server **1.32.9**, 2026-08-12, from
step 2 after `action='back'`, declaring `Lender` on the CORD `ppp_loans` source:

```text
"status":"error", "message":"Schema plan validation failed. Fix the errors and try again."
"errors":[
  "schema_plan[0] (lender): 'embedded_master' requires 'record_id_source'",
  "schema_plan[0] (lender): 'embedded_master' requires 'embedded_in'",
  "profile schema 'ppp_loans' has no disposition in schema_plan",
  "schema_plan must contain at least one 'master' disposition — the main/primary entities use
   disposition 'master'; change the central schema's disposition to 'master'."
]
```

Four errors, from three independent omissions:

1. **`record_id_source` is required** and the example does not carry it. The field is required for
   master entries in the typed branch too, so its absence here reads as deliberate rather than
   elided — a guide has no reason to add it.

2. ⚠️ **`embedded_in` is required, and it is documented nowhere.** It is absent from
   `phase2-data-mapping.md`, and — checked against the same response — absent from the tool's own
   step-2 instructions, which say only *"For embedded_master: provide field_count (number of fields
   from parent schema that belong to this entity)"*. It is not in the typed `for_step 2` branch
   either, because that branch cannot express `embedded_master` at all (`:263-266`). **The key is
   discoverable only by sending a payload without it and reading the rejection.** That is an upstream
   documentation gap, and the plugin currently inherits it silently.

3. **The `entity_plan` list replaces the entire plan, so it must also re-declare the parent master.**
   The example shows a one-element list holding only the embedded master, which drops `ppp_loans`
   from the plan — hence errors 3 and 4. This is the more dangerous omission because the surviving
   `schema_plan` in state *looks* preserved after `back` (it is), so a guide reasonably reads the
   one-element example as an addition to the existing plan rather than a replacement of it.

**Why the earlier verification missed it.** The originating spec
(`module5-cannot-honour-an-embedded-entity-discovered-at-step-3`) records the legacy shape as
"Verified on server 1.32.9, 2026-08-12". What was verified is that the step-2 response *documents* the
legacy channel as accepted, and that `action='back'` works — both true, both re-confirmed today. What
was never done is **sending an `embedded_master` payload and seeing it validate**. The plugin
therefore documents the right channel with a payload that cannot travel it, which is a strictly worse
failure than documenting nothing: it reads as verified, and it fails at the one moment a bootcamper is
watching the guide honour their choice.

**The working payload**, established empirically the same session and same server version:

```text
data={'entity_plan': [
  {'schema_name': 'ppp_loans', 'disposition': 'master', 'data_source': 'PPP_LOANS',
   'record_type': 'ORGANIZATION', 'record_id_source': 'RECORD_ID', 'field_count': 19},
  {'schema_name': 'lender', 'disposition': 'embedded_master', 'data_source': 'PPP_LOANS',
   'record_type': 'ORGANIZATION', 'record_id_source': 'RECORD_HASH', 'embedded_in': 'ppp_loans',
   'field_count': 1}]}
```

## Root cause

**A payload shape was documented from a response's prose rather than from a successful call.**

The step-2 response advertises the legacy shape in a parenthesis that lists five keys
(`schema_name`, `disposition`, `data_source`, `record_type`, `record_id_source`). The plugin's example
was written from that advertisement, dropped `record_id_source` in transcription, and could not have
known about `embedded_in` because the response never names it. Nothing caught it because the
offline suite cannot call the tool (INV-108) and the dry run that filed the original spec verified the
*route* — `back`, and the channel's acceptance — without ever exercising the payload.

This is the same failure shape the module already warns about for step 1: a response's prose and its
enforced contract disagreeing. Here the prose is not wrong, merely incomplete, and the plugin
inherited the incompleteness plus a transcription loss.

## Proposed change

1. **Replace the example at `:263-275` with the verified working payload**, including both entries —
   the parent master and the embedded master — so the replacement semantics are visible in the shape
   itself rather than stated.

2. **State plainly that `entity_plan` replaces the whole plan**, so every schema must be re-declared,
   not just the new one. This is the trap that produces the two least obvious of the four errors.

3. **Document `embedded_in`** with its dated provenance and the note that the tool does not document
   it — the value is the parent schema's name. Flag it as discovered from a validation rejection, so a
   future reader knows why it is not citable to any response text.

4. **Give `record_id_source` for an embedded master its own line.** `RECORD_HASH` is the right value
   here and the reason is the tool's own EMBEDDED MASTER RULES (derived `RECORD_ID` is a deterministic
   hash of identifying features), which the module already quotes at `:277-280` — connect the two so
   the choice is derived rather than copied. Confirmed accepted: the server echoed
   `"record_id_source":"RECORD_HASH"` into the validated plan, and step 4's instructions then define
   the sentinel's meaning — *"If it is the sentinel `RECORD_HASH` … generate `RECORD_ID` as a
   deterministic hash over that entity's stable IDENTITY fields only"*.

4a. **Say how `KEY` is expressed in a `REL_POINTER` / `REL_ANCHOR` derived entry.** `:277-280` says the
   parent gets "a derived `REL_POINTER` naming domain, key and role", which is correct about the
   *attributes* and silent about the *payload*: the typed derived branch has `domain` and `role`
   properties and **no `key`** (`additionalProperties: false`, so adding one is rejected). The tool's
   own example packs it into `value` — `{"derived_as": "REL_ANCHOR", "value": "DOMAIN=<DS>,
   KEY=<RECORD_ID>"}`. Verified accepted this session in that form on both entries:

   ```text
   parent : {'disposition':'derived','derived_as':'REL_POINTER','domain':'PPP_LOANS','role':'LENDER',
             'value':'DOMAIN=PPP_LOANS, KEY=hash(Lender), ROLE=LENDER'}
   embedded: {'disposition':'derived','derived_as':'REL_ANCHOR','domain':'PPP_LOANS',
             'value':'DOMAIN=PPP_LOANS, KEY=hash(Lender)'}
   ```

   Same root cause as the rest of this spec — a shape described from prose rather than from a call —
   and a few lines in the same section, so it rides along here rather than in its own spec.

5. **Report the `embedded_in` documentation gap upstream** — an undocumented required key is a
   legitimate `submit_feedback` (category `bug`) item. ⛔ **Draft it, do not send it:** a dry run must
   not transmit, and whether to file is the maintainer's call.

## Acceptance criteria

- [ ] The example at `:263-275` carries both entries and all required keys, matching the verified
      payload above. Verified by opening `phase2-data-mapping.md`.
- [ ] The whole-plan-replacement semantics of `entity_plan` are stated explicitly.
- [ ] `embedded_in` is documented, with its dated provenance and the note that the tool does not
      document it.
- [ ] The `record_id_source: RECORD_HASH` choice is stated and tied to the EMBEDDED MASTER RULES
      already quoted in the same section.
- [ ] A test asserts the example carries `record_id_source`, `embedded_in`, **and** a `master` entry
      alongside the `embedded_master` entry. **Not vacuous:** it extracts the embedded-master section
      and asserts within it — the whole-file token check is the exact mutation escape the originating
      spec recorded at its `## Deviations` section.
- [ ] **Negative-controlled, mutation verified to land:** deleting `embedded_in` from the example
      fails; deleting the `master` entry from the example fails; deleting the replacement-semantics
      sentence fails. Revert all three.
- [ ] The `action='back'` route, the typed-branch-cannot-express-it ⛔, the step-3 offer and the
      silent-downgrade ⛔ are **unchanged** — verified by `git diff`.
- [ ] Full suite passes (baseline **1792 passed, 3 skipped**). Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
- `tests/test_tool_directives_do_not_override_interaction.py` — extends the existing embedded-master
  guard class.

## Source

- Dry run, **phase 3**, 2026-08-12, fresh session, maintainer answering as the Bootcamper. The
  Bootcamper chose "make each lender its own organisation record", and carrying it out ran the
  documented route: `back` → legacy `entity_plan` → step 3.
- **MCP:** server **1.32.9**, 2026-08-12. The four-error rejection is verbatim from the live response
  to the module's own example payload. `action='back'` returning to step 2 with `schema_plan`
  preserved was re-confirmed in the same run.
- Priority: **High.** It is on the required path the previous fix created, it fails closed at the exact
  moment the bootcamper's explicit choice is being honoured, and the module currently presents it as
  verified. A guide that hits four validation errors while carrying out a decision the bootcamper just
  made is the worst possible place for this to surface.
- Related: `module5-cannot-honour-an-embedded-entity-discovered-at-step-3` (the spec whose example
  this corrects), `embedded-master-check-belongs-at-plan-time-not-only-as-a-back-recovery` (the
  companion finding from the same walk), INV-080 (the tool's payload contracts are authoritative),
  INV-125 (record the raw failure).

## Invariants introduced

- `INV-206` — An **MCP payload example in shipped plugin guidance** MUST be one that was executed
  successfully against the live server, and MUST carry the server version and date of that successful
  call (recorded in `specs/INVARIANTS.md`, 2026-08-12, indexed under **MCP sourcing and tool
  contracts**).

**Approved by the maintainer on 2026-08-12** after being proposed rather than assumed here, because it
implies an audit of every other payload example in the module. The recurring shape it closes, across
two sessions: *a payload example in the plugin was written from a tool response's prose without ever
being sent.* It is narrower than INV-080 — that one makes the tool authoritative on payload shape;
this one governs how the plugin establishes what the shape actually is.

⚠️ **Registering this ID incidentally resolved a failing test.** `citations.py verify` was reporting
`undefined invariant INV-206 cited in specs:2` — see
`proving-an-id-is-unused-by-writing-it-cites-it`, whose two citations were the evidence sentences for
a claim that the ID had never been minted. Defining INV-206 makes those citations resolve. That is a
side effect, not the fix: the sentences still assert something now doubly false, and that spec stays
open.

## Deviations from this spec, and why (2026-08-12)

**One criterion is not met, for a reason unrelated to this work.** "Full suite passes (baseline 1792
passed, 3 skipped)" **does not hold** — and it did not hold before this change either. The suite is
red on `main` from a self-referential `INV-206` citation, filed as
`proving-an-id-is-unused-by-writing-it-cites-it`. Measured numbers:

```text
HEAD (498a0be, clean worktree):  1 failed, 1788 passed, 3 skipped, 1539 subtests
with this change:                1 failed, 1794 passed, 3 skipped, 1543 subtests
```

The delta is **+6 passed**, exactly the six tests added here, and the one failure is byte-identical
before and after. The criterion is therefore **disclosed, not ticked** — and the recorded 1792 baseline
turns out to be four higher than the committed tree ever produced, which is part of that separate spec.

**The guard shipped larger than the criteria asked, again.** Three mutations were required; six were
run, one per new assertion. Two additional assertions went beyond the criteria: that the section
carries the `MCP-NEGATIVE` marker (the `embedded_in` claim is a negative, and negatives are the one
shape the offline suite cannot notice going stale), and `assertNotRegex(r"'key':")` — a guard against
the *plausible wrong fix*, since a reader who learns KEY is required will reach for a `key` property
that `additionalProperties: false` rejects.

⚠️ **Two mutations escaped on the first attempt, and the cause was the mutations, not the guards.**
Both target claims are stated twice in the section — `embedded_in` in the ⛔ heading *and* in the
MCP-NEGATIVE marker; `KEY=` on the parent entry *and* the embedded entry — so a single-occurrence edit
left the claim standing and the test correctly passed. Re-run with whole-paragraph and global-regex
mutations: all six caught, doc restored byte-identical to its `cp` backup.

One guard was genuinely weak and was strengthened by the escape: `test_the_rel_pointer_key_is_shown_
going_into_value` originally asserted a bare `KEY=` appears somewhere in the section, which would pass
on prose mentioning the attribute while the example showed a rejected `key` property. It now pins
`'value': '…KEY=` — the claim is that KEY travels *inside* `value`, so that is what is asserted. This
is the fourth instance of the session's recurring error: **asserting a token appears somewhere rather
than that the claim holds where it is made.** Every instance has been caught by the mandatory negative
control rather than by review, which is the argument for the control.

**No other deviation.** `git diff` shows six removed lines, all of them the old payload example and its
trailing note; the typed-branch ⛔ (its enum, `additionalProperties: false`, "in neither slot"), the
`action='back'` route, the step-3 offer and the silent-downgrade ⛔ are untouched, and the "also
accepted for backward compatibility" sentence is preserved verbatim in the new text.

## Upstream report — DRAFTED, NOT SENT

For the maintainer to send or discard. Category `bug`:

> `mapping_workflow` step 2 rejects a legacy `entity_plan` entry with `'embedded_master' requires
> 'embedded_in'`, but `embedded_in` is not documented anywhere in the step-2 response: the
> instructions say only "For embedded_master: provide field_count", and the typed `for_step 2` branch
> cannot express `embedded_master` at all (its `support_schemas.disposition` enum is
> `lookup|relationship|child` with `additionalProperties: false`). The required key is discoverable
> only by triggering the validation error. Please document `embedded_in` in the step-2 instructions
> alongside `field_count` — and consider adding `embedded_master` to the typed branch, since a client
> following the response's own "preferred" path cannot declare one. Server 1.32.9.
