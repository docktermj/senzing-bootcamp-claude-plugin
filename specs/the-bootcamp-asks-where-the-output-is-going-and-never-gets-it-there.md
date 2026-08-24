# The bootcamp asks the Bootcamper which downstream systems the output feeds, records the answer under an invariant, and never produces an artifact any of them can consume

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

A Bootcamper loaded the bootcamp's ER output into their graph platform and got **disconnected nodes
with none of their business attributes**. In their words:

> "as I load the Senzing ER output into Neo4j DB and GDS … yet, the output only show bubbles without
> any network and relationship, and upon checking the output file, for some reason the mule accounts,
> off-ramps, dormant account, from sender to target, amounts, are not there."

They then obtained a working result **by going outside the bootcamp**, and presented it to a C-suite
audience. So the bootcamp's final artifact was not the one that did the job.

⛔ **Their diagnosis names a step the bootcamp does not have, and that is itself the finding.** They
attribute it to "the Enrichment steps in the bootcamp wasn't enforced". There is no Enrichment step.
A repository-wide search finds `enrich` only in Module 3b's `search_builder.py` specification
(`visualization-api-reference.md:1157-1191`), which enriches *search results* with resolution
reasoning for the viz app's Search panel — unrelated to AML, to post-mapping, or to export. `Neo4j`,
`Memgraph`, `GDS`, `GraphXR` and `graph database` have **zero** occurrences anywhere in the plugin.

A competent Bootcamper assumed a step existed that would prepare the output for the target they had
already been asked about. Understanding *why* they assumed that is the whole spec.

## Root cause

**Module 1 asks where the output is going. Nothing ever takes it there.**

`module-01-business-problem/phase2-document-confirm.md:66-111`, Step 10a, asks for the Bootcamper's
downstream systems and holds `integration_targets` — governed by **INV-097**. The answer is written
into `config/bootcamp_preferences.yaml`, rendered into the business-problem document under
*"Downstream systems / Integration method / Systems mentioned"* (`:154`), used to shape a
`search_docs` lookup (`:215`), and read again at graduation
(`graduation/SKILL.md:167`, `:179-183`, `:202`).

Then graduation's `production/` project copies (`graduation/SKILL.md:804-808`):

| Source | Destination |
|---|---|
| `src/transform/**` | `production/src/transform/` |
| `src/load/**` | `production/src/load/` |
| `src/query/**` | `production/src/query/` |
| `data/senzing-ready/**` | `production/data/senzing-ready/` |

Code, and the **input** data. Not the resolved output, and nothing shaped for any
`integration_target`. The loop the bootcamp opens in Module 1 has no closing end, and a Bootcamper who
answered "Neo4j" in Module 1 and saw it echoed in their own documents has every reason to expect one.

### Three mechanisms produce exactly what they saw — all re-verified on server 1.33.0, 2026-08-21

**1. No edges: `RELATED_ENTITIES` is flag-conditional.** A naive export built from
`SZ_ENTITY_INCLUDE_*` members returns rows with **no `RELATED_ENTITIES` key at all** — entities with
no relationships, which renders as "bubbles". The plugin already documents this precisely, at
`module-06-data-processing/phaseD-validation.md:246-267`, including a live confirmation that
`SZ_EXPORT_DEFAULT_FLAGS` yields top-level keys `[RESOLVED_ENTITY, RELATED_ENTITIES]` while an
`SZ_ENTITY_INCLUDE_*`-composed flag set yields no `RELATED_ENTITIES` key. **That guidance is scoped to
the bootcamp's own match-key audit** and is never applied to an artifact leaving the project.
`reporting_guide(topic='graph')` corroborates the shape at the source: its `find_network` snippet now
names *"ENTITY_PATHS holds the seed-to-seed paths; ENTITY_NETWORK_LINKS holds the edges"*.

**2. No business attributes: the raw record JSON is `get_record`-only.**
`get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_RECORD_JSON_DATA')` reports
`applies_to: ["get_record"]`, and its `response_paths` include — literally —
**`JSON_DATA.AMOUNT`** and **`JSON_DATA.STATUS`**, alongside `JSON_DATA.RECORD_TYPE` and the
name/address/phone paths. Payload attributes live in the record JSON, and **the record JSON is not in
an entity-level export or a `get_entity_*` response at all.** This is the best explanation for
"amounts … are not there": amounts and account-role labels (mule, off-ramp, dormant) are payload, and
no export flag brings payload back — only a per-record `get_record` pass does. The plugin knows the
`get_record`-only fact and records it as a *rendering caveat for the discover step*
(`module-07-query-visualize-discover/phase2b-discover.md:98`), not as the reason a downstream export
is empty of business data.

**3. Candidate, unconfirmed: disclosed relationships may not have linked.** The same Bootcamper's
earlier entry records that this run's `embedded_master` used `record_id_source: RECORD_HASH`, making
REL_* keys derived hashes (see
`specs/rel-key-attributes-fail-the-verbatim-gate-too-whenever-record-id-is-a-hash.md`). If a
`REL_POINTER_KEY` hash does not match the `REL_ANCHOR_KEY` hash on its target, the disclosed
relationship resolves to nothing and the sender-to-target edges never exist in the engine — a
different cause with the same symptom as mechanism 1. ⚠️ **This is a hypothesis, not a finding.**
Settling it needs their `mapping_spec.json` and one exported row, neither of which was available at
triage; do not write it into shipped prose as established.

⚠️ **Which mechanism actually hit them is undetermined.** All three are consistent with the report and
they are not mutually exclusive. The remedy below does not depend on picking one — it makes all three
visible and verifiable — but the spec must not claim their specific cause was diagnosed.

### What Senzing owns, and what it does not

`reporting_guide(topic='graph')` owns the export patterns (`find_network`, `find_path`,
`export_json_entity_report`) and states the relevant anti-pattern: *"Export only Senzing
relationships with match type and match key as edge properties. Feature-level edges create noise and
massive graph bloat."* `reporting_guide(topic='data_mart')` owns the analytical schema, and
`topic='graph')`'s visualization entry names `sz_dm_relation` as the edge source. So **the server owns
the format and the bootcamp must delegate to it (INV-080)** rather than inventing an export shape.

What the server does **not** ship is a worked graph-database example.
`find_examples(query='export entities and relationships to graph database neo4j cypher')` across 45
indexed repositories returns no Neo4j/Memgraph example — the nearest are `senzing/elasticsearch` (a
different downstream sink) and `brianmacy/sz_spark`, whose tutorial describes replicating resolved
entities to *"a serving store, a warehouse, a graph"* via the `WITH_INFO` affected-entity feed.
`owner-checked: reporting_guide(topic='graph') and topic='data_mart' — the routes that own export and
schema patterns for graph consumption; they return the SDK patterns, the edge-property anti-pattern
and the sz_dm_relation edge source, but no graph-database-specific worked example, which find_examples
across 45 repos also does not carry.` So the *format* is delegable; the *handoff step* is ours.

## Proposed change

1. **Add an output-handoff step keyed to `integration_targets`.** Where Module 1 recorded downstream
   systems, produce an export the Bootcamper can actually load: entities, the relationships between
   them, and the payload attributes their use case needs. Where `integration_targets` is empty, offer
   it rather than skipping silently — a Bootcamper who said "none" in Module 1 may still want the
   artifact. Module 7 (after the discover phase, where the query programs already exist) or graduation
   (where `production/` is assembled) are the two candidate homes; graduation is the better fit if the
   artifact belongs in `production/`, Module 7 if it is part of the learning arc. **Pick one at
   implementation time and say why.**

2. **Take the export shape from the server, not from this spec (INV-080).** Call
   `reporting_guide(topic='graph', language=<chosen>)` and `topic='data_mart'` at the step, and follow
   the edge-property anti-pattern (Senzing relationships as edges with match type and match key —
   never feature-level edges). Do not hardcode a Cypher or CSV schema into the plugin; relay what the
   server returns.

3. **Make the two silent-blank traps explicit at the point of export, because both fail without an
   error.**
   - Start from `SZ_EXPORT_DEFAULT_FLAGS`, **dump one row, and read its top-level keys** before
     writing the reader — the procedure `phaseD-validation.md:265-267` already prescribes for the
     internal audit, applied here.
   - State that payload attributes require a per-record `get_record` pass because
     `SZ_ENTITY_INCLUDE_RECORD_JSON_DATA` is `get_record`-only, so an entity-level export **cannot**
     carry them however the flags are set. This is the half a Bootcamper cannot discover by adding
     flags, and it is the one that cost this report.

4. **Verify the artifact before handing it over, and report the counts.** Edges and payload-bearing
   nodes are both zero-by-default failure modes that produce a valid file, so the step must assert
   what it produced: entity count, edge count, and how many nodes carry the payload attributes the
   Bootcamper asked for. A zero edge count must be reported as a failure, not written out silently
   (INV-179's silent-blank shape — the same class as rendering a blank field as a result).

5. **Correct the expectation in the text, so the next Bootcamper does not infer a step that is not
   there.** Say plainly what the bootcamp does and does not produce for downstream systems. If the
   handoff step lands, Module 1 Step 10a should name it, so the question and its consequence sit
   together.

⛔ **Do not add an "Enrichment" step or adopt that name.** No such step exists, the sender's use of the
term describes work they did outside the bootcamp, and naming a new step after a misdiagnosis would
make the confusion permanent. Name it for what it does — the output handoff.

## Acceptance criteria

- [ ] A step produces an export for the recorded `integration_targets`, offered rather than skipped
      when the list is empty, and its home (Module 7 or graduation) is chosen with a stated reason.
- [ ] The export shape comes from `reporting_guide(topic='graph')` / `topic='data_mart'` at runtime;
      no Cypher, CSV or property-graph schema is hardcoded in the plugin.
- [ ] The step dumps one export row and reads its top-level keys before writing a reader, and says
      what to do when `RELATED_ENTITIES` is absent.
- [ ] The step states that payload attributes need a per-record `get_record` pass, because
      `SZ_ENTITY_INCLUDE_RECORD_JSON_DATA` is `get_record`-only — re-verified live at implementation
      time, not carried from this spec.
- [ ] The step reports entity count, edge count, and payload-bearing node count, and treats a zero
      edge count as a failure rather than writing the file silently.
- [ ] Shipped text states what the bootcamp does and does not produce for downstream systems, and
      contains no step named "Enrichment".
- [ ] Verified end to end on a source with disclosed relationships and payload attributes: the export
      loads into a property-graph tool with non-zero edges and the payload attributes present. This
      requires a live engine and is stated as such rather than asserted by the offline suite.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the export
      is written in the Bootcamper's chosen language (INV-090), and no graph vendor's tooling is a
      prerequisite for producing the file.

## Open questions for implementation

- **Which artifact shape?** A property-graph pair (nodes + edges files) is the most portable and loads
  into Neo4j, Memgraph and GraphXR alike; a vendor-specific loader script is friendlier and narrower.
  The `integration_targets` value should drive this, and the server's guidance should decide the
  format.
- **The pptx was referenced and never received.** It is the sender's picture of a correct result and
  would define what the artifact must contain. Ask for it before finalizing the acceptance criteria —
  writing them without it risks building something that again is not the thing that did the job.
- **Does this expand the bootcamp's scope past its stated boundary?** Modules 8–11 do not exist
  (`specs/advanced-modules-8-11-scope.md`, implemented), so there is no advanced tier to defer this
  to; it lands in the core path or not at all. A maintainer scope call, recorded either way.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/` or
  `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the new handoff step, per the choice in
  change 1
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the `production/` copy table (`:804-808`),
  if the artifact belongs there
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — Step 10a
  (`:66-111`) names where the answer is acted on
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — reference only;
  `:246-267` is the dump-one-row procedure to reuse
- `tests/` — coverage for the count reporting and the zero-edge failure path

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Matthew_email.md` → "Improvement: the ER output loaded
  into a graph database shows nodes with no edges and none of the AML attributes" (2026-08-21,
  Module Query, Visualize and Discover / graduation; `Source: bootcamper-reported`). Arrived by email
  rather than through the capture flow; the entry quotes the message verbatim.
- Priority: pending — the Bootcamper did not set one. Impact argues High (the bootcamp's final artifact
  was unusable for its stated purpose); scope argues this is a feature the bootcamp never claimed.
  Maintainer's call.
- MCP re-check: server 1.33.0, 2026-08-21 — **still reproduces** as a gap, and two of the three
  mechanisms are confirmed server-side.
  `get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_RECORD_JSON_DATA')` returns
  `applies_to: ["get_record"]` with `response_paths` including `JSON_DATA.AMOUNT` and
  `JSON_DATA.STATUS`; `reporting_guide(topic='graph', language='python')` returns the export patterns
  and the edge-property anti-pattern and names `ENTITY_PATHS` / `ENTITY_NETWORK_LINKS`;
  `get_sdk_reference(topic='response_schemas', filter='find_network_by_entity_id')` confirms the link
  and path structures. For the missing worked example:
  `owner-checked: reporting_guide(topic='graph') and topic='data_mart' — the routes that own graph
  export and analytical schema; they return SDK patterns, the edge-property anti-pattern and the
  sz_dm_relation edge source but no graph-database worked example, and find_examples across 45
  indexed repositories returns none either (nearest: senzing/elasticsearch, brianmacy/sz_spark).`
  The third mechanism (REL_* hash keys failing to link) is a hypothesis and is marked as such.
- Upstream: not applicable — the format guidance exists and is correct; the missing handoff is the
  plugin's. A feature request that Senzing add a graph-database worked example is defensible and was
  **not** filed; raise it separately if wanted.
- Related specs: `specs/export-related-entities-is-flag-conditional.md`,
  `specs/method-default-flags-omit-record-data.md`,
  `specs/match-key-audit-cannot-read-related-entities-from-export.md`,
  `specs/relay-the-default-flags-production-caution.md`,
  `specs/rel-key-attributes-fail-the-verbatim-gate-too-whenever-record-id-is-a-hash.md`,
  `specs/graduation-reads-integration-and-deployment-answers.md`,
  `specs/relocate-integration-deployment-questions-to-module1.md`,
  `specs/advanced-modules-8-11-scope.md`
