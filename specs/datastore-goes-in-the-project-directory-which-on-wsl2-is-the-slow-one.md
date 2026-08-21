# The datastore always goes in the project directory, which on the Windows+WSL2 path the bootcamp itself routes to is 300x slower — and nothing measures it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

On Windows with the Senzing SDK in WSL2 and the project on the Windows filesystem (`/mnt/c/...`),
the SQLite datastore is reached over the 9p protocol. Measured with the SDK's own
`check_repository_performance(5)`:

| Datastore location | Inserts in 5s |
|---|---|
| `/mnt/c/...` (the project directory) | 1,112 |
| `~/senzing-bootcamp/` (WSL-native ext4) | 326,606 |

End-to-end load throughput was **3 records/second**, projecting to **~7.5 hours** for 83,338
records. After relocating the datastore: **138–180 records/second**, **~9 minutes**. Same code,
same data, same machine.

**A Bootcamper who does not think to benchmark simply experiences the bootcamp as very slow**, and
has no reason to suspect storage. There is no error, no warning, and no number anywhere to compare
against. The load is not broken; it is two orders of magnitude off, silently, on a platform path
the bootcamp actively routes people into.

## Root cause

**The plugin fixes the datastore inside the project directory unconditionally, by rule.**
`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:1444`:

> - Always use `database/G2C.db` for SQLite (never `/tmp/sqlite`).

with the same instruction at `:1001`, `:1039` ("if the generated scaffold uses `/tmp/`… override
the path to `database/G2C.db`") and enforced again in Module 7
(`module-07-query-visualize-discover/phase1-query-visualize.md:210-212`). The rule is right and
should stay: it is INV-200's no-files-outside-the-working-directory guarantee, and on every other
platform the project directory is a perfectly good place for the datastore. **The Windows+WSL2
combination is the one case where the working directory and the fast filesystem are different
filesystems**, and no site distinguishes it.

**The plugin knows it is on WSL2 and never uses the fact.** SDK setup records the host
(`host: WSL2 Ubuntu ... on Windows 11`). A repository-wide grep for `WSL` finds four hits —
`bootcamp-preparation/SKILL.md:275` and `module-02-sdk-setup/SKILL.md:540` (both about language
routing), and two in `hooks/README.md` and `visualization-api-reference.md:1091` about shell
availability. **No file mentions `/mnt/` at all.** The detection exists; nothing branches on it.

**`check_repository_performance` appears nowhere in the plugin.** Zero hits across every skill,
script and hook — even though Senzing's own anti-pattern documentation says to run it before a load,
and the plugin already calls `search_docs(category='anti_patterns')` at
`module-02-sdk-setup/SKILL.md:414-415` before recommending an install approach. The check that would
have caught this in five seconds is one the plugin is already positioned to run and never does.

**Both halves confirmed on server 1.33.0, verified 2026-08-21**, via
`search_docs(query='loading', category='anti_patterns')`:

- *Do Not Use Low-IOPS Storage* — "Senzing entity resolution is I/O intensive. Spinning disks
  (HDD), NAS/SAN over network, and shared storage systems typically cannot provide the IOPS needed
  for good performance… Avoid network-attached storage (NAS/NFS) for the database data directory…
  Run `check_repository_performance()` to validate your storage meets requirements."
- *Do Not Skip check_repository_performance() Before Production* — "Senzing provides
  `check_repository_performance()` in the `SzDiagnostic` module… Always run
  `check_repository_performance()` on your production database before starting a large data load.
  This validates that your storage IOPS, network latency, and database configuration can support
  the required throughput." with the signature `diagnostic.check_repository_performance(seconds_to_run=10)`.

9p over a WSL2 boundary is exactly the shared/network-attached case the first anti-pattern
describes. **Senzing's guidance is correct and complete; the bootcamp never connects it to the setup
the bootcamp recommends.** The SDK is behaving as documented — this is a plugin defect, not a
server one.

## Proposed change

1. **Detect the crossing and warn, at datastore placement.** At SDK setup Step 7, when the host is
   WSL2 (or any case where the project path is a mounted host filesystem — `/mnt/` on WSL2, and
   the equivalent bind-mount case on the Docker path) say so plainly and give the number: the
   datastore is about to live on a filesystem reached over a protocol that will cost roughly two
   orders of magnitude of load throughput.

2. **Measure rather than assert.** Run `check_repository_performance` once at setup and show the
   insert rate. It takes five seconds, it is Senzing's own prescribed instrument, and it converts
   "this may be slow" into a number the Bootcamper can act on. Source the call and its argument
   from the server at implementation time (INV-080) — it lives on `SzDiagnostic`, not `SzEngine`.
   Non-blocking: a failed or unavailable check reports one line and proceeds (INV-048).

3. **Offer the relocation, and let the Bootcamper decide.** Where the rate is far below what the
   platform should manage, offer a WSL-native datastore path with the trade-off stated: the
   datastore leaves the project directory, so it is not alongside the rest of their artifacts and
   not picked up by a copy of the project folder. This is a real cost, not a formality — and it is
   the Bootcamper's call, not the plugin's (INV-006).

4. **Carve the exception into the `database/G2C.db` rule rather than leaving two rules in
   conflict.** INV-200 and the "always use `database/G2C.db`" instruction must state the one case
   where the datastore may sit outside the project directory, and that it happens only on an
   explicit yes. Left implicit, the next audit reads a relocated datastore as an INV-200 violation
   — and the write-gate may treat the path as out of bounds, which needs checking as part of this
   work.

⛔ **Do not silently default the datastore outside the project directory.** INV-200 exists because
files appearing where the Bootcamper did not put them is its own defect. The default stays
`database/G2C.db`; what changes is that the cost becomes visible and the alternative becomes
available.

## Acceptance criteria

- [ ] On a WSL2 host with the project under `/mnt/`, SDK setup states that the datastore location
      will limit load throughput, before the datastore is created.
- [ ] SDK setup runs `check_repository_performance` once and reports the measured insert rate; a
      failure reports one line and does not block (INV-048).
- [ ] The relocation is offered, never applied without an explicit yes, and the trade-off (datastore
      outside the project directory) is stated in the offer.
- [ ] The `database/G2C.db` rule and INV-200 both name the mounted-filesystem exception and its
      consent requirement.
- [ ] The write-gate permits the relocated datastore path when the Bootcamper accepted it, and the
      behavior is covered by a test.
- [ ] The throughput figures in this spec are recorded as observation-only (one workstation,
      SDK 4.3.4, SQLite, 83,338 records) and are not asserted by the offline suite, which cannot
      measure a filesystem it is not running on.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      warning is silent on platforms where the project directory is not a mounted filesystem.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 7 datastore placement gains
  the crossing detection, the measurement and the offer; the "always use `database/G2C.db`" rules
  (`:1001`, `:1039`, `:1444`) gain the exception
- `plugins/senzing-bootcamp/hooks/write-gate.py` — the relocated datastore path, if the gate blocks
  it today
- `specs/INVARIANTS.md` — INV-200's carve-out for the consented relocation
- `tests/` — write-gate coverage for the relocated path

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Joel.md` → "Improvement: WSL2 + project on /mnt/c
  makes the datastore ~300x slower, and nothing warns" (2026-08-18, Module SDK setup / Data
  processing; `Source: self-observed (assistant retrospective)`)
- Priority: High
- MCP re-check: server 1.33.0, 2026-08-21 — **still reproduces**, and Senzing owns both halves of
  the guidance the plugin never relays. `search_docs(query='loading', category='anti_patterns')`
  returns *Do Not Use Low-IOPS Storage* (avoid network-attached storage for the database directory;
  run `check_repository_performance()`) and *Do Not Skip check_repository_performance() Before
  Production* (with the `SzDiagnostic` signature). The absence is in the plugin, not the server:
  `check_repository_performance` has zero occurrences across
  `plugins/senzing-bootcamp/`, and no shipped file mentions `/mnt/`.
- Upstream: not submitted — the SDK behaves as documented and the anti-patterns are already correct
  and complete. Nothing here is Senzing's to fix.
- Related specs: `specs/auto-detect-platform.md`,
  `specs/sqlite-branch-says-no-additional-setup-but-the-schema-is-required.md`,
  `specs/harden-write-gate.md`, `specs/inv200-overstates-what-the-write-gate-blocks.md`

## Deviations from this spec, and why (2026-08-21)

**Implemented PARTIALLY, by maintainer decision, during an unattended run.** The maintainer reviewed
this spec before implementation and held part of it for their return. What shipped and what did not
is recorded in the `specs/IMPLEMENTED.md` entry, criterion by criterion; the held criteria are
**not ticked** there.

**The partiality is enforced by a guard, not just documented.** A half-implemented spec whose
boundary lives only in prose drifts the moment someone lands the other half — so the held portion is
pinned by a test that fails if it arrives without the shipped side being revisited. That is the
difference between "we did half of this" and "we did half of this and the seam will hold".
