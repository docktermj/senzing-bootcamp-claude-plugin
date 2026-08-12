# Bootcamp preparation summarises the model/effort trigger as the comparison ground-rules forbids

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two shipped files state the trigger for the model/effort switch question in incompatible terms, and
the wrong one is the summary a guide is most likely to read first — it sits in the module that
*retires* the old model-guidance question, so a guide arriving there is already thinking about this
subject.

**`bootcamp-onboarding/ground-rules.md:535-551` (authoritative, and explicit):**

> ⛔ **Compare the recommendation against what the bootcamper is running right now — not against the
> previous stage's recommendation.** … ⛔ Applying the previous-stage row to a dial that *was*
> determinable is the failure this clause exists to prevent: a bootcamper demonstrably on Opus 5
> would be compared against the previous stage's recommended Sonnet 5, found "unchanged", and never
> offered the switch — **silently defeating the purpose of the invariant this superseded.**

**`bootcamp-preparation/SKILL.md:212-216` (the summary):**

> at each module start and graduation start the guide surfaces the stage's recommendation, and **when
> the recommendation changes** it pauses on the pinned switch question followed by the pinned "Are
> you done modifying the model and effort?" gate; **when it is unchanged** it is a one-line
> statement.

"When the recommendation changes" / "when it is unchanged" is recommendation-to-recommendation — the
comparison the ⛔ forbids by name.

**This is not hypothetical; it changed the behaviour of a live walk.** Executing the files as written
on 2026-08-12, entering **Discover the Business Problem** on the Claude Code CLI:

| Trigger read | Comparison | Outcome |
|---|---|---|
| `ground-rules.md` (correct) | running **Opus 5** vs recommended **Sonnet 5** → differs | **Switch question asked**, model dial only |
| `bootcamp-preparation/SKILL.md` (summary) | previous stage recommended Sonnet 5, this stage recommends Sonnet 5 → unchanged | **One-line statement, no switch question** |

The stage table (`docs/model-selection.md:158-162`) recommends Sonnet 5 at medium effort for
Onboarding, Bootcamp preparation, Entity Resolution Concepts **and** Discover the Business Problem —
four consecutive identical rows. So for the first four stages of every Core run, the summary's
reading suppresses the switch question entirely, for exactly the bootcamper `ground-rules.md` names:
one who is "demonstrably on Opus 5". Running one model for the whole bootcamp is called out there as
"the common case, not an edge case".

**Why the summary is the dangerous half.** `ground-rules.md`'s clause is long, carries two ⛔ markers
and a worked example, and is hard to misread *once reached*. The preparation file's sentence is
short, declarative, and sits at the end of Step 3a — the step that exists to say "ask nothing here" —
so a guide reading it has no signal that the one-clause trigger it states is a simplification of a
17-line rule with a per-dial resolution procedure.

**No Senzing fact is involved.** Internal consistency only; no MCP tool was called for this finding.

## Root cause

`INV-137` restored the unconditional switch-question behaviour, superseding INV-119/INV-120, and the
detailed rule was written into `ground-rules.md` where the behaviour lives. `bootcamp-preparation`
Step 3a was rewritten in the same change to say the question is retired, and it added a one-sentence
description of what happens instead — a pointer, not a specification. It was phrased from the
*stage table's* point of view ("the recommendation changes", which is what a reader of that table
sees) rather than from the *session's* point of view, which is what the rule requires.

The per-dial resolution (`:537-543` — model compared directly when determinable, effort falling back
to the completed stage only because it "is exposed nowhere and typically cannot be read at all") came
later still, and the summary was never revisited against it. Nothing links the two: no test asserts
that the files agree, and the divergence is invisible to the suite because both sentences are
individually well-formed prose.

## Proposed change

1. **Correct the summary to point rather than paraphrase.** In `bootcamp-preparation/SKILL.md:212-216`,
   replace "when the recommendation changes … when it is unchanged" with the session-relative
   trigger and an explicit deferral — e.g. *"…and when the stage's recommendation differs from what
   the bootcamper is running right now (compared per dial), it pauses on the pinned switch question…;
   when it already matches, it is a one-line statement. `ground-rules.md` → 'Best-value model/effort
   prompt' is authoritative for the comparison, including the per-dial rule for a value that cannot
   be read."*
2. **Do not restate the per-dial procedure there.** Two copies is how this happened. The summary
   should carry the *direction* of the comparison (against the session, not the previous stage) and
   nothing more.
3. **Guard the agreement.** A test asserting that no shipped file describes the model/effort trigger
   as a change in the *recommendation* between stages — i.e. no file outside `ground-rules.md`'s
   authoritative clause pairs the trigger with "recommendation changes"/"unchanged" phrasing. That is
   the durable form: it catches the next paraphrase wherever it appears.

**Do not touch `ground-rules.md:535-563`.** It is correct, and its two ⛔ markers and worked example
are load-bearing — the spec's job is to make the summary agree with it, not to re-litigate it.

## Acceptance criteria

- [ ] `bootcamp-preparation/SKILL.md`'s Step 3a describes the trigger as the stage recommendation
      versus **what the bootcamper is currently running**, not as a change between stages, and defers
      to `ground-rules.md` for the comparison procedure.
- [ ] No shipped file states or implies that the switch question fires only when the recommendation
      differs from the **previous stage's** recommendation.
- [ ] `ground-rules.md:535-563` is unchanged (`git diff` shows no edit to the authoritative clause).
- [ ] A test asserts the property in criterion 2 across all shipped skill/command files.
      Negative-controlled: restoring the "when the recommendation changes" phrasing fails the suite,
      with the mutation verified to land.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      documentation and a text assertion only.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — Step 3a's summary (`:212-216`).
- `tests/` — the agreement guard.

## Source

- Dry run: `dry-run` phase 3 (conversational walk), 2026-08-12, at the Module 1 start apparatus on
  the Claude Code CLI (`Source: self-observed (assistant retrospective)`). Found by needing to
  *decide* whether to ask the switch question and finding two files answering differently — the
  divergence is invisible when reading either file alone, which is why a walk surfaced it and three
  audits did not.
- Priority: **Medium.** Not cosmetic: under the summary's reading the switch question is suppressed
  for the first four stages of every Core run, which is the precise outcome `ground-rules.md` calls
  "silently defeating the purpose of the invariant this superseded". Bounded because the authoritative
  file is correct and a guide that reaches it behaves properly.
- MCP re-check: **n/a — no Senzing fact.** No tool called for this finding.
- Upstream: not applicable.
- Related specs: `specs/preparation-recap-template-contradicts-its-own-rules.md` (a second
  self-inconsistency in the same file, found in the same walk),
  `specs/model-effort-guidance-advisory-not-gate.md` and
  `specs/model-switch-single-turn-continuation.md` (prior work on this gate's behaviour).
