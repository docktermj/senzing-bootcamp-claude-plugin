# Entity Resolution Concepts module: invite questions/discussion before the quiz offer

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

In the Entity Resolution Concepts module (Module 0), immediately after the primer
the bootcamp jumps straight to the optional quiz offer ("👉 Would you like to test
your knowledge of entity resolution with a short quiz?"). The bootcamper wants a
step **before** the quiz offer that asks whether they have any questions about
entity resolution or want to discuss the concepts first — so learners get space to
clarify before being asked to self-test.

The module *does* invite questions, but only later, inside the mandatory
exploration/readiness gate that comes **after** the quiz offer — so the very first
thing offered after the primer is the quiz, not an opening to ask.

## Root cause (confirmed)

The Module 0 flow is sequenced primer → quiz offer → exploration gate, with the
only "ask me anything" invitation buried in the gate:

- Primer content: `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md:40-56`.
- Optional quiz offer immediately follows the primer: `concepts.md:58-89` ("After
  the primer and before the mandatory exploration gate below, offer an optional
  short quiz").
- The questions/discussion invitation lives only inside the mandatory exploration
  gate, *after* the quiz: `concepts.md:91-100` ("invite the bootcamper to explore
  before moving on. Offer example questions…").
- The step outline in `SKILL.md:31-49` mirrors this order (Step 3 = quiz, Step 4 =
  exploration gate); there is no step between the description and the quiz.

So no defect — it is a sequencing choice: there is no dedicated questions/discussion
prompt between the primer and the quiz offer.

## Proposed change

In `concepts.md`, insert a new step **between** the primer ("How Senzing handles it",
ending ~`:56`) and the "Optional knowledge-check quiz" section (`:58`): after the
primer, invite the bootcamper to ask questions or discuss the concepts, then end the
turn on a single pinned 👉 yes/no question. Handle any question the bootcamper raises
using the module's **existing** MCP-verified Q&A rules (`concepts.md:32-38` and
`:113-115`): research via `search_docs`, confirm with a second MCP call, present, and
re-offer. When the bootcamper has no (further) questions, proceed to the quiz offer,
then the mandatory exploration/readiness gate, unchanged. Update the `SKILL.md:31-49`
step outline to add this step ahead of the quiz.

Design constraints to respect (surface, do not paper over):

- The new question is a 👉 question (INV-005), asked once (INV-006), with exactly one
  meaning for "yes" and one for "no" (INV-008) and **no "or"-joined choices**
  (INV-051/INV-009). The bootcamper's own phrasing ("questions … or want to discuss
  something") joins two intents with "or" — the pinned wording must collapse that into
  one intent (e.g. "👉 Do you have any questions about entity resolution before we
  continue?"), treating "discuss" as part of the same invitation, not a second branch.
- Pin the wording verbatim (INV-056), consistent with the module's other pinned
  questions (the quiz offer and the readiness gate).
- Do **not** duplicate or weaken the mandatory exploration/readiness gate (INV-073) —
  it remains the module's exit. Reconcile the end gate's existing "invite to explore"
  framing (`concepts.md:93-100`) so the bootcamper is not effectively asked the same
  "any questions?" thing twice (INV-006 in spirit); the pre-quiz step covers "clarify
  the concepts now", the end gate remains "ready to move on?".
- Keep it MCP-only for any answers (INV-080 / the file's verify rule); no training-data
  fallback. It is a lightweight, non-blocking step (Module 0 stays a preamble,
  INV-078); exactly one 👉 ends each yielding turn (INV-005).

## Acceptance criteria

- [ ] After the primer and **before** the quiz offer, Module 0 asks a single pinned-verbatim (INV-056) 👉 question inviting the bootcamper to ask questions / discuss entity resolution, with exactly one yes/no meaning (INV-008) and no "or"-joined choices (INV-051/INV-009).
- [ ] Any question the bootcamper asks at this step is answered under the existing MCP-research-then-verify rule (`concepts.md:32-38`), MCP-only with no training-data fallback (INV-080); the step never blocks and, when the bootcamper is done, flows into the quiz offer.
- [ ] The mandatory exploration/readiness gate (INV-073, "Are you ready to move on to the next module: Discover the Business Problem?") is unchanged and remains the module's exit; the new step does not cause the same "any questions?" invitation to be asked twice (INV-006).
- [ ] Exactly one 👉 ends each yielding turn (INV-005); Module 0 remains a lightweight preamble with no per-module completion apparatus (INV-078).
- [ ] The `SKILL.md` step outline reflects the new step ahead of the quiz.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md` — insert the questions/discussion step (pinned 👉 question + MCP-verified handling) between the primer (`:40-56`) and the quiz offer (`:58`); reconcile the end-gate "invite to explore" framing (`:93-100`) so questions are not invited redundantly.
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md` — add the new step to the Step 1 outline (`:31-49`) ahead of the quiz step.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Ask for questions/discussion before the ER concepts quiz" (2026-07-20, Module 0 — Entity Resolution Concepts)
- Priority: Not specified (bootcamper did not state one)
- Related specs: `concepts-module-verified-qa-and-quiz.md` (added the quiz + MCP-verified Q&A this step reuses and sits before), `entity-resolution-module-zero.md` (INV-073 Module 0 structure / explore gate), `onboarding-explore-gate-wording.md` (INV-056 pinned gate wording), `mcp-grounding-in-every-skill.md` (INV-080).
