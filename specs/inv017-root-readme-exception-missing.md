# INV-017 forbids the project-root `README.md` that INV-050, the ground rules and Module 1 all require

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two foundational invariants disagree about where the generated project's `README.md` lives,
and the plugin ships the behavior the *other* one describes.

**INV-017** (`specs/INVARIANTS.md:76`) admits exactly one exception:

> All Markdown files (`.md`) are kept in appropriate places in the `docs/` directory.
> Exception: the generated `production/` project deliverable carries its own Markdown files
> (e.g. `README.md`, `MIGRATION_CHECKLIST.md`, `GRADUATION_REPORT.md`).

**INV-050**'s layout tree puts a `README.md` at the **project root** (`:158`,
`├── README.md  # Project overview`), separately and additionally to `docs/README.md`
(`:186`). Under INV-017 as written, that root file is a violation — `production/` is the
only exception, and the project root is not `production/`.

Three shipped sites side with INV-050:

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:216-217` states the
  layout rule with **both** exceptions: *"docs and all `*.md` (except `README.md` and the
  generated `production/` project's own `.md` files) -> `docs/`"*.
- The same file's **project root whitelist** (`:220-222`) names `README.md` explicitly and
  then forbids *"`.md` (except README)"* in the root — i.e. the root README is deliberate
  and every other root `.md` is banned.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md:186`
  is a step headed **"## 12. Update README.md"**, so the bootcamp actively writes it.

So INV-017 is the outlier: the ruleset's most-cited placement invariant forbids a file that
the ruleset's layout invariant mandates, that the ground rules whitelist by name, and that
a module updates.

**What the conflict costs.** INV-017 is cited as the authority for file placement across the
plugin. An agent applying it literally — or an audit checking conformance against it — has
two defensible conclusions: move the root `README.md` into `docs/` (breaking INV-050's tree,
the root whitelist, and Module 1 Step 12), or treat INV-017 as unreliable. Both are bad, and
the second is worse because it discounts a foundational invariant wholesale.

## Root cause

INV-017 and INV-050 are both in the original INV-001–050 block, so neither supersedes the
other and no supersession note exists to reconcile them. INV-017's exception clause was
extended once — to cover the `production/` deliverable — and the project-root `README.md`
was never added, even though `ground-rules.md:216-217` had already written the two-exception
form that INV-017 should mirror.

Nothing could catch it: the shipped ground rules are correct, so no bootcamp run
misbehaves, and no test compares INV-017's exception list against `ground-rules.md`'s. The
defect is visible only by reading the two invariants against each other, which is what this
finding did.

## Proposed change

**Clarify INV-017 in place so its exception list matches the operative rule already shipped
in `ground-rules.md:216-217`** — the project root's `README.md` **and** the generated
`production/` project's own `.md` files.

This is an in-place clarification under rule 2 of "Maintaining this file", not a change of
meaning: INV-050 has mandated the root `README.md` since the same original block, the ground
rules have always excepted it, and Module 1 has always updated it. INV-017's text is being
corrected to describe what the invariant set has always required, so no behavior changes and
no shipped file moves.

Record the correction the way the file records its other in-place fixes — a dated
parenthetical naming what was stale and the evidence — so a later reader can tell a
clarification from a silent rewrite.

⚠️ **Do not "fix" this by moving the root `README.md` into `docs/`.** That would break
INV-050's layout tree, contradict the root whitelist that names it, and orphan Module 1
Step 12. INV-017's text is the defect, not the file's location.

⚠️ **If the maintainer judges this a change of meaning rather than a clarification**, rule 2
requires a *new* invariant instead: INV-017 stays as written and is annotated as superseded
on its exception clause only. The spec's outcome is the same either way — what changes is the
mechanism, and that call is the maintainer's.

## Acceptance criteria

- [ ] INV-017's exception clause names the project-root `README.md` in addition to the
      generated `production/` project's `.md` files.
- [ ] INV-017's exception list is equivalent to `ground-rules.md:216-217`'s parenthetical —
      the two state the same rule.
- [ ] The change is recorded as a dated in-place clarification naming what was stale, or —
      if the maintainer rules it a meaning change — as a new invariant with INV-017
      annotated as superseded on that clause only. No invariant is deleted or renumbered.
- [ ] No file moves and no shipped guidance changes: `docs/README.md`, the root
      `README.md`, INV-050's tree, the root whitelist and Module 1 Step 12 are all unchanged.
- [ ] A test asserts INV-017's exception list and `ground-rules.md`'s placement
      parenthetical agree, so the two cannot drift apart again.
- [ ] `python3 .claude/skills/compact-dev-environment/citations.py verify` stays clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-017 (`:76`), exception clause.
- `tests/` — a new or extended test pinning the INV-017 ↔ `ground-rules.md` agreement.

## Source

- **Found by:** maintainer question — *"Are there any invariants in @specs/INVARIANTS.md
  that conflict with each other?"* — 2026-07-31.
- Priority: **Medium.** Nothing is broken for a Bootcamper — the shipped ground rules are
  correct — but a foundational placement invariant contradicts three shipped sites, which
  misleads any agent or audit that applies it literally.
- MCP re-check: **n/a (no Senzing fact).** File placement is plugin-internal; no MCP tool
  owns it and none was called.
- Upstream: not applicable.
- Related specs: `specs/layout-tree-reconciliation.md` (INV-070, the last time the layout
  tree and a placement rule were reconciled), `specs/invariants-index-flattens-partial-supersession.md`
  (found in the same pass).
