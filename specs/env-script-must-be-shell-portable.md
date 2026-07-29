# `senzing-env.sh` must resolve its own path under zsh, macOS's default shell

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 2 requires a project-local `src/scripts/senzing-env.sh` and instructs sourcing it before running
tasks. Resolving the project root inside that script with `${BASH_SOURCE[0]}` — the standard idiom, and
the one a reader reaches for — works when the script is sourced from **bash**, and expands to **empty**
under **zsh**, which is macOS's default shell and therefore the shell a bootcamper is in when they
follow `source src/scripts/senzing-env.sh` literally.

The failure is silent and misattributed: the script still runs, the project root resolves to the wrong
directory, `SENZING_ENGINE_CONFIGURATION_JSON` comes back empty, and the JVM fails later with
**"Unable to get settings"** — an error that points at the SDK, not at the shell.

macOS on Apple Silicon is a first-class supported platform for the Java and C# paths (INV-001), and zsh
is its default shell, so any bootcamper who sources the env script directly as instructed hits this.

## Root cause

**The module mandates the script and the source-then-launch pattern, but gives no path-resolution
idiom — and the natural one is shell-specific.**

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:318` requires an environment script at
  `src/scripts/senzing-env.sh` (or `.bat` for Windows).
- `:343` states *"That is why `senzing-env.sh` must be sourced in the same shell that launches the
  JVM"* — so sourcing directly into the bootcamper's interactive shell is the documented pattern, not
  an edge case.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md:163-164`
  instructs `source src/scripts/senzing-env.sh` on Linux/macOS, and
  `graduation/SKILL.md:675` tells the bootcamper to re-source it. So three modules depend on the
  script being sourceable in whatever shell the bootcamper actually has.

`BASH_SOURCE` appears **nowhere** in the plugin (confirmed by grep) — the module never suggests the
idiom, and never warns against it. That absence is the defect: the script's content is generated at
Module 2 time, the obvious idiom is bash-only, and nothing in the guidance says the script must work in
the platform's default shell.

This is the shell-portability sibling of the Windows/PowerShell gap already fixed for the other
supported platform (INV-166/INV-167): the plugin documents a supported platform's shell without
documenting that shell's semantics.

## Proposed change

1. **State the portability requirement where the script is specified** (`:318`): a sourced env script
   MUST resolve its own location in the platform's **default** shell, not only in bash — because the
   documented usage is to source it interactively.
2. **Give a working idiom**, since "be portable" is not actionable. Branch on the shell:
   `${ZSH_VERSION}` present → `${(%):-%x}`; otherwise `${BASH_SOURCE[0]}`. Keep the plugin's existing
   preference for putting real logic in a file rather than inline (INV-167's file-over-shell rule).
3. **Make the failure loud rather than silent.** After resolving the root, the script MUST verify the
   path it computed actually contains what it expects (e.g. the engine configuration it is about to
   export) and fail with a message naming the resolved path when it does not. An empty
   `SENZING_ENGINE_CONFIGURATION_JSON` that surfaces later as a JVM "Unable to get settings" is the
   defect this prevents — the same fail-loudly discipline INV-111 applies to generators.
4. **Name the symptom where it lands.** System Verification and the Module 2 troubleshooting list
   should connect "Unable to get settings" / an empty engine configuration to a mis-resolved env-script
   path, so the error is diagnosed at the shell rather than in the SDK.

## Acceptance criteria

- [ ] Module 2 states that the env script must resolve its own path in the platform's default shell,
      and gives a zsh-and-bash idiom.
- [ ] A generated `senzing-env.sh` sourced from **zsh** resolves the same project root as when sourced
      from bash, and exports a non-empty engine configuration.
- [ ] A mis-resolved root fails with a message naming the path it computed, rather than exporting an
      empty configuration (INV-111).
- [ ] "Unable to get settings" / an empty `SENZING_ENGINE_CONFIGURATION_JSON` is documented as a
      symptom of a mis-resolved env-script path, in Module 2's troubleshooting and where System
      Verification would meet it.
- [ ] The Windows `.bat` path and the existing same-shell requirement at `:343` are unchanged — this
      adds portability, it does not relax the sourcing rule.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the fix
      concerns the shell the script is sourced in, not the bootcamper's chosen programming language,
      and Windows keeps its own script.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — the env-script specification
  (`:318`), the same-shell rationale (`:343`), and Troubleshooting for the symptom.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — connect an
  empty engine configuration to the env-script path.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the shell-semantics section
  added for Windows/PowerShell (INV-166/INV-167) is the natural home for a one-line "a sourced script
  must resolve its own path in the platform's default shell" rule, so the two platforms' shell
  guidance sits together.
- `tests/` — assert the portability requirement and the idiom are stated, and that `BASH_SOURCE` never
  appears as an unqualified recommendation.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "BASH_SOURCE is bash-only, so a sourced env script
  breaks under zsh (macOS default)" (2026-07-28, Module SDK setup;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin`; `Upstream: not applicable`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact — this is shell semantics and plugin guidance). Server 1.32.1,
  2026-07-28.
- Upstream: not applicable
- Related specs: `specs/windows-powershell-encoding-and-syntax.md` (INV-166/INV-167 — the same defect
  class for the other supported platform: a documented shell whose semantics were undocumented),
  `specs/macos-jvm-launch-environment-guidance.md` (the macOS JVM launch path this breaks),
  `specs/cross-platform-hook-execution.md` (INV-052 — the no-shell-dependency precedent),
  `specs/auto-detect-platform.md`

## Deviations from this spec, and why (2026-07-28)

**This spec's own `MCP re-check: n/a (no Senzing fact)` was wrong, and re-verification changed the
fix.** The spec does assert a Senzing fact — that a mis-resolved root surfaces as a JVM
*"Unable to get settings"*, *"an error that points at the SDK, not at the shell"*. On server 1.32.1
(2026-07-28) that is not what the string is:

- `search_docs(query='"Unable to get settings"')` finds it **only** in Senzing's own official code
  snippets (`senzing/code-snippets-v4` — `java/snippets/information/GetVersion.java`,
  `GetLicense.java`, and the C# `Program.cs` equivalents), where the sample program's *own* guard
  prints `Unable to get settings.` and throws `IllegalArgumentException` / `ArgumentException`.
- `search_docs(category='troubleshooting')` and `explain_error_code('0058')` return no engine error of
  that name. The nearest documented codes are `SENZ0058 EAS_ERR_SZ_INITIALIZATION_FAILURE` and
  `SENZ0050 EAS_ERR_SZCORE_NOT_INITIALIZED`, and **neither is documented as the symptom of an unset
  environment variable** — so neither is cited in the shipped guidance (INV-169).

Two consequences, both of which make the fix better than the spec's version:

1. **The guidance says the opposite of "points at the SDK".** The symptom carries *no SENZ code*
   precisely because it is not an engine error, so both new troubleshooting entries tell the reader
   **not** to route it through `explain_error_code` — there is nothing to explain — and to look at the
   env script instead. The spec's framing would have sent readers to the tool that cannot help.
2. **The guard tests `settings == null`, i.e. *unset*, not empty.** An
   `export SENZING_ENGINE_CONFIGURATION_JSON=""` therefore sails straight past the SDK's own check and
   fails deeper and less legibly than no export at all. That turned the spec's item 3 from "verify the
   path" into a positive rule the snippet enforces: **refuse to export an empty configuration** rather
   than export one. `SENZING_ENGINE_CONFIGURATION_JSON` itself was re-confirmed as the documented
   variable via `search_docs(category='configuration')` on the same server and date.

**Added, because item 3 is unsafe without it: `return 1`, never `exit 1`.** The spec requires the
script to fail loudly, and the obvious way to fail in a shell script — `exit 1`, or `set -e` — closes
the bootcamper's terminal or leaks the option into their interactive session, because a sourced script
*is* their shell. Implementing item 3 literally would have traded a silent wrong root for a killed
shell. The snippet uses `return 1 2>/dev/null || exit 1` (returns when sourced, still exits if the file
is run directly), and the rule is stated in both Module 2 and ground-rules.

**The documented snippet is executed by the tests, not merely asserted present.**
`tests/test_env_script_shell_portability.py` extracts the fenced block that follows the
`env-script-path-resolution` anchor, installs it as `senzing-env.sh` in a synthetic project tree, and
sources it — asserting the resolved root, the export, cwd-independence, the failure message naming the
computed path, the empty-config refusal, and that a failing source leaves the shell alive. A
path-resolution idiom that is present but wrong is exactly the defect being fixed, so presence alone is
not evidence.

**Verified that bash needs no `eval` guard around the zsh-only expansion.** `${(%):-%x}` sits in a
branch bash never takes, and the concern was whether bash *parses* it. It does, without a
bad-substitution or syntax error (confirmed by running it, and asserted by
`test_bash_tolerates_the_zsh_only_expansion_in_the_untaken_branch`), so the straightforward `if`
branch is used rather than a harder-to-read `eval`.

**Scoped to bash and zsh, not POSIX `sh`.** `${BASH_SOURCE[0]}` is a bad substitution under dash, and
there is no reliable POSIX way for a sourced file to learn its own path. The guidance therefore covers
the two shells that are a default login shell on the supported Unix platforms rather than claiming
portability it cannot deliver, and Windows keeps `senzing-env.bat` with `%~dp0`.

**Acceptance criteria status — one is NOT runtime-verified.** Criterion 2 ("sourced from **zsh**
resolves the same project root as when sourced from bash") is verified for the **bash** half only:
**zsh is not installed in this environment** (`command -v zsh` returns nothing), so the zsh half is
disclosed rather than ticked. The test for it exists and skips with that reason, and will run on any
machine that has zsh. Every other criterion is met, and criteria 3 and 5 are runtime-verified by
executing the snippet.

## Invariants introduced

- `INV-175` — Any script the SBCP tells the Bootcamper to `source` MUST resolve its own location in
  the platform's **default** shell rather than assuming bash, MUST verify the path it computed before
  exporting anything derived from it, and on failure MUST `return` (never `exit` or `set -e`) naming
  the resolved path; a value derived from an unverified root — and an **empty** value in place of no
  value — MUST NOT be exported (recorded in `specs/INVARIANTS.md`).
