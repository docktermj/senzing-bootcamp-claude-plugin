# Pin the Module 1 "visual explanations" question so it can't drift into an ambiguous "or" question

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

At Module 1 Step 9 (encourage visual explanations), the bootcamper was asked:

> "👉 Do you have any diagrams of your data architecture or flows you'd like to
> share, or should I proceed with the scenario as described?"

This joins two alternatives with "or", so a bare "no" is ambiguous — it could mean
"no diagrams" or "no, don't proceed". The bootcamper flagged it as confusing and
noted it wastes a turn on clarification.

## Root cause (confirmed)

Step 9 is authored as **unpinned prose**, not a pinned verbatim 👉 question, so the
model improvised the ambiguous "or"-joined wording at runtime:

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md:5-8`
  — "## 9. Encourage visual explanations / Ask for diagrams of data architecture,
  data flows, or example records. If an image contains placeholders like
  `[variable]`, ask what each represents. **Checkpoint:** write step 9." There is no
  pinned 👉 question here, so INV-056 does not protect it — exactly the drift INV-056
  exists to prevent, and the improvised question violated INV-008/INV-009/INV-051.

This site is not covered by the prior `pin-visualization-offer-questions.md` audit
(which pinned other offers but not `phase2-document-confirm.md:5-8`) nor by
`interaction-or-questions.md` (which fixed enumerated questions elsewhere), so it is
a genuine new instance.

## Proposed change

Pin Step 9 as a single-purpose, verbatim 👉 question in
`phase2-document-confirm.md`, e.g.:

> 👉 **Do you have any diagrams of your data architecture or flows you'd like to
> share?**

Treat "no" as the standalone signal to proceed with the scenario as described — do
**not** fold the "proceed" branch into the question. Keep the follow-up handling
(placeholders like `[variable]`) as internal instruction after the pinned question.

## Acceptance criteria

- [ ] Step 9's question is written verbatim in `phase2-document-confirm.md` with a leading 👉 (INV-005), pinned so it can't drift at runtime (INV-056).
- [ ] The question has exactly one meaning for "yes" and one for "no" (INV-008), with no "or"-joined choices (INV-009/INV-051); "no" alone means "proceed with the scenario as described".
- [ ] A grep of 👉 lines in `phase2-document-confirm.md` shows no "or"-joined bootcamper question.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — pin the Step 9 question verbatim (`:5-8`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "An 'or'-joined question made 'yes'/'no' ambiguous (ground-rules violation)" (2026-07-18, Module 1).
- Priority: Medium.
- Related specs: `interaction-or-questions.md` (INV-051, the "or" rule), `pin-visualization-offer-questions.md` (INV-056 pinning audit — did not cover this site), `onboarding-explore-gate-wording.md` (INV-056 pinned-gate precedent).
