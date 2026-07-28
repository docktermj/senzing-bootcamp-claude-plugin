# A wrong SUPPORTPATH surfaces as `SENZ7426` while `SzProduct` keeps succeeding — a version check cannot validate it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Credit first

The plugin **already handles this well.** `module-02-sdk-setup/SKILL.md:598-630` instructs verifying
SUPPORTPATH with `Test-Path` before saving the configuration, checking the parent-level path when the
first attempt is missing, and reporting clearly if neither exists — Windows-only, exactly where it is
needed, with the Scoop-layout rationale stated. Following it produced a correct configuration on the
first try: `...\senzingsdk\current\er\data` does not exist, `...\senzingsdk\current\data` does. This
spec refines a detail, not the approach.

## Problem

`module-02-sdk-setup/SKILL.md:592` states the consequence of a wrong SUPPORTPATH as
"initialization failures (e.g., SENZ2027 when SUPPORTPATH is wrong)". On the reporting install the
failure signature was different, and worse:

- The failing code is **`SENZ7426`**, not `SENZ2027`. `SENZ7426` appears nowhere in the plugin's
  documentation, so searching the docs for what a bootcamper actually sees returns nothing.
- **`SzProduct` calls keep succeeding** while every `SzEngine` and `SzDiagnostic` call fails.

The second point is the expensive one. A verification step that calls `SzProduct.getVersion()` to
confirm the SDK works will **pass against a broken configuration**. The install looks healthy, the
version prints, and the first real engine call fails later with a code the docs do not mention — by
which time the SUPPORTPATH step is several steps behind.

"Wrong path causes an initialization failure" implies the failure is immediate and obvious. In reality
it is deferred and partial, so a smoke test can certify a broken install.

## Root cause

**One wrong symptom code, and one undocumented masking behavior.**

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:592` names `SENZ2027` as the symptom
  of a wrong SUPPORTPATH. `SENZ2027` is otherwise used across the skills only as the generic
  *example* of a SENZ code in the error-handling routing blocks (`module-01`…`module-07` SKILL.md,
  each at "**SENZ error code** … e.g. `SENZ2027`"), so `:592` is the one place it is asserted as a
  specific diagnosis — and that assertion does not match the observed failure.
- Nothing anywhere states that `SzProduct` succeeds while `SzEngine`/`SzDiagnostic` fail under a bad
  SUPPORTPATH. Without it, an SDK-works check has no reason to exercise an engine call.

**The verification steps that would catch it do not require an engine call.** Module 2's Step 9
(`:635-644`) tests the database connection through
`generate_scaffold(language=…, workflow='initialize')` and states its success indicator as "engine
initializes and connects without errors" — the right intent, but nothing pins which class the check
must exercise, so a scaffold or a shortcut that calls only `SzProduct` satisfies the wording while
proving nothing about SUPPORTPATH. Module 3 System Verification's phase 1 begins at an MCP
connectivity check (`phase1-verification.md:77`) and mentions no SDK-initialization probe at all
(grep finds no `SzProduct`, `SzEngine` or `SzAbstractFactory` in that module), so the masked failure
survives to the first real engine call.

**Verification status.** The reporting session set SUPPORTPATH to the verified sibling directory per
the skill's instruction, so the damaging path was never hit — the error-code and masking details were
noted while writing the configuration rather than observed as a live failure. Confirm both against
`explain_error_code('SENZ7426')` and the MCP server's SUPPORTPATH documentation at implementation
time; state the code as observed-on (SDK 4.3.3, Win64) rather than as the universal symptom, and do
not drop `SENZ2027` unless the server contradicts it (INV-080).

## Proposed change

1. **Broaden the symptom at `:592`.** State that a wrong SUPPORTPATH can surface as `SENZ7426`
   (observed on SDK 4.3.3, Win64) as well as `SENZ2027`, sourcing both from
   `explain_error_code` rather than asserting them. Prefer "can surface as" to naming one code, since
   the point of the sentence is "do not guess these paths", not error-code trivia.

2. **Add the masking warning explicitly** next to the Windows SUPPORTPATH check (`:598-630`):
   **`SzProduct` calls succeed while `SzEngine` and `SzDiagnostic` calls fail** under a bad
   SUPPORTPATH, so a version check does not validate the configuration and a green version print is
   not evidence of a working install.

3. **Require the SDK-initialization check to exercise an engine call.** Pin Module 2's Step 9
   (`:635-644`) and its success criteria (`:650-656`) to an `SzEngine` (or `SzDiagnostic`) call, not
   only `SzProduct.getVersion()`, so a bad SUPPORTPATH fails at the verification step where it is
   diagnosable and one step from its cause. Keep the call MCP-generated
   (`generate_scaffold(workflow='initialize')`) — this constrains which class the generated check must
   touch, not how the code is obtained (INV-080), and it stays language-agnostic because every binding
   has both classes.

4. **Cover it in System Verification too.** Module 3 verifies the full setup end-to-end; its first
   SDK-touching step should fail loudly on an engine-initialization error and route via
   `explain_error_code`, so a masked-through install cannot reach data loading.

## Acceptance criteria

- [ ] `module-02-sdk-setup/SKILL.md` names `SENZ7426` alongside `SENZ2027` as a possible wrong-SUPPORTPATH
      symptom, attributed to its observed SDK version and platform rather than stated universally.
- [ ] The Windows SUPPORTPATH block states that `SzProduct` succeeds while `SzEngine`/`SzDiagnostic`
      fail, and that a version check therefore does not validate SUPPORTPATH.
- [ ] Module 2's SDK/database verification exercises an `SzEngine` (or `SzDiagnostic`) call; a
      configuration with a wrong SUPPORTPATH fails at that step rather than at the first data
      operation.
- [ ] Module 3 System Verification reports an engine-initialization failure explicitly and routes it
      through `explain_error_code`.
- [ ] Both error codes and the masking behavior are confirmed against the MCP server at implementation
      time; nothing about SENZ codes is asserted from training data (INV-080).
- [ ] The existing `Test-Path` sibling-directory check and its Scoop rationale are unchanged — this
      spec adds to it and removes nothing.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      SUPPORTPATH check stays Windows-gated as it is today, while the "exercise an engine call"
      requirement applies on every platform and in every binding.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — `:592` (symptom code), `:598-630`
  (the masking warning next to the SUPPORTPATH check), `:635-644` and `:650-656` (Step 9 and success
  criteria: exercise an engine call).
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — the first
  SDK-touching step: fail loudly on engine-initialization failure and route via `explain_error_code`.
- `tests/` — assert the skill names both codes and that the verification step requires an engine-class
  call.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "SUPPORTPATH failure presents as SENZ7426 with
  SzProduct still succeeding — documented code is SENZ2027" (2026-07-28, Module SDK setup;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin`;
  `Upstream: not applicable`)
- Priority: Medium
- Related specs: `specs/auto-detect-platform.md`,
  `specs/artifact-level-verification-for-deliverables.md` (INV-129 — verify the thing, not the exit
  status; this is its SDK-install analogue),
  `specs/mcp-grounding-in-every-skill.md` (INV-080),
  `specs/module02-postgres-credentials-hardening.md` (the sibling Module 2 hardening),
  `specs/windows-powershell-encoding-and-syntax.md` (the other Windows findings from this session)
