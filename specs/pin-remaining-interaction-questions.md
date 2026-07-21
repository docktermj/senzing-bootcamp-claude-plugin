# Pin the remaining un-pinned Bootcamper questions and fix the next-module prose

Maintain the invariant conditions in @INVARIANTS.md and fix the following issues:

## Problem

The final review found the last few Bootcamper-facing questions still left to the model to phrase,
plus one hardcoded module name:

1. **A1 (INV-051/009).** Module 4's data-provision question — "upload a file, provide a URL/file
   path, connect to a database, **or** use an API endpoint" — is un-pinned prose with `or`-joined
   choices, the one multi-choice prompt in the plugin not rendered as a `👉` + numbered list.
2. **B1 (INV-076/079).** Module 2's transition lead-in hardcodes "The next module (System
   verification) …" directly above the correct `{next module name}` placeholder — factually wrong in
   a Customized path that deselects System verification (an optional module).
3. **A2 (INV-005/056).** Two yes/no offers left un-pinned: the Module 6 UAT offer
   (`phaseD-validation.md:81`) and the Module 5 Phase-3 decision gate
   (`phase3-test-load.md:139`, "Ask the bootcamper to review the results before proceeding").
4. **A3 (INV-074).** `feedback-capture.py`'s injected context recaps the feedback steps but never
   mentions the pinned BOOTCAMP FEEDBACK / FEEDBACK SAVED banners, so a run that follows the injected
   list without loading `feedback.md` could skip them.
5. **A4.** Internal step-number typo in `phase1-discovery.md`: heading "6b–6d" but items labeled
   `7b/7c/7d`.

## Root cause

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:101-102`
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:756`
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md:81`
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md:139`
- `plugins/senzing-bootcamp/scripts/feedback-capture.py:41-57`
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:233-235`

## Proposed change

1. Pin the Module 4 data-provision question verbatim as `👉 … Reply with a number:` (1) upload a
   file, (2) provide a URL or file path, (3) connect to a database, (4) use an API endpoint — no
   `or`-joined choices.
2. Make the Module 2 lead-in generic ("The next module in your selected sequence …") so it never
   names a module a Customized path skipped.
3. Pin the UAT offer (`👉 Would you like to involve business users…? (respond yes or no)`) and the
   Module 5 Phase-3 decision gate (`👉 Are you ready to proceed? (respond yes or no)`).
4. Add a clause to `feedback-capture.py`'s injected context to begin/end with the pinned feedback
   banners (see `feedback.md`).
5. Renumber the `phase1-discovery.md` items to `6b/6c/6d`.

## Acceptance criteria

- [x] The Module 4 data-provision question is a pinned `👉` + numbered list with no `or`-joined choices (INV-051).
- [x] Module 2's transition prose no longer hardcodes the next module name; only the `{next module name}` placeholder resolves it (INV-076/079).
- [x] The UAT offer and Module 5 Phase-3 gate are pinned `👉` yes/no questions (INV-005/056/008).
- [x] `feedback-capture.py` injected context references the pinned feedback banners (INV-074); the file still parses as valid Python.
- [x] `phase1-discovery.md` step items are numbered `6b/6c/6d`.
- [x] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md`
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md`
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md`
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md`
- `plugins/senzing-bootcamp/scripts/feedback-capture.py`
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` (item renumber)

## Source

- Audit (fourth deep-dive, final review), 2026-07-19 — interaction-pin findings; maintainer chose "fix all verified findings".
- Priority: Low.
- Related specs: `specs/interaction-or-questions.md`, `specs/onboarding-explore-gate-wording.md`.
