# SQLite branch says "no additional setup" but the schema is required

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

SDK setup's database step offers SQLite as option 1, *recommended for learning and
evaluation* — the choice essentially every bootcamper makes — and then says:

> - Database path: `database/G2C.db`.
> - **No additional setup needed: SQLite is built in.**

That is wrong. The SQLite database file is not auto-created and its schema is not
auto-applied. A bootcamper who follows the step as written reaches Step 9 with no
database file at all, and gets:

```text
SzDatabaseError - SENZ1001|Critical Database Error '(14:unable to open database file)'
```

The plugin covers this correctly for PostgreSQL — `SKILL.md:915-937` applies
`szcore-schema-postgresql-create.sql` and states outright that "the SDK does NOT
auto-create it". The SQLite branch, which is the recommended one, has no equivalent
rung. Step 8a then compounds it: its premise is "a datastore you just
**schema-created**" (`:1091`, `:1105`), a state the SQLite path never reaches.

## Root cause

`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:855-861` (the SQLite
branch of Step 7) creates the `database/` directory, names the path, and stops.
Nothing in the module applies `szcore-schema-sqlite-create.sql`; a grep for
`szcore-schema` across the module returns only PostgreSQL occurrences.

The live server says the opposite, in two places at once.
`sdk_guide(topic='install', platform='linux_apt', language='python')`, server
1.32.9, 2026-08-13:

`install.platform.post_install[]`:

```bash
# Create SQLite database directory (the DB file is NOT auto-created)
mkdir -p /tmp/sqlite
# Create the SQLite database schema (required for senzingsdk-setup; senzingsdk-poc's
# sz_create_project does this automatically)
sqlite3 /tmp/sqlite/G2C.db < /opt/senzing/er/resources/schema/szcore-schema-sqlite-create.sql
```

`install.engine_config_notes[]`:

> "SQLite is the correct default for local testing on Linux (linux_apt, linux_yum)
> and macOS when you need persistence or multi-process access. **The DB file is NOT
> auto-created** — you must: (1) create the directory, (2) create the schema
> (`sqlite3 … < …/szcore-schema-sqlite-create.sql`), then (3) run the configure code
> to seed Senzing config. **Step 2 is required when using `senzingsdk-setup`.**"

The bootcamp installs `senzingsdk-setup` (it is in the module's own install command,
and `sdk_guide`'s), so the condition on that last sentence is always met. The
`senzingsdk-poc` alternative that would do it automatically is not what the bootcamp
installs.

### Measured chain, one rung at a time

Dry-run machine, 2026-08-13, Senzing **4.3.4** (4.3.4-26210), `senzingsdk-setup`
4.3.4-26210 installed, Linux x86-64. Engine config carried
`CONFIGPATH`/`RESOURCEPATH`/`SUPPORTPATH` from `sdk_guide` and
`SQL.CONNECTION=sqlite3://na:na@<project>/database/G2C.db`:

| State | `create_engine()` |
|---|---|
| Step 7 as written — directory created, no schema | ❌ `SENZ1001\|Critical Database Error '(14:unable to open database file)'`; **no `database/G2C.db` was created** |
| after applying `szcore-schema-sqlite-create.sql` (176 KB db file) | ❌ `SENZ7220\|No engine configuration registered in datastore` |

The second row is the exact state Step 8a documents and fixes, so the missing rung
is precisely one: schema creation. The schema file ships with the SDK at
`/opt/senzing/er/resources/schema/szcore-schema-sqlite-create.sql` (4,394 bytes,
2026-07-29 on this install).

### Second gap in the same branch: the connection string must be absolute

Step 7's SQLite branch says only "Database path: `database/G2C.db`". Written into
the connection string as-is, the engine cannot open it **from any directory**:

| `SQL.CONNECTION` | cwd | Result |
|---|---|---|
| `sqlite3://na:na@database/G2C.db` | project root | ❌ `SENZ1001 (14: unable to open database file)` |
| `sqlite3://na:na@database/G2C.db` | `$HOME` | ❌ `SENZ1001 (14: unable to open database file)` |
| `sqlite3://na:na@/home/…/senzing-bootcamp-phase3/database/G2C.db` | either | ✅ engine created |

So it is not a working-directory problem that a `cd` would fix — the path after
`@` must be absolute. The server's own example has the same shape:
`sqlite3://na:na@/tmp/sqlite/G2C.db`, with the `/` immediately after `@`.

This is compatible with INV-200 rather than in tension with it: the database file
still lives inside the project at `database/G2C.db`; it is the *connection string*
that must carry that path's absolute resolution. The step needs to say both things,
because a reader today gets the file location and nothing about the URL form.

## Proposed change

1. Replace "No additional setup needed: SQLite is built in" in the Step 7 SQLite
   branch with the three rungs the server states: create the directory, **apply the
   schema**, then let Step 8a seed the config. Take the schema path from
   `sdk_guide(topic='install', platform=…)` at run time rather than hardcoding it
   (INV-080), the same way the PostgreSQL branch already does.
2. Keep the existing `/tmp` override rule — the server's own example path is
   `/tmp/sqlite/G2C.db`, which INV-200 forbids, and the step is already right to
   override it to `database/G2C.db`. Say explicitly that the override applies to
   the schema command too, not just the connection string.
3. **Do not prescribe the `sqlite3` CLI.** Windows is supported (INV-001) and has no
   `sqlite3` binary by default; Python is already a hard bootcamp dependency, so
   apply the schema through Python's `sqlite3` module — reading the `.sql` file and
   running it as a script — which works identically on all three platforms. State
   this as the cross-platform form and keep the CLI form as the illustration the
   server returns.
4. Make Step 8a's premise true for both branches: it says "a datastore you just
   schema-created", which only the PostgreSQL path currently satisfies.
5. Note that `SENZ1001 (14: unable to open database file)` before the schema step
   means "the schema has not been applied yet", so it is not diagnosed as a
   permissions or path fault.

## Acceptance criteria

- [ ] Following Step 7's SQLite branch produces a `database/G2C.db` with the
      Senzing schema applied.
- [ ] The module no longer says SQLite needs no additional setup.
- [ ] The schema is applied through Python, not a `sqlite3` CLI invocation, and the
      path comes from `sdk_guide` at run time.
- [ ] The path stays project-relative (`database/G2C.db`), never the server's
      `/tmp/sqlite/G2C.db` (INV-200).
- [ ] After Step 7 on the SQLite branch, `create_engine()` fails with `SENZ7220`
      (config not yet seeded) rather than `SENZ1001` — i.e. the remaining gap is
      exactly the one Step 8a closes.
- [ ] Step 8a's "schema-created datastore" premise holds for the SQLite branch too.
- [ ] Step 7 states that the SQLite `SQL.CONNECTION` path must be **absolute** —
      the absolute resolution of the project's `database/G2C.db` — and that a
      relative path fails with `SENZ1001` from every working directory, including
      the project root. (Independently checkable from the schema criteria above.)
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).
      The schema requirement is a property of the datastore, not of the binding, so
      every language on the SQLite branch needs it.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 7's SQLite
  branch; Step 8a's schema-created premise.

## Source

- Feedback: dry run phase 3, 2026-08-13 — chose SQLite at Step 7 on a Core walk and
  executed it (`Source: self-observed (assistant retrospective)`)
- Priority: **High** — it breaks the recommended path of a required module, and the
  bootcamper is the one who picked the option the plugin recommended.
- MCP re-check: server 1.32.9, docs indexed 2026-08-11 20:52 UTC, checked
  2026-08-13 via `sdk_guide(topic='install', platform='linux_apt',
  language='python')`. Both `post_install` and `engine_config_notes` state the DB
  file is not auto-created and the schema step is required with `senzingsdk-setup`.
  **Server contradicts the plugin.** Still reproduces.
- Upstream: not applicable — the server is right.
- Related specs: `specs/sdk-setup-step-4-requires-an-engine-before-the-datastore-exists.md`
  (same module; both are step-order/prerequisite gaps around engine creation)
