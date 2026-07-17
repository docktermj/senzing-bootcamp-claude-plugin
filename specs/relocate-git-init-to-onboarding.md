# Move the optional git-init question into onboarding, after language selection

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The optional "would you like me to initialize a git repository for version
control?" question is asked in Module 1, Phase 1, Step 1 — the first step of the
first module. The bootcamper wants it grouped with the other setup-adjacent
decisions in onboarding, right after the programming-language choice, so all the
setup decisions happen together before Module 1's actual work begins.

> "It fits naturally alongside the programming-language choice, before setup
> starts … simply move the question."

## Root cause

Not a defect — this is the current designed location:

- The git-init question lives at
  `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:6-20`
  (Module 1, Phase 1, Step 1): check `git rev-parse` (skip if already a repo);
  otherwise ask the pinned 👉 question; on yes run `git init`; checkpoint step 1.
- The programming-language gate the bootcamper wants it to follow is at
  `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:162-183`
  (step 7), just before the "any questions" step (step 8, `:185-203`) and the
  consolidated preference write.

No invariant pins git-init to Module 1 (it is not among INV-033/INV-034's Module 1
outcomes), so it can move. The move must preserve the existing semantics:

1. The "already a repo → skip the question" check (`phase1-discovery.md:14`).
2. `git init` is an **action**, not just a stored preference — onboarding's
   consolidated write (`onboarding-flow.md:197-203`) persists *choices*; running
   `git init` during onboarding must be done as part of the (quiet,
   administrative) setup, not folded into that preference write.
3. Checkpoint/step-numbering: removing Step 1 from `phase1-discovery.md` renumbers
   the remaining steps (privacy reminder, pattern-gallery offer, discovery
   paths, …) and their `config/bootcamp_progress.json` checkpoints.

## Proposed change

Relocate the git-init decision from Module 1 Step 1 into the onboarding preface,
immediately after the programming-language gate (step 7) and before "any
questions" (step 8):

- Add a new onboarding sub-step (e.g. step 7b) that performs the same logic:
  check whether the working directory is already a git repo (cross-platform);
  if not, ask the pinned 👉 git-init question verbatim; on yes run `git init`; on
  no, skip. Keep it optional and single-meaning (INV-008), reusing the existing
  pinned wording from `phase1-discovery.md:16`.
- Run `git init` as part of onboarding's quiet administrative setup (it is an
  action), not via the consolidated preference write; if a `git_init` preference
  is recorded, include it in that single consolidated write (INV-058) rather than
  adding a separate write.
- Remove Step 1 from `phase1-discovery.md`, renumber the remaining Phase 1 steps
  and their progress checkpoints, and confirm nothing else references the old
  "Step 1 = git-init" numbering.
- Make the repo-detection check cross-platform (the current example shows only
  the Linux/macOS `git rev-parse --git-dir 2>/dev/null` form); ensure it works on
  Windows too.

## Acceptance criteria

- [ ] The git-init question is asked during onboarding, immediately after the
      programming-language gate, and is no longer asked in Module 1.
- [ ] The "already a git repo → skip the question" behavior is preserved in the
      new location.
- [ ] `git init` runs as a quiet administrative action when accepted; any
      recorded `git_init` preference is folded into the single consolidated
      preface write (INV-058), adding no extra write.
- [ ] Module 1 Phase 1 steps and their `config/bootcamp_progress.json`
      checkpoints are renumbered consistently, with no dangling references to the
      removed Step 1.
- [ ] The git-init 👉 question stays pinned verbatim (INV-056), single-meaning
      (INV-008), and exactly one 👉 ends its yielding turn (INV-005).
- [ ] Repo detection and `git init` work on Linux, macOS, and Windows and stay
      language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — add the git-init sub-step after step 7 (`:162-183`); wire any `git_init` preference into the consolidated write (`:197-203`).
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — remove Step 1 (`:6-20`) and renumber the remaining Phase 1 steps and checkpoints.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — if the progress/step-boundary guidance references the Module 1 step numbering, reconcile it.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Move the git-init question into onboarding, after language selection" (2026-07-17, Module 1)
- Priority: Medium
- Related specs: `specs/auto-detect-platform.md` (also edits onboarding step 7, but for OS detection — distinct); none covering git-init.
