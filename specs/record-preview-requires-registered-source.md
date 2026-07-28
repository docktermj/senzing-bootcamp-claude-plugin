# `getRecordPreview` needs the data source registered, and the plugin never mentions the method

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`SzEngine.getRecordPreview(recordDefinition)` returns Senzing's own interpretation of a record
**without loading it** — the authoritative way to check whether an attribute name will actually
participate in matching, rather than reading field names against the specification text and hoping.

Used during Phase 1's Senzing-readiness check, it failed:

```text
SENZ2207|Data source code [ICIJ] does not exist
```

Preview persists nothing, so needing prior configuration registration is non-obvious — and the
readiness check naturally runs *before* registration, because registration belongs to the loading
phase.

The fix is trivial once known. The cost is that it sits directly on the path of the most valuable
verification available in the mapping module: asking Senzing how it interprets a record instead of
inspecting field names by eye. Anything that discourages that check costs more than the two minutes
it takes to diagnose.

## Root cause

**The plugin never mentions the method at all.** `getRecordPreview` / `get_record_preview` appears
**nowhere** in `plugins/senzing-bootcamp/skills/` (confirmed by grep), so a bootcamper who reaches for
it — correctly — gets no guidance about its prerequisite, and the module's own readiness check does not
route them to it either.

**The prerequisite is not in the SDK reference.** Verified on MCP server 1.32.1, 2026-07-28:
`get_sdk_reference(topic='parameters', filter='getRecordPreview')` returns the signature for every
binding —

```text
getRecordPreview(recordDefinition: String, flags: Set<SzFlag>) -> String
getRecordPreview(recordDefinition: String) -> String
```

— with the usual cross-binding argument-type warnings, and **no note that the record's
`DATA_SOURCE` must already be registered**. That is the upstream half of this item, already reported
per the entry's `Upstream:` field.

**The error code, unusually, does explain itself well.** `explain_error_code('SENZ2207')` returns
`EAS_ERR_DATA_SOURCE_CODE_DOES_NOT_EXIST: Data source code [{0}] does not exist.` with actionable
resolution steps: register via `SzConfig::register_data_source(<CODE>)` and commit a new config,
list registered codes to confirm, note that codes are case-sensitive and conventionally UPPERCASE, and
reinitialize the engine afterwards. So a bootcamper who calls `explain_error_code` **is** led to the
fix — which makes this a documentation-and-signposting gap rather than a diagnostic dead end, and is
why it is Low priority rather than higher.

## Proposed change

1. **Name the method where the readiness check happens.** In Phase 1's Senzing-readiness step, offer
   `getRecordPreview` as the authoritative way to see how Senzing interprets a mapped record — and
   state that it requires the record's `DATA_SOURCE` code to be registered first, even though preview
   writes nothing.
2. **Give the ordering explicitly**, since the natural order is the failing one: register the source
   codes (or reuse the registration the loading phase will need anyway), then preview. Obtain the
   registration code from MCP — `sdk_guide(topic='configure')` — rather than hand-writing it (INV-080).
3. **Route `SENZ2207` from this step.** The code's own guidance is good, so the plugin's job is only to
   say "this is expected here, and this is the order" — call `explain_error_code` first as always, and
   do not duplicate its resolution steps.
4. **Keep it optional and non-blocking.** A readiness check that cannot run because registration has
   not happened yet must not block Phase 1 (INV-048); it degrades to the existing specification-based
   review, with the reason reported.

## Acceptance criteria

- [ ] Phase 1's readiness step names `getRecordPreview` and states the registered-`DATA_SOURCE`
      prerequisite.
- [ ] The step gives the working order (register, then preview) and sources the registration code from
      MCP rather than hand-writing it (INV-080).
- [ ] `SENZ2207` at this step routes through `explain_error_code` first, and the plugin does not restate
      its resolution steps.
- [ ] A preview-based check that cannot run does not block Phase 1; the fallback and the reason are
      reported (INV-048).
- [ ] The method's signature is not restated in the plugin as fact — it is obtained per binding via
      `get_sdk_reference` when code is generated (INV-132).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      prerequisite is a property of the engine configuration, not of a platform, and the method name
      differs per binding so the guidance names the canonical operation and defers the spelling to MCP.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` — the
  Senzing-readiness step: introduce the method, its prerequisite, the ordering, and the `SENZ2207`
  route.
- `tests/` — assert the readiness guidance names the prerequisite and does not restate a per-binding
  signature.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "getRecordPreview requires the data source code to
  be registered first" (2026-07-28, Module Data Quality, Mapping, and Transformation;
  `Source: self-observed (assistant retrospective)`; `Routing: both`;
  `Upstream: submitted 2026-07-28`)
- Priority: Low (as filed — it degrades to a diagnosable error with good built-in guidance; the cost is
  discouraging the module's most valuable verification)
- MCP re-check: **still reproduces** on server 1.32.1, 2026-07-28.
  `get_sdk_reference(topic='parameters', filter='getRecordPreview')` returns both overloads for every
  binding with no configuration prerequisite noted. `explain_error_code('SENZ2207')` confirms
  `EAS_ERR_DATA_SOURCE_CODE_DOES_NOT_EXIST` **and** returns good resolution steps — register, list,
  check case, reinitialize — so unlike this session's `SENZ7221` case the error code does lead to the
  fix.
- Upstream: already submitted 2026-07-28 per the entry; **not re-filed**. A follow-up was judged not
  worth sending: the only thing this re-check adds is that the prerequisite is still undocumented on
  the current version, which the original report already asserted.
- Related specs: `specs/sdk-guide-configure-unseeded-datastore.md` (the sibling
  registration/configuration prerequisite, and the `SENZ7221` contrast — an error code whose own
  guidance does *not* name its cause), `specs/verify-sdk-parameter-shapes-and-flag-families.md`
  (INV-132), `specs/mcp-grounding-in-every-skill.md` (INV-080)
