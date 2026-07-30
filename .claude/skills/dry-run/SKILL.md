---
name: dry-run
description: 'Dry-run the Senzing Bootcamp plugin to find defects that reading it cannot: phase 1 verifies every MCP call against the live Senzing MCP server, phase 2 executes the hooks and bundled scripts against a realistic scratch project, phase 3 walks the conversational layer with the maintainer answering as the Bootcamper. Use when the maintainer wants to dry-run, smoke-test, or exercise the plugin, verify it actually works rather than reads correctly, or asks what a fresh audit should look at next. Maintainer tool — not part of the bootcamper experience.'
---

# Dry Run

This is a **maintainer** tool for developing the Senzing Bootcamp Claude Plugin
(SBCP). It is never invoked during a bootcamp.

## Why this exists

Three full audits and 399 passing tests all read the plugin. Then one dry run found
that **Module 5's mapping workflow could not execute at all** — `mapping_workflow`
requires a `workspace_dir` parameter the plugin never passed, and five of its eight
documented action names were payload field names rather than actions. The
instructions were coherent, internally consistent, well cross-referenced, and wrong
about the tool they called.

That is the defect class this skill exists for, and it has a shape:

> Static analysis can only confirm the plugin agrees **with itself**. It cannot see
> where the plugin disagrees with the world — the MCP server's real schemas, the
> filesystem, a rendered artifact, or a human being answering questions.

Each phase points at one of those. Run them in order; each is independently useful
and each has found real defects.

| Phase | Checks the plugin against | Needs |
|---|---|---|
| 1 — [MCP call contracts](phase1-mcp-contracts.md) | the live Senzing MCP server's schemas | MCP access |
| 2 — [Hooks and scripts](phase2-hooks-and-scripts.md) | a real filesystem and real artifacts | `python3` |
| 3 — [Conversational layer](phase3-conversational.md) | a human answering questions | **the maintainer** |

Phase 1 is the highest yield per minute — it targets the plugin's hard dependency
and its entire factual foundation. Start there unless the maintainer says otherwise.

## Before you start

1. **Ask which phases to run** if the maintainer did not say. Present them as a
   numbered list (1, 2, 3, or all three); do not assume. Phase 3 costs the
   maintainer's time in a way 1 and 2 do not, so it is never implied by "dry-run
   the plugin".
2. **Work outside the repo.** Phase 2 and 3 create a bootcamp project. Put it in
   `$HOME/senzing-bootcamp-dryrun` (or `-phase3`), never inside the repo and never
   under `/tmp` — a maintainer hook blocks system-temp writes, and the plugin's own
   file-placement rules assume a project directory.
3. **Note the environment's limits up front**, so the report can state them rather
   than imply coverage it did not have. Check and record: is the `senzing` Python
   package importable? is `libSz.so` present? is `fpdf2` installed? is `docker`
   available? is there a headless browser? Missing pieces are fine — silently
   skipping the paths that need them is not.
4. **Run the coverage reports to choose where to look.** Two blind spots have hidden
   real defects — an invariant no test cites, and a spec file a ledger entry never
   recorded changing. Both are reports rather than tests, because a hit in either is
   usually legitimate; they tell you where a conformance sweep is unguarded:

   ```bash
   python3 .claude/skills/dry-run/coverage_reports.py both
   ```

   `invariants` lists invariants no test mentions by ID — INV-060 and INV-097 both sat
   there while standing unimplemented for weeks. `affected` lists ledgered specs whose
   `## Affected files` predicted a path the entry's `Files changed:` never recorded —
   which is how the graduation half of INV-097 went missing. Read-only, stdlib-only, exit 0
   whatever it finds. The `auto-test` skill can call it the same way.

## Absolute rules

⛔ **Never send anything outside the machine.** Do not call `submit_feedback` under
any category. Verify its *schema* — never invoke it. A dry run must not file junk
upstream or transmit a name and email. The same goes for `download_resource` on
anything large.

⛔ **Never fabricate a Bootcamper answer.** This is what makes phase 3 impossible to
self-play: the plugin forbids simulating the Bootcamper's response, and an assistant
grading its own 👉 discipline proves nothing. If the maintainer is unavailable, say
phase 3 is untested rather than approximating it.

⛔ **Commit or copy aside before mutating the tree.** This one cost real work twice
in the session that produced this skill. `git restore` cannot tell your fix from a
defect you injected to test a guard — it reverts both. Either commit the fix first,
or back the file up with `cp` and restore with `mv`.

⛔ **Clear `__pycache__` after any same-size revert.** `"…"` and `"..."` are both
three bytes; a restored file with the same size and a same-second mtime lets Python
reuse bytecode compiled from the mutated source, so the suite keeps failing on
already-correct code. `find . -name __pycache__ -type d -exec rm -rf {} +`.

## What to do with a finding

A dry-run finding is only half done when the plugin is fixed. Follow this for each:

1. ⛔ **Write it into `specs/` as you find it — before fixing anything.** A finding that
   exists only in the conversation is not recorded, it is *remembered*, and it dies at
   session end or the next compaction. This is not a filing preference; it is the
   difference between a durable improvement and a good afternoon.

   - **File:** `specs/<kebab-case-title>.md`, using the shape in
     `../feedback-to-specs/spec-template.md` — Problem, Root cause, Proposed change,
     Acceptance criteria, Affected files, Source. Cite `file:line`, and date every MCP
     claim with the server version that produced it.
   - **When:** immediately for phase 3, because a walk stops on whatever turn the
     maintainer stops it; by the end of the phase at the latest for phases 1 and 2.
     Do **not** defer to the final report — the report is the last thing that happens
     and the first thing lost.
   - **Even when you fix it the same session.** The spec is what the `IMPLEMENTED.md`
     entry points at, what makes the finding legible to whoever reads it next, and what
     survives if the fix has to be reverted. Writing the spec is not made redundant by
     also fixing it.
   - **Grouping:** one spec per root cause. Several small prose corrections from one walk
     may share a spec when each is a few lines in the same file or two — give each its own
     acceptance criteria so they stay independently implementable — but two unrelated
     defects never share one.
   - **Where not to put it.** Not the session scratchpad: the maintainer's global
     `write-location-gate.py` blocks system-temp paths, so a `/tmp/...` note fails outright.
     Not repo `tmp/` either — it is not gitignored, so it becomes untracked clutter that
     "leave the repo with only intended changes" then tells you to delete. `specs/` is the
     home, and it has the additional property that `/implement-spec` lists it as
     outstanding work.

   Phase 3's collapsed test-notes blocks are *working notes* — the running observation
   channel for a walk in progress. They are never the record.

2. **Fix the class, not the instance,** where the class is cheap to remove. The
   `_clip` ellipsis defect had three call sites; changing the suffix to ASCII inside
   `_clip` made the ordering hazard unreachable instead of fixing three callers.
3. **Write a test in the repo-level `tests/`** — stdlib only, no `plugins/` (INV-108).
   A dry run you cannot repeat cheaply is a one-off; a test is the durable half.
4. ⛔ **Negative-control the test.** Reintroduce the defect, confirm the test fails,
   revert. A guard whose docstring claims more than its assertion checks is worse
   than no guard, because it certifies what it never tested. This is not optional:
   in the originating session, one existing test had **pinned the wrong premise**,
   which is how the defect it covered survived three audits.
5. **Record the outcome** in `specs/IMPLEMENTED.md`, naming the spec from step 1, and
   either register the invariant it establishes in `specs/INVARIANTS.md` or state that it
   establishes none — `tests/test_spec_ledger_invariants.py` enforces this for entries
   dated on or after its cutoff. Two homes, two purposes: the **spec** is the finding as
   pending work, the **ledger** is what was done about it. A finding you did not fix has a
   spec and no ledger entry, which is exactly right — it stays visible as outstanding
   rather than looking handled.
6. **Correct an invariant in place when the invariant itself is wrong.** INV-132
   asserted the MCP reference could not answer parameter shapes; the server answers
   them. Add a dated correction note explaining what was verified and when. An
   invariant that encodes a false premise is worse than a missing one.

⛔ **Do not end a run with unwritten findings.** Before reporting, list what you found and
confirm each one is either in a spec or in the ledger. "I described it in the report" is not
recorded — the report is a message, and messages are not durable. This rule exists because a
phase-3 walk reached eight turns with four findings held only in conversation, and it took
the maintainer asking *"are you keeping notes that might lead to improvements / specs?"* to
surface it.

## Reporting

Report to the maintainer with the severity ordering the findings deserve, and:

- ⛔ **Name the spec file each finding was written into**, and say plainly which findings are
  fixed and which are recorded-but-open. A report that lists findings without naming where
  they live reads as though the work is captured when it is only described.
- **Lead with anything that breaks a documented path**, not with the longest list.
- **Say what you verified as correct**, briefly. "The routing table is right, the
  opaque-state contract is handled, no `add_data_source` confabulation" is
  information, and it stops the next audit re-checking the same ground.
- ⛔ **State the coverage limits explicitly.** "No `libSz.so`, so the live server and
  every SDK-dependent path went unexercised" is the difference between a report and
  a false clean bill of health.
- **Report your own mistakes.** If a probe was wrong, or a fix was under-specified,
  or a `git restore` ate work, say so — the methodology's value depends on the
  reader trusting the parts that did work.

## Cleaning up

Remove the scratch project when the run is done (`rm -rf $HOME/senzing-bootcamp-dryrun`)
and clear `__pycache__`. Leave the repo with only intended changes: `git status`
should show the fixes, the new tests, **and the specs the findings were written into** —
nothing else.

⛔ **The scratch project is disposable; the specs are the run's actual output.** Deleting the
project is cleanup. Deleting or never writing the specs loses the run. If a run produced no
spec and no ledger entry, it produced nothing durable, however good the conversation was.

## Scope note

`.claude/` is **not** propagated to the public repo (`propagate.sh` mirrors
`plugins/`, `.claude-plugin/`, `docs/` and `README.md` only), so this skill and its
`scaffold_project.py` helper never ship to bootcampers.
