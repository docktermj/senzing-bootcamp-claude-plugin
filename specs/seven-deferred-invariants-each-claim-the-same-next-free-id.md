# Seven pending deferred invariants each name 285 as "the next free id"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`specs/IMPLEMENTED.md` carries **8** `DEFERRED INVARIANT — awaiting the maintainer's sign-off`
blocks. **Seven** of them contain the same parenthetical:

> **INV-NNN** — *(next free id: 285; written as NNN deliberately, because a literal id here would
> read as a citation of an invariant that does not exist and turn `citations.py verify` red)*

The highest id defined in `INVARIANTS.md` today is **284**, so 285 is correct — **for the first one
minted, and for no other.** A maintainer working through the queue mints 285 for whichever block
they sign off first; the remaining six then carry a parenthetical that is wrong, while reading
exactly as authoritative as it did when it was right.

The instruction beside it is fine and self-correcting — *"mint it at the next free id"* stays true
however many have been minted. It is the **number** that cannot survive the queue being worked.

## Root cause

The parenthetical was written once, correctly, and then copied into each new deferral as the
convention spread. Each copy was accurate **on the day it was written**, because no id had been
minted in between — which is exactly what makes this hard to notice: every block is individually
defensible, and only the set is wrong.

⚠️ This is the **stale-enumeration** class (`production-readiness-audit` Step 2, defect class 4)
applied to a figure rather than a list: *"An invariant stating a property survives change; one
listing members breaks the moment a member moves, and it breaks silently because the list still
reads authoritative."* A literal id in a queue of pending mints is a member reference.

## Proposed change

1. Replace the number with the **property** in each pending block — the thing that stays true:

   > **INV-NNN** — *(written as NNN deliberately: a literal id here would cite an invariant that
   > does not exist and turn `citations.py verify` red. Mint at the next free id — read it off
   > `INVARIANTS.md`, do not trust a number written here, as several deferrals are pending and only
   > the first minted gets the id any of them names.)*

2. ⚠️ **Do not renumber, delete or rewrite the substance of any deferral.** These are drafts
   awaiting the maintainer's sign-off; only the parenthetical changes, and its meaning is
   preserved.

3. Add a guard asserting that no `DEFERRED INVARIANT` block states a **literal next-free id**,
   since the failure is silent and the blocks are added one at a time by different runs.

## Acceptance criteria

- [ ] No pending `DEFERRED INVARIANT` block names a specific next-free id as a number.
- [ ] Every block still explains why the id is written as `NNN` — that reason is real and must not
      be lost (a literal id turns `citations.py verify` red).
- [ ] The drafted wording of every deferral is otherwise byte-unchanged.
- [ ] A repo-level test fails when a deferral block names a literal next-free id.
      Negative-controlled: reintroduce one, confirm it fails, revert.
- [ ] Resolved deferrals (`DEFERRED INVARIANT (resolved INV-NNN, …)`) are untouched — they are
      historical records of what the draft said.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/IMPLEMENTED.md` — the seven pending blocks carrying `next free id: 285`.
- `tests/test_spec_ledger_invariants.py` or a new guard — the literal-id check.

## Source

- Feedback: none — found by `production-readiness-audit` on 2026-09-01, counting the deferrals an
  unattended run had accumulated (`Source: self-observed (assistant retrospective)`).
- Priority: Low — nothing shipped is wrong and the operative instruction is correct; the hazard is
  that six of seven hints become wrong the moment the queue is worked, and they read as verified.
- MCP re-check: n/a (no Senzing fact).
- Upstream: not applicable
- Related specs: none — but every spec whose ledger entry carries a pending deferral is affected by
  the wording change.
