# The scaffold's engine_config fixture stops one gate short of the SDK path it exists to reach

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`scaffold_project.py` writes `config/engine_config.json` and its banner states the fixture's
purpose:

> `config/engine_config.json` — minimal settings so scripts reach their **real failure**, not a
> missing-file one

It does not achieve that. The file it writes is:

```json
{
  "PIPELINE": {}
}
```

An empty `PIPELINE` trips `senzing_viz_server.py`'s **config-completeness pre-flight check**,
which fires *before* the SDK is touched:

```
Engine settings in config/engine_config.json are incomplete: PIPELINE is missing
CONFIGPATH, RESOURCEPATH, SUPPORTPATH.
The engine cannot initialize without them, and proceeding would fail with SENZ7426
(transliteration), which points at SUPPORTPATH rather than at this file.
```
→ exit **2**, no snapshot written.

Supplying a complete `PIPELINE` (verified 2026-09-02) reaches the intended failure instead:

```
Could not build entity model: SzSdkError: failed to load the Senzing library
ERROR: Unable to load the Senzing library: libSz.so: cannot open shared object file
```
→ exit **1**, no snapshot written.

**Both paths are correct** — each fails loudly and writes nothing, so INV-077 holds either way.
The defect is in the *fixture*: phase 2's viz-server check is specified as "without `libSz.so`
it must fail loudly and write **no** snapshot", and with the shipped fixture that assertion is
satisfied by a **different gate than the one being tested**, at a different exit code.

## Root cause

`.claude/skills/dry-run/scaffold_project.py:362` writes `{"PIPELINE": {}}`. The banner entry at
`:289` describes an intent the value does not deliver.

Why it survived: in every previous phase-2 run the environment had **no `libSz.so`**, so both
gates produced "no snapshot, non-zero exit, loud message" and were indistinguishable without
reading the exit code and the text. The 2026-09-02 run was the first with a working SDK
(Senzing **4.4.0**, uncapped license), which is what separated them — and it separated them
only because the complete-config case was tried deliberately.

This matters beyond tidiness: a phase-2 run that believes it exercised the SDK-missing branch
has actually exercised the config-validation branch, so the `libSz.so` failure path has been
**unverified by every prior dry run** despite being listed as checked.

## Proposed change

1. Write a **complete** `PIPELINE` into the scaffold's `engine_config.json` — `CONFIGPATH`,
   `RESOURCEPATH`, `SUPPORTPATH` and a `SQL.CONNECTION` pointing inside the scratch project —
   using the values `sdk_guide(topic='install', platform='linux_apt')` returns in
   `default_paths` (`/etc/opt/senzing`, `/opt/senzing/er/resources`, `/opt/senzing/data`), so
   the fixture reaches the SDK on a machine where the SDK is absent **and** initializes on one
   where it is present.
2. Keep the incomplete config as a **second, explicitly named fixture** (e.g.
   `config/engine_config_incomplete.json`) so the pre-flight gate stays covered too — it is
   good behavior worth a test, not something to delete. Name both in the banner with the gate
   each one reaches.
3. Update `phase2-hooks-and-scripts.md`'s viz-server bullet to name **both** outcomes and their
   distinct exit codes (2 = incomplete settings, 1 = SDK unavailable), so a run cannot report
   the SDK branch as checked when it hit the config branch.

## Acceptance criteria

- [ ] With the default scaffold and no `libSz.so` reachable, `senzing_viz_server.py --no-serve
      --snapshot …` exits **1** with the `failed to load the Senzing library` message and writes
      no snapshot.
- [ ] With the default scaffold on a machine where the SDK **is** installed and a repository is
      initialized, the same command exits 0 and writes a snapshot.
- [ ] The incomplete-config fixture still reproduces the exit-2 pre-flight message, and the
      scaffold banner names which fixture reaches which gate.
- [ ] `phase2-hooks-and-scripts.md` distinguishes the two exit codes so neither can be mistaken
      for the other.
- [ ] Negative control: restore `{"PIPELINE": {}}` as the default and confirm the SDK-missing
      assertion starts passing for the wrong reason (exit 2), then revert.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/dry-run/scaffold_project.py` — write a complete PIPELINE; add the incomplete fixture; correct the banner
- `.claude/skills/dry-run/phase2-hooks-and-scripts.md` — name both gates and their exit codes

## Source

- Feedback: `/dry-run` phase 2, 2026-09-02 (`Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: **server 1.36.0, 2026-09-02** — `sdk_guide(topic='install', platform='linux_apt')` returns `default_paths` = `{config_path: /etc/opt/senzing, support_path: /opt/senzing/data, resource_path: /opt/senzing/er/resources, db_url: sqlite3://na:na@/tmp/sqlite/G2C.db}`, which is the source for the corrected fixture's values. ⚠️ The returned `db_url` points at `/tmp`, which the maintainer's `write-location-gate.py` and INV-109 forbid — the fixture MUST point `SQL.CONNECTION` inside the scratch project instead, not copy that default.
- Upstream: not applicable — maintainer-tool fixture, not a server or plugin defect.
- Related specs: none


## Deviations from this spec, and why (2026-09-02)

1. **The `SQL.CONNECTION` could not use the `default_paths` `db_url` the spec pointed at.**
   Proposed change 1 says to use the values `sdk_guide(topic='install', platform='linux_apt')`
   returns in `default_paths`. Re-asked on **server 1.36.0, 2026-09-02**: that response's `db_url`
   is `sqlite3://na:na@/tmp/sqlite/G2C.db`, and the maintainer's global `write-location-gate.py`
   blocks system-temp writes — a fixture pointing there would fail for a reason unrelated to the
   gate being tested. The three `PIPELINE` paths are used verbatim as returned
   (`/etc/opt/senzing`, `/opt/senzing/er/resources`, `/opt/senzing/data`); the datastore is
   derived from the project root instead (`<root>/database/G2C.db`, using a directory `DIRS`
   already creates). Pinned by `test_the_sql_connection_points_inside_the_scratch_project`, which
   asserts against the scaffold **source** so the tempting verbatim copy is what fails.

2. **The literal paths are the `linux_apt` defaults, and the scope is stated rather than
   engineered around.** The cross-platform invariant is satisfied in the sense that matters: a
   *complete* `PIPELINE` clears the completeness pre-flight on every platform, which is the whole
   job of the fixture, so the SDK gate is the one reached everywhere. Only criterion 2's
   "SDK present → exit 0" case is Linux-specific. Deriving the paths per-platform was considered
   and rejected: the three platforms do not share a shape (Linux puts `CONFIGPATH` at
   `/etc/opt/senzing`, outside `SENZING_ROOT`, while macOS and Windows put it under the root and
   place `SUPPORTPATH` at a *sibling* `data` directory), so the derivation would be three
   hardcoded shapes wearing a function. The per-platform values are recorded in the comment for a
   maintainer running phase 2 elsewhere, and `test_the_linux_only_scope_is_stated` pins that.

3. **An existing guard had to be rescoped, and the spec did not anticipate it.**
   `tests/test_dry_run_scaffold_paths_exist.py` asserts every `FIXTURE_MAP` path appears somewhere
   under `plugins/` — a fixture at a filename the plugin never reads "looks like coverage". Adding
   `config/engine_config_incomplete.json` failed it. The guard's premise does not hold for this
   file: the plugin **does** read it, when passed to `senzing_viz_server.py --settings`, which is
   the flag the pre-flight gate is reached through. Rescoped, per the dry-run rule to invert or
   rescope rather than delete: a path absent from `plugins/` is accepted only if **both** its base
   path (the name with the trailing `_suffix` removed) is under `plugins/` **and** the variant
   filename is named in the dry-run phase docs. ⛔ Negative-controlled on both conditions —
   `src/system_verification/records.jsonl`, the drift that guard was written for, still fails
   (no real base), and an *undocumented* variant of a real path fails too. A one-off allowlist was
   rejected as the listed-guard antipattern (INV-246).

4. **All three gates were verified LIVE, which is what this spec is really about.** Criterion 2
   needed "a machine where the SDK is installed and a repository is initialized", so one was
   created at the fixture's own datastore path (schema from
   `/opt/senzing/er/resources/schema/szcore-schema-sqlite-create.sql`, then
   `create_config_from_template()` + `set_default_config()`, config id 1973165579). Results on
   Senzing SDK **4.4.0, build 4.4.0.26242**: incomplete fixture → **exit 2**, pre-flight message,
   no snapshot; complete fixture with `PYTHONPATH`/`LD_LIBRARY_PATH` unset → **exit 1**,
   `libSz.so: cannot open shared object file`, no snapshot; complete fixture with the SDK and the
   initialized repository → **exit 0**, a 342 KB snapshot written. ⚠️ **This is the first time the
   SDK-missing branch has actually been exercised** — the point of the spec.

5. **I read `$?` after a pipe again and briefly recorded exit 0 for the exit-2 case.** The same
   mistake this session already produced once, and it is why the criterion-3 measurement was
   redone with output redirected to a file instead of piped to `tail`. Recorded because the
   methodology's value depends on the measurements being trustworthy, and this one was wrong on
   first reading.

## Invariants introduced

None. The rule this establishes — a fixture must reach the gate its banner claims — is the
existing property of `tests/test_dry_run_scaffold_paths_exist.py` and
`tests/test_scaffold_banner_matches_build.py`, now extended to fixture *content* rather than only
its path and its banner row. Both guards are development-environment rules under `.claude/`, which
`coverage_reports.py shipped` exempts by design, and no shipped hard rule was added (checked by
set difference per INV-282: 11 added lines, all from earlier implementations, 0 uncited).
