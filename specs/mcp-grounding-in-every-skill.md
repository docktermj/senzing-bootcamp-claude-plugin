# Restate the MCP-grounding / no-speculation requirement explicitly in every skill

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The MCP-first invariant (all Senzing facts come from the Senzing MCP server, never
from training data or speculation) lives in `ground-rules.md` and is referenced by
the module skills, but is not restated as an explicit requirement inside every
individual skill. The bootcamper wants the requirement added directly to all skills
so no module can ignore or overlook it — "a rule enforced only by reference risks
being missed in an individual skill."

## Root cause (confirmed)

The rule is centralized and only pointed at, not duplicated per-skill:

- The full rule (absolute-precedence clause, pre-response checklist, tool routing,
  MCP-failure handling) lives **only** in
  `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:52-70`
  ("## MCP-first invariant (absolute precedence)").
- Each module SKILL.md merely names it in a one-line pointer, e.g.
  `module-01-business-problem/SKILL.md:8-11`, `module-02-sdk-setup/SKILL.md:8-12`,
  `module-03-system-verification/SKILL.md:8-12` — all "Follow
  ../bootcamp-onboarding/ground-rules.md throughout (👉 one-question-at-a-time,
  MCP-first, file placement, checkpointing)". Beyond that pointer, MCP grounding
  appears only as scattered per-step tool directives.
- Module 3 uniquely adds a domain-specific MCP-precedence subsection
  (`module-03-system-verification/SKILL.md:51-71`), but even that does not restate
  the general pre-response checklist.

So an implementer editing a single skill sees only "MCP-first" as a word, not the
enforceable rule or the pre-response checklist.

## Proposed change

Add an explicit, prominent MCP-grounding / no-speculation clause to **every** skill
file — all `module-0X-*/SKILL.md` (and their phase/reference files that drive
responses), `bootcamp-onboarding`, and `graduation` — not only a pointer to
`ground-rules.md`. To keep the wording consistent and prevent drift, author it once
as a **shared snippet** and inline/reference it at the top of each skill. The clause
must state that all Senzing facts, SDK method names, attribute names, config
options, and error codes come from the Senzing MCP tools, that the skill must never
speculate or fall back to training data, and it must carry the pre-response
checklist ("if the response contains Senzing specifics, an MCP tool must have been
called this turn"). `ground-rules.md:52-70` stays the canonical source of truth.

## Acceptance criteria

- [ ] Every skill that produces bootcamper-facing Senzing content (all `module-0X-*` SKILL.md and response-driving phase files, `bootcamp-onboarding`, `graduation`) carries an explicit MCP-grounding / no-speculation clause including the pre-response checklist — not merely the word "MCP-first" pointing at `ground-rules.md`.
- [ ] The clause wording is identical across skills (authored once as a shared snippet / single source, inlined or referenced) so it cannot drift; `ground-rules.md:52-70` remains the canonical definition.
- [ ] The clause is prominent (near the top of each skill), not buried in per-step directives.
- [ ] Existing per-step tool-routing directives and Module 3's TruthSet MCP-precedence subsection are preserved.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — canonical clause (`:52-70`); optionally define the shared snippet here.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/SKILL.md`, `module-02-sdk-setup/SKILL.md`, `module-03-system-verification/SKILL.md`, `module-04-data-collection/SKILL.md`, `module-05-data-quality-mapping/SKILL.md`, `module-06-data-processing/SKILL.md`, `module-07-query-visualize-discover/SKILL.md`, `module-00-entity-resolution-concepts/SKILL.md`, `graduation/SKILL.md`, `bootcamp-onboarding/SKILL.md` — add the explicit clause near the top.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Add an explicit MCP-grounding / no-speculation requirement to EVERY skill" (2026-07-18, General/all skills).
- Priority: High.
- Related specs: `visible-mcp-source-attribution.md` (surfacing grounding to the bootcamper, distinct), `concepts-module-verified-qa-and-quiz.md` (per-answer MCP verification in Module 0, distinct). Upholds the MCP-first invariant at `ground-rules.md:52-70`.
