# The SUPPORTPATH trap is documented on macOS too, and the plugin tells macOS users it does not apply to them

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-02-sdk-setup/SKILL.md:921-957` implements a SUPPORTPATH existence check with a
parent-directory fallback, and closes with:

> This SUPPORTPATH verification applies to **Windows only**. On Linux and macOS, use the
> MCP-returned paths without modification.

Its rationale (`:946-954`) explains the trap as a *Scoop* quirk: `SENZING_DIR` points at the `er`
subdirectory while `data` sits one level above it. The `SENZ7426` diagnostic block (`:906-915`) is
scoped the same way — attributed to `sdk_guide(topic='install', **platform='windows'**)`, verified
against server 1.32.2 on 2026-07-30.

**The same trap is now documented on macOS, in more detail, and the shape is identical.**
`sdk_guide(topic='install', platform='macos_arm', language='java')` on **server 1.32.3, verified
2026-07-31**, returns this gotcha:

> SENZ7426 EAS_ERR_XLITERATOR_FAILED on getEngine/getDiagnostic/addRecord means **SUPPORTPATH is
> WRONG — it is NOT a broken install.** The cask's own shipped `etc/sz_engine_config.ini` sets
> `SUPPORTPATH=${INSTALLPATH}/senzing/er/data`, and that directory **DOES NOT EXIST**. The real
> support data (address_datamodel, nomicon, and the `*TransRules.sz` transliteration modules) lives
> **one level up**, at `$(brew --prefix)/opt/senzing/data`. With SUPPORTPATH pointing at the
> nonexistent er/data the engine finds zero transliteration modules and aborts … **SzProduct still
> works because it needs no support data, so the install LOOKS healthy.** FIX: set SUPPORTPATH to
> `$(brew --prefix)/opt/senzing/data` … Confirmed end-to-end on cask 4.4.0.26206: with the correct
> SUPPORTPATH, getEngine() and addRecord() both succeed on macOS Apple Silicon; with er/data the
> failure reproduces exactly. **Reported against 4.3.3.26191, which ships the same wrong path.**

`data` one level above `er`, `SzProduct` masking the failure, `SENZ7426` on the first real engine
call — that is the Windows/Scoop case verbatim, on a second platform.

**What it costs a Bootcamper.** The plugin's own advice is not wrong: `sdk_guide(topic='configure')`
returns the correct macOS `SUPPORTPATH`, so a guide that saves the MCP JSON unmodified gets a working
config. The defect is what happens **when SENZ7426 appears anyway** — from the cask's shipped `.ini`,
from `setupEnv`, or from an environment configured before the bootcamp. Module 3's engine check
catches the failure and routes the reader to "Module 2's Step 8 SUPPORTPATH…"
(`module-03-system-verification/phase1-verification.md:136`), and Step 8 tells them the verification
is Windows-only. The one diagnostic that would name their cause is gated away from the platform that
has it, and `explain_error_code('SENZ7426')` — re-checked on 1.32.3, 2026-07-31 — still returns only
generic input-validation causes ("Malformed or invalid input data", "Missing required fields",
"Invalid JSON format or encoding") and resolution steps about validating input JSON.

**This is not hypothetical.** The bootcamper in `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "SENZ7426
transliteration failure on the official macOS Homebrew Senzing SDK cask" (2026-07-27, macOS arm64,
SDK 4.3.3.26191) hit exactly this, spent the session isolating it, and concluded the **cask ships an
incomplete support-data payload** — inspecting `/opt/homebrew/opt/senzing/er/data`, finding only
Burmese/Khmer/Thai rules, and reading the cask's Ruby definition. That diagnosis is **wrong**: the
data was never missing, it was one directory up, in the location this plugin's Windows block already
knows to look. They then filed the incorrect diagnosis upstream. The server now names their exact
SDK version as affected, so the report appears to have landed and been corrected there.

## Root cause

The Windows check was written from a Windows finding, and its scope sentence was written as a
statement about platforms rather than about a *layout*. The property is "the support-data directory
may be a sibling of `er` rather than a child" — which is true of Scoop and true of the Homebrew cask.
Nothing re-checked whether the other supported platforms had the same shape when the server later
documented that they do.

The narrowing is invisible to every existing check. `citations.py verify` sees a resolving
invariant; `test_engine_verification_and_senz2027.py` deliberately permits a **conditioned**
SENZ7426→SUPPORTPATH claim (`:109`, "SENZ7426 must never be an *unconditioned* SUPPORTPATH
symptom") and the Windows-scoped block satisfies it; and no test compares the plugin's platform
coverage against the server's. INV-001 makes macOS a supported platform, but nothing binds a
*diagnostic* to platform parity the way INV-189 binds install instructions.

## Proposed change

1. **Restate the check by layout, not by platform.** The rule is: after `sdk_guide(topic='configure')`
   returns the engine config, confirm the `SUPPORTPATH` directory exists; if it does not, check one
   level up from `er`; use the parent if it exists; otherwise report both paths tried. That is
   already the Windows procedure — it needs to stop being labelled Windows-only.
2. **Add the macOS specifics, quoted with provenance.** The cask's shipped
   `etc/sz_engine_config.ini` points at a nonexistent `er/data`; the correct location is
   `$(brew --prefix)/opt/senzing/data`; the server's own verification command is
   `ls "$(brew --prefix)/opt/senzing/data"/*TransRules.sz`. Cite
   `sdk_guide(topic='install', platform='macos_arm')`, server 1.32.3, 2026-07-31 (INV-080).
3. **Widen the SENZ7426 diagnostic block** (`:906-915`) so its provenance names both platforms the
   server documents, keeping the ⛔ note that `explain_error_code` does **not** carry this and that
   `sdk_guide` is the tool that owns it — that note is now more valuable, not less, and re-confirmed
   on 1.32.3.
4. **Fix Module 3's routing.** `phase1-verification.md:136` sends a failed engine check to Step 8;
   Step 8 must be reachable for the platform the reader is on.
5. **Keep Linux as the server describes it.** Do not widen to Linux on inference — `sdk_guide` for
   `linux_apt`/`linux_yum` was not re-checked in this triage, so the spec asserts nothing about it.
   The implementer re-asks (criterion below); if Linux carries the same shape, include it, and if it
   does not, say so at the step.

⚠️ **Do not present this as "the plugin was wrong".** Saving the MCP-returned config unmodified is
correct and produces a working macOS install. The gap is diagnostic coverage when the environment
supplies a bad SUPPORTPATH from elsewhere — which is the realistic case, since the cask ships one.

⚠️ **Do not restate the bootcamper's diagnosis anywhere.** "The cask ships an incomplete
support-data payload" is refuted by the server and by the existence of the data one level up.
Writing it into the plugin would ship a fresh wrong fact carrying a bootcamper's authority.

## Acceptance criteria

- [ ] The SUPPORTPATH existence check and its parent-directory fallback apply to **macOS as well as
      Windows**, expressed as a layout rule rather than a platform list.
- [ ] The macOS specifics are present with provenance — the shipped `.ini`'s wrong `er/data`, the
      correct `$(brew --prefix)/opt/senzing/data`, and the `*TransRules.sz` verification — each
      attributed to `sdk_guide(topic='install', platform='macos_arm')` with the server version and date.
- [ ] The `SENZ7426` block names both documented platforms and **keeps** the ⛔ note that
      `explain_error_code` does not carry the SUPPORTPATH connection, re-verified this session.
- [ ] `module-03-system-verification/phase1-verification.md`'s routing to Step 8 resolves for a macOS
      reader — checked by **opening that file**, not inferred from the Module 2 edit (INV-182).
- [ ] Linux is either included on re-checked evidence or explicitly stated as not-re-checked; no
      platform is widened by inference.
- [ ] `tests/test_engine_verification_and_senz2027.py` still passes, and a test asserts the
      SUPPORTPATH check is not gated to a single platform — so this cannot re-narrow silently.
- [ ] **Re-verification clause:** implementing this requires re-asking
      `sdk_guide(topic='install', platform='macos_arm')` and `explain_error_code('SENZ7426')`. If the
      server has since fixed the cask `.ini`, or `explain_error_code` has gained the SUPPORTPATH
      cause, the change's content shifts and the deviation is recorded.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md). The macOS
      path is **not runtime-verified here** — this environment is Linux, so the `brew --prefix`
      layout could not be exercised and the evidence is the server's own end-to-end confirmation.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — the SENZ7426 block (`:906-915`),
  the SUPPORTPATH check (`:921-957`), and the Windows-only sentence (`:956-957`).
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — the
  routing at `:136`.
- `tests/test_engine_verification_and_senz2027.py` — the not-single-platform assertion.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "SENZ7426 transliteration failure on the official
  macOS Homebrew Senzing SDK cask" (2026-07-27, Module: SDK setup / System verification, Priority:
  High; `Source: bootcamper-reported`). The entry's own `Upstream:` records a `submit_feedback`
  submission on 2026-07-27.
- Priority: **High.** It blocked a bootcamper's entire SDK-setup path on a first-class platform, and
  the diagnostic that would have named the cause in minutes was gated to another platform.
- MCP re-check: **server 1.32.3, 2026-07-31 — the entry's diagnosis is refuted and the real cause is
  now server-documented.** `sdk_guide(topic='install', platform='macos_arm', language='java')`
  carries the SUPPORTPATH gotcha quoted above, names `$(brew --prefix)/opt/senzing/data` as the fix,
  and states it was confirmed end-to-end on cask 4.4.0.26206 and reported against 4.3.3.26191 — the
  bootcamper's exact version. `explain_error_code('SENZ7426')` re-checked the same day still returns
  only generic input-validation causes. Tools called: `get_capabilities`, `sdk_guide`,
  `explain_error_code`.
- Upstream: the cask defect was already submitted by the bootcamper on 2026-07-27 and **must not be
  re-filed** — the server's guidance now names 4.3.3.26191, so it was received. A **separate**
  candidate remains: `explain_error_code('SENZ7426')` and `sdk_guide` disagree on the same server,
  and the error-code tool is the one a reader hits first. Drafted for the maintainer's approval
  alongside this spec.
- Related specs: `specs/supportpath-failure-code-and-szproduct-masking.md` (established the
  engine-call verification and the `SENZ2027` diagnostic; its criterion 4 forbade an *unconditioned*
  SENZ7426→SUPPORTPATH claim, which this respects — the claim stays conditioned on `sdk_guide` and
  now names two platforms), `specs/windows-scoop-facts-the-server-now-owns.md`.
