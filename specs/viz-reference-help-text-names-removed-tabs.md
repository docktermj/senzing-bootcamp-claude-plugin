# The shipped visualization reference's `--help` text still describes a Relationship Network tab that INV-155 forbids

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`senzing_viz_server.py` is the reference every non-Python Truth Set visualization server is modeled
on (INV-090). Its module docstring — which argparse prints verbatim as `--help`, since
`description=__doc__` at `:1640` — still tells the reader the app has a **Relationship Network tab**:

```text
- ``GET /api/graph``   entity nodes + relationship edges (Entity Graph + Relationship
  Network tabs)
…
The Relationship Network tab reuses ``/api/graph`` (the related-entity subgraph); the
entity-size distribution is the Merge Statistics histogram (``/api/stats``), not a
separate view.
```

INV-155 fixes the tab set at exactly six and requires the relationship view be a **mode** of the
Entity Graph tab, not a tab of its own. A reader building the server in Java or C# from this
reference — the reader INV-090 says exists — is being told to build a seventh tab.

## Root cause

`plugins/senzing-bootcamp/scripts/senzing_viz_server.py`:

- `:18-19` — *"(Entity Graph + Relationship Network **tabs**)"*
- `:34` — *"**The Relationship Network tab** reuses `/api/graph` (the related-entity subgraph)"*

Both are present tense and both are in the docstring, i.e. in `--help`. Everywhere else in the same
file the wording is already correct — the consolidation was done properly in the code and its
comments:

- `:713` — *"'Relationship Network' was …"* (the removal note)
- `:802` — *"the subgraph the **removed** Relationship Network tab showed"*
- `:885` — *"carried over unchanged from the **removed** Relationship Network tab"*
- `:930` — *"**Replaces** the standalone Relationship Network tab"*

and `ALL_TABS` at `:717` declares exactly the six INV-155 requires. So the app is conformant; only
its front-door description is stale.

The consolidation spec that removed the tab — `specs/consolidate-truthset-viz-merges-and-network-tabs.md`
— cited `senzing_viz_server.py:637` (the eight-tab declaration) and its Affected-files entry at
`:142` says *"remove the `merges` and `network` …"*. It set no criterion for the module docstring, so
the docstring was never in scope and nothing caught it. The tab tests
(`test_tab_set_is_singular.py`, `test_viz_tab_consolidation.py`) assert the declaration and the
contract table, not the prose above them.

Note the contrast with `capture_screenshots.py:82-93`, which handles the same legacy ids **correctly
and explicitly**:

```python
# ⛔ `network` and `merges` are RESERVED, not tabs to capture from a current app — a
# current server MUST NOT serve them, and DEFAULT_TABS excludes them. They stay here
# so this helper still names them correctly when pointed at a snapshot saved by an
# earlier eight-tab run …
```

That is the model for how the reference should describe them.

## Proposed change

1. **Correct the two docstring statements** in `senzing_viz_server.py`:
   - `:18-19` — attribute `/api/graph` to the **Entity Graph tab, including its relationship-subgraph
     mode**, not to two tabs.
   - `:34` — restate as: the Entity Graph tab's *"Show only entities with relationships"* mode reuses
     `/api/graph`; the standalone Relationship Network and Record Merges tabs were **removed**
     (INV-155), their unique capabilities living on as that mode and as Search / Probe's
     *"Show all merged entities"* button.
2. **Name the tab set once, positively**, in the docstring: the six tabs of INV-155, in the row order
   of `visualization-api-reference.md`'s tab table (`:602-611`), which remains the ordering authority
   (INV-147) — so a `--help` reader gets the same six in the same order as the contract.
3. **Assert it**, since the existing tab tests deliberately look at the declaration and not the prose:
   extend `tests/test_tab_set_is_singular.py` to scan the module docstring (and, for good measure, the
   rendered `--help` output) for any present-tense claim that `network` or `merges` is a tab. Allow the
   `capture_screenshots.py`-style "removed"/"RESERVED" phrasings so the honest legacy notes keep
   passing.

## Acceptance criteria

- [ ] `senzing_viz_server.py`'s module docstring describes exactly the six INV-155 tabs and attributes
      the relationship view to Entity Graph's mode toggle.
- [ ] No present-tense claim that a Relationship Network or Record Merges **tab** exists remains in the
      docstring; "removed"/"reserved" references are permitted and preserved.
- [ ] `python3 senzing_viz_server.py --help` prints the corrected text (the docstring is the help text).
- [ ] A test scans the docstring — not only the tab declaration — for stale tab claims, and permits the
      explicit "removed"/"RESERVED" phrasing used in `capture_screenshots.py:82-93`.
- [ ] No behavior change: `ALL_TABS` (`:717`), the endpoint set, and every existing viz test are
      untouched and still pass.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the fix is
      documentation in the shipped reference, and its purpose is that a server generated in **any**
      language is built from a correct description (INV-090/INV-124).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — module docstring `:14-36`.
- `tests/test_tab_set_is_singular.py` — extend to cover the docstring / `--help` text.
- `specs/consolidate-truthset-viz-merges-and-network-tabs.md` — append a dated note that the docstring
  was outside the original scope and is discharged here; do not edit its criteria.

## Source

- Feedback: n/a — found by the deep-dive invariant-conformance audit of 2026-07-29, run at the
  maintainer's request; `Source: self-observed (assistant retrospective)`.
- Priority: **Medium** — no runtime effect, but the file is the model INV-090 points every non-Python
  implementer at, and INV-164 records what happens when a defect lives in the reference: it reaches
  generated code.
- MCP re-check: n/a (no Senzing fact — the plugin's own tab inventory). Server **1.32.2** confirmed
  current at triage time via `get_capabilities`, 2026-07-29.
- Upstream: not applicable.
- Related specs: `specs/consolidate-truthset-viz-merges-and-network-tabs.md` and
  `specs/consolidate-merge-statistics-and-results-dashboard-tabs.md` (the consolidations INV-155
  retroactively recorded), the `deep-dive-audit-2026-07-27` ledger entry in `specs/IMPLEMENTED.md`
  (which established INV-155; recorded there directly, with no spec file),
  `specs/organization-search-requires-name-org.md` (INV-164 — a defect in the reference reaching
  generated code), `specs/per-tab-screenshot-capture-and-grounded-captions.md` (INV-124's tab hooks).
