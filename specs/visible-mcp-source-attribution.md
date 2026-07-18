# Make MCP grounding visible to the bootcamper (inline "via Senzing docs" attribution)

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The bootcamper asked that the business-problem pattern gallery (Customer 360, Fraud
Detection, etc.) — and, by extension, forthcoming Senzing-specific responses — be
generated from the Senzing MCP server, and be visibly grounded in the "truth" the
MCP server returns, so they can trust the answers are real and sourced, not
fabricated. The gallery **was** in fact sourced via `search_docs` (the MCP-first
invariant was followed), but the grounding was not visible/traceable to the
bootcamper — a trust/UX gap, not a rule violation.

## Root cause (confirmed)

The content is MCP-sourced but the sourcing is an internal instruction only, with no
attribution surfaced to the bootcamper:

- The pattern gallery pulls real-world examples via `search_docs`
  (`plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:20-31`,
  "pull real-world examples via `search_docs`") but shows **no** "via Senzing docs"
  citation to the bootcamper.
- In Module 0, MCP attribution is offered only reactively — "Senzing documentation
  via MCP" is shown **if asked** (`module-00-entity-resolution-concepts/concepts.md:30`),
  not proactively.
- The MCP-first invariant (`ground-rules.md:52-70`) mandates MCP sourcing but says
  nothing about surfacing it visibly.

## Proposed change

Keep sourcing all Senzing-specific claims via the MCP server (unchanged), and make
that grounding **visible** to the bootcamper: add a brief, unobtrusive inline
attribution (e.g. "via Senzing docs" / "source: Senzing MCP") on generated
Senzing-specific content such as the pattern-gallery items and comparable generated
material. Add the convention to `ground-rules.md` so it applies going forward, and
apply it at the pattern gallery as the first concrete instance. Respect verbosity
settings (INV-011/INV-012) — the attribution must stay lightweight and be
suppressible at the lowest verbosity presets so it does not become clutter.

## Acceptance criteria

- [ ] The business-problem pattern gallery shows a brief inline attribution indicating the content came from the Senzing MCP server / docs.
- [ ] A general convention for visibly attributing MCP-sourced Senzing content is documented in `ground-rules.md`, so future generated content follows it.
- [ ] Attribution is lightweight and honors verbosity (INV-011/INV-012) — suppressed at the lowest presets; it never replaces or weakens the MCP-first sourcing itself (`ground-rules.md:52-70`).
- [ ] No content is attributed to the MCP server unless an MCP tool actually produced it (attribution must be truthful).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — add visible attribution to the pattern gallery (`:20-31`).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — document the visible-attribution convention (near the MCP-first invariant, `:52-70`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Make MCP-grounding of the business-problem pattern gallery (and all future responses) more visible/traceable" (2026-07-18, Module 1).
- Priority: Medium.
- Related specs: `mcp-grounding-in-every-skill.md` (per-skill MCP rule, distinct — that is internal enforcement; this is external visibility). Upholds the MCP-first invariant.
