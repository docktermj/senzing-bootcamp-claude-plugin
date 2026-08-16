# Verbose mapping mode requires an entity-plan 👉 the module never defines

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`phase2-data-mapping.md`'s INV-205 carve-out overrides the `mapping_workflow` tool's
"do not ask the user" directive at the entity-plan advance, and routes the decision to the
bootcamper's mapping-verbosity choice:

> - **At the entity-plan advance, the mapping verbosity choice decides** — not the tool. In the
>   guided mode, **present the plan and end the turn on this module's own 👉 before advancing.** In
>   the faster mode, present it and advance the same turn, which is what the tool wanted anyway.

**There is no such 👉.** Step 10 ("Plan") contains no question at all — only the advance
instruction, the `embedded_master` check, a checkpoint, and a verbosity-conditional *presentation*
block. A grep of the whole phase finds these 👉 questions and no plan gate among them:

| Line | Question |
|---|---|
| 30 | mapping-verbosity mode |
| 561 | two source fields for the same feature family |
| 837 | validator rejected twice without saying why |
| 954 | web page showing the quality analysis |
| 982 / 989 / 996 | the three quality-gate branches |
| 1136 | module transition |

So in verbose mode the guide is told to end a turn on a question that does not exist.

### Why the guide cannot resolve this on its own

The two available moves are each forbidden by something else in the same module:

1. **Invent a question.** Phase 1's step-7 gate carries an explicit ⛔ against exactly this —
   *"Do not invent a gate question for the ≥80% branch… improvising one breaches INV-056, which pins
   every gate question's wording precisely so it cannot drift at runtime."* INV-056 is module-wide,
   not scoped to that branch, so improvising a plan gate has the same defect: two guides ask
   differently, and the wording is unreviewed.
2. **Advance without asking.** This breaches the carve-out, and it silently breaks the promise the
   verbosity offer made one step earlier — *"Verbose mode — I'll show each mapping step in detail:
   field detection, attribute selection rationale, transformation preview."* The plugin says so
   itself, of following the tool here: *"Following the tool there breaks that promise silently — a
   single-schema plan clears the 0.80 bar trivially, so the entity plan would advance with nothing
   shown and nothing asked."*

**Observed live, phase-3 dry run, 2026-08-14, MCP server 1.32.9.** Walking Module 5 Phase 2 on a
single flat CSV (`meridian_crm`, 14 records, 6 fields) in **verbose** mode, `mapping_workflow`
returned step 2 carrying its directive verbatim:

> **INTERACTIVE MODE:** - If ALL entries have confidence >= 0.80: present the plan summary AND
> immediately call mapping_workflow action="advance" in the SAME turn. **Do NOT ask the user to
> confirm, approve, type YES, or proceed. Do NOT wait for a response. Just advance.**

The plan is one master schema at confidence 0.95 — comfortably over the bar, so the tool's
fast path applies and the carve-out is supposed to override it. At that point there was nothing
pinned to ask, and the walk had to compose a question to proceed at all.

This is the **common** case, not an edge one: any single-schema source clears 0.80 trivially, which
the plugin already says in the sentence quoted above.

## Root cause

The carve-out was written to fix a *behavioral* defect (the tool suppressing interaction) and
correctly located the decision in `mapping_verbosity`. But it delegates the question itself to "this
module's own 👉" without ever adding one to step 10 — the step it governs. The instruction and the
artifact it depends on live in different sections, and only the instruction was written.

`specs/inv205-covers-whether-to-ask-but-not-how.md` extended INV-205 to cover the *form* of a
question (the `QUESTION FORMAT` shape breach). The same gap one level up — whether the question
*exists* — was not covered.

## Proposed change

**Pin an entity-plan confirmation question at step 10, conditional on `mapping_verbosity`.**

Add to step 10, inside its existing verbosity-conditional presentation block, the guided-mode gate —
pinned verbatim (INV-056), neutral lead, numbered options, no "or" joining choices (INV-051):

> 👉 **Here's the entity plan for {source}. How would you like to proceed? Reply with a number:**
>
> 1. **Looks right — map the fields.**
> 2. **Change the entity type** (currently {record_type}).
> 3. **Change which field identifies each record** (currently {record_id_source}).
> 4. **Something else** — tell me what to adjust.

Options 2–4 exist because a confirmation gate whose only answer is "yes" is the pointless question
INV-012 forbids; the bootcamper in guided mode was promised the decisions, so the gate must let them
change the two the plan actually commits to. Option 3 is the one that matters most — `record_id_source`
is where the tool's own reference warns a whole-record hash "re-keys whenever ANY field changes", and
it cannot be revised after step 3 without going `back`.

Then state the routing explicitly at step 10, rather than leaving it in the carve-out:

- **Verbose:** present the plan per the existing verbose presentation rules, then end the turn on
  the pinned question. Advance on option 1; on 2–4, revise and re-present it (do not re-ask a
  settled part — INV-006).
- **Concise:** present the plan summary and advance in the same turn, with **no** question. This is
  the tool's own fast path and needs no gate.

And **cross-reference from the carve-out to the pinned question** so the two cannot drift apart —
the carve-out states the rule, step 10 owns the wording (INV-183's shape: the rule is named where it
is needed, never forked).

⚠️ **Scope note:** this adds one pinned question and states the routing. The carve-out's other
clauses — the language directive being already satisfied, the `QUESTION FORMAT` reshaping, the ⛔
that everything non-conversational in the tool response stays authoritative — are unchanged.

### Check the sibling advances for the same gap

Step 11 (Map / workflow step 3) and step 15 (the verdict advance) are governed by the same carve-out
sentence. Step 11 has the line-561 question for the specific two-fields-one-family case but no
general guided-mode gate; step 15's verdict is a decision the bootcamper in guided mode plausibly
owns too. Audit both while fixing this, and either pin a gate or state explicitly that the advance
is unconditional there — an absent question that is *intended* to be absent should say so, so the
next reader does not find this same hole.

## Acceptance criteria

1. Step 10 carries a pinned, verbatim entity-plan question with a neutral lead and numbered options
   including at least: accept, change record type, change record-id field.
2. Step 10 states the verbose/concise routing explicitly (verbose ends the turn on the question;
   concise advances in the same turn with no question).
3. The INV-205 carve-out points at step 10 for the wording instead of referring to an undefined
   "this module's own 👉", and does not restate the question.
4. Step 11 and step 15 either carry an equivalent guided-mode gate or state explicitly that their
   advance is unconditional; neither is left implying a question that does not exist.
5. A test asserts that every place instructing the guide to "end the turn on" a question resolves to
   a pinned question in the same skill — negative-controlled by removing the new question while
   leaving the carve-out's instruction in place, which must fail.
6. The tool's non-conversational authority is asserted unchanged (payload shapes, opaque `state`
   echo, the mapping reference), as is the concise-mode fast path.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
- `tests/test_end_the_turn_questions_exist.py` (new)
- `specs/IMPLEMENTED.md`

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-14, walking Module 5 Phase 2 in verbose
  mapping mode against MCP server 1.32.9 and reaching workflow step 2 with a single master schema at
  confidence 0.95 (`Source: self-observed (assistant retrospective)`). The tool's
  "Do NOT ask the user… Just advance" directive was returned verbatim, confirming the carve-out is
  still needed and still dated correctly; what is missing is the question it defers to.
- Priority: **Medium-High.** It is an unsatisfiable instruction in the module the whole `dry-run`
  skill was created over, on the path a bootcamper takes when they explicitly asked to be walked
  through each decision. Either resolution available to the guide breaks a different rule, and the
  failure is silent: advancing anyway looks like normal progress.
- MCP re-check: **confirmed, server 1.32.9, 2026-08-14.** `mapping_workflow(action='advance')` from
  step 1 returned the step-2 instructions carrying the INTERACTIVE MODE directive quoted above, and
  the step-2 `advance_schema` still enumerates `support_schemas.disposition` as
  `lookup | relationship | child` with `additionalProperties: false` — so the existing
  `embedded_master`-needs-the-legacy-payload note remains accurate and is untouched by this spec.

## Invariants introduced

- `INV-233` — Wherever shipped guidance instructs the guide to **end the turn on** a question, a
  pinned 👉 question MUST exist in the section that owns it: the same section, or — when the
  instruction names another step — that step's section (recorded in `specs/INVARIANTS.md`).

## Deviations from this spec, and why (2026-08-14)

- **Criterion 4 resolved by stating the advance is unconditional, not by pinning two more gates.**
  The spec permitted either. Step 11's questions are *conditional* and each is already pinned or
  specified where it triggers (a sub-0.80-confidence field via the reshaped `QUESTION FORMAT`, the
  shared-feature collision, the twice-rejecting validator), so a general gate there would duplicate
  them. Step 15's `verdict` is a QA judgment that follows from the analyzer's own output rather than
  a preference the bootcamper holds, and that step already ends on pinned questions (the
  visualization offer, the quality-gate branches). Both now say so explicitly, with the reason, so
  the absence reads as intended rather than as the same hole step 10 had.
- **The guard shipped broader than the criterion asked.** Criterion 5 asks that every "end the turn
  on" instruction resolve to a pinned question *in the same skill*; the implemented sweep resolves
  cross-references to the named step's section and runs over **every** shipped `.md` under
  `plugins/`, which was verified clean plugin-wide before being pinned. That is what INV-233
  registers.
