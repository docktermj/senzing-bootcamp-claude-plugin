# TODO

This are ideas for future specs.

- **✅ DONE 2026-07-28 — rewritten.** `specs/supportpath-failure-code-and-szproduct-masking.md`
  was rewritten against what the server actually says; see its "What changed in this spec, and
  why" section. The evidence is kept below because it is the reason the spec reads as it now does.
- **~~Rewrite `specs/supportpath-failure-code-and-szproduct-masking.md` — its central claim is false.~~**
  Routed back from `implement-spec` on 2026-07-28 (option (b): left unimplemented, not recorded in
  `IMPLEMENTED.md`). Re-verified against MCP server 1.32.1 that day:
  - `explain_error_code('SENZ7426')` → `EAS_ERR_XLITERATOR_FAILED: Transliteration failed`, with
    documented causes of malformed input data, missing `DATA_SOURCE`/`RECORD_ID`, invalid JSON
    encoding. **Nothing connects it to SUPPORTPATH.**
  - `explain_error_code('SENZ2027')` → `EAS_ERR_PLUGIN_INIT: Plugin initialization error`, and
    `search_docs` returns a Senzing FAQ titled *"I get SENZ2027 Plugin initialization error GNR data
    files failed to load"*: *"You are missing the senzingsdk-runtime data directory. The libraries are
    present but the GNR data files (in `resources/data/`) are not deployed."*
  - So `SENZ2027` **is** the documented symptom of missing support/GNR data, and
    `module-02-sdk-setup/SKILL.md:592`'s existing text is correct. Implementing the spec's item 1
    (broaden the symptom to `SENZ7426`) would write a false Senzing fact into the plugin (INV-080,
    INV-169). The feedback entry itself said the failure "was not hit in its damaging form" and that
    the code came from inference while writing the configuration.
  - The `SzProduct`-succeeds-while-`SzEngine`-fails masking claim is **neither confirmed nor refuted**
    by any MCP source. The FAQ supports only a weaker form: the libraries can load while the support
    data is absent, so a check proving the SDK imports does not prove the engine can initialize.
  - **Worth keeping from the spec:** item 3 — the SDK-verification step should exercise an `SzEngine`
    (or `SzDiagnostic`) call rather than only `SzProduct.getVersion()`. That is sound regardless of
    which code appears, and is the part the spec itself called the important one.
  - **Worth adding, MCP-sourced:** the FAQ's diagnostic is more actionable than what either the plugin
    or the spec says — `SENZ2027` + "GNR data files failed to load" means the runtime **data
    directory** is missing, which is exactly the Windows/Scoop sibling-directory case Step 8's
    `Test-Path` check already handles.
