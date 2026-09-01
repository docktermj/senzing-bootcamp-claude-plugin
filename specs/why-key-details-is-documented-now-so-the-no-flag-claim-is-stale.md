# Three files still say no flag is documented to populate `WHY_KEY_DETAILS` — the server documents it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Three shipped files carry an observation-only note whose central claim is now false:

| File | Line | Claim |
|---|---|---|
| `skills/module-07-query-visualize-discover/phase1-query-visualize.md` | 153 | "…the why response and **no flag is documented as populating it**" |
| `skills/module-07-query-visualize-discover/phase2-discover.md` | 158 | "…real path on the why response, and **no flag is documented as populating it**" |
| `skills/module-03b-truthset-visualization/visualization-api-reference.md` | 373 | "…Note that **no flag is *documented* to** populate it" |

On MCP server **1.35.3, 2026-09-01** the flag **is** documented, from both reference directions:

- `get_sdk_reference(topic='response_schemas', filter='why_entities', language='python')` returns
  `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS` carrying
  `requires_flags: ["SZ_INCLUDE_MATCH_KEY_DETAILS"]`, and the same for its
  `CONFIRMATIONS[]` subtree. The document is shared by `why_entities`, `why_records` and
  `why_record_in_entity`.
- `get_sdk_reference(topic='flags', filter='SZ_INCLUDE_MATCH_KEY_DETAILS')` returns
  `applies_to` including `why_entities`, `why_records` and `why_record_in_entity`, and a
  description that also documents the **relations-flag dependency** the plugin had recorded as
  an unexplained observation: *"dependent on using one of the following flags:
  SZ_ENTITY_INCLUDE_ALL_RELATIONS, SZ_ENTITY_INCLUDE_POSSIBLY_SAME_RELATIONS,
  SZ_ENTITY_INCLUDE_POSSIBLY_RELATED_RELATIONS, SZ_ENTITY_INCLUDE_NAME_ONLY_RELATIONS, or
  SZ_ENTITY_INCLUDE_DISCLOSED_RELATIONS."*

So the plugin's own dated guess — *"may require `SZ_INCLUDE_MATCH_KEY_DETAILS` plus a relations
flag"* — was **right**, and is now a documented fact rather than an observation. Both halves of the
note need to change: the guess becomes a citation, and the "nothing documents this" clause is simply
wrong.

**The triggering observation is also explained, and it is correct behavior.**
`get_sdk_reference(topic='flags', filter='SZ_WHY_RECORDS_DEFAULT_FLAGS')` returns
`composite_members: ["SZ_INCLUDE_FEATURE_SCORES"]` — *"Equivalent to: SZ_INCLUDE_FEATURE_SCORES."*
So `whyRecords(...)` under its own default composite returns feature scores and **no**
`WHY_KEY_DETAILS` because the default composite contains only the feature-scores flag. Nothing is
broken; the field is conditional and the condition is documented.

## Root cause

The note was written 2026-08-16 (`visualization-api-reference.md:373` carries the date) against a
server that did not yet annotate the field, and was correct then. INV-080 routes every Senzing fact
through the server, and INV-149 marks a fact the server cannot reach as observation-only — but
neither says who re-asks an observation once the server *can* reach it. Nothing does, so the note
stayed as written while the ground under it moved.

⚠️ This is the mirror of the defect `mcp-negative-markers-carry-rationale-nothing-reverifies`
addresses: that one is a dated **negative** whose rationale went stale; this is a dated
**observation-only** claim whose *premise* — that the server documents nothing — has been overtaken.
`coverage_reports.py negatives` does not list it, because it carries no `MCP-NEGATIVE` marker; it is
prose, not a marker.

## Proposed change

1. **Rewrite the claim at all three sites** as an MCP-sourced fact with its provenance:
   `WHY_KEY_DETAILS` requires `SZ_INCLUDE_MATCH_KEY_DETAILS`, which is itself dependent on one of
   the five relations flags, per `get_sdk_reference(topic='response_schemas', filter='why_entities')`
   and `topic='flags'` (server 1.35.3, 2026-09-01). Drop "no flag is documented".
2. **Keep the empty-section guidance.** The operational advice — if the field is missing for the
   flags in force, say so and fall back to `FEATURE_SCORES` rather than rendering an empty section —
   is unaffected and is what protects against the silent-blank failure mode.
3. **Say why a default composite does not produce it**, naming `SZ_WHY_RECORDS_DEFAULT_FLAGS`
   (= `SZ_INCLUDE_FEATURE_SCORES`), so a reader who hits the empty section knows the cause rather
   than suspecting the engine.
4. ⚠️ **Do not promote the observation about "two SDK builds" into a documented claim.** That it was
   *absent without the flag on two builds* remains an observation; what is now documented is which
   flag the schema says populates it.

## Acceptance criteria

- [ ] No shipped file claims that no flag is documented to populate `WHY_KEY_DETAILS`.
- [ ] All three sites cite the flag and the route that documents it, with server version and date.
- [ ] The relations-flag dependency is stated as documented, not as an observation.
- [ ] The empty-section fallback guidance is unchanged.
- [ ] A repo-level test fails if the retired claim reappears, deriving its site set by scanning
      shipped markdown rather than listing the three paths (INV-246). Negative-controlled.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — :153
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md` — :158
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` — :373
- `tests/test_why_key_details_flag_is_cited_not_guessed.py` (new) — the guard.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`, entry *"WHY_KEY_DETAILS absent from why_records
  under its own default flags (confirms an observation-only note)"*, 2026-08-26, module
  **Query, Visualize and Discover**, priority **Low**, `Source: self-observed (assistant
  retrospective)`, plugin 0.5.2, macOS 26.5.2.
- Priority: Low as filed; **the subject is redirected** — the entry routed this `mcp-server` and
  asked Senzing to document the flag. The server already does. What remains is a plugin defect:
  three files assert the opposite.
- MCP re-check: server **1.35.3**, 2026-09-01 — **server now contradicts the plugin.** Tools called:
  `get_capabilities`; `get_sdk_reference(topic='response_schemas', filter='why_entities',
  language='python')`; `get_sdk_reference(topic='flags', filter='SZ_INCLUDE_MATCH_KEY_DETAILS')`;
  `get_sdk_reference(topic='flags', filter='SZ_WHY_RECORDS_DEFAULT_FLAGS')`.
  owner-checked: this spec asserts the plugin is wrong, not that the server lacks anything — the
  one residual absence claim is that `topic='flags'` lists `response_paths:
  ["RELATED_ENTITIES[].MATCH_KEY_DETAILS"]` for `SZ_INCLUDE_MATCH_KEY_DETAILS` and **not** the
  why-side `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS`. Owner: `get_sdk_reference(topic='flags',
  filter='SZ_INCLUDE_MATCH_KEY_DETAILS')` IS the route that owns a flag's response paths, and it was
  asked — it returns the entity-side path only (routing negative: the why-side annotation lives in
  `topic='response_schemas'`, which does carry it).
- Upstream: **not sent, and not owed as a new report.** The entry's `Upstream:` reads *"offered,
  awaiting the Bootcamper's decision"*, but its ask is already satisfied: the schema documents the
  flag. The residual `response_paths` omission is the **same class** as
  `flag-gated-fields-are-unannotated-in-both-reference-topics`, which was sent upstream 2026-08-31
  with the maintainer's approval — this is a second data point on a filed finding, not a new one.
- Related specs: `flag-gated-fields-are-unannotated-in-both-reference-topics.md`;
  `mcp-negative-markers-carry-rationale-nothing-reverifies.md` (the same staleness mechanism, for
  markers rather than prose).
