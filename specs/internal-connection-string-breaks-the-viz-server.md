# Reject the `internal://` connection string — it silently empties the visualization server

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The bootcamp is a **multi-process** application, but the MCP server recommends a
**single-process-only** database connection string, and the plugin has no rule against
adopting it. An assistant that follows the server's advice — which the plugin instructs it
to read at runtime — produces a bootcamp where every load reports success and the
visualization then renders an empty graph, with nothing in either output naming the cause.

`sdk_guide(topic='install', platform='macos_arm', language='java')` returns this in
`engine_config_notes` (server 1.32.9, verified 2026-08-14):

> For quick single-process dev/test on v4.3+, use `internal://` as the connection string —
> zero setup, in-memory, no schema creation needed. Limitation: `internal://` is confined to
> a single process via the SDK; it cannot be shared across processes, persisted, or used with
> external tools.

The recommendation and the disqualifying limitation sit in one note, and the
recommendation reads first. `internal://` appears **zero** times anywhere under `plugins/`,
so the plugin neither adopts it nor forbids it.

## Root cause

The bootcamp writes records in one process and reads them from another, so a connection
string that cannot be shared across processes cannot work — but nothing states that.

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1511-1517` builds its **own**
  engine in its **own** process: `from senzing_core import SzAbstractFactoryCore`, then
  `SzAbstractFactoryCore("bootcamp_viz", settings, verbose_logging=False)` followed by
  `factory.create_engine()`. Its settings come from the project's engine-config file or
  `$SENZING_ENGINE_CONFIGURATION_JSON` (`senzing_viz_server.py:68`), i.e. the same
  `CONNECTION` the loading scripts use.
- The loads run in a separate process, driven by `generate_scaffold(workflow='add_records')`
  code (`plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md:191`).

So with `CONNECTION` set to `internal://`, the loader populates a per-process in-memory
datastore that is discarded at exit, and the viz server's separate process opens an empty
one. Both processes exit 0.

This is the failure INV-077 exists to prevent — a blank visualization that satisfies a
file-exists check — reached by a route the plugin does not guard. The plugin already has the
correct convention for this exact shape one level up: INV-200 in
`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:288-291` says to
"Override MCP-suggested paths (e.g. `/tmp/`, `ExampleEnvironment`) to project-relative
ones", binding tool **arguments** and not only writes. An MCP-suggested *connection string*
is the same class of hazard and has no equivalent rule.

The plugin's own SQLite guidance is correct and unaffected: it uses an absolute
`sqlite3://na:na@/absolute/path/to/<project>/database/G2C.db`
(`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:989`) and applies
`szcore-schema-sqlite-create.sql` (`module-02-sdk-setup/SKILL.md:1261`). Nothing about the
persistent path needs to change — only the absence of a rule forbidding the in-memory
alternative.

## Proposed change

1. Add a ⛔ rule to `ground-rules.md`'s "File placement" section, immediately after the
   INV-200 path-override rule it generalizes, forbidding `internal://` for the bootcamp's
   `CONNECTION` and giving the reason in terms the assistant can check: the bootcamp runs the
   visualization server as a separate process against the same datastore, so the datastore
   must be persistent and shareable. State that this holds even though `sdk_guide` recommends
   `internal://`, and cite the same response's own limitation clause as the justification —
   so the rule reads as applying the server's note rather than contradicting the server.
2. Register the invariant as **INV-231** in `specs/INVARIANTS.md` (INV-230 is currently the
   highest), naming `ground-rules.md` so the rule is reachable from the step that needs it
   (INV-183).
3. Add `tests/test_internal_connection_string_rejected.py` — stdlib only, no `plugins/`
   import (INV-108) — asserting the prohibition is present in shipped text and that no file
   under `plugins/` ever offers `internal://` as a `CONNECTION` value.

## Acceptance criteria

- [ ] `ground-rules.md` contains a ⛔ rule forbidding `internal://` as the bootcamp's
      `CONNECTION`, citing the multi-process viz server as the reason.
- [ ] The rule cites INV-231, and INV-231 is registered in `specs/INVARIANTS.md` naming
      `ground-rules.md`.
- [ ] A test fails if the prohibition is removed from shipped text, and fails if any file
      under `plugins/` proposes `internal://` as a connection string. Negative-controlled in
      both directions.
- [ ] The persistent SQLite guidance in `module-02-sdk-setup/SKILL.md` is unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — add the ⛔
  `internal://` prohibition after the INV-200 path-override rule.
- `specs/INVARIANTS.md` — register INV-231.
- `tests/test_internal_connection_string_rejected.py` — new guard.

## Source

- Feedback: none — found by `/dry-run` phase 1 on 2026-08-14 (`Source: self-observed
  (assistant retrospective)`), by diffing the live `sdk_guide` response's
  `engine_config_notes` against the plugin's process model.
- Priority: Medium — the documented path still works; this is a latent trap whose failure is
  silent and lands three modules after the mistake.
- MCP re-check: server 1.32.9, 2026-08-14 — server now contradicts the plugin's
  architecture. Called `get_capabilities` and
  `sdk_guide(topic='install', platform='macos_arm', language='java')`. The server carries
  both the `internal://` recommendation and its single-process limitation in one
  `engine_config_notes` entry, so this rests on no absence claim about the server: the fact
  is served, and the gap is that the plugin states no rule.
- Upstream: not applicable — the server's note is accurate and self-consistent; the missing
  rule is ours.
- Related specs: none
