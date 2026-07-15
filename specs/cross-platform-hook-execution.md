# Cross-platform hook execution on Windows

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The invariants require the SBCP to run on Linux, macOS, **and** Windows. All four
hook scripts are `#!/usr/bin/env bash` shell scripts. Their path logic is already
cross-platform aware (Windows `%TEMP%`/drive-letter handling, macOS `$TMPDIR`,
backslash normalization), but execution still depends on a `bash` interpreter,
which on native Windows means relying on Claude Code's bundled Git Bash. There is
no non-bash fallback, so the Windows story is implicit rather than verified.

## Root cause

`plugins/senzing-bootcamp/hooks/hooks.json` wires each hook to a `.sh` script
(`session-start.sh`, `feedback-capture.sh`, `write-gate.sh`, `stop-nudge.sh`), and
each begins with `#!/usr/bin/env bash`. On Windows this requires a bash on PATH.

## Proposed change

Confirm and document (or harden) the Windows execution path. Options:

- Verify that Claude Code always provides a bash capable of running these hooks on
  Windows, and state that dependency explicitly in `hooks/README.md`.
- Or make the hooks portable across the interpreters Claude Code guarantees on all
  three platforms (e.g. a language-neutral runner), avoiding a hard bash dependency.

Whichever is chosen, the goal is that the hooks are demonstrably functional on
Windows, not merely assumed to be.

## Acceptance criteria

- [ ] The Windows execution path for all four hooks is either verified and documented, or removed as a dependency.
- [ ] `write-gate.sh` and `stop-nudge.sh` behavior is unchanged on Linux/macOS (re-run their existing verification scenarios).
- [ ] `hooks/README.md` states the runtime prerequisites per platform.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/hooks/hooks.json`, `plugins/senzing-bootcamp/hooks/README.md`
- `plugins/senzing-bootcamp/scripts/*.sh` (only if the interpreter dependency is changed)

## Source

- Audit: `migrate-kiro-power` verify/backfill audit (2026-07-15), invariant T1.
- Priority: Medium (cross-platform invariant; currently implicit on Windows).
- Related specs: `migrate-kiro-power.md`.
