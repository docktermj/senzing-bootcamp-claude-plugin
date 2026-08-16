# Phase C steps 13 and 15 each pin their own confirm question, and on the generated path they fire back to back

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

In Data processing (Module 6) Phase C, a Bootcamper on the generated-scenario path was asked two
consecutive yes/no questions, each of which stated its own answer before asking:

1. 👉 **The generated sources have no load-order dependencies — shall I proceed with none?** → yes
2. 👉 **I recommend the Sequential loading strategy for this generated dataset — shall I use it?**

The Bootcamper interrupted at the second to file this: *"it slows the flow with pointless
confirmations."*

Both facts were already established from provenance — all three sources were `provenance:
synthesized` and `docs/business_problem.md` carried the `> 🤖 Bootcamp-generated business case`
marker — so each question is a rubber stamp, and the Bootcamper was given no new information
between them on which to answer either differently.

## Root cause

Two independently-authored confirm gates on the same path, with nothing between them and nothing
reconciling them.

- `module-06-data-processing/phaseC-multi-source.md:42` — step 13's generated-path question.
- `module-06-data-processing/phaseC-multi-source.md:80` — step 15's generated-path question.
- Step 14 (`:60-68`, "Determine load order") sits between them and **asks nothing** — it presents a
  recommended order for review. So the two questions are consecutive in the Bootcamper's
  experience even though they are two steps apart in the file.

Both were introduced by the same spec, `provenance-aware-phasec-load-questions`, whose acceptance
criteria treat them as two separate sites: *"Steps 13 and 15 present a proposed answer … via a
single pinned confirm-style question"* — "a single … question" **per step**, never a budget across
the pair. Each step is individually compliant with what that spec asked for, and the pair is what
the Bootcamper experiences.

**The behaviour is exactly what the skill files prescribe**, which is why this is a design issue
rather than a deviation: nothing here is a misreading of the text.

## The invariants pull in opposite directions, and the spec must say so

- **INV-012** — output that is not important to the Bootcamper is suppressed. `ground-rules.md`
  warns against confirmation gates whose only realistic answer is "yes", and each step's own text
  concedes the plugin already knows the answer on this path (`:39`, `:77` — "State that briefly
  (INV-012) and confirm rather than asking an open question").
- **INV-007** — *All questions MUST be answered by the Bootcamper. The plugin cannot answer
  questions nor assume answers.* This is why `provenance-aware-phasec-load-questions` kept a
  confirm rather than proceeding silently, and it is the reason the Bootcamper's second suggested
  fix cannot simply be taken.

⛔ **So the Bootcamper's "proceed without asking on the generated-scenario path" option is NOT
available as stated**, and this spec does not adopt it. Recording that explicitly, per the
feedback-to-specs guardrail that a conflict with an invariant is stated in the spec rather than
silently overridden. Their **first** option — combine the two into one question — satisfies both
invariants: the decision is still the Bootcamper's, no answer is assumed, and the turn count drops
from two to one.

## Proposed change

1. **Merge the two generated-path confirmations into one pinned question**, presented at step 13,
   covering both facts and both proposed answers. Sketch (exact wording to be pinned, INV-056):

   > 👉 **The generated sources have no load-order dependencies, and I recommend the Sequential
   > loading strategy for this dataset — shall I proceed on both?** (respond yes or no)

   ⚠️ **This is a two-part question and INV-008/INV-009 bind it.** It must be unambiguous with
   respect to yes/no and must not be "complex". Verify the final wording against both before
   pinning; if a single unambiguous question cannot be written, keep two and drop one of them to a
   *stated decision with an offered override* rather than a gate — say which invariant drove the
   choice either way.
2. **On "no", present both overrides in sequence** — ask for the dependency map (step 13's existing
   no-branch, `:44-45`) and then the numbered strategy menu (step 15's existing no-branch, `:82-83`
   → `:89-93`). The override the step-15 text relies on ("a *no* routes to the full strategy menu")
   is preserved in full; only the yes-path turn count changes.
3. **Leave the Bootcamper-supplied path untouched.** `:47-54` and `:85-95` ask genuinely open
   questions of someone who is the only one who knows the answers. Nothing in this spec reaches
   them.
4. **Record where the merged question lives.** Step 15's provenance branch should route to the
   answer already captured at step 13 rather than re-deciding, so the merge cannot regrow into two
   gates the next time either step is edited.

## Acceptance criteria

- [ ] On the generated path (every loaded source `provenance: cord`/`synthesized`, or the
      generated marker present), Phase C poses **one** confirm question covering both the
      dependency and the strategy decision, not two.
- [ ] The merged question is pinned verbatim (INV-056), preceded by 👉 (INV-005), and is
      unambiguous with respect to yes/no (INV-008) and not complex (INV-009).
- [ ] The Bootcamper still answers it; no answer is assumed or self-supplied (INV-007).
- [ ] A "no" reaches **both** existing overrides — the dependency-map capture and the full
      numbered strategy menu (INV-007, INV-051).
- [ ] The Bootcamper-supplied path still asks steps 13 and 15 as two separate open questions,
      unchanged.
- [ ] A test asserts the generated path carries exactly one 👉 question across steps 13–15, so a
      later edit to either step cannot silently restore the pair.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md` — the step 13
  generated branch (`:34-45`) and the step 15 generated branch (`:72-83`).
- `tests/` — new or extended guard counting generated-path questions across the step range.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Two consecutive self-answered confirmations in Data processing Phase C" (2026-08-15 23:52 EDT, Module `data_processing` Phase C; `Source: bootcamper`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact). Neither question depends on the Senzing MCP server; the entry's own routing note records that a perfect server would not change this.
- Upstream: not applicable — routed `plugin`, so no `submit_feedback` submission is offered.
- Related specs: `specs/provenance-aware-phasec-load-questions.md` (introduced both gates; its per-step acceptance criteria are the mechanism), `specs/skip-business-user-uat-for-generated-scenario.md` (the same provenance-guard pattern in Phase D), `specs/drop-checklist-and-summary-gates.md`

## The general shape, worth carrying into the fix

Each gate was written to a per-step budget of one question. Nothing in either spec or either step
counts questions **across** steps on a path where several such gates fire in a row, so a path can
accumulate rubber stamps one defensible step at a time. Phase C is where two happen to be adjacent;
the fix should say so at the step, so the next provenance-aware confirm added to this phase is
weighed against the ones already there rather than only against itself.
