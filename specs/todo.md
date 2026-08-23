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
  - **✅ SUPERSEDED 2026-07-31 — the masking claim is now MCP-confirmed, by a different tool.**
    `sdk_guide(topic='install', platform='windows')` (server 1.32.2) states that a `SUPPORTPATH`
    built as `%SENZING_DIR%\data` makes "every SzEngine/SzDiagnostic call … fail with `SENZ7426`
    … **while SzProduct keeps working — so the install looks healthy**". Both halves the 2026-07-28
    check could not establish. Recorded in `module-02-sdk-setup/SKILL.md` beside the existing
    masking warning, attributed to `sdk_guide`. **The 2026-07-28 reasoning below stands as written**
    — it was correct on the evidence available, and the correction is the point: that check asked
    `explain_error_code`, which *still* makes no SUPPORTPATH connection (re-verified 2026-07-31).
    "The server does not cover X" is only ever "the tool I asked does not cover X".
    (Source: `windows-scoop-facts-the-server-now-owns`.)
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

- **✅ RESOLVED 2026-07-31 — the `auto-test` skill is tracked; this entry was stale.**
  ~~The `auto-test` skill and its 11 tests are untracked, deliberately.~~ All seven files
  (`.claude/skills/auto-test/{SKILL.md,autotest.py,mcp_probe.py,walk.py,transcript_lint.py,baseline/mcp-snapshot.json}`
  and `tests/test_auto_test_harness.py`) are in git, added by **`47d108d`**
  *"#1 test(auto-test): add the auto-test skill and its harness test"*. The test count (11) was
  right. **The consequence of leaving this uncorrected was the real cost:** the entry instructed a
  reader to discount every suite figure by 11, which would have made every count reported since
  wrong. Verified with `git ls-files` and `git log --diff-filter=A`.

- **Senzing web app as a curriculum option.** Bootcamper suggestion, 2026-07-27 (Module 0), no detail
  given before they returned to the bootcamp — recorded in `feedback/PROCESSED.jsonl` as
  `needs-clarification`. The curriculum is SDK-code-focused; `truthset_visualization` is the one
  existing web-app-based module. Needs a scoping conversation — which modules, alongside or instead
  of generated SDK code — before it can be specced.

- **Point Module 7's query-program guidance at the factory-lifetime rule.** The rule is already
  shipped and correct — `bootcamp-onboarding/ground-rules.md:322`, landed 2026-07-26 by `341bbe4`
  from `factory-must-outlive-every-engine-it-creates` — and it still did not bind: a 2026-08-18 run
  on plugin 0.5.1 wrote a shared helper that created `SzAbstractFactoryCore` as a local and returned
  only the engine, which failed on the first call with `SzSdkError - engine object has been
  destroyed and can no longer be used, create a new one`. Factoring engine setup into a helper is
  the first move anyone makes when writing five query programs, so
  `module-07-query-visualize-discover/phase1-query-visualize.md` Step 2 (Create query programs) is
  the point of use and carries no pointer. One line there, next to the existing INV-115 response-shape
  block. Source: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Joel.md` → "an SzAbstractFactoryCore kept as a
  local destroys its engine when it goes out of scope" (`self-observed`, Medium). Senzing's own
  `search_docs(query='loading', category='anti_patterns')` covers the adjacent thread-safety rule
  ("Do Not Initialize Factory or Environment Per Call or Thread") and not the object-lifetime angle
  — re-checked server 1.33.0, 2026-08-21.
