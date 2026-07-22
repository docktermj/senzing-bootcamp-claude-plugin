# At graduation, save a revisit/resume bundle (database backup, resume-state manifest, return guide)

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Graduation produces the recap PDF and a `production/` project but **explicitly never
preserves the resolved database**, and there is no resume-state manifest or return
guide. A returning bootcamper must re-run SDK setup, re-create the database/schema,
re-map, and re-load from scratch to get back to where they were. The bootcamper wants
graduation to silently preserve everything needed to resume — including a database
backup — plus a return guide documenting what they did and what they can do when they
come back.

## Root cause

`plugins/senzing-bootcamp/skills/graduation/SKILL.md`, Step 2 (`## Step 2: Build the
production project`, from `:203`):

- The copy table (`:218-225`) copies only `src/transform|load|query|utils`,
  `data/senzing-ready/`, and a dependency manifest.
- The never-copy-DB rule (`:227-229`): "Create `production/database/.gitkeep` as an
  empty placeholder (never copy the eval database itself)."
- The exclude list (`:230-232`) explicitly excludes `config/bootcamp_progress.json`,
  `config/bootcamp_preferences.yaml`, `docs/bootcamp_recap.md`, `data/samples/`,
  `data/raw/`, `logs/`, `backups/`, `docs/feedback/`.
- `config/data_sources.yaml`, `config/engine_config.json`, `config/license.json`, and
  `docs/mapping/` are in neither list, so they are **not** carried anywhere.

So the resolved data is dropped; there is no `RESUME_STATE` manifest and no
`REVISIT_BOOTCAMP.md`. INV-050 already defines reserved backup locations
(`data/backups/`, top-level `backups/`) and `database/` for the SQLite repo.

**Invariant note (do not silently override):** touches **INV-049** (`production/`
populated), **INV-048** (recap PDF), **INV-050** (layout). A DB-backup step must
**reconcile the "never copy the eval database" rule** (`:227-229`) — preferably via a
*separate* revisit-bundle path rather than loosening the `production/` exclusion, since
progress/preferences are deliberately kept out of `production/`. A new invariant would
be established for the bundle guarantee. The DB may contain the bootcamper's own data,
so confirm before any large/destructive backup action per existing graduation
conventions.

## Proposed change

Add a silent, non-blocking "revisit bundle" step to graduation (before the terminal
banner) that saves:

1. **Database backup.** PostgreSQL: `docker exec … pg_dump` of the `G2` database to a
   backup dir (document the `pg_dump`/`pg_restore` restore commands). SQLite: copy
   `database/G2C.db`. Use a dedicated, explicitly-confirmed backup subdir (e.g.
   `backups/` or `production/database/backup/`), reconciling the never-copy rule.
2. **Resume-state manifest.** Snapshot `config/bootcamp_progress.json`,
   `config/bootcamp_preferences.yaml`, `config/data_sources.yaml`,
   `config/engine_config.json`, `config/license.json`, and `docs/mapping/`, indexed by
   a single `RESUME_STATE.json` (or yaml).
3. **Return guide.** Write `REVISIT_BOOTCAMP.md` covering: accomplishments (from the
   recap), the business problem and data sources, how to restore the database from the
   backup, how to re-source the env and re-init the engine, how to re-run the
   loader/queries/visualization, the license location/expiry, and a top-of-file
   quick-start command list.
4. **Also include** the standalone visualization snapshot(s) under
   `docs/visualizations/` and the recap PDF.

Keep it non-blocking (warn-and-continue on any failure), silent/administrative
(INV-012), and confirm before large/destructive actions. Establish a new invariant for
the bundle. This pairs with `docker-container-lifecycle-teardown-and-resume` for a
complete resume story.

## Acceptance criteria

- [ ] Graduation produces a database backup (`pg_dump` for PostgreSQL, file copy for SQLite) with documented restore commands.
- [ ] A `RESUME_STATE` manifest bundles the progress/preferences/data-sources/engine/license state and the mapping specs.
- [ ] A `REVISIT_BOOTCAMP.md` return guide documents accomplishments, restore steps, re-init/re-run steps, license location, and a quick-start.
- [ ] The bundle step is silent, non-blocking (warn-and-continue), and confirms before any large/destructive database action.
- [ ] The "never copy the eval database" rule is reconciled explicitly via a dedicated backup path, not by loosening the `production/` exclusion.
- [ ] `INVARIANTS.md` records the new bundle guarantee; INV-049/INV-048/INV-050 remain satisfied.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (PostgreSQL and SQLite both handled; Docker optional) (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — new revisit-bundle step; reconcile `:227-232`.
- `specs/INVARIANTS.md` — new invariant for the revisit-bundle guarantee.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "At graduation, save a full 'revisit/resume' bundle (state + database backup + return guide)" (2026-07-22, Module Graduation)
- Priority: High
- Related specs: `specs/docker-container-lifecycle-teardown-and-resume.md`, `specs/recap-pdf-professional-design.md`; INV-049, INV-048, INV-050
