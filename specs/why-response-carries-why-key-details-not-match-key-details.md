# Step 4b names MATCH_KEY_DETAILS, but a why response carries WHY_KEY_DETAILS

## Problem

`module-07-query-visualize-discover/phase2-discover.md:113-123` (step 4b.3) instructs the guide to
generate the `why_records` / `why_entities` call with **both** flags and explains what each buys:

> - `SZ_INCLUDE_FEATURE_SCORES` … the numeric similarity scores for each feature comparison
> - `SZ_INCLUDE_MATCH_KEY_DETAILS`: explain: "I'm using SZ_INCLUDE_MATCH_KEY_DETAILS so we can
>   see exactly which feature combinations triggered the resolution. This is the match key
>   Senzing used to decide these records belong together."

A `why_records` response does **not** contain `MATCH_KEY_DETAILS`. It contains **`WHY_KEY_DETAILS`**.

Measured live on this walk (Senzing SDK 4.3.4, Java binding, 2026-08-14), calling
`whyRecords(MERIDIAN_CRM/MC-1001, SUMMIT_BILLING/SB-9001, flags)` two ways:

| Flags passed | `WHY_RESULTS[0].MATCH_INFO` keys |
|---|---|
| `SZ_INCLUDE_FEATURE_SCORES` + `SZ_INCLUDE_MATCH_KEY_DETAILS` (as prescribed) | `CANDIDATE_KEYS, DISCLOSED_RELATIONS, FEATURE_SCORES, MATCH_LEVEL_CODE, WHY_ERRULE_CODE, WHY_KEY, WHY_KEY_DETAILS` |
| the same **plus** the four relations flags | *identical* — same seven keys |

`MATCH_KEY_DETAILS` is absent in both. This is consistent with the server's own flag
documentation, which is easy to misread: `get_sdk_reference(topic='flags')` describes
`SZ_INCLUDE_MATCH_KEY_DETAILS` as putting a `MATCH_KEY_DETAILS` object on **each related entity**
(`response_paths: RELATED_ENTITIES[]`), and marks it `depends_on` one of the relations flags. Related
entities are a different surface from why results — and this dataset has zero relationships, so the
flag has nothing to attach to regardless.

The consequence is the failure mode the plugin warns about everywhere else: a guide following step
4b writes a parser for `MATCH_KEY_DETAILS`, gets nothing, and renders blank — no error, no
exception. `ground-rules.md` → "Defensive parsing" calls this out explicitly ("a wrong field name
yields `None`, which renders as blank text"), and step 4b.3 itself instructs looking up
`response_schemas` before parsing. The step's own prose is what points at the wrong field name.

## Two secondary observations from the same call, worth fixing alongside

1. **The dependency is unstated.** `SZ_INCLUDE_MATCH_KEY_DETAILS` `depends_on`
   `SZ_ENTITY_INCLUDE_ALL_RELATIONS` (or one of the four relation flags). Step 4b.3 presents it as a
   flag you simply add.
2. **In the Java binding a composite is not an `SzFlag`.** `whyRecords` takes `Set<SzFlag>`, but
   `SzFlags.SZ_ENTITY_INCLUDE_ALL_RELATIONS` is a `long` bitmask — it does not compile into that
   argument (`incompatible types: long cannot be converted to Collection<? extends SzFlag>`), so the
   composite must be enumerated as its four member constants. Nothing in the module says composites
   and individual flags have different types in Java, and the plugin's "confirm their exact names"
   instruction addresses names, not types. This is the per-binding hazard INV-002 and the
   cross-binding warnings exist for, in a form the module does not cover.

## Proposed change

1. In `phase2-discover.md` step 4b.3, replace `MATCH_KEY_DETAILS` with **`WHY_KEY_DETAILS`** in both
   the flag rationale and any downstream parsing instruction, and describe it as the field that
   breaks the why key down.
2. State that `SZ_INCLUDE_MATCH_KEY_DETAILS` targets `RELATED_ENTITIES[]` and needs a relations
   flag — so it belongs to relationship inspection (step 4d), not to the why demonstration.
3. Add one line to step 4b's flag guidance: in a `Set<SzFlag>` argument, composites must be
   enumerated as their member constants; confirm the **type** as well as the name via
   `get_sdk_reference`.
4. Keep the step's existing instruction to check `response_schemas` before parsing — it is correct,
   and following it is what surfaces this.

## Acceptance criteria

- Step 4b.3 names `WHY_KEY_DETAILS` for the why demonstration.
- `SZ_INCLUDE_MATCH_KEY_DETAILS` is described with its `RELATED_ENTITIES[]` target and its relations
  dependency, and is not prescribed for the why call.
- The composite-vs-enum type hazard is stated once in the module's flag guidance.
- A test asserts `phase2-discover.md` does not instruct parsing `MATCH_KEY_DETAILS` out of a why
  response.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md`
- `tests/test_module07_why_flags.py` (new)

## Source

`/dry-run` phase 3, 2026-08-14, measured against the walk's own load. Senzing SDK 4.3.4 (Java),
MCP server 1.32.9, docs indexed 2026-08-11 20:52 UTC. Both flag combinations run and compared;
`src/query/why_demo.java` in the scratch project is the reproduction.

## Deviations from this spec, and why (2026-08-14)

Re-verified against MCP server **1.32.9** on 2026-08-14 before any edit. The core finding holds
— the why response carries `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS` and no `MATCH_KEY_DETAILS`
(`get_sdk_reference(topic='response_schemas', filter='why_records')`). Three things differed.

1. **There is no flag to substitute, so proposed change 1 could not be applied as written.** It
   asks to "replace `MATCH_KEY_DETAILS` with `WHY_KEY_DETAILS` in the flag rationale", which
   presumes a flag whose rationale is the why-key breakdown. No flag applicable to `why_records`
   documents `WHY_KEY_DETAILS` among its `response_paths`, and the method's own default composite
   `SZ_WHY_RECORDS_DEFAULT_FLAGS` is documented as *"Equivalent to: `SZ_INCLUDE_FEATURE_SCORES`"*
   — one flag, not two (`get_sdk_reference(topic='flags', filter='why_records')`, 1.32.9,
   2026-08-14). The step therefore prescribes `SZ_INCLUDE_FEATURE_SCORES` alone and names
   `WHY_KEY_DETAILS` as a **response path to parse**, not as a flag rationale. The spec's own
   measurement could not have caught this: both of its runs passed
   `SZ_INCLUDE_MATCH_KEY_DETAILS`, so neither isolates what populates `WHY_KEY_DETAILS`.

2. **"Does not apply to why results" is too strong.** `SZ_INCLUDE_MATCH_KEY_DETAILS`'s
   `applies_to` **does** list `why_entities`, `why_records` and `why_record_in_entity`. The
   accurate statement, and the one shipped, is that the why methods *accept* it while what it
   populates is a `MATCH_KEY_DETAILS` object on each **related entity** (`response_paths:
   RELATED_ENTITIES[]`), gated behind `depends_on` a relations flag — so on a why call it has
   nothing to attach to. Shipping "it does not apply" would have been the INV-169 failure mode.

3. **The Java type hazard is observation-only and is marked as such.** The server documents
   `composite_members` (`SZ_ENTITY_INCLUDE_ALL_RELATIONS` → the four relation flags), which is
   what makes the *actionable* instruction MCP-sourced. It does not document per-binding constant
   **types**, so the spec's `long`-vs-`SzFlag` finding is kept as a dated observation (Senzing SDK
   4.3.4, Java, 2026-08-14) rather than promoted to an MCP fact, per INV-080/INV-149.

**Establishes no invariant.** The candidate rule — *guidance prescribing a flag must name the
response path that flag populates* — is already **INV-179**, which requires confirming that the
flag populating a field is in force and names "a correct field name the flags in force do not
populate" as a distinct cause of a blank. This step was a live violation of it. What was missing
was the citation at the step (INV-183), now added; the ⚠️ type bullet likewise cites INV-132.

**Also touched, within the spec's named file:** step 5 ("Match-key breakdown") presented an
unnamed "match-key string". It now reads the key from `WHY_RESULTS[].MATCH_INFO.WHY_KEY` and
uses the step-3 `WHY_KEY_DETAILS` confirmations for the per-component explanation, so the
presentation and the parse agree on one documented path.
