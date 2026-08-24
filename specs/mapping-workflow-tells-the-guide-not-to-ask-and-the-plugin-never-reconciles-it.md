# `mapping_workflow` orders the guide not to ask the Bootcamper, and the plugin never reconciles it

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`mapping_workflow`'s step-2 response instructs the calling model, verbatim (server **1.32.9**,
2026-08-12):

> **INTERACTIVE MODE:**
> - If ALL entries have confidence >= 0.80: present the plan summary AND immediately call
>   `mapping_workflow` action="advance" **in the SAME turn. Do NOT ask the user to confirm,
>   approve, type YES, or proceed. Do NOT wait for a response. Just advance.**

and, at step 1:

> **MAPPING MODE — determined by how the user phrased their request** … AUTONOMOUS MODE: … "map
> this without me" … INTERACTIVE MODE (default) … **MAPPER LANGUAGE — determine from context (do
> not ask)**

**Nothing in Module 5 addresses any of this.** A grep of `phase2-data-mapping.md` for *do not ask*,
*just advance*, *autonomous mode*, *interactive mode* or *without asking* returns **nothing**.

**The two authorities give opposite instructions, and the plugin's are absolute.** `ground-rules.md`
requires the guide to end a turn on its single 👉 question and wait; INV-007 states the plugin
"cannot answer questions nor assume answers"; Module 5's own SKILL.md opens by saying a step
containing a 👉 question "has the same absolute precedence as a ⛔ mandatory gate, and no internal
reasoning can override it". The tool says: do not ask, do not wait, just advance.

**It bites hardest exactly where the Bootcamper asked to be involved.** Phase 2 opens with a pinned
mapping-verbosity question (`:30`): option 1 is *walk through each field with me, so you see how
mapping decisions get made*. A Bootcamper who picks option 1 has explicitly asked to see the
decisions — and the tool then instructs the guide to advance through the entity-plan step without
showing or asking anything, because a single-schema plan trivially clears the 0.80 confidence bar.
The bootcamp promises involvement and the tool suppresses it.

**Observed, not hypothetical.** In a phase-3 walk the Bootcamper chose option 1; the very next tool
response carried the do-not-ask instruction, with one master schema at high confidence — the exact
configuration where the tool says advance silently.

**A second, milder instance in the same responses.** *"MAPPER LANGUAGE — determine from context (do
not ask)"* is compatible with the plugin only by luck: `programming_language` is already captured in
Bootcamp preparation and persisted (INV-075/INV-133), so there is nothing to ask. That it happens to
agree is worth stating, because it shows the conflict is about *who owns the interaction contract*,
not about one badly-worded line.

**No Senzing fact is at issue.** Both sides are instructions about conversation.

## Root cause

**Two interaction contracts, no precedence rule.**

`mapping_workflow` is designed to be driven by a general coding agent with no conversational
obligations, so it reasonably optimizes for throughput — advance when confident, ask only when
uncertain. The bootcamp is a *teaching* conversation whose invariants (INV-005 through INV-009) make
the asking the point. Both are internally coherent; nothing states which wins.

`phase2-data-mapping.md` has a detailed "Calling `mapping_workflow` correctly" section (`:115-176`)
covering required parameters, the opaque-state contract and the action enum — everything about the
tool's **call** shape, and nothing about the tool's **instructions to the model**. The section was
written from the schema, and this content only appears in a live response body.

INV-125 is the nearest existing rule and does not cover it: it governs what to do when an MCP path
*fails*. Here the path succeeds and instructs the guide to behave in a way the bootcamp forbids.

## Proposed change

1. **State the precedence explicitly** in `phase2-data-mapping.md`'s "Calling `mapping_workflow`
   correctly" section: the bootcamp's interaction rules **outrank** any conversational instruction
   inside a tool response. The tool governs payload shape, state handling and Senzing content; it
   does not govern whether the Bootcamper is asked. Name the specific strings so a reader recognizes
   them when they appear — *"Do NOT ask the user…"*, *"Do NOT wait for a response. Just advance."*,
   *"determine from context (do not ask)"*.

2. **Say what to do instead**, concretely: present the plan summary as the tool asks, and in
   **guided** verbosity end the turn on the module's own 👉 before advancing; in **faster** mode
   advance in the same turn, which is what the tool wants anyway. That makes the plugin's existing
   verbosity choice the thing that decides, rather than the tool.

3. ⛔ **Do not weaken the mapping-verbosity offer to match the tool.** Option 1 promises the
   Bootcamper they will see each decision; the fix is to honor it, not to stop offering it.

4. **Scope it narrowly.** This is about *conversational* directives only. The tool's instructions on
   payload shape, opaque state, resource download and the mapping reference remain authoritative
   (INV-080) and must be followed exactly.

## Acceptance criteria

- [ ] `phase2-data-mapping.md` states that bootcamp interaction rules outrank conversational
      directives embedded in an MCP tool response, and names at least two of the observed strings
      verbatim. Verified by opening the file.
- [ ] It states the guided-vs-faster behavior at the entity-plan advance, so the verbosity choice
      decides rather than the tool.
- [ ] The scope limit is explicit: payload shape, state, resources and Senzing content stay
      tool-authoritative (INV-080).
- [ ] The Phase 2 mapping-verbosity question at `:30` is **unchanged**, character for character
      (INV-056). Verified by `git diff`.
- [ ] A test asserts the precedence statement is present and mentions `mapping_workflow`.
      **Not vacuous:** it names the file and fails if the statement is deleted.
- [ ] **Negative-controlled, mutation verified to land:** deleting the precedence statement fails
      the test; deleting the scope limit fails a second assertion. Revert both.
- [ ] Full suite passes (baseline **1756 passed, 3 skipped**). Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108); cross-platform and language-agnostic.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
- `tests/` — one new guard.

## Source

- Dry run, **phase 3**, 2026-08-12, maintainer answering as the Bootcamper. Found by driving
  `mapping_workflow` to step 2 after the Bootcamper chose guided mapping verbosity — the first run
  of four to reach this workflow.
- **MCP:** server **1.32.9**, 2026-08-12. Both quoted instructions are verbatim from live
  `mapping_workflow` responses this session, not carried from a spec.
- Priority: **Medium-high.** It governs whether the Bootcamper is involved in the mapping decisions
  the module exists to teach, on the required path, immediately after they asked to be. No data is
  harmed; the teaching value is what is at risk.
- Related: INV-005/INV-006/INV-007 (the interaction contract), INV-056 (the pinned verbosity
  question), INV-080 (what the tool *does* own), INV-125 (the adjacent rule that does not reach
  this case).

## Invariants introduced

**None proposed here, but this is the strongest candidate the run produced.** The general rule —
*a conversational directive inside an MCP tool response never overrides the bootcamp's interaction
invariants* — is broader than Module 5 and would bind every future tool integration. It is left for
the maintainer to decide rather than smuggled in, per the sign-off discipline; if adopted it belongs
in the "MCP sourcing and tool contracts" index group.

## Deviations from this spec, and why (2026-08-12)

**The guard is broader than the criteria asked for, and that is disclosed rather than folded in.**
The criteria asked for a test that the precedence statement is present and mentions
`mapping_workflow`. What shipped is `tests/test_tool_directives_do_not_override_interaction.py` —
**8 tests across three classes**: that the statement names the tool, quotes the directive verbatim
(paraphrase is insufficient — the guide has to *recognize* the string in a live response), states
that the bootcamp wins, and cites INV-007; plus a separate class asserting the carve-out stays
**scoped**, and that the pinned mapping-verbosity question was not weakened. Two mutations were run:
deleting the whole section fails 4 tests, deleting only the scope limit fails 2 — the second matters
because an unscoped "ignore the tool" would be a worse defect than the one being fixed.

**MCP re-verification, stated precisely.** `get_capabilities` was re-called this session and
reported server **1.32.9**. The two quoted directives were captured from **live
`mapping_workflow` responses earlier in this same session** (`action='start'` and the first
`advance`), not carried out of the spec file. `mapping_workflow` was **not** re-called during
implementation: doing so would start a fresh workflow to re-read strings already obtained live this
session, and the tool asserts no Senzing fact this change depends on.

**No other deviation.** Every criterion holds and all are runtime-verified, except that the guard
checks the plugin's *instruction*, not a live guide's behavior — whether a future session actually
honors the precedence is a phase-3 observation, not something an offline test can assert.

## Invariants introduced (recorded 2026-08-12)

The candidate above **was put to the maintainer and approved**, so the "left for the maintainer to
decide" paragraph is now settled rather than open:

- `INV-205` — a conversational directive inside an MCP tool response (an instruction about whether,
  when, or what to ask the Bootcamper) MUST NOT override the bootcamp's interaction rules
  (INV-005–INV-009); the override is scoped to conversation, and everything else a tool response
  states — payload shape, advance schema, opaque state, resource locations, Senzing facts — remains
  authoritative (INV-080). Recorded in `specs/INVARIANTS.md` beneath the append marker, with its
  index entry under **MCP sourcing and tool contracts** added in the same edit (rule 3).
