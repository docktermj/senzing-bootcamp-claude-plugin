# Step 25's "do not ask" branch sits two lines above the pinned question it forbids

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

On a bootcamp-generated scenario, the guide asked the UAT stakeholder question that the same step
explicitly forbids on that path. The Bootcamper answered "no", which routes to the same
self-directed spot-check the generated branch prescribes, so no work was affected — but it was a
question they should never have seen, at the end of a long session, asking them to convene business
users for a business case the bootcamp itself invented. That is the re-litigation INV-006 and
INV-012 exist to prevent.

`module-06-data-processing/phaseD-validation.md:101-115`:

```text
## 25. Execute UAT with business users

**First, check whether there are real stakeholders.** … there are no business users to
involve — so **do not ask** the involvement question (INV-006/INV-012). State briefly that
the scenario is bootcamp-generated, so you will self-direct the UAT …

Otherwise (a real business problem with stakeholders), offer to involve business users — pin
the question verbatim:

👉 **Would you like to involve business users in testing the cross-source results?** (respond yes or no)
```

The prohibition and the forbidden question are **twelve lines apart**, and the question is the most
visually prominent text in the section: bold, 👉-prefixed, pinned verbatim, and sitting at the
section's **outer** level rather than inside the `Otherwise` branch that owns it.

## Root cause

**The generated branch has no question of its own, so the only pinned text on the page is the one
that must not be used.**

The reporter identified this precisely, and it is worth preserving because it explains why the same
layout is handled correctly elsewhere: *"The same shape appears in step 13 and step 15 … and I got
those right, which suggests what differs here: in those the confirm-instead-of-ask branch supplies
its **own** pinned question, so there is something to say. In step 25 the generated branch has no
question at all."*

So the failure is not carelessness about a prohibition — it is a layout in which the correct path
terminates in prose while the incorrect path terminates in the only 👉 on the page. A guide
assembling the turn reaches for the pinned text because pinned text is what INV-056 trains it to
reach for.

⚠️ **This is a skill-authoring shape, not a one-off.** The generated-scenario carve-out appears
wherever the Business Case Offer's marker is checked, and any step where a "do not ask" branch and a
pinned question share an outer level has the same exposure. The fix should be judged on whether it
removes the shape, not only this instance.

## Proposed change

1. **Move the pinned question inside the `Otherwise` branch** so it is structurally unreachable from
   the generated path — indentation carrying the same information the prose carries, which is what
   the correctly-handled steps 13 and 15 already do by supplying a question per branch.
2. **Add the marker check as a one-line precondition immediately above the question**, so a reader
   who arrives at the question directly — which is how a long-session guide arrives at it — meets
   the condition before the text. Belt and braces; the two remedies are not alternatives, and the
   entry proposes them as such.
3. **Sweep the class rather than the instance (INV-246).** Find every shipped step where a
   `do not ask` / `do not offer` instruction and a pinned 👉 question sit at the same outer level
   with no question on the suppressed path, derived by scanning for the shape, not from this spec's
   single example.
4. ⚠️ **Do not give the generated branch a question just to balance the shape.** It correctly ends
   without one — it proceeds to a self-directed spot-check and then to step 26. Manufacturing a
   question there to make the branches symmetrical would breach INV-006 in the opposite direction.

## Acceptance criteria

- [ ] On a `docs/business_problem.md` carrying `> 🤖 Bootcamp-generated business case`, step 25 asks
      no 👉 question and proceeds to the self-directed spot-check.
- [ ] The pinned question is structurally inside the real-stakeholders branch, and the marker
      condition is stated immediately above it.
- [ ] The generated branch still ends with **no** 👉 question (INV-006/INV-012), and a test asserts
      that rather than only asserting the real branch works.
- [ ] Every other shipped step with the same shape is found by a scan and fixed or recorded as
      already correct — the site set derived by scanning, not from this spec's list (INV-246).
- [ ] The question's verbatim wording is unchanged (INV-056).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — step 25,
  `:101-115`.
- Further shipped steps sharing the shape, to be identified by the sweep.
- `tests/` — guard for the generated-scenario path and for the class.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "the \"do not ask\" instruction sits directly above the pinned question it forbids" (2026-08-17, Module Query, Visualize and Discover per the entry — see the correction below; `Source: self-observed (assistant retrospective)`)
- Priority: **Medium.** One unnecessary question, no work lost, and it self-corrected on the answer. It earns a spec because the cause is a reusable layout rather than a slip, and because it is a conversational defect the offline suite cannot see.
- MCP re-check: **n/a (no Senzing fact).** Entirely a skill-authoring layout question about the plugin's own step. No SDK, flag, response shape or server behavior is asserted, and no absence about the server is relied on. Server **1.32.9** (`get_capabilities`, 2026-08-17) recorded for this run.
- Upstream: not applicable — routed `plugin` by the entry, and confirmed.
- Related specs: `specs/statement-only-step-cannot-satisfy-one-question-per-turn.md` and `specs/results-presentation-turns-end-with-zero-questions.md` (the neighboring class — a step whose branch legitimately ends without a question), `specs/encourage-own-business-case.md` and `specs/data-collection-does-not-recognize-a-synthesized-scenario.md` (other consequences of the bootcamp-generated marker), `specs/synthesized-scenarios-make-the-quality-gate-unreachable.md`, and INV-006, INV-012, INV-056, INV-246.

## One correction to the feedback entry

The entry files this under **Module: Query, Visualize and Discover**, `module / step:
query_visualize_discover / 25`, and names *"a skill-authoring layout issue in
`phase1-query-visualize.md` step 25"*. All three are wrong. Step 25 "Execute UAT with business
users" is in **Data processing** — `module-06-data-processing/phaseD-validation.md:101`. Searched:
`phase1-query-visualize.md` contains no stakeholder or business-user question at all, and the only
`👉 Would you like to involve business users…` in the shipped plugin is the one cited above.
Recorded so implementation does not open the wrong file on the entry's authority. (The step number
25 is correct, which is likely how the module was misattributed — both modules number past 20.)
