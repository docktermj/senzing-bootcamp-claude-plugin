# `explain_error_code('SENZ7221')` now names the cause and the fix; the plugin says it does not

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-02-sdk-setup/SKILL.md` tells the guide, in two places, that `SENZ7221`'s own
explanation is useless and misleading — and instructs it to **disregard** the tool's
resolution steps. On server 1.32.2 that is false, and the steps it says to ignore are the
correct fix.

What the plugin says now (`module-02-sdk-setup/SKILL.md:780-782`):

> The error names no remedy — `explain_error_code('SENZ7221')` returns "No engine
> configuration registered with data ID" and resolution steps about paths, connection
> strings and initialization, **none of which is the actual fix**.

and again at `:856-860`:

> Call `explain_error_code('SENZ7221')` first as always (INV-080), but know that its
> resolution steps (verify paths, check the connection string, ensure the engine is
> initialized) do **not** name this cause, so **do not be pulled toward re-checking
> paths** that are already correct.

What the server returns — `explain_error_code('SENZ7221')`, server 1.32.2, docs indexed
2026-07-29 11:11 UTC, 2026-07-30:

```text
common_causes[0]: "No default config has EVER been registered on this datastore — it was
                   schema-created (e.g. via szcore-schema-*-create.sql) but never seeded"
common_causes[1]: "get_default_config_id() returned 0, and create_config_from_config_id(0)
                   was called with that unseeded value"
common_causes[2]: "Config was registered by a different datastore/database than the one
                   this engine instance is pointed at"

resolution_steps[0]: "Seed a default config first: create_config_from_template() (or
                      create_config()), then set_default_config(config_json, comment) —
                      see sdk_guide topic='configure' (called WITHOUT data_sources, this
                      returns the seeding snippet)"
resolution_steps[1]: "Do NOT call create_config_from_config_id() until
                      get_default_config_id() returns a nonzero id — check the id first"
resolution_steps[2]: "Verify SENZING_ENGINE_CONFIGURATION_JSON's SQL.CONNECTION points at
                      the datastore you actually seeded, not a different one"
```

`common_causes[0]` **is** the plugin's own diagnosis, almost word for word, and
`resolution_steps[0]` **is** the plugin's own remedy (Step 8a's seeding) including the
same `sdk_guide(topic='configure')` route the plugin recommends.

**Why this is worse than ordinary staleness.** The other stale claims found this week said
"the server does not cover X" and merely cost a redundant lookup. This one tells the guide
that the tool's answer is a *wrong direction* and to resist it. A guide that follows the
plugin will read three accurate, ordered resolution steps and discount them — the plugin
is now the thing pulling the reader away from the fix. That inverts INV-080, which exists
to route the guide **to** MCP.

It is also the fourth instance this week of one defect class: **the plugin characterising
what an MCP tool returns, and the characterisation going stale** (after INV-132's
`flags`/`response_schemas` claim, the `response_schemas` top-level claim, and
`reporting_guide`'s gating). A claim about a tool's *output* has no test that can catch it
and no reason to be revisited.

## Root cause

The characterisation was accurate when written (2026-07-28, server 1.32.1) and nothing
re-asks a negative claim about a tool's output. Senzing improved this specific code's
entry — `SENZ2027`, checked the same day, is still a stub returning a placeholder cause —
so richness varies per code and cannot be inferred from one sample.

## Proposed change

1. **`module-02-sdk-setup/SKILL.md:780-782`** — replace "the error names no remedy" with
   what the tool now returns: it names the unseeded-datastore cause first and the
   seeding remedy first. Keep the passage's real teaching, which is unaffected: the error
   surfaces several steps from its cause, and seeding first avoids it entirely.
2. **`module-02-sdk-setup/SKILL.md:856-860`** — delete the "do not be pulled toward
   re-checking paths" caution and say instead that the tool's steps now lead to the fix,
   with `resolution_steps[2]` (wrong datastore) as a genuine third possibility rather than
   a distraction. **Keep** the `explain_error_code` call itself (INV-080) and keep the
   pointer to Step 8a.
3. **Add the provenance stamp** both places: server 1.32.2, 2026-07-30.
4. **Do not generalise to other codes.** `SENZ2027` remains a stub — verified the same
   day — and the plugin's compensating text for it is still correct and must stay. Any
   wording introduced here must be about `SENZ7221` specifically, not about
   `explain_error_code` in general.

## Acceptance criteria

- [ ] Neither site claims `SENZ7221`'s explanation lacks a remedy, and neither instructs
      the guide to discount its resolution steps.
- [ ] Both sites still call `explain_error_code('SENZ7221')` first (INV-080) and still
      route to Step 8a's seeding.
- [ ] Both carry `MCP server 1.32.2, 2026-07-30`.
- [ ] The `SENZ2027` guidance is untouched and still says its resolution steps do not name
      the missing-runtime-data cause — that claim was re-verified 2026-07-30 and stands.
- [ ] **Re-verification clause:** implementing this requires
      `explain_error_code('SENZ7221')` to still return the unseeded-datastore cause and
      the seeding remedy. If it has reverted to a generic entry, the plugin's original
      caution is right again and this spec must be re-triaged, not implemented.
- [ ] `tests/test_config_seeding_guidance.py` and
      `tests/test_engine_verification_and_senz2027.py` pass; any assertion quoting the
      removed wording is updated.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — lines 780-782 and 856-860.
- `tests/` — any assertion pinning the removed wording.

## Source

- Sweep: `delegate-to-mcp-server`, 2026-07-30 (seventh pass — both server axes unchanged,
  so the run covered un-ledgered sites only), ledger key `senz7221-names-no-remedy`
- Verdict: `contradicted`
- MCP evidence: server 1.32.2, docs indexed 2026-07-29 11:11 UTC, 2026-07-30 —
  `explain_error_code('SENZ7221')`, quoted above.
- Priority: **High for this class** — not because the bootcamp breaks, but because the
  plugin actively directs the guide away from a correct answer, which is the inverse of
  what INV-080 exists to do.
- Upstream: not applicable — the server improved; the plugin is stale.
- Related specs: `specs/sdk-reference-carries-signatures-under-every-topic.md`,
  `specs/response-schemas-now-documents-match-info-depth.md`,
  `specs/reporting-guide-topics-gate-on-language.md` — the same defect class, same week.
