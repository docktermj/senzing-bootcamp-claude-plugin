# `SZ_INCLUDE_MATCH_KEY_DETAILS` does list the export methods, and one of the two sites says it does not

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-03b-truthset-visualization/visualization-api-reference.md:110-115` groups three flags
together and says none of them applies to export:

> Those relationship-detail flags (`SZ_ENTITY_INCLUDE_ALL_RELATIONS` and its members,
> `SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO`, `SZ_INCLUDE_MATCH_KEY_DETAILS`) **do not list the export
> methods** in their `applies_to` — confirm with
> `get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_ALL_RELATIONS')` — which is why
> composing an export's flags out of those alone is the case that loses relationships.

**Two of the three are right; the third is wrong.** `get_sdk_reference(topic='flags',
filter='SZ_ENTITY_INCLUDE_ALL_RELATIONS')` on **server 1.32.8, docs index 2026-08-11 13:35 UTC,
asked 2026-08-11** returns:

| Flag | `applies_to` includes export methods? |
|---|---|
| `SZ_ENTITY_INCLUDE_ALL_RELATIONS` | **No** |
| `SZ_ENTITY_INCLUDE_RELATED_ENTITY_NAME` | **No** |
| `SZ_ENTITY_INCLUDE_RELATED_RECORD_SUMMARY` | **No** |
| `SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO` | **No** |
| `SZ_ENTITY_INCLUDE_RELATED_RECORD_DATA` | **No** |
| `SZ_ENTITY_INCLUDE_RELATED_RECORD_TYPES` | **No** |
| **`SZ_INCLUDE_MATCH_KEY_DETAILS`** | **YES** — `export_json_entity_report`, `export_csv_entity_report` |

`SZ_INCLUDE_MATCH_KEY_DETAILS`'s full `applies_to` is `get_entity_by_entity_id`,
`get_entity_by_record_id`, `search_by_attributes`, `how_entity_by_entity_id`, `why_entities`,
`why_records`, `why_record_in_entity`, `why_search`, **`export_json_entity_report`**,
**`export_csv_entity_report`**, `find_path_by_entity_id`, `find_path_by_record_id`,
`find_network_by_entity_id`, `find_network_by_record_id` — the only flag in that group that names
the export family, and the only one the plugin's sentence gets wrong.

**The sibling site states it correctly.** `module-06-data-processing/phaseD-validation.md:225-227`
makes the same argument but scopes it to "the relationship-detail flags
(`SZ_ENTITY_INCLUDE_ALL_RELATIONS` **and its members**)" — which is exactly true, and does not name
`SZ_INCLUDE_MATCH_KEY_DETAILS`. So the two copies of one rule disagree, and the more specific one is
the wrong one.

**INV-169 applied.** Not a conditions mismatch. The claim is about a flag's `applies_to` under
`topic='flags'`, and that is the tool and topic asked, with the filter the plugin's own text names.
`SZ_INCLUDE_MATCH_KEY_DETAILS` does carry `depends_on` — it requires one of the relations flags — so
it is *conditional*, but the plugin's sentence is about `applies_to`, not about dependency, and on
that axis it is simply wrong.

**Consequence, and why it is mild but worth fixing.** The paragraph's *conclusion* survives: composing
an export's flags out of the relations members alone still loses relationships, because those members
genuinely do not apply to export. What breaks is the reasoning a reader takes away — someone who
wants match-key detail on an export and believes this sentence will not even try the flag that does
apply, and will fall back to per-entity calls they do not need.

## Root cause

The sentence was written from one lookup and generalized across a list. `SZ_INCLUDE_MATCH_KEY_DETAILS`
is returned *in the same response* as the relations flags — it appears in the
`filter='SZ_ENTITY_INCLUDE_ALL_RELATIONS'` result because it `depends_on` them — so it is easy to read
the whole response as one homogeneous group and miss that one row's `applies_to` is longer than the
others'. The `confirm with …` instruction the plugin gives is correct and would have caught it; the
sentence just did not follow its own advice for the third flag.

## Proposed change

**Split the claim so each flag carries what the server actually says.**

Rewrite `:110-115` to state:

1. `SZ_ENTITY_INCLUDE_ALL_RELATIONS` and its members (`SZ_ENTITY_INCLUDE_RELATED_ENTITY_NAME`,
   `_RELATED_RECORD_SUMMARY`, `_RELATED_MATCHING_INFO`, `_RELATED_RECORD_DATA`,
   `_RELATED_RECORD_TYPES`) do **not** list the export methods in `applies_to` — unchanged, still the
   reason composing an export's flags from those alone loses relationships.
2. `SZ_INCLUDE_MATCH_KEY_DETAILS` **does** list `export_json_entity_report` and
   `export_csv_entity_report`, so match-key detail *is* available on an export — but it
   `depends_on` one of the relations flags, so it only produces output when the export's flag set
   already includes relationships.

Carry the provenance the page uses elsewhere: the tool, the filter, server 1.32.8 and the date.

**What stays.** The whole surrounding argument: the two-bootcamp observation about
`RELATED_ENTITIES` present vs absent, "an export **is** a legitimate edge source when its rows carry
the key", the per-entity/network fallback, and the existing `confirm with get_sdk_reference(...)`
instruction — which is the thing that makes this page self-correcting and should be more prominent,
not less.

**Check `phaseD-validation.md:225-227` and leave it alone if it still scopes correctly.** It does
today. Do not "harmonize" the two by copying the wrong sentence into it — the divergence is the
correct one being narrower, and the fix is to narrow the other.

**Fallback (INV-125).** None needed; this corrects a stated fact and adds no new call.

## Acceptance criteria

- [ ] `visualization-api-reference.md` no longer includes `SZ_INCLUDE_MATCH_KEY_DETAILS` in the set
      said not to list the export methods.
- [ ] It states that `SZ_INCLUDE_MATCH_KEY_DETAILS` **does** apply to `export_json_entity_report` and
      `export_csv_entity_report`, and that it `depends_on` one of the relations flags.
- [ ] The claim carries its provenance: tool, filter, server version, date.
- [ ] The surrounding argument is intact — the two-session observation, the "export is a legitimate
      edge source" conclusion, and the `confirm with get_sdk_reference(...)` instruction.
- [ ] `phaseD-validation.md:225-227` is **verified by opening it** (INV-182) and left correct — it
      scopes to "`SZ_ENTITY_INCLUDE_ALL_RELATIONS` and its members", which holds.
- [ ] **Re-verification clause:** implementing this requires
      `get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_ALL_RELATIONS')` to still return
      `SZ_INCLUDE_MATCH_KEY_DETAILS` with `export_json_entity_report` and `export_csv_entity_report`
      in its `applies_to`, and the six relations flags without them. If that has changed, re-triage.
- [ ] Any test pinning the grouped wording is repointed to the requirement, with a docstring saying
      what changed and when (INV-181). Check `tests/test_related_entities_guidance.py` and
      `tests/test_viz_endpoint_sync.py`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — `:110-115`.
- `tests/` — only if an assertion pins the grouped wording.

## Source

- Sweep: `delegate-to-mcp-server`, 2026-08-11 (second pass). Server **1.32.8**, docs index
  **2026-08-11 13:35 UTC** — **both axes unchanged** since the same day's first pass, so this run
  covered only sites never examined before. This claim had no ledger row.
- Tools called: `get_capabilities`, `search_docs` (index stamp),
  `get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_ALL_RELATIONS')`,
  `get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_RECORD_DATA')`.
- Verdict: `contradicted`, ledger key `relationship-flags-omit-export-methods`.
- Priority: **Medium.** The paragraph's conclusion is still right, so nothing a Bootcamper builds
  breaks; the cost is a reader who believes match-key detail is unavailable on exports when it is,
  in the file that exists to be authoritative about flags and response shapes.
- Upstream: not applicable — the server is right; one of the plugin's two copies is stale.
- Related specs: `specs/export-related-entities-is-flag-conditional.md`,
  `specs/match-key-audit-cannot-read-related-entities-from-export.md`,
  `specs/related-entities-guidance.md` if present.

## Deviations from this spec, and why (2026-08-11)

**Criterion 7 was vacuous, so a guard was added instead.** It asks that "any test pinning the
grouped wording is repointed". No test pinned it — `tests/test_viz_endpoint_sync.py` does not mention
the flags at all, and `tests/test_related_entities_guidance.py` names the claim only in its module
docstring, correctly scoped to "`SZ_ENTITY_INCLUDE_*` members", which is true and was left alone.
Repointing nothing would have left the correction unguarded, so
`TestMatchKeyDetailsIsNotGroupedWithTheRelationsFlags` (5 tests) was added to that file. This is
beyond the spec's criteria and is disclosed rather than folded into them.

**One of those new assertions was vacuous on its first attempt, and mutation testing caught it.**
`test_the_claim_carries_its_provenance` originally matched `verified on MCP server 1\\.\\d+\\.\\d+`
against the whole file. The page carries several other stamps, so stripping the provenance from
**this** claim still passed. It is now scoped to the paragraph, and the mutation is caught. Four
mutations were tried in total — regrouping into the wrong form, deleting the exception paragraph,
dropping the dependency clause, stripping the provenance — and all four now fail the suite.

**`phaseD-validation.md` was verified by opening it** (INV-182) and left unchanged: `:222-229`
scopes to "`SZ_ENTITY_INCLUDE_ALL_RELATIONS` and its members" and never names
`SZ_INCLUDE_MATCH_KEY_DETAILS`, so it was already correct. A new assertion pins that it stays that
way, since the obvious "harmonize the two files" instinct would propagate the wrong form into it.
