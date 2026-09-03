# The work-commit detector sees nothing on a merge, so it passes one silently

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`_widen_past_a_work_commit` — added hours earlier by
`since-last-audit-reports-zero-when-the-audit-record-shares-the-work-commit` — decides whether
a recorded audit ref carries shipped work by asking:

```python
subprocess.run(["git", "show", "--name-only", "--format=", ref], ...)
```

⛔ **On a merge commit that command prints no file names at all**, so the detector concludes the
ref touches nothing propagated, skips the warning, and uses the ref as recorded — which is the
silent pass the whole check exists to remove.

**Verified in a throwaway repository on 2026-09-03, not inferred from documentation:** a merge
whose side branch adds `plugins/senzing-bootcamp/s.md` reports **zero** names under
`git show --name-only --format=`, while `git diff-tree --no-commit-id --name-only -r -m` on the
same commit reports both `plugins/senzing-bootcamp/s.md` and `specs/a.md`.

## Root cause

`git show` suppresses the file list for a merge by default: with no `-m`, `-c` or `--cc` it
shows the commit header and no diff, because there is no single parent to diff against. The
detector reads an empty list as "touches nothing shipped" — the same conflation between *no
answer* and *a clean answer* that the spec it was written for is about, reproduced one level
down in the fix itself.

## Reachability, measured rather than assumed

- **No recorded ref is a merge today.** All **444** distinct hashes in `specs/IMPLEMENTED.md`'s
  `Commit:` fields resolve, and **none** points at a merge commit.
- **Merges do exist in this repository** — 14 in the full history, though none on the current
  branch — so the shape is not structurally impossible, only unreached.
- An audit record is created by `git commit`, never by `git merge`, so reaching this needs an
  unusual path: a recorded hash that later names a merge, or a workflow change that merges into
  the working branch and records that hash.

⚠️ **This is why it is Low and not Medium.** It is filed rather than shrugged off because the
cost of fixing it is one argument and the failure mode is invisible: nothing distinguishes "the
detector examined a merge and found nothing" from "the detector examined a normal commit and
found nothing".

## Proposed change

1. **Ask a command that answers for a merge too:**
   `git diff-tree --no-commit-id --name-only -r -m <ref>`, de-duplicated — it reports each
   parent's diff, so a path introduced through any parent is seen. ⚠️ Keep the existing
   behavior for ordinary commits byte-identical; the point is to add the merge case, not to
   re-report the normal one differently.
2. **Extend the fixture guard** in `tests/test_since_last_audit_widens_past_a_work_commit.py`
   with a third commit shape: a merge whose side branch adds a shipped file. Assert
   `SUSPECT-REF` fires and the range widens. ⛔ **Negative-control it by reverting to
   `git show --name-only`** and confirming that assertion — and only that one — fails, since
   that is the exact regression.
3. **Say in the helper's docstring what the probe does and does not see**, so the next reader
   does not have to rediscover git's merge default.

## Acceptance criteria

- [ ] A recorded ref that is a merge carrying a propagated path is reported as `SUSPECT-REF`
      and the range widens to its first parent.
- [ ] An ordinary commit's detection is unchanged — the existing two fixture cases still pass
      with identical output.
- [ ] A merge carrying **no** propagated path is still accepted silently, so the fix does not
      turn every merge into a warning.
- [ ] The guard is negative-controlled by restoring `git show --name-only --format=`.
- [ ] Full suite green; `citations.py verify` clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      trivially: maintainer-side Python 3 stdlib plus git, run in this repo only.

## Affected files

- `.claude/skills/production-readiness-audit/conformance.py` — the probe in
  `_widen_past_a_work_commit`, and its docstring
- `tests/test_since_last_audit_widens_past_a_work_commit.py` — the merge fixture case

## Source

- Feedback: none — self-observed during `production-readiness-audit-2026-09-03d`, cycle 2 of the
  unattended loop (`Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: **n/a (no Senzing fact).** The subject is a git invocation in a maintainer-side
  scanner. Nothing here asserts anything about Senzing (INV-080).
- Upstream: not applicable
- Related specs: `specs/since-last-audit-reports-zero-when-the-audit-record-shares-the-work-commit.md`

## Deviations from this spec, and why (2026-09-03)

- ⛔ **The spec's own remedy was incomplete, and implementing it as written would have traded
  one blind spot for another.** Proposed change 1 named
  `git diff-tree --no-commit-id --name-only -r -m <ref>`. Measured across all three commit
  shapes in a throwaway repository before changing anything:

  | probe | root commit | normal | merge |
  |---|---|---|---|
  | `git show --name-only --format=` | lists | lists | **EMPTY** |
  | `diff-tree --name-only -r -m` | **EMPTY** | lists | lists |
  | `diff-tree --name-only -r -m --root` | lists | lists | lists |

  So the spec's command answers nothing for a commit with no parent. Shipped with `--root`,
  which covers all three. The table is recorded at the call site, because the next reader will
  otherwise re-derive it — and the naive fix is the one that looks obviously right.
- **A third fixture case was added beyond the two the spec asked for:** a root commit carrying
  shipped work, built as its own repository since a root commit cannot be appended to an
  existing history. Without it, the `--root` half of the fix is unguarded and the next
  simplification would silently reintroduce the gap.
- **Two negative controls, one per blind spot**, each failing exactly one test: reverting to
  `git show --name-only` fails only the merge case; dropping `--root` fails only the root case.

## My own mistakes in this cycle, recorded (2026-09-03)

- ⛔ **A patch script asserted against text I had assumed rather than read**, so it applied
  nothing and exited on the assertion — leaving the root-blind probe in place and the suite red
  until the file was actually opened. The assertion is what made it visible; a `replace()`
  without one would have reported success and changed nothing.
- ⛔ **A revert restored a copy taken BEFORE the cycle's edit**, which silently undid the
  comment and docstring along with the probe. That is the "same-size revert" hazard
  `unattended-spec-loop` names, in a different guise: the danger is not only stale bytecode but
  a `cp` whose source predates the work being controlled. Re-applied in full and verified by
  grepping for both the flag and the docstring line rather than trusting the copy.
- **A stray CJK glyph was typed into a test docstring** (`答s` for `answers`) and removed on
  reading. Harmless here, and worth noting because INV-259's encoding checks govern shipped
  text while `tests/` is unguarded for it.
