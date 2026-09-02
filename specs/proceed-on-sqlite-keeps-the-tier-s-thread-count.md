# "Proceed on SQLite" keeps the volume tier's thread count, and the engine says so on stderr

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two decisions in Data processing are taken independently and never reconciled:

1. **Step 1** captures the *production* volume tier, and **Step 3** selects the loader architecture
   from it. Every tier except `demo` gets the threaded pattern, and the thread count comes from
   Senzing's own anti-pattern guidance — *"Start with 2-8 workers per CPU core"*.
2. The **SQLite volume pre-load check** then asks a two-option question — proceed on SQLite, or
   migrate to PostgreSQL — and on *proceed* says only *"record `sqlite_volume_prompt` … then
   continue to the Phase B load."*

Nothing between those two points reduces the concurrency. So the sanctioned path runs a
thread-pooled loader against a database the *same* anti-patterns document describes as one that
*"does not support concurrent writes"*.

Observed live on 2026-09-02 (Senzing SDK **4.4.0**, build 4.4.0.26242, SQLite, 16 cores → 64
worker threads, `medium` tier, 5,000 records):

```
  4,000 loaded, 0 errors, 4.7s elapsed, 854 rec/s
2026-09-02 15:30:53.045 [szstatic:7306bc3966c0] ERR: Resolved entity [303236] is out of sync. Expected [1] but got [2]
2026-09-02 15:30:53.882 [szstatic:7306605ff6c0] ERR: Resolved entity [300782] is out of sync. Expected [3] but got [4]
  5,000 loaded, 0 errors, 10.3s elapsed, 485 rec/s
```

Throughput also halved across that window (854 → 485 rec/s), consistent with write contention.
The load itself completed correctly: **5,000 attempted, 5,000 loaded, 0 failed**, 1,602 redo
records drained.

**Two distinct gaps, and the second is the one a Bootcamper feels.**

- **(a) No concurrency reconciliation.** `grep` across `module-06-data-processing/` finds nothing
  relating thread count, worker count or concurrency to `database_type`. The tier decides the
  architecture; the database choice is recorded and then ignored by it.
- **(b) No guidance for engine stderr that is not a record failure.** Nothing in the module
  mentions `out of sync`, `szstatic`, or engine-level log output at all. Step 6 tells the guide to
  *"Watch the console output for resolution activity"* and Step 7 to *"Monitor progress"* — so the
  Bootcamper is pointed *at* the console, sees two lines prefixed **`ERR:`**, and the loader's own
  summary says **0 failed** in the same breath. There is no instruction telling the guide whether
  to explain them, suppress them, or treat them as a fault.

## Root cause

`plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md`:

- `:432-434` — the *proceed* branch carries no architecture consequence.
- Step 3 (`:225-250`) — derives concurrency from the tier alone, with no `database_type` input,
  even though Module 2 Step 7 persists `database_type` precisely so later modules can read it (the
  SQLite check at `:391` reads it for the *prompt*, then nothing reads it for the *loader*).

The prompt's own framing is what makes the gap easy to miss: it is described as a
*"stop-and-confirm heads-up, NOT a mandatory gate"*, and both its options are about **where** the
data lands rather than **how** it is written. Answering "proceed" reads as accepting a known
slowdown, not as accepting a loader tuned for a database that cannot take it.

⚠️ **This is not an argument for forcing PostgreSQL.** Proceeding on SQLite is a legitimate,
supported bootcamp choice, and the load worked. The defect is that the choice silently keeps a
thread count chosen for a different database.

## Proposed change

1. **Make `database_type` an input to Step 3's architecture selection, not just to the prompt.**
   When the datastore is SQLite, cap the worker count regardless of tier and say so in the code
   comment the step already requires — the comment currently states the tier and architecture, so
   it is the natural place to record that concurrency was reduced for the datastore and what to
   change when moving to PostgreSQL. Source the cap from MCP rather than writing a number into the
   skill (a sourcing floor); the anti-patterns document's SQLite entry and its "2-8 workers per
   core" line are the routes that bear on it.
2. **Give the *proceed* branch an architecture consequence.** One line, after the existing
   `sqlite_volume_prompt` write: proceeding keeps SQLite *and* reduces loader concurrency to match
   it, with the take-home loader carrying the comment that says how to restore it.
3. **Say what engine-level stderr is.** Add a short note to Step 6 or 7: the engine writes its own
   diagnostics to stderr (`[szstatic:…] ERR: …`), these are **not** per-record failures — the
   loader's own error log and the `failed` count are the authority on those — and an `out of sync`
   line under concurrent SQLite writes is contention, not data loss, provided the redo queue was
   drained and the final counts reconcile. ⛔ **Do not assert that from this spec:** re-ask MCP at
   implementation time. `search_docs(query='resolved entity is out of sync expected got concurrent
   loading SQLite lock')` on server **1.36.0, 2026-09-02** returned no document naming this
   message — it returned the 4.4.0 advisory-locking article, which confirms SQLite *"falls back to
   `LEASE` automatically"* with no advisory locks, and the clustering article. So the message text
   itself is **not currently covered by the indexed corpus**, and the note must either be sourced
   from a route that does cover it or be marked as an environment observation with its version and
   date (INV-080/INV-149) — never stated as a Senzing fact.

## Acceptance criteria

- [ ] With `database_type: sqlite` and a `small`/`medium`/`large` tier, the generated loader's
      worker count is capped for SQLite rather than taken from the tier alone, and its header
      comment names both the tier's architecture and the datastore reduction.
- [ ] The *proceed on SQLite* branch states the architecture consequence, not only the recorded
      preference.
- [ ] With `database_type: postgresql`, the tier's full concurrency is unchanged — the cap must not
      leak to other datastores.
- [ ] Step 6 or 7 distinguishes engine-level stderr from per-record failures, and names the
      loader's `failed` count and error log as the authority on the latter.
- [ ] Any claim about what an `out of sync` line means is either MCP-sourced or explicitly marked
      as an environment observation with SDK version and date.
- [ ] A test asserts the loader-generation step reads `database_type`.
- [ ] Negative control: set `database_type: sqlite` with the cap removed and confirm the test fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — Step 3 reads `database_type`; the proceed branch states its consequence
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md` — Step 6/7 note on engine stderr vs record failures
- `tests/` — guard that loader generation consumes `database_type`

## Source

- Feedback: `/dry-run` phase 3, 2026-09-02, Data processing Phase A Step 3 / the SQLite pre-load check / Phase B Step 7 (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — the load completed correctly (5,000/5,000, 0 failed), so nothing was lost; the cost is a Bootcamper shown `ERR:` lines with no explanation on the path the bootcamp told them to take, and a take-home loader tuned for a database they are not using
- MCP re-check: **server 1.36.0, 2026-09-02.** `search_docs(query='loading', category='anti_patterns')` returned "Do Not Use Single-Threaded Loading" (2-8 workers per core) and "Do Not Use SQLite in Production" ("does not support concurrent writes") — the two claims that together create the conflict. `search_docs(query='resolved entity is out of sync expected got concurrent loading SQLite lock')` returned **no document naming that message**; owner-checked: `search_docs` is the corpus route for a documented engine message and the nearest material it serves is the 4.4.0 advisory-locking article stating SQLite falls back to `LEASE`, so the message is uncovered by the corpus rather than missed by the query (absence negative). The throughput and `ERR:` observations are environment observations on SDK 4.4.0 (build 4.4.0.26242), not MCP claims.
- Upstream: not applicable — the plugin's reconciliation is what is missing; no server defect implied.
- Related specs: none

