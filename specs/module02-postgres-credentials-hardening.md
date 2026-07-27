# Harden the Module 2 Docker Postgres credentials (generated password, localhost-bound port)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-02-sdk-setup/SKILL.md`'s "Option 1 — PostgreSQL in a Docker container" hands the
agent a copy-paste `docker run` that sets a trivial, guessable password
(`POSTGRES_PASSWORD=senzing`, matching `POSTGRES_USER=senzing`) and publishes the port on
**all interfaces** (`-p 5432:5432`). Because the agent reproduces this verbatim on the
bootcamper's real machine every run, every bootcamp DB ends up with the same known password,
reachable from the LAN for as long as the container runs. Low real-world severity (local,
often ephemeral), but it is a poor default a security-conscious bootcamper would flag, and
the fix is small.

## Root cause

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:439-441` — hardcoded
  `POSTGRES_PASSWORD=senzing` and `-p 5432:5432` (binds `0.0.0.0`).
- The same password value flows into the engine-config connection URL
  (`postgresql://user:password@host:port/database`, lines ~460-462), so any change must
  thread through consistently.

## Proposed change

1. **Generate a per-project Postgres password** instead of the literal `senzing`: have the
   agent create a random password once, record it in a project-local location (e.g. a
   `config/` entry consistent with INV-050/INV-101 lifecycle tracking), and reuse it for the
   `docker run` env, and the `SQL.CONNECTION` URL in `config/engine_config.json`. Because the
   password is baked into the project-local volume on first init, it MUST be persisted and
   reused on container restart (the SessionStart restart offer, INV-101) — not regenerated,
   which would mismatch the persisted volume.
2. **Bind the published port to localhost**: `-p 127.0.0.1:5432:5432` so the DB is not exposed
   on other interfaces. (`POSTGRES_USER`/`POSTGRES_DB` may stay as-is.)
3. Keep the `docker exec … psql -U senzing` step unchanged (local socket, no password on the
   wire); only the TCP connection used by the SDK needs the generated password.

Keep the instruction MCP-grounded — the engine config is still produced via
`sdk_guide(topic='configure', …)`, never hand-constructed (per the surrounding text and
INV-011-family).

## Acceptance criteria

- [ ] The Module 2 Docker Postgres flow no longer instructs a fixed `POSTGRES_PASSWORD=senzing`;
      it uses a generated, project-recorded password.
- [ ] The generated password is persisted and reused on container restart, so the SDK
      connection still succeeds after a SessionEnd/SessionStart cycle (INV-101).
- [ ] The published port is bound to `127.0.0.1` (not `0.0.0.0`).
- [ ] The `SQL.CONNECTION` URL in the engine config uses the same generated password; a fresh
      end-to-end load still succeeds.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Option 1 `docker run`
  (generated password + localhost bind) and the engine-config connection-URL step.

## Source

- Claude Code Review, `Senzing/senzing-bootcamp-claude-plugin` PR #4 (comment 5073711304),
  Part 5 — "Hardcoded default credentials".
- Priority: Low (local/ephemeral container; hygiene of a shipped copy-paste default).
- Related specs: `specs/postgres-in-docker-database-option.md`,
  `specs/docker-container-lifecycle-teardown-and-resume.md`.
