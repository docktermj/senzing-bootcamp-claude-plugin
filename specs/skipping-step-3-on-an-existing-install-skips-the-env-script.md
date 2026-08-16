# Skipping Step 3 on an existing install skips the env script

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

When SDK setup finds Senzing already installed, Step 1 says "**Skip Steps 2 and 3
entirely**" and jump to Step 4. But Step 3 does two different jobs — it installs the
SDK **and** it creates the project-local environment script `src/scripts/senzing-env.sh`
that exports `LD_LIBRARY_PATH` and `PYTHONPATH`. Only the first job is redundant on
an existing install. The second is exactly what an existing install is most likely
to be missing.

The result: a bootcamper with Senzing installed but no environment configured
finishes SDK setup with no env script and no exported variables, and every later
module fails at import with a message that looks like a broken install:

```text
senzing.szerror.SzSdkError: failed to load the Senzing library
ERROR: Unable to load the Senzing library: libSz.so: cannot open shared object file
```

Step 1 itself predicts this failure mode — its filesystem fallback exists precisely
because "the import check fails for reasons that have nothing to do with the SDK
being absent — `PYTHONPATH` unset on Linux" — and then routes past the step that
would have fixed it.

The module's own troubleshooting compounds it. `SKILL.md:1244-1246` tells the guide
to "Check instead that `senzing-env.sh` was **sourced** (not executed) in this
shell" — advice about a file the existing-install path never created.

## Root cause

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:117-118` — on a
  V4.0+ existing install: "Skip Steps 2 and 3 entirely. Jump to Step 4 (verify
  installation)".
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:540` — inside Step 3
  (which spans `:391-693`): "create a project-local environment script at
  `src/scripts/senzing-env.sh`", with the zsh/bash path-resolution idiom, the
  fail-loudly root check, and the empty-config guard at `:555-591`.

Step 3 is titled "Install Senzing SDK", so the environment work is invisible to
anyone reading the skip instruction. Nothing in the required-stops list at
`:124-128` mentions it either — that list names Step 4 and Step 5 only.

The env script is not optional downstream: `ground-rules.md:304-319` treats it as
the supported mechanism (a sourced script that must work in the platform's default
shell, never a global shell-profile edit, per INV-199), and Module 2's own Java
guidance at `:643-645` requires it to be sourced in the shell that launches the JVM.

### Observed on this walk

Dry-run machine, 2026-08-13. Senzing 4.3.4 installed and current, `libSz.so` present
at `/opt/senzing/er/lib/`. `LD_LIBRARY_PATH` unset, `PYTHONPATH` empty.

- Step 1's Python import check failed with the message above — a healthy install.
- Step 1 correctly recovered via the native-library check and skipped Steps 2 and 3.
- **Every subsequent command in Steps 4 through 9 required
  `LD_LIBRARY_PATH=/opt/senzing/er/lib PYTHONPATH=/opt/senzing/er/sdk/python` to be
  supplied by hand.** Nothing in the module was going to create the script that
  supplies them.
- `src/scripts/senzing-env.sh` does not exist in the project at the end of the
  module.

The values are not guesswork either — `sdk_guide(topic='install',
platform='linux_apt', language='python')` returns both under
`install.platform.env_vars` (server 1.32.9, 2026-08-13), so the skip path has
everything it needs to write the script.

## Proposed change

1. **Split Step 3's two jobs.** Make the environment-script work its own step (or an
   explicitly named sub-step, e.g. Step 3b) that is **not** skipped on an existing
   install. The install commands stay skippable; the env script does not.
2. **Add it to the required-stops list** at `:124-128`, alongside Step 4 (verify)
   and Step 5 (license), with the same framing: never skipped, even when the SDK is
   already installed.
3. **Reword Step 1's skip instruction** so it names what is being skipped —
   installation only — rather than "Steps 2 and 3 entirely".
4. On the existing-install path, take the variable *values* from
   `sdk_guide(topic='install', platform=…, language=…)` rather than the install
   transcript, since no install ran (INV-080).
5. Make the Step 8 troubleshooting note at `:1244-1246` safe on both paths: if
   `senzing-env.sh` does not exist, say so as the finding rather than asking whether
   it was sourced.

## Acceptance criteria

- [ ] After SDK setup completes on a machine where Senzing was **already**
      installed, `src/scripts/senzing-env.sh` (or the platform equivalent) exists
      and exports the values `sdk_guide` returns for that platform and language.
- [ ] The required-stops list names the environment step as never skipped.
- [ ] Step 1's skip instruction names installation only, not "Steps 2 and 3
      entirely".
- [ ] The env script created on the skip path carries the same zsh/bash path
      resolution, fail-loudly root check and empty-config guard as the one created
      on the install path (`:555-591`) — one implementation, not two.
- [ ] The Step 8 troubleshooting note handles the script being absent.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).
      Windows uses `senzing-env.bat` and does not use the DYLD/LD variables
      (`:687`); the skip path must produce the right artifact per platform.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 1's skip
  instruction and required-stops list; split the env-script work out of Step 3;
  Step 8's troubleshooting note.

## Source

- Feedback: dry run phase 3, 2026-08-13 — walked SDK setup on a machine with
  Senzing 4.3.4 already installed; the existing-install path completed Steps 4–9
  with the environment never configured (`Source: self-observed (assistant
  retrospective)`)
- Priority: **High** — it breaks a documented path for the specific bootcamper the
  skip was written to help, and the resulting failure reads as a broken install in
  a *later* module, far from its cause.
- MCP re-check: server 1.32.9, docs indexed 2026-08-11 20:52 UTC, checked
  2026-08-13 via `sdk_guide(topic='install', platform='linux_apt',
  language='python')` — `install.platform.env_vars` returns both `LD_LIBRARY_PATH`
  and `PYTHONPATH`, so the values are available on the skip path. n/a as a
  contradiction: the server is not implicated, the step order is.
- Upstream: not applicable
- Related specs: `specs/senzing-python-sdk-must-not-be-pip-installed.md` (the
  `PYTHONPATH` half of the same environment problem, from the other direction),
  `specs/sdk-setup-step-4-requires-an-engine-before-the-datastore-exists.md` and
  `specs/sqlite-branch-says-no-additional-setup-but-the-schema-is-required.md`
  (same module)

## Deviations from this spec, and why (2026-08-14)

- **Proposal 1's renumbering was not done; the env script is a named required stop instead.**
  The spec suggested making the environment work "its own step (or an explicitly named
  sub-step, e.g. Step 3b)". Step numbers in this module are addresses: Step 1's routing, the
  required-stops list, the checkpoint vocabulary (`write step 3`), Step 8's troubleshooting and
  two sibling specs all cite them. Renumbering to express a rule that can be expressed directly
  would have been a wider change than the defect needs. Instead Step 1's skip instruction now
  names **installation only** and positively directs the environment work, and the
  required-stops list carries "Step 3's environment script" with its rationale. Every acceptance
  criterion is satisfied by that shape — criterion 3 asks only that the skip instruction name
  installation rather than "Steps 2 and 3 entirely".
- **Criterion 1 is not runtime-verified.** Whether the script *exists at the end of the module*
  depends on a conversational walk that this environment cannot run. The instruction that
  produces it is asserted instead. ⚠️ The variable **values** were confirmed on this machine
  while verifying the sibling SQLite spec: with `PYTHONPATH=/opt/senzing/er/sdk/python`,
  `senzing.__file__` resolved under the SDK rather than the PyPI packages also present here, and
  the engine then reached `SENZ7220` — so the script's contents do the job.
