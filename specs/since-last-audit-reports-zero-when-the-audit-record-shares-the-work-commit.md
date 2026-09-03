# `since --since-last-audit` reports zero when the audit record shares a commit with the work

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`conformance.py since --since-last-audit` resolves its range start from the newest
`## production-readiness-audit-*` ledger entry's `Commit:` field. That is right only while an
audit record is committed **before** the work the next audit must examine. When the record
shares a commit with implementations — or lands after them — the range starts *at* that commit
and the added rules fall outside it.

**Measured on 2026-09-03, in this repo:**

```text
$ conformance.py since --since-last-audit
   (ref ffa6a2f from ledger entry production-readiness-audit-2026-09-03b)
   0 hard-rule line(s) added since ffa6a2f, across 0 file(s)

$ conformance.py since --ref e5fee7c        # the commit before ffa6a2f
   6 hard-rule line(s) added since e5fee7c, across 5 file(s)
```

⛔ **The failure mode is the one the check exists to prevent.** `0 hard-rule lines added` is
indistinguishable from a run that genuinely added none, and it is the answer that lets an
implementation ship a hard rule with no invariant and no deferral — the 2026-08-17 defect that
`implement-spec`'s Step 5 and INV-282's set-difference procedure were both written for. Every
downstream check inherits it: `tests/test_new_hard_rules_are_cited_or_deferred` **skips** when
`since` reports nothing added, so the guard reports green by not running, and the
`unattended-spec-loop` set-difference script iterates over an empty list and prints nothing.

Nothing warns. The output names the ref it used, which reads like provenance rather than like
the thing to check.

## Root cause

`.claude/skills/production-readiness-audit/conformance.py`'s `--since-last-audit` resolver takes
the newest audit entry's recorded hash and uses it verbatim as the range start. It never asks
whether that commit is an **audit-record commit** — one touching only `specs/` — even though
the ledger entry beside it almost always claims exactly that (*"no shipped file modified by
this audit"*), which is a machine-checkable claim sitting one field away.

**How the condition arose here, stated plainly because it was self-inflicted:** the
`2026-09-03b` audit record was committed together with the two implementations it produced
(`ffa6a2f`), rather than on its own as `4f0b22c` had been, because both were finished in one
attended session before `/unattended-spec-loop` started. The tooling has no guard against that
ordering, and the loop's own procedure — one commit per spec, then the audit — makes the
ordering easy to get wrong in either direction.

## Proposed change

1. **Detect the contradiction and report it loudly.** When the resolved ref's commit touches any
   propagated path (`plugins/`, `.claude-plugin/`, `docs/`, `README.md`), print a ⛔ line naming
   the ref, the shipped files it touched, and the ledger entry it came from — because an
   audit-record commit that modifies shipped files contradicts what such an entry says about
   itself.
2. **Then report against the parent commit as well**, labeled as such, so the run cannot come
   away with a vacuous zero. ⚠️ **Report both, never silently substitute one for the other:** a
   resolver that quietly re-points the range is a second thing a reader has to know about, and
   an audit whose ref moved without saying so is how a wrong baseline becomes invisible again.
3. **Make the skip visible where it matters.** `tests/test_new_hard_rules_are_cited_or_deferred`
   skips on "nothing added". Have its skip message distinguish *the range was empty* from *the
   range may be wrong because its ref touches shipped files*, so a green suite cannot be read as
   "no rules were added" when the range never covered them.
4. **State the ordering rule where the loop can act on it.** The audit record should be
   committed **before** the implementations that answer it, or the next cycle must pass an
   explicit `--ref`. `.claude/` is maintainer-side, so this is a procedure note in
   `unattended-spec-loop/SKILL.md` and `production-readiness-audit/SKILL.md`, not shipped text.

## Acceptance criteria

- [ ] With the newest audit entry's ref pointing at a commit that touches shipped paths,
      `since --since-last-audit` prints a ⛔ warning naming the ref, the ledger entry and the
      shipped files, and reports the parent range as well as the recorded one.
- [ ] With a normal audit-only ref, output is unchanged — verified against a ref that touches
      only `specs/`, so the warning cannot fire on the ordinary case.
- [ ] `test_new_hard_rules_are_cited_or_deferred`'s skip message distinguishes an empty range
      from a suspect ref.
- [ ] A test asserts the detection, negative-controlled by pointing the resolver at an
      audit-only commit and confirming no warning.
- [ ] Both maintainer skills state the commit-ordering rule.
- [ ] Full suite green; `citations.py verify` clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      trivially, since this is maintainer-side Python 3 stdlib run in this repo only.

## Affected files

- `.claude/skills/production-readiness-audit/conformance.py` — the resolver's check and the
  dual report
- `tests/test_new_hard_rules_are_cited_or_deferred.py` — the skip message
- `.claude/skills/unattended-spec-loop/SKILL.md`, `.claude/skills/production-readiness-audit/SKILL.md`
  — the ordering rule
- `tests/` — one new guard

## Source

- Feedback: none — self-observed during `production-readiness-audit-2026-09-03c`, cycle 1 of the
  unattended loop (`Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: **n/a (no Senzing fact).** The subject is a maintainer-side scanner's range
  resolution. Nothing here asserts anything about Senzing (INV-080).
- Upstream: not applicable
- Related specs: `specs/the-audit-skill-reads-its-own-ledger-backwards.md`,
  `specs/a-malformed-ledger-entry-is-invisible-to-every-guard.md`,
  `specs/the-invariant-to-enforcing-test-link-is-asserted-nowhere.md`

## Deviations from this spec, and why (2026-09-03)

- **Criterion 1 asked for the parent range "as well as" the recorded one; one widened range
  ships instead**, with the ⛔ warning naming both refs. `test_new_hard_rules_are_cited_or_deferred`
  parses this view's output into the set of added rules, and two overlapping ranges give it two
  answers to reason about — the ambiguity would land in the guard whose correctness this spec
  exists to protect. The "never silently substitute" requirement is met by the warning, which
  names the recorded ref, the entry that recorded it, the propagated files it touched, and the
  ref actually used.
- **`_PROPAGATED` is pinned against `.claude/skills/propagate-to-public/propagate.sh`**, not
  `scripts/propagate.sh` — the script lives under the skill that owns it. ⚠️ The pin was first
  written to `skipTest` when the file was missing, which is what it did: it reported `1 skipped`
  and would have looked like coverage indefinitely. It now asserts the file exists. A skipped
  assertion reads like a passing one, which is the same defect shape as a zero that reads like a
  clean range.
- **Not implemented: a version guard on the fixture's git.** It calls
  `git init --initial-branch`, needing git ≥ 2.28, and the guard skips only when `git` is absent
  entirely. Left as a disclosed assumption rather than fixed, since the repo's tooling already
  assumes a modern git.
