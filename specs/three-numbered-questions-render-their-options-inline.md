# Three numbered-choice questions render their options inline, against a "no exception" rule

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`ground-rules.md` → the 👉 protocol states, as a ⛔:

> **A 👉 question's answer options render DIRECTLY BENEATH it — pinned or generated at runtime, no
> exception.** The rule above permits the options to follow the question; this one requires it, **so
> two readers cannot render the same gate two ways.** A question that says "reply with a number"
> above a list the bootcamper has already scrolled past is asking them to answer upwards.

Three shipped questions put their options on the 👉's own line instead:

| File | Line | Question |
|---|---|---|
| `skills/module-01-business-problem/phase1-discovery.md` | 354 | `👉 **Which records are you working with? Reply with a number:** (1) people, (2) organizations, (3) both.` |
| `skills/module-01-business-problem/phase1-discovery.md` | 356 | `👉 **What does the end result look like? Reply with a number:** (1) a clean master list, (2) an API, (3) reports, (4) something else.` |
| `skills/bootcamp-onboarding/feedback.md` | 78 | `👉 **What priority would you give this? Reply with a number:** (1) High, (2) Medium, (3) Low.` |

The class is small and bounded: **3 of the 40** `Reply with a number` questions across the shipped
skills. The other 37 render a list beneath the question, including `feedback.md`'s **own** Step 3c
upstream gate two screens below the offender, and all four Bootcamp preparation gates.

The consequence is the exact one the ⛔ names. Encountering `phase1-discovery.md:356` in a live walk,
a guide has two defensible renderings — reproduce the shipped inline form, or apply the ⛔ — and
nothing decides between them, so the same gate renders two ways depending on which file the guide
weighted. INV-224 ("the question says reply with a number, so the numbers must follow it") is
satisfied by both readings, which is why it does not break the tie.

Severity is low in isolation and worth fixing anyway: a placement rule that says "no exception" and
has three exceptions teaches that ⛔ rules are approximate, which is the failure mode
`ground-rules.md` explicitly worries about elsewhere ("a guide that internalized it that way…", "it
trains the model to treat the surrounding instructions as advisory").

## Root cause

The three questions were written as inline prose. None of them is pinned — none carries an INV-056
citation, and none appears in a "verbatim" block — so nothing forced the inline shape and nothing
protects it.

Nothing detects the divergence, and the reason is structural: **the rule lives in `ground-rules.md`
and the violations live in two other files.** A section-scoped conformance scan is satisfied by any
`INV-NNN` in the surrounding section, and both ends independently cite invariants, so the pair is
never compared. This is the same shape recorded for INV-212 — a rule stated in one place and
binding on a step somewhere else — and it is why a phase-3 walk, rather than a static audit, is what
surfaced it.

## Proposed change

1. Re-render all three questions with their options as a numbered list directly beneath the 👉,
   matching the 37 that already do:

   ```markdown
   👉 **What priority would you give this? Reply with a number:**

   1. **High**
   2. **Medium**
   3. **Low**
   ```

2. Add a repo-level guard: a test that greps the shipped skills for a 👉 line carrying its own
   options and fails naming each file and line. The pattern is cheap and specific —
   a line containing `👉` and `Reply with a number:` followed on the same line by `(1)` — and the
   population it guards is 40 questions, so it cannot drift far before firing. Stdlib only, no
   `plugins/` import (INV-108).

⚠️ **Do not pin any of these three questions as part of this change.** They are unpinned today; the
fix is placement, and adding an INV-056 pin would freeze wording that nothing has reviewed for
pinning.

## Acceptance criteria

- [ ] All three questions render their options as a numbered list directly beneath the 👉.
- [ ] `grep -rn "👉.*Reply with a number:\*\*[[:space:]]*(1)" plugins/` returns nothing.
- [ ] A repo-level test fails when a 👉 question carrying inline options is reintroduced, and names
      the offending file and line. Negative-controlled: reintroduce one of the three, confirm the
      test fails, revert.
- [ ] No question in this change acquires an INV-056 pin.
- [ ] The 37 already-correct questions are untouched.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — lines 354, 356.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` — line 78.
- `tests/test_question_options_render_beneath.py` (new) — the guard.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31 (`Source: self-observed (assistant
  retrospective)`) — found by *executing* `feedback.md` Step 2 rather than reading it, then grepping
  for the class, which turned one instance into three.
- Priority: Low
- MCP re-check: n/a (no Senzing fact) — this is entirely the plugin's own interaction specification.
- Upstream: not applicable
- Related specs: `specs/feedback-step-2-mishandles-a-partial-feedback-report.md` (the other defect in
  the same passage; different root cause, filed separately)

## Deviations from this spec, and why (2026-09-01)

**None to the substance.** All three questions re-rendered, the guard added, no question pinned.

**One point worth recording for the next reader:** the guard's matcher is anchored on `(1)`
following a 👉 **on the same line**, not on any question wording — the phrasings already seen are
what INV-282 warns against pinning. Three correctly-rendered questions are pinned as **must-not-match
fixtures** beside the historical inline shape, including the comma-separated multi-select idiom and
an open-ended 👉 with no options at all, so a later widening that starts flagging compliant prose
fails here rather than being absorbed.

**Landed in one commit with `desired-outcome-question-is-single-select-for-a-multi-valued-answer`.**
Both specs rewrite Step 6d's line; this one changes its shape, the other changes what it asks.
