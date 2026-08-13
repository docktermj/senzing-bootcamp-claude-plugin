# No license-path environment variable

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two places in the plugin assume Senzing reads a license *path environment variable*.
The live MCP server documents no such variable — not under either name the plugin has
used. The consequences differ by site:

1. `graduation/SKILL.md:749` writes `SENZING_LICENSE_PATH` into the `.env.example`
   the bootcamper carries into production. It is a fabricated environment variable in
   a shipped deliverable: a bootcamper who sets it gets no license, and the failure
   surfaces later as a capacity error (`SENZ9000|LIMIT`) with nothing pointing back at
   the empty variable.
2. `module-02-sdk-setup/SKILL.md:717-725` states a "license check order" whose second
   step is "a license-path environment variable", then ⛔-instructs the guide to
   "Confirm the environment variable's exact name from MCP before naming it to the
   bootcamper". That instruction is **unsatisfiable**: MCP has no name to return, and
   the note supplies no fallback for that outcome, so a guide following it faithfully
   calls the server, gets nothing, and is left improvising in exactly the place the
   note exists to prevent improvisation.

The module-02 note is self-aware about the risk — it records that the text "previously
hardcoded `SENZING_LICENSE_PATH` while `sdk_guide` returns `SENZING_LICENSE_FILE`; the
two differ by one word and neither was verified here". Neither is right, and the wrong
one of the two is still live in graduation.

## Root cause

The plugin models licensing as an environment variable. Senzing models it as an
**engine-configuration `PIPELINE` key**. The plugin already knows this in two other
places — `module-04-data-collection/SKILL.md:616-617` correctly writes `LICENSEFILE`
into the PIPELINE section, and `module-02-sdk-setup/SKILL.md:769` describes "wiring
`LICENSEFILE`" — so the defect is a stale third model surviving alongside the correct
one, not a misunderstanding.

Live MCP server, **1.32.9, verified 2026-08-13**:

- `sdk_guide(topic='configure', language='python', platform='linux_apt')` — the
  `environment.env_vars` map contains exactly two entries, `LD_LIBRARY_PATH` and
  `PYTHONPATH`. No license variable. Its `engine_config_notes` state the license
  options outright: "License options: LICENSESTRINGBASE64 (inline base64 string in
  config — preferred for containers/automation) or LICENSEFILE (path to .lic file on
  disk)", both shown inside `"PIPELINE"`.
- `sdk_guide(topic='install', platform='macos_arm')` — same: license appears only as
  `LICENSESTRINGBASE64` / `LICENSEFILE` under `PIPELINE`.
- `search_docs(query='license file environment variable SENZING_LICENSE_FILE path')` —
  returns EULA/pricing prose only, no variable name.

So `SENZING_LICENSE_FILE` is also not returned by `sdk_guide` today, whatever it
returned when the module-02 note was written. The note's premise has expired; the
premise it warns against is a confabulation either way ("Wrong file paths and
environment variables" is on the server's own `common_confabulations` list).

`SENZING_ENGINE_CONFIGURATION_JSON` is fine to keep in `.env.example` — the server
names it, with the caveat that it "is a naming convention used by POC tools and most
official examples. It is NOT required by the SDK."

## Proposed change

1. **`graduation/SKILL.md:749`** — drop `SENZING_LICENSE_PATH` from the `.env.example`
   key list. Licensing belongs inside the `SENZING_ENGINE_CONFIGURATION_JSON` value as
   a `PIPELINE` key, so add a comment line to that effect instead of a separate
   variable: the example should show `LICENSEFILE` (or `LICENSESTRINGBASE64`) as a
   commented-out `PIPELINE` entry within the engine-config placeholder, matching what
   `module-04-data-collection/SKILL.md:616` already does.
2. **`module-02-sdk-setup/SKILL.md:717-725`** — correct the license check order to
   drop the environment-variable step, and replace the unsatisfiable ⛔ note with the
   positive fact: there is no license-path environment variable; a custom license is
   supplied as a `PIPELINE` key (`LICENSEFILE` for a `.lic` path,
   `LICENSESTRINGBASE64` for an inline key). Keep the INV-080 routing for the
   *record-capacity figure*, which the server does answer and which must still not be
   hardcoded.

Fix the class, not just the instance: any remaining `SENZING_LICENSE_*` spelling in
the plugin is wrong by construction, so a guard should assert the plugin contains no
`SENZING_LICENSE_` token at all rather than blocking one of the two spellings.

## Acceptance criteria

- [ ] No file under `plugins/` contains the token `SENZING_LICENSE_` in any spelling.
- [ ] `graduation/SKILL.md`'s `.env.example` description names no license environment
      variable, and expresses a custom license as a `PIPELINE` key.
- [ ] `module-02-sdk-setup/SKILL.md` Step 5 states that no license-path environment
      variable exists, and its license check order has no environment-variable step.
- [ ] Module-02 Step 5 still routes the evaluation-license **record limit** to
      `sdk_guide(topic='load', …, record_count=…)` and hardcodes no figure (INV-080).
- [ ] A repo-level stdlib-only test in `tests/` enforces the first criterion, and
      fails when `SENZING_LICENSE_PATH` is reintroduced at `graduation/SKILL.md:749`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — remove the fabricated
  variable from the `.env.example` key list; express license as a PIPELINE key.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — correct the license
  check order and replace the unsatisfiable confirm-from-MCP note.
- `tests/test_license_env_var_absent.py` — new guard for the class.

## Source

- Feedback: none — dry run phase 1 (2026-08-13), MCP call-contract sweep
  (`Source: self-observed (assistant retrospective)`)
- Priority: High — a fabricated environment variable ships to the bootcamper in a
  production deliverable, and the compensating instruction cannot be followed.
- MCP re-check: server 1.32.9, 2026-08-13 — **server contradicts the plugin**. Called
  `sdk_guide(topic='configure', language='python', platform='linux_apt')`,
  `sdk_guide(topic='install', platform='macos_arm')`, and
  `search_docs(query='license file environment variable SENZING_LICENSE_FILE path')`.
  None returns any license environment variable; all license references are
  `PIPELINE.LICENSEFILE` / `PIPELINE.LICENSESTRINGBASE64`.
- Upstream: not applicable — the plugin is wrong here, not the server.
- Related specs: none
