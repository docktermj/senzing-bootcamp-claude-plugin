# Document the network-link endpoint fields, and say what to do when `response_schemas` has no entry

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-115 requires looking up a method's response structure via
`get_sdk_reference(topic='response_schemas', filter='<method>')` before writing code that parses it.
For several methods the bootcamp routinely parses, that lookup returns nothing:

- **`get_version` and `get_license`** — `data` came back as an empty array, so the response shape had
  to be discovered by dumping a raw response. Module 4's licence gate parses `get_license`'s
  `recordLimit`; Module 2 reports the SDK version.
- **`find_network_by_entity_id`** — no `response_schemas` entry at all, at the one step whose
  guidance explicitly demands the lookup first.

The second gap then produced the exact failure INV-115 exists to prevent. `ENTITY_NETWORK_LINKS`
entries key their endpoints as **`MIN_ENTITY_ID` / `MAX_ENTITY_ID`** — normalized low-to-high — not
the `ENTITY_ID` / `RELATED_ENTITY_ID` pairing used everywhere else in the SDK's responses. Parsing
with the latter yields `None` for both endpoints while `MATCH_KEY` renders correctly.

That partial render is the harmful part. A row showing a real match key and two blank endpoints does
not read as a parsing bug — it reads as a relationship Senzing could not fully describe. An
all-blank row invites suspicion; a half-populated one does not.

## Root cause

The guidance mandates a lookup that cannot succeed for these methods, and never records the answer
once someone has paid to discover it.

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md:29-32`
  requires both `get_sdk_reference(topic='flags', filter='find_network')` **and**
  `get_sdk_reference(topic='response_schemas', filter='find_network')` before generating the call,
  and `:35-36` restates INV-115's ⛔. The reference has no `find_network` entry, so the required step
  yields nothing and the guidance offers no next move at that point.
- INV-115 does provide the general fallback — "where `response_schemas` does not reach (nesting below
  the top-level shape it documents), a dumped raw response is the authority" — but it is phrased for
  *depth*, not for *absence*. A reader whose lookup returned an empty `data` array is not obviously
  in the case the rule describes.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md:248-249`
  lists the MCP-confirmed paths as `find_path_*` → `ENTITY_PATHS[]`, `ENTITIES[]` and `find_network_*`
  → `ENTITY_PATHS[]`, `ENTITIES[]`, `ENTITY_NETWORK_LINKS[]`. It stops at the top-level keys, so the
  link element's own fields are undocumented — and `MIN_ENTITY_ID` / `MAX_ENTITY_ID` appear **nowhere**
  in the plugin (confirmed by grep across all skills and scripts).
- The file already carries the right pattern for precisely this trap — the "Watch this asymmetry —
  it is a silent-blank trap" note at `:252-256`, which documents the
  `WHY_KEY_DETAILS` / `MATCH_KEY_DETAILS` divergence. The network-link normalization is the same
  class of finding and is simply missing from it.

**Upstream component (Senzing MCP server), not fixable in this repository.** `response_schemas`
should carry entries for `get_version`, `get_license`, `find_network_*` and `find_path_*`, noting the
`MIN_ENTITY_ID` / `MAX_ENTITY_ID` normalization. Offered upstream and **declined**.

## Proposed change

1. **Record the network-link fields in the contract.** Extend the MCP-confirmed paths table in
   `visualization-api-reference.md:242-249` so `find_network_*` documents the element shape, not just
   the array name: `ENTITY_NETWORK_LINKS[]` entries key their endpoints as `MIN_ENTITY_ID` /
   `MAX_ENTITY_ID` (normalized low-to-high), with `MATCH_KEY` alongside. Verify against a dumped raw
   response at implementation time and mark it as such — the table's existing convention — rather
   than copying it from this spec.

2. **Add it to the silent-blank trap note.** The asymmetry note at `:252-256` is where a reader looks
   for "field name differs from where you'd expect". Put the endpoint-key divergence there too, with
   the reason it is dangerous: parsing with `ENTITY_ID` / `RELATED_ENTITY_ID` still renders
   `MATCH_KEY`, so the row looks populated.

3. **State the no-entry outcome at the call site.** In `phase2b-discover.md`, after the required
   lookups, say what an empty result means and what to do: `response_schemas` has no entry for the
   graph methods, so the lookup returning nothing is the **expected** outcome, not a failed call —
   dump one raw response and read the endpoints from it before writing the parser. Name
   `get_version` and `get_license` as two more methods with no entry, so the pattern is recognizable
   rather than surprising.

4. **Extend the blank-field rule to partial rows.** INV-115 covers a field that comes back
   null/blank. Add the sibling case: when **some** fields of a parsed record populate and others are
   blank, the blanks are a probable wrong field name, not partial data from Senzing. A partially
   populated row is more deceptive than an empty one, because the populated fields signal that the
   parse worked. Applies wherever the bootcamp renders per-row SDK output.

## Acceptance criteria

- [ ] `visualization-api-reference.md`'s MCP-confirmed paths table documents `ENTITY_NETWORK_LINKS[]`
      element fields including the `MIN_ENTITY_ID` / `MAX_ENTITY_ID` endpoint keys, verified from a
      dumped raw response at implementation time and marked as verified-when.
- [ ] The silent-blank trap note names the endpoint-key divergence and states that `MATCH_KEY` still
      renders when the endpoints are parsed under the wrong names.
- [ ] `phase2b-discover.md` states that `response_schemas` has no entry for the graph methods, that
      an empty result is expected rather than a failed call, and that a raw-response dump is the
      authority (INV-115).
- [ ] `get_version` and `get_license` are named as methods with no `response_schemas` entry, at or
      near the steps that parse them.
- [ ] The guidance treats a partially-populated parsed row as a probable field-name error, and such a
      row is not rendered as a real result (extends INV-115).
- [ ] A relationship-network rendering built from this guidance shows both endpoint ids populated.
- [ ] No field name in the new text is asserted from training data — each is dump-verified or
      MCP-sourced (INV-080).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): response
      field names are language-independent JSON, and the contract binds a visualization server in any
      language (INV-090/INV-124).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the MCP-confirmed paths table (`:242-249`) and the silent-blank trap note (`:252-256`).
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md` — the
  lookup block at `:29-36`: the no-entry outcome and the dump instruction.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the partially-populated-row
  rule, so it reaches every module that parses an SDK response.
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — Step 8a (`:486-492`): note
  that `get_license`'s shape is not in `response_schemas`.
- `tests/` — extend the response-shape guidance test to assert the endpoint keys are documented.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "response_schemas has no entry for several
  commonly-parsed methods, and find_network link fields are undocumented" (2026-07-26, Module Query,
  Visualize and Discover; `Source: self-observed (assistant retrospective)`; `Routing: mcp-server`;
  `Upstream: offered, declined`)
- Priority: Medium
- Related specs: `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115 — this closes its
  absence case and extends it to partial rows),
  `specs/verify-sdk-parameter-shapes-and-flag-families.md` (INV-132 — the same step's *input* shapes),
  `specs/match-key-audit-cannot-read-related-entities-from-export.md`,
  `specs/mcp-grounding-in-every-skill.md` (INV-080)
