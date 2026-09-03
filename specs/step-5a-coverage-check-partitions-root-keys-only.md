# Step 5a's coverage check partitions root keys only, so a non-spec sub-list reads as structural

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-05-data-quality-mapping/phase1-quality-assessment.md` Step 5a, coverage check, says:

> Over the same sampled records, partition every **root key** into three sets:
> - **structural keys** — `DATA_SOURCE`, `RECORD_ID`, `RECORD_TYPE`, `FEATURES`, and the legacy
>   per-feature root sub-lists (`NAMES`, `ADDRESSES`, `IDENTIFIERS`, …);
> - **specification attributes** — keys that resolve to an attribute in the Entity Specification…
> - **unrecognized keys** — everything else.

On a legacy-flat source the entity data lives **inside** those sub-lists, and the partition never
looks there. The trailing `…` in the structural set is the problem: it gives no rule for deciding
whether an arbitrary ALL-CAPS root array is a per-feature sub-list or an unrecognized key.

Observed live on 2026-08-31 mapping `las-vegas / GLEIF` (1,952 records). Its root keys are:

```
ADDRESSES  COUNTRIES  DATA_SOURCE  DATES  IDENTIFIERS  LAST_CHANGE
NAMES  RECORD_ID  RECORD_TYPE  RELATIONSHIPS  RISKS  URL
```

Four of those are arrays that *look* like per-feature sub-lists. Three genuinely are — their
contents resolve to spec attributes (`COUNTRIES.REGISTRATION_COUNTRY`, `DATES.REGISTRATION_DATE`,
`RELATIONSHIPS.REL_ANCHOR_*`/`REL_POINTER_*`). The fourth does not: **`RISKS` contains `TOPIC`
(547 occurrences), which is not a Senzing attribute at all.**

Running the check as written, `RISKS` lands in **structural** — the same bucket as `NAMES` — and its
undispositioned contents are invisible. I made exactly this error while walking the step.

**The consequence is the one the step exists to prevent.** Step 5a gates the fast-path offer on the
coverage check, and its own ⛔ says why:

> Classifying a partially-mapped source as ready on this test alone is what let a source with eleven
> undispositioned columns skip the module.

A source whose only non-spec content sits inside such a sub-list — trivially constructible, and
GLEIF is one stray root scalar away from it — passes the coverage check with zero unrecognized keys
and is offered the fast path, skipping the mapping module with real fields undispositioned. GLEIF
itself was saved only by two unrelated root scalars (`LAST_CHANGE`, `URL`).

## Root cause

`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`,
Step 5a, coverage check. Two compounding issues:

1. **The partition unit is the root key**, but on the legacy-flat shape the dispositionable content
   is one level down. Step 5a's *structural* check (step 2) already reads inside records; the
   *coverage* check (step 3) does not.
2. **The structural set is open-ended.** `(NAMES, ADDRESSES, IDENTIFIERS, …)` invites membership by
   resemblance — plural, uppercase, an array of objects — which is exactly what `RISKS` satisfies.

The step is otherwise careful about this class of mistake: it already warns against resolving spec
attributes by exact string match, because `BUSINESS_NAME_ORG` must resolve to `NAME_ORG`. That
warning is about the same failure at the leaf level; this is the same failure at the container level.

## Proposed change

1. **Close the structural set** to what the Entity Specification actually defines: the record-level
   keys (`DATA_SOURCE`, `RECORD_ID`, `RECORD_TYPE`), `FEATURES`, and root sub-lists **whose contents
   resolve to spec attributes**. Membership is decided by looking inside, never by the key's shape.
2. **Recurse the partition one level.** For any root key holding an array of objects, partition the
   *contained* keys by the same three-way test, and count an unresolved contained key as an
   unrecognized key of the source.
3. **State the discriminator in one line**, since it is the whole rule: *a root array is a
   per-feature sub-list only if its contents are spec attributes; if its contents do not resolve, the
   array is unrecognized content, not structure.*

## Acceptance criteria

- [ ] The coverage check examines the contents of root arrays, not only root key names.
- [ ] A source carrying a root array whose contained keys do not resolve to spec attributes is
      classified **not** fast-path eligible.
- [ ] Applied to `las-vegas / GLEIF`, `RISKS` is reported as unrecognized content (via `TOPIC`),
      alongside `LAST_CHANGE` and `URL`.
- [ ] Genuine per-feature sub-lists (`NAMES`, `ADDRESSES`, `IDENTIFIERS`, `COUNTRIES`, `DATES`,
      `RELATIONSHIPS` on GLEIF) still classify as structural.
- [ ] The structural set is stated as closed, with the contents test as its membership rule.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  Step 5a, coverage check (step 3).

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, Data Quality/Mapping Step 5a
  (`Source: self-observed (assistant retrospective)`) — found by making the error the step permits
  while running its coverage check against a real legacy-flat CORD source, then catching it when the
  profiler exposed the nested attribute inventory.
- Priority: Medium
- MCP re-check: server **1.35.1**, 2026-08-31 — the shape claim is re-confirmed:
  `get_sample_data(dataset='las-vegas', source='GLEIF')` returns the legacy per-feature sub-list form
  with `NAMES`/`ADDRESSES`/`IDENTIFIERS`/`RELATIONSHIPS` plus non-spec `RISKS` and `URL`, matching
  the step's own statement that CORD ships both shapes. `RISKS.TOPIC` appears in no Senzing feature
  family in the delivered mapping reference's catalog.
  owner-checked: the `mapping_workflow` step-2 inline mapping reference is the authority on valid
  feature families and attribute keys, and neither `RISKS` nor `TOPIC` appears in either list.
- Upstream: not applicable — the check is the plugin's.
- Related specs: none
