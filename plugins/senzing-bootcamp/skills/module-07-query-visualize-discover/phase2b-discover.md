# Module 7, Phase 2b: Discover, Part B (steps 4d–4e)

Follow the ground rules. `🛑`/`⛔` are internal directives, never render them; signal a stop by
ending the turn on the single 👉 question and waiting. On load, read
`config/bootcamp_progress.json` and check which 4x sub-steps are already checkpointed under
`module_7_query.steps`. Resume from the first incomplete step; do not re-run completed
demonstrations.

Load this file after completing steps 4a–4c in `phase2-discover.md`. When complete, return to
`phase1-query-visualize.md` for the Query Completeness Gate.

**No direct SQL and no fabricated methods (see SKILL.md):** `find_network` and `find_path` are
SDK methods, not MCP tools. Generate the SDK code, sourcing flags and signatures from
`get_sdk_reference` and network/path patterns from `reporting_guide(topic='graph', ...)`. Never
query `database/G2C.db` tables directly.

## Steps 4d–4e: Discover (continued)

### Step 4d: Relationship network exploration

Demonstrate relationship-network exploration using entities identified in step 4a that have
disclosed relationships or shared attributes. This teaches the bootcamper how to explore
connections between entities using `find_network` and `find_path`.

1. **Entity selection:** use entities from step 4a with disclosed relationships or shared
   attributes. State which and why: "I'll use Entities [ID1], [ID2], and [ID3], which have
   disclosed relationships or shared attributes. These give us a connected set of entities to
   explore as a network."
2. **Flag lookup:** before generating the `find_network` or `find_path` calls, look up available
   flags:
   - `get_sdk_reference(method='find_network', topic='flags')` for network exploration.
   - `get_sdk_reference(method='find_path', topic='flags')` for path finding.

   Select flags appropriate for relationship exploration and explain each: "I'm using [flag] so
   we can see [what it provides]." For example: "I'm using [relationship detail flag] so we can
   see the full attribute information for each entity in the network. This helps us understand
   what connects them."
3. **find_network demonstration:** call `find_network` with a set of related entity IDs (at
   least 2–3 entities from the relationship clusters in step 4a). Present the resulting network
   structure:
   - **Which entities are connected:** list each entity and its connections, with entity IDs
     and brief identifying information (name, data source).
   - **What attributes they share:** for each connection, explain the common attributes , 
     shared addresses, phone numbers, names, or other features that create the link.
   - **Degrees of separation:** show how many hops separate each pair. "Entity A is directly
     connected to Entity B (1 degree), and Entity B connects to Entity C (so A and C are 2
     degrees apart)."

   Present this as a clear textual network diagram or structured list so the bootcamper can
   follow the connections.
4. **find_path demonstration:** demonstrate `find_path` between two indirectly connected
   entities (2+ degrees of separation if available). Show the shortest path of relationships:
   - State which two entities and why: "Let's find the shortest path between Entity [ID1] and
     Entity [ID2]. These aren't directly connected, so we'll see the intermediate entities
     that link them."
   - Present each step in the path: Entity A → Entity B → Entity C, with the connecting
     attributes at each hop.
   - Explain what the path reveals about the relationship between the two endpoints.
5. **Network structure explanation:**
   - **How entities connect through shared attributes:** "Entities in Senzing connect through
     shared features, when two entities share an address, phone number, or other attribute,
     that creates a relationship link between them."
   - **What relationship types mean:** explain disclosed relationships (explicitly stated in
     source data, like 'spouse' or 'employer') versus discovered relationships (inferred from
     shared attributes like a common address).
   - **How to interpret degrees of separation:** "Degrees of separation tell you how many
     entity-to-entity hops connect two entities. Direct connections are 1 degree; connections
     through an intermediary are 2 degrees, and so on."
6. **Practical use cases:**
   - **Fraud ring detection:** "find_network reveals clusters of connected entities that share
     attributes. This is how investigators discover fraud rings where multiple identities
     share addresses, phones, or other features."
   - **Supply chain analysis:** "Tracing entity connections helps identify hidden relationships
     between suppliers, intermediaries, and end customers in complex supply chains."
   - **Beneficial ownership tracing:** "find_path can trace the chain of relationships from a
     company to its ultimate beneficial owners through intermediate entities."
   - **Customer household grouping:** "find_network identifies entities that share a household
     address, helping group related customers for marketing or risk assessment."
7. **Graceful fallback (no relationships in data):** if the bootcamper's data contains no entity
   relationships or disclosed connections (as determined in step 4a), do NOT attempt the live
   demonstration. Instead:
   - State: "Your data doesn't contain disclosed relationships, so I'll explain what this would
     look like with connected data."
   - Describe what `find_network` returns when entities are connected: a graph structure with
     entity nodes, relationship edges, shared attributes at each connection, and degrees of
     separation.
   - Describe what `find_path` returns: an ordered list of entities forming the shortest path
     between two endpoints, with the connecting attributes at each hop.
   - Explain the SDK methods conceptually so the bootcamper understands how to use them with
     relationship-rich data.
   - Write step 4d status as `"skipped"` with reason `"no_relationships"` in the checkpoint.
8. **Transition:**

   👉 **Would you like to continue to the next demonstration (Visualization Suggestions, data-specific analytical views), or proceed to module completion?**

   *(Internal: end the turn on this question and wait.)* If the bootcamper chooses to exit,
   write `discover_phase: "skipped"` to `config/bootcamp_progress.json` and return to
   `phase1-query-visualize.md` for the Query Completeness Gate.

**Checkpoint:** write step 4d under `module_7_query.steps.4d`:

- If relationships were demonstrated: `{"status": "completed"}`.
- If no relationships exist in data: `{"status": "skipped", "reason": "no_relationships"}`.

Include the `reason` field only when the step is skipped. Also set top-level `current_step` to
`"4d"`.

### Step 4e: Data-specific visualization suggestions

Suggest at least two visualizations tailored to the bootcamper's data structure and resolution
results. Select from the catalog below based on what was found in step 4a.

1. **Visualization catalog, select based on the bootcamper's data:**
   - **Cross-source overlap heatmap**: suggest when 2+ data sources are loaded. Reveals which
     sources share the most resolved entities. Framing: "Since you have records from [Source A]
     and [Source B], a cross-source overlap heatmap would show which sources share the most
     resolved entities, helping you see where your data sources agree."
   - **Entity size distribution chart**: suggest for any data. Shows records per entity
     (singletons vs. small merges vs. large merges). Framing: "An entity size distribution
     chart would show how your records clustered, how many entities are singletons versus
     multi-record merges."
   - **Relationship network graph**: suggest when relationships exist (from step 4a). Shows how
     entities connect through shared attributes. Framing: "Since your data has relationship
     clusters, a network graph would visualize how entities connect through shared attributes."
   - **Match key frequency analysis**: suggest when multi-record entities exist. Shows which
     feature combinations (match keys) drive the most resolutions. Framing: "A match key
     frequency chart would show which feature combinations, like NAME+ADDRESS or NAME+DOB , 
     are driving the most resolutions in your data."
   - **Feature score distribution**: suggest when multi-record entities exist. Shows how
     closely features match across resolved records. Framing: "A feature score distribution
     would show how tightly your resolved records match, whether most merges are near-exact or
     fuzzy matches."
2. **Selection logic:** select at least 2 visualizations relevant to the bootcamper's specific
   data structure based on the patterns found in step 4a. Do not suggest visualizations that
   require data patterns not present:
   - No cross-source heatmap if only one data source is loaded.
   - No relationship network graph if no relationships were found in step 4a.
   - No match key frequency or feature score distribution if no multi-record entities exist.
   - The entity size distribution chart is always applicable.
3. **Relevance explanation:** for each suggested visualization, explain concretely what it would
   reveal about the bootcamper's specific data. Reference their actual data sources, entity
   counts, and step-4a patterns. Be specific, not generic: "Since you have 5 cross-source
   entities spanning CUSTOMERS and WATCHLIST, a cross-source overlap heatmap would show exactly
   how much overlap exists between those two sources."
4. **Generation:** when the bootcamper selects a visualization, generate it in their chosen
   language. Source the underlying data via `reporting_guide(topic='dashboard', ...)` and
   `reporting_guide(topic='graph', ...)` (never direct SQL), and generate working rendering code
   that queries the bootcamper's actual data. (The Kiro `visualization-guide.md`: code
   structure, charting-library selection, output format, is a later porting phase; until then,
   use the reporting_guide patterns and keep all code and output inside the working directory.)
5. **Handle decline:** if the bootcamper declines all suggestions, acknowledge gracefully and
   proceed to the module completion gate. Do not push or re-offer after a decline.
6. **Transition:** after visualization generation (or decline), return to
   `phase1-query-visualize.md` for the Query Completeness Gate.

**Checkpoint:** write step 4e under `module_7_query.steps.4e`:

- If visualizations were offered:
  `{"status": "completed", "visualizations_offered": N}` where N is the number suggested.
- If the step was skipped: `{"status": "skipped", "visualizations_offered": 0}`.

Also set top-level `current_step` to `"4e"`.

### Discover phase completion

After step 4e is complete (or after any early exit), update the top-level `discover_phase`
status in `config/bootcamp_progress.json` under `module_7_query`:

- Set `"discover_phase": "completed"` when all steps 4a–4e have been checkpointed (whether
  completed or individually skipped due to data limitations).
- Set `"discover_phase": "skipped"` when the bootcamper declines the Discover phase at the
  opt-in prompt or exits early at any transition point.

The full checkpoint structure in `config/bootcamp_progress.json` is:

```json
{
  "module_7_query": {
    "steps": {
      "4a": {"status": "completed", "patterns_found": {"multi_record": 5, "cross_source": 3, "relationships": 2}},
      "4b": {"status": "completed", "entity_demonstrated": 1234},
      "4c": {"status": "completed", "entity_demonstrated": 5678},
      "4d": {"status": "completed"},
      "4e": {"status": "completed", "visualizations_offered": 2}
    },
    "discover_phase": "completed"
  }
}
```

After updating the `discover_phase` status, return to `phase1-query-visualize.md` for the Query
Completeness Gate.

**Success:** Discover phase completed (or explicitly skipped), data patterns analyzed, why/how
analysis demonstrated, relationship networks explored, and visualization suggestions offered.
