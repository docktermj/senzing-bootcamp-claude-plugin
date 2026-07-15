---
name: feedback-to-specs
description: 'Analyze a Senzing Bootcamp plugin feedback file and turn it into one or more improvement specs under specs/. Use when the maintainer wants to process SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md, triage bootcamper feedback, or generate/refresh specs from collected feedback. Maintainer tool — not part of the bootcamper experience.'
---

# Feedback → Specs

This is a **maintainer** tool for developing the Senzing Bootcamp Claude Plugin
(SBCP). It reads a feedback file collected during bootcamps, analyzes and triages
each item against the codebase and the existing specs, and writes **one or more
improvement specs** into `specs/`. It does **not** implement the fixes — it turns
raw feedback into actionable, deduplicated specs a developer (or a follow-up
session) can act on.

It is unrelated to the bootcamper-facing `/bootcamp-feedback` flow, which only
*captures* feedback. This skill *consumes* that captured feedback.

## Scope and guardrails

- **Write only under `specs/`.** Never modify plugin code, hooks, scripts, skills, or the feedback file itself. Generating specs is the deliverable; implementing them is a separate, later step.
- **Never invent feedback.** Every spec must trace to a real entry in the feedback file. If an entry is too vague to spec, mark it *needs clarification* rather than guessing.
- **Deduplicate.** If an existing spec already covers a feedback item, do not create a second one. Note it as already-tracked (and optionally enrich the existing spec).
- **Respect the invariants.** Every generated spec references `@invariants.md` and must not propose anything that violates it (cross-platform Linux/macOS/Windows, language-agnostic, production-ready, consistent/coherent/complete). If feedback conflicts with an invariant, say so in the spec instead of silently overriding it.

## Step 1: Locate and read the feedback file

Resolve the feedback file in this order:

1. An explicit path the maintainer gave (argument or message).
2. `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` at the repo root.
3. `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` (a bootcamper project's file, if copied into the repo).

If more than one candidate exists and none was named, ask which to use. If none is
found, say so and stop — there is nothing to analyze.

Read the whole file.

## Step 2: Parse the feedback into discrete items

Feedback is usually a series of `## Improvement: <title>` blocks with subsections
(**What happened**, **Why it matters**, **Suggested fix**, **Context when
reported**), plus **Date**, **Module**, and **Priority** lines. Handle free-form
prose too — bootcampers do not always follow the template.

For each item, extract: `title`, `symptom` (what happened, with any verbatim
error/output), `impact` (why it matters), `suggested_fix`, `priority`, `module`,
and `date`. Skip the file's header/placeholder sections (e.g. an empty "Your
Feedback" heading with no content).

## Step 3: Load triage context (do this before writing anything)

- **Read `specs/invariants.md`.** This is the ruleset every spec must respect.
- **List and skim every existing `specs/*.md`.** Record each spec's title and the problem it covers so you can deduplicate. (For example, a feedback item about the write-gate blocking `/tmp/` paths is already covered by `specs/PreToolUseWriteError.md`.)
- **Skim `specs/todo.md`** — the lightweight idea backlog, so you can route minor items there instead of into a full spec.

## Step 4: Analyze each item (go beyond the feedback text)

For every parsed item:

1. **Classify** it: bug / false-positive, UX or wording, missing feature, invariant gap, documentation, or unclear.
2. **Confirm the root cause in the codebase**, don't just restate the report. Open the code the feedback implicates — `plugins/senzing-bootcamp/hooks/`, `scripts/`, `skills/`, `commands/` — and verify what actually causes the symptom. Cite `file:line`. If you cannot confirm it, label the root cause "Unverified — needs investigation" rather than asserting one.
3. **Deduplicate** against existing specs (Step 3). Mark the item `already-tracked → specs/<file>.md` when covered.
4. **Group**: merge items that share one root cause or one fix into a single spec; keep unrelated items in separate specs. The number of specs per run is whatever the analysis warrants — one, several, or (if everything is already tracked or too vague) none.

## Step 5: Write the spec(s)

For each new spec, write `specs/<kebab-case-title>.md` using the template in
`spec-template.md` (in this skill's directory). Rules:

- **Pick a filename that does not collide** with an existing spec. Match the terse, developer-facing tone of the current specs.
- **Ground it in code.** Root cause cites real `file:line`; affected-files lists real paths.
- **Make acceptance criteria observable and testable**, and always include a criterion that the change holds on Linux, macOS, and Windows and stays language-agnostic (the invariants).
- **Link the source**: name the feedback file, the entry title, its date, module, and priority.

For minor items that don't warrant a full spec, propose a one-line addition to
`specs/todo.md` (append only) and ask before writing it.

## Step 6: Report the triage

Present a compact table so the maintainer sees every item's disposition:

| Feedback item | Classification | Action |
|---|---|---|
| <title> | <bug/UX/feature/…> | New spec → `specs/<file>.md` |
| <title> | <…> | Already tracked → `specs/<file>.md` |
| <title> | unclear | Needs clarification |

Then list the spec files created (as clickable `specs/<file>.md` paths), note
anything routed to `todo.md` or left for clarification, and offer next steps
(e.g. "I can implement `specs/<file>.md` next" or "want me to open the questions
for the unclear items?"). Do not start implementing unless asked.
