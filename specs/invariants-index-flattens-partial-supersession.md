# The invariants index tells readers to skip five rules that are still binding, and its counts drift on every append

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`specs/INVARIANTS.md`'s `### Index by subject` is described as the way to find the rules on
a subject: *"this index, not the ordering, is how you find the rules on a subject"*
(`:240`). It separates superseded rules per group under the label
**"*Superseded — skip these; each names its replacement:*"**, and states the reason
plainly (`:245-247`):

> 22 of the 142 development rules are **superseded** — listed separately per group so a
> reader looking for what applies never reads a retired rule by accident.

Two defects, coupled because fixing the first changes what the second counts.

**(1) Three of the thirteen listed IDs are only *partly* superseded, and each says so in
its own text.** A reader who obeys "skip these" skips live, unreplaced requirements:

| ID | What is actually superseded | What is still the only statement of it | Cited by live invariants |
|---|---|---|---|
| INV-079 | its recap-heading clause only, by INV-085 | the `MODULE: [NAME IN CAPS]` banner, the transition-question form, the `✅ Module complete` line | INV-028, INV-085, INV-140 |
| INV-086 | its recording-location framing only, by INV-087 | the first-class-module / full-apparatus / not-apparatus-exempt guarantee | INV-087 |
| INV-137 | its **trigger** only, by INV-138 | the pinned switch question, gate-after-yes-only, the absence of any `model_guidance` preference | INV-133, INV-138, INV-139 |

INV-138 states it outright: *"Supersedes INV-137's trigger only. Every other part of
INV-137 is unchanged and still binding."* INV-087 says INV-086's guarantee *"otherwise
stands."* INV-079's own note supersedes exactly one clause. The index flattens all three
to fully-retired.

Two more are worse than partial — they were **restored**. INV-063 and INV-119/INV-137
form a chain that ends with INV-063's behaviour reinstated, and INV-063's own note says
so: *"so the behavior described here is once again the behavior, with no preference
gating it."* INV-069's note likewise records INV-137 restoring its gate unconditionally.
Both are on the skip list, and INV-098 and INV-114 cite both as live authority — INV-114
calls it "the INV-063 nudge".

Repo-wide these five are cited in **24 files** (INV-079), **16** (INV-086) and **14**
(INV-137), so the skip instruction contradicts how the rest of the repo actually uses them.

**(2) Both numbers in that sentence are wrong, and one of them is wrong by construction.**

- **"142 development rules"** was **correct when written** on 2026-07-30, when the highest
  ID was INV-192 (INV-051–192 = 142). INV-193 and INV-194 were appended on 2026-07-31 and
  the count was not touched, so it is now **144**. This is not an oversight — rule 3 of
  "Maintaining this file" requires a new ID be added to its index group **in the same
  edit**, and `tests/test_invariants_index.py` enforces that for the *ID list*. Nothing
  couples the *prose count* to an append, so it drifts silently every time. It drifted
  twice on the day this was found.
- **"22 … are superseded"** is a correct total for the **whole file** wrongly attributed
  to the development-rules subset. The index lists **13**; the other 9 are the superseded
  invariants inside INV-001–050 (INV-013, 019, 020, 021, 024, 025, 026, 028, 038) — the
  block the two sentences immediately above (`:242-243`) explicitly exclude from
  "development rules". 13 + 9 = 22. The sentence conflates the two categories it has just
  separated.

## Root cause

`specs/topical-index-for-the-invariants.md` (implemented 2026-07-30) built the index with a
**binary** model: an invariant is either live or superseded. That model has no way to
express the file's actual and common case — an invariant one clause of which was replaced
while the rest stays binding — so the three partial cases were sorted into the only
non-live bucket available, and the "skip these" label was written for the fully-retired
case it was designed around.

The count is a separate cause: it is hand-written prose sitting beside a machine-checked
list. `tests/test_invariants_index.py` asserts every ID appears in exactly one group, which
is why the *list* has stayed correct while the *sentence about the list* has not.

Neither defect is reachable by any existing check: `citations.py verify` confirms every
`INV-NNN` resolves, not that a classification is right, and no test reads the header prose.

## Proposed change

1. **Add a third state to the index: partially superseded.** Give each group (where it
   applies) a distinct sublist — e.g. *"Partially superseded — still binding except as
   noted; read the invariant:"* — and move INV-079, INV-086 and INV-137 into it. The label
   MUST NOT say "skip".
2. **Move INV-063 and INV-069 out of the superseded sublist.** Their behaviour was
   restored by INV-137 and they are cited as live by INV-098 and INV-114. Either list them
   as live with a note pointing at the chain, or place them in the partially-superseded
   sublist — but they must not carry a "skip" instruction.
3. **Make the counts derivable or remove them.** Preferred: replace the two literals with
   prose that does not carry a number ("the superseded rules are listed separately per
   group so …"), because a hand-maintained count beside an append-only file is guaranteed
   to drift. If the maintainer wants the figures kept, they MUST be asserted by
   `tests/test_invariants_index.py` against the file itself so the next append fails the
   suite rather than silently invalidating the sentence.
4. **If a count is kept, state which population it counts.** "N invariants file-wide are
   superseded, M of them development rules" — never one number attributed to the subset.

⚠️ **This is an index/navigation fix, not an invariant edit.** No invariant's meaning
changes; the classification is corrected to match what the invariants already say about
themselves. Rule 1 (never delete or renumber) and rule 2 (in-place edits only clarify) are
untouched — nothing here edits an invariant's statement.

## Acceptance criteria

- [ ] The index distinguishes **fully superseded** from **partially superseded**, and only
      the fully-superseded label instructs the reader to skip.
- [ ] INV-079, INV-086 and INV-137 are classified as partially superseded, each with a
      one-line note naming which clause was replaced and by what.
- [ ] INV-063 and INV-069 no longer carry a skip instruction, and their entry reflects that
      INV-137 restored the behaviour they describe.
- [ ] No invariant statement is edited, deleted, or renumbered — only index metadata changes.
- [ ] Either the two counts are gone, or `tests/test_invariants_index.py` asserts both
      against the live file and fails when an append invalidates them. A count that is kept
      names the population it counts.
- [ ] `tests/test_invariants_index.py` still asserts every development-rule ID appears in
      exactly one group, with the new sublist included in that accounting.
- [ ] A test asserts that an ID listed as fully superseded does **not** appear as a live
      authority in another invariant's text — the mechanical form of defect (1), which is
      what let three partial cases be mislabelled.
- [ ] `python3 .claude/skills/compact-dev-environment/citations.py verify` stays clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — `### Index by subject` (`:236-278`): the header sentence
  (`:245-247`) and the four `*Superseded …:*` sublists (`:261`, `:264`, `:267`, `:270`).
- `tests/test_invariants_index.py` — the new sublist in the exactly-one-group accounting,
  the live-authority cross-check, and the count assertions if counts are kept.

## Source

- **Found by:** maintainer question — *"Are there any invariants in @specs/INVARIANTS.md
  that conflict with each other?"* — 2026-07-31, answered by reading all 194 and verifying
  the index's bookkeeping mechanically.
- Priority: **High** for defect (1) — the index actively instructs skipping binding rules,
  and it is the file's own stated entry point. Medium for defect (2).
- MCP re-check: **n/a (no Senzing fact).** This is internal consistency of the plugin's own
  ruleset; nothing here asserts anything about Senzing, so no MCP tool was called and none
  governs.
- Upstream: not applicable.
- Related specs: `specs/topical-index-for-the-invariants.md` (built the index and the binary
  model this corrects — its nine acceptance criteria all held; the gap is that none of them
  covered partial supersession).
