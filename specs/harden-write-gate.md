# Harden the PreToolUse write-gate (`~` expansion, case-folding, Senzing secret detection)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issues:

## Problem

`plugins/senzing-bootcamp/scripts/write-gate.py` is the plugin's dedicated PreToolUse
write-gate — the enforcement mechanism the skills repeatedly cite ("the plugin's write-gate
enforces the temp-path and secret rules"). Three gaps let unsafe writes slip through or fail
inconsistently:

1. **Home-relative (`~`) paths are never expanded.** A path like `~/Downloads/out.txt` or
   `~/tmp/x` is not absolute and not a drive path, so it falls into the `else` branch and is
   joined onto `os.getcwd()` — producing a bogus in-project-looking path
   (`/project/~/tmp/x`). Home-relative temp targets therefore evade the "no writes outside
   the project" check (they never match the literal `/tmp/`, `/var/tmp/`, `$TMPDIR` prefixes).

2. **The in-project exemption is case-sensitive while the temp/Downloads checks are not.**
   The exemption compares `target`/`here` verbatim, but the temp/Downloads checks two branches
   later are deliberately lower-cased "because Windows/macOS filesystems are case-insensitive."
   On a case-insensitive filesystem where the tool-reported path and the cwd differ only in
   case, the exemption can fail to match, and a project living under a path containing `/tmp/`
   (the exact scenario `PreToolUseWriteError.md` fixed) could then be falsely blocked.

3. **No Senzing license-secret detection.** The plugin's whole domain is Senzing, and its
   skills generate/handle `.lic` license files (e.g. `licenses/g2.lic`, INV-050 tree). The
   gate's secret regex covers only PEM private keys and AWS `AKIA…` keys — it has no pattern
   for `AQAAAD`-prefixed Senzing license blobs, nor any guard against a plaintext license key
   being written into a checked-in path. This is a coverage gap for exactly the secret type
   this plugin is most likely to encounter.

## Root cause

- `plugins/senzing-bootcamp/scripts/write-gate.py:52-59` — the absolute/drive/relative
  branch never calls `os.path.expanduser`, so a leading `~` is treated as a relative segment.
- `plugins/senzing-bootcamp/scripts/write-gate.py:88` — `target == here or
  target.startswith(here + "/")` compares case-sensitively, unlike the lower-cased
  temp/Downloads checks at lines 94-101.
- `plugins/senzing-bootcamp/scripts/write-gate.py:112` — the secret regex
  (`BEGIN … PRIVATE KEY | AKIA[0-9A-Z]{16}`) omits any Senzing `AQAAAD…` license pattern.

## Proposed change

1. Expand `~` before the absolute/relative branch:
   `file_path = os.path.expanduser(file_path)` (only when `file_path` is non-empty), so
   `~/…` resolves to the real home path and is then classified correctly as
   inside/outside the project.
2. Lower-case both sides of the in-project exemption the same way the temp/Downloads checks
   do (compare `target.lower()` against `here.lower()`), so the exemption and the block use a
   single, consistent case-folding rule. (Keep `norm` behavior otherwise unchanged.)
3. Extend the secret regex to flag `AQAAAD`-prefixed license payloads (the documented
   Senzing license-key prefix) in the write payload, reusing the existing fail-closed
   `SECRET_MSG` path. Keep the message guidance ("route the key to a file / use environment
   variables"), consistent with Module 4's "never paste a key into chat" handling. Do **not**
   block writes to a `licenses/*.lic` path the plugin itself creates — the gap is a *raw key
   value* appearing in a write payload, not the existence of a `.lic` file.

## Acceptance criteria

- [ ] A Write to a home-relative *system-temp/Downloads* path (`~/Downloads/x.txt`,
      `~/AppData/Local/Temp/x`) is blocked with `LOC_MSG`; a personal directory merely named
      `tmp` (`~/tmp/x`) and an in-project path under `$HOME` (`~/<project>/…`) are allowed.
      (Per `PreToolUseWriteError.md` the gate blocks *system* temp/Downloads, not merely
      "outside the project" — so `~/tmp` as a personal dir must stay allowed. Correction to
      the original criterion, which wrongly listed `~/tmp/x` as blocked.)
- [ ] On a case-insensitive filesystem, an in-project path whose case differs from the cwd
      (e.g. cwd `/Users/me/Proj`, path `/users/me/proj/config/x`) is allowed, not blocked.
- [ ] A write payload containing an `AQAAAD…` Senzing license string is blocked with
      `SECRET_MSG`; ordinary content and legitimate `licenses/g2.lic` file *paths* (with no
      raw key in the payload) are not blocked.
- [ ] Existing behavior is preserved: the gate stays disabled outside an active bootcamp
      (no `config/bootcamp_progress.json`), still fails open on location when `file_path`
      extraction yields nothing, and still fails closed on the secret check (INV per
      `PreToolUseWriteError.md`).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/write-gate.py` — `~` expansion (line ~52-59),
  case-folded in-project exemption (line ~88), and the `AQAAAD` secret pattern (line ~112).

## Source

- Claude Code Review, `Senzing/senzing-bootcamp-claude-plugin` PR #4 (comment 5073711304),
  Parts 4 & 5 — write-gate `~`-expansion, case-sensitivity, and missing `AQAAAD`/`.lic`
  secret detection.
- Priority: Medium (correctness/hardening of a security control; the plugin only writes
  inside a bootcamper's own project, so real-world exposure is limited).
- Related specs: `specs/PreToolUseWriteError.md`, `specs/cross-platform-hook-execution.md`.

## Invariants introduced

- `INV-109` — The write-gate MUST detect PEM private keys, AWS access-key IDs, and
  Senzing `AQAAAD` license blobs, blocking with `SECRET_MSG` (recorded in
  `specs/INVARIANTS.md`).
