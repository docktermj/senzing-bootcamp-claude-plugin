# Phase 3 — The conversational layer

Walk the bootcamp with the **maintainer answering as the Bootcamper**. This is the
only phase that tests what the plugin actually is: a conversation. Phases 1 and 2
test its dependencies.

## Why this cannot be self-played

⛔ **The assistant must not play both roles.** Two independent reasons, and both are
disqualifying:

1. `ground-rules.md` forbids fabricating the Bootcamper's response, and INV-007 says
   the plugin "cannot answer questions nor assume answers". Simulating the answers
   violates the thing under test.
2. Even if it were permitted, an assistant that knows it is being graded on
   one-👉-per-turn discipline will comply. The behavior under test is *whether the
   files produce that discipline*, which self-play cannot distinguish from the
   assistant simply being careful.

If the maintainer is not available, report phase 3 as **untested**. Do not
approximate it, and do not describe a self-played walkthrough as a dry run.

## Setup

Scaffold an **empty** project (no `bootcamp_progress.json` content, no preferences) —
this phase tests the fresh-start path:

```bash
python3 .claude/skills/dry-run/scaffold_project.py "$HOME/senzing-bootcamp-phase3" --fresh
```

**Then do a second, short walk with `--seeded`.** It pre-fills exactly the preferences
INV-133 makes honorable (`path`, `verbosity: minimal`, `programming_language: Java`), so
Bootcamp preparation must **skip** Steps 1, 3 and 4 and mark each line
"from your saved preferences" in its Step 7 recap:

```bash
python3 .claude/skills/dry-run/scaffold_project.py "$HOME/senzing-bootcamp-phase3" --seeded
```

Both directions are needed and the first run only proves one of them. A walk where
everything was asked exercises the honor path **only in its inert direction** — it shows
the rule does not fire when it shouldn't, and says nothing about whether it fires when it
should. The seeded walk is short: preparation should ask nothing at all and hand straight
off, which is also the fastest way to catch a step that asks anyway.

Run only as far as the SDK is not required. **Onboarding preface → Bootcamp
preparation → Module 0 → Module 1** needs MCP access and nothing else, and it covers
the densest concentration of interaction invariants in the plugin. Going further
means installing the SDK, a database, and a licence — worth doing eventually, but a
different exercise.

Tell the maintainer up front which stretch you plan to cover and that they should
answer as themselves.

## How to run it

Follow the skill files **as written**, not from memory of what they should say. Read
`onboarding-flow.md`, then `bootcamp-preparation/SKILL.md`, and execute their
numbered steps in order. The point is to find where following them faithfully
produces something wrong — which cannot happen if you are improvising a good
bootcamp instead.

Keep the two channels separate:

- **The bootcamp output** — exactly what a Bootcamper would see. Nothing else.
- **A collapsed test-notes block** after it, clearly marked ignorable, holding your
  observations. Do not narrate findings inside the bootcamp text; it changes what is
  being tested.

⛔ **The test-notes blocks are working notes, not the record.** They live in the conversation
and die with it. The moment an observation firms up into a finding, write it into a
`specs/` file — see the SKILL's "What to do with a finding", rule 1. Do this *during* the
walk, not at the end: this phase stops on whatever turn the maintainer stops it, so "I'll
write it up when we finish" is a bet that there is a finish. A walk that reached eight turns
holding four findings in conversation alone is why this paragraph exists.

## What to watch for

Interaction invariants, in rough order of how often they break:

- **INV-005 / one 👉 per turn.** Exactly one, ending the turn. Zero or two is a
  violation — including a stray question inside an acknowledgment.
- **INV-133 / saved preferences.** A preference already in
  `config/bootcamp_preferences.yaml` must be honored and its question **not asked**.
  Pre-seed one (e.g. `verbosity: minimal`) on a second run and see whether it is
  asked anyway. Only `model_guidance` implements the read-first check today.
- **INV-006 / ask-once.** Nothing re-asked unless the Bootcamper requested a repeat.
- **INV-058 / one consolidated write.** Bootcamp preparation must show the maintainer
  **one** config diff, not one per gate. Count the diffs.
- **Apparatus exemptions.** Bootcamp preparation and Module 0 must show *no* journey
  map, before/after, step overview, time estimate, or model/effort nudge (INV-075,
  INV-078). Content modules must show all of them (INV-028–031, INV-096).
- **INV-079 / names not numbers.** No "Module 4" in anything the Bootcamper reads,
  including casual acknowledgments.
- **INV-051 / no "or" joining choices.** Numbered lists, neutral lead question. The
  only sanctioned "or" is a trailing `(respond yes or no)`.
- **INV-112 / the quiz offer.** Module 0 must present it verbatim every run;
  "optional" describes the answer, not whether it is asked.
- **INV-005 pinned wording.** Compare each ⛔ gate question against the pinned text
  character for character (INV-056). Paraphrase is the failure mode.

## The finding class unique to this phase

Phases 1 and 2 find things that are *wrong*. Phase 3 also finds rules that are
**unsatisfiable** — instructions the guide is told it must follow and provably
cannot. The originating run hit one immediately: `ground-rules.md` requires every
acknowledgment to reference "at least one specific thing they said" and forbids a
bare "Got it", but the answer to "any questions before we get started?" is often just
"no", where there is nothing specific to reference and no carve-out exists.

These are worth reporting even at low severity, because an instruction that cannot be
followed trains the model to treat the surrounding instructions as advisory.

## What this walk cannot test — say so rather than implying coverage

The walk is an assistant following the skill files in a normal session, which leaves real
gaps. Name them in the report; a phase-3 run that lists findings without listing these
reads as broader coverage than it had.

- **Administrative write noise.** INV-012 wants config writes unnarrated, and
  `hooks/README.md` records that no harness mechanism suppresses Write/Edit diffs — so the
  plugin minimises write *frequency* instead (INV-058's single consolidated write). During
  a walk you will likely write config with `Bash`, which renders as tool output rather than
  an inline diff, so **the walk cannot tell you whether the noise INV-058 exists to reduce
  is actually reduced**. What it *can* check is the count: one write per file at Bootcamp
  preparation, not one per gate.
- **The hooks do not fire.** They are installed globally with the plugin, not by running
  these files, so `SessionStart` / `Stop` / `UserPromptSubmit` stay silent in a walk. In
  particular the `Stop` hook's closing-question safety net is untested here — phase 2
  executes all six directly instead.
- **Anything past the SDK.** The walk stops where a real Senzing install is needed, so the
  loads, the live visualisation server, and graduation's deliverables are out of reach.
- **The assistant's own compliance is not evidence.** A walk shows that following the files
  *can* produce correct behaviour. It cannot show that a different assistant, or the same
  one without a maintainer watching, would land the same way. Findings are trustworthy;
  clean stretches are weaker evidence than they feel.

## Stopping

Stop wherever the maintainer stops — a partial walk is still evidence, and the
findings do not depend on reaching graduation. Then clean up the project and report,
naming exactly how far you got so the untested remainder is visible.

⛔ **Before stopping, confirm every finding is in a spec.** The stop is not yours to schedule,
so treat each turn as potentially the last: an observation that has firmed up and is still only
in a test-notes block is one message away from being lost. A partial walk whose findings are
written down is a contribution; a partial walk whose findings are not is a conversation.
