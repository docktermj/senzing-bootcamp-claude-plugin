# Entity Resolution Introduction

Used in the onboarding preface (the entity-resolution concepts step). Teach the core concept
before the WELCOME banner and the rest of the preface.

## Banner (show first)

Present this banner verbatim as the FIRST bootcamper-facing content of this step, before the
description:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧭🧭🧭  ENTITY RESOLUTION CONCEPTS  🧭🧭🧭
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Hard rule: facts come from MCP, not memory

Before presenting, call the Senzing MCP `search_docs` tool for the Senzing-specific material.
Suggested queries:

- "Senzing principle-based entity resolution approach"
- "entity resolution relationships disclosed discovered"
- "entity resolution ambiguous match possible match"
- "Senzing differentiators real-time explainability attribution"
- "entity resolution pipeline standardization blocking scoring clustering"

Do NOT present hardcoded Senzing facts from training data. Every Senzing-specific claim must
come from `search_docs`. If asked for a source, cite "Senzing documentation via MCP".

## What to teach (generic concept, plain language)

- **What entity resolution is:** deciding whether different records refer to the *same
  real-world entity* (person or organization), then matching, relating, and deduplicating them.
- **Two failure modes:** false negatives (same entity split apart) and false positives
  (different entities merged).
- **The conceptual pipeline:** ingestion/standardization -> candidate selection (blocking) ->
  comparison/scoring -> classification (match / no-match / possible-match) -> entity clustering.
- **Disclosed vs. discovered relationships.**
- **Three outputs:** resolved entities (golden record), cross-source relationships, and
  deduplication.

### How Senzing handles it (pull specifics from MCP)

Cover, using `search_docs` results: principle-based matching (frequency, exclusivity,
stability); pre-configured for people and organizations; differentiators (real-time, no model
training required, explainability, scalability).

## Mandatory exploration gate (internal)

After presenting, invite the bootcamper to explore before moving on. Offer example questions:

- "How does Senzing match records without rules?"
- "What's the difference between matching and relating?"
- "What kinds of data does entity resolution work with?"

Add: "You can ask any question about entity resolution - not just these examples. When you're
ready to move on, just say so."

Then end the turn on this single 👉 question, asked **verbatim**, and wait:

> 👉 **Are you ready to move on to the welcome?**

The wording is pinned so it stays compliant: it is a single yes/no where "yes" (or any readiness
signal) means "yes, move on to the welcome" and "no" means "no, keep exploring" — exactly one
meaning each (INV-008), with no "or"-joined choices (INV-051, INV-009). Do not paraphrase it into
an either/or (e.g. "…or shall we move on?"), which would give "yes" two meanings. This is a ⛔
gate (internal - do not render the `⛔`/`🛑` glyphs). Do not advance until the bootcamper is ready.

- **Follow-up question** (contains "?", asks for explanation): answer it via `search_docs`, then
  re-present the pinned gate question. Do NOT advance.
- **Readiness signal** ("ready", "let's go", "continue", "next", "yes"): advance to the WELCOME
  banner and overview. Do not re-present the intro or the gate.
- **Not ready** ("no", "not yet", "wait"): acknowledge, invite another entity-resolution question
  or topic, and re-present the pinned gate question. Do NOT advance.
- **Ambiguous:** treat as a follow-up.
- **`search_docs` empty or failing:** tell the bootcamper no docs were found, suggest a
  rephrase, and re-present the pinned gate question.
