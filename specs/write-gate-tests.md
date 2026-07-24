# Add a test harness for the write-gate security control

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`plugins/senzing-bootcamp/scripts/write-gate.py` is the plugin's PreToolUse security control
— it decides whether the agent may write a given path and whether a payload contains a
secret — yet it has no automated tests. Its logic is non-trivial and regression-prone: path
normalization (`norm`, including `..` resolution), the temp/Downloads classification, the
in-project exemption, `%TEMP%`/`$TMPDIR` handling, and the secret regex. Regressions here
fail silently (a write that should be blocked slips through, or a legitimate write is
wrongly blocked) and the review flagged the absence of tests specifically because this is a
security control. The plugin currently ships **zero** test infrastructure.

## Root cause

Not a defect — a coverage gap. `write-gate.py`'s pure logic is easily exercised (feed
synthetic stdin JSON, assert exit code + stderr), but nothing does so today.

## Proposed change

Add a small, dependency-light test harness targeting `write-gate.py`:

- **Location — outside the shipped plugin.** Put tests in a **top-level `tests/`** directory,
  NOT under `plugins/`. `propagate.sh` mirrors all of `plugins/` (minus `__pycache__`/`.pyc`)
  into the public repo, so tests placed there would ship to bootcampers; a top-level `tests/`
  is not in the propagation allowlist and stays dev-only.
- **Invoke as a subprocess.** `write-gate.py` reads `sys.stdin` at import time, so it cannot
  be imported directly. Run it via `subprocess.run(["python3", write_gate_path], input=…,
  cwd=tmp_project)` where `tmp_project` contains a `config/bootcamp_progress.json` (so the
  gate is active) and assert the exit code (`0` allow, `2` block) and `stderr` message.
- **Cases** (align with `specs/harden-write-gate.md` once implemented):
  - allow: project-relative path; absolute path inside cwd; extraction-failure (fail open).
  - block (location): `/tmp/…`, `/var/tmp/…`, `.../Downloads/…`, `%TEMP%\…`, `$TMPDIR/…`,
    and (post-harden) `~/tmp/…`, `~/Downloads/…`.
  - not-blocked edge: a project that itself lives under a `/tmp/`-containing path
    (the `PreToolUseWriteError.md` scenario); a case-differing in-project path on a
    case-insensitive filesystem (post-harden).
  - `..` traversal: `config/../../etc/x` resolves outside the project and is blocked.
  - block (secret): PEM `BEGIN … PRIVATE KEY`, `AKIA…`, and (post-harden) `AQAAAD…`;
    ordinary content is allowed.
- **Runner:** plain `python3 -m unittest` (stdlib, no new dependency) is sufficient; use
  `pytest` only if the maintainer wants it. Document how to run it (a line in `docs/` or a
  `scripts/sync-check.sh`-style helper) so it is discoverable and CI-runnable.

This spec is intentionally scoped to the write-gate only (the security-critical script);
broader coverage of the hooks / viz server / PDF writer is out of scope here.

## Acceptance criteria

- [ ] A `tests/` harness exists at the repo top level (not under `plugins/`) and does not get
      mirrored by `propagate.sh`.
- [ ] Running the tests exercises allow, temp/Downloads block, `..`-traversal block, and
      secret-detection cases, and passes against current `write-gate.py`.
- [ ] The suite covers the three `harden-write-gate` behaviors (or is written so those cases
      are added when that spec lands) — `~` expansion, case-folded exemption, `AQAAAD`.
- [ ] The suite runs with only the standard library (or a clearly-declared `pytest` dev
      dependency) and has a documented, one-command invocation.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `tests/test_write_gate.py` (new) — subprocess-driven cases for `write-gate.py`.
- `plugins/senzing-bootcamp/scripts/write-gate.py` — no change required; optionally guard the
  top-level execution under `if __name__ == "__main__":` and expose `norm`/classification as
  importable functions to enable direct unit tests (coordinate with `harden-write-gate.md`).
- A short "running the tests" note (location TBD, e.g. `docs/` or repo `README.md`).

## Source

- Claude Code Review, `Senzing/senzing-bootcamp-claude-plugin` PR #4 (comment 5073711304),
  Parts 1, 2, 4 & 5 — "No unit tests … for a security control".
- Priority: Medium.
- Related specs: `specs/harden-write-gate.md`, `specs/PreToolUseWriteError.md`,
  `specs/cross-platform-hook-execution.md`.

## Invariants introduced

- `INV-108` — Dev-only tests live in the top-level `tests/` (never under `plugins/`),
  stdlib-only, run via `python3 -m unittest discover -s tests` (recorded in
  `specs/INVARIANTS.md`).
