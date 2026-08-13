# A criterion proved "INV-206 appears zero times" by writing INV-206, which broke `citations.py verify`

⚠️ **Status changed the same day it was filed — read this first (2026-08-12).** INV-206 now **exists:**
it was recorded from `embedded-master-legacy-payload-example-is-not-runnable` with the maintainer's
approval, for an unrelated reason (an MCP payload example must have been executed successfully). So the
two citations below now resolve, `citations.py verify` reports **clean at 206**, and the failing test
passes — the suite is green at `1795 passed, 3 skipped`.

**That fixed the symptom and none of the defect.** What remains, and why this spec stays open:

1. Both sentences still assert *"`INV-206` appears zero times"*, which is now **doubly false** — the ID
   is defined *and* cited. A reader auditing the INV-205 work is told something demonstrably untrue
   about the file they are holding.
2. The recorded **1792 baseline is still wrong** (HEAD produced 1788), and every later spec's
   full-suite criterion is still checked against it.
3. The class is untouched: nothing stops the next "identifier X is unused" claim from citing X.

⚠️ **It was also luck.** The ID that happened to be next in sequence was claimed by the next
implemented spec within the day. Had the citation named an ID far up the sequence — one no spec would
mint for months — the suite would still be red.

⚠️ **Instance 3, committed into this very file (2026-08-12).** The sentence above originally illustrated
the point by naming a concrete high ID. `citations.py verify` immediately reported
`undefined invariant <that ID> cited in specs:1` — so the spec *documenting* this defect reproduced it,
one paragraph after describing it, while its author was actively thinking about it. Reworded to describe
the ID instead of naming one. This moves the candidate invariant below from instance 2 to **instance 3**,
and it is the strongest argument available that the class needs a mechanical guard rather than care:
care demonstrably fails here even under maximum attention.

*(This file quoted the ID enough times to need the scanner's `ignore-file` marker while INV-206 was
undefined — without it the verifier's count went from `specs:2` to `specs:8`, making this spec a worse
instance of the defect it reports. The marker was removed once the ID became real, so these citations
now count normally.)*

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`tests/test_citation_census.py::VerifyCatchesWhatCompactionBreaks::test_the_live_repo_verifies_clean`
**fails on `main`:**

```text
1 referential problem(s):
  - undefined invariant INV-206 cited in specs:2
```

The two citations are the *evidence sentences for a criterion asserting the ID was never minted* —
both written by commit `788be20`:

- `specs/inv205-covers-whether-to-ask-but-not-how.md:141` — "verified: `INV-206` appears zero times"
- `specs/IMPLEMENTED.md:58` — "verified: `INV-206` appears **zero** times"

Writing the sentence made the statement false, and made the verifier see two citations of an
invariant that does not exist. The same ledger entry records `citations.py verify` as **clean at
205** — which was true when it was run, and false the moment the entry containing the ID was saved.
The check was run *before* the artifact that broke it existed.

**Nothing noticed for one commit.** `788be20` reported "Suite 1792 passed, 3 skipped. citations.py
verify clean at 205", and both halves were accurate at the time of measurement. The next full-suite
run — this one, a session later — is where it surfaced. So the failure is not a regression from new
work; it is a latent one committed alongside the claim it contradicts.

**This exact shape is already in the ledger once.** The `harden-write-gate` entry records: *"a first
version of the report test was self-invalidating (naming INV-060/INV-097 made the test file cite
them)"*. That instance was caught during implementation; this one was not, because the self-reference
was in prose rather than in a test the run executed.

**The same entry's suite count is also wrong, and by more than the failure explains.** `788be20`
records the baseline as **"1792 passed, 3 skipped"**. Measured on a clean worktree at that exact commit
(`git worktree add … 498a0be`, pytest, 2026-08-12):

```text
1 failed, 1788 passed, 3 skipped, 1539 subtests passed
```

So `main` is **four passing tests short** of what the ledger claims, on top of carrying a failure the
ledger reports as absent. One failed test accounts for one of the four; the other three are
unexplained and worth a look, because every subsequent spec's "full suite passes (baseline 1792)"
criterion is checked against a number that was never true of the committed tree. A wrong baseline is
quietly corrosive: it makes a real regression look like an arithmetic discrepancy.

⛔ **Whatever the cause, do not "fix" this by editing the recorded number to match.** The number is
evidence of what was measured; the discrepancy is the finding. Establish why it differs first.

## Root cause

**A negative claim about an identifier was evidenced by quoting the identifier.** For any checker
that counts references, "X appears zero times" is self-refuting when written in a scanned file — and
`citations.py` scans `specs/` including `IMPLEMENTED.md`.

The deeper cause is *when* the check ran. `citations.py verify` was executed as part of the criterion
walk, then the ledger entry was written afterwards. Any claim about the repo's reference graph that is
recorded **in** the reference graph has to be re-verified after recording, and nothing in
`implement-spec` says so.

## Proposed change

1. **Reword both sentences so they assert the fact without citing the ID.** The claim worth keeping is
   that the implementation minted no new invariant — provable as "the highest invariant ID is
   unchanged at INV-205" or "no ID above INV-205 is defined or cited", neither of which names an
   undefined ID. ⛔ **The ledger is update-only, not rewrite-only:** correct the sentence in place and
   leave the rest of entry `inv205-covers-whether-to-ask-but-not-how` intact.

2. **Re-run `citations.py verify` after writing the ledger entry, not before.** Add it to
   `implement-spec`'s Step 4 as the last action: the entry is part of the corpus the verifier reads,
   so a clean result recorded before the entry exists is measuring a different repo than the one that
   ships.

3. **Consider teaching `citations.py` to ignore a negated citation** — a reference inside a phrase like
   "appears zero times" / "is unused" / "was not minted". ⚠️ **Recommended against for now:** it makes
   the scanner parse intent, and the prose fix costs one sentence. Recorded so the option is visible
   rather than re-derived.

## Acceptance criteria

- [x] `python3 .claude/skills/compact-dev-environment/citations.py verify` reports **clean** — already
      true as of 2026-08-12, incidentally, because INV-206 was defined for other reasons. The count is
      **206**, not the 205 this criterion originally predicted.
- [x] `tests/test_citation_census.py::VerifyCatchesWhatCompactionBreaks::test_the_live_repo_verifies_clean`
      passes — same incidental cause. ⚠️ **Neither tick means this spec is done:** both were satisfied by
      the ID becoming real, not by fixing the sentences that cite it. Do not close on these two.
- [ ] Neither reworded sentence names an undefined invariant ID; both still assert that no new ID was
      minted. Verified by opening both files.
- [ ] The rest of the `inv205-covers-whether-to-ask-but-not-how` ledger entry and spec is byte-identical
      apart from the reworded sentence — verified by `git diff -U0`.
- [ ] `implement-spec`'s Step 4 states that `citations.py verify` runs **after** the ledger entry is
      written, with the reason.
- [ ] Full suite passes. Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108).

## Affected files

- `specs/inv205-covers-whether-to-ask-but-not-how.md` — one sentence.
- `specs/IMPLEMENTED.md` — one sentence inside an existing entry.
- `.claude/skills/implement-spec/SKILL.md` — Step 4 ordering note.

## Source

- Found during `/implement-spec embedded-master-legacy-payload-example-is-not-runnable`, 2026-08-12,
  by the full-suite run that spec's acceptance criteria require. Confirmed pre-existing rather than
  caused by that work: both `INV-206` mentions are present at `HEAD` (`git show HEAD:…`), and neither
  of the two specs written that session mentions the ID.
- **No Senzing fact involved** — this is entirely about the repo's own reference graph, so no MCP
  re-check applies.
- Priority: **Medium-high.** Low effort, but it is a **red suite on `main`**, which suppresses the
  signal every other guard in the repo exists to give. It also blocks the "full suite passes"
  criterion of any spec implemented until it is fixed.
- Related: `harden-write-gate` (the prior self-invalidating-verification instance, caught in flight),
  INV-108 (offline suite), and the ledger discipline in `implement-spec` Step 4.

## Invariants introduced

**One candidate, at instance 3, deliberately not registered.** The rule would be: *a claim about the
repo's own reference graph MUST be verified after it is recorded, never before* — or more narrowly,
*evidence for "identifier X is unused" MUST NOT quote X*. Instance 1 is the `harden-write-gate`
report test (caught in flight); instance 2 is the INV-205 criterion this spec reports (shipped);
instance 3 is this spec's own illustrative sentence, caught by the verifier seconds after it was
written. Recorded as a stop-marker following the threshold discipline `senz7221` set, for the
maintainer to decide rather than assumed by this spec — though instance 3 argues the decision is
overdue, since it shows the failure surviving an author who had the defect fully in mind.

⚠️ **A mechanical guard is cheap, and worth proposing alongside it.** `citations.py verify` already
detects the condition — it caught all three instances. What is missing is only that it runs at the
**end** of `implement-spec` Step 4 rather than mid-walk, which is Proposed change 2 above.
