# Fix the guaranteed Module 3 Truth-Set snapshot rendering empty

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-038 guarantees the Bootcamper **ALWAYS** sees a dynamic web-app visualization
of the Truth Set. The always-on mandate is enforced by a completion gate that
checks the snapshot artifact exists and is non-empty. But on the default path that
snapshot can render with **zero entities** — a blank visualization that still
passes the gate — so the Bootcamper's guaranteed "wow moment" silently shows
nothing.

## Root cause (confirmed)

The Step 9.2 snapshot command — the exact artifact the completion gate checks —
reads three source files that **no pipeline step ever creates**:

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md:55-63`
  passes `src/system_verification/customers.jsonl`, `reference.jsonl`, and
  `watchlist.jsonl` as three explicit paths.
- Step 2 writes the TruthSet to a **single** file:
  `phase1-verification.md:154` — `src/system_verification/truthset_data.jsonl`
  (Step 5a and the fallback also reference only `truthset_data.jsonl`). No step
  emits per-source files.
- The bundled server globs the three non-existent paths
  (`scripts/senzing_viz_server.py:63-89`) → empty record set → `Model.build`
  yields `records_total=0` → `write_snapshot` still writes a valid, non-empty HTML
  page and exits 0.
- The completion gate (`phase3-report-close.md:6-21`) only checks the file exists
  and is non-empty, so it passes on a ~15 KB zero-entity template.

The live-server command (Step 9.3, `phase2-visualization.md:76-80`) uses the glob
`src/system_verification/*.jsonl`, which matches `truthset_data.jsonl` and works —
so the defect hides behind a working live demo while the durable, gate-enforced
snapshot is empty.

## Proposed change

Make the 9.2 snapshot command consume the same records the live server does:

- Change `phase2-visualization.md:55-63` to pass
  `--records "src/system_verification/"*.jsonl` (matching 9.3 at `:76-80` and the
  server's own docstring example at `senzing_viz_server.py:24`), instead of the
  three hardcoded per-source filenames.
- Harden the completion gate (`phase3-report-close.md:6-21`) to also confirm the
  snapshot contains at least one entity/record (e.g. the server prints a record
  count on `--no-serve`, or the gate greps the emitted HTML/embedded data for a
  non-zero record count), so a zero-entity snapshot no longer satisfies INV-038.

Alternative (heavier, not preferred): have Step 2 additionally emit per-source
files matching the hardcoded names. The glob fix is minimal and keeps a single
source of truth (`truthset_data.jsonl`).

## Acceptance criteria

- [ ] On the default Module 3 path, the Step 9.2 snapshot at
      `docs/visualizations/truthset_verification.html` contains the acquired
      TruthSet entities (non-zero), not an empty template.
- [ ] The completion gate fails (and re-runs Step 9) when the snapshot has zero
      records, rather than passing on a blank page.
- [ ] The Step 9.2 snapshot and the Step 9.3 live server read the same input set,
      so the two never diverge.
- [ ] The Step 2a non-deterministic substitute (whatever DATA_SOURCE codes it
      carries) also renders, since the glob does not assume the three standard
      codes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per
      @INVARIANTS.md) — the change is to the viz invocation/gate, not to any
      bootcamper-language code.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md` — 9.2 snapshot command: replace the three hardcoded filenames with the `*.jsonl` glob.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase3-report-close.md` — completion gate: also require a non-zero record/entity count in the snapshot.
- (Optional) `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — if a machine-readable record count on `--no-serve` is needed for the gate.

## Source

- Invariant audit, 2026-07-17 (deep-dive over the plugin), Module 3 finding — verified by hand: 9.2 references `customers.jsonl`/`reference.jsonl`/`watchlist.jsonl`; Step 2 writes only `truthset_data.jsonl`.
- Priority: High (undermines INV-038, the flagship "always sees a visualization" guarantee).
- Related specs: `module3-register-truthset-data-sources.md` (INV-068, adjacent Step 5a). Upholds INV-038.
