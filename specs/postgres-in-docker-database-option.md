# Offer "PostgreSQL in a Docker container" as an explicit database option

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

At the SDK setup database-selection step the choices are SQLite and PostgreSQL. When
PostgreSQL is chosen but no server is installed, the follow-ups are: switch to SQLite,
install PostgreSQL locally, or use an existing PostgreSQL server. Running PostgreSQL
**in a Docker container** is not offered — the bootcamper had to ask for it, after
which it was viable (Docker was available). A container is often the lowest-friction
way to get a production-style PostgreSQL without a system-wide install or admin
rights, and many bootcampers already have Docker.

## Root cause

`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` Step 7 (`:635-659`)
offers exactly two options (`:637-640`); the PostgreSQL branch is three thin lines
(`:653-657`) that defer to `sdk_guide` and assume an installed/running server. The
switch/install/existing follow-ups the feedback cites are not even codified (runtime
improvisation). There is no Postgres-in-Docker option, no schema-DDL step, and no
`postgresql://` wiring. In Module 2, Docker appears only as an *SDK-install* target
(`:138-155`, `:177-189`), and `:179-182` steers away from it for the DB default
(prebuilt tools images require PostgreSQL, no SQLite).

**Invariant note:** **INV-037** (a database is initialized for use by Senzing) —
Postgres-in-Docker is a new path to satisfy it. The Senzing PostgreSQL schema DDL path
and setup commands MUST be confirmed via the Senzing MCP tools (INV-080), not training
data.

## Proposed change

In SDK setup Step 7, when PostgreSQL is chosen (or up front when Docker is present),
detect Docker availability and, when present, surface "PostgreSQL via Docker" as an
explicit, selectable option alongside SQLite, local install, and existing-server. The
flow should: run a postgres image with a project-local volume, apply the Senzing
PostgreSQL schema DDL (verify the exact path/commands via MCP — the reference is
`/opt/senzing/er/resources/schema/szcore-schema-postgresql-create.sql`), and wire the
`postgresql://…` connection string into the engine config. Keep SQLite as the default
recommendation for pure evaluation. Present the choices as a neutral lead + numbered
list, never "or"-joined (INV-051/INV-008), pinned verbatim (INV-056). A container
started here MUST be recorded for lifecycle tracking (see
`docker-container-lifecycle-teardown-and-resume`).

## Acceptance criteria

- [ ] SDK setup Step 7 presents "PostgreSQL in a Docker container" as an explicit, selectable database option, surfaced when Docker is detected.
- [ ] Choosing it runs a postgres container with a project-local volume, applies the Senzing PostgreSQL schema DDL (path/commands confirmed via MCP), and wires `postgresql://` into the engine config; the resulting database satisfies INV-037.
- [ ] SQLite remains the default recommendation for evaluation.
- [ ] The started container is recorded so it can be torn down/resumed (cross-ref the container-lifecycle spec).
- [ ] The choice wording is pinned verbatim, unambiguous, and numbered (INV-056/INV-008/INV-051).
- [ ] Docker is treated as optional: when absent, the flow degrades to the other PostgreSQL options.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 7 database choice and PostgreSQL branch (`:635-659`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Offer 'PostgreSQL in a Docker container' as an explicit database option" (2026-07-22, Module SDK setup — Step 7)
- Priority: Medium
- Related specs: `specs/docker-container-lifecycle-teardown-and-resume.md` (records/tears down the container this starts); INV-037, INV-080
