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
  }
}
```

Required fields: `records_total`, `entities_total`, `multi_record_entities`,
`cross_source_entities`, `relationships_total`, `data_sources_total`, `histogram`,
`bucket_entities`. The `histogram`
maps record-count buckets (1, 2, 3, 4+) to entity counts; `bucket_entities` maps the same buckets
to the entities in each (each `{entity_id, entity_name, record_count}`) so the histogram bars are
clickable and drill down to the entities in a bucket. Implementations MAY cap each bucket list
(the reference caps at 200 per bucket); the `histogram` counts remain authoritative.
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

> `source_entity_id`/`target_entity_id` are the unchanged API contract; mapping to D3's
> `source`/`target` is a client-side concern handled in `drawGraph` (see the edge-mapping
> requirement in Step 2 of `phase1-visualization.md`).

**Edge discovery.** The example JSON above shows the edge shape only; it does not imply edges come
from a default export. `graph_builder.py` SHALL discover relationships explicitly (a plain
`export_json_entity_report` does not include relationship data by default, so reading
`RELATED_ENTITIES` from it yields an empty `edges` array). Obtain relationships using either or
both of:

- **`find_network_by_entity_id`:** for multi-record/related entities, call
  `find_network_by_entity_id` to retrieve the relationship network and derive edges from the
  returned links.
- **Relationship-inclusion export flag:** request the entity export/report with the flag that
  includes all relations (`SZ_ENTITY_INCLUDE_ALL_RELATIONS`, confirmed via the Senzing MCP
  server) so `RELATED_ENTITIES` is populated, then build edges from it.

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

**`GET /api/why?entity_id=<id>`:** Explain WHY the records in an entity resolved together

Backed by `why_records` (comparing two of the entity's constituent records) or, for a
single-record entity, `why_record_in_entity`. Use the `SZ_WHY_RECORDS_DEFAULT_FLAGS` /
`SZ_WHY_RECORD_IN_ENTITY_DEFAULT_FLAGS` group (these include `SZ_INCLUDE_FEATURE_SCORES`; add
`SZ_INCLUDE_MATCH_KEY_DETAILS` for match-key breakdowns) — confirm exact method/flag names via the
Senzing MCP server (`get_sdk_reference`).

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

**`GET /api/dashboard`:** Results-dashboard payload — headline counts, the records-per-entity
histogram, and a sample of the largest resolved entities

```json
{
  "counts": {
    "records_total": 510, "entities_total": 395, "multi_record_entities": 87,
    "cross_source_entities": 42, "relationships_total": 156
  },
  "histogram": {"1": 308, "2": 65, "3": 17, "4+": 5},
  "sample_entities": [
    {"entity_id": 1, "entity_name": "Robert Smith", "record_count": 3, "data_sources": ["CUSTOMERS", "REFERENCE"]}
  ]
}
```

`counts` and `histogram` are drawn from the same aggregates as `/api/stats`; `sample_entities` is
the multi-record entities in descending record-count order (the reference caps the list at 10),
each `{entity_id, entity_name, record_count, data_sources}`. Backs the **Results Dashboard** tab.

**`GET /api/overlap`:** Cross-source overlap matrix — how many resolved entities each pair of data
sources shares

```json
{
  "sources": ["CUSTOMERS", "REFERENCE", "WATCHLIST"],
  "matrix": [[395, 42, 12], [42, 210, 8], [12, 8, 95]]
}
```

`sources` is the sorted distinct data-source codes; `matrix` is a square `len(sources)` ×
`len(sources)` grid where `matrix[i][j]` (i≠j) is the number of resolved entities containing
records from **both** `sources[i]` and `sources[j]`, and the diagonal `matrix[i][i]` is the number
of entities present in `sources[i]`. Symmetric. Backs the **Cross-Source** heatmap tab (shown only
when `data_sources_total` ≥ 2).

**`GET /api/matchkeys`:** Match-key frequency — which feature combinations drove resolutions

```json
{
  "match_keys": [{"match_key": "+NAME+ADDRESS", "count": 128}, {"match_key": "+NAME+DOB", "count": 74}],
  "distinct": 11,
  "capped": false
}
```

`match_keys` is the per-record match keys aggregated across all resolved entities, most frequent
first (the reference returns the top 20); `distinct` is the total number of distinct match keys and
`capped` is true when `distinct` exceeds the returned list length. Backs the **Match Keys** tab
(shown only when multi-record entities exist). Per-record match keys come from the entity's records
(the default entity flags' record-matching info); the seed record's match key is typically empty
and is excluded.

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
| **Entity Graph** (default) | `/api/graph` | always — force-directed graph of the full entity population; also the cross-source entity-relationship view (subsumes the former `multi_source_results.html`) |
| **Relationship Network** | `/api/graph` | relationships exist (`relationships_total` > 0) — the subgraph of entities connected by relationships, edges colored by relationship type |
| **Record Merges** | `/api/merges`, `/api/why`, `/api/how` | always — cards with **Why?**/**How?** actions |
| **Merge Statistics** | `/api/stats` | always — records-per-entity histogram; this **is** the entity-size distribution (clickable bars drill down via `bucket_entities`, each linking to **How?**) |
| **Match Keys** | `/api/matchkeys` | multi-record entities exist |
| **Feature Scores** | `/api/features` | multi-record entities exist |
| **Cross-Source** | `/api/overlap` | 2+ data sources (`data_sources_total` ≥ 2) |
| **Results Dashboard** | `/api/dashboard` | always |
| **Search / Probe** | `/api/search`, `/api/why`, `/api/how` | always |

**De-duplication (required).** Do NOT add redundant tabs: the entity-size distribution is the
**Merge Statistics** histogram, and the cross-source entity-relationship view / former
`multi_source_results.html` is the **Entity Graph** tab. The **Relationship Network** tab is
distinct (the related-entity subgraph emphasizing relationship type), not a second full-population
graph.

The Record Merges tab and each Search / Probe result carry **Why?** and **How?** actions that call
`/api/why` and `/api/how` and render the explanation (match keys, feature scores, construction
steps) in a modal. The Merge Statistics histogram bars are clickable (driven by `bucket_entities`),
listing the entities in each bucket and linking each to its **How?** explanation.

**Static snapshot degradation:** the standalone snapshot has no live backend, so `why`/`how` and
live `search` are unavailable there — those actions show a note directing the viewer to the live
server. Everything else renders **offline** because the snapshot embeds `stats`, `graph`, `merges`,
`dashboard`, `overlap`, `matchkeys`, and `features` — so the Entity Graph, Relationship Network,
Merge Statistics (with bucket drill-down), Match Keys, Feature Scores, Cross-Source, and Results
Dashboard tabs all work with no network access. The Feature Scores tab shows whatever was computed
(capped) at build time.

**Error response (all endpoints):** HTTP 500 with `{"error": "<description>"}` on SDK failure.
Exception: `why`/`how` return a `200` with an `error` field per the shapes above so one entity's
failure never breaks the tab.

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
