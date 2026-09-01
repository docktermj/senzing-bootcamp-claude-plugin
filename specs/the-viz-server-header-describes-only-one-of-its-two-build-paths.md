# The visualization server's own header describes only one of its two build paths — the one Module 7 forbids

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:47-49`, in the module header:

> Data source: `get_entity_by_record_id` with `SZ_ENTITY_DEFAULT_FLAGS` (which includes
> `SZ_ENTITY_INCLUDE_ALL_RELATIONS`), so nodes and edges come from **one call per loaded record**.
> No direct SQL is ever run against the database.

Since `the-export-stream-build-is-unreachable-in-the-shipped-server` (2026-09-01, `c64faaa`) the
file has **two** data sources. `build_model` selects the export stream when `--records` is omitted,
and that is the path `module-07-query-visualize-discover/phase1-query-visualize.md:671` **mandates**
for a Bootcamper's own datastore:

> ⛔ **Build the model from the EXPORT STREAM, not one `get_entity` call per record.**

So the header describes, as the file's only behavior, the path the module forbids for the case the
module is about — and the header is the first thing a reader sees.

**The Usage block below it has the same gap**: every example passes `--records`, so a guide reading
the file top-to-bottom never learns the export invocation exists.

⚠️ **This matters because of who reads this file.** Module 7 tells the guide to *"Build it modeled on
the shipped Truth Set visualization server"*. A guide modeling on it reads the header, learns
"one call per loaded record", and implements exactly what the module's own ⛔ rule prohibits — which
is the instruction/reference disagreement `the-export-stream-build-is-unreachable-in-the-shipped-server`
was filed to remove, relocated from the call graph into the file's prose.

## Root cause

The fix wired `build_model` to select between two paths and did not revisit the module header or the
Usage block. This is the **incomplete-application** class (`production-readiness-audit` Step 7,
class 1): one rule, several sites, fixed at one of them — and the site that was missed is the one a
reader meets first.

⚠️ `conformance.py` cannot see this: it scans shipped **markdown**, and this is a Python module
docstring.

## Proposed change

1. **Rewrite the header's "Data source" paragraph to name both paths and when each applies** — the
   records file for the Truth Set, the export stream for a Bootcamper datastore — keeping the "no
   direct SQL" guarantee, which is true of both.
2. **Add an export-form invocation to the Usage block**, so the form is discoverable where the other
   forms are.
3. **Do not restate the flag rationale in the header.** `build_model` already carries it beside the
   call, and INV-179's own lesson is that a rule belongs at the step that needs it; the header
   should name the choice and point down.

## Acceptance criteria

- [ ] The module header names both build paths and the condition selecting each.
- [ ] The Usage block shows an invocation with `--records` and one without.
- [ ] The "no direct SQL" guarantee survives and is stated as covering both paths.
- [ ] The header does not contradict `phase1-query-visualize.md:671`.
- [ ] A repo-level test asserts the header names the export path, so a later edit cannot drop it
      back to describing one. Negative-controlled.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      header describes a strategy, not a binding.

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — the module header (`:47-49`) and the
  Usage block (`:51-57`).
- `tests/test_visualization_model_build_scales.py` — extend.

## Source

- Feedback: none — found by `production-readiness-audit` on 2026-09-01, reading the shipped Python
  changed by the previous audit's own fixes (`Source: self-observed (assistant retrospective)`).
- Priority: Medium — nothing breaks, but a guide told to model on this file is told the wrong thing
  by its opening paragraph, and that is the exact defect the fix above was supposed to close.
- MCP re-check: **n/a (no Senzing fact)** — which path the reference documents is the plugin's own
  choice. The SDK names in the header were verified against server 1.35.3 when the export path was
  written.
- Upstream: not applicable
- Related specs: `the-export-stream-build-is-unreachable-in-the-shipped-server.md` — the fix that
  created the second path and left the header describing one.
