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

## Stopping

Stop wherever the maintainer stops — a partial walk is still evidence, and the
findings do not depend on reaching graduation. Then clean up the project and report,
naming exactly how far you got so the untested remainder is visible.
