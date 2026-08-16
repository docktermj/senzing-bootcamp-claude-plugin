# Verify SUPPORTPATH with an engine call, and name the GNR-data diagnostic `SENZ2027` carries

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

> **⚠️ This spec was rewritten on 2026-07-28.** Its first version asserted that a wrong SUPPORTPATH
> surfaces as `SENZ7426` rather than the documented `SENZ2027`, and asked for the plugin's symptom
> code to be broadened accordingly. **The Senzing MCP server contradicts that**, so implementing it
> would have written a false Senzing fact into the plugin. See
> [What changed in this spec, and why](#what-changed-in-this-spec-and-why) at the end for the
> evidence. The surviving substance — verify with an engine call, and carry the real diagnostic — is
> what this spec now asks for.

## Problem

Module 2 configures the Senzing engine and then verifies it. The verification is weaker than it
looks, in a way that lets a broken installation pass.

`module-02-sdk-setup/SKILL.md:675-686` (Step 9, "Test Database Connection") obtains initialization
code via `generate_scaffold(workflow='initialize')` and states its success indicator as *"engine
initializes and connects without errors"*. That is the right intent, but nothing pins **which SDK
class the check must touch**. A check that only proves the SDK imports and reports its version — an
`SzProduct` call — satisfies the wording while proving nothing about whether the engine can
initialize.

That gap matters specifically because the libraries and the support data can be present or absent
**independently**. The Senzing FAQ, verbatim (`search_docs`, verified 2026-07-28 against server
1.32.1):

> **I get SENZ2027 Plugin initialization error GNR data files failed to load** — You are missing the
> senzingsdk-runtime data directory. The libraries are present but the GNR data files (in
> `resources/data/`) are not deployed.

"The libraries are present but the data files are not" is exactly the state a wrong SUPPORTPATH
produces. So an install can load its libraries, answer a version query, and still be unable to
initialize an engine — and Module 2's verification does not require the step that would find out.

The consequence is deferred, not immediate: the version prints, Step 9 passes, and the first real
engine call fails later, several steps from the configuration that caused it.

## Root cause

**Module 2's verification does not specify the class it must exercise.** `:675-686` says "engine
initializes and connects" and delegates the code to
`generate_scaffold(language=…, workflow='initialize')`. That scaffold's snippets cover factory and
environment lifecycle (verified 2026-07-28: `abstract_factory`, `abstract_factory_with_config_id`,
`engine_priming`, `factory_destroy`, `purge_repository`, `signal_handler`,
`sz_engine_config_ini_to_json`), so the generated check *can* create an engine — but the skill's
wording does not require it, and `:43`/`:686`'s success indicators are satisfied by a weaker probe.

**Module 3 System Verification does not close the gap either.** Its phase 1 begins at an MCP
connectivity check (`phase1-verification.md:77`) and its next step generates synthetic records
(`:109`); no step between them exercises SDK initialization, so a masked-through install survives
into data loading (confirmed by grep: `SzProduct`, `SzEngine` and `SzAbstractFactory` appear nowhere
in that module).

**The diagnostic the plugin already names is correct but under-explained.** `:592` says
"initialization failures (e.g., SENZ2027 when SUPPORTPATH is wrong)". `SENZ2027` is right — see the
evidence section — but the text stops at the code. It does not carry the FAQ's actual finding (the
runtime **data directory** is missing), which is the sentence that turns the error into an action,
and which lines up exactly with the Windows/Scoop sibling-directory case the `Test-Path` check at
`:598-630` already handles.

## Proposed change

1. **Require the verification to exercise an engine-class call.** In Step 9, state that the check
   MUST create and use an `SzEngine` (or `SzDiagnostic`) — not only `SzProduct.getVersion()` — so a
   configuration that cannot initialize fails at the step designed to catch it. Keep the code
   MCP-generated (`generate_scaffold(workflow='initialize')`); this constrains **which class the
   generated check must touch**, not how the code is obtained (INV-080). Update the success
   indicators at `:43` and `:686` so they cannot be satisfied by a version probe.
2. **Say why a version check is insufficient**, in the terms the FAQ supports: the libraries and the
   support data can be present independently, so proving the SDK imports does not prove the engine can
   initialize. Do **not** assert the stronger per-class claim (that `SzProduct` succeeds while every
   `SzEngine`/`SzDiagnostic` call fails) — no MCP source states it; see the evidence section.
3. **Carry the real diagnostic next to the SUPPORTPATH check.** At `:592` and in the Windows block at
   `:598-630`, add the FAQ's finding: `SENZ2027` with "GNR data files failed to load" means the
   runtime **data directory** is not where the configuration points — which is the Scoop
   sibling-directory case that block already fixes. Quote it as MCP-sourced with its date, and keep
   `explain_error_code` as the first call for any SENZ code (INV-080).
4. **Do not name `SENZ7426`.** It is a transliteration error, unrelated to SUPPORTPATH (see the
   evidence section). A test should assert the plugin does not tie it to SUPPORTPATH, so the retracted
   claim cannot be reintroduced.

## Acceptance criteria

- [ ] Module 2's Step 9 requires an `SzEngine` or `SzDiagnostic` call, and its success indicators
      (`:43`, `:686`) cannot be satisfied by an `SzProduct`-only probe.
- [ ] The verification code is still obtained from MCP rather than hand-written (INV-080).
- [ ] Module 2 states that libraries and support data can be present independently, so a version
      query does not validate the engine — without asserting the unverified per-class masking claim.
- [ ] `SENZ2027`'s entry names the runtime data directory as the thing to check, quoted from
      `search_docs` with its verification date, and `explain_error_code` remains the first call.
- [ ] The existing Windows `Test-Path` SUPPORTPATH check and its Scoop rationale are unchanged — this
      spec adds to them and removes nothing.
- [ ] `SENZ7426` is not presented anywhere as a SUPPORTPATH symptom, and a test asserts it.
- [ ] Module 3's phase 1 reports an SDK/engine initialization failure explicitly and routes it via
      `explain_error_code`, so a masked-through install cannot reach data loading.
- [ ] Every Senzing fact added carries its provenance (tool, parameters, server version, date) and
      none is asserted from training data or from this spec's earlier version (INV-080, INV-169).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      SUPPORTPATH `Test-Path` check stays Windows-gated as today, while "exercise an engine call"
      applies on every platform and in every binding, since each has both classes.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — `:592` (the diagnostic), `:598-630`
  (the Windows SUPPORTPATH block), `:675-686` (Step 9) and the success indicators at `:43` / `:686`.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — an
  initialization failure is reported explicitly and routed via `explain_error_code`.
- `tests/` — assert the engine-class requirement, the `SENZ2027` diagnostic wording, and that
  `SENZ7426` is never tied to SUPPORTPATH.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "SUPPORTPATH failure presents as SENZ7426 with
  SzProduct still succeeding — documented code is SENZ2027" (2026-07-28, Module SDK setup;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin`; `Upstream: not applicable`).
  The entry itself recorded that the failure "was not hit in its damaging form" and that the
  error-code and masking details "come from the SDK's documented behavior for that path and were noted
  while writing the configuration" — i.e. inference, not observation. That caveat is why the
  re-verification below matters, and it was under-weighted when this spec was first written.
- Priority: Medium
- MCP re-check: server **1.32.1**, 2026-07-28 — **the entry's central claim is refuted; the plugin was
  already correct.** `explain_error_code('SENZ7426')` → `EAS_ERR_XLITERATOR_FAILED: Transliteration
  failed`, causes listed as malformed input data, missing `DATA_SOURCE`/`RECORD_ID`, invalid JSON
  encoding — nothing about SUPPORTPATH. `explain_error_code('SENZ2027')` →
  `EAS_ERR_PLUGIN_INIT: Plugin initialization error`, and `search_docs` returns the FAQ quoted above
  tying it to a missing runtime data directory. The masking claim is neither confirmed nor refuted by
  any MCP source.
- Upstream: not applicable (plugin-side)
- Related specs: `specs/sdk-guide-configure-unseeded-datastore.md` (the sibling Module 2
  configure-step defect, and the `SENZ7221` precedent for an error whose own guidance does not name
  its cause), `specs/artifact-level-verification-for-deliverables.md` (INV-129 — verify the thing,
  not the exit status; this is its SDK-install analog),
  `specs/mcp-grounding-in-every-skill.md` (INV-080),
  `specs/export-related-entities-is-flag-conditional.md` (INV-169 — the rule this spec's first
  version violated)

## What changed in this spec, and why

Rewritten 2026-07-28 after `implement-spec`'s Step 3.3 re-verification refuted its central claim.
The maintainer chose to route it back for rewrite rather than implement a partial version.

**Dropped — `SENZ7426` as a SUPPORTPATH symptom.** The first version asked to broaden `:592` to name
`SENZ7426` "as well as `SENZ2027`", on the strength of the feedback entry. Verified 2026-07-28 on
server 1.32.1, `SENZ7426` is `EAS_ERR_XLITERATOR_FAILED: Transliteration failed`, documented with
input-data causes; no MCP source connects it to SUPPORTPATH. Meanwhile `SENZ2027`
(`EAS_ERR_PLUGIN_INIT`) **is** the documented missing-GNR-data symptom. The plugin's existing text
was correct, and implementing the original spec would have introduced a false Senzing fact — the
failure INV-169 exists to prevent. Criterion 6 above now guards against reintroducing it.

**Weakened — the masking claim.** The first version asked the plugin to state that `SzProduct`
succeeds while every `SzEngine`/`SzDiagnostic` call fails. No MCP source states that. What the FAQ
does support is the weaker and sufficient point now in change 2: libraries and support data can be
present independently, so a version query does not validate the engine.

**Kept — the engine-call requirement.** This was the first version's item 3 and the part it called
"the important one". It is sound independently of which error code appears: a version probe is a
weaker check than an engine call, so the step meant to catch a bad configuration should make one.

**Added — the FAQ diagnostic.** Found by the same re-verification and absent from the first version:
`SENZ2027` + "GNR data files failed to load" means the runtime data directory is missing, which is
more actionable than the bare code and matches the Scoop sibling-directory case the Windows block
already handles.
