# Enrich feedback capture with diagnostic context

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

When a Bootcamper submits bootcamp feedback, the entry appended to
`docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` records only a thin slice of
context — the current module and a free-text "what they were doing". That is
usually not enough for the `feedback-to-specs` skill to reconstruct the *specific*
situation and generate a spec that fixes the actual issue: it cannot tell which
step was active, what was just asked and answered, what the plugin was doing
behind the scenes, or how the observed behavior diverged from what the hooks and
skills should have produced. Specs generated from such entries risk being generic
or missing the real root cause.

## Root cause

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` captures a
minimal snapshot:

- Step 0 (lines 13–19) reads only `current module` + completed modules and notes
  "what the bootcamper was doing".
- Step 3's "Context when reported" block (lines 74–77) records only
  **Current module** and **What they were doing**.

Richer context is readily available but is not gathered: `config/bootcamp_progress.json`
holds `current_module` and `current_step`; the plugin version is in
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; the recent 👉 questions and the
Bootcamper's answers are in the session transcript; and the active hook/skill/gate
state is knowable from the workflow in progress.

## Proposed change

Expand the silent context capture (Step 0) and the entry template (Step 3) in
`feedback.md` so every feedback entry records a richer, structured
"Context when reported" section. At minimum, capture:

- **Time of feedback** — date and time.
- **Plugin version** — from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`.
- **Module and step** — `current_module` and `current_step` from
  `config/bootcamp_progress.json`.
- **Recent questions** — the last few 👉 questions asked of the Bootcamper.
- **Bootcamper responses** — their answers to those questions.
- **Behind the scenes** — what the plugin was doing (which hook fired, which
  skill/phase/gate was active, relevant config or state).
- **Observed problem** — what the Bootcamper actually saw.
- **Expected behavior** — what should have happened per the active hooks, skills,
  and `ground-rules.md`.
- **Divergence** — the best assessment of why the expected action did not occur.

The proposed enriched block (extends, does not replace, the existing fields):

```markdown
### Context when reported

- **Time:** YYYY-MM-DD HH:MM (local)
- **Plugin version:** [from .claude-plugin/plugin.json, or "Unknown"]
- **Module / step:** [current_module / current_step from bootcamp_progress.json, or "Unknown"]
- **Recent questions:** [the last few 👉 questions asked]
- **Bootcamper responses:** [their answers to those questions]
- **Behind the scenes:** [active hook/skill/phase/gate and relevant state]
- **Observed problem:** [what the Bootcamper saw]
- **Expected behavior:** [what the active hooks/skills/ground-rules imply should happen]
- **Divergence:** [why expected ≠ actual]
```

This context MUST be gathered silently (from `bootcamp_progress.json`, the plugin
manifest, and the transcript) — it adds no new 👉 questions and never burdens the
Bootcamper (INV-005, INV-012). Any field whose source is missing is recorded as
"Unknown"/"Unavailable" rather than fabricated. Appending stays append-only and
local-only (INV-010, INV-015): the header and earlier entries are preserved, and
nothing is sent externally unless the Bootcamper asks.

Keep the `feedback-capture.py` hook's injected workflow guidance consistent with
the enriched field list, so the hook and `feedback.md` describe the same capture.

## Acceptance criteria

- [ ] A feedback entry's "Context when reported" section captures time, plugin version, current module and step, the recent 👉 questions and the Bootcamper's responses, a behind-the-scenes summary, the observed problem, the expected behavior, and the expected-vs-actual divergence.
- [ ] The context is gathered silently — no additional 👉 question is asked of the Bootcamper — and only from available sources, with "Unknown"/"Unavailable" fallbacks when a source is missing (no fabricated values).
- [ ] Appending remains append-only and local-only; the file header and existing entries are preserved, and nothing is sent externally without explicit consent.
- [ ] Given an enriched entry, a `feedback-to-specs` run can identify the specific module/step and the expected-vs-actual divergence — i.e., the captured fields are sufficient to write a context-specific spec.
- [ ] The `feedback-capture.py` hook's injected guidance stays consistent with the enriched field list.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` — expand Step 0 capture and the Step 3 "Context when reported" template.
- `plugins/senzing-bootcamp/scripts/feedback-capture.py` — update the injected feedback-workflow guidance to name the richer capture (keep it consistent with `feedback.md`).

## Source

- Maintainer request (2026-07-15): capture richer per-feedback context so `feedback-to-specs` can produce specs that address the issue seen in that specific context.
- Priority: Medium.
- Related specs: `interaction-or-questions.md` (also edited `feedback.md`'s questions); `todo.md` (if a lighter idea backlog entry exists).

## Invariants introduced

- `INV-053` — Every bootcamp feedback entry in `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` MUST include a diagnostic "Context when reported" section (time, plugin version, module/step, recent questions and responses, behind-the-scenes state, observed problem, expected behavior, and divergence), gathered silently with "Unknown" for missing sources (recorded in `specs/INVARIANTS.md`).
