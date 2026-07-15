---
name: implement-spec
description: 'Implement one or more specs from the specs/ directory. With no argument, list every spec not yet implemented and ask the maintainer which one(s) to implement; with an argument, implement specs/<argument>.md (name without the .md suffix). Records completed specs in specs/IMPLEMENTED.md. Maintainer tool for developing the Senzing Bootcamp Claude Plugin (SBCP) — the counterpart to feedback-to-specs, which produces the specs this skill consumes.'
---

# Implement Spec

This is a **maintainer** tool for developing the Senzing Bootcamp Claude Plugin
(SBCP). It takes a spec under `specs/` — a terse, developer-facing description of
a bug fix or improvement — and **implements it in the codebase**, then records
that the spec is done so it is not offered again.

It is the counterpart to the `feedback-to-specs` skill: that skill *writes*
specs; this skill *implements* them.

## Invocation modes

- **No argument** → discovery mode. List every spec that has **not** yet been
  implemented and ask the maintainer to choose one or more to implement.
- **An argument** → the argument is a spec **filename without the `.md`
  suffix** (e.g. `stop-hook-issue` → `specs/stop-hook-issue.md`). Implement that
  spec. Multiple names may be given (space- or comma-separated); implement each.

## The implementation record

`specs/IMPLEMENTED.md` is the **source of truth** for which specs are done. A
spec is considered implemented **iff** `IMPLEMENTED.md` contains a `## <name>`
heading whose text exactly matches the spec's filename without `.md`. Create the
file from the scaffold below if it does not exist. Never delete existing
entries; append new ones (newest first).

## What is (and isn't) a spec

Candidate specs are the `specs/*.md` files **excluding** these meta files, which
are never implementable specs:

- `invariants.md` — the ruleset every spec must respect (not a task).
- `todo.md` — the lightweight idea backlog (not yet specs).
- `IMPLEMENTED.md` — the record this skill maintains.

## Step 1: Load state

1. **List** `specs/*.md` and drop the meta files above → the candidate set.
2. **Read `specs/IMPLEMENTED.md`** (create it from the scaffold if missing) and
   collect the `## <name>` headings → the implemented set.
3. **Unimplemented = candidates − implemented.**
4. **Read `specs/invariants.md`.** Every spec begins "Maintain the invariant
   conditions in @invariants.md" — the implementation must honor it (cross-platform
   Linux/macOS/Windows, language-agnostic, production-ready, consistent/coherent/
   complete, and the per-module outcomes).

## Step 2a: Discovery mode (no argument)

If no unimplemented specs remain, say so and stop.

Otherwise present a compact numbered list — one row per unimplemented spec with
its title and a one-line summary drawn from the spec's `## Problem` section:

```text
Specs not yet implemented:

  1. stop-hook-issue      — Stop hook loops, re-asking the same closing question
  2. PreToolUseWriteError — write-gate blocks legitimate /tmp scratch paths
  ...
```

Then ask exactly one clear question inviting the choice, e.g.:

> 👉 **Which spec(s) would you like me to implement?** (reply with numbers or
> names, `all`, or a range like `1-3`)

Wait for the answer — do not choose for the maintainer. Once they answer,
resolve their choice to spec filenames and proceed to Step 3 for each.

## Step 2b: Named mode (argument given)

For each name given:

1. Strip any trailing `.md` and resolve `specs/<name>.md`.
2. If the file does not exist, say so and list the available unimplemented spec
   names, then stop for that name.
3. If it names a meta file (`invariants`, `todo`, `IMPLEMENTED`), explain it is
   not an implementable spec and stop for that name.
4. If it is **already implemented** (present in `IMPLEMENTED.md`), report that
   with the recorded date and ask whether to re-implement before proceeding —
   do not silently redo it.

## Step 3: Implement each chosen spec

Work one spec at a time. For each:

0. **Check whether it is already done in the code.** The ledger can be empty or
   stale — a spec may have been implemented before this skill (or ledger) existed.
   Watch for a `**Status:** Implemented` line in the spec header, checked-off
   acceptance criteria, or a diff/commit that already matches `## Proposed change`.
   If the code already satisfies the spec, **do not re-implement it** — jump to
   Step 3.4 (verify against the acceptance criteria) and, if it holds, record it
   in Step 4. Only implement from scratch when the code does not yet satisfy it.
1. **Read the spec in full.** Note its `## Problem`, `## Root cause`,
   `## Proposed change`, `## Acceptance criteria`, and `## Affected files`.
   (Older specs may not use these exact headings — read the whole file and infer
   the intent.)
2. **Confirm the root cause in the code before changing anything.** Open the
   files the spec implicates (`plugins/senzing-bootcamp/hooks/`, `scripts/`,
   `skills/`, `commands/`, etc.), verify the cause is what the spec says, and
   cite `file:line`. If the spec's root cause turns out to be wrong or
   unconfirmable, pause and report it rather than implementing the wrong fix.
3. **Make the change** described in `## Proposed change`, touching the
   `## Affected files` (and any others the change genuinely requires). Keep edits
   minimal and in the style of the surrounding code. **Honor every invariant** —
   in particular keep the change cross-platform and language-agnostic.
4. **Verify against the acceptance criteria.** Walk each checkbox and confirm it
   holds — run the relevant script/hook/command or exercise the flow where
   possible (consider the `/verify` skill). If a criterion cannot be satisfied,
   do not mark the spec done; report what's blocking.

If a spec is too ambiguous to implement safely, stop and ask for clarification
rather than guessing.

## Step 4: Record the implementation

Only after the change is made **and** its acceptance criteria are met, prepend an
entry to `specs/IMPLEMENTED.md` under the header (newest first). Get the date
with `date +%F` (do not hardcode it). Use the spec's filename-without-`.md` as
the `## ` heading so detection in Step 1 stays reliable:

```markdown
## <spec-name>

- **Implemented:** YYYY-MM-DD
- **Files changed:** `path/one`, `path/two`
- **Summary:** <what was done and how the acceptance criteria were satisfied>
- **Commit:** <hash, or "uncommitted">
```

Leave a blank line after the `##` heading and around the list (MD022/MD032).

If the maintainer chose to re-implement an already-recorded spec, update that
spec's existing entry rather than adding a duplicate.

Leave the spec file itself in place under `specs/` — the ledger, not the file's
location, records completion. Do not commit unless the maintainer asks; if they
do, reference the commit hash in the entry.

## Step 5: Report

For each spec implemented, report:

- The spec name and a one-line summary of the change.
- The files changed (as clickable `path:line` where useful).
- How each acceptance criterion was verified.
- The `IMPLEMENTED.md` entry that was added.

If several specs were requested, give a compact table:

| Spec | Result |
|---|---|
| `<name>` | Implemented → recorded in `specs/IMPLEMENTED.md` |
| `<name>` | Blocked — <reason> |

Then offer next steps (e.g. "want me to commit these?" or "shall I implement the
remaining specs?"). Do not implement specs that were not requested.

## Guardrails

- **Never mark a spec implemented that isn't.** The ledger must reflect reality;
  if verification fails, leave the spec off the record and say why.
- **Never invent or edit spec content** to make it easier to implement. If a
  spec is wrong, report it — fixing/authoring specs is `feedback-to-specs`' job.
- **Respect `@invariants.md`.** A change that would violate an invariant is not a
  valid implementation; surface the conflict instead.
- **Ledger is append/update only.** Never delete implementation history.
