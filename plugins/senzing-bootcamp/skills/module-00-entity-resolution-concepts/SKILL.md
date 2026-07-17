---
name: module-00-entity-resolution-concepts
description: 'Bootcamp Module 0 (optional): the Entity Resolution Concepts primer. Use when the bootcamper reaches the optional entity-resolution concepts step after onboarding, wants the entity-resolution primer, or asks to explore entity resolution concepts before Module 1.'
---

# Module 0 (optional): Entity Resolution Concepts

Follow `../bootcamp-onboarding/ground-rules.md` throughout (👉 one-question-at-a-time,
MCP-first, no fabricated answers). This is an **optional** primer, offered after the onboarding
preface (WELCOME, overview, level of detail, track, programming language, any questions) and
before Module 1. It teaches the core idea of entity resolution so the bootcamper has context
before the guided modules begin.

Module 0 is a **preamble, not a numbered module**: it is not counted among the mandatory
Modules 1–7 (INV-013), skipping it is a permitted, requested skip (INV-014), and it does **not**
run the per-module completion apparatus (no journey map, no `docs/bootcamp_recap.md` section, and
it is not added to `modules_completed`). Keep it lightweight.

## 1. Offer the primer (skip/keep gate)

State in one or two sentences that entity resolution is the foundation for the rest of the
bootcamp and that this short primer is optional — an experienced bootcamper can skip straight to
Module 1. Then end the turn on this single, pinned 👉 question, asked **verbatim** (INV-056):

> 👉 **Would you like to go through the Entity Resolution Concepts primer before Module 1?**

The wording is pinned so it stays compliant: a single yes/no where "yes" (or any affirmative)
means "yes, give me the primer" and "no" (or "skip") means "no, go straight to Module 1" —
exactly one meaning each (INV-008), with no "or"-joined choices (INV-051, INV-009). This is a ⛔
gate (internal — do not render the `⛔`/`🛑` glyphs). Do not assume the answer; wait for it.

- **Skip** ("no", "skip", "I know this", "straight to Module 1"): acknowledge briefly and hand
  off to Module 1 (Step 3). Do NOT present the concepts banner or description.
- **Keep** ("yes", "sure", "let's do it"): run the primer (Step 2).

## 2. Run the primer (only if not skipped)

Follow `concepts.md` in this skill directory:

1. Present the **ENTITY RESOLUTION CONCEPTS** banner (defined in `concepts.md`) — this is the
   INV-019 banner outcome, now delivered here in Module 0 (INV-073).
2. Give the description of entity resolution, pulling all Senzing-specific facts from the Senzing
   MCP server, never from memory (INV-020 / MCP-first invariant).
3. End on the mandatory exploration gate using the pinned 👉 question defined in `concepts.md` —
   verbatim: **"Are you ready to move on to Module 1?"** (INV-021 explore-gate outcome). It is a
   single yes/no with exactly one meaning for "yes" and one for "no", and no "or"-joined choices
   (INV-008 / INV-051). Answer any entity-resolution follow-up via `search_docs`, then re-present
   the gate; do not advance until the bootcamper is ready.

## 3. Hand off to Module 1

When the bootcamper skips the primer (Step 1) or signals they are ready to move on (Step 2's
gate), invoke the `module-01-business-problem` skill to begin Module 1, applying the module-start
banner and journey map from `ground-rules.md`. The numbered modules then run in ascending order
(Module 1 → Module 2 → … → Module 7).
