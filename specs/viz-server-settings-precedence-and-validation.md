# Viz server prefers a stub settings file over a correct env var, and validates neither

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`senzing_viz_server.py` resolves engine settings from a **file that wins over the
environment variable**, falls back to the env var only when the file is *absent*, and
then validates neither. A `config/engine_config.json` containing `{"PIPELINE": {}}` —
syntactically valid, semantically empty — therefore silently defeats a correctly
populated `SENZING_ENGINE_CONFIGURATION_JSON`, and the run fails deep inside the engine
with an error that points somewhere else entirely.

Observed in the dry run (2026-08-13), with the SDK present and `LD_LIBRARY_PATH` set,
a correct env var exported, and a stub settings file on disk:

```text
2026-08-13 09:59:36 [szstatic] ERR: No transliteration rules found! Transliteration
requires at least one module.
Could not build entity model: SzBadInputError: SENZ7426|Transliteration failed: No
transliteration rules found! Transliteration requires at least one module.
```

Nothing in that output names the settings file, the empty `PIPELINE`, or the fact that
the exported env var was never read. The reported cause is transliteration; the actual
cause is an empty `SUPPORTPATH` because the wrong settings source won.

**The misdiagnosis is actively steered by the plugin's own guidance.** `SENZ7426` is
documented — MCP's `sdk_guide(topic='install', platform='macos_arm')` gotcha and the
plugin's SENZ7426 material both say it means `SUPPORTPATH` is wrong and is *not* a
broken install. A bootcamper who reads that will go and fix a `SUPPORTPATH` that is
already correct in the place they are looking (the env var), because the value actually
in force came from a file they were not told was preferred.

## Root cause

`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1704-1710`:

```python
if os.path.exists(args.settings):
    with open(args.settings, encoding="utf-8") as _sf:
        settings = _sf.read()
else:
    settings = os.getenv("SENZING_ENGINE_CONFIGURATION_JSON", "")
if not settings:
    sys.stderr.write("No engine settings (missing --settings file and env var).\n")
```

Two distinct defects:

1. **Precedence is existence-based, not content-based, and is undocumented.** The
   docstring at `:63-64` says settings come from `--settings` (default
   `config/engine_config.json`) "or the `SENZING_ENGINE_CONFIGURATION_JSON` env var",
   which states no order. A reader cannot tell that a stub file beats a good env var.
2. **`if not settings` only catches an empty *string*.** `{"PIPELINE": {}}` is truthy,
   so the emptiness check passes and the run proceeds into `build_model` with no
   `CONFIGPATH`, `RESOURCEPATH` or `SUPPORTPATH`.

The plugin already knows this hazard in the *other* direction:
`module-02-sdk-setup/SKILL.md:578` records that `export
SENZING_ENGINE_CONFIGURATION_JSON=""` "sails straight past that check and fails later".
The same reasoning was never applied to the file branch.

Reachability is not hypothetical. `module-02-sdk-setup/SKILL.md:878` writes the settings
to `config/engine_config.json`, `module-02-sdk-setup/SKILL.md:561` exports the env var,
and `module-03b-truthset-visualization/phase1-visualization.md:184-187` runs
`senzing_viz_server.py` directly on the Python path — where `--settings` defaults to that
file. Any divergence between the two (a file written before the settings were complete,
then corrected only in the shell) lands exactly here.

To be explicit about what the dry run did **not** establish: the happy path was never
reached. With a complete settings file the run advanced to a different, unrelated
environment error (`SENZ7317|Failed to open file: …/etc/cfgVariant.json`, this POC
layout needing `sz_create_project`), so the fix below is verified against the failure
modes only.

## Proposed change

1. **Validate the chosen settings before building the model.** After resolving
   `settings`, parse it and require a non-empty `PIPELINE` carrying `CONFIGPATH`,
   `RESOURCEPATH` and `SUPPORTPATH`. On a shortfall, fail with a message that names
   **which source was used**, **its path or `$SENZING_ENGINE_CONFIGURATION_JSON`**, and
   **which keys are missing** — never proceed into the engine. This keeps the existing
   contract (fail loudly, write no snapshot) while making the reported cause the real
   one (INV-111).
2. **Make the precedence content-aware, or at least loud.** Preferred: if the file
   resolves to settings with an empty/incomplete `PIPELINE` *and* a populated
   `SENZING_ENGINE_CONFIGURATION_JSON` is present, use the env var and say so on stderr.
   Minimum: keep file-wins but emit a stderr line naming the source whenever both are
   present and they differ, so the losing source is never silently discarded.
3. **State the precedence in the docstring** at `:63-64`, replacing "or" with the actual
   order and the tie-break.

Fix the class: the same existence-over-content precedence should be checked in any other
bundled script that accepts both a settings file and the env var.

## Acceptance criteria

- [x] With a `{"PIPELINE": {}}` settings file present, the script exits non-zero, writes
      no snapshot, and its stderr names the settings **source** and the **missing
      `PIPELINE` keys** — and does not present transliteration as the **cause**.
      ⚠️ **Criterion refined during implementation, deliberately and recorded here rather
      than silently.** As first written it said "does not mention transliteration" at all.
      That is too strict: naming `SENZ7426` as what *would* have happened, and saying it
      points at `SUPPORTPATH` rather than at this file, is exactly the sentence that saves
      the reader who has already seen the error and is searching for it. What must not
      happen is transliteration being reported as the cause. The guard pins the refined
      form — the headline (first) line must name the incomplete settings, and must not
      contain "transliteration".
- [ ] With a stub file present and a populated `SENZING_ENGINE_CONFIGURATION_JSON`, the
      env var's values are the ones used, and stderr says which source won.
- [ ] With both present and populated but differing, stderr names the source in force.
- [ ] With neither present, the existing "No engine settings" message is unchanged.
- [ ] The docstring states the precedence order explicitly.
- [ ] A repo-level stdlib-only test in `tests/` covers the stub-file case without
      requiring the Senzing SDK (assert on the message and the absent snapshot, not on
      engine behavior) — per INV-108.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — settings resolution at
  `:1689` / `:1704-1710`, and the docstring at `:63-64`.
- `tests/test_viz_settings_resolution.py` — new guard.
- Possibly `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md`
  — if the run instruction should pass `--settings` explicitly rather than relying on the default.

## Source

- Feedback: none — dry run phase 2 (2026-08-13), bundled-script execution
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — non-blocking and agent-side, but it manufactures a misleading
  diagnosis that the plugin's own SENZ7426 guidance then reinforces, on the Python
  visualization path a bootcamper actually runs.
- MCP re-check: server 1.32.9, 2026-08-13 — the `SENZ7426` meaning was confirmed against
  `sdk_guide(topic='install', platform='macos_arm')`, whose gotcha states the error
  "means SUPPORTPATH is WRONG — it is NOT a broken install". That is what makes the
  misdirection costly, and it is correct guidance being applied to a wrongly-reported
  cause. No Senzing fact in this spec is contradicted by the server.
- Upstream: not applicable — the defect is in the plugin's script, not the server.
- Related specs: none
