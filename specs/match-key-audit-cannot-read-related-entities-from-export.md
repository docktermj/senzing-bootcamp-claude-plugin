# The match-key audit cannot read `RELATED_ENTITIES` from a bulk export

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`skills/module-06-data-processing/phaseD-validation.md`'s "Match-key audit" instructs reading match
keys from **both** `RESOLVED_ENTITY.RECORDS[].MATCH_KEY` and `RELATED_ENTITIES[].MATCH_KEY`. The
audit was built on a full-database export via `export_json_entity_report`, with every
`SZ_ENTITY_INCLUDE_*` detail flag that could be found added — including the relationship flags
(`SZ_ENTITY_INCLUDE_ALL_RELATIONS` family). The export still returned **no `RELATED_ENTITIES` key at
all**.

The audit therefore reported an **empty** cross-source suppressor list, which reads exactly like
"no suppressors found — clean result" rather than "this data source cannot answer the question."

It was caught only by manually investigating an unrelated entity (`AMAZONMASONRYINC`) and finding a
`-TRUSTED_ID` suppressor the audit had never reported. Re-running the same lookup through
`get_entity_by_entity_id` returned the relationship detail immediately. The real audit result was
`TRUSTED_ID` on **284 same-source / 86 cross-source** comparisons — the single most important
finding of the module, initially invisible.

This is the exact defect class the match-key audit exists to catch, reproduced *in the audit itself*:
all gates green, the finding silently absent. A bootcamper following the phase D instructions with an
export-based reader will conclude their mapping has no cross-source suppressors, and the module's own
iterate-vs-proceed gate will be decided on a number that was **never measured**. Nothing in the
output looks wrong.

## Root cause

Two gaps, one of which is an actively misleading instruction.

**1. Phase D never says the export cannot supply relationships.**
`plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md:172-175`:

> 1. **Read the match keys** from the loaded results using generated SDK code … Per
>    `get_sdk_reference(topic='response_schemas')`, a resolved entity's per-record match keys are at
>    `RESOLVED_ENTITY.RECORDS[].MATCH_KEY`, and relationship match keys at
>    `RELATED_ENTITIES[].MATCH_KEY`.

Both paths are presented as equally readable "from the loaded results", with no note that the second
requires a per-entity call. A reader who reaches for a bulk export — the obvious choice for
"tabulate across the whole database" — gets one of the two and no signal about the other.

Step 3 (`:181-186`) then asks for a finding about high-share cross-source suppressors, with no
defensive check on an empty list.

**2. The plugin's own documented workaround is wrong.**
`plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md:98-108`
already documents the limitation for graph edges:

> a plain `export_json_entity_report` does not include relationship data by default, so reading
> `RELATED_ENTITIES` from it yields an empty `edges` array

— so the knowledge exists in the plugin; it just is not present where phase D sends the reader. But
the **second remedy** that same passage offers is contradicted by this session's observation:

> - **Relationship-inclusion export flag:** request the entity export/report with the flag that
>   includes all relations (`SZ_ENTITY_INCLUDE_ALL_RELATIONS`, confirmed via the Senzing MCP
>   server) so `RELATED_ENTITIES` is populated, then build edges from it.

That is precisely what was tried, and `RELATED_ENTITIES` was still absent. So the plugin documents a
workaround that does not work, in the file that is otherwise the authority on this.

**Verification status:** the observed behavior (no `RELATED_ENTITIES` from
`export_json_entity_report` at any flag combination, on SDK 4.3.3 build 4.3.3.26191) is a single
careful observation, not yet re-confirmed against the MCP server. **Re-verify via the Senzing MCP
server before rewriting the `visualization-api-reference.md` bullet** — if the flag does work under
some condition, the fix is to state that condition; if it does not, the bullet must go. Either way
phase D's fix below stands on its own.

## Proposed change

**1. State the constraint where phase D sends the reader.**

In the match-key audit step, say explicitly that `RELATED_ENTITIES[].MATCH_KEY` requires a per-entity
`get_entity_by_entity_id` / `get_entity_by_record_id` call and is **not** obtainable from
`export_json_entity_report`. Separate the two reads structurally, so the instruction cannot be
satisfied halfway:

- per-record match keys (`RESOLVED_ENTITY.RECORDS[].MATCH_KEY`) — from the bulk export;
- relationship match keys (`RELATED_ENTITIES[].MATCH_KEY`) — per-entity calls over the entity set,
  or `find_network_by_entity_id`.

**2. Add the defensive empty-result check the audit needs.**

If the cross-source suppressor list comes back empty, **verify the reader actually has
`RELATED_ENTITIES` before reporting "no suppressors."** An empty result here is a probable plumbing
failure first and a clean bill of health second — exactly as INV-115 already prescribes for blank
parsed fields. Concretely: assert that at least one entity known to have relationships
(`relationships_total > 0` from the stats, or any entity with a `POSSIBLY_SAME`/`POSSIBLY_RELATED`
link) yields a non-empty `RELATED_ENTITIES` from the reader before any "no cross-source suppressors"
statement is made. If that assertion fails, report **"the audit could not read relationship match
keys"** — never "no suppressors were found."

**3. Carry the unmeasured case into the gate.**

The iterate-vs-proceed gate (`phaseD-validation.md:196-205`) must distinguish "audited, no finding"
from "could not audit". A gate decided on an unmeasured number is worse than a gate told the
measurement failed. Keep the audit non-blocking (INV-117) — this adds a third state to the finding,
not a new blocker.

**4. Correct or qualify the `visualization-api-reference.md` bullet** (`:106-108`) after MCP
re-verification, and cross-reference the phase D constraint from it so the two files agree.

## Acceptance criteria

- [ ] `phaseD-validation.md` states that `RELATED_ENTITIES[].MATCH_KEY` is not obtainable from
      `export_json_entity_report` regardless of flags, and names the per-entity methods that do
      supply it.
- [ ] The audit's two reads are described as two distinct operations with distinct methods, not one
      bullet listing two field paths.
- [ ] An empty cross-source suppressor list triggers a reader-capability check before any
      "no suppressors" claim, and reports "could not read relationship match keys" when the check
      fails.
- [ ] The iterate-vs-proceed gate distinguishes three states — finding, no finding, could-not-measure
      — and presents the third as such (INV-117: still a finding that routes, never a blocker).
- [ ] A run whose reader genuinely lacks `RELATED_ENTITIES` produces a visible statement that the
      relationship half of the audit did not execute; the bootcamper cannot mistake it for a clean
      result (INV-115).
- [ ] The `SZ_ENTITY_INCLUDE_ALL_RELATIONS` remedy in `visualization-api-reference.md:106-108` is
      re-verified against the Senzing MCP server and then either corrected with its actual condition
      or removed — the two files no longer disagree.
- [ ] All match-key reading still goes through MCP-generated SDK code, never direct SQL against
      `database/G2C.db` (INV-117).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      constraint is described in terms of SDK methods, not Python specifics.

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — split the two
  reads and state the export constraint (`:172-175`); add the empty-result capability check
  (`:181-186`); add the could-not-measure state to the gate (`:196-205`).
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — correct or qualify the relationship-inclusion-flag remedy after MCP re-verification (`:98-108`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "`export_json_entity_report` never returns
  `RELATED_ENTITIES`, silently emptying the Module 6 match-key audit" (2026-07-26, Module Data
  processing; `Source: self-observed (assistant retrospective)`)
- Priority: High
- Related specs: `specs/post-load-match-key-semantic-audit.md` (INV-117 — established this audit),
  `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115 — the blank-field rule this applies
  to an empty list), `specs/verify-sdk-parameter-shapes-and-flag-families.md` (the sibling
  export-flag findings from the same phase D work),
  `specs/artifact-level-verification-for-deliverables.md`.
