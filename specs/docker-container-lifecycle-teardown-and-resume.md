# Track bootcamp-started Docker containers, tear them down on exit, and restore them on resume

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

If the bootcamp starts any Docker containers, they are not stopped when the bootcamp is
exited, leaving them running after the session ends and consuming resources (memory,
ports, disk). The bootcamper wants: (1) containers the bootcamp started stopped on
exit, and (2) a record of which containers were used so that on resume they can be
restarted or regenerated.

## Root cause

The bootcamp does start containers — `module-02-sdk-setup/SKILL.md:138`, `:143-145`,
`:148`, `:177-186` (running the SDK in a container for several OS/language combos), and
`bootcamp-preparation/SKILL.md:168`. But session exit handling in
`plugins/senzing-bootcamp/scripts/session-end.py` only folds the recap checkpoint
(`:16-18`); there is no docker/container handling (grep is empty).
`hooks/hooks.json:59-68` wires `SessionEnd → session-end.py`. Resume state in
`config/bootcamp_progress.json` tracks modules but no containers, and bootcamp-active
detection is merely "does `config/bootcamp_progress.json` exist"
(`recap_checkpoint.py:26-28`).

**Invariant note:** **INV-052** (hooks MUST be python3, exec-form, no shell dependency)
— any teardown-on-exit must live in the python3 `SessionEnd` hook, not a shell script.
**INV-001** (Linux/macOS/Windows) and **INV-002** (language-agnostic) — teardown must be
cross-platform and Docker must stay optional (the `docker` CLI may be absent). No
invariant currently governs container lifecycle; a new one would be established. This
pairs with `postgres-in-docker-database-option`, which starts a container that this
spec must track.

## Proposed change

1. **Track** the containers the bootcamp starts (name, image, purpose, ports, volume)
   in `config/bootcamp_progress.json` (e.g. a `docker_containers` list). Each skill
   that starts a container records it there.
2. **Tear down on exit:** in `session-end.py` (python3, cross-platform), stop the
   tracked containers when `docker` is present; warn-and-continue when it is not.
3. **Reconcile on resume:** in `session-start.py`, compare the record with running
   Docker state and restart existing containers or offer to regenerate missing ones.

Keep all Docker interaction optional and gated on `docker` availability. Establish a
new invariant for the lifecycle guarantee.

## Acceptance criteria

- [ ] Containers the bootcamp starts are recorded in `config/bootcamp_progress.json` with enough detail to restart/regenerate them.
- [ ] On session exit, tracked bootcamp-started containers are stopped when `docker` is available; absence of `docker` degrades gracefully (warn-and-continue, no error).
- [ ] On resume, the record is reconciled with running Docker state and containers are restarted or regenerated.
- [ ] The teardown logic runs from the python3 `SessionEnd` hook (INV-052), is cross-platform (INV-001), and treats Docker as optional (INV-002).
- [ ] `INVARIANTS.md` records the new container-lifecycle guarantee.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/session-end.py` — stop tracked containers on exit.
- `plugins/senzing-bootcamp/scripts/session-start.py` — reconcile/restart on resume.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` (and the Postgres-in-Docker flow) — record started containers in progress state.
- `specs/INVARIANTS.md` — new invariant for the lifecycle guarantee.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Stop Docker containers on exit and remember them for resume" (2026-07-22, Module General — reported at graduation)
- Priority: Medium
- Related specs: `specs/postgres-in-docker-database-option.md` (starts a container this tracks), `specs/graduation-revisit-resume-bundle.md`; INV-052, INV-001, INV-002

## Invariants introduced

- `INV-101` — Bootcamp-started Docker containers are recorded in `config/bootcamp_progress.json` (`docker_containers`); the python3 SessionEnd hook stops them on exit (`docker stop`, not remove) when docker is available, and SessionStart surfaces them on resume; all docker interaction is optional and warns-and-continues when docker is absent/erroring (recorded in `specs/INVARIANTS.md`). Maintainer-approved wording.
