# The desired-outcome question is single-select, but its options are complements

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-01-business-problem/phase1-discovery.md` Step 6d asks:

> 👉 **What does the end result look like? Reply with a number:** (1) a clean master list, (2) an
> API, (3) reports, (4) something else.

"Reply with a number" is singular, but the options are **complements, not alternatives**. A clean
master list, an API over it, and reports off it are the three normal deliverables of the same
entity-resolution project, and most organizations want more than one.

Observed live on 2026-08-31: asked this question in a walk, the Bootcamper answered **"1 and 3"**.
That is a cooperative, coherent answer — not a bootcamper ignoring the format — and the shipped
question has no way to record it.

The sibling question three lines above shows the plugin already recognized this problem in the same
passage and solved it there:

> 6b (record types): 👉 **Which records are you working with? Reply with a number:** (1) people,
> (2) organizations, (3) both.

Step 6b has an explicit **"both"** because record types are plainly multi-valued. Step 6d has no
equivalent, though its options are no less combinable.

The answer is not discarded when this happens — it flows into `docs/business_problem.md` under
**Desired Output** (Phase 2 Step 11), and from there into the stakeholder summary and graduation. A
question that can only record one of the Bootcamper's two answers writes an incomplete requirement
into the document the rest of the bootcamp is steered by.

## Root cause

`plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:356` — the question
was written in the single-select idiom, and nothing in Step 6 says what to do with a multi-valued
reply. The guide must either silently drop one of the Bootcamper's choices, or improvise the
handling.

The plugin has an established multi-select idiom and it is not used here.
`bootcamp-preparation/SKILL.md` Step 2 renders one, including the INV-051-compliant way to express
"none" without an "or":

> 👉 **Which optional modules would you like to include? Reply with the numbers from the list below,
> comma-separated — reply "none" for just the required modules:**

## Proposed change

1. Re-render Step 6d as a multi-select, reusing the Bootcamp preparation idiom so there is one
   multi-select shape in the plugin rather than two:

   > 👉 **What does the end result look like? Reply with the numbers from the list below,
   > comma-separated:**
   >
   > 1. **A clean master list**
   > 2. **An API**
   > 3. **Reports**
   > 4. **Something else**

   Options beneath the 👉, per `ground-rules.md`'s placement rule — see
   `specs/three-numbered-questions-render-their-options-inline.md`, which covers this same line for
   a different reason. **The two changes touch the same line and should land together.**

2. State in one line that Step 11's **Desired Output** section records every option chosen, so a
   multi-valued answer survives into `docs/business_problem.md` rather than being narrowed to the
   first.

⚠️ Leave Step 6b alone. Its "both" option already covers its combinations, and record types are a
closed three-way set rather than an open list.

## Acceptance criteria

- [ ] Step 6d asks for comma-separated numbers, using the same wording shape as Bootcamp
      preparation Step 2, with no "or" joining the choices (INV-051).
- [ ] A multi-valued answer ("1 and 3", "1,3") is recorded in full in `docs/business_problem.md`
      under **Desired Output** — no chosen option is dropped.
- [ ] Step 6b is unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — line 356:
  re-render 6d as a multi-select.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — Step 11:
  one line confirming Desired Output records every chosen option.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, Discover the Business Problem Step 6d
  (`Source: self-observed (assistant retrospective)`) — surfaced by the maintainer answering the
  question naturally, in character, with two numbers.
- Priority: Low
- MCP re-check: n/a (no Senzing fact).
- Upstream: not applicable
- Related specs: `specs/three-numbered-questions-render-their-options-inline.md` — same line, different
  root cause; land them together.
