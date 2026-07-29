# Query code that iterates a source's rows must deduplicate by `(data_source, record_id)` before counting

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

An over-matching review query (`find_duplicates`) iterated every row of each source's mapped
JSONL file and grouped by resolved `ENTITY_ID`, counting one constituent record per row. OFAC's
source data carries verified byte-identical duplicate rows — the same `RECORD_ID` appearing
several times in the file, a characteristic **documented at mapping time in Module 5**, where
the mapping decision was to keep them rather than pre-deduplicate.

The count therefore inflated two entities to **23 and 15 apparent records**, and both were
flagged for manual over-matching review. Spot-checking each with `get_entity_by_entity_id`
showed **2 real records each**: `add_record` had upserted the duplicate rows into one Senzing
record all along.

The failure is a false alarm, and an expensive one: it routes a bootcamper into an
"investigate over-matching" cycle for entities that were never over-matched, and in a KYC
context it is a wrong signal about which entities need analyst attention. Nothing errors — the
numbers look like findings.

## Root cause

`plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md:89-93`
("Iterate over records, not entity IDs") establishes the correct pattern — query programs
iterate loaded records "(from the input JSONL file or a record manifest)" and resolve each via
`get_entity_by_record_id`, never over guessed entity IDs — but it treats **one file row as one
record**. It never says that a mapped file may contain more rows than distinct
`(data_source, record_id)` keys, nor that per-record analysis must fold them before counting.

The upstream half of the gap is that Module 5 records the duplicate-row characteristic as a
mapping decision but nothing carries it forward into Module 7's query-writing guidance, so the
program is written as if row count equals record count.

`find_duplicates` is named at `phase1-query-visualize.md:84` as one of the four example query
programs — so this is the guidance's own worked example, not an exotic path.

### What the live server returned

The upsert premise the correction rests on is **confirmed**. `search_docs(query='duplicate
record id loading same record twice idempotent replace')` — server **1.32.2**, verified
**2026-07-29** — returns, from "Data Source Records (DSRs) Explained":

> "When a record with a unique key is sent to Senzing that matches a record already loaded, the
> new record replaces the current one in Senzing and doesn't contribute to the DSR count."

and, on exact duplicates within one source:

> "Senzing, by default, will automatically detect when records from the same Data Source have
> the exact same entity resolution-related data. It will preserve the records independently but
> will automatically 'dedupe' them for processing."

`get_sdk_reference(topic='parameters', filter='add_record', language='python')`, same server and
date, confirms the key is the caller-supplied pair:

```text
add_record(data_source_code: str, record_id: str, record_definition: str, flags: int = <SzEngineFlags.SZ_NO_FLAGS: 0>) -> str
```

So Senzing's own record identity is `(data_source_code, record_id)`, and re-sending the same
key replaces rather than accumulates. Per-record analysis that counts file rows is therefore
counting something Senzing does not model — which is exactly why the inflated figure had no
counterpart in `get_entity_by_entity_id`'s view.

## Proposed change

In `phase1-query-visualize.md`, extend the "Iterate over records, not entity IDs" block with the
record-identity rule:

1. **State the identity:** a Senzing record is identified by `(data_source, record_id)`, and
   `add_record` replaces on a repeated key rather than adding a second record (cite the server
   per the above). So *n* file rows carrying the same key are **one** record.
2. **Require the fold:** when a query program iterates a source's raw or mapped file rows to
   associate them with resolved entities, deduplicate by `(data_source, record_id)` **before**
   counting or grouping. Note that a mapped file legitimately carries more rows than distinct
   keys when Module 5's mapping decision was to keep a source's verified duplicate rows.
3. **Name the failure mode it prevents:** an inflated constituent-record count that falsely
   flags an entity for over-matching review. Add the cross-check — when a per-record count looks
   surprising, confirm it against Senzing's own view via `get_entity_by_entity_id` before
   reporting it as a finding, since Senzing's resolved view is the authority on how many records
   an entity has and the file is not.

Keep it language-agnostic: the rule is "fold on the key pair", not a Python idiom.

## Acceptance criteria

- [ ] `phase1-query-visualize.md` states that a Senzing record's identity is
      `(data_source, record_id)` and that repeated keys are replaced, not accumulated, with
      MCP provenance (tool, server version, date).
- [ ] The guidance requires deduplicating by `(data_source, record_id)` before counting or
      grouping whenever a query program iterates source/mapped file rows, and says a mapped file
      may legitimately carry more rows than distinct keys because of a Module 5 mapping decision.
- [ ] The guidance names the false-flag consequence (inflated constituent-record count →
      spurious over-matching review) and requires cross-checking a surprising count against
      `get_entity_by_entity_id` before reporting it.
- [ ] The rule is stated as a key-fold, with no language-specific idiom, so it holds for every
      bootcamper-chosen language.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md`
  — the "Iterate over records, not entity IDs" block (~lines 89-93), and the `find_duplicates`
  example description (~line 84) if it needs the same caveat inline.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "query code iterating raw source rows must deduplicate by (data_source, record_id) when a source has known duplicate rows" (2026-07-29, Module Query, Visualize and Discover; `Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: **still reproduces**, and the correction's premise is now server-grounded —
  server **1.32.2**, 2026-07-29, via `get_capabilities`,
  `search_docs(query='duplicate record id loading same record twice idempotent replace')` and
  `get_sdk_reference(topic='parameters', filter='add_record', language='python')`. The
  replace-on-repeated-key behavior and the `(data_source_code, record_id)` identity are both
  confirmed; the entry had asserted the upsert from observation only.
- Upstream: not applicable — the defect is in the plugin's query-writing guidance, not in
  Senzing or the MCP server.
- Related specs: `specs/post-load-match-key-semantic-audit.md`,
  `specs/match-key-audit-cannot-read-related-entities-from-export.md`

## Deviations from this spec, and why (2026-07-29)

- **No material deviation.** Both Senzing facts were re-confirmed at implementation before being
  written into the plugin: the replace-on-repeated-key behaviour via `search_docs` ("Data Source
  Records (DSRs) Explained" — *"the new record replaces the current one in Senzing and doesn't
  contribute to the DSR count"*) and the `(data_source_code, record_id)` identity via
  `get_sdk_reference(topic='parameters', filter='add_record', language='python')` (server
  **1.32.2**, verified **2026-07-29**). The implemented text quotes the server rather than
  paraphrasing it.
- **One addition the spec did not name.** The cross-check now offers `RECORD_SUMMARY[]`'s
  `RECORD_COUNT` alongside `get_entity_by_entity_id` as a way to confirm a surprising per-record
  count, because that field is populated by the *default* flags on both `search_by_attributes` and
  `find_network` and so needs no extra call or flag widening — confirmed in the same session via
  `get_sdk_reference(topic='response_schemas', filter='search_by_attributes')`. This composes with
  the sibling spec `method-default-flags-omit-record-data`, implemented in the same pass.
- **Every acceptance criterion is met and none needed a live engine.** The spec's criteria are all
  properties of the guidance text; the entity counts it cites (23 and 15 apparent records versus 2
  real ones) are the reporting run's own observation, quoted as such rather than re-verified here,
  since reproducing them would need a live engine with that source loaded.

## Invariants introduced

- `INV-180` — Code that walks a source's raw or mapped file rows to associate them with resolved
  entities MUST deduplicate by `(data_source, record_id)` before counting or grouping, because that
  pair is a Senzing record's identity and re-sending it replaces rather than adds. Senzing's
  resolved view, never the file, is the authority on how many records an entity has. (Recorded in
  `specs/INVARIANTS.md`, 2026-07-29.)
