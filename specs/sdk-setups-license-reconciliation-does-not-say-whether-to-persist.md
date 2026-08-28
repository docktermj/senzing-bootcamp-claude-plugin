# SDK setup's license reconciliation never says whether to persist, and two files still call Module 4 the only writer — so the gate this was meant to restore can stay suppressed

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`license-record-limit-has-a-detected-only-contract-nothing-enforces` (implemented 2026-08-28,
`999bcdd`) added a reconciliation step to SDK setup: read the recorded `license_record_limit`, run
the license check, and on a mismatch *"**take the measurement and say the recorded figure was
withdrawn**, naming both numbers"* (`module-02-sdk-setup/SKILL.md`, Step 5a).

**"Take the measurement" does not say whether to write it down, and both readings are wrong.**

**Reading A — do not persist.** SDK setup presents the corrected figure and leaves
`config/bootcamp_progress.json` holding the false one. Module 4's Step 8a then reads it and
**skips the gate**:

> **Volume-skip (the common case).** If the collected total is at or below the effective limit — or
> the limit is `0` (unlimited) — the built-in evaluation license suffices. State that briefly and
> skip to Step 8b. **Do not ask for a License Key.**
> — `module-04-data-collection/SKILL.md:807-809`

With the reported values — a stated `100000` against a measured `500`, on a ~94,000-record
scenario — 94,000 is "at or below" 100,000, so the single volume-gated prompt in the bootcamp is
suppressed. ⛔ **That is the exact failure the fix was written to prevent, surviving the fix.**

**Reading B — persist.** Then SDK setup writes `license_record_limit`, and two shipped files say
plainly that nothing but Module 4 ever does:

- `module-01-business-problem/phase1-discovery.md:312` — *"`license_record_limit` is **written only
  by Module 4's Step 8a gate**, which is volume-gated by design, so its absence here means *not yet
  measured*"*
- `module-06-data-processing/phaseA-build-loading.md:190` — *"**The only writer of
  `license_record_limit` is Module 4's Step 8a gate**, which is volume-gated by design: a bootcamper
  with a small dataset never triggers it, so the field is absent no matter what license is
  installed."*

Both statements become false, and they are load-bearing rather than decorative: each is the premise
for an *absence* branch that INV-244 governs. A reader who finds them false has no way to tell which
half of the sentence still holds.

⚠️ **The two claims survive Reading B in substance even though they are false as written** — SDK
setup's reconciliation only fires when the field is **present**, so it never creates a value where
there was none, and "absent means not yet measured" stays true. That is precisely why this needs
correcting rather than shrugging at: the conclusion is still right, the stated reason is not, and a
rule whose reason is wrong is one a later edit will "simplify" incorrectly.

## Root cause

The fix added a **second measurement point** without touching the **single-writer contract** that
three files share. The contract was written when Module 4 Step 8a was genuinely the only place a
license could be measured; SDK setup became a second such place the moment it was told to run the
check, because it is the first step at which the SDK exists.

Neither the spec nor its implementation noticed, because the single-writer statements live in the
*other* two modules and say nothing about SDK setup — so a sweep for `license_record_limit` finds
them, but a reader checking "did I break anything in module-02?" does not.

## Proposed change

1. **Say explicitly that SDK setup persists the measured value**, replacing the recorded one, and
   that it records what it replaced. Reading B is the right one: a correction the bootcamp knows
   about and does not write down is a correction that only affects one screen.
2. **Correct the single-writer statements in both files** to name the two legitimate writers —
   Module 4 Step 8a's gate and SDK setup's reconciliation — while keeping each absence branch's
   conclusion intact, since neither writer creates a value where none existed. ⛔ **Do not delete the
   reasoning**; restate it so the conclusion follows from what is now true.
3. **State the precedence once**: a measured value replaces a recorded one, whichever step measured
   it, and the replacement is announced when it lowers reported capacity. Cite it from the three
   sites rather than restating it (INV-179).
4. ⛔ **Do not have SDK setup write the field when it is ABSENT.** That would convert a
   volume-gated measurement into an unconditional one, contradict INV-093's single-prompt rule by
   the back door, and break the absent-means-not-yet-measured branch INV-244 depends on. The
   reconciliation fires only on a value that is already there.

## Acceptance criteria

- [ ] `module-02-sdk-setup/SKILL.md` Step 5a states that the measured value is **written to**
      `config/bootcamp_progress.json`, replacing the recorded one, and that the replaced figure is
      named.
- [ ] Step 5a states that it does **not** write the field when it is absent.
- [ ] Neither `phase1-discovery.md` nor `phaseA-build-loading.md` claims Module 4 Step 8a is the
      only writer; both name the two writers and keep their absence-branch conclusions.
- [ ] With a stated `100000` recorded, a measured `500`, and a ~94,000-record collection, Module 4's
      Step 8a **presents** the License-Key gate rather than volume-skipping it. ⚠️ This is the
      criterion that matters and it is **not** offline-testable — it is the end-to-end behavior the
      original fix claimed. Verify it in a `dry-run` phase-3 walk, or state plainly that it is
      unverified.
- [ ] A test asserts no shipped file calls any single step the only writer of
      `license_record_limit`, deriving its site set by scanning (INV-246). Stdlib only, no
      `plugins/` import (INV-108).
- [ ] Negative-controlled: restoring either "only writer" sentence fails the test, and so does
      removing the persist instruction.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 5a's reconciliation
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — `:312`
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — `:190`
- `tests/` — a guard on the single-writer claim

## Source

- Feedback: none — found by `/production-readiness-audit` on 2026-08-28, cycle 2 of the second
  unattended loop (`Source: self-observed (assistant retrospective)`). Found by a Step 4 coherence
  sweep of the license state machine across the four modules that touch it — chosen as the rotation
  target precisely because that area had just been changed, which is where a fresh contradiction is
  most likely.
- Priority: **Medium**, and arguably High on impact alone. Under Reading A the original defect is
  not fixed at all: the volume-gated License-Key prompt stays suppressed on exactly the numbers that
  motivated the report. It is filed Medium because the ambiguity is one sentence, the correction is
  small, and a careful guide reading "take the measurement" alongside "the recorded figure was
  withdrawn" will probably persist — but "probably" is what the fix was supposed to remove.
- MCP re-check: **n/a (no Senzing fact).** The subject is which of this plugin's own steps may write
  one of its own state fields. No Senzing behavior, SDK surface or server claim is asserted.
  `get_capabilities` was called this session to date the run: server **1.33.0**, 2026-08-28.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `specs/license-record-limit-has-a-detected-only-contract-nothing-enforces.md` (the
  fix this completes — implemented `999bcdd`, same day);
  `specs/inv244-absent-license-branch-exists-in-module-4-too.md` and
  `specs/license-limit-assumed-when-it-could-be-measured.md` (the INV-244 absence lineage whose
  reasoning the corrected sentences must preserve);
  `specs/scenario-generation-has-no-size-cap-or-load-time-warning.md` (the compounding half — the
  scenario sized against the figure this gate would have caught)
