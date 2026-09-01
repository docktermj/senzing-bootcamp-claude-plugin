# Step 15's "both versions visible" gate is unsatisfiable on a generated scenario

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-01-business-problem/phase2-document-confirm.md` Step 15 opens with a ⛔:

> **(INV-275) Present the document with BOTH versions visible, and say which is which.** Before
> asking, state plainly that the `> "…"` lines are their own words as they said them and the prose
> above each is your rendering of it — and that a mismatch between the two is exactly what this
> question is for. Without that, the gate asks *"does this plausible-sounding text sound right?"*
> rather than *"does this match what I said?"*, and a single substituted adjective inside an
> otherwise-accurate sentence survives it.

On the **generated-scenario** path there is no second version, so the instruction cannot be
followed. Step 11's own rule is what removes it:

> ⚠️ **Where an answer was a selection rather than prose, OMIT the quote — never manufacture one.**
> Drop the `> "…"` line entirely for that section.

All five quote-carrying sections are selections or bootcamp-authored on that path. Observed live on
2026-08-31, on a walk that accepted the Business Case Offer: Problem Description and Success
Criteria were **written by the bootcamp**; Desired Output came from a bare option reply ("1 and 3");
Integration Requirements from a bare "no"; Notes had no interview prose at all. The resulting
`docs/business_problem.md` carries **zero** `> "…"` lines — correctly, per Step 11 — and Step 15
then asks the guide to present "BOTH versions" of a document that has one.

This is not a path the plugin treats as unusual. The Business Case Offer is one of three options at
Step 4 and is the designated route for any Bootcamper without their own data, which the module
describes as the case that lets them "complete the full bootcamp".

**The risk INV-275 exists to catch is still live on this path.** The Step 11 document is a rendering
of the scenario the Bootcamper approved at Steps 4a/6a, and it can drift from it in exactly the
documented way. In the observed walk the reply "1 and 3" was rendered as
`**Format**: Master list and Reports`; rendering it as `Master list` alone would have written a
narrowed requirement into the document that steers Module 7's query requirements, and Step 15 would
have asked the Bootcamper to confirm plausible-sounding text with nothing to check it against —
precisely the failure the ⛔ describes, reached by a different route. (The single-select framing that
invites that narrowing is filed separately as
`specs/desired-outcome-question-is-single-select-for-a-multi-valued-answer.md`.)

⚠️ This is the **unsatisfiable-instruction** class rather than a wrong instruction: the guide is told
it must do something and provably cannot. Left as-is it teaches that a ⛔ can be quietly skipped when
it does not fit, which costs more than the gate itself.

## Root cause

`phase2-document-confirm.md` Step 15's ⛔ was written for the Bootcamper-described path, where the
`> "…"` lines always exist. It has no generated-scenario branch, though Steps 9 and 11 both have one
(9a/9b, and Step 11's "Generated scenario (Business Case Offer accepted)" block) — so the branching
convention is already established in this file and simply was not applied at 15.

The comparison target on the generated path is not missing, only different: it is the scenario text
the Bootcamper confirmed at Step 4a ("Does that scenario work for you?") and the summary they
confirmed at Step 6a — both approved in conversation, and the second of which the file already
prescribes as a structured summary.

## Proposed change

1. Branch Step 15 the way Steps 9 and 11 already branch.

   - **Bootcamper-described case** — unchanged.
   - **Generated scenario** — state that the document is a rendering of the scenario they approved
     earlier, and name what to check it against: the confirmed scenario and the Step 6a summary,
     with particular attention to the fields derived from bare option replies (Desired Output,
     Integration Requirements), since those are the ones with no prose to compare against.

2. Say explicitly that a document with **no** `> "…"` lines is the expected, correct outcome on the
   generated path — not a Step 11 failure to be repaired by manufacturing quotes. Without this, the
   most likely reaction to the contradiction is to invent the quotes Step 11 forbids, which is worse
   than either alternative.

3. Leave the pinned question at Step 15 untouched (INV-056). What changes is the framing above it,
   which the step already says is the part that varies.

## Acceptance criteria

- [ ] Step 15 carries a generated-scenario branch, and following it on a generated scenario requires
      no instruction the path cannot satisfy.
- [ ] The step states that zero `> "…"` lines is correct on the generated path, and that quotes are
      never manufactured to satisfy the gate.
- [ ] The generated branch names a concrete comparison target — the confirmed scenario and the
      Step 6a summary — so the gate still asks "does this match what was agreed?" rather than "does
      this sound right?".
- [ ] The pinned question at Step 15 is unchanged (INV-056).
- [ ] The Bootcamper-described branch behaves exactly as today.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — Step 15:
  add the generated-scenario branch.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, Discover the Business Problem Step 15
  (`Source: self-observed (assistant retrospective)`) — found by generating the Step 11 artifacts on
  the Business Case Offer path and then reaching a gate that asks for a second version the path does
  not produce.
- Priority: Medium
- MCP re-check: n/a (no Senzing fact).
- Upstream: not applicable
- Related specs: `specs/desired-outcome-question-is-single-select-for-a-multi-valued-answer.md` — the
  narrowing risk this gate would fail to catch.
