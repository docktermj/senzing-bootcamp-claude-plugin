# The post-yes switch statement ignores what the Bootcamper already set

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The module-start model/effort nudge names the literal CLI command in its question:

> 👉 **Would you like to switch to `/effort medium` for this module?** (Recommended for best
> value; …)

Naming the command invites the Bootcamper to **run it before answering** — which is the natural
response to being shown a command, not an edge case. `ground-rules.md` then has exactly one
post-yes branch:

> This switch turn ends at the 👉. On **yes**, open the reply turn with a one-line statement
> telling the bootcamper how to make the change (run the `/model`/`/effort` commands in the Claude
> Code CLI …), then end the turn on this pinned confirmation gate

There is no branch for *"they already ran it"* and none for *"they ran it and chose a different
value."* Both are common, and the second produces output that contradicts the session.

**Observed live, phase-3 dry run, 2026-08-14, at the Data collection module start.** The walk
presented the correct effort-only step-down question (`/effort medium`, current `high`). The
Bootcamper replied **yes** and, in the same turn, ran `/effort xhigh` — *up*, not down. Following
the flow as written then required emitting:

> Switching to `/effort medium` — run `/effort medium` in the Claude Code CLI.

which is wrong twice over: it instructs a command already run, and it names a value the Bootcamper
had just deliberately rejected in favour of a higher one. The pinned gate that follows —
"👉 **Are you done modifying the model and effort?**" — then asks a question the transcript has
already answered.

The failure is not the Bootcamper doing something unusual. It is that the question hands them a
command and the reply path assumes they have not used it yet.

### Why the existing rules do not already cover this

- **INV-138 / the per-dial comparison** governs *what to compare and when to ask*. It says nothing
  about the reply turn after a yes.
- **`specs/model-effort-switch-done-confirmation.md`** (implemented; the gate exists against
  INV-064's single-turn preference) added the confirmation gate specifically to give a window for
  running the commands. A Bootcamper who runs them **early** does not need the window, and is
  asked to confirm into it anyway.
- **`specs/effort-above-every-recommendation-triggers-a-step-down-question-every-module.md`**
  covers the *next* module's comparison once effort sits above the table. It does not touch the
  turn in which the Bootcamper put it there.

So this is a genuine gap in the post-yes branch, not a restatement of any of the three.

## Root cause

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`, "Best-value model/effort
prompt" — the post-yes instruction is unconditional and imperative ("telling the bootcamper how to
make the change"), with no read of the live session between the yes and the statement. The same
flow is mirrored in `plugins/senzing-bootcamp/skills/graduation/SKILL.md`, so a fix in one place
without the other leaves the identical defect at the last stage of the bootcamp (the INV-097
second-consumer shape).

The deeper cause is that the flow models one actor changing state in one order — guide asks,
Bootcamper answers, Bootcamper acts — while the CLI lets the Bootcamper act *first*, and the
transcript makes that visible.

## Proposed change

**Read the dial before composing the post-yes statement.** In `ground-rules.md`'s post-yes branch,
require the guide to check whether the transcript already shows the dial set, then take one of
three shapes:

1. **Not yet set** — the current behaviour, unchanged: "run `/effort medium` in the Claude Code
   CLI", then the pinned gate.
2. **Already set to the recommended value** — acknowledge it instead of instructing it ("You're on
   `/effort medium` already — that's this module's recommendation."), then proceed to Step 1 **in
   the same turn**, skipping the confirmation gate. There is nothing left to confirm, and asking
   anyway is the pointless question INV-006/INV-012 forbid. This also restores INV-064's
   single-turn continuation for the case where it is genuinely correct.
3. **Already set to a different value** — state what is in force and do **not** re-instruct the
   recommendation: "You're on `/effort xhigh`; this module recommends `medium`, and running higher
   is fine — it costs more, nothing else." Then proceed to Step 1 in the same turn. ⛔ Never repeat
   the recommended command after the Bootcamper has chosen a different value: they answered the
   question with an action, and the recommendation is advisory (the table is "a recommended floor
   for value, not a ceiling").

Shape 3 must reuse the vocabulary the above-the-table exemption already uses for
running-higher-is-fine, so the two do not drift.

Apply the same three shapes to `graduation/SKILL.md`'s copy of the flow.

⚠️ **Scope note:** this changes only the reply turn after a **yes**. The switch question itself,
its pinning (INV-056), the `{dial}` substitution, and the per-dial comparison (INV-138) are all
unchanged.

## Acceptance criteria

1. When the Bootcamper answers yes and the transcript shows the dial **not** set, the reply turn
   is unchanged from today: the run-commands statement naming only the moving dial, then the pinned
   "Are you done modifying the model and effort?" gate.
2. When the Bootcamper answers yes and the transcript shows the dial **already at the recommended
   value**, the reply turn acknowledges it, does **not** instruct the command, does **not** present
   the confirmation gate, and continues to Step 1 in the same turn.
3. When the Bootcamper answers yes and the transcript shows the dial **at a different value**, the
   reply turn states the value in force, says running higher costs more and nothing else (reusing
   the above-the-table wording), does **not** re-instruct the recommended command, and continues to
   Step 1 in the same turn.
4. `graduation/SKILL.md` carries the same three shapes; a test sweeps **every** file with a pinned
   switch question so one copy cannot be fixed while the other regresses.
5. The switch question, its pinned wording, the `{dial}` substitution, and INV-138's per-dial
   comparison are asserted unchanged.
6. Cross-platform and interface-aware: the intent-based (non-CLI) form gets the same three shapes,
   since Claude Desktop / web / IDE Bootcampers can also change the setting before replying.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the post-yes branch of
  "Best-value model/effort prompt"
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the mirrored flow
- `tests/test_post_yes_switch_reads_the_dial.py` (new)
- `specs/IMPLEMENTED.md`

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-14, at the Data collection module start,
  when the maintainer answered yes to an `/effort medium` step-down and ran `/effort xhigh` in the
  same turn (`Source: self-observed (assistant retrospective)`). The wrong output was produced by
  following the file faithfully, which is what makes it a plugin defect rather than a walk error.
- Priority: **Medium.** It does not break a documented path — the bootcamp proceeds — but it emits
  a self-contradicting instruction at a module boundary, and it does so in the case the question's
  own wording encourages. An instruction that visibly contradicts what the Bootcamper just did
  teaches them the surrounding guidance is approximate.
- MCP re-check: n/a (no Senzing fact).
