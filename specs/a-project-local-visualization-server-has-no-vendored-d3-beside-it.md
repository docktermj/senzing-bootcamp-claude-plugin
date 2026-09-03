# A project-local visualization server has no vendored D3 beside it, and Module 7 does not say what to do about that

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The shipped reference server inlines its offline D3 asset, resolving it **relative to its own file**
(`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1635-1639`):

> *"Return an inline `<script>` carrying the vendored D3, so the visualization…"* —
> `os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "d3.v7.min.js")`

That is correct **for the reference**, which sits beside `scripts/vendor/d3.v7.min.js`. But Module 7
does not run the reference: `phase1-query-visualize.md:607` instructs the guide to *"Build it
modeled on the shipped Truth Set visualization server"* — a **new server, written into the
Bootcamper's project**. A file at `<project>/…/viz_server.py` has no `vendor/` directory beside it,
so `__file__`-relative resolution finds nothing, and the module never says what the project-local
copy should do instead.

The consequences split, and only one of them is severe:

- **The standalone snapshot is safe** — D3 is inlined into the generated HTML at build time, so a
  saved snapshot keeps working with no asset lookup at all.
- **The live server is not.** Module 7 frames the visualization as something to keep and return to,
  so a Bootcamper restarting it later needs the asset to still resolve — from a plugin directory a
  plugin update can move, or from nowhere at all if the guide copied the reference's `__file__`
  logic into a file that has no sibling `vendor/`.

⛔ **A CDN fallback is not the fix.** The offline guarantee is the point of vendoring D3 at all, and
the reference correctly refuses to render rather than reaching the network.

## Root cause

`module-07-query-visualize-discover/phase1-query-visualize.md:607` delegates by resemblance —
*"modeled on"* — without naming which parts of the reference are **position-dependent**. The D3
lookup is exactly such a part: it is correct in the plugin's own directory layout and wrong in every
other one. The reference cannot know where its copy will live, and the instruction does not tell the
guide to think about it.

⚠️ **The reporter described a different mechanism, and it no longer exists.** The 2026-08-26 entry
(plugin **0.5.2**) reports the server resolving D3 from `CLAUDE_PLUGIN_ROOT/scripts/vendor/` or
`SENZING_VENDOR_D3` and refusing to render without one. Neither string appears anywhere under
`plugins/` today — the lookup is now `__file__`-relative and the asset is inlined. The **exposure**
the entry names survives the rewrite; its stated cause does not, so this spec is filed against what
ships rather than against what was reported.

## Proposed change

1. **Have Module 7 name the asset question explicitly** where it says to model the server on the
   reference: a project-local server must resolve D3 from a path that exists in the *project*, not
   from the plugin's own directory.
2. **Copy the vendored asset into the project when the visualization is first built**, so the live
   server keeps working across plugin updates and the project stays self-contained. The reporter
   applied this locally and it worked.
3. **Keep the refusal-to-render behavior** when no asset can be found. Failing visibly is correct;
   the offline guarantee (INV-070's family) is what a CDN fallback would break.
4. **State the split**: the standalone snapshot inlines D3 and is unaffected; only the live server
   needs a resolvable asset.

## Acceptance criteria

- [ ] Module 7's "model it on the shipped server" instruction names the D3 asset as
      position-dependent and says what a project-local server must do.
- [ ] The visualization build copies the vendored asset into the Bootcamper's project.
- [ ] A live server restarted from the project resolves D3 without reading anything under the
      plugin directory.
- [ ] No path added by this change reaches the network for D3.
- [ ] The standalone snapshot is unchanged.
- [ ] A repo-level test asserts the instruction names the project-local asset requirement.
      Negative-controlled: remove it, confirm the test fails, restore.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      asset question is the same in every binding the server may be written in.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — :607.
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — the D3 resolution at `:1635-1639`, as
  the reference the guide copies.
- `tests/test_project_local_visualization_finds_its_d3.py` (new) — the guard.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`, entry *"Vendored D3 resolves only through the
  plugin cache, so the live visualization breaks after a plugin update"*, 2026-08-26, module
  **Query, Visualize and Discover**, priority **Low**, `Source: self-observed (assistant
  retrospective)`, plugin 0.5.2, macOS 26.5.2.
- Priority: Low — the snapshot is unaffected and the failure is loud rather than silent.
- MCP re-check: **n/a (no Senzing fact)** — the asset, the lookup and the instruction are all the
  plugin's; no Senzing behavior is involved.
- Upstream: not applicable
- Related specs: `vendor-d3-offline-visualization.md` (implemented — established the vendored,
  inlined asset this spec extends to a project-local server);
  `bundled-file-reads-resolve-like-bundled-script-runs.md` (the same position-dependence class for
  bundled file reads).

## Deviations from this spec, and why (2026-09-01)

**`senzing_viz_server.py` was not changed, though `## Affected files` lists it.** The spec lists it
*"as the reference the guide copies"*, and the reference is **correct as it stands**: it sits beside
`scripts/vendor/` and resolving the asset relative to its own file is right for the plugin's layout.
The defect is in what Module 7 tells the guide to carry over, not in the reference. Changing the
reference to hunt for a project directory it does not live in would break the Truth Set path to fix
a copy that does not exist yet. The guard instead **pins the reference's current behavior as
correct**, so a later edit cannot "fix" it into the project-local form.

**Criterion 3 is implemented but not runtime-verified.** *"A live server restarted from the project
resolves D3 without reading anything under the plugin directory"* is a property of a server the
**guide writes during a bootcamp**, not of any file in this repo. It needs a `dry-run` phase 3 walk
that builds the Module 7 visualization and restarts it. What is asserted here is the instruction.
