# Add a graduation retrospective that files the assistant's own false starts as feedback

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Every feedback entry the plugin has ever collected exists because the **bootcamper** noticed something
and typed "bootcamp feedback". Friction the assistant hit and silently worked around — wrong assumptions,
failed commands, tools behaving differently than documented, dead ends recovered from — leaves no record
anywhere except the transcript.

The bootcamper asked that the Graduation module review the session's internal false starts, errors,
course corrections, and learnings, and capture them in
`docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` as if they were bootcamp feedback, so continuous
improvement does not depend on the bootcamper noticing and reporting.

Why it matters, in their words: "The plugin's improvement loop currently has exactly one sensor, and it
is the bootcamper. That sensor is blind to the most valuable class of defect: **the kind that looks like
it worked.**"

Their concrete example from that session: `get_sdk_reference` exposes a `response_schemas` topic, which
the plugin references **zero** times. The response shape was consequently guessed wrong three times in
Module 7 (`FEATURE_TYPE` instead of `FTYPE_CODE`; `MATCH_LEVEL_CODE` at the result root instead of nested
under `MATCH_INFO`; `INBOUND_VIRTUAL_ENTITY` instead of `VIRTUAL_ENTITY_1`/`VIRTUAL_ENTITY_2`). Every one
produced **silently blank output rather than an error**. No bootcamper would ever report those, because
on screen they look like empty sections rather than failures.

They estimate roughly 20 such moments occurred in that one session. None would have been captured.

**This spec is self-evidently load-bearing:** five of the entries in this feedback round are marked
`Source: self-observed (assistant retrospective)` and were produced by the reporter performing this
retrospective by hand. Four of them became specs that no bootcamper-driven report would have generated.

## Root cause

**Confirmed: there is no code path by which the assistant can file feedback on its own initiative.**

- Grep of `skills/graduation/` for retrospective-related language (retrospectiv, false start, course
  correction, lessons learned) returns **no matches**. There is no existing step to extend.
- The feedback workflow is triggered exclusively by a bootcamper utterance: the `UserPromptSubmit` hook on
  "bootcamp feedback", or the `/bootcamp-feedback` command. `skills/bootcamp-onboarding/feedback.md`
  Step 2 gathers content by asking the bootcamper 👉 questions one at a time — the whole flow assumes a
  human author.
- No module reviews the session retrospectively.

## Proposed change

Add a retrospective step to the Graduation skill, **before** the recap PDF is rendered, that reviews the
session and appends findings to `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`.

1. **What to review** — the four categories the reporter specified:
   - **False starts** — an approach begun and abandoned.
   - **Errors** — commands, compiles, or tool calls that failed and had to be retried differently.
   - **Course corrections** — a stated plan or hypothesis that measurement disproved.
   - **Learnings** — anything discovered about the environment, the SDK, or the MCP tools that is not in
     the plugin's documentation.
2. **Write each as a normal `## Improvement:` entry** using the existing template at
   `skills/bootcamp-onboarding/feedback.md:83-116`, appended (never overwriting), so the existing
   tooling and this triage skill consume them unchanged.
3. **Add a `**Source:**` field to the template**, distinguishing `bootcamper-reported` from
   `self-observed (assistant retrospective)`. Without it a future maintainer cannot tell which findings
   came from real user friction and which from the assistant's own stumbles — and those deserve different
   weight when prioritizing. Add it to the template at `feedback.md:83-88` so bootcamper-authored entries
   carry `Source: bootcamper-reported` going forward. Backfilling existing entries is optional.
4. **Filter for recurrence, not embarrassment.** The stated inclusion test: *"would this happen to
   another bootcamper?"* — not *"did the assistant look bad?"*. A one-off typo is noise; a documented tool
   that behaves differently than documented is signal. Put this test in the skill text, because without it
   the step degenerates into either self-flagellation or nothing.
5. **Reuse the existing durability machinery.** `feedback.md:117-124` (Step 3b) re-reads the file to
   confirm the entry landed. The retrospective must use the same verification — an unwritten
   retrospective is worse than none, since nobody is watching for it.
6. **Keep it strictly non-blocking.** A retrospective that fails, finds nothing, or cannot access the
   session history must never prevent graduation. Report and continue.
7. **Do not ask the bootcamper to author it.** The entire point is that this sensor is independent of
   them. Announce that it happened and where it was written (one line), but do not gate it behind a 👉
   question — consistent with `specs/drop-deliverable-generation-gates.md`.
8. **PII boundary.** These entries are written into the bootcamper's own project and may be shared back to
   the maintainer. `graduation/SKILL.md:168` already forbids recording hostname, username, IP address, or
   other personal/host identifiers (INV-065); that constraint applies to retrospective entries too. Note
   that the existing feedback template deliberately *does* record OS/architecture and model/effort as
   diagnostic context, which is permitted — the line is personal/host identifiers, not environment facts.
9. **Skip the feedback-flow banners.** `feedback.md:48-62` and `:128-136` pin entry/exit banners marking
   the boundary between the bootcamp flow and the bootcamper-driven feedback flow. A retrospective is not
   that flow — it is a graduation step — so it must not present those banners
   (`specs/feedback-flow-boundary-banner.md` established them for the interactive path).

## Acceptance criteria

- [ ] `skills/graduation/SKILL.md` has a retrospective step that runs **before** the recap PDF is
      rendered and reviews the session for false starts, errors, course corrections, and learnings.
- [ ] Findings are appended as `## Improvement:` entries to
      `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`, never overwriting existing content.
- [ ] The feedback template carries a `**Source:**` field; retrospective entries are marked
      `self-observed (assistant retrospective)` and bootcamper-authored entries
      `bootcamper-reported`.
- [ ] The skill states the "would this happen to another bootcamper?" inclusion test explicitly.
- [ ] The step re-reads the file to verify the entries landed, reusing the Step 3b durability pattern.
- [ ] A retrospective failure — including finding nothing to report — never blocks graduation.
- [ ] The step is announced in one line, not gated behind a 👉 question, and does not present the
      feedback-flow entry/exit banners.
- [ ] No hostname, username, IP address, or other personal/host identifier appears in a retrospective
      entry (INV-065).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      retrospective reviews the session narrative, not language- or platform-specific build output, and
      writes a plain Markdown entry.

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — new retrospective step before Step 1's recap
  PDF render
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` — add `**Source:**` to the entry
  template (lines ~83-88); note that the retrospective reuses the template and the Step 3b durability
  check but not the entry/exit banners
- `.claude/skills/feedback-to-specs/SKILL.md` and `.claude/skills/feedback-to-specs/spec-template.md` —
  teach the triage side to read `Source:` and weight self-observed vs. bootcamper-reported findings

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Add a Graduation retrospective that captures the
  assistant's own false starts as feedback" (2026-07-25, Graduation)
- Priority: **High**
- Related specs: `specs/lookup-sdk-response-schemas-before-parsing.md` (the worked example that motivated
  this), `specs/enrich-feedback-context.md`, `specs/feedback-file-durability.md`,
  `specs/feedback-flow-boundary-banner.md`, `specs/drop-deliverable-generation-gates.md`

## Invariants introduced

- `INV-116` — Every feedback entry MUST carry a `**Source:**` field (`bootcamper-reported` or
  `self-observed (assistant retrospective)`), and graduation MUST run a non-blocking session
  retrospective before rendering the recap PDF that files self-observed findings using the same
  template and durability re-read as the bootcamper-driven flow — no entry/exit banners, no 👉 gate,
  no personal/host identifiers. (Recorded in `specs/INVARIANTS.md`.)

## Implementation notes

The retrospective is Step 0 — after Pre-checks, before Step 1's PDF render. It was also added to
graduation's preface step enumeration: INV-031 requires listing the module's steps, and the
retrospective produces visible output (the one-line "filed N notes" announcement), so omitting it
would have left the enumeration incomplete.
