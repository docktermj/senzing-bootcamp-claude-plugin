# Two arrays in one `find_network` response use different endpoint keys, and step 4d warns about neither

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A guide building the relationship-network view read the **path** endpoint names off a **link**
element. All 38 edges of a corporate hierarchy printed `null -> null`, with no error. A silently
empty edge list is indistinguishable from "this data has no relationships" — the wrong conclusion to
hand an analyst, in the capability the fraud-detection pattern leans on hardest.

One `find_network` response carries two arrays that do not agree on how an endpoint is named
(**re-verified on MCP server 1.32.9, 2026-08-17**,
`get_sdk_reference(topic='response_schemas', filter='find_network', language='java')`):

| Array | Endpoint keys | Other fields |
|---|---|---|
| `ENTITY_PATHS[]` | `START_ENTITY_ID`, `END_ENTITY_ID` (directed) | `ENTITIES[]` |
| `ENTITY_NETWORK_LINKS[]` | `MIN_ENTITY_ID`, `MAX_ENTITY_ID` (undirected, normalized low-to-high) | `MATCH_KEY`, `MATCH_LEVEL_CODE`, `ERRULE_CODE`, `IS_AMBIGUOUS`, `IS_DISCLOSED` |

The distinction is sensible once seen — a link is an unordered pair, a path is directed — but
`START_`/`END_` is the natural wrong guess precisely **because the sibling array in the same
response uses it**.

## Root cause

**Step 4d's warning runs along the wrong axis.** `phase2b-discover.md:40-69` is a long, careful
block about *carrying a parser between `find_path` and `find_network`* — the cross-method axis. It
never mentions the within-response axis, where the two arrays of a single response disagree.

Worse, the sentence that would be the natural place to say so actively points away from it
(`:46-48`):

> Everything else matches: both carry `ENTITIES[]` and `ENTITY_PATHS[]` with the same sub-fields,
> and **both link elements carry the same seven fields**, which is what makes the array name the one
> difference a shared parser misses.

⚠️ **That sentence is literally true and still misleads.** Verified today on 1.32.9: across the
`find_path` and `find_network` documents, `ENTITY_PATHS[]` *does* carry the same three sub-fields
(`START_ENTITY_ID`, `END_ENTITY_ID`, `ENTITIES[]`) and both link arrays *do* carry the same seven.
So "everything else matches" is correct **about the comparison the step is making**. But the step
**never names `ENTITY_PATHS[]`'s three fields** while naming the links' seven explicitly, and it
tells the reader the two documents differ in "exactly one key". A reader reasonably concludes the
endpoint convention is uniform. It is not.

**The one endpoint warning the step does give is for a different wrong guess.** `:60-64` says do not
assume `ENTITY_ID` / `RELATED_ENTITY_ID`, "the pairing that related-entity records use". The failure
observed here is `START_ENTITY_ID` / `END_ENTITY_ID` — a pairing that is *correct in the same
response*, one array over. The existing warning does not reach it.

**Nothing else in the plugin covers it.** `visualization-api-reference.md:326-327` records both link
arrays' seven fields and the `ENTITY_PATH_LINKS[]` vs `ENTITY_NETWORK_LINKS[]` array-name trap
(implemented from `find-path-and-find-network-links-diverge`), and names `ENTITY_PATHS[]` in the
outer-array list — but never records `ENTITY_PATHS[]`'s own endpoint fields either.

## Proposed change

1. **State the within-response divergence at step 4d, in one sentence beside the existing
   cross-method warning:** in a `find_network` response, `ENTITY_PATHS[]` endpoints are
   `START_ENTITY_ID` / `END_ENTITY_ID` (directed) while `ENTITY_NETWORK_LINKS[]` endpoints are
   `MIN_ENTITY_ID` / `MAX_ENTITY_ID` (undirected, normalized low-to-high) — and say *why*, because
   the reason (a link is an unordered pair) is what makes it memorable rather than another name to
   recall.
2. **Name `ENTITY_PATHS[]`'s three fields** wherever the seven link fields are named, so the
   asymmetry is visible rather than inferred. That is step 4d and
   `visualization-api-reference.md`'s MCP-confirmed response-paths table.
3. **Repair the "everything else matches" sentence** so it cannot be read as "the endpoint
   convention is uniform". It is making a cross-document claim; it should say so and stop there.
4. **Keep the existing `ENTITY_ID` / `RELATED_ENTITY_ID` caution.** It is a real and different wrong
   guess. This adds a second one rather than replacing it — and the pair is the point: two plausible
   wrong endpoint namings, one from related-entity records, one from the sibling array.

## Acceptance criteria

- [ ] Step 4d names `ENTITY_PATHS[].START_ENTITY_ID` / `.END_ENTITY_ID` and
      `ENTITY_NETWORK_LINKS[].MIN_ENTITY_ID` / `.MAX_ENTITY_ID` as belonging to the **same**
      response, and says why they differ.
- [ ] No shipped sentence can be read as claiming the two arrays share an endpoint convention.
- [ ] `visualization-api-reference.md`'s MCP-confirmed table records `ENTITY_PATHS[]`'s three
      fields with route, server version and date, alongside the link rows it already carries.
- [ ] The existing `ENTITY_ID`/`RELATED_ENTITY_ID` caution and the `ENTITY_PATH_LINKS[]` array-name
      trap both survive unchanged.
- [ ] A test asserts both endpoint pairs are named at step 4d and fails if either is dropped.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — these
      are response JSON key names, identical in every binding.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md` — step 4d,
  `:40-69` (the `:46-48` sentence and the `:60-64` caution).
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the MCP-confirmed response-paths table, `:326-327`.
- `tests/` — guard for both endpoint pairs.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "findNetwork links and paths use DIFFERENT endpoint key names" (2026-08-17, Module Query, Visualize and Discover, step 4d; `Source: self-observed (assistant retrospective)`)
- Priority: **High.** Silent blank output in the module's relationship view, reached by a guess the response itself encourages, on the capability the headline fraud pattern depends on.
- MCP re-check: **server 1.32.9, 2026-08-17 — the divergence is real and fully documented by the server.** `get_sdk_reference(topic='response_schemas', filter='find_network', language='java')` returns `ENTITY_PATHS[].START_ENTITY_ID`, `.END_ENTITY_ID`, `.ENTITIES[]` and `ENTITY_NETWORK_LINKS[].{MIN_ENTITY_ID, MAX_ENTITY_ID, MATCH_KEY, MATCH_LEVEL_CODE, ERRULE_CODE, IS_AMBIGUOUS, IS_DISCLOSED}`. The same call with `filter='find_path'` returns `ENTITY_PATHS[]` with the identical three fields plus `ENTITY_PATH_LINKS[]` with the identical seven — confirming the cross-document claim the step already makes, and the within-response asymmetry it does not.
- Upstream: **not applicable, and the entry's proposed report MUST NOT be sent.** ⛔ The entry routes this `mcp-server` and asks Senzing to "document both arrays' fields under `get_sdk_reference(topic='response_schemas', filter='find_network')`". **The server already documents every field the entry lists**, including the `MIN`/`MAX` versus `START`/`END` split — verified above. Filing it would report a gap that does not exist. Rerouted to `plugin`.
- Related specs: `specs/find-path-and-find-network-links-diverge.md` (implemented; the cross-method axis, and the reason step 4d reads the way it does), `specs/network-link-fields-and-uncovered-response-schemas.md` and `specs/confirm-json-data-and-network-link-response-paths.md` (where the link fields were first recorded, when `response_schemas` did not yet carry them), `specs/how-analysis-step-does-not-name-the-confusable-virtual-entity-keys.md` (the same defect class one step earlier, at 4c), and INV-080, INV-115, INV-148, INV-149.

## Two corrections to the feedback entry

1. ⛔ **The routing is wrong and the upstream offer must be withdrawn.** The entry states
   *"`reporting_guide(topic='graph')` names both arrays but neither array's fields"* and concludes
   the defect is Senzing's. `reporting_guide` is not the route that owns response shapes —
   `get_sdk_reference(topic='response_schemas')` is, and it carries every field the entry asks for.
   The gap is that the plugin's step 4d does not relay it.
2. **The repo's earlier record of this area is now stale in the plugin's favor, not against it.**
   `specs/IMPLEMENTED.md:2135` recorded the link fields as "explicitly NOT in `response_schemas`"
   (2026-07-28), and `visualization-api-reference.md:327` has already been updated to say they are
   "now documented by `response_schemas`" (1.32.2, 2026-07-30). Today's check confirms that remains
   true on 1.32.9. No stale-negative removal is owed.
