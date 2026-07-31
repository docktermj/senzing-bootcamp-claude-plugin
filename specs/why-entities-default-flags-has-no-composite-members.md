# `SZ_WHY_ENTITIES_DEFAULT_FLAGS` returns no `composite_members`, so the plugin's own default-flags procedure cannot be run for it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-07-query-visualize-discover/phase1-query-visualize.md` carries an explicit rule:
"Before parsing an entity field out of a response, read the composite's `composite_members`
and confirm the flag that populates *that* field is in it," with a table covering
`SZ_SEARCH_BY_ATTRIBUTES_ALL`, `SZ_FIND_NETWORK_DEFAULT_FLAGS` and `SZ_ENTITY_DEFAULT_FLAGS`.

**For the `why_*` composites the rule is unrunnable.** Verified on server 1.32.2, docs
indexed 2026-07-29 11:11 UTC, 2026-07-31:

```text
get_sdk_reference(topic='flags', filter='SZ_WHY_ENTITIES_DEFAULT_FLAGS')  →
  { "applies_to": ["why_entities*"],
    "description": "Replaces `G2_WHY_ENTITY_DEFAULT_FLAGS`, focused on the
                    `whyEntities*` functions",
    "name": "SZ_WHY_ENTITIES_DEFAULT_FLAGS",
    "source_file": "docs-release-4-4_0_breaking_changes-4_0_breaking_changes_sdk.md" }
```

No `composite_members`. No `response_paths`. A one-line description sourced from the
V3→V4 breaking-changes document rather than the flags documentation. Its `applies_to` is even
the literal glob `"why_entities*"` — every sibling lists real method names.

Every other composite in the **same response** carries a full membership list —
`SZ_ENTITY_DEFAULT_FLAGS` (9 members), `SZ_ENTITY_CORE_FLAGS` (6),
`SZ_ENTITY_INCLUDE_ALL_RELATIONS` (4) — as do `SZ_FIND_PATH_DEFAULT_FLAGS`,
`SZ_FIND_NETWORK_DEFAULT_FLAGS` and `SZ_HOW_ENTITY_DEFAULT_FLAGS`. The gap is specific to the
`why_*` default composites.

**What it costs a reader.** Calling `why_entities` with
`SZ_WHY_ENTITIES_DEFAULT_FLAGS | SZ_INCLUDE_FEATURE_SCORES | SZ_INCLUDE_MATCH_KEY_DETAILS`
returned both entity names as `null` while every other field — match level, why key, ER rule,
all feature scores and buckets, CONFIRMATIONS and DENIALS — rendered correctly. Adding
`SZ_ENTITY_INCLUDE_ENTITY_NAME` explicitly fixed it, and the server confirms that flag's
`applies_to` includes `why_entities`.

So the only route to discovering the omission is to call it, notice the nulls, and guess —
which inverts INV-115. The reference is supposed to prevent the empirical discovery, not
require it.

It is also the **more deceptive** shape of the half-populated row (INV-148): the *analytical*
content of the response is complete and correct, and only the human-readable labels are
missing, so the output reads as an unnamed-data problem rather than a flags problem.

## Root cause

The plugin's rule assumes every composite carries its membership, because every composite in
its own table does. The `why_*` composites are documented from the breaking-changes note
rather than the flags reference, so they arrive with a description and nothing machine-readable.
The rule has no branch for "the lookup returned no membership" — and a rule with no
unhappy path silently becomes "assume it is fine".

## Proposed change

The upstream half is already filed (the reporting entry records `Upstream: submitted
2026-07-31`), so **do not re-file it**. This spec is the plugin half.

1. **Add a row to the default-flags table** in `phase1-query-visualize.md`:
   `SZ_WHY_ENTITIES_DEFAULT_FLAGS` does not carry `SZ_ENTITY_INCLUDE_ENTITY_NAME`, so
   `ENTITY_NAME` reads `null` — OR it in explicitly. Cite the tool, server version and date.
2. **Give the rule its unhappy path**, which is the durable half: when a composite is
   returned **without** a `composite_members` list, the procedure **cannot be run**, and the
   sub-flags MUST be OR-ed in explicitly rather than assumed. State this generally, not only
   for `why_entities` — the same shape applies to its `why_records` and `why_record_in_entity`
   siblings, and to any composite documented from the breaking-changes note.
3. **Do not assert the sibling composites are identically affected** without checking them.
   The entry infers it; the server was asked only about `SZ_WHY_ENTITIES_DEFAULT_FLAGS`.
   Either check `why_records` and `why_record_in_entity` during implementation and record
   what they return, or scope the table row to what was verified and say the siblings are
   unverified.

## Acceptance criteria

- [ ] The default-flags table names `SZ_WHY_ENTITIES_DEFAULT_FLAGS` and states that
      `SZ_ENTITY_INCLUDE_ENTITY_NAME` must be OR-ed in explicitly, with tool, version and date.
- [ ] The rule states what to do when a composite returns **no** `composite_members`: the
      check cannot be run, so OR the needed sub-flags in explicitly rather than assuming.
- [ ] That instruction is general, not scoped to `why_entities` alone.
- [ ] The `why_records` / `why_record_in_entity` siblings are either verified and recorded, or
      explicitly marked unverified — not asserted from the `why_entities` result (INV-169).
- [ ] **Re-verification clause:** implementing this requires
      `get_sdk_reference(topic='flags', filter='SZ_WHY_ENTITIES_DEFAULT_FLAGS')` to still
      return no `composite_members`. If Senzing has populated it — the upstream request asks
      exactly that — the table row is unnecessary and only the general unhappy-path rule should
      ship. **Check this first; it is the one criterion most likely to have changed.**
- [ ] `tests/test_sdk_parameter_shapes.py` passes; a test pins the general
      no-membership rule so it cannot be dropped if the specific row is later removed.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — the default-flags table and the rule's unhappy path.
- `tests/test_sdk_parameter_shapes.py` — the no-membership rule pin.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "get_sdk_reference returns
  SZ_WHY_ENTITIES_DEFAULT_FLAGS with no composite_members, so the plugin's own default-flags
  procedure cannot be run for it" (2026-07-31, Module: Query, Visualize and Discover;
  `Source: self-observed (assistant retrospective)`; `Routing: both`)
- Priority: Medium
- MCP re-check: server 1.32.2, docs indexed 2026-07-29 11:11 UTC, 2026-07-31 — **still
  reproduces**, confirmed verbatim including the absent `response_paths` and the glob
  `applies_to`. Tool: `get_sdk_reference(topic='flags', filter='SZ_WHY_ENTITIES_DEFAULT_FLAGS')`.
  The same response confirms every sibling composite carries a full `composite_members` list.
- Upstream: **already sent 2026-07-31** per the entry's own `Upstream:` field — do not
  re-file. A follow-up would be warranted only with something the first submission lacked.
- Related specs: `specs/verify-sdk-parameter-shapes-and-flag-families.md` (INV-132),
  `specs/find-path-and-find-network-links-diverge.md` (the sibling trap in the adjacent step).
