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

1. **Fix the class, not the instance,** where the class is cheap to remove. The
   `_clip` ellipsis defect had three call sites; changing the suffix to ASCII inside
   `_clip` made the ordering hazard unreachable instead of fixing three callers.
2. **Write a test in the repo-level `tests/`** — stdlib only, no `plugins/` (INV-108).
   A dry run you cannot repeat cheaply is a one-off; a test is the durable half.
3. ⛔ **Negative-control the test.** Reintroduce the defect, confirm the test fails,
   revert. A guard whose docstring claims more than its assertion checks is worse
   than no guard, because it certifies what it never tested. This is not optional:
   in the originating session, one existing test had **pinned the wrong premise**,
   which is how the defect it covered survived three audits.
4. **Record it** in `specs/IMPLEMENTED.md`, and either register the invariant it
   establishes in `specs/INVARIANTS.md` or state that it establishes none —
   `tests/test_spec_ledger_invariants.py` enforces this for entries dated on or
   after its cutoff.
5. **Correct an invariant in place when the invariant itself is wrong.** INV-132
   asserted the MCP reference could not answer parameter shapes; the server answers
   them. Add a dated correction note explaining what was verified and when. An
   invariant that encodes a false premise is worse than a missing one.

## Reporting

Report to the maintainer with the severity ordering the findings deserve, and:

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
should show the fixes and new tests, nothing else.

## Scope note

`.claude/` is **not** propagated to the public repo (`propagate.sh` mirrors
`plugins/`, `.claude-plugin/`, `docs/` and `README.md` only), so this skill and its
`scaffold_project.py` helper never ship to bootcampers.
