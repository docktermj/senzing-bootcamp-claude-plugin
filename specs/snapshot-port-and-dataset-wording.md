# The retained snapshot hardcodes port 8080 and calls the bootcamper's data "this Truth Set"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The standalone visualization snapshot's Search / Probe tab tells the reader:

> example searches run against **this Truth Set**. In the live app
> (`http://localhost:8080`) you can search any name.

Both claims are wrong in Module 7. There the app points at **the bootcamper's own data**, not the
Truth Set, and the server may have been started on any `--port`. Both strings ship into
`docs/visualizations/*.html` — the retained keepsake — so the artifact the bootcamper keeps tells
them to open a port nothing is listening on and mislabels their own data as a Senzing demo set.

The failure is entirely silent: the snapshot renders, the text is grammatical, and nothing in the
pipeline compares the wording against the port that was actually used or the dataset that was
actually loaded.

## Root cause

Two hardcoded string literals in one place —
`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1539-1540`, inside
`_snapshot_probe_html()`:

```python
note = (
    '<p class="muted">This is a saved snapshot, so live search is disabled. Below are '
    "example searches run against this Truth Set. In the live app "
    "(<code>http://localhost:8080</code>) you can search any name.</p>"
)
```

- **The port** is written as a constant even though the server parses `--port` — so any run on a
  non-default port produces a snapshot pointing at the wrong URL.
- **"this Truth Set"** is correct for the Truth Set visualization module and wrong for Module 7,
  which reuses the same server against the bootcamper's data
  (`consolidate-module7-visualizations-as-truthset-app-tabs`). One code path serves two datasets;
  only one of them is the Truth Set.

Because `_snapshot_probe_html()` receives no port and no dataset label, neither value is available
at the point the text is built — the fix has to thread them in, not just reword.

## Proposed change

1. **Derive the URL from the parsed `--port`.** Pass the port through to the snapshot builder and
   interpolate it, so the retained artifact names the URL the server actually served on. Keep it a
   `localhost` URL — the snapshot is offline and must not imply a remote host (INV-081).
2. **Make the dataset wording neutral.** Replace "this Truth Set" with wording that is true for both
   callers ("this dataset", "the loaded data"). Where a caller knows the dataset's real name, prefer
   passing it in and using it; a neutral default is required either way so a future third caller
   cannot inherit a false label.
3. **State it in the any-language contract**, not only in the Python reference, since the
   visualization server is generated in the bootcamper's chosen language (INV-090/INV-124): the
   snapshot's text MUST NOT hardcode a port or name a dataset the caller did not supply.

## Acceptance criteria

- [ ] A snapshot built from a server started with `--port 9001` contains `9001` and does **not**
      contain `8080`.
- [ ] A snapshot built for Module 7 (bootcamper data) does not contain the phrase "Truth Set".
- [ ] A snapshot built for the Truth Set visualization module is still accurate about what it shows.
- [ ] No port number or dataset name is hardcoded in the snapshot text path; both arrive from the
      caller.
- [ ] The snapshot remains fully offline — the interpolated URL is `localhost` and no remote host is
      implied (INV-081).
- [ ] `visualization-api-reference.md` states the requirement as server behavior, so a server written
      in any language inherits it (INV-090/INV-124).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the change
      is string construction from existing parsed values, with no platform-specific behavior.

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — `_snapshot_probe_html()` (`:1539-1540`)
  and its call site: thread the port and a dataset label through.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — state the no-hardcoded-port / no-assumed-dataset rule in the snapshot section.
- `tests/` — assert a non-default port reaches the snapshot text and that "Truth Set" is absent when
  the caller supplied a different dataset.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Visualization snapshot hardcodes port 8080 and
  calls the data 'this Truth Set'" (2026-07-28, Module Query, Visualize and Discover;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin`; `Upstream: n/a (plugin-side)`)
- Priority: Medium (not stated by the reporter; assessed from impact — it ships two false statements
  into the permanent keepsake, silently, on every non-default-port or non-Truth-Set run)
- MCP re-check: n/a (no Senzing fact — both defects are string literals in a bundled script). Server
  1.32.1 was the version current at triage, 2026-07-28.
- Upstream: not applicable
- Related specs: `specs/consolidate-module7-visualizations-as-truthset-app-tabs.md` (the reuse that
  made "this Truth Set" wrong), `specs/visualization-server-in-chosen-language.md` (INV-090),
  `specs/escape-viz-snapshot-script-payload.md`,
  `specs/rebuild-viz-snapshot-after-customization.md` (INV-130 — the snapshot is the kept artifact)

## Invariants introduced

- `INV-172` — A retained artifact MUST NOT hardcode an environment fact (a port) nor assert a dataset
  identity the caller did not supply; the port comes from the parsed value in use, dataset wording
  from the caller with a neutral default, and a caller-supplied label reaching HTML is escaped
  (recorded in `specs/INVARIANTS.md`).
