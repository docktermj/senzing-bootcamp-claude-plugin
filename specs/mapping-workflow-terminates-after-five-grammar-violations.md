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
