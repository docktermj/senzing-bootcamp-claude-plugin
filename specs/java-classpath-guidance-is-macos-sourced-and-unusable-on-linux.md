# SDK setup's Java classpath guidance is macOS-sourced and resolves to a broken path on Linux

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A **Linux + Java** bootcamper reaching SDK setup is given a classpath example that cannot work on
their platform, and the MCP route the step tells them to confirm it against carries no Java content
at all.

`module-02-sdk-setup/SKILL.md:807-810` states:

> **Classpath:** the MCP install guidance's example is
> `java -cp "${SENZING_ROOT}/sdk/java/sz-sdk.jar:<your classes>" MyApp`.

`SENZING_ROOT` is **not set on Linux** and is not returned by any `linux_apt` MCP route. Applied
verbatim on a working Linux install (Senzing 4.3.4-26210, OpenJDK 21.0.12, 2026-08-28) the example
expands to `-cp "/sdk/java/sz-sdk.jar"` and fails:

```text
$ echo "SENZING_ROOT='${SENZING_ROOT:-<UNSET>}'"
SENZING_ROOT='<UNSET>'

$ javac -cp "${SENZING_ROOT}/sdk/java/sz-sdk.jar" Probe.java
Probe.java:1: error: package com.senzing.sdk does not exist
import com.senzing.sdk.SzEngine;
                      ^
```

The real Linux jar is at `/opt/senzing/er/sdk/java/sz-sdk.jar`, and with that path the identical
probe compiles and runs (`SzEngine visible: com.senzing.sdk.SzEngine`). Nothing in the Linux MCP
route names it.

## Root cause

The classpath sentence is sourced from the **macOS** response and presented in a passage whose
"Other platforms" paragraph (`SKILL.md:841-850`) tells the Linux reader only that the library
variable is `LD_LIBRARY_PATH` and to "confirm the specifics via `sdk_guide`" — which, for Linux +
Java, confirms nothing.

Live comparison, **MCP server 1.33.0, 2026-08-28**:

- `sdk_guide(topic='install', platform='macos_arm', language='java')` — `env_vars` carries
  `SENZING_ROOT`, `PATH`, `DYLD_LIBRARY_PATH`, and `gotchas[]` carries a Java-specific entry naming
  the jar verbatim: *"Java on macOS: -Djava.library.path alone is insufficient. DYLD_LIBRARY_PATH
  must be set at the shell level before JVM launch. Run: `java -cp
  "${SENZING_ROOT}/sdk/java/sz-sdk.jar:myapp.jar" MyApp`"*. So the plugin's sentence is an accurate
  quotation — **of the macOS response**.
- `sdk_guide(topic='install', platform='linux_apt', language='java')` — `env_vars` carries only
  `LD_LIBRARY_PATH` and `PYTHONPATH` (the latter Python-only and explicitly Linux-only), there is
  **no** `SENZING_ROOT`, **no** jar path, and **no** Java-specific `gotchas[]` entry. Passing
  `language='java'` does not change the response from the no-language call.

`SENZING_ROOT` is additionally macOS-specific by the server's own anti-pattern list: *"SENZING_DIR
on macOS → correct: SENZING_ROOT (macOS uses different env var than Windows)"* — it is named for
macOS and Windows, never for Linux.

This compounds at Step 3's env-script instruction (`SKILL.md:714-735`), which tells the guide to
take the script's variable set from the **same** response's `env_vars` plus the language-specific
`gotchas[]`. For Linux + Java both are empty of Java content, so a faithfully-built
`src/scripts/senzing-env.sh` exports `LD_LIBRARY_PATH` and nothing else — no `SENZING_ROOT` for the
example to interpolate and no classpath for the JVM. The step's own framing ("READ `gotchas[]` FOR
YOUR LANGUAGE, NOT `env_vars` ALONE") assumes a language-specific entry exists; on this platform it
does not, and the instruction has no branch for that.

The failure lands in **System verification** and every later Java module as
`package com.senzing.sdk does not exist` — which reads as a broken install, one module away from the
step that actually omitted the path.

## Proposed change

1. **Attribute the classpath example to its platform, and give the Linux form.** In
   `SKILL.md:807-810`, mark the `${SENZING_ROOT}` form as the macOS response's example, and state
   the Linux jar location as an environment observation (`/opt/senzing/er/sdk/java/sz-sdk.jar`,
   observed on 4.3.4-26210) — dated and marked observation-only per INV-080/INV-149, because no MCP
   route serves it for Linux.
2. **Give Step 3's env-script instruction a branch for "the response carries no language-specific
   `gotchas[]` entry."** Today the instruction assumes one exists. It should say: when the chosen
   language has no entry for the detected platform, derive the language's paths from the install
   layout and record them as an observation, rather than exporting only what `env_vars` happens to
   carry. For JVM languages that means the SDK jar; the native library path is already covered.
3. **Add a dated MCP-NEGATIVE marker** at the Linux classpath statement recording that
   `sdk_guide(topic='install', platform='linux_apt', language='java')` carries no jar path,
   no `SENZING_ROOT` and no Java `gotchas[]` entry — with `owner:` naming that same call as the
   route that would carry it (absence negative).
4. **Report upstream** that `language='java'` is inert on `linux_apt` while it is honored on
   `macos_arm` — the Linux route serves no Java content though the SDK ships `sdk/java/sz-sdk.jar`.

## Acceptance criteria

- [ ] `module-02-sdk-setup/SKILL.md` no longer presents `${SENZING_ROOT}/sdk/java/sz-sdk.jar` as
      platform-neutral guidance; the macOS form is attributed to `platform='macos_arm'` and a Linux
      form naming `/opt/senzing/er/sdk/java/sz-sdk.jar` is given, dated and marked observation-only.
- [ ] Step 3's env-script instruction carries an explicit branch for a platform/language pair whose
      `gotchas[]` has no language-specific entry, so a Linux + Java env script is not built from
      `env_vars` alone.
- [ ] A dated MCP-NEGATIVE marker with an `owner:` clause records the `linux_apt` + `java` absence,
      so `coverage_reports.py negatives` lists it for re-asking.
- [ ] A repo-level test asserts the plugin never presents `${SENZING_ROOT}` as the classpath root
      without naming macOS in the same passage (stdlib only, no `plugins/` import — INV-108), and
      fails when the qualification is removed (negative-controlled).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — the classpath statement
  (`:807-810`), the "Other platforms" paragraph (`:841-850`), and Step 3's env-script variable-set
  instruction (`:714-735`)
- `tests/` — a guard that the classpath root is platform-qualified

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-28, in the **analysis stretch** at the
  maintainer-chosen start module (SDK setup), on the first phase-3 walk with a real Linux Senzing
  install and a Java-language bootcamp (`Source: self-observed (assistant retrospective)`).
  Surfaced by following Step 1's existing-install path and then reading Step 3's instruction to
  source the env script's variables from `sdk_guide` — the Linux response has no Java content, which
  is invisible unless the macOS response is fetched alongside it for comparison.
- Priority: **High.** It blocks a documented path rather than degrading it: every Java bootcamper on
  Linux who follows the classpath example gets a compile failure, and the failure surfaces in a
  later module where it reads as a broken SDK install. Filed High rather than Medium because the
  bootcamp's own seeded-preferences fixture (`path: core`, `programming_language: Java`) is exactly
  this configuration, and because the wrong path is *plausible* — `${SENZING_ROOT}` looks like a
  variable the setup established, so a bootcamper is more likely to hunt their install than to
  doubt the example.
- MCP re-check: **server 1.33.0, 2026-08-28 — still reproduces.** Tools called:
  `sdk_guide(topic='install', platform='linux_apt', language='java')` and
  `sdk_guide(topic='install', platform='macos_arm', language='java')`.
  `owner-checked: sdk_guide(topic='install', platform='linux_apt', language='java')` IS the route
  that would carry a Java jar path or `SENZING_ROOT` for Linux — it returns neither, and returns a
  response identical to the same call without `language`.
- Upstream: **not yet sent.** The inert `language='java'` parameter on `linux_apt` is a genuine
  server-side coverage gap and is worth reporting, but `/dry-run` forbids `submit_feedback` under
  any category, so no submission was made. **The report is STILL OWED.**

## Invariants introduced

- `INV-283` — A platform- or language-scoped value an MCP route returns MUST be attributed to the
  platform or language whose response returned it, at the site it is presented, and where the
  Bootcamper's own pair has no such value from any route the step MUST say so and supply that pair's
  form as an observation (recorded in `specs/INVARIANTS.md`, 2026-08-31, on the maintainer's
  sign-off).

## Deviations from this spec, and why (2026-08-31)

- **Re-verified against server 1.35.1, two versions after the spec was written — the absence still
  holds, and one claim was strengthened.** `sdk_guide(topic='install', platform='linux_apt',
  language='java')` still returns no `SENZING_ROOT`, no jar path and no Java `gotchas[]` entry
  (`env_vars` carries only `PYTHONPATH` and `LD_LIBRARY_PATH`), while `macos_arm` still returns the
  Java `gotchas[]` entry quoted verbatim in the plugin. The spec's *"identical to the same call
  without `language`"* claim was **re-established live** rather than carried over: the no-language
  `linux_apt` call was made this session and returns the same content, so the parameter is inert on
  that platform. The Linux jar path was re-measured on this machine against `senzingsdk-runtime`
  **4.3.4-26210** and is marked observation-only.
- **Proposed change 2 could not be written the way the spec words it.** The spec asks for a branch
  in Step 3's env-script instruction covering a language whose `gotchas[]` has no entry, and its
  example is Java. That instruction lives **inside the generated script's comment block**, which
  three separate guards require to name no programming language (INV-002) — naming Java there failed
  `test_env_script_names_every_required_export`, `test_env_script_shell_portability` and
  `test_ld_library_path_is_not_relayed_as_conditional`. The branch is therefore stated as a
  **behavior** in the snippet ("when the chosen language has no entry for the detected platform,
  derive that language's paths from the install layout and record them as an observation"), with the
  concrete JVM-on-Linux case as prose outside the fence, beside the existing Python note. This is
  INV-002's own boundary test applied as written.
- **One dated `MCP-NEGATIVE` marker, not two.** A first pass carried the negative twice — once at
  the classpath bullet and once in the env-script instruction — which
  `coverage_reports.py unmarked` correctly flagged as an unmarked dated negative in the second
  place. The env-script prose now routes to the classpath bullet's marker rather than restating it:
  a second dated copy is a second thing to keep true, and INV-183 is satisfied by the pointer.
- ⛔ **The guard's first version did not fail on the real defect, and the fix is the unit it
  measures.** `tests/test_classpath_root_is_platform_qualified.py` originally scoped its check to
  the blank-line-delimited passage — and passed when the defective sentence was reintroduced,
  because a *neighboring* bullet two items earlier mentions "macOS's default shell" in an unrelated
  aside. Re-scoped to the **bullet**, which is what a bootcamper actually copies, it now fails on
  the shipped text (3 of its 6 tests) and passes on the correction.
- **Proposed change 4 (report upstream): `submitted 2026-08-31`** (INV-281 vocabulary). The
  maintainer asked to see the exact message before it went, approved it unchanged, and
  `submit_feedback(category='bug')` was then invoked once with that text verbatim — nothing was
  edited between approval and sending. The report states the `linux_apt` + `language='java'`
  absence, contrasts it with the honored `macos_arm` response, gives the shipped jar path measured
  on `senzingsdk-runtime` 4.3.4-26210, and proposes returning a Java `gotchas[]` entry for
  `linux_apt`/`linux_yum` or saying plainly that Java paths are not covered there.
  ⚠️ **This supersedes the `## Source` section's `Upstream: **not yet sent**… The report is STILL
  OWED.`** — true when the spec was written under `/dry-run`, which forbids `submit_feedback` under
  any category, and discharged here. The spec's own text is left unedited per this skill's
  guardrails; this bullet is the record. The server's reply confirms submissions are **anonymous
  with no follow-up channel**, so no response will arrive and none should be waited for; the
  plugin-side fix never depended on it.
