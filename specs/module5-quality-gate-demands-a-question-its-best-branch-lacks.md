# Module 5's quality gate orders "exactly one 👉" and its ≥80% branch supplies none

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`phase1-quality-assessment.md:507-527`, "Quality gate: iterate vs. proceed", opens with an
instruction and closes with a matching one:

> After presenting the quality assessment, guide the user's decision. **Ask exactly one 👉 question
> to close the turn:**
>
> - **Quality ≥80%:** "Your data quality is strong. Let's continue to mapping."
> - **Quality 70-79%:** … 👉 **… What would you like to do? Reply with a number:** 1. / 2.
> - **Quality <70%:** … 👉 **… What would you like to do? Reply with a number:** 1. / 2.
>
> *(Internal: end the turn on the applicable question and wait.)*

**The ≥80% branch contains no 👉 question.** It is a statement. So a guide reaching that branch is
told to ask exactly one question, told to end the turn on "the applicable question", and given no
applicable question to end on.

**This is the good-data branch — the common one.** A CORD source is curated; the walk that found
this measured `PPP_LOANS` at 100% completeness across all 3,488 records with zero duplicate
`(DATA_SOURCE, RECORD_ID)` pairs. Every Bootcamper whose data is fine lands here.

**Both ways out are violations.** A guide following the header literally **invents** a question,
which breaches INV-056 (every gate question's wording is pinned verbatim, precisely so it cannot
drift at runtime) and adds the pointless ask INV-012 forbids. A guide following the branch ends its
turn on a statement, which contradicts the section's own instruction and the ground rule that a turn
stops on its single 👉.

The plugin is almost certainly *right* that no question is needed — strong data should flow into
mapping without a gate. The defect is that the surrounding instruction says the opposite, so the
correct behaviour looks like disobedience.

**Why this class matters beyond the instance.** An instruction that cannot be followed teaches the
model that the surrounding instructions are advisory. This section is dense with genuinely binding
⛔ rules — the label-must-match-the-band rule sits 80 lines above it — and they rely on being read
as literal.

**No Senzing fact is involved.** Internal consistency only.

## Root cause

**The header was written for the two branches that gate, and the pass-through branch was added or
kept without re-reading it.**

The 70–79% and <70% branches are the ones the section is *about* — its title is "iterate vs.
proceed", and both carry a pinned two-option question. The ≥80% case is not a decision at all; it is
the absence of one. It was written as a one-line reassurance, and the "ask exactly one 👉" header —
correct for the two branches beneath it — was never scoped to them.

Nothing catches it because no test reads a section header against the branches it governs, and a
prose reader skims three parallel bullets and sees three branches of one rule. It surfaces only when
you are *in* the ≥80% branch and have to decide what to actually say, which is what a walk does and
a read does not.

## Proposed change

1. **Scope the header to the branches that gate.** Something of the form: *"Where the score gates
   (70–79% and below 70%), ask exactly one 👉 question to close the turn. At ≥80% there is no
   decision to make — state the result and continue to Phase 2 in the same turn."*

2. **Say explicitly what the ≥80% branch does next**, so "no question" does not read as "turn ends
   here": it continues into Phase 2's first step, which supplies that turn's single 👉.

3. **Adjust the closing internal note** — *"end the turn on the applicable question"* — to cover the
   branch where none applies.

⛔ **Do not add a 👉 question to the ≥80% branch to satisfy the header.** That would trade a wording
defect for a real one: a "your data is fine, shall we continue?" gate is exactly the pointless
question INV-012 forbids, and INV-006 counts it against the ask-once budget. The fix is to correct
the instruction, not to manufacture the question it implies.

## Acceptance criteria

- [ ] The gate's header scopes "exactly one 👉" to the 70–79% and <70% branches. Verified by opening
      the file.
- [ ] The ≥80% branch states what happens next (continue into Phase 2 in the same turn) rather than
      leaving the turn's end undefined.
- [ ] The closing internal note accounts for the no-question branch.
- [ ] **No 👉 question is added to the ≥80% branch** — verified by `git diff` showing no new 👉 in
      that bullet.
- [ ] The two pinned gate questions at 70–79% and <70% are **unchanged**, character for character
      (INV-056). Verified by `git diff`.
- [ ] A test asserts the ≥80% branch carries no 👉 **and** that the header does not demand one
      unconditionally. **Not vacuous:** it names the file and the section it parsed, and fails if the
      section heading is renamed.
- [ ] **Negative-controlled, mutation verified to land:** adding a 👉 to the ≥80% branch fails the
      test; restoring the unconditional header wording fails it. Revert both.
- [ ] Full suite passes (baseline **1756 passed, 3 skipped**). Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108); cross-platform and language-agnostic.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`
- `tests/` — one new guard.

## Source

- Dry run, **phase 3 (conversational walk)**, 2026-08-12, maintainer answering as the Bootcamper.
  Found on arrival at the gate with a real source scoring in the ≥80% band — the branch with no
  question — after completing Steps 1–6 against `data/raw/PPP_LOANS.jsonl` (3,488 records, fetched
  and count-verified per INV-203).
- This is the **unsatisfiable-instruction class** `dry-run/phase3-conversational.md` names as unique
  to this phase: *"instructions the guide is told it must follow and provably cannot"*. The prior
  instance was `ground-rules.md`'s acknowledgment rule against a bare "no", which now carries an
  explicit carve-out (`ground-rules.md:60-65`) — the same remedy shape this spec proposes.
- Priority: **Medium-low.** No data is harmed and the sensible reading is obvious to a careful
  guide. It costs a fabricated question on the happy path, and it erodes the literalness the
  surrounding ⛔ rules depend on.
- MCP re-check: **n/a — no Senzing fact.** Server **1.32.9** this session; no tool was called for
  this finding.
- Related: INV-056 (pinned gate wording), INV-012 and INV-006 (the question that must not be
  invented), INV-005 (one 👉 per turn).

## Invariants introduced

**None proposed.** INV-005, INV-006, INV-012 and INV-056 already govern; this is one section's
header contradicting one of its own branches. The general rule — *a branch-selecting instruction
must hold for every branch beneath it* — is a real pattern but has one recorded instance besides
this, so it is noted here rather than proposed.

## Deviations from this spec, and why (2026-08-12)

**Two defects in my own guard, both caught by running the mutation rather than by reading it.**

1. **The scope assertion searched the whole gate section**, so restoring the unconditional header
   ("Ask exactly one 👉 question to close the turn.") **passed** — because the closing internal
   note, several paragraphs below, happens to contain "gating branches" too. Fixed by splitting the
   section into sentences and asserting the scope sits on **every sentence that carries the
   instruction**, which is where the claim is actually made. This is the third instance today of the
   same shape: a guard asserting a token appears *somewhere* rather than that the claim holds *where
   it matters*.
2. **A `%`-formatting bug in the failure message.** The message contained "≥80% branch", which
   Python read as a format specifier and raised `ValueError: unsupported format character 'b'` —
   turning the test into an ERROR on the correct tree as well as the mutated one. Escaped to `%%`.

**No other deviation.** The two pinned gate questions (70-79% and <70%) are unchanged, verified by a
`git diff` showing no removed 👉 line other than the header sentence this spec rescopes, and pinned
by their own assertion. No 👉 was added to the ≥80% branch — asserted, and mutation-verified.
