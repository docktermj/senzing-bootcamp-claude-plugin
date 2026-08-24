# `conformance.py all` omits both new views while Step 1 calls it "every lead generator", and `since --ref` names a ref no run can compute

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`conformance.py` gained `per-rule` and `since` on 2026-08-21 because the section-scoped `rules`
count cannot see a new hard rule that lands beside an unrelated citation. Three places now tell a
run to use them — the bidirectional-invariant-contract section, the audit's Step 3, and
`implement-spec`'s Step 5. **Neither view is reachable from the path that actually prescribes the
generators.**

**1. `all` does not include them, and Step 1.3 calls `all` "every lead generator".**

```text
$ conformance.py all
== hard rules whose section cites no invariant
== invariants that enumerate (stale-risk surface)
== shipped markdown: 44 files, 165,436 words
== passages of 14+ words appearing in more than one shipped file
```

`per-rule` and `since` are absent. So a run that follows Step 1.3 literally — *"Run every lead
generator"* — gets exactly the one view that is documented, in the same file, as unable to see the
class. It reaches the other two only if it reads Step 3 before acting on Step 1, which is the
reverse of the order the steps are numbered in.

⚠️ **This is the fixed defect reappearing one layer out.** The 2026-08-21 finding was that a run
watched a count that could not answer the question it was being used for. The remedy added views
that answer it and left the prescribed command pointing at the old one.

**2. `since --ref` names a ref nobody can compute.** Both call sites pass a placeholder:

- audit Step 1: `since --ref <last audit>`
- `implement-spec` Step 5: `since --ref <this run's base>`

Neither says how to obtain it, and neither value is mechanically available to a run. The session
that wrote these instructions had to reverse-engineer its own base with
`git log --since="2026-08-20 23:00" --reverse | head -1`, a timestamp heuristic that works only
for a run that knows when it started and breaks across a date boundary. An instruction whose
argument cannot be derived is an instruction that will be skipped or guessed.

## Root cause

**The views were built and documented, and not wired into the two mechanisms that make a
generator get run:** the aggregate command, and a default for the one required argument. Both
omissions are invisible to the suite, because the tests written for the new views invoke them
directly with explicit arguments — which is the right way to test a view's behavior and the wrong
way to notice that nothing else invokes it.

⛔ **`since` genuinely cannot be folded into `all` as-is** — it needs a ref, and guessing one would
silently report the wrong range, which is worse than not running. That is the argument for giving
it a computable default, not for leaving it out.

The ledger already holds the ref this repo wants: every audit entry is a
`## production-readiness-audit-<date>` heading with a `- **Commit:** <hash>` field, and the newest
one marks exactly the boundary both instructions are reaching for.

## Proposed change

1. **Include `per-rule` in `all`.** It takes no required argument and is the standing worklist.
   Print it after `rules` so the two counts are read together — the whole point is that they differ.
2. **Give `since` a computable default: `--since-last-audit`**, resolving the ref from the newest
   `## production-readiness-audit-*` entry's `Commit:` field in `specs/IMPLEMENTED.md`. Then both
   call sites name a flag rather than a placeholder. ⛔ If the field is missing, `uncommitted`, or
   unresolvable as a git ref, **fail loudly and name what it read** — never fall back to a guess
   (INV-110/INV-115).
3. **Have `all` state that `since` was not run and how to run it**, rather than silently omitting
   it. An aggregate that quietly covers three of four views is the same shape as the count that
   quietly covered one population of two.
4. **Fix both call sites** to pass the flag, and fix Step 1.3's wording so "every lead generator"
   is either true or replaced by naming what `all` covers.
5. **Add a test that `all` runs every argument-free view**, derived by enumerating the script's
   subcommands rather than by listing them — a listed test would certify the views someone
   remembered, which is the defect being fixed (INV-246).

## Acceptance criteria

- [ ] `conformance.py all` output includes the per-rule view's section.
- [ ] A test derives the set of argument-free subcommands from the script's own parser and asserts
      `all` runs each — negative-controlled by removing one from `all` and confirming failure.
- [ ] `conformance.py since --since-last-audit` resolves the ref from the newest audit entry's
      `Commit:` field and reports the range it used.
- [ ] An unresolvable or `uncommitted` ref exits non-zero naming what it read, never zero with an
      empty result.
- [ ] The audit's Step 1 and Step 3, and `implement-spec`'s Step 5, pass the flag instead of a
      placeholder.
- [ ] `all` names `since` as not run and how to run it.
- [ ] Step 1.3's "every lead generator" is accurate for what it prescribes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      `conformance.py` is stdlib-only maintainer tooling under `.claude/`, which `propagate.sh`
      does not ship. Ref resolution uses `git` through `subprocess`, already required by `since`.

## Affected files

- `.claude/skills/production-readiness-audit/conformance.py` — `all`, and `since`'s default ref.
- `.claude/skills/production-readiness-audit/SKILL.md` — Step 1.3 and Step 3.
- `.claude/skills/implement-spec/SKILL.md` — Step 5.
- `tests/` — the all-covers-every-view test and the ref-resolution coverage.

## Source

- Audit: `production-readiness-audit`, 2026-08-21 (iteration 2), found by running `all` and
  reading which sections it printed — against the same session's own change.
- Priority: **High.** The views exist to stop an unattended run shipping an unregistered
  guarantee, and the path every run is told to take does not reach them. That is the 2026-08-17 and
  2026-08-21 findings' mechanism intact, one layer out.
- MCP re-check: n/a (no Senzing fact) — maintainer tooling and the repository's own ledger.
- Upstream: not applicable.
- Related specs: `specs/conformance-rules-cannot-see-a-new-rule-beside-an-old-citation.md` (added
  the views), `specs/the-hard-rule-detector-misses-every-rule-not-first-on-its-line.md`,
  `specs/the-audit-skills-baselines-and-required-reading-are-stale.md`
