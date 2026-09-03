# The audit skill's own reading step returns the oldest entries

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`production-readiness-audit`'s Step 1.2 tells the auditor to read *"the newest five or so"*
audit entries, and gives the command to get them. The command returns the **oldest eight**.

`specs/IMPLEMENTED.md` is newest-first — its own header says *"Entries are newest first"* —
so `tail` takes the bottom of the file, which is the oldest end.

## Root cause

`.claude/skills/production-readiness-audit/SKILL.md`, Step 1.2:

```bash
grep -n '^## \(production-readiness-audit\|deep-dive-audit\)' specs/IMPLEMENTED.md | tail -8
```

Run on 2026-09-02 this returned `production-readiness-audit-2026-08-11` and seven
`deep-dive-audit-*` entries from 2026-07-26 to 2026-07-30 — the seven oldest in the file.
The newest (`2026-09-01e`, and four others from the same day) are at lines 88–254 and never
appear. `head -8` returns them.

⚠️ **The skill's own prose is the argument against its command.** Two paragraphs below it:

> **The newest entry matters most after an unattended run** … On 2026-08-17 the newest entry
> recorded a reverse-contract defect produced *specifically* by an unattended implement run
> and added the `implement-spec` guardrail a later run is supposed to follow. **A reading
> list fixed at the oldest six routed around exactly that.**

The command produces the failure the paragraph describes, by a different mechanism.

⚠️ **Also stale by the same measure:** the "Why this exists" section says *"The six prior
audits"* and quotes green-suite counts up to 1059 tests. There are **55** entries across the
two series today, and the suite is at 3,989. The skill elsewhere forbids exactly this — *"Do
not enumerate those entries here, and do not state how many there are"* — and then does it
two sections earlier.

## Proposed change

1. `tail -8` → `head -8` in Step 1.2, with a one-line note that the ledger is newest-first
   so the direction is not re-broken.
2. Replace *"The six prior audits"* and its fixed counts with the same
   read-it-off-the-run treatment the file already applies to `conformance.py` figures. Keep
   the three worked examples — they are the rationale, and the skill forbids cutting
   rationale for brevity.

## Acceptance criteria

- [ ] Step 1.2's command returns the newest entries.
- [ ] No sentence in the skill states how many audit entries exist or fixes a suite count.
- [ ] The three named example defects survive — they are why the section exists.
- [ ] A guard asserts the reading command is not `tail` against a newest-first ledger.
      ⚠️ Decide whether this warrants a test: `.claude/` does not ship, and the repo does
      guard other maintainer-side files, so precedent exists either way.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/production-readiness-audit/SKILL.md`

## Source

- Feedback: none — found by `production-readiness-audit` on 2026-09-02, on its own Step 1
  (`Source: self-observed (assistant retrospective)`). The run noticed because the returned
  entries were dated July while the previous audit was known to be 2026-09-01.
- Priority: Medium — it routes every future run away from the entry the skill says matters
  most, and it does so silently: the output is a plausible list of real audit entries.
- MCP re-check: n/a (no Senzing fact) — a maintainer-side skill's own instructions.
- Upstream: not applicable.
- Related specs: none.
