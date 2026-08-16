# A results-presentation step silently ends a non-yielding run with zero 👉 questions

## Problem

`bootcamp-onboarding/ground-rules.md:39-61` defines the non-yielding-step contract: a step with no
👉 question does not end a turn; it is presented in the same turn as the next step that *does* ask,
and that step's single 👉 ends the turn for both. The rule explicitly anticipates **runs** of such
steps and names examples (Module 1's 4a/4b/5/5a, System verification, Data collection's
generated-scenario path).

What it does not anticipate is *where inside such a run the guide actually stops*. On a `/dry-run`
phase 3 walk (2026-08-14) the same failure occurred **three times**, always in the same shape:

| # | Where | Steps in the run | Turn ended on |
|---|---|---|---|
| 1 | Module 6 Phase C | 17–20 (orchestrator, test, run, redo) | orchestration summary + record counts |
| 2 | Module 6 Phase D | 21–24 (match accuracy, UAT, cross-source, quality) | validation results + evidence tables |
| 3 | Module 7 Phase 1 | 2–3a (query programs, run queries, present results) | the five business answers |

Each time, the turn ended with **zero** 👉 questions, and the Bootcamper — the maintainer, playing
themselves — had to ask *"What's the question beginning with a 👉 that I should answer?"* Twice.

The common factor is not the length of the run. It is that each run **terminates in a step whose
output is a results presentation**: a summary block, an evidence table, a set of answers. That
output has the *shape* of a turn ending — it is substantial, it concludes something, and it reads as
complete — so the run stops there instead of continuing to the next asking step. In all three cases
the next 👉 was one or two steps further on (Phase C → Phase D's gate, Phase D → the decision gate
and transition question, Module 7 3a → 3b/3c).

This is the INV-005 violation the `Stop` hook exists to catch, and the hook does not fire in a walk
(`.claude/skills/dry-run/phase3-conversational.md` → "The hooks do not fire"). In a real bootcamp the
hook would paper over it — which means the underlying prompt weakness would never be observed, only
its symptom.

## Root cause

The non-yielding-step rule is stated as a property of the *step* ("has no 👉 question, so does not
end a turn"). Nothing in it addresses the property of the *output*: a step can be non-yielding and
still produce a page of results. The rule's own worked examples are all low-output steps — a privacy
reminder, a set of checks, a scenario generation — so the case where a non-yielding step produces a
conclusion-shaped block is never illustrated, and the guide's natural reading ("this is clearly the
end of something") wins over the rule.

The phases where it fired are exactly the ones whose late steps are all presentation: Module 6
Phase D is *entirely* validation reporting (steps 21–27, one conditional 👉 among them), and Module
7 step 3a is titled "Present query results".

## Proposed change

Add a short clause to `ground-rules.md`'s non-yielding-step section, immediately after the "run of
them is the same case" bullet:

- ⛔ **A results presentation is not a turn ending.** A non-yielding step that produces a summary,
  an evidence table, or a set of answers still does not end the turn — and it is the step most
  likely to be mistaken for one, because its output concludes something. Before ending any turn,
  confirm the turn carries exactly one 👉; if the step just presented has none, continue to the next
  asking step in the same turn.

Name the three observed sites in the phase files so the rule is reinforced where it breaks, one line
each, cross-referencing the ground rule rather than restating it:

- `module-06-data-processing/phaseC-multi-source.md` step 20 (redo) — the turn continues into Phase D.
- `module-06-data-processing/phaseD-validation.md` steps 21–24 — the turn continues to the decision
  gate.
- `module-07-query-visualize-discover/phase1-query-visualize.md` step 3a — the turn continues to 3b/3c.

## Acceptance criteria

- `ground-rules.md`'s 👉-protocol section states that a results-presentation step is still
  non-yielding and names it as the likeliest false turn-ending.
- Each of the three phase files carries a one-line pointer at the identified step.
- A test asserts the ground-rules clause exists (searching for the results-presentation wording), so
  it cannot be dropped in a later consolidation.

## Caveat on the evidence

⚠️ This is **one walk and one guide**, and `phase3-conversational.md` is explicit that "the
assistant's own compliance is not evidence" — a clean stretch proves little, and so does a failing
one. What raises this above a single slip is that it recurred **three times in three different
phases with the same structural signature**, and that the two phases where it fired are the two with
the longest presentation-only step runs in the plugin. A second walk hitting the same sites would
settle it; a second walk that does not should downgrade this to a note.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md`
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md`
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md`
- `tests/test_ground_rules_nonyielding_presentation.py` (new)

## Source

`/dry-run` phase 3, 2026-08-14. Analysis started at Data processing. Three occurrences observed
directly, two of them surfaced by the maintainer asking which question was pending.

## Deviations from this spec, and why (2026-08-14)

Implemented as proposed — the clause wording, the three site pointers, and the test are all as
specified. Three things are worth recording rather than left implicit.

1. **Establishes no invariant, deliberately.** The candidate — *a non-yielding step whose output
   is a results presentation still does not end the turn* — is a restatement of **INV-225**, which
   already makes a step with no 👉 non-yielding and forbids it ending a turn, and of **INV-005**,
   which requires exactly one 👉 per yielding turn. Nothing here is a new standing rule: the
   failure was not a missing rule but a rule whose worked examples were all low-output steps, so
   the case that actually breaks it was never illustrated. That is a documentation gap in an
   existing invariant, and minting a second ID for it would split one rule across two addresses.
   The clause cites INV-005 at the action it requires.

2. **The evidence caveat is unresolved and is carried into the shipped guard.** The spec is
   explicit that this is one walk and one guide, and that a second walk not hitting these sites
   should downgrade it to a note. Nothing in this implementation settles that. The test file's
   docstring carries the caveat verbatim so a later reader meets it at the guard rather than
   having to find this spec. The change is safe under either outcome — it adds a clause and three
   cross-references to a rule that already exists, and removes nothing.

3. **The pointers cite rather than restate**, and a test enforces that (`test_no_pointer_restates_
   the_rule_instead_of_citing_it`). The spec asks for "one line each, cross-referencing the ground
   rule rather than restating it"; a restated rule in four places is four things to keep in sync,
   which is the drift this repo has recorded before. The pointers therefore name the step run and
   the ground rule, and nothing else.
