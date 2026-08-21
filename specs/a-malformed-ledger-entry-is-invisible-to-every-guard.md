# A ledger entry whose heading is not line-anchored is invisible to every guard, so a corrupted `IMPLEMENTED.md` passes the whole suite

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

On 2026-08-21 two ledger entries were written into `specs/IMPLEMENTED.md` with **literal `\n` text
instead of newlines**, spliced into the middle of an unrelated entry's `- **Summary:**` line. The
result: two entries existing as one 4,539-character line, their `## <spec-name>` headings not at line
start, and a third, pre-existing entry cut in half around the splice point.

**The full suite passed.** 3,141 tests, exit 0. It was committed.

Nothing in the repo could see it. `tests/test_spec_ledger_invariants.py` finds entries with
`(?m)^## (\S+)$`, so a heading that is not line-anchored is not *invalid* — it is **absent**. Every
downstream check inherits that: the `Commit:`-vocabulary gate, the affected-files accounting, and the
forward-coverage check all iterate the entries the regex found, so a malformed entry is simply not
among them. The corruption was found by `list_specs.py` reporting `open: 11` immediately after two
specs had been implemented — a count comparison a human happened to make.

## Root cause

**Every ledger guard is written to validate entries, and none validates the file.** The parse is the
gate: text the regex does not match is out of scope rather than a failure. That is the correct shape
for asserting properties *of* an entry and the wrong shape for noticing that an entry is not an entry.

Three specific gaps:

1. **No check that the file is well-formed.** Nothing asserts that `IMPLEMENTED.md` contains no
   literal `\n` sequence outside a code span, that every `## ` heading starts a line, or that no line
   exceeds a plausible length. A 4,539-character line in a file whose longest legitimate line is a
   Summary paragraph is a strong signal and nothing looks for it.
2. **No cross-check between the ledger and the spec inventory.** `list_specs.py` computes
   `candidates − implemented − declined` and is the only thing that noticed. Nothing asserts that the
   heading count moves by the expected amount when entries are added, and nothing compares the
   ledger's entry count against the number of `specs/*.md` files it claims.
3. **The insertion is unguarded at the point of writing.** `implement-spec` Step 4 says to prepend an
   entry under the header and describes the format, but nothing verifies the write landed. The failing
   run's own tooling printed "2 entries prepended" from a `print` statement while the artifact was
   mangled — the shape `implement-spec`'s own Step 4 warns about for a different case (*"a tool that
   exits 0 but creates/modifies NO files did not do its job"*).

⚠️ **The immediate cause was heredoc escaping**, and that part is already mitigated: the repair used a
script anchored on the marker comment that refuses to write when the addition contains a literal
`\n` and asserts the heading count grew by exactly the number of blocks. But that script is
maintainer-side scaffolding from one session, not a guard — the next run will write the entry some
other way, and the file will accept it.

## Proposed change

1. **Add a file-integrity guard for `IMPLEMENTED.md` and `DECLINED.md`.** Assert: no literal `\n`
   two-character sequence outside a fenced block or code span; every `## ` heading begins a line; no
   line exceeds a generous ceiling (the longest legitimate Summary sets it); the file parses to the
   same heading count by two independent methods (line-anchored regex, and splitting on `\n## `).
2. **Cross-check the ledger against the inventory.** Assert that every `## <name>` in either ledger
   resolves to an existing `specs/<name>.md` — the `<spec-name>` template placeholder excepted —
   which would have caught the corruption from the other side, since the mangled headings resolve to
   nothing.
3. **Assert the arithmetic `list_specs.py` already computes.** It is the only thing that caught this;
   make it a test rather than a report a human must think to compare. `specs − implemented − declined`
   equals the open count, and no name appears in both ledgers.
4. **Verify the write at the point of writing.** `implement-spec` Step 4 should require confirming
   the entry landed — heading present at line start, count incremented — rather than trusting the
   editing tool's own report. One `grep -n '^## '` would have caught this immediately.
5. ⛔ **Do not attempt to repair a malformed ledger automatically.** The repair path is to restore the
   file from the last good commit and re-insert, which is what happened here; a guard that tried to
   fix formatting would risk rewriting history the file exists to preserve. Fail loudly and name the
   line.

## Acceptance criteria

- [ ] A guard fails on a literal `\n` sequence in `IMPLEMENTED.md` or `DECLINED.md` outside a code
      span, on a `## ` heading not at line start, and on a line exceeding the ceiling.
- [ ] A guard asserts every ledger heading resolves to an existing spec file, excepting the template
      placeholder.
- [ ] A guard asserts `list_specs.py`'s arithmetic and that no spec appears in both ledgers.
- [ ] Each is negative-controlled by reproducing the 2026-08-21 corruption shape — splicing an entry
      with literal `\n` into another entry's line — and confirming the guard fails, then reverting.
- [ ] `implement-spec` Step 4 requires verifying the entry landed at a line start before proceeding.
- [ ] No guard modifies either ledger; all fail loudly and name the offending line.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      stdlib-only tests over markdown, no `plugins/` import (INV-108).

## Affected files

- `tests/test_spec_ledger_invariants.py` — the file-integrity and inventory cross-checks, or a sibling
  file if that one is already large.
- `.claude/skills/implement-spec/SKILL.md` — Step 4's verify-the-write requirement.

## Source

- Audit: `production-readiness-audit`, 2026-08-21. The corruption and its repair are recorded in
  commit `1e6e49a`, whose message names this gap as known and unaddressed; this spec is that
  follow-up.
- Priority: **High.** The ledger is the source of truth for what is implemented, `implement-spec`
  reads it to decide what to offer, and a corrupted entry both hides completed work and can silently
  damage an unrelated entry. It passed 3,141 tests.
- MCP re-check: n/a (no Senzing fact) — the subject is the repository's own record-keeping.
- Upstream: not applicable.
- Related specs: `specs/declined-ledger-negatives-are-invisible-to-the-scanner.md`,
  `specs/the-invariant-to-enforcing-test-link-is-asserted-nowhere.md`,
  `specs/bytecode-caching-hides-a-latent-syntax-error-from-the-suite.md`
