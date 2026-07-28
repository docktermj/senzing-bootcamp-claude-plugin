# Phase D's "the export never returns `RELATED_ENTITIES`" absolute is false on SDK 4.3.3 — make it flag-conditional

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two MCP-grounded instructions the bootcamp relies on directly contradict each other about whether a
bulk export carries relationship data.

`phaseD-validation.md` → "Match-key audit" states, with a stop marker:

> ⛔ **Do not expect `RELATED_ENTITIES` from `export_json_entity_report`.** … A live run on SDK 4.3.3
> returned entity rows with **no `RELATED_ENTITIES` key at all** and no error.

`reporting_guide(topic='evaluation')` states the opposite:

> Each exported row is a JSON object containing RESOLVED_ENTITY … and RELATED_ENTITIES[] (with
> ENTITY_ID, MATCH_LEVEL_CODE, MATCH_KEY, ERRULE_CODE, RECORD_SUMMARY[])

Rather than trust either, the export was run with `SZ_EXPORT_DEFAULT_FLAGS` and the first row's
top-level keys dumped:

```text
first export row top-level keys: [RESOLVED_ENTITY, RELATED_ENTITIES]
export carries RELATED_ENTITIES : true
```

**On SDK 4.3.3 the export DOES carry `RELATED_ENTITIES` under `SZ_EXPORT_DEFAULT_FLAGS`.** The
relationship figures used throughout validation — 48,071 DISCLOSED / 38,328 POSSIBLY_RELATED /
17,461 POSSIBLY_SAME, deduplicated to 103,860 unique pairs — were read from the export in a single
pass, and the 4,213-pair cross-system review queue was built the same way.

Two costs. The Phase D instruction is an absolute, so it gets followed: it sends the reader to a
per-entity reader, which works but is O(entities) instead of one export pass — on a real dataset,
the difference between a single scan and tens of thousands of individual SDK calls. And because the
two instructions cannot both be followed, whichever is read second looks like the error, and a
bootcamper has no way to adjudicate without dumping a row themselves.

The specific claim — "returned entity rows with no `RELATED_ENTITIES` key at all" — is also the more
damaging direction of error: it teaches that a correct approach is broken.

## Root cause

**`plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md:181-188`** states
the constraint as an absolute and generalizes one observation beyond its evidence. Its reasoning
(`:182-185`) is:

> Every relationship-detail flag — `SZ_ENTITY_INCLUDE_ALL_RELATIONS` and its members … lists only the
> per-entity, `why_*` and `find_*` methods in its `applies_to`; the export methods are **not** among
> them.

That inference does not hold, and the MCP server shows why. Verified against the live server at
triage time:

```text
get_sdk_reference(topic='flags', filter='SZ_EXPORT_DEFAULT_FLAGS')
  -> applies_to: ["export"]
     "Reduced the information returned for each entity, to match the normal entity defaults"
```

`SZ_EXPORT_DEFAULT_FLAGS` is itself an export-family flag whose documented behavior is to match the
**normal entity defaults** — and the entity defaults include the relationship-inclusion members
(visible in `get_entity`'s own default flag set: `SzEntityIncludePossiblySameRelations`,
`...PossiblyRelatedRelations`, `...NameOnlyRelations`, `...DisclosedRelations`,
`...RelatedEntityName`, `...RelatedMatchingInfo`, `...RelatedRecordSummary`). So "no
`SZ_ENTITY_INCLUDE_*` relationship flag lists `export` in its `applies_to`" does not entail "an export
cannot carry relationships": the export default flag bundles them.

**The two observations are compatible, and the flag set is the variable.** The earlier session
(`match-key-audit-cannot-read-related-entities-from-export`) composed a flag set explicitly from
`SZ_ENTITY_INCLUDE_*` members and got no `RELATED_ENTITIES`; this session used
`SZ_EXPORT_DEFAULT_FLAGS` and got them. A flag set assembled from entity-detail members without the
export defaults plausibly omits the relationship inclusion the defaults carry. The defect is not that
either observation was wrong — it is that the first was written up as a property of the **method**
rather than of the **flag set**.

The server does not enumerate `SZ_EXPORT_DEFAULT_FLAGS`'s composite members, so the exact membership
is not MCP-assertable and must be established by dumping a row at implementation time (INV-080,
INV-149).

## Proposed change

1. **Replace the absolute with a flag-conditional caution.** In `phaseD-validation.md:181-188`: an
   export **can** carry `RELATED_ENTITIES` — observed on SDK 4.3.3 with `SZ_EXPORT_DEFAULT_FLAGS` —
   and whether it does depends on the flag set, not on the method. Record both observations with their
   flag sets and SDK version, so neither is presented as a property of `export_json_entity_report`
   itself.

2. **Make the check the instruction.** Keep the underlying discipline, which is what caught this in
   both directions: **dump one export row's top-level keys before choosing a reader.** Then route on
   what the dump shows — `RELATED_ENTITIES` present → single export pass; absent → per-entity reader
   or `find_network_by_entity_id`. This is INV-115/INV-149 applied to a routing decision rather than
   to a field name, and it is strictly better than either absolute.

3. **Reconcile with `reporting_guide(topic='evaluation')`,** which is correct here, so the two no
   longer contradict. Where phase D restates SDK response shape, cite the reporting guide rather than
   asserting against it.

4. **Rewrite the two-reads table (`:176-179`) accordingly.** The row "Relationship match keys → **per-entity**
   `get_entity_by_entity_id` … or `find_network_by_entity_id`" must stop implying the export is
   incapable; it should name the export-with-defaults path first, with the per-entity reader as the
   fallback when the dump shows no `RELATED_ENTITIES`.

5. **Keep every guarantee the prior spec established.** The empty-result capability check
   (`:244-248`), the three-state gate (finding / no finding / could-not-measure), and the
   never-report-"no suppressors"-on-a-failed-read rule (INV-115) all stand unchanged — this spec
   corrects *which reader to reach for*, not the audit's defensive discipline. The capability check
   becomes cheaper, not unnecessary.

6. **Correct `visualization-api-reference.md` if it still carries the absolute.** The prior spec left
   its relationship-inclusion-flag remedy to be re-verified; verify it now against a dumped row and
   state the condition.

## Acceptance criteria

- [ ] `phaseD-validation.md` no longer asserts that `export_json_entity_report` cannot return
      `RELATED_ENTITIES`; the caution is conditioned on the flag set and carries the SDK version and
      flag set of each observation.
- [ ] The audit instructs dumping one export row's top-level keys **before** choosing a reader, and
      routes on the dump: export pass when `RELATED_ENTITIES` is present, per-entity reader when it is
      not.
- [ ] Phase D and `reporting_guide(topic='evaluation')` no longer contradict each other on where
      relationship data comes from; a reader encountering both is not forced to adjudicate.
- [ ] The relationship half of the audit is achievable in one export pass on an installation where
      the dump shows `RELATED_ENTITIES`, without tens of thousands of per-entity calls.
- [ ] The empty-result capability check, the three-state iterate-vs-proceed gate, and the
      never-"no suppressors"-on-a-failed-read rule are all still present and still non-blocking
      (INV-115, INV-117).
- [ ] No flag membership is asserted from training data or from this spec: `SZ_EXPORT_DEFAULT_FLAGS`'s
      relationship behavior is confirmed by a dumped row at implementation time and marked
      verified-when (INV-080, INV-149).
- [ ] `visualization-api-reference.md` agrees with phase D on this point.
- [ ] All match-key reading still goes through MCP-generated SDK code, never direct SQL against
      `database/G2C.db` (INV-117).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      guidance is expressed in SDK methods and flags, not Python specifics.

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — the two-reads
  table (`:176-179`) and the ⛔ absolute (`:181-188`): make it flag-conditional and put the row dump
  ahead of the reader choice.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the relationship-inclusion-flag remedy: state the verified condition.
- `specs/IMPLEMENTED.md` — record the correction against
  `match-key-audit-cannot-read-related-entities-from-export`, whose shipped absolute this reverses,
  so the reversal is traceable rather than looking like drift.
- `tests/` — if a test asserts the absolute, update it to assert the conditional and the
  dump-before-routing instruction.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Phase D states export does NOT supply
  RELATED_ENTITIES — it does on SDK 4.3.3" (2026-07-28, Module Data processing;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin`;
  `Upstream: not applicable`)
- Priority: Medium
- Related specs: `specs/match-key-audit-cannot-read-related-entities-from-export.md` (**this spec
  corrects the absolute that one shipped** — read them together),
  `specs/post-load-match-key-semantic-audit.md` (INV-117 — the audit itself),
  `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115),
  `specs/network-link-fields-and-uncovered-response-schemas.md` (INV-149 — dump-is-the-authority),
  `specs/verify-sdk-parameter-shapes-and-flag-families.md` (INV-132 — the sibling export-flag
  findings, and the precedent for retracting an over-generalized flag claim)
