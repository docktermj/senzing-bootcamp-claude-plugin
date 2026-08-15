# A question with no origin in a skill file reached the Bootcamper

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A Bootcamper on plugin 0.5.0 was asked about **"auto-mode for the bootcamp"** while taking the
bootcamp. Their report:

> They believe this option should only be available during bootcamp plugin development, never
> surfaced to someone actually taking the bootcamp. […] It confuses the experience and undermines
> confidence in the guided flow.

The timing is the sharp part. It happened in the **onboarding preface**, with
`👉 Do you have any questions before we get started?` (`onboarding-flow.md:199`) pending and
unanswered — before Bootcamp preparation had run, before any module had started, and therefore
before the bootcamp's own sanctioned interface question had ever fired. The Bootcamper answered it
by filing feedback instead.

No plugin file asks this. A repo-wide search for `auto-mode`, `auto mode`, `auto-accept`,
`permission mode`, `plan mode`, `fast mode` and `bypass permissions` across `plugins/`, `.claude/`
and `tests/` returns **zero** matches. The question originated outside the bootcamp's scripted
flow — the Claude Code CLI's own session-level control surfaced alongside the bootcamp, or the
guide originated it — which is what the entry's `Routing:` field was recording when it declined to
pick `plugin` or `mcp-server`.

## Root cause

Two halves, and the second is the one this repo owns.

**The preface's script has no room for it.** `onboarding-flow.md:110-218` presents exactly two
bootcamper-facing items — the WELCOME banner plus the overview (step 3) and the single 👉 at
`:199` — and `:216-218` states that the preface writes no preferences at all, because every setup
choice belongs to Bootcamp preparation (INV-058). There is no step at which an option question is
due.

**Nothing in the plugin forbids a question the plugin never wrote, and one thing makes such a
question look native.** The 👉 protocol at `ground-rules.md:32-124` governs a question's *count*
(exactly one per yielding turn — INV-005, `:39`), its *shape* (INV-008/INV-009/INV-051 at `:92-103`,
INV-224 at `:83-91`), its *placement* (INV-211 at `:72-82`) and, for ⛔ gates only, its *verbatim
wording* (INV-056, `specs/INVARIANTS.md:518`). None of them governs **provenance.** A 👉 question
that traces to no step in any skill file breaches nothing on the books. INV-012
(`specs/INVARIANTS.md:68`) does not reach it either: it suppresses output the Bootcamper cannot act
on, and a session toggle is something they *can* act on — it simply is not the bootcamp's to offer.

The plugin ships **94** pinned 👉 questions across **24** files, and exactly one class of them asks
the Bootcamper to operate a control in their Claude interface: the module-start model/effort switch
(`ground-rules.md:644-925`, pinned at `:778` and `:784`; INV-063, INV-098, INV-158, INV-236).
Nothing anywhere says it is the only one. So the bootcamp has already established that session dials
are in scope and named no boundary — and a Bootcamper who has been asked *"Would you like to switch
to `/model …` + `/effort …` for this module?"* has no way to tell an "auto-mode?" question from
bootcamp content. Here the confusion was worse than that: the unsanctioned question arrived
**first**, so the frame the Bootcamper formed for every later interface question came from a
question the bootcamp never authored.

## What re-verification and analysis changed about the request

**The entry's suggested fix is not available to the plugin in the form it was written.** It asks to
"suppress the auto-mode prompt entirely for bootcamper-facing runs". If the Claude Code CLI renders
its own Auto Mode affordance, no plugin file removes it — a plugin ships skills, hooks and commands,
and none of those can suppress a host control. Writing an acceptance criterion for suppression would
produce a criterion nobody can meet.

What the plugin **can** guarantee is the half that actually produced the confusion: that the
bootcamp never asks about a host control, never treats one as part of the flow, and has a stated
answer when the Bootcamper raises one. This spec is therefore routed `plugin` on that narrower
ground, not on the ground the entry considered and rejected.

## Proposed change

1. **Close the question set in the 👉 protocol** (`ground-rules.md:32-124`). Draft wording for the
   maintainer's sign-off (`INVARIANTS.md` is append-only; `implement-spec` Step 5 requires approval
   before recording):

   > Every 👉 question presented to the Bootcamper MUST trace to a step in a shipped skill file. The
   > guide MUST NOT originate a gate the bootcamp does not specify, and MUST NOT present a **session-
   > or host-level control** — auto mode, auto-accept edits, permission mode, plan mode, fast mode,
   > background tasks, `/compact`, `/loop` — as a bootcamp question, whether or not the host surfaces
   > that control alongside the bootcamp. The **only** control the bootcamp asks the Bootcamper to
   > operate is the model/effort switch (INV-063/INV-098/INV-158/INV-236). Answering a Bootcamper's
   > own question is not a new gate: a clarifying counter-question inside that answer is the turn's
   > single 👉 under INV-005, and the pending bootcamp question is re-presented verbatim afterwards.

2. **State the exception where the precedent is set.** One line in the model/effort section
   (`ground-rules.md:644-925`) saying it is the only Claude-interface control the bootcamp offers.
   The section that creates the expectation is where the limit is legible; a rule stated only 600
   lines earlier is read by nobody writing a new nudge.

3. **Give the Bootcamper a stated response, not silence.** Add a handling line beside the any-time
   controls (`ground-rules.md:615-641`): if the Bootcamper asks about a host control, answer in one
   sentence — it is their session setting, the bootcamp neither needs nor recommends a value — and
   return to the pending 👉 verbatim. This matters because the report happened **at** a pending gate;
   the re-present rule at `:629-641` already owns the return, and this only supplies the answer that
   precedes it.

4. **Guard what a test can see, and say plainly what it cannot.** Add
   `tests/test_no_host_control_is_offered_as_a_question.py`, asserting that no 👉 line in any shipped
   file under `plugins/senzing-bootcamp/` names a host control other than `/model` and `/effort`, and
   that the closed-set rule and the sole-exception sentence are both present in `ground-rules.md`.

   ⛔ **The runtime half is out of the guard's reach and MUST NOT be claimed.** A test reads files;
   this defect was a question that exists in no file, so a green run is not evidence it cannot recur.
   The guard's real value is the other direction — it keeps the rule shipped, and it stops a future
   module from adding a second interface question by accident. Recording that limit in the docstring
   is required: a guard that reads as covering the reported symptom is the pattern
   `coverage-reports-count-known-non-defects-as-hits` exists to stop.

## Acceptance criteria

- [ ] An invariant records the closed-question-set rule, worded and **approved by the maintainer**,
      appended with the next unused `INV-NNN` and its index entry in the same edit.
- [ ] `ground-rules.md`'s 👉 protocol states that every 👉 question traces to a step in a shipped
      skill file, and names the model/effort switch as the only Claude-interface control the bootcamp
      offers.
- [ ] The model/effort section states the same limit at the point the precedent is set, so a reader
      adding a nudge meets it there.
- [ ] A Bootcamper question about a host control has a stated one-sentence answer, and the pending 👉
      question is re-presented verbatim afterwards.
- [ ] The new guard fails when a 👉 line in any shipped file names a host control other than `/model`
      or `/effort` — **negative-controlled**, mutation verified to land, then reverted.
- [ ] The guard's docstring states that it cannot detect a runtime-improvised question, so a clean run
      is not read as proof the defect is gone.
- [ ] No shipped file gains a claim that the plugin suppresses a host control — the scope change above
      is recorded, not papered over.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the closed-set rule in the
  👉 protocol (`:32-124`), the sole-exception line in the model/effort section (`:644-925`), and the
  host-control handling line beside the any-time controls (`:615-641`).
- `specs/INVARIANTS.md` — one new invariant, appended, plus its index entry.
- `tests/test_no_host_control_is_offered_as_a_question.py` — new.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: Auto-mode option should not be
  offered during a live bootcamp run" (2026-08-15, Module General — onboarding preface;
  `Source: bootcamper-reported`)
- Priority: **High** (as filed). It is the Bootcamper's first impression of whether the guided flow
  knows what it is doing, it landed on an unanswered gate, and it cost the run its pending question.
- MCP re-check: **n/a (no Senzing fact).** The entry makes no claim about Senzing, the SDK, or the
  MCP server — it is entirely about the bootcamp's interaction layer, so there is no server fact to
  re-verify and no absence claim about the server to substantiate. `get_capabilities` was called once
  at triage to date the run: server **1.32.9**, 2026-08-15.
- Upstream: not applicable — not a Senzing MCP server defect. (The entry's own `Upstream:` field
  reads `not applicable`.)
- Related specs: `surface-aware-model-effort-instructions` (same section, the surface the nudge
  detects), `skip-model-guidance-question`,
  `effort-only-switch-question-says-keep-your-current-model`,
  `coverage-reports-count-known-non-defects-as-hits` (why the guard's limit is stated), and
  INV-005, INV-012, INV-056, INV-063, INV-098, INV-158, INV-236.

## Invariants introduced

- `INV-247` — Every 👉 question presented to the Bootcamper MUST trace to a step in a shipped skill
  file; the guide MUST NOT originate a gate the bootcamp does not specify, and MUST NOT present a
  session- or host-level control as a bootcamp question. The model/effort switch
  (INV-063/INV-098/INV-158/INV-236) is the only Claude-interface control the bootcamp asks the
  Bootcamper to operate. (Recorded in `specs/INVARIANTS.md`, indexed under *Questions, gates and
  bootcamper-facing conversation*.)

## Deviations from this spec, and why (2026-08-15)

- **The invariant is shorter than the draft in `## Proposed change` item 1.** Its closing sentence —
  "Answering a Bootcamper's own question is not a new gate: a clarifying counter-question inside that
  answer is the turn's single 👉 under INV-005, and the pending bootcamp question is re-presented
  verbatim afterwards" — is a clarification rather than a second testable condition, and
  `INVARIANTS.md` rule 4 requires one condition per ID. The sentence ships in full, as prose in
  `ground-rules.md`'s 👉 protocol ("Answering a question the bootcamper asks is not originating
  one"), and `tests/test_no_host_control_is_offered_as_a_question.py` asserts it is there. Maintainer
  chose this over folding it in or splitting into two IDs, 2026-08-15.
- **Two files changed beyond `## Affected files`.** `tests/test_invariant_enforcer_citations.py`
  needed `EXPECTED_PAIRS` 59 → 60, because INV-247 names its enforcing test and that file counts
  invariant→test pairs deliberately rather than dynamically. Separately, the sole-exception line
  first quoted the switch question verbatim, which `tests/test_model_effort_nudge_edges.py` reads as
  a **pinned** question and requires to carry the `{dial}` placeholder; the line was reworded to
  paraphrase ("a bootcamper who has just been asked to set `/model` and `/effort`") rather than
  weaken that guard.
- **The count in `## Root cause` has drifted.** The spec says 94 pinned 👉 questions across 24 files;
  the same scan on 2026-08-15 finds **96** across 24. Nothing in the analysis turns on the figure —
  the file count is unchanged and no new question names a host control — so it is recorded rather
  than corrected here (correcting spec content is `feedback-to-specs`' job).
- **No Senzing fact required re-verification.** `get_capabilities` was called to date the run
  (server **1.32.9**, 2026-08-15), confirming the spec's `MCP re-check: n/a`. The spec's one
  falsifiable factual claim is about *this repo*, not the server — that no plugin file asks about a
  host control — and it was re-run rather than copied: `grep -rniE 'auto-mode|auto mode|auto-accept|
  permission mode|plan mode|fast mode|bypass permissions'` across `plugins/`, `.claude/` and `tests/`
  returned zero matches before any edit.
