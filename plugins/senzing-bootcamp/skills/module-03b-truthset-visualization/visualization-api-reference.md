# Truth Set Visualization: API Reference

> **Language note (INV-090):** the API endpoints and JSON response shapes below are the contract to
> implement in the Bootcamper's chosen language. `search_builder.py` / `graph_builder.py` are the
> **Python reference implementation's** internal module names — not required file names for your
> implementation.

**Purpose:** full API response schemas and the `search_builder.py` enrichment specification for
the Truth Set visualization web service. This is reference material, loaded on demand from
`phase1-visualization.md` (Step 2). See that file for the executable generation and verification
steps.

All endpoint data derives from Senzing SDK methods (`export_json_entity_report`,
`get_entity_by_entity_id`, `search_by_attributes`, `find_network_by_entity_id`,
`why_records`, `why_record_in_entity`, `how_entity_by_entity_id`). These are SDK
methods, not MCP tools; generate the SDK code for them via `get_sdk_reference` + `sdk_guide`, and
confirm exact method and flag names via the Senzing MCP server. Never query `database/G2C.db`
with SQL.

## API Endpoints

The server SHALL expose these endpoints:

**`GET /api/stats`:** Aggregate entity resolution statistics

```json
{
  "records_total": 510,
  "entities_total": 395,
  "multi_record_entities": 87,
  "cross_source_entities": 42,
  "relationships_total": 156,
  "data_sources_total": 3,
  "histogram": {"1": 308, "2": 65, "3": 17, "4+": 5},
  "bucket_entities": {
    "1": [{"entity_id": 10, "entity_name": "Alice Johnson", "record_count": 1}],
    "2": [{"entity_id": 1, "entity_name": "Robert Smith", "record_count": 2}],
    "3": [], "4+": []
  },
  "sample_entities": [
    {"entity_id": 1, "entity_name": "Robert Smith", "record_count": 3, "data_sources": ["CUSTOMERS", "REFERENCE"]}
  ]
}
```

Required fields: `records_total`, `entities_total`, `multi_record_entities`,
`cross_source_entities`, `relationships_total`, `data_sources_total`, `histogram`,
`bucket_entities`, `sample_entities`. The `histogram`
maps record-count buckets (1, 2, 3, 4+) to entity counts; `bucket_entities` maps the same buckets
to the entities in each (each `{entity_id, entity_name, record_count}`) so the histogram bars are
clickable and drill down to the entities in a bucket. Implementations MAY cap each bucket list
(the reference caps at 200 per bucket); the `histogram` counts remain authoritative.
`sample_entities` is the multi-record entities in descending record-count order (the reference caps
the list at 10), each `{entity_id, entity_name, record_count, data_sources}` — the largest resolved
entities, shown beneath the histogram on the same tab.
`data_sources_total` is the count of distinct data-source codes across all entities; the client
uses it to decide whether the **Cross-Source** tab applies (it needs 2+ sources).

**`GET /api/graph`:** Entity nodes and relationship edges

```json
{
  "nodes": [
    {"entity_id": 1, "entity_name": "Robert Smith", "record_count": 3, "data_sources": ["CUSTOMERS", "REFERENCE"], "records": [{"data_source": "CUSTOMERS", "record_id": "1001"}]}
  ],
  "edges": [
    {"source_entity_id": 1, "target_entity_id": 2, "match_key": "+NAME+ADDRESS", "relationship_type": "possible_match"}
  ]
}
```

Each node: `entity_id`, `entity_name`, `record_count`, `data_sources`, `records`. Each edge:
`source_entity_id`, `target_entity_id`, `match_key`, `relationship_type`.

**`relationship_type` vocabulary (enumerated).** `relationship_type` MUST be one of the values
below — a closed set, so the legend and the edge styling cannot drift apart. Derive it from the
Senzing relationship fields, which `get_sdk_reference(topic='response_schemas')` documents on
`RELATED_ENTITIES[]` as `MATCH_LEVEL_CODE` (values `POSSIBLY_SAME`, `POSSIBLY_RELATED`),
`IS_DISCLOSED` (1 when the relationship was disclosed in the source data) and `IS_AMBIGUOUS`
(verified 2026-07-25 — re-verify rather than trusting this table):

| `relationship_type` | Derived from | Bootcamper-facing label |
|---|---|---|
| `possibly_same` | `MATCH_LEVEL_CODE == "POSSIBLY_SAME"` | "possibly the same entity" |
| `possibly_related` | `MATCH_LEVEL_CODE == "POSSIBLY_RELATED"` | "possibly related" |
| `disclosed` | `IS_DISCLOSED == 1` (takes precedence over the match level) | "disclosed relationship" |
| `ambiguous` | `IS_AMBIGUOUS == 1` | "ambiguous" |

Emit the label alongside the code so the legend text and the edge data share one source. Do not
invent additional values: an unrecognized relationship falls back to `possibly_related` rather than
creating a new type the legend does not know about.

> `source_entity_id`/`target_entity_id` are the unchanged API contract; mapping to D3's
> `source`/`target` is a client-side concern handled in `drawGraph` (see the edge-mapping
> requirement in Step 2 of `phase1-visualization.md`).

**Edge discovery.** The example JSON above shows the edge shape only; it does not imply edges come
from an export. ⛔ **`export_json_entity_report` does not supply `RELATED_ENTITIES` — reading edges
from an export yields an empty `edges` array, and no error.** Every relationship-detail flag
(`SZ_ENTITY_INCLUDE_ALL_RELATIONS` and its members, `SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO`,
`SZ_INCLUDE_MATCH_KEY_DETAILS`) lists only the per-entity, `why_*` and `find_*` methods in its
`applies_to`; the export methods are **not** among them. Confirm with
`get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_ALL_RELATIONS')`.

`graph_builder.py` SHALL therefore discover relationships through a **per-entity or network**
method:

- **`find_network_by_entity_id`:** for multi-record/related entities, retrieve the relationship
  network and derive edges from the returned links. (Note the Python binding takes a plain
  `List[int]` of entity IDs, not an entity-IDs JSON document.)
- **`get_entity_by_entity_id` / `get_entity_by_record_id`:** per entity, with
  `SZ_ENTITY_INCLUDE_ALL_RELATIONS` (or `SZ_ENTITY_DEFAULT_FLAGS`, which contains it), then build
  edges from each entity's `RELATED_ENTITIES[]`.

`SZ_EXPORT_INCLUDE_ALL_HAVING_RELATIONSHIPS` is a **row filter** — it selects which entities appear
in an export, not what relationship detail each row carries — so it does not substitute for either
of the above.

⛔ If the resulting `edges` array is empty, treat it as a probable reader failure before reporting
"no relationships" (INV-115): confirm against the load summary's relationship count, and say the
edges could not be read rather than rendering a graph that implies there were none.

Map each discovered relationship to an `Edge`: `match_key` is taken from the Senzing
relationship's match-key string and `relationship_type` reflects the relationship kind (e.g.,
possible match / disclosed / discovered). De-duplicate edges and create an edge only between
entities that both appear in the node set above.

> Confirm the exact Senzing flag/method names via the Senzing MCP server (`search_docs` /
> `sdk_guide` / `get_sdk_reference`) when generating code; do not assert them from training data.
> Refer to the MCP server by name only; no URL.

**`GET /api/merges`:** Multi-record entities with constituent records

```json
[
  {
    "entity_id": 1, "entity_name": "Robert Smith", "match_key": "+NAME+ADDRESS",
    "records": [
      {"data_source": "CUSTOMERS", "record_id": "1001", "name": "Robert Smith", "address": "123 Main St", "phone": "555-0100", "identifiers": {"SSN": "123-45-6789"}}
    ]
  }
]
```

Each entity: `entity_id`, `entity_name`, `match_key`, `records`. Each record: `data_source`,
`record_id`, `name`, `address`, `phone`, `identifiers`. Only entities with 2+ records are
returned.

**`GET /api/search`:** Search entities with enriched resolution reasoning

```json
{
  "results": [
    {
      "entity_id": 1,
      "entity_name": "Robert Smith",
      "record_count": 3,
      "data_sources": ["CUSTOMERS", "REFERENCE"],
      "match_keys": {
        "entity_level": "+NAME+DOB+PHONE",
        "per_record": ["+NAME+DOB", "+PHONE", "+NAME+ADDRESS"]
      },
      "feature_scores": [
        {"feature": "NAME", "score": 97, "label": "CLOSE"},
        {"feature": "DOB", "score": 100, "label": "SAME"},
        {"feature": "PHONE", "score": 100, "label": "SAME"}
      ],
      "resolution_rules": [
        {"data_source": "CUSTOMERS", "record_id": "1001", "rule": "CNAME_CFF_CEXCL"},
        {"data_source": "REFERENCE", "record_id": "2001", "rule": "CNAME_CFF"}
      ],
      "enrichment_error": null
    }
  ],
  "query": {
    "name": "Robert Smith",
    "address": null,
    "phone": null,
    "email": null
  }
}
```

Each result includes the base fields (`entity_id`, `entity_name`, `record_count`,
`data_sources`) plus enrichment fields:

| Field | Type | Description |
|-------|------|-------------|
| `match_keys.entity_level` | `string \| null` | The overall match key string for the entity |
| `match_keys.per_record` | `list[string]` | Per-record match key strings (empty list for single-record entities) |
| `feature_scores` | `list[object]` | Each entry: `feature` (string), `score` (int 0-100), `label` (string) |
| `resolution_rules` | `list[object]` | Each entry: `data_source` (string), `record_id` (string), `rule` (string) |
| `enrichment_error` | `string \| null` | Non-null if `get_entity_by_entity_id` failed; contains exception type + message |

**Error case response:** when enrichment fails for a specific entity, return the basic result
with null enrichment fields and an `enrichment_error` string:

```json
{
  "entity_id": 5,
  "entity_name": "Jane Doe",
  "record_count": 2,
  "data_sources": ["WATCHLIST"],
  "match_keys": null,
  "feature_scores": null,
  "resolution_rules": null,
  "enrichment_error": "SzError: Entity 5 not found in repository"
}
```

**Single-record entity response:** when an entity has only one record (no inter-record
resolution occurred), return an empty `per_record` list and empty `resolution_rules` list:

```json
{
  "entity_id": 10,
  "entity_name": "Alice Johnson",
  "record_count": 1,
  "data_sources": ["CUSTOMERS"],
  "match_keys": {
    "entity_level": "+NAME",
    "per_record": []
  },
  "feature_scores": [
    {"feature": "NAME", "score": 95, "label": "CLOSE"}
  ],
  "resolution_rules": [],
  "enrichment_error": null
}
```

> ⛔ **The JSON payloads below illustrate SHAPE, not field names (INV-115).** They are examples,
> not authority. Before writing any code that parses an SDK response, call
> `get_sdk_reference(topic='response_schemas', filter='<method>')`; for nesting deeper than that
> topic documents, dump one raw response and read it. A wrong field name does not raise — it
> yields `None` and renders blank, so the output reads as "Senzing found nothing" rather than a
> bug. Three such mistakes shipped silently in one bootcamp before anyone noticed.
>
> **MCP-confirmed response paths** (verified 2026-07-25 against `get_sdk_reference` and
> `search_docs`; re-verify rather than trusting this list):
>
> | Method | Confirmed paths |
> |---|---|
> | `get_entity_by_entity_id` / `get_entity_by_record_id` | `RESOLVED_ENTITY.ENTITY_ID`, `.ENTITY_NAME`, `.FEATURES`, `.RECORD_SUMMARY`, `.RECORDS[]` with `.DATA_SOURCE` / `.RECORD_ID` / `.MATCH_KEY` / `.MATCH_LEVEL_CODE` / `.ERRULE_CODE`; `RELATED_ENTITIES[]` with `.ENTITY_ID` / `.MATCH_LEVEL_CODE` / `.MATCH_KEY` / `.IS_DISCLOSED` / `.IS_AMBIGUOUS` |
> | `why_entities` / `why_records` / `why_record_in_entity` | `WHY_RESULTS[]` (carries `MATCH_INFO`), `ENTITIES[]` |
> | `how_entity_by_entity_id` | `HOW_RESULTS.RESOLUTION_STEPS[]`, `HOW_RESULTS.FINAL_STATE` |
> | `search_by_attributes` | `RESOLVED_ENTITIES[]` (each carries `MATCH_INFO` and `ENTITY`) |
> | `find_path_*` | `ENTITY_PATHS[]`, `ENTITIES[]` |
> | `find_network_*` | `ENTITY_PATHS[]`, `ENTITIES[]`, `ENTITY_NETWORK_LINKS[]` |
>
> **Watch this asymmetry — it is a silent-blank trap.** With `SZ_INCLUDE_MATCH_KEY_DETAILS`, the
> match-key breakdown sits under a **differently named key** depending on the call: `why_*` puts a
> **`WHY_KEY_DETAILS`** object inside `MATCH_INFO`, while `how_entity_by_entity_id` puts a
> **`MATCH_KEY_DETAILS`** object inside each resolution step's `MATCH_INFO`. Both contain
> `CONFIRMATIONS` (and optionally `DENIALS`). Reusing one parser for both silently yields nothing.
>
> Field names *inside* those `CONFIRMATIONS` entries, and the exact `FEATURE_SCORES` path, are
> **not** documented by `response_schemas` — dump a raw response to confirm them. Do not copy
> field names from any prior implementation, this file included.
>
> **The graph methods stop at the top level, and their link elements are the next trap.** Verified
> 2026-07-26: `get_sdk_reference(topic='response_schemas', filter='find_network')` **does** return an
> entry, but it documents only the three arrays above — `ENTITY_NETWORK_LINKS[]` is described as
> "Network link details between entities" with **no element fields**. So the lookup succeeds and
> still leaves you guessing at the very field names you are about to parse. Dump one raw link
> element and read its keys before writing the parser (INV-115).
>
> ⚠️ **Do not assume a link's endpoints are keyed the way related-entity records are.** A bootcamp
> session reported that parsing `ENTITY_NETWORK_LINKS` entries with the `ENTITY_ID` /
> `RELATED_ENTITY_ID` pairing used elsewhere yielded `None` for **both** endpoints while `MATCH_KEY`
> rendered correctly, and that the endpoints were instead carried under normalized low-to-high keys.
> That observation is **not MCP-confirmable** — it is not in `response_schemas` and not in the
> indexed documentation — so treat it as a **warning about where to look, never as the field names
> to code against**. Dump the element and use what is actually there.
>
> ⛔ **A partially populated row is a wrong field name, not partial data.** This is the shape the
> above failure takes: `MATCH_KEY` renders, both endpoints are blank, and the row looks like a
> relationship Senzing could not fully describe. An all-blank row invites suspicion; a half-populated
> one does not, because the fields that *did* populate signal that the parse worked. When some fields
> of a parsed record populate and others do not, suspect the blank ones' names first (INV-115) and
> confirm against a dumped response before rendering.
>
> **Methods with no `response_schemas` entry at all.** `get_version` and `get_license` return an
> empty `data` array (verified 2026-07-26) — the lookup is not failing, the coverage is simply
> absent. An empty result is the expected outcome for those, not an error to retry: dump the response
> and read the shape from it.

**`GET /api/why?entity_id=<id>`:** Explain WHY the records in an entity resolved together

Backed by `why_records` (comparing two of the entity's constituent records) or, for a
single-record entity, `why_record_in_entity`. Use the `SZ_WHY_RECORDS_DEFAULT_FLAGS` /
`SZ_WHY_RECORD_IN_ENTITY_DEFAULT_FLAGS` group (these include `SZ_INCLUDE_FEATURE_SCORES`; add
`SZ_INCLUDE_MATCH_KEY_DETAILS` for match-key breakdowns) — confirm exact method/flag names **and
the response structure** via the Senzing MCP server (`get_sdk_reference`, topics `flags` and
`response_schemas`).

```json
{
  "entity_id": 1,
  "mode": "why_records",
  "result": {"WHY_RESULTS": ["..."], "ENTITIES": ["..."]}
}
```

`result` is the SDK `why_*` response JSON verbatim. On failure, return
`{"entity_id": <id>, "error": "<type>: <message>"}` (not a 500), so one entity's failure never
breaks the tab.

**`GET /api/how?entity_id=<id>`:** Explain HOW an entity was constructed from its records

Backed by `how_entity_by_entity_id` with `SZ_HOW_ENTITY_DEFAULT_FLAGS` (confirm via the MCP
server).

```json
{
  "entity_id": 1,
  "result": {"HOW_RESULTS": {"RESOLUTION_STEPS": ["..."], "FINAL_STATE": {"VIRTUAL_ENTITIES": ["..."]}}}
}
```

`result` is the SDK response JSON verbatim: `HOW_RESULTS.RESOLUTION_STEPS[]` are the construction
steps, and `FINAL_STATE.VIRTUAL_ENTITIES[]` describes the resolved entity when there are no
incremental steps. On failure, return `{"entity_id": <id>, "error": "..."}`.

**`GET /api/dashboard`: REMOVED.** Its content is served by `/api/stats`, which carries the same
`histogram` and headline counts plus the `sample_entities` list that was this endpoint's only
unique content. Do NOT implement it, and do not add a separate "Results Dashboard" tab — see
"De-duplication (required)" below.

**`GET /api/records?entity_id=<id>`:** The constituent records of one entity

```json
{
  "entity_id": 1,
  "entity_name": "Robert Smith",
  "records": [
    {"data_source": "CUSTOMERS", "record_id": "1001", "name": "Robert Smith", "address": "123 Main St", "phone": "555-0100", "identifiers": {"SSN": "123-45-6789"}}
  ]
}
```

Backs the **Records** action everywhere an entity is shown (see "Per-entity actions" below),
including single-record entities — unlike `/api/merges`, which returns only multi-record entities.
Each record carries the same fields `/api/merges` uses: `data_source`, `record_id`, `name`,
`address`, `phone`, `identifiers`. On failure return `{"entity_id": <id>, "error": "<type>: <message>"}`
with HTTP 200, so one entity's failure never breaks the tab.

Unlike `why`/`how`, this endpoint's data MUST also be **embedded in the standalone snapshot**, so
the Records action works offline — it needs no engine call at view time, only the record data
already gathered when the model was built.

**`GET /api/overlap`:** Cross-source overlap matrix — how many resolved entities each pair of data
sources shares

```json
{
  "sources": ["CUSTOMERS", "REFERENCE", "WATCHLIST"],
  "matrix": [[395, 42, 12], [42, 210, 8], [12, 8, 95]],
  "cell_entities": {
    "0,1": [{"entity_id": 1, "entity_name": "Robert Smith", "record_count": 3}],
    "0,0": [{"entity_id": 7, "entity_name": "Alice Johnson", "record_count": 1}]
  },
  "cell_capped": false
}
```

`sources` is the sorted distinct data-source codes; `matrix` is a square `len(sources)` ×
`len(sources)` grid where `matrix[i][j]` (i≠j) is the number of resolved entities containing
records from **both** `sources[i]` and `sources[j]`, and the diagonal `matrix[i][i]` is the number
of entities present in `sources[i]`. Symmetric. Backs the **Cross-Source** heatmap tab (shown only
when `data_sources_total` ≥ 2).

`cell_entities` maps each cell to the entities it counts, keyed `"i,j"` with `i <= j` (the matrix is
symmetric, so store each pair once and have the client normalize the key). Each entry is
`{entity_id, entity_name, record_count}` — the same shape as `bucket_entities` on `/api/stats`, so
one drill-down renderer serves both. Implementations MAY cap each cell list (the reference caps at
200); `cell_capped` is true when any cell was capped, and the client MUST surface that so the cap is
never silent. `matrix` counts remain authoritative.

**`GET /api/matchkeys`:** Match-key frequency — which feature combinations drove resolutions

```json
{
  "match_keys": [{"match_key": "+NAME+ADDRESS", "count": 128}, {"match_key": "+NAME+DOB", "count": 74}],
  "distinct": 11,
  "capped": false,
  "match_key_entities": {
    "+NAME+ADDRESS": [{"entity_id": 1, "entity_name": "Robert Smith", "record_count": 3}]
  },
  "entities_capped": false
}
```

`match_keys` is the per-record match keys aggregated across all resolved entities, most frequent
first (the reference returns the top 20); `distinct` is the total number of distinct match keys and
`capped` is true when `distinct` exceeds the returned list length. Backs the **Match Keys** tab
(shown only when multi-record entities exist). Per-record match keys come from the entity's records
(the default entity flags' record-matching info); the seed record's match key is typically empty
and is excluded.

`match_key_entities` maps each returned match key to the entities carrying it, each
`{entity_id, entity_name, record_count}` — the same shape as `bucket_entities` and `cell_entities`,
so the one drill-down renderer serves all three. Implementations MAY cap each list (the reference
caps at 200); `entities_capped` is true when any list was capped and the client MUST surface it.
`count` remains authoritative.

**`GET /api/features`:** Feature-score distribution across a capped sample of multi-record entities

```json
{
  "features": [
    {"feature": "NAME", "buckets": {"SAME": 40, "CLOSE": 22, "LIKELY": 5}},
    {"feature": "DOB", "buckets": {"SAME": 30, "PLAUSIBLE": 3}}
  ],
  "sampled": 40,
  "multi_record_total": 87,
  "capped": true
}
```

`features` aggregates, per feature, the count of each Senzing score bucket (`SAME`, `CLOSE`,
`PLUS`, `LIKELY`, `PLAUSIBLE`, `UNLIKELY`, `NO_CHANCE`) observed by calling `why_records` over a
**capped** sample of multi-record entities (the reference caps at 40 to bound build cost). `sampled`
is the number of entities actually aggregated, `multi_record_total` the number available, and
`capped` is true when a cap was hit — the client MUST surface the sample size so the cap is never
silent. Computation is guarded: any `why_records` failure skips that entity and never blocks the
model or snapshot build (INV-077); when nothing could be sampled, `features` is `[]` and the tab is
hidden or shows a note. Backs the **Feature Scores** tab (shown only when multi-record entities
exist). Live-only: because it needs the engine, the static snapshot embeds whatever was computed at
build time (or an empty distribution).

**Where these surface in the UI (tabs).** The app is a **single consolidated, tabbed artifact** —
it is the one visualization Module 7 offers for results, so there are no separate static
visualization pages. Every tab is populated from the endpoints above; tabs whose data is absent are
not shown:

| Tab | Endpoint(s) | Shown when |
|-----|-------------|-----------|
| **Entity Graph** (default) | `/api/graph`, `/api/records`, `/api/why`, `/api/how` | always — force-directed graph of the entity population, with a **"Show only entities with relationships"** mode toggle (shown only when `relationships_total` > 0) that switches to the relationship subgraph with edges colored and dashed by `relationship_type` and a click-to-filter relationship legend; also the cross-source entity-relationship view (subsumes the former `multi_source_results.html`). **Above 400 entities that toggle defaults ON** — see "Defaults at production scale" below |
| **Merge Statistics** | `/api/stats`, `/api/records`, `/api/why`, `/api/how` | always — records-per-entity histogram (this **is** the entity-size distribution) with clickable bars drilling down via `bucket_entities`, plus the largest resolved entities from `sample_entities` |
| **Match Keys** | `/api/matchkeys`, `/api/records`, `/api/why`, `/api/how` | multi-record entities exist — clickable rows drilling down via `match_key_entities` |
| **Feature Scores** | `/api/features` | multi-record entities exist |
| **Cross-Source** | `/api/overlap`, `/api/records`, `/api/why`, `/api/how` | 2+ data sources (`data_sources_total` ≥ 2) — clickable cells drilling down via `cell_entities` |
| **Search / Probe** | `/api/search`, `/api/merges`, `/api/records`, `/api/why`, `/api/how` | always — with pre-verified example-query chips and a **"Show all merged entities"** button that lists every multi-record entity with no query (the one capability the former Record Merges tab uniquely had) |

**De-duplication (required).** Do NOT add a tab whose content is derivable from another tab's
endpoint. When two candidate tabs share their aggregates, **they are one tab.** Applying that test:

- The entity-size distribution is the **Merge Statistics** histogram — not a second tab.
- The cross-source entity-relationship view / former `multi_source_results.html` is the **Entity
  Graph** tab.
- There is **no "Results Dashboard" tab.** Its headline counts and histogram came from the same
  aggregates as `/api/stats`, and its only unique content — the largest resolved entities — is now
  `sample_entities` on that endpoint, rendered beneath the Merge Statistics histogram. Two tabs
  showing one histogram read as redundant, not complementary.
- There is **no "Relationship Network" tab.** This reverses an earlier ruling here that it *was*
  distinct: the related-entity subgraph is a filtered view of **Entity Graph's own** `/api/graph`
  data, so by this rule they are one tab. What made it look distinct — the relationship-type edge
  coloring/dashing and the click-to-filter legend — is preserved as Entity Graph's
  "Show only entities with relationships" mode, so nothing was lost by folding it in.
- There is **no "Record Merges" tab.** For any entity present in both, Search / Probe's per-entity
  result is a strict **superset**: Record Merges showed entity name, record count and one
  entity-level match key; Search / Probe shows all of that plus per-record match keys and feature
  scores. Its one unique capability was browsing *all* merged entities with no query, which is now
  the "Show all merged entities" button on that tab — so the removal is lossless rather than a
  trade. `/api/merges` is retained: the example-query chips and that button both read it.

### Defaults at production scale (required)

Every visual default here was chosen against the Truth Set's 84 entities, and Module 7 points this
same app at the bootcamper's own data — routinely thousands. Two defaults do **not** survive that
and are therefore contract, not implementation detail:

**1. Match-key labels must stay distinguishable.** Real match keys run to 70+ characters
(`+NAME+ADDRESS+NATIONAL_ID+OTHER_ID+REGISTRATION_DATE+REGISTRATION_COUNTRY+LEI_NUMBER`). A fixed
label gutter with right-anchored text pushes the **head** of each key off the left edge, so the
highest bars all render as the same trailing fragment and cannot be told apart — counts correct,
labels useless, chart looking fine. Required behavior:

- Size the label gutter from the longest key present, up to a cap, before truncating anything.
- **Middle-ellipsize** (`+NAME+ADDRESS+NATIONAL_ID+…RATION_COUNTRY+LEI_NUMBER`); never trim from the
  left. Right-truncation alone is **not** sufficient: match keys are `+A+B+C…` sequences that
  commonly share a long prefix and differ only in the final segment, so head-only truncation renders
  the top bars identically — the same unreadable chart, failing from the other end. Keeping both
  ends distinguishes keys that differ at either.
- Guarantee that **no two rendered labels are identical unless their keys are identical** — that is
  the testable property; the exact ellipsis strategy is not. Middle-ellipsis reduces collisions but
  does **not** guarantee this: two keys sharing a long head *and* a long tail, differing only in the
  elided middle, still render identically. So compare the fitted labels and disambiguate any that
  collide while their keys differ (the Python reference appends a positional suffix); the full key
  stays reachable on hover regardless.
- Expose the full, untruncated key on hover (`<title>` or equivalent), on both the bar and its label.

**2. The entity graph must open on something readable.** Hiding labels does not thin 4,464 edges;
at that density the graph conveys shape only, with no practical way to locate an entity. Required:
**above 400 entities, Entity Graph opens on the relationship subgraph** rather than the full
population, provided a subgraph exists (`relationships_total` > 0). The toggle still switches both
ways, a bootcamper's explicit choice is never overridden, and an inline note states both counts —
"Showing the N entities that have relationships, of M total" — for the same reason the label note
exists: otherwise a default reads as the data.

State the threshold as a number so every language implementation (INV-090) picks the same behavior.
Re-check these against the bootcamper's **actual** scale, not the Truth Set: both defects pass every
check 84 entities can run.

### Tab identifiers and deep-linking (required)

Tab ids are **contract**, not an implementation detail: the recap screenshot helper selects a tab by
id, so a server in any language (INV-090) must use these exact ids and expose the two hooks below.

**The row order below is also the order the app presents its tabs, left to right, and therefore the
order screenshots are embedded in the recap** — by `module-completion.md`'s capture step and by
graduation's orphaned-screenshot backfill alike. Both cite this table rather than restating the
list, so changing a tab's position here changes it everywhere. The recap is a walkthrough of the
app; images in capture or append order cannot be lined up against the interface.

| Tab | Id | Section id | Nav button id | Screenshot slug |
|---|---|---|---|---|
| Entity Graph | `graph` | `tab-graph` | `navbtn-graph` | `entity-graph` |
| Relationship Network — **REMOVED** | `network` | `tab-network` | `navbtn-network` | `relationship-network` |
| Record Merges — **REMOVED** | `merges` | `tab-merges` | `navbtn-merges` | `record-merges` |
| Merge Statistics | `stats` | `tab-stats` | `navbtn-stats` | `merge-statistics` |
| Match Keys | `matchkeys` | `tab-matchkeys` | `navbtn-matchkeys` | `match-keys` |
| Feature Scores | `features` | `tab-features` | `navbtn-features` | `feature-scores` |
| Cross-Source | `overlap` | `tab-overlap` | `navbtn-overlap` | `cross-source` |
| Search / Probe | `probe` | `tab-probe` | `navbtn-probe` | `search-probe` |

The two **REMOVED** rows are retained as reserved identifiers, not as tabs to build: a current app
MUST NOT serve them. They stay listed so the recap screenshot helper still recognizes them when
pointed at a snapshot saved by an earlier, eight-tab run, and so nothing reuses those ids for a
different view.

The app MUST provide:

- **`activate(<id>)`** — a page-scope function that shows that tab. The screenshot helper injects a
  call to it into a temp copy of the standalone snapshot (falling back to clicking
  `#navbtn-<id>`), which is how a tab is captured with no browser-automation dependency.
- **`?tab=<id>` / `?q=<text>` deep-linking** — applied at the end of `init()`, after the async
  data load and `buildNav()` have settled. `?tab=` activates that tab when it is applicable and
  present; `?q=` fills the search box and runs the search, defaulting the tab to `probe` when `q` is
  given without `tab`. This makes any view of the app a shareable URL, and it is what lets the live
  Search / Probe tab be captured showing **real results** rather than an empty box.

Deep-linking MUST be tolerant: an unknown or non-applicable `tab` value leaves the default tab
active rather than erroring or blanking the page.

Headline counts belong in the page-level summary strip and appear **once**. A tab MUST NOT repeat
them in its own summary sentence.

## Per-entity actions (required everywhere)

Every place an entity is shown with actions gets the **same three buttons, in this order — never a
subset**:

| Action | Calls | Shows |
|---|---|---|
| **Records** | `/api/records?entity_id=` | the entity's constituent records |
| **Why?** | `/api/why?entity_id=` | why the records resolved together |
| **How?** | `/api/how?entity_id=` | how the entity was constructed |

That set applies to: the Entity Graph node detail (in either mode), Record
Merges cards, the Merge Statistics bucket drill-down **and** its `sample_entities` list, the
Cross-Source cell drill-down, the Match Keys row drill-down, and Search / Probe results. Implement
it as **one shared renderer** invoked from every surface — the failure mode this prevents is real:
the buttons were added per-code-path, so each new entity surface silently shipped with a different
subset, and bootcampers reported the gaps one tab at a time.

**Drill-down on every aggregate view.** Every aggregate is clickable and opens the underlying
entities with the action set above: histogram bars (`bucket_entities`), Cross-Source cells
(`cell_entities`), Match Keys rows (`match_key_entities`). All three payloads share one entity
shape, so one drill-down renderer serves all three. An aggregate that shows a count but cannot be
opened is a dead end and is not acceptable.

**No redundant inline record listings.** Where an entity list offers the Records action, it MUST
NOT also print the constituent records inline. The "Show all merged entities" cards on Search /
Probe show entity name, record count,
and match key plus the actions — nothing more. Showing the same records twice is clutter, and it
reads as unfinished once "click Records to see records" is the established pattern everywhere else.

> ⚠️ **Implementation pitfall — `onclick` + JSON serialization.** When building `onclick="..."`
> attributes by string concatenation, never embed serialized-JSON output (which is double-quoted)
> inside a double-quoted HTML attribute: the browser truncates the attribute at the first embedded
> quote and the handler silently never fires. This bug is easy to miss because calling the same
> function directly from the browser console works fine, which masks the failure. Escape the payload
> for the attribute context, or attach handlers programmatically instead of inlining them. This is
> language-agnostic front-end JavaScript, not a quirk of any one implementation.

Each Search / Probe result — searched or listed via "Show all merged entities" — carries **Why?**
and **How?** actions that call
`/api/why` and `/api/how` and render the explanation (match keys, feature scores, construction
steps) in a modal.

## Rendering contract

These are requirements, not suggestions. This module is the bootcamp's "wow moment" — the surface
whose whole purpose is a strong first impression — so the quality bar below is the **default every
implementation ships**, not something a bootcamper has to ask for one improvement at a time.

### Escaping data-sourced strings (required — security)

⛔ **Every string that reaches the page from the loaded data MUST be escaped for the context it is
written into.** Entity names, data-source codes, record IDs, match keys, resolution rules and feature
descriptions all originate in the Bootcamper's records, so none of them can be treated as trusted
markup. This is a **stored** injection surface, not a reflected one: the standalone snapshot is
saved, kept, and shared, so anything injected persists in the artifact the Bootcamper hands to
someone else.

Two contexts, two rules:

1. **Values embedded in an inline `<script>` block** — the snapshot inlines the whole entity model
   this way. Serializing with your language's plain JSON writer is **not sufficient**: JSON does not
   escape `<`, so a value containing the literal `</script>` closes the script element early and the
   browser parses what follows as markup. Escape `<`, `>` and `&` as their `\uXXXX` JSON escapes
   (`\u003c`, `\u003e`, `\u0026`) after serializing. The result is still valid JSON and the parsed
   data is byte-identical, so nothing downstream changes.
2. **Values written into rendered HTML** — entity cards, tooltips, legends, table cells, modal
   bodies. Escape `&`, `<` and `>` (and quotes in attribute position) before insertion, or use an
   API that treats the value as text rather than markup.

Live `/api/*` responses served as `application/json` are **exempt** — they are not an HTML-embed
surface.

*Reference implementation (Python):* `senzing_viz_server.py` provides `_script_json()` for case 1 and
`_esc_html()` for case 2. Those are the names in the bundled reference, **not** the requirement —
implement the equivalent for your language (INV-090). A server that skips this ships a stored-XSS
vector in a shared keepsake, which is why it is a ⛔ and not a nicety (INV-106).

### Offline rendering (required)

The live page and the standalone snapshot MUST both render with **no network access**: inline the
vendored D3 asset rather than fetching from a CDN, and embed every payload the snapshot needs. A
snapshot that reaches for a CDN is broken in exactly the air-gapped and proxy-restricted settings
where it matters most (INV-091). See `phase1-visualization.md` → "Render offline" for the vendored
asset's location.

### Why? / How? — plain language first, raw JSON behind a twistie

The API returns the SDK response verbatim; that is about *availability*, not about what the UI
renders. Dumping `JSON.stringify` output into a `<pre>` block satisfies the letter of "verbatim"
and defeats the entire purpose of the feature, which exists to make Senzing's reasoning legible.

- **Why?** renders match level, match key, and resolution rule, then a per-feature table:
  feature · this record · compared-to record · score · bucket.
- **How?** renders a numbered, step-by-step merge narrative ("Step 1: record A from CUSTOMERS
  established the entity. Step 2: record B was added because …").
- **Score buckets render as color-coded badges**, mapped from the buckets this contract already
  enumerates for `/api/features`: `SAME`/`CLOSE` → positive, `PLUS`/`LIKELY`/`PLAUSIBLE` → caution,
  `UNLIKELY`/`NO_CHANCE` → negative. Use `brand_tokens`' `SIGNAL_GREEN` for the positive bucket —
  that is exactly its reserved "resolved state" meaning (INV-081) — and define the caution and
  negative colors **once, as named constants in one place**, since the brand palette deliberately
  does not supply status colors. Never scatter hex literals through the render code.
  **Never rely on color alone** — keep the bucket name as text, so the badge survives a monochrome
  recap screenshot and is readable without color vision.
- **The raw SDK response stays available but collapsed**, behind a `<details>`/twistie that is
  closed by default. Available on demand; never the default view.
- Parse these responses against `get_sdk_reference(topic='response_schemas')`, never from the
  illustrative payloads above (INV-115). A summary view makes a wrong field name *harder* to spot,
  because it becomes a blank cell rather than visibly-absent JSON.

### Modal chrome

Entity-detail dialogs (Records / Why? / How?) are a primary "wow moment" surface and get the same
visual care as the headline tabs: a real header bar (title plus a close control) visually separated
from the body, deliberate spacing and typographic hierarchy, and a subtle entrance transition.
Palette and type come from `scripts/brand_tokens.py` (INV-081) — the brand tokens apply *inside* the
modal, not only to the app shell. A functionally-correct but visually plain dialog undersells the
moment.

### Graph rendering — labels, scale, and legends

Applies to **Entity Graph** in both of its modes.

- **Independent label toggles.** Separate show/hide controls for **node** (entity name) labels and
  **edge** (match key / relationship type) labels. Two independent dials, not one combined control,
  so a bootcamper can declutter for an overview pass or drill into detail without switching tabs.
- **Scale-dependent defaults.** Label visibility defaults by graph size, not to a fixed value: both
  label sets default **off above ~150 nodes** and on below it. State the threshold in the
  implementation so every language build behaves the same.
- **Say why they started off.** When labels default off, show a short inline note ("Labels hidden —
  3,986 entities; use the toggles above to show them"). Without it, a label-less graph reads as
  broken rather than as a deliberate default.
- **Legible labels when shown.** On-canvas node labels MUST avoid unreadable overlap — a
  collision/overlap-avoidance pass, truncation, or zoom-gated labels. A hover-only tooltip does
  **not** satisfy this: the complaint it addresses is being unable to tell which records matched
  without hovering every node in turn.
- **Legends are generated FROM the data, and filter it.** Build each legend from the values actually
  present in the rendered set — the `relationship_type` values on the drawn edges, the data sources
  on the drawn nodes. A legend entry can then never exist without matching marks, which is what
  makes "the legend shows three colors that appear nowhere in the graph" structurally impossible.
  Clicking a legend entry filters the view to that type/source and toggles back; show the active
  filter state and a per-entry count. Pair color with a non-color distinction (e.g. line style per
  relationship type) so the encoding survives a monochrome screenshot.
- **Data-source colors are ASSIGNED FROM the sources present, never from a name-keyed palette.**
  Build the source→color map at model-build time from the data-source codes actually loaded. A map
  keyed by source *name* is not acceptable: the shipped palette names the Truth Set's sources
  (`CUSTOMERS`, `REFERENCE`, `WATCHLIST`), and **no bootcamper uses those names for their own data,
  by definition** — so a name-keyed lookup drops every real source to one identical fallback color
  and reduces the payoff module's centerpiece to a monochrome hairball. It fails silently: a graph
  renders, just uninformative, and a bootcamper who did not build the server cannot tell a bad
  default from genuinely unclustered data.

  Requirements: Truth Set names keep their preferred assignment (so the Truth Set view is
  unchanged); every other source takes the next unclaimed palette entry, so two sources never
  collide; assignment is **deterministic** (sort the codes) so a rebuilt snapshot or a re-captured
  screenshot still matches the recap prose describing it; when there are more sources than palette
  entries, vary a second visual channel (e.g. node stroke) rather than silently reusing a color; and
  the reserved signal green is never assigned as a categorical color. The Python reference implements
  this as `brand_tokens.color_for_sources()`.
- **Init-state note.** An unchecked toggle fires no change event, so apply its render state
  explicitly at load — do not rely on the event handler to establish the initial view.

> **Scale principle (general).** Any default chosen while developing against the Truth Set MUST be
> reviewed for its behavior at 100× scale. Module 7 reuses this same app over the bootcamper's real
> data (`../module-07-query-visualize-discover/phase1-query-visualize.md`), which is usually far
> larger — a default tuned to 84 entities produced an unreadable hairball at 3,986, in the module
> meant to showcase results, and the bootcamper cannot tell a bad default from bad data.

### Search / Probe — pre-verified example queries

The Search / Probe tab MUST ship a small set of example queries as clickable chips that both fill
the search box **and** run the search on click. They are generated per-dataset from the loaded data
and **verified live to return at least one match** before being offered — a hint that returns
nothing is worse than no hint. Never present a bare search box: a bootcamper exploring a Truth Set
they did not build has no idea what a good demo query looks like, and a failed first search is a
poor first impression of the product.

**Distinguish "no data returned" from "rendered empty" (INV-115).** Where the UI renders a parsed
field — a feature-score table, a match key, a resolution step — an absent or blank value MUST be
labeled as such ("no feature scores returned for this entity"), never rendered as an empty row,
empty cell, or bare punctuation. A wrong field name and genuinely empty data look identical
otherwise, and the wrong-field case is the far likelier of the two. This is what makes the failure
visible to whoever is looking at the screen; it is the defense that survives a future field rename,
and it matters more once a plain-language summary replaces the raw JSON, because a mis-named field
becomes a blank cell rather than visibly-absent JSON. The Merge Statistics histogram bars are clickable (driven by `bucket_entities`),
listing the entities in each bucket and linking each to its **How?** explanation.

**Static snapshot degradation:** the standalone snapshot has no live backend, so `why`/`how` and
live `search` are unavailable there — those actions show a note directing the viewer to the live
server. Everything else renders **offline** because the snapshot embeds `stats`, `graph`, `merges`,
`records`, `overlap`, `matchkeys`, and `features` — so the Entity Graph (both modes, since the
relationship subgraph is filtered from the same embedded `graph` payload), Merge Statistics (with
bucket drill-down and the largest-entities list), Match Keys (with row drill-down), Feature Scores,
and Cross-Source (with cell drill-down) tabs all work with no network access. `merges` stays embedded
because Search / Probe's "Show all merged entities" browse reads it, so **that browse works offline**
— which is what keeps the removed Record Merges tab's no-query capability available in the keepsake,
not only in the live app. The snapshot's Search / Probe body MUST therefore include the
`#probe-btns` container even though it has no live search box; without it the browse has nowhere to
render and the snapshot silently loses the capability. The example-query **chips** are live-only by
design — they drive the search box, which a static file does not have — so they are suppressed
there rather than shipped as dead controls. **The Records action works offline too**, because `records` is embedded: it needs no
engine call at view time, unlike `why`/`how`. The Feature Scores tab shows whatever was computed
(capped) at build time. (`dashboard` is no longer embedded — the endpoint was removed and its
content folded into `stats`.)

**Error response (all endpoints):** HTTP 500 with `{"error": "<description>"}` on SDK failure.
Exception: `why`/`how` return a `200` with an `error` field per the shapes above so one entity's
failure never breaks the tab.

## Server lifetime (required in every module that starts one)

⛔ **A visualization server, once started, stays up until the bootcamper has explicitly approved
teardown.** Agent-side verification — API probes, endpoint checks, screenshot capture for the recap
— is a *preliminary* step that runs **while the server keeps running**. It is never the end of the
interaction, and it MUST NOT stop the server. The bootcamper explores *after* the agent verifies,
not instead of it.

The sequence in every module that starts a server is therefore:

1. Start the server and verify it (agent-side; server stays up).
2. Hand the URL to the bootcamper and let them explore at their own pace.
3. Ask the teardown gate below, and only then clean up.

**The teardown gate.** Before stopping the server — and before any data purge that accompanies it —
ask a pinned question (INV-056) and end the turn on it. The gate MUST name **exactly** what is
about to happen in that module and nothing more, because the consequences differ:

- Where teardown stops the server **and** removes data (Truth Set visualization, whose records are
  scaffolding): say both. → 👉 **Ready for me to stop the visualization server and clean up the Truth Set data?**
- Where teardown stops **only** the server (any module pointed at the bootcamper's own loaded data):
  say only that, and say the data stays. → 👉 **Ready for me to stop the visualization server?**

⛔ Never ask a vague "and clean up" in a module that has no purge — the bootcamper's own loaded
data is needed downstream (recap, graduation), and a gate that sounds like it authorizes deleting it
either frightens them or licenses a destructive step the module never intended.

Tell the bootcamper what they are consenting to before they answer: the live URL goes dead, and the
standalone snapshot preserves every tab that renders from embedded data but **not** the live
`why`/`how`/`search` actions, which need the running engine (see "Static snapshot degradation"
above). A yes given without that is not an informed yes.

⛔ **This is not an INV-006 violation.** INV-006 forbids re-asking *the same* question. An earlier
"are you ready to continue?" or "done with the tour?" asks whether the bootcamper is ready to move
on in the module; this asks whether an **irreversible** action may proceed. They are different
questions with different consequences, and the second MUST be asked on its own. Never cite INV-006
as a reason to skip it.

**On "no" or "not yet":** acknowledge, leave the server running, and continue with whatever comes
next. Do not re-ask on a loop — INV-006 *does* apply to this gate — and proceed with teardown when
the bootcamper says they are done.

**Never design the flow so a restart request is the normal path.** Restarting on request is fine,
but a bootcamper should not have to ask for a server to come back that they never agreed to stop.
(This mirrors the Docker container lifecycle handling: containers are stopped, not removed, and are
surfaced on resume — the same principle that a bootcamper never loses access to something they were
using.)

## search_builder.py: Entity Enrichment Specification

The `search_builder.py` module SHALL implement the following enrichment behavior:

**Enrichment flow:**

1. Call `search_by_attributes` with the query parameters to get matching entities.
2. For each matched entity (up to a maximum of 10), call `get_entity_by_entity_id` to retrieve
   full resolution detail.
3. Extract match keys, feature scores, and resolution rules from the entity detail response.
4. Return enriched results combining basic search info with resolution reasoning.

**Enrichment cap:** enrichment is capped at 10 entities maximum. If a search returns more than 10
matching entities, only the first 10 are enriched with resolution detail. Remaining entities
(positions 11+) are returned as basic search results with null values for `match_keys`,
`feature_scores`, and `resolution_rules`.

**Extraction functions:**

| Function | Input | Output |
|----------|-------|--------|
| `_extract_match_keys(entity_detail)` | Full entity detail JSON | `{"entity_level": "+NAME+DOB", "per_record": ["+NAME+DOB", "+PHONE"]}`: entity-level match key string + list of per-record match key strings |
| `_extract_feature_scores(search_match_info)` | Search match comparison info | `[{"feature": "NAME", "score": 97, "label": "CLOSE"}, ...]`: feature name, numeric percentage (0-100), classification label |
| `_extract_resolution_rules(entity_detail)` | Full entity detail JSON | `[{"data_source": "CUSTOMERS", "record_id": "1001", "rule": "CNAME_CFF_CEXCL"}, ...]`: per-record data source, record ID, and resolution rule string |

**Graceful degradation:** if `get_entity_by_entity_id` raises any exception for a specific
entity, the search builder SHALL return the basic search result for that entity with:

- `match_keys`: null
- `feature_scores`: null
- `resolution_rules`: null
- `enrichment_error`: a non-empty string containing the exception type and message (e.g.,
  `"SzError: Entity 5 not found in repository"`)

One entity's enrichment failure SHALL NOT prevent enrichment of the remaining entities.
