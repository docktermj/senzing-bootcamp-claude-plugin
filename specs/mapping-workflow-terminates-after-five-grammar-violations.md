# `mapping_workflow` terminates after five grammar violations, and the plugin never says so

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`mapping_workflow` counts malformed advance payloads and **terminates the workflow after five**.
The plugin's call contract (`module-05-data-quality-mapping/phase2-data-mapping.md:115-150`) covers
what a correct call looks like — `workspace_dir` on `start`, the five action names, the opaque
`state` echo — but nowhere warns that getting it wrong has a budget, or that the budget does not
reset.

Observed on a phase-3 walk, 2026-08-22, MCP server 1.33.0, when a step-3 payload was sent while the
workflow was at step 2:

    ⚠ ENFORCEMENT NOTICE — your client emitted an advance payload the published JSON Schema
    forbids (step2_missing_plan_key); a schema-enforcing client could not have produced it.
    Your client is NOT constraining output to the advance contract, so YOU must hand-match it
    EXACTLY. This is grammar-impossible advance 1 of 5 before this workflow terminates.

The returned `state` then carried `grammar_violation_count: 1`, and **the count persisted through
the subsequent valid advance** — it is cumulative for the run, not a consecutive-failure counter.

Why it matters here specifically: this module runs one full workflow **per source**, and a
bootcamper with several sources meets the same payload shapes repeatedly. Five cumulative mistakes
across a multi-source run is not a remote possibility, and the failure mode is losing the workflow
mid-module — after the mapper code and documentation for earlier sources already exist, which is the
worst point to restart from.

## Root cause

New server-side enforcement the plugin's call contract predates. Nothing in the plugin is wrong; it
is simply silent about a constraint that changes what a payload mistake costs.

The plugin already carries the two rules that consume the budget fastest — the step-1
prose-versus-schema contradiction (send the array) and the five field-names-that-are-not-actions —
so a guide that follows the contract is unlikely to spend violations. The gap is that a guide who
*does* slip has no way to know the run is on a clock.

## Proposed change

Add a short paragraph to the call contract, beside the existing three numbered rules:

- A malformed advance payload returns an `ENFORCEMENT NOTICE` naming the violation
  (e.g. `step2_missing_plan_key`) and counts against a budget of **five per workflow run**, after
  which the workflow terminates.
- The count is **cumulative and does not reset** on a subsequent valid advance; it is visible as
  `grammar_violation_count` in the returned `state`.
- On a rejection, re-read the response's `advance_schema` and match it field for field rather than
  retrying a variant — a second guess spends a second violation.
- State the practical consequence: the budget is per workflow run, and this module starts one run
  per source, so the exposure is per source rather than per module.

Date the observation with the server version, as the file's other MCP claims are dated, so a later
reader can re-check whether the limit still applies.

## Acceptance criteria

- [ ] `phase2-data-mapping.md`'s "Calling `mapping_workflow` correctly" section states the
      five-violation budget, that it is cumulative within a run, and where the count is visible.
- [ ] The guidance says to re-read `advance_schema` on a rejection rather than retrying a variant.
- [ ] The claim carries a server version and date, matching the dating convention used by the
      neighboring MCP claims in the same section.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — the call
  contract gains the budget paragraph.

## Source

- Feedback: `/dry-run` phase 3, Data Quality, Mapping and Transformation (2026-08-22;
  `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: server 1.33.0, 2026-08-22 — reproduced live. One malformed advance returned the
  enforcement notice quoted above and set `grammar_violation_count: 1` in `state`; the next valid
  advance succeeded with the count still at 1. The limit itself ("of 5 before this workflow
  terminates") is the server's own wording, not an inference.
- Upstream: not applicable — this is server behavior the plugin should document, not a server defect.
- Related specs: `specs/a-step-names-what-to-select-without-naming-the-route.md`

## Deviations from this spec, and why (2026-08-23)

⛔ **The spec's central claim about the counter is false on the current server, and the shipped
text says the opposite of what the spec asked for.**

The spec states the count is *"cumulative and does not reset"* on a subsequent valid advance, and
frames the hazard as "five cumulative mistakes across a multi-source run". Re-run end to end
against **server 1.33.0, 2026-08-23**, echoing the returned `state` verbatim at every call:

1. A step-3-shaped payload sent at step 2 → `step2_missing_plan_key`, *"This is grammar-impossible
   advance **1** of 5 before this workflow terminates"*, and `grammar_violation_count: 1` in the
   returned `state` (alongside `last_advance_hash` and `dup_advance_count: 1`, two fields the spec
   does not mention).
2. The next **valid** advance (a well-formed step-2 `master_schemas` payload) succeeded, and the
   returned `state` **omitted `grammar_violation_count` entirely.**
3. A second malformed payload, now at step 3 → `step3_missing_schema_mappings`, and
   *"grammar-impossible advance **1** of 5"* again, with `grammar_violation_count: 1` — **not 2.**

So the counter does not survive a successful advance. From the caller's side — which is the only
side that exists, since `state` is opaque and must be echoed verbatim — it counts **consecutive**
failures. What shipped says that, with the sequence dated.

**Why this mattered rather than being a wording nit:** implementing the spec faithfully would have
written a false Senzing fact into the plugin (INV-080) with a spec file making it look reviewed,
and it would have *overstated* the hazard — losing a run needs five misses in a row, not five
spread across a multi-source session. The budget itself (5, and the enforcement notice's wording)
is confirmed exactly as the spec reported it.

⚠️ **One claim about mechanism was deliberately NOT made.** Whether the server resets a counter or
simply rebuilds `state` per step and omits fields not set on that call is indistinguishable from
the client, so the text says the effect and says the mechanism is not observable, rather than
picking one.

**Established beyond the spec, and shipped because it bounds what a rejection proves:** step 1's
prose `ADVANCE FORMAT` shows `profile_summary` as an object keyed by schema name while its own
embedded schema declares an **array** — and the object form advanced cleanly with `status: ok` and
no enforcement notice. So a shape the schema does not describe is not necessarily a violation, and
a rejection is evidence about that payload rather than a general map of what the tool tolerates.
