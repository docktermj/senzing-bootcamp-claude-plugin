# Empty progress file makes resume unsatisfiable

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A bootcamper who quits any time between the onboarding preface's silent project
setup and Bootcamp preparation's Step 6 write comes back to a session that
announces a bootcamp is in progress and then has nothing to resume from. The
guide is told, by three separate places, to "offer to resume from the last
recorded module" when there is no recorded module.

`config/bootcamp_progress.json` exists and is `{}` for that whole window, because
`onboarding-flow.md` Step 1 creates it empty and nothing writes to it again until
Bootcamp preparation Step 6. That window spans the entire preface plus all seven
Bootcamp-preparation steps — the Core/Customized gate, module selection,
verbosity, and the programming-language gate — so it is not a narrow race.

The observable result on the next session is the `SessionStart` hook printing:

```text
A Senzing bootcamp is in progress. Read config/bootcamp_progress.json and offer
to resume from the last recorded module before doing anything else.
```

followed by a guide that cannot do what it was just told to do, on a project
where the correct behaviour is to run onboarding from the top.

## Root cause

Every resume decision in the plugin tests the progress file's **existence**, never
its **content**:

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/SKILL.md:23-28` — "Check for
  `config/bootcamp_progress.json` … **Missing** -> fresh … **Present** -> a bootcamp
  is already underway. Read it and offer to resume from the last recorded
  module/step."
- `plugins/senzing-bootcamp/scripts/recap_checkpoint.py:54-56` —
  `bootcamp_active()` returns `os.path.isfile(PROGRESS)`.
- `plugins/senzing-bootcamp/scripts/session-start.py:18-25` — gates the resume
  message on `bootcamp_active()`.
- `plugins/senzing-bootcamp/commands/start-bootcamp.md:8` — "file exists in the
  working directory, resume from the last recorded module; otherwise …".

`recap_checkpoint.current_module()` (`:65-78`) already returns `None` for a
progress file with no usable `current_module`, so the distinction the callers need
is computed and then not used by any of them.

The file is created empty by design:
`plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:75-76`
("Create `config/bootcamp_progress.json` … if they do not exist"), and the first
write that gives it a `current_module` is
`plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md:358-360`.

n/a — no Senzing fact is involved.

## Proposed change

Make "a bootcamp is underway" mean *the progress file records a module*, not *the
progress file exists*, in all four places:

1. `bootcamp-onboarding/SKILL.md` — replace the two-way Missing/Present branch with
   three cases: missing → fresh; present but recording no `current_module` (empty,
   `{}`, malformed, or `current_module` null/blank) → **fresh, run onboarding from
   the top, silently**; present with a `current_module` → resume. State explicitly
   that an empty progress file is the normal state during the preface and Bootcamp
   preparation, so it is not a corruption to report to the bootcamper (INV-012).
2. `commands/start-bootcamp.md` — same three-way wording.
3. `recap_checkpoint.bootcamp_active()` — return true only when
   `current_module()` is not `None`, keeping the existing never-raises contract
   (INV-048). Check the other `bootcamp_active()` callers before changing it;
   `checkpoint-tick.py` and the fold hooks share it, and a scaffold-only checkpoint
   during onboarding is exactly the case they already skip.
4. `session-start.py` — no change needed once `bootcamp_active()` tightens, but
   confirm the no-fold branch's message still reads correctly.

Prefer fixing the shared predicate over the four call sites: the class is
"existence stands in for content", and `bootcamp_active()` is where it is cheapest
to remove.

## Acceptance criteria

- [ ] With `config/bootcamp_progress.json` present and containing `{}`,
      `recap_checkpoint.bootcamp_active()` is false and `session-start.py` prints
      nothing.
- [ ] Same for a progress file that is empty, is not a JSON object, is malformed
      JSON, or has `current_module` set to `null` or `""`; none of these raise.
- [ ] With `current_module` set to a non-empty string, `bootcamp_active()` is true
      and the resume message is printed unchanged.
- [ ] `bootcamp-onboarding/SKILL.md` and `commands/start-bootcamp.md` each state
      the three-way branch, and say that a contentless progress file means fresh
      start rather than corruption.
- [ ] A test in the repo-level `tests/` covers the empty-`{}` case and is
      negative-controlled (reverting the predicate to `isfile` fails it).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/recap_checkpoint.py` — `bootcamp_active()` tests
  for a recorded module, not for the file.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/SKILL.md` — three-way
  fresh/contentless/resume branch.
- `plugins/senzing-bootcamp/commands/start-bootcamp.md` — same wording.
- `plugins/senzing-bootcamp/scripts/session-start.py` — confirm messages still read
  correctly under the tightened predicate.

## Source

- Feedback: dry run phase 3, 2026-08-13 — found during setup of the `--fresh`
  scratch project, whose `bootcamp_progress.json` fixture is `{}` (`Source:
  self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: none
