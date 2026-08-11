# INV-050's layout tree enumerates three artifacts the plugin never creates

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-050 states: *"The generated Bootcamp project MUST follow this layout"*, followed by a `text`
tree of 53 entries. Three of the 23 **files** in that tree are named **nowhere else in the
repository** — not in any skill, script, test, doc, or spec:

| Entry | Tree comment | Producer | Reader | Test |
|---|---|---|---|---|
| `config/session_log.jsonl` | "Session activity log" | none | none | none |
| `config/visualization_tracker.json` | "Visualization run tracking" | none | none | none |
| `docs/completion_summary.md` | — | none | none | none |

Verified 2026-08-11 by extracting the tree's leaf entries and grepping the whole repo:
`grep -rl "<name>" plugins/ docs/ tests/ README.md` returns **zero files** for each, outside
`specs/INVARIANTS.md` itself. Every other file in the tree resolves to at least one producing or
consuming site.

**This is a MUST that the plugin does not satisfy.** A Bootcamper's generated project will never
contain these three, so INV-050 is false as written on every run that has ever happened.

**Why it is invisible.** The tree still reads authoritative — it is a fenced block inside a
foundational invariant, and nothing walks it. `tests/test_bundled_script_and_production_paths.py`
checks directories that *are* used; no test enumerates the tree and asserts each entry is reachable.
This is the stale-enumeration class the audit skill ranks fourth: *"one listing members breaks the
moment a member moves, and it breaks silently because the list still reads authoritative."*

**The tree already demonstrates the correct handling**, which is what makes the omission a defect
rather than a design choice: `bootcamp_journal.md` carries the inline annotation *"superseded by the
consolidated `bootcamp_recap.md`, INV-085"*. Entries that stopped being produced are supposed to say
so. These three say nothing.

**No Senzing fact is involved** — this is entirely internal consistency, and no MCP tool was called
for it.

## Root cause

The tree descends from the Kiro-derived project layout that predates most of the modules. Three
entries were designed and never built, and nothing since has walked the list against what ships. The
supersession annotation on `bootcamp_journal.md` shows the tree *is* maintained when a file is
consciously retired — the failure mode here is a file that was never created in the first place, so
there was no moment at which anyone was prompted to annotate it.

## Proposed change

**This is the maintainer's call between two valid readings**, and the spec deliberately does not
choose:

- **(a) The invariant is stale** → annotate the three entries in place with a dated note
  (`# not produced as of 2026-08-11 — never implemented`), in the same idiom
  `bootcamp_journal.md` already uses. INVARIANTS.md rule 2 permits clarifying wording in place; this
  records a fact about the tree rather than changing what the tree requires.
- **(b) The plugin is incomplete** → the three artifacts should exist, and this is a gap in Modules
  3b/7 and graduation. That is a much larger change and needs its own specs.

⛔ **Do not delete the entries.** INV-050 is cited widely and the tree is quoted in audits; silently
shortening it loses the record that these were once intended.

**Either way, add the guard.** A test must walk INV-050's tree and assert every leaf entry is
either (i) referenced somewhere in `plugins/`, or (ii) carries an inline annotation explaining why
it is not. That is the check whose absence let this sit: it fails on a *new* unproduced entry and on
an entry that quietly loses its producer, and it passes on a consciously-retired one.

## Acceptance criteria

- [ ] Each of `session_log.jsonl`, `visualization_tracker.json` and `completion_summary.md` is
      either produced by a named step, or annotated in the tree with a dated reason it is not.
- [ ] INV-050 is **not** shortened, renumbered, or stripped of any entry.
- [ ] A test walks the INV-050 tree, extracts its leaf file entries, and asserts each is either
      referenced under `plugins/` or annotated — with a not-vacuous guard asserting the extraction
      found the expected number of entries (23 files as at 2026-08-11), so a parser drift cannot
      make it pass silently.
- [ ] The test is negative-controlled: adding a fictional unannotated entry to the tree fails it.
- [ ] Stdlib-only, no `plugins/` import (INV-108); holds on Linux, macOS and Windows.

## Affected files

- `specs/INVARIANTS.md` — INV-050's tree (annotation only, under reading (a)).
- `tests/` — the new tree-walk guard.
- Under reading (b): the modules that would produce the three artifacts.

## Source

- Audit: `production-readiness-audit`, 2026-08-11. Step 2 (enumeration sweep) and Step 5
  (completeness: every enumerated thing exists).
- Suite was green at the time of the finding: 1587 passed, 3 skipped, 1253 subtests.
- Priority: **Medium.** Nothing a Bootcamper does breaks, and no artifact they receive is wrong —
  but a foundational invariant states a MUST the product has never satisfied, which devalues the
  tree as a specification and would mislead anyone implementing against it.
- MCP re-check: **n/a — no Senzing fact.** Internal consistency only; no tool called.

## Deviations from this spec, and why (2026-08-11)

⛔ **THIS SPEC IS WRONG AND MUST NOT BE IMPLEMENTED.** Its central factual claim is false, and the
error is in the spec, not in the plugin.

**What the spec claims:** the three entries "say nothing", in contrast to `bootcamp_journal.md`
which carries a supersession annotation.

**What `specs/INVARIANTS.md` actually contains** (lines 166, 167, 197):

```text
  │   ├── session_log.jsonl              # Session activity log (reserved)
  │   └── visualization_tracker.json     # Visualization run tracking (reserved)
  │   ├── completion_summary.md          # (reserved)
```

All three are annotated `(reserved)`. The annotation was added deliberately on **2026-07-17** by
the maintainer via `specs/layout-tree-reconciliation.md` (commit `cc46a55`), whose ledger entry
records it in as many words: *"annotated the reserved/unused entries (`config/session_log.jsonl`,
`config/visualization_tracker.json`, `data/backups/`, `docs/completion_summary.md`, `src/server/`,
`monitoring/`, `tests/`)"*. That spec had already found and settled exactly this question.

**How the audit got it wrong.** The extraction ran `body = line.split("#")[0]` before matching —
discarding the comment column, which is the only place the annotation lives. It then asked "is this
filename mentioned anywhere else in the repo?", got no, and concluded the tree was stale. The
evidence that refutes the finding sat in the part the scan deleted. The `production-readiness-audit`
skill warns that its own lead generators "are lead generators, not verdicts"; this run wrote its own
scan and then treated it as a verdict, which is the same failure with an extra step.

**The correct check, run 2026-08-11**, keeps the comment and accepts an entry as accounted for if it
is either referenced under `plugins/` **or** annotated as reserved/superseded/future. It returns
**zero unaccounted entries** — the INV-050 tree is fully consistent with what ships.

**What survives.** Nothing in the Problem or Proposed change. One idea from the acceptance criteria
is independently worth building and is NOT justified by this spec: a tree-walk guard asserting every
INV-050 leaf entry is either referenced or annotated. Its value is not the defect this spec claims —
there is none — but that it would fail on a *future* unannotated entry, and it would have caught
this error in seconds. If wanted, it needs its own spec with an honest premise.

**Disposition:** do not implement. A spec whose facts are wrong is `feedback-to-specs` business —
the remedy is a corrected or superseding spec, not a `DECLINED.md` entry (which records a decision
not to build something correct).
