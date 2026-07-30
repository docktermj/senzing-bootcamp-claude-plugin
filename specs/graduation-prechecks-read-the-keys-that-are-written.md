# Graduation's Pre-checks read three preference keys nothing writes, so language, database and data sources reach every handover artifact unknown

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Graduation's Pre-checks read the bootcamper's chosen language and database engine under key names
that no step in the bootcamp writes. The keys resolve to nothing, and because the step's fallback
triggers on a *missing file* rather than a missing key, nothing asks and nothing warns. Graduation
then generates the entire handover — `docker-compose.yml`, `.env.example`, `production/README.md`,
`GRADUATION_REPORT.md`, the recap's Run-environment block, and the revisit bundle — with the two
facts it needs most left unresolved.

Module 2 predicted this failure in its own words
(`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:694`):

```text
… and a different key name is the same failure as no key at all.
```

## Root cause

`plugins/senzing-bootcamp/skills/graduation/SKILL.md:134`:

```text
1. **Read preferences:** load `config/bootcamp_preferences.yaml` and extract `name`, `language`,
   `path` (Core/Customized; older sessions may store this as `track`), `selected_modules`,
   `database` (SQLite/PostgreSQL), and `data_sources` if present.
```

Three of those six are wrong:

| Graduation reads | Actually written as | Writer |
|---|---|---|
| `language` | `programming_language` | `bootcamp-preparation/SKILL.md:79`, `:87` (INV-133) |
| `database` | `database_type` | `module-02-sdk-setup/SKILL.md:680-694` |
| `data_sources` (from preferences) | `config/data_sources.yaml` (its own file) | Module 4; INV-050's layout tree |

`grep` over the whole of `graduation/SKILL.md` returns **zero** occurrences of
`programming_language` or `database_type`. Nothing writes a top-level `language:` or `database:`
key anywhere in the plugin — `graduation/SKILL.md:134` is the only place either name appears as a
preference key.

**Why it fails silently rather than loudly.** Pre-check 3 (`:136`) reads:

> **Fallback if files are missing:** tell the bootcamper, then ask for the programming language and
> database type with one 👉 question at a time …

The files are *not* missing — they exist and parse fine; only the keys don't match. So the fallback
never fires, no question is asked, and no warning is emitted. Absent a value, the six consumers
degrade quietly:

- `:596` Step 3 — `docker-compose.yml` ("SQLite single service **or** PostgreSQL app + db with a
  health check, per the chosen database") and `.env.example`'s `DATABASE_URL`
- `:605` Step 4 — `production/README.md`, "parameterized by language, database, and data sources"
- `:616` Step 5 — `GRADUATION_REPORT.md`, which records "language, database type"
- `:311-325` — the recap's **Run environment** block, whose `Language runtime` and `Database` rows
  feed the keepsake (INV-105)
- `:644` Step 6a — the revisit backup, which branches on `database` to choose *file copy* vs
  `pg_dump` (INV-094). A wrong branch here means the database backup is skipped or attempted with
  the wrong tool.
- `:661-670` Step 6b — `RESUME_STATE.json`, which records "the programming language and database
  type"

This is INV-170's defect class again — a value recorded in one place and read from another — and it
is the mirror image of the certificate-name bug: there the generator read the wrong *source*, here
graduation reads the wrong *key*.

## Proposed change

1. **Fix the three key names** at `graduation/SKILL.md:134`:
   - `language` → **`programming_language`** (keep no alias; nothing ever wrote `language`)
   - `database` → **`database_type`**, values `sqlite` / `postgresql` (the two lowercase spellings
     Module 2 Step 7 pins)
   - `data_sources` → read the registry from **`config/data_sources.yaml`**, not from preferences
   Keep the existing `path`/`track` legacy alias note — `track` genuinely was written by older
   sessions, unlike `language` and `database`.
2. **Propagate the corrected names** to every downstream reference in the file, in particular Step
   6a's `database` read (`:644`) and Step 6b's manifest (`:661-670`).
3. **Make a missing key distinguishable from a missing file** in Pre-check 3. A present file with
   an absent `database_type` means Module 2 Step 7 did not record the choice — which Module 4
   already treats as a **plugin defect to note internally**, not a bootcamper outcome
   (`module-04-data-collection/SKILL.md:581`). Mirror that: note it internally so it surfaces in
   the retrospective (Step 0), and only then fall back to the pinned question. Keep the whole path
   non-blocking (INV-048).
4. **Assert the contract**, not just this instance: a test that every `config/bootcamp_preferences.yaml`
   key graduation claims to read is a key some skill file states it writes. That is the guard that
   would have caught all three, and it generalizes to future readers.

## Acceptance criteria

- [ ] `graduation/SKILL.md` Pre-checks read `programming_language` and `database_type`, and take the
      source registry from `config/data_sources.yaml`.
- [ ] No occurrence of `` `language` `` or `` `database` `` remains in `graduation/SKILL.md` as a
      *preference key* (the words may still appear as prose, and `Database:`/`Language runtime:`
      remain the recap's Run-environment row **labels** per INV-105).
- [ ] Step 6a's backup branch and Step 6b's manifest read the corrected key.
- [ ] Pre-check 3 distinguishes "file missing" from "key absent", notes a missing `database_type`
      internally as a plugin defect (mirroring `module-04-data-collection/SKILL.md:581`), and still
      never blocks graduation.
- [ ] A test asserts that every preference key graduation reads is written somewhere in
      `plugins/senzing-bootcamp/skills/**`, and fails if a reader names a key no writer produces.
- [ ] `tests/test_config_seeding_guidance.py`, `tests/test_saved_preferences_honored.py` and the
      graduation suites still pass.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Pre-checks 1 and 3 (`:134`, `:136`);
  Step 6a (`:644`); Step 6b (`:661-670`); and any prose in Steps 3-5 that names the old keys.
- `tests/test_preference_keys_have_writers.py` (new) — the reader/writer contract guard.

## Source

- Feedback: n/a — found by the deep-dive invariant-conformance audit of 2026-07-29, run at the
  maintainer's request; `Source: self-observed (assistant retrospective)`.
- Priority: **High** — it silently degrades every handover artifact plus the revisit database
  backup, and it is invisible to exit codes, retention figures, and all 1015 tests.
- MCP re-check: n/a (no Senzing fact — plugin-internal key names). Server **1.32.2** confirmed
  current at triage time via `get_capabilities`, 2026-07-29.
- Upstream: not applicable.
- Related specs: `specs/certificate-name-must-reach-the-generator.md` (INV-170, same class),
  `specs/dry-run-phase3-interaction-prose-defects.md` (added the `database_type` **writer** on
  2026-07-29 and did not check its readers), `specs/skip-model-guidance-question.md` (INV-133),
  `specs/show-plugin-version-and-record-environment.md` (INV-105's Run-environment rows),
  `specs/graduation-revisit-resume-bundle.md` (INV-094's backup branch).

## Note

Do the reader/writer guard even if the three renames feel like a two-line fix. The renames close
today's instance; the guard closes the class — and this is the second instance in two days (the
`database_type` writer itself was missing until 2026-07-29).

## Deviations from this spec, and why (2026-07-29)

- **The reader/writer guard declares the contract instead of inferring it.** Criterion 5 asks for a
  test that "every preference key graduation reads is written somewhere in
  `plugins/senzing-bootcamp/skills/**`". Inference was implemented, measured, and rejected: scanning
  for a `key: value` site outside graduation *passes* both broken keys (`language:` and `database:`
  appear in prose in `bootcamp-onboarding/`, `module-07-.../`, `module-03-.../`) and *fails* four
  legitimate ones (`deployment_target`, `cloud_provider`, `os`, `arch` appear in no `key: value` form
  anywhere), and a YAML-fence scan finds only 4 of 15 keys. A rule that both false-passes and
  false-fails is worse than none — the shape INV-144/INV-173 forbid — so
  `tests/test_graduation_reads_persisted_answers.py` carries a `WRITERS` map (key → writing file) and
  asserts **both** directions: every key graduation declares is in the map, and every map entry's
  writer really mentions its key. A stale map fails its own test.
- **The Pre-checks read became a table, not a corrected prose list.** The spec says "fix the three key
  names". Seven keys with their writing module now sit in a table, because the same pass implemented
  `graduation-reads-integration-and-deployment-answers` (INV-097's two keys belong in the same read)
  and because the failure mode was a reader inventing names — a table naming the writer beside each
  key is what makes that visible at the point of use.
- **Guard scoping was itself mutation-caught.** The first version asked whether a key appeared
  *anywhere* in Pre-checks; deleting the `integration_targets` table row still passed, because prose
  below mentions it. Rescoped to the table's first column ("declared as a key to read"), and the
  retired-name check had to be flattened before matching, since the framing phrase and the mention
  land on different source lines once prose wraps.
- **Not runtime-verified:** nothing needed a live engine. All 7 criteria are static guidance plus
  tests; each guard was mutation-tested (key rename reverted, table rows dropped, missing-key branch
  removed) and reverted.
