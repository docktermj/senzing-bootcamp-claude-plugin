# `sdk_guide(topic='configure')`'s snippet fails on a freshly created datastore (SENZ7221)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The `RegisterDataSources` snippet returned by `sdk_guide(topic='configure')` assumes a datastore that
already has a registered configuration. Against a **freshly schema-created** SQLite database — exactly
what the same tool's notes tell you to create with `szcore-schema-sqlite-create.sql` — the first two
calls fail: the default config id comes back `0`, and creating a config from id `0` throws

```text
SENZ7221 EAS_ERR_NO_CONFIG_REGISTERED_FOR_DATA_ID
```

So the documented happy path breaks at the one moment it is most likely to be followed: the first
configure step after the install guide's own schema-creation step. A bootcamper hits an engine error
code while doing precisely what two consecutive tool responses told them to do.

## Root cause

**Upstream, in the MCP server's returned snippet — re-verified on server 1.32.1, 2026-07-28**, so this
is current behavior and not a stale report. `sdk_guide(topic='configure', language='python')` returns:

```python
current_config_id = sz_configmanager.get_default_config_id()
sz_config = sz_configmanager.create_config_from_config_id(current_config_id)
```

with `register_config()` + `replace_default_config_id()` below. Every one of those calls presupposes
an existing default config. Three things make the gap hard to see from the response alone:

- **`init_default_config` is present but unsignposted.** It appears only as a bare entry in
  `alternatives` — `{"name": "init_default_config", "source_path": "python/configuration/init_default_config.py"}`
  — with no note that it is the *required* first step on an unseeded datastore. A reader takes the
  primary snippet and never learns the alternative is a precondition rather than a variation.
- **The `notes` do not state the precondition.** They cover adapting `INSTANCE_NAME` and replacing
  sample data-source names; nothing about needing a config to exist.
- **The response's own `compatibility_notes` name the method that would seed it, attached to a
  different instruction.** They say *"After `set_default_config()`, call `env.reinitialize(config_id)`"*
  — but the returned snippet never calls `set_default_config()`; it calls
  `replace_default_config_id()`. `set_default_config(config_definition: str, config_comment: str) -> int`
  does exist on `SzConfigManager` (confirmed via
  `get_sdk_reference(topic='parameters', filter='set_default_config', language='python')`,
  2026-07-28) and is exactly the call that seeds an empty datastore. So the response contains the
  answer, filed under the wrong question.

`explain_error_code('SENZ7221')` (verified 2026-07-28) returns *"No engine configuration registered
with data ID [{0}]"* with generic resolution steps — verify paths, check the connection string, ensure
the engine is initialized. **None of them is the actual remedy** (seed a default config), so the error
code does not lead a reader back to the cause either.

**Plugin-side gap.** The plugin never mentions the seeding path: `init_default_config`,
`set_default_config`, `get_default_config_id` and `SENZ7221` appear **nowhere** in
`plugins/senzing-bootcamp/skills/` (confirmed by grep). Module 2 Step 8 saves the MCP-returned engine
config and Step 9 runs `generate_scaffold(workflow='initialize')` to test the connection, so a
bootcamper whose datastore is unseeded meets SENZ7221 with no guidance in the plugin at all.

## Proposed change

**Upstream (report, do not work around silently) — see `## Source`.** Ask Senzing to either branch the
primary snippet on an unseeded datastore or state the precondition in the notes, and to make
`init_default_config` discoverable as the first step rather than an unannotated alternative.

**In the plugin, meanwhile:**

1. **Name the precondition where the plugin configures the engine.** In Module 2's configure/verify
   steps, state that a freshly schema-created datastore has **no** registered configuration, so a
   config must be seeded before `get_default_config_id()` returns anything useful — and that
   `SENZ7221` is the symptom when it has not been.
2. **Route the error.** Add `SENZ7221` to the module's troubleshooting so the code maps to "seed the
   default config", not to the generic path-and-connection checks `explain_error_code` returns. Keep
   `explain_error_code` as the first call (INV-080) and add the plugin's own known-cause note beside
   it — this is the INV-150 pattern: a detected local condition governs over generic guidance.
3. **Do not hand-write the seeding code.** Obtain it from MCP —
   `sdk_guide(topic='configure')`'s `init_default_config` alternative, or
   `generate_scaffold(workflow='initialize')` — and say which call establishes the config. The plugin
   states *when* and *why*; the MCP server supplies the code (INV-080).
4. **Verify the seed, don't assume it.** After configuring, confirm a default config id is present
   before proceeding, so the failure surfaces at the configure step rather than at the first load.

## Acceptance criteria

- [ ] Module 2's configure/verify guidance states that a freshly schema-created datastore has no
      registered configuration and that one must be seeded first.
- [ ] `SENZ7221` is named in the plugin with its actual cause and remedy, and the guidance still routes
      the error through `explain_error_code` first (INV-080).
- [ ] The seeding code is MCP-sourced, not hand-written in the plugin (INV-080).
- [ ] The configure step confirms a default config id exists before the flow proceeds to loading, so an
      unseeded datastore fails where it is diagnosable rather than at first load.
- [ ] A run against a freshly schema-created SQLite database completes configuration without hitting
      `SENZ7221`.
- [ ] The upstream report is sent (or explicitly declined) and its outcome recorded here.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      precondition is a property of the datastore, not of a platform or binding, and the guidance names
      no language-specific method as authoritative.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 8 (engine configuration) and
  Step 9 (connection test): the precondition, the seed-then-verify step, and `SENZ7221` in
  Troubleshooting.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md` — the Phase 3
  sandbox creates its own datastore, so it needs the same precondition.
- `tests/` — assert the plugin names `SENZ7221` with the seeding remedy and does not hand-write the
  seeding call.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "sdk_guide(topic='configure') snippet fails on a
  fresh datastore (SENZ7221)" (2026-07-28, Modules Data Quality/Mapping/Transformation Phase 3 sandbox
  and Data processing; `Source: self-observed (assistant retrospective)`; `Routing: mcp-server`)
- Priority: High (not stated by the reporter; assessed from impact — the documented path fails outright
  at the first configure step, and the error code's own guidance does not lead back to the cause)
- MCP re-check: **still reproduces on server 1.32.1, verified 2026-07-28.**
  `sdk_guide(topic='configure', language='python')` still returns `get_default_config_id()` →
  `create_config_from_config_id(...)` as the primary snippet with `init_default_config` only as an
  unannotated alternative; `explain_error_code('SENZ7221')` confirms the code and returns no
  seed-the-config remedy; `get_sdk_reference(topic='parameters', filter='set_default_config')` confirms
  `set_default_config(config_definition, config_comment)` exists on `SzConfigManager`.
- Upstream: **sent 2026-07-28 via `submit_feedback` (`category='bug'`)** — the entry recorded it as
  "offered to the bootcamper as a batch" (not yet sent); the maintainer approved the drafted message
  at triage and it was submitted. The submission is **anonymous** — the server captures no sender
  identity, so no follow-up on it is possible; `support@senzing.com` is the channel if this needs a
  conversation. The plugin-side change below stands regardless of whether upstream acts.
- Related specs: `specs/verify-sdk-parameter-shapes-and-flag-families.md` (INV-132),
  `specs/mcp-grounding-in-every-skill.md` (INV-080),
  `specs/reconcile-sdk-guide-license-note-with-detected-limit.md` (INV-150 — the precedent for a
  detected local condition governing over generic MCP guidance),
  `specs/supportpath-failure-code-and-szproduct-masking.md` (the sibling documented-symptom mismatch)
