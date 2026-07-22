# Module 7, Phase 2b: Discover, Part B (step 4d)

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

## Step 4d: Discover (continued)

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
8. **Transition:** relationship-network exploration is the final Discover demonstration. After
   presenting it (or the fallback above), end the turn on this single question:

   👉 **Would you like to wrap up the Discover phase and continue to module completion?**

   *(Internal: end the turn on this question and wait.)* The Discover phase is complete either
   way — proceed to Discover phase completion below, then return to `phase1-query-visualize.md`
   for the Query Completeness Gate.

**Checkpoint:** write step 4d under `module_7_query.steps.4d`:

- If relationships were demonstrated: `{"status": "completed"}`.
- If no relationships exist in data: `{"status": "skipped", "reason": "no_relationships"}`.

Include the `reason` field only when the step is skipped. Also set top-level `current_step` to
`"4d"`.

### Discover phase completion

After step 4d is complete (or after any early exit), update the top-level `discover_phase`
status in `config/bootcamp_progress.json` under `module_7_query`:

- Set `"discover_phase": "completed"` when all steps 4a–4d have been checkpointed (whether
  completed or individually skipped due to data limitations).
- Set `"discover_phase": "skipped"` when the bootcamper declines the Discover phase at the
  opt-in prompt or exits early at any transition point.

(The former step 4e — data-specific visualization suggestions — has moved to the Phase 1
step-3c visualization gate, sub-offer (d), and is no longer part of the Discover phase.)

The full checkpoint structure in `config/bootcamp_progress.json` is:

```json
{
  "module_7_query": {
    "steps": {
      "4a": {"status": "completed", "patterns_found": {"multi_record": 5, "cross_source": 3, "relationships": 2}},
      "4b": {"status": "completed", "entity_demonstrated": 1234},
      "4c": {"status": "completed", "entity_demonstrated": 5678},
      "4d": {"status": "completed"}
    },
    "discover_phase": "completed"
  }
}
```

After updating the `discover_phase` status, return to `phase1-query-visualize.md` for the Query
Completeness Gate.

**Success:** Discover phase completed (or explicitly skipped), data patterns analyzed, why/how
analysis demonstrated, and relationship networks explored. (Data-specific visualization
suggestions are offered separately at the Phase 1 step-3c visualization gate.)
