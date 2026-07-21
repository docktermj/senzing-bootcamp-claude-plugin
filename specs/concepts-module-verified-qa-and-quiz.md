# Entity Resolution Concepts module: MCP-verified Q&A and an optional knowledge-check quiz

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Two related requests for the Entity Resolution Concepts module (Module 0):

1. **Verified Q&A** — the bootcamper wants every answer to a bootcamper-asked
   question to be both researched via the Senzing MCP server **and separately
   verified** against the MCP server before being presented — not just researched
   once and presented as-is — "to make sure answers are accurate, not just
   plausible."
2. **Optional quiz** — right before the module's final readiness gate, offer an
   optional short quiz: "👉 Would you like to test your knowledge of entity
   resolution with a short quiz? (It may help you understand entity resolution
   better; worth a try!)". On accept, pose questions and evaluate the responses; the
   bootcamper must be able to exit at any time. Questions should start at **moderate**
   difficulty (not trivially easy) to keep the bootcamper engaged and curious.

The two are coupled: the quiz's questions/answers should be sourced and verified via
the MCP server per request (1).

## Root cause (confirmed)

- Follow-up questions are answered from a **single** MCP call with no verification
  pass: `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md:71-72`
  — "answer it via `search_docs`, then re-present the pinned gate question." The
  general facts-from-MCP rule (`concepts.md:18-30`) is likewise single-source.
- There is **no quiz mechanism** anywhere in `concepts.md`; the module ends directly
  on the mandatory exploration/readiness gate ("👉 Are you ready to move on to
  Module 1?", `concepts.md:63`, section `concepts.md:50-79`).

## Proposed change

1. **Verified Q&A.** In `concepts.md` (the follow-up handling at `:71-72` and,
   broadly, the module's Q&A), add an explicit verification step: after drafting an
   answer from an initial MCP call, make a second MCP call to confirm/cross-check the
   claim before presenting it, rather than presenting the first result directly.
   Keep it MCP-only (no training-data fallback) and non-blocking on the readiness
   gate. (Note trade-off: this adds an MCP round-trip per follow-up; scope it to
   substantive entity-resolution claims, not conversational replies.)
2. **Optional quiz.** In `concepts.md`, after the primer content and **before** the
   mandatory readiness gate (`:50-79`), add a pinned-verbatim (INV-056) optional
   quiz offer as its own single-meaning 👉 question. On accept: ask a short series of
   entity-resolution questions (sourced/verified via the MCP server per change 1),
   evaluate each answer, and let the bootcamper **exit at any time** back to the
   readiness gate. Calibrate initial difficulty to **moderate** (not the easiest
   tier). On decline: proceed straight to the readiness gate as today. The quiz is
   optional and never blocks; the mandatory readiness gate remains the module's exit.

## Acceptance criteria

- [ ] Answers to bootcamper follow-up questions in Module 0 are verified with a second MCP call before being presented; no substantive entity-resolution claim is presented from a single unverified call, and no training-data fallback is used.
- [ ] Before the readiness gate, Module 0 offers an optional quiz via a pinned-verbatim (INV-056), single-meaning (INV-008), 👉 question with no "or"-joined choices (INV-051).
- [ ] On accept, the quiz poses MCP-sourced/verified questions, evaluates answers, starts at moderate difficulty, and lets the bootcamper exit at any time back to the readiness gate; on decline, the flow proceeds to the readiness gate unchanged.
- [ ] The quiz never blocks progress and does not replace the mandatory readiness gate ("👉 Are you ready to move on to Module 1?", INV-073); exactly one 👉 ends each yielding turn (INV-005).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md` — add the verification step to follow-up handling (`:71-72`) and the general Q&A rule (`:18-30`); add the optional quiz offer + loop before the readiness gate (`:50-79`).
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md` — reflect the quiz step in the module's step outline (`:44-48`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Require every bootcamper Q&A in the Entity Resolution Concepts module to be MCP-researched and MCP-verified" (2026-07-18, Module 0; priority not stated — bootcamper moved on before answering); "Add an optional knowledge-check quiz at the end of the Entity Resolution Concepts module" (Module 0, Medium).
- Priority: Medium (quiz); pending/low (verified Q&A — priority not given).
- Related specs: `entity-resolution-module-zero.md` (INV-072/073, Module 0 structure), `mcp-grounding-in-every-skill.md` (per-skill MCP rule, distinct), `customizable-module-selection.md` (Module 0 becomes a selectable module).
