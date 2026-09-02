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

