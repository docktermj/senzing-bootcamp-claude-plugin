# The Windows/Scoop install facts: one is contradicted, and one the server refused to confirm it now confirms

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

One call — `sdk_guide(topic='install', platform='windows')`, server 1.32.2, docs indexed
2026-07-29 11:11 UTC, 2026-07-30 — settles two open questions in `module-02-sdk-setup`,
in opposite directions.

### 1. "Unofficial" is wrong — `contradicted`

`module-02-sdk-setup/SKILL.md:754` says:

> **Why the Scoop layout differs:** The **unofficial** Windows Scoop package places
> `SENZING_DIR` …

The server's own install commands say otherwise:

```text
# Add the official Senzing Scoop bucket and install
scoop bucket add senzingsdk https://github.com/Senzing/scoop-senzingsdk
scoop install senzingsdk/senzingsdk
```

The bucket is hosted under Senzing's own GitHub organisation and the server calls it
**official**. Calling it unofficial in the plugin invites a Bootcamper on Windows to
distrust the very route the vendor publishes — on the one platform where the SDK's
supported-language set is already narrowest.

**The layout claim in the same sentence is correct** and must survive. The server
confirms it in detail:

> `SENZING_DIR`: "Set automatically by Scoop to `<scoop-app-dir>\er` — NOTE this points at
> the `er` subdirectory, NOT the Senzing root. The support data is the root's SIBLING
> `data` directory, so SUPPORTPATH must NOT be built by appending to `%SENZING_DIR%`."

### 2. `SENZ7426` and the SzProduct masking — the server now confirms what it once could not

`specs/todo.md` records that on **2026-07-28** the spec
`supportpath-failure-code-and-szproduct-masking` was routed back **unimplemented**, because
its central claims could not be verified:

> `explain_error_code('SENZ7426')` → `EAS_ERR_XLITERATOR_FAILED: Transliteration failed` …
> **Nothing connects it to SUPPORTPATH.**

and

> The `SzProduct`-succeeds-while-`SzEngine`-fails masking claim is **neither confirmed nor
> refuted** by any MCP source.

Both are now confirmed — by a different tool. From the same Windows install response's
`gotchas`:

> "Building SUPPORTPATH as `%SENZING_DIR%\data` yields `<dir>\er\data`, which does not
> exist, and every SzEngine/SzDiagnostic call then fails with **SENZ7426
> EAS_ERR_XLITERATOR_FAILED** ('No transliteration rules found! Transliteration requires at
> least one module') **while SzProduct keeps working — so the install looks healthy.**"

That is the rejected spec's thesis, verbatim, from an MCP source: the wrong `SUPPORTPATH`
→ `SENZ7426`, and `SzProduct` masking the failure.

**The methodological point is the valuable half.** The 2026-07-28 check asked
`explain_error_code`, concluded the server had no such fact, and rejected the spec on that
basis. The fact was reachable the whole time from `sdk_guide(topic='install',
platform='windows')`. "The server does not cover X" is only ever "the tool I asked does not
cover X" — and a negative finding from a single tool is evidence about the query, not the
corpus. This repo has now made that mistake twice in three days (the other was a
`search_docs` query that appeared to show the Entity Specification lacked a marker it does
carry).

## Root cause

Both are the sweep's core shape: a fact written when it was true, with nothing to re-ask.
The "unofficial" characterisation was plausible when the Scoop route was newer. The
`SENZ7426` gap was a genuine absence in one tool that another tool has since filled — or
always had.

## Proposed change

1. **`module-02-sdk-setup/SKILL.md:754`** — drop "unofficial". Say the Scoop bucket is
   Senzing's own (`github.com/Senzing/scoop-senzingsdk`), and keep the whole layout
   explanation, which the server confirms. Stamp it 1.32.2 / 2026-07-30.
2. **Record the `SENZ7426` confirmation where the SUPPORTPATH guidance lives**
   (`module-02-sdk-setup/SKILL.md` around :703-729): a wrong `SUPPORTPATH` fails every
   `SzEngine`/`SzDiagnostic` call with `SENZ7426` while `SzProduct` keeps working, so the
   install looks healthy — cite `sdk_guide(topic='install', platform='windows')` as the
   source, **not** `explain_error_code`, which still does not make the connection.
3. **Update `specs/todo.md`'s entry** for `supportpath-failure-code-and-szproduct-masking`
   with a dated note: the masking claim is no longer unverifiable, and the tool that
   carries it. Do not delete the original reasoning — it was correct on the evidence
   available, and the correction is the point.
4. **Do not revive the rejected spec wholesale.** Its item 1 (broaden the `SENZ2027`
   symptom to `SENZ7426`) is still wrong: `SENZ2027` and `SENZ7426` are different
   failures with different causes, and `explain_error_code('SENZ2027')` still returns the
   plugin-init error. Only the SUPPORTPATH→`SENZ7426`→masking chain is now supported.

## Acceptance criteria

- [ ] `module-02-sdk-setup/SKILL.md` no longer calls the Scoop package unofficial, and
      names the Senzing-org bucket.
- [ ] The `SENZING_DIR`-points-at-`er` layout explanation and the `%SENZING_DIR%\..\data`
      fallback both survive unchanged — the server confirms them.
- [ ] The SUPPORTPATH guidance records the `SENZ7426` + `SzProduct`-masking behaviour,
      attributed to `sdk_guide(topic='install', platform='windows')`.
- [ ] No text attributes the SUPPORTPATH→`SENZ7426` link to `explain_error_code`, which
      does not make it.
- [ ] `specs/todo.md` carries a dated note that the masking claim is now MCP-confirmed and
      by which tool; the original 2026-07-28 reasoning is left intact.
- [ ] **Re-verification clause:** implementing this requires
      `sdk_guide(topic='install', platform='windows')` to still return the official-bucket
      command and the `SENZ7426`/`SzProduct` gotcha. If either is gone, re-triage rather
      than implement.
- [ ] `tests/test_windows_powershell_guidance.py` and
      `tests/test_supportpath*`-equivalent assertions pass; any pinning the removed wording
      is updated.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — line 754, and the SUPPORTPATH guidance near 703-729.
- `specs/todo.md` — the dated note on the routed-back spec.
- `tests/` — any assertion pinning "unofficial".

## Not in scope

`SENZING_ACCEPT_EULA=I_ACCEPT_THE_SENZING_EULA` — the server now documents this for
**non-interactive** installs, verified against the Scoop manifest's `pre_install` block,
and notes any other name/value is ignored. The bootcamp installs interactively behind a
pinned 👉 EULA gate (`module-02-sdk-setup/SKILL.md:207-224`), so it does not need the
variable. Recorded as examined and deliberately not adopted.

## Source

- Sweep: `delegate-to-mcp-server`, 2026-07-30 (ninth pass — both axes unchanged, so the run
  covered un-ledgered sites only), ledger keys `scoop-package-called-unofficial` and
  `senz7426-supportpath-masking-now-confirmed`
- Verdict: `contradicted` (item 1); `contradicted` for the todo.md verdict (item 2)
- MCP evidence: `sdk_guide(topic='install', platform='windows')`, server 1.32.2, docs
  indexed 2026-07-29 11:11 UTC, 2026-07-30. Quoted above.
- Priority: Medium — nothing breaks, but one claim disparages the vendor's own install
  route and the other leaves a confirmed failure mode recorded as unverifiable.
- Upstream: not applicable — the server is right on both.
- Related: `specs/supportpath-failure-code-and-szproduct-masking.md` (routed back
  2026-07-28; this reopens only its masking claim, not its `SENZ2027` item).

## Deviations from this spec, and why (2026-07-31)

- **The spec's history is wrong, and the ledger is the authority.** It says
  `supportpath-failure-code-and-szproduct-masking` was "routed back **unimplemented**",
  citing `specs/todo.md`. `specs/IMPLEMENTED.md` shows it was routed back, then **rewritten
  and implemented** the same day (`06c33e9`) with the `SENZ7426` link stripped as
  unverifiable — and that Module 2 Step 9 already requires an `SzEngine`/`SzDiagnostic`
  call, and `:719-722` already describes the masking. So the plugin already did the right
  *thing*; what it could not do was say *why*. The change made was correspondingly smaller
  than the spec describes: supply the missing citation and the concrete failure code, not
  reopen a rejected proposal.
- **Two test guards existed to prevent exactly this change, and both were right to fire.**
  `TheRetractedClaimStaysRetracted` banned any SENZ7426/SUPPORTPATH pairing outright, and a
  second test banned the SzProduct-masking wording, both on the premise that no MCP source
  stated either. One now does. They were **reworked rather than removed**, and the
  distinction they now enforce is INV-169's, applied the other way round from the original
  retraction: the **absolute** ("SENZ7426 means SUPPORTPATH is wrong") is still unsupported
  and still banned; the **conditioned** form (Windows/Scoop, `%SENZING_DIR%\data` absent) is
  supported and permitted *only* when the text names both the platform and `sdk_guide`. The
  masking guard now checks attribution instead of forbidding the claim. Both mutation-tested.
- **The first guard needed a denial exemption.** Module 2 mentions `SENZ7426` twice: once
  making the conditioned claim, once *denying* that `explain_error_code` supports it. A
  literal reading banned the denial — the very sentence that stops the retracted absolute
  being rebuilt from the wrong tool. The guard now skips windows that disclaim the link.
- **`explain_error_code('SENZ7426')` was re-verified 2026-07-31 and still makes no
  SUPPORTPATH connection** — generic transliteration causes only. The two tools differ in
  coverage rather than contradicting each other: a missing data directory means no
  transliteration modules, so a transliteration failure is what you would expect. That is
  why the attribution requirement is load-bearing rather than cosmetic.
