# Initialize git automatically without prompting

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

During Bootcamp preparation Step 5 (version control), when the working directory is
not already a git repository, the bootcamp asks an optional 👉 question:

> "If you don't know what 'git' is, just skip this. It's optional: would you like me
> to initialize a git repository for version control?"

The bootcamper considers the answer to always be "yes," so the question adds a
needless turn with no real decision behind it. They want git initialized
automatically with no prompt.

## Root cause

`plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md:211-232`
(`## 5. Initialize version control`). Detection at `:218`
(`git rev-parse --is-inside-work-tree`); if already a repo, holds `git_init: existing`
(`:221-222`); if not a repo, asks the pinned question at `:225` and branches to
`git_init: true` (yes) or `git_init: false` (no) at `:227-229`. The value is written
in the consolidated write `## 6` (`:234-244`, key referenced at `:239`).

**Invariant note (do not silently override):** this **amends INV-075**, which
enumerates "the version-control (git-init) question" as one of preparation's
questions. The git-init *action* stays; the *question* is removed, so the
pinned-verbatim (INV-056) and one-👉-per-turn (INV-005) guarantees simply stop
applying to it. Related spec `relocate-git-init-to-onboarding` preserved this
question and its yes/no branches; this removes them. `auto-detect-platform` is the
analogous "detect, don't ask" precedent.

## Proposed change

Remove the §5 git-init 👉 question and its "no" branch. When the working directory is
not already a git repository, run `git init` automatically as a quiet administrative
action (INV-012) and record `git_init: true` in the consolidated write; when it is
already a repo, record `git_init: existing`. Never prompt. If `git` is unavailable,
degrade gracefully (record e.g. `git_init: unavailable`, warn-and-continue — do not
block). Optionally, provide a preferences/env opt-out for environments that
deliberately want no repo (maintainer decision), with the default being
"initialize automatically, no prompt." Amend INV-075 to reflect the question's
removal.

## Acceptance criteria

- [ ] Bootcamp preparation never presents a git-init question.
- [ ] When the working directory is not a git repo and `git` is available, `git init` runs automatically and `git_init` is recorded as `true`; when already a repo, `git_init: existing`. The `git_init: false` value no longer occurs.
- [ ] When `git` is unavailable, the step degrades gracefully without blocking.
- [ ] The action runs quietly with no bootcamper-facing prompt noise (INV-012).
- [ ] `INVARIANTS.md` is updated to amend INV-075 (git-init question removed; action retained).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — §5 (`:211-232`) remove the question; §6 (`:234-244`) record `git_init` from auto-init.
- `specs/INVARIANTS.md` — amend INV-075.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Don't ask the git-init question — always initialize git automatically" (2026-07-22, Module Bootcamp preparation)
- Priority: Medium
- Related specs: `specs/relocate-git-init-to-onboarding.md`, `specs/auto-detect-platform.md`; INV-075

## Invariants introduced

- `INV-095` — Bootcamp preparation auto-initializes git (`git init`) with no 👉 question when the directory is not a repo, recording `git_init: true`/`existing`/`unavailable`; it never prompts about version control (recorded in `specs/INVARIANTS.md`; INV-075 annotated to note the question's removal). Maintainer-approved wording.
