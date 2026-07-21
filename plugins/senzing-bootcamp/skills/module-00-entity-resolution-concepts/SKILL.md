---
name: module-00-entity-resolution-concepts
description: 'Bootcamp Module 0 (optional): the Entity Resolution Concepts primer. Runs only when "Entity Resolution Concepts" was selected during Bootcamp preparation. Use when the bootcamper reaches the entity-resolution concepts module, or asks to explore entity resolution concepts before Module 1.'
---

# Module 0 (optional): Entity Resolution Concepts

> **MCP grounding (mandatory — applies to this entire skill).** Every Senzing fact you present —
> SDK method and attribute names, config options, error codes, and entity-resolution specifics —
> MUST come from the Senzing MCP tools, never from training data, memory, or speculation.
> **Pre-response checklist:** if a reply contains any Senzing specific, you MUST have called an MCP
> tool this turn to obtain it; if not, stop and call it first. This has the same precedence as a ⛔
> gate. The full rule and tool routing are the "MCP-first invariant" in
> `../bootcamp-onboarding/ground-rules.md`.

Follow `../bootcamp-onboarding/ground-rules.md` throughout (👉 one-question-at-a-time,
MCP-first, no fabricated answers). This is an **optional** primer that teaches the core idea of
entity resolution so the bootcamper has context before the guided modules begin.

**Inclusion is driven by module selection, not by a per-module gate.** Whether this module runs is
decided once, during the **Bootcamp preparation** module (`../bootcamp-preparation/SKILL.md`): Core
always includes it; Customized includes it only if the bootcamper chose it. When this skill is
invoked, the bootcamper has already opted in — so **run the primer directly**; do NOT ask a
skip/keep question (that gate has been retired to avoid asking the same decision twice — INV-078).

Module 0 is a **preamble, not a numbered module**: it is not counted among the mandatory
Modules 1–7 (INV-076/INV-078), skipping it (by not selecting it) is a permitted, requested skip (INV-014),
and it does **not** run the per-module completion apparatus (no journey map, no
`docs/bootcamp_recap.md` section, and it is not added to `modules_completed`). Keep it lightweight.

## 1. Run the primer

Follow `concepts.md` in this skill directory:

1. Present the **ENTITY RESOLUTION CONCEPTS** banner (defined in `concepts.md`) — this is the
   INV-073 banner outcome, delivered here in Module 0.
2. Give the description of entity resolution, pulling all Senzing-specific facts from the Senzing
   MCP server, never from memory (MCP-first invariant / INV-073). Verify substantive claims with a
   second confirming MCP call before presenting them (see `concepts.md`).
3. **Invite questions/discussion before the quiz** (`concepts.md`): after the description and before
   the quiz offer, give the bootcamper space to clarify, ending on the pinned 👉 question — verbatim:
   **"Do you have any questions about entity resolution before we continue?"** (INV-056). Answer any
   question via `search_docs` verified with a second MCP call, then re-present; on "no", proceed to
   the quiz. It is issued once (INV-006), single-meaning yes/no with no "or"-joined choices
   (INV-008 / INV-051), and never blocks (not a ⛔ gate).
4. Offer the **optional knowledge-check quiz** (`concepts.md`) as its own pinned 👉 question before
   the readiness gate. On accept, pose a short series of MCP-sourced/verified questions at moderate
   difficulty, one 👉 per turn, letting the bootcamper exit at any time; on decline, go straight to
   the gate. The quiz never blocks and never replaces the gate.
5. End on the mandatory exploration gate using the pinned 👉 question defined in `concepts.md` —
   verbatim: **"Are you ready to move on to the next module: Discover the Business Problem?"**
   (INV-073 explore-gate outcome; Module 1 always follows Module 0). It is a
   single yes/no with exactly one meaning for "yes" and one for "no", and no "or"-joined choices
   (INV-008 / INV-051). Answer any entity-resolution follow-up via `search_docs`, verified with a
   second MCP call, then re-present the gate; do not advance until the bootcamper is ready.

## 2. Hand off to Module 1

When the bootcamper signals they are ready to move on (Step 1's gate), invoke the
`module-01-business-problem` skill to begin Module 1 — **Discover the Business Problem** (name the
module to the bootcamper, never "Module 1") — applying the module-start banner and journey
map from `ground-rules.md`. The selected numbered modules then run in the order recorded in
`selected_modules` (Module 1 is the next module after Module 0 in every path).
