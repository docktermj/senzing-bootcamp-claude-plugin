# The recap checkpoint is folded and cleared by machinery, but written only by model compliance

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`docs/progress/recap_checkpoint.md` was never created across all ten completed modules of a
full bootcamp run, and `docs/progress/` did not exist — in a session that had crossed at
least one context-compaction boundary, which is precisely when the checkpoint is supposed to
earn its keep.

⚠️ **The reporting entry's root cause is wrong, and the correct one is worse.** It says "No
step in any module skill says to write or update it." The plugin in fact ships deterministic
machinery for the checkpoint:

- `hooks/hooks.json:48-54` registers `scripts/precompact-recap.py` on the **PreCompact**
  event.
- `scripts/precompact-recap.py:18-24` calls `recap_checkpoint.fold_checkpoint()` when
  `recap_checkpoint.bootcamp_active()`, then **prints a reminder**: "Keep the current
  module's in-progress recap saved to `docs/progress/recap_checkpoint.md` (append-only,
  refreshed at each step boundary)".
- `bootcamp-onboarding/module-completion.md` Step 2d and `graduation/SKILL.md` Step 1a both
  read, fold, or clear it.

So every operation on the file is automated **except creating it**. Folding is
deterministic; clearing is deterministic; writing is a sentence addressed to the model. The
run that produced this report is the outcome that design predicts.

Two consequences the entry did not reach:

1. **The reminder arrives too late to help.** It is emitted by the *PreCompact* hook — it
   cannot fire until a compaction is already happening. Before the first compaction the
   guidance is nowhere in the model's context at all, which is exactly the window in which
   the checkpoint would have to have been written for the fold to have anything to fold.
2. **`fold_checkpoint()` on a file that never existed is a silent no-op.** Nothing
   distinguishes "folded a checkpoint" from "there was nothing to fold", so ten modules
   passed with the safety net absent and no signal anywhere.

Nothing failed in this run, because the finalized `## {Module name}` sections are appended
at each module's close as designed (INV-103). The loss is confined to the case the
checkpoint exists for: **a module interrupted mid-way**, where graduation's recovery path
reads a file that will not be there.

## Root cause

The contract was specified from the consumer's end. Two skills and one hook describe
reading, folding and clearing the checkpoint; no component owns producing it. That is
invisible in review because each half reads as complete on its own — and it survives
because the append-at-close design works, so nothing ever exercises the recovery path.

INV-059 requires the in-progress recap be checkpointed at step boundaries. Nothing enforces
it, and `coverage_reports.py invariants` does not currently flag INV-059 because a test
cites it — the citation is about the *file path*, not about anything writing to it.

## Proposed change

Pick one of two coherent designs and make the whole contract match it. **Do not leave the
current split.**

**Option A — make the writer deterministic (preferred).** Have `recap_checkpoint.py` own
creation as well as folding, invoked from the same hook family that already runs at step
boundaries, so the file exists without model compliance. Then `fold_checkpoint()` must
distinguish "folded N sections" from "no checkpoint present" on stderr (INV-111), so a
missing checkpoint is legible rather than silent.

**Option B — drop the consumer half.** Remove the fold-and-clear instructions from
`module-completion.md` Step 2d and `graduation/SKILL.md` Step 1a, delete the PreCompact
reminder, and rely on the append-at-close design that demonstrably works. Then reconcile
INV-059, which currently requires a checkpoint nothing produces — per `INVARIANTS.md`'s
rules, by appending a dated superseding note, never by deletion.

Whichever is chosen, the acceptance criteria below apply to it. Option A keeps a real
safety net; Option B removes a contract that reads as maintained and is not. Keeping the
current state is the one outcome that misleads a future reader, because the clean-up
instructions imply a file that routinely exists.

## Acceptance criteria

- [ ] Either something deterministic writes `docs/progress/recap_checkpoint.md` during a
      module (Option A), or no shipped file instructs folding or clearing it (Option B).
- [ ] No shipped text describes the checkpoint as routinely maintained unless a component
      maintains it.
- [ ] Under Option A: `fold_checkpoint()` reports on stderr whether it folded anything, so
      an absent checkpoint is not a silent no-op (INV-111).
- [ ] Under Option B: INV-059 carries a dated superseding note; it is neither deleted nor
      renumbered.
- [ ] A test asserts the chosen design end to end — that a simulated module boundary
      produces the file (A), or that no skill references folding it (B). The current gap was
      invisible to 1156 tests.
- [ ] The append-at-close recap behaviour (INV-103) is unchanged either way — it is what
      kept this run correct.
- [ ] MCP re-check: n/a — no Senzing fact is involved.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/recap_checkpoint.py` — creation and the fold report (Option A).
- `plugins/senzing-bootcamp/scripts/precompact-recap.py` — the reminder (both options).
- `plugins/senzing-bootcamp/hooks/hooks.json` — hook wiring, if a step-boundary writer is added.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — Step 2d.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1a.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — where the step-boundary rule would be stated.
- `specs/INVARIANTS.md` — INV-059, under Option B only.
- `tests/` — the end-to-end assertion.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "nothing ever creates
  docs/progress/recap_checkpoint.md, though two documents describe maintaining and clearing
  it" (2026-07-31, Module: General; `Source: self-observed (assistant retrospective)`)
- Priority: Low as reported; the redirected root cause does not raise it — the impact is
  still confined to interrupted modules — but it widens the fix from a doc change to a
  design choice.
- MCP re-check: n/a (no Senzing fact).
- **Re-triaged:** the entry's root cause ("no step instructs creating it") is incorrect.
  `hooks.json:48` and `precompact-recap.py:18` show the machinery exists and that creation
  is delegated to the model by a reminder that cannot fire before the first compaction. The
  spec's subject changed accordingly, from documenting a step to resolving a split contract.
- Upstream: not applicable.
- Related specs: `specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (INV-111, the
  silent-no-op rule this invokes), `specs/consolidate-recap-per-module-summary.md` (INV-103).
