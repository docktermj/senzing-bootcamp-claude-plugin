# The "generic concept" label collides with the MCP-first checklist

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-00-entity-resolution-concepts/concepts.md:62` heads the primer's core teaching material
**"What to teach (generic concept, plain language)"** and lists under it: what entity resolution
is, the two failure modes, the five-stage conceptual pipeline (ingestion/standardization →
candidate selection → comparison/scoring → classification → clustering), disclosed vs discovered
relationships, and the three outputs. Only the sub-section beneath it — "How Senzing handles it" —
is marked "(pull specifics from MCP)".

The MCP-first invariant's pre-response checklist
(`bootcamp-onboarding/ground-rules.md`) says a reply containing "entity-resolution technical
details" requires an MCP call **on that turn**. Blocking, scoring, classification and clustering
are entity-resolution technical details. So the two readings of the same paragraph disagree: the
heading licenses the pipeline as generic prose, and the checklist requires it be sourced.

The failure this invites is quiet. A guide taking the "generic" label at face value presents the
pipeline from training data, and it will usually be roughly right — which is exactly why nobody
notices when it is not.

## Root cause

The heading distinguishes *generic concept* from *Senzing-specific*, which is a real distinction
for **attribution** (the material is not proprietary to Senzing) but not the distinction the
MCP-first checklist draws, which is about **whether the claim is an entity-resolution technical
detail**. Two different axes, one label.

The material is in fact fully retrievable, so nothing is lost by requiring the call. Verified on
**MCP server 1.33.0, docs index 2026-08-20 17:33 UTC, 2026-08-22**:
`search_docs('entity resolution pipeline standardization blocking scoring clustering')` returns
*"What Is Entity Resolution? How It Works & Why It Matters."* → "How Does Entity Resolution Work?",
whose five numbered steps match the file's list almost word for word, and
`search_docs('entity resolution false positives false negatives accuracy')` returns the
ambiguous-match / invisible-false-positive material, which is a better account of the two failure
modes than the bare pair the file describes.

## Proposed change

Retitle the section so it names the axis the checklist uses — the material is generic in
*origin* but still MCP-sourced in *presentation* — and add the two queries above to the suggested
list, so the requirement comes with its route (INV-212). One sentence stating that "generic" means
"not Senzing-proprietary", never "exempt from the MCP-first checklist", removes the collision.

Consider whether the ambiguous-match / invisible-false-positive framing should replace the bare
"two failure modes" bullet: it is the same concept, it is what the documentation actually carries,
and it landed well in the walk.

## Acceptance criteria

- [ ] `concepts.md`'s "What to teach" section no longer implies its material may be presented
      without an MCP call, and says explicitly that "generic" describes provenance of the idea,
      not exemption from the pre-response checklist.
- [ ] The suggested-query list carries a query for the pipeline stages and one for the failure
      modes.
- [ ] A test asserts the section does not carry an unqualified exemption-shaped label.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md` — the
  "What to teach" heading, one clarifying sentence, two added suggested queries.
- `tests/` — a guard on the heading.

## Source

- Feedback: `/dry-run` phase 3, analysis from Bootcamp preparation (2026-08-22; Entity Resolution
  Concepts; `Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: server 1.33.0, 2026-08-22 — both queries above run live and returned the material,
  so the fix costs one call per primer and loses nothing.
- Upstream: not applicable
- Related specs: `specs/a-step-names-what-to-select-without-naming-the-route.md`
