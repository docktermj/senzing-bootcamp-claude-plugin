# Verify and preserve the bootcamp feedback file so submitted feedback is never lost

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The bootcamp feedback file was found **missing/empty during graduation** and had to
be recreated; earlier entries were restored from the session record. Feedback the
bootcamper submitted mid-bootcamp was at risk of being silently lost. Verbatim, from
the recreated file's header:

> Note: this file was found missing/empty during graduation (2026-07-17) and was
> recreated. The two earlier entries below were restored from the session record;
> the third is the graduation entry. That the file went missing mid-bootcamp may
> itself be worth investigating.

Losing captured feedback undercuts `INV-015` ("Submitted bootcamp feedback is
captured in `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`") — capture that does
not persist is not capture.

## Root cause

**Confirmed durability gap.** The feedback workflow appends an entry and then tells
the bootcamper it was saved, but it never confirms the write actually landed:

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md:62-106` — Step 3
  appends the entry ("never overwrite"), Step 4 confirms *"Saved your feedback to
  `docs/feedback/…`"* and returns the bootcamper to where they were. There is **no
  re-read / verify-it-landed** step.
- Contrast the recap flow, which **does** verify:
  `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:91-96`
  ("2c. Verify it landed" — re-read the file, re-append if the section is missing).
  The recap also has a durability mechanism (`recap-durability` / `INV-059`:
  checkpoint + `PreCompact`/`SessionEnd`/`SessionStart` folding). The feedback file
  has **no** analogous verify or durability safeguard, so a lost or partial write (a
  session/compaction boundary, or a write that silently did not persist) goes
  unnoticed until someone looks — e.g. at graduation.

**Unverified — needs investigation.** The exact mechanism by which the file went
*fully* missing is not confirmed in code. No plugin path deletes `docs/feedback/`:
the `UserPromptSubmit` hook only injects guidance
(`scripts/feedback-capture.py`), graduation *excludes* `docs/feedback/` from the
production build (`graduation/SKILL.md:158`) and only *reminds* about it
(`:194-198`), and the graduation CommonMark pass targets `docs/*.md`
(`graduation/SKILL.md:86`), a non-recursive glob that should not reach
`docs/feedback/…`. Suspects to check: a never-verified lost write (most likely), a
session/compaction boundary, or a CommonMark/normalization implementation that
recurses into subdirectories.

## Proposed change

1. **Add a "verify it landed" step to the feedback workflow** (mirror the recap's
   `module-completion.md:91-96`). In `feedback.md`, after appending (Step 3) and
   **before** confirming (Step 4): re-read `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`
   and confirm the just-added `## Improvement:` entry is present. If it is missing,
   re-append it, then re-read again. Only claim "Saved …" after the entry is
   confirmed on disk.
2. **Guarantee graduation never clobbers the feedback file.** Make explicit (and
   guard) that the CommonMark normalization pass (`graduation/SKILL.md:86`) and the
   production-project build never delete, empty, or rewrite `docs/feedback/*.md`; the
   feedback file MUST survive graduation intact. (They appear to already avoid it —
   this pins the guarantee so a future change cannot regress it.)
3. **Investigate the disappearance path** listed under Root cause; if a concrete
   clobber/loss path is found, fix it. If none is found, the verify-it-landed
   safeguard is the mitigation. A full recap-style checkpoint is likely
   disproportionate for the small, infrequent feedback file — prefer the lightweight
   verify-and-re-append unless investigation shows it is insufficient.

## Acceptance criteria

- [ ] The feedback workflow re-reads the feedback file after appending and confirms the new entry is present **before** telling the bootcamper it was saved; if the write did not land, it re-appends and re-verifies.
- [ ] No graduation step (CommonMark normalization, production build, cleanup) deletes, empties, or rewrites `docs/feedback/*.md`; the feedback file survives graduation intact.
- [ ] The disappearance mechanism is investigated and documented; any concrete clobber/loss path found is fixed (else the verify-it-landed safeguard stands as the mitigation).
- [ ] `INV-015` continues to hold: submitted feedback is durably present in `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` — add a Step 4 "verify it landed" (re-read + re-append) before the success confirmation.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — make explicit that the CommonMark pass (`:86`) and production build never touch `docs/feedback/*.md`.
- (investigation) the CommonMark normalization step / any code that walks `docs/` — confirm it cannot reach `docs/feedback/`.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → recreated-file header note "found missing/empty during graduation" (2026-07-17, Graduation).
- Priority: Medium (data loss, but recoverable; touches `INV-015`).
- Related specs: `recap-durability.md` (`INV-059`, the analogous recap verify + durability mechanism this borrows from), `enrich-feedback-context.md` (`INV-053`, feedback context capture).

## Invariants introduced

- `INV-067` — When bootcamp feedback is appended to `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`, the write MUST be verified to have landed (re-read and confirm the entry is present, re-appending if not) before the bootcamper is told it was saved, and no later bootcamp step (CommonMark normalization, production build, cleanup) may delete or empty that file. (Hardens `INV-015`; mirrors the recap verify of `INV-059`.) (Recorded in `specs/INVARIANTS.md`, 2026-07-17.)
