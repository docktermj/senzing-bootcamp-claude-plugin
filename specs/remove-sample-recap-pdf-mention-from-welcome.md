# Remove the sample recap PDF mention from the WELCOME overview

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

During the WELCOME overview, onboarding shows a non-blocking sentence pointing the
bootcamper to the bundled example recap PDF:

> "A sample of a finished recap ships with the plugin at
> `docs/examples/bootcamp_recap.example.pdf` (under the plugin root,
> `${CLAUDE_PLUGIN_ROOT}`); point the bootcamper to it if they'd like to see what
> theirs will look like (yours will differ). This is a non-blocking mention, not a
> question or a gate."

The bootcamper finds this pointer unnecessary in the welcome overview and wants it
deleted.

## Root cause

The sentence lives in `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:94-98`,
inside `## 3. Welcome and overview (preface item 1)` (header at `:78`). It was added
deliberately by the implemented spec `example-recap-reference` (INV-065), which
requires the example asset to **ship** but does **not** require the overview to
mention it. Two other pointers to the same asset exist and are out of scope:
graduation's own pointer (`graduation/SKILL.md:82-85`) and the README doc links
(`README.md:147`, `:169`).

## Proposed change

Delete the sample-PDF pointer sentence from `onboarding-flow.md` §3. Leave the
bundled example `.md`/`.pdf` in place (still shipping, still regenerable) and leave
the graduation Step 1 pointer and README links untouched — they are separate
mentions, not the welcome overview.

## Acceptance criteria

- [ ] The WELCOME overview no longer mentions `docs/examples/bootcamp_recap.example.pdf`.
- [ ] The example `.md` and `.pdf` still ship inside the plugin and remain regenerable via `generate_recap_pdf.py` (INV-065 intact).
- [ ] The graduation Step 1 example-PDF pointer and the README links remain unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — remove the sample-PDF pointer sentence in §3 (`:94-98`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Remove sample recap PDF mention from welcome overview" (2026-07-22, Module Onboarding)
- Priority: Medium
- Related specs: `specs/example-recap-reference.md` (added this mention — removal partially undoes its overview clause; INV-065 unaffected)
