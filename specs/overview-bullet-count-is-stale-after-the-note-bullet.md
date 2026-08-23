# Overview bullet count is stale after the note bullet was added

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The onboarding preface's overview (step 3) is governed by a verbosity treatment table that
tells the guide what the overview *is* at each preset. The `standard` / `detailed` row reads
"all ten, as written", and the paragraph below it repeats "so all ten are shown". The list it
governs has **eleven** bullets.

A guide following the file literally has a count that disagrees with the list in front of it.
The two available readings are both wrong: present ten and silently drop a bullet (the note
bullet is the newest and the likeliest casualty, which would defeat INV-254 — an any-time
control nobody is told about is an any-time control nobody uses), or notice the mismatch and
treat the surrounding ⛔ instructions as approximate.

## Root cause

The count was written when the list had ten bullets and was not updated when an eleventh was
added. `1b42648` ("#1 feat(notes): let the Bootcamper capture their own ideas, and keep them")
appended the "Had an idea of your own? Say \"make a note\"…" bullet at
`plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:199` and added the
paragraph making it verbosity-aware, but left both occurrences of the literal "ten" as they
were.

Current bullets, `onboarding-flow.md:168-201` — guided discovery (168), goal (170), recap PDF
(171), the named-module sequence (173), the Core-vs-Customized preview (177), the Truth Set
visualization caveat (182), licensing (185), unfamiliar terms (187), how long it takes (189),
the feedback trigger (195), and the note bullet (199). Eleven.

The stale literals are at `onboarding-flow.md:160` (the treatment table's
`standard` / `detailed` row) and `onboarding-flow.md:164` (the fresh-bootcamp paragraph).

This is a count of the plugin's own prose, not a Senzing fact.

## Proposed change

Replace the hard-coded count with a form that cannot go stale the next time a bullet is added
or removed: say "every bullet below, as written" in the table row, and "so every bullet is
shown" in the paragraph. A count carries no information the reader does not already have from
the list — its only effect is to disagree with it eventually.

Apply the same treatment to any other place that counts this list.

## Acceptance criteria

- [ ] Neither `onboarding-flow.md:160` nor `:164` states a number of overview bullets; both
      refer to the list itself.
- [ ] A test asserts that the overview's verbosity treatment table carries no bare bullet
      count for the `standard` / `detailed` row, so re-introducing one fails.
- [ ] The `minimal` and `concise` rows are unchanged — neither counts, and both name their
      bullets by content.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — lines 160 and 164:
  drop the literal "ten" in favor of a reference to the list.
- `tests/` — a new guard that fails if the row states a count.

## Source

- Feedback: `/dry-run` phase 3, analysis starting at Bootcamp preparation (2026-08-21; onboarding
  preface, step 3; `Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: none
