# Treat `sz_json_analyzer.py`'s verdict on the supported sub-list format as conformance advice, not a structural failure

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The bootcamp anchors mapping validation on `sz_json_analyzer.py` and treats its result as the
authoritative check. Run against the five CORD sources — all of them retrieved from the MCP server
via `get_sample_data` — it returned exit 1 with **200+ errors per source**:

```text
Line 1: Missing or non-array FEATURES
Line 1: Feature attribute 'RECORD_TYPE' must be inside FEATURES array
```

plus the warning `No NAME features found`. It skipped feature analysis entirely and reported `NAMES`
and `ADDRESSES` as *payload* attributes.

The data is not broken. The Entity Specification served by the **same** MCP server states: "In prior
versions we allowed a flat JSON structure with a separate sub-list for each feature … **While we
still support that**, we now recommend …". Two empirical checks confirmed the Specification, not the
analyzer:

- Loading one unmodified record produced `ENTITY_NAME: 'Bally Technologies Inc'` with features
  `ADDRESS, LEI_NUMBER, NAME, OTHER_ID, RECORD_TYPE, REGISTRATION_COUNTRY` extracted.
- A controlled A/B test on an 18-record cross-source group — each format loaded into a purged
  database in isolation — produced **identical** resolution: 2 entities, largest 17 records,
  spanning the same three sources.

A bootcamper following the analyzer would hand-write five mappers to convert data that already loads
and resolves perfectly. `No NAME features found` is the most damaging line, because names *are*
being extracted — it invites the conclusion that the source is unusable. The severity is also
miscalibrated: conformance-to-recommendation findings are reported as structural **errors** with a
non-zero exit.

This is on the default path, not an edge case. The sample data the plugin hands the bootcamper is in
the format the analyzer rejects, so every CORD-path run reproduces it.

## Root cause

The validation stack has no category for "valid but not the recommended shape", and no tiebreaker
when two MCP-served artifacts disagree.

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md:286-289`
  — "**`sz_json_analyzer.py` (primary validation):** structural + Entity-Specification validation …
  When available, run it and use its result as the **authoritative check**." `:297` repeats it:
  "anchor validation on `sz_json_analyzer.py`".
- The surrounding guidance is entirely about **availability**: `:284-300` degrades the verbatim and
  routing checks when their scripts 404. Nothing addresses an analyzer that runs successfully and
  returns a wrong verdict.
- The ⛔ block at `phase2-data-mapping.md:303-312` is the only escape hatch, and it does not fire
  here by construction: it defines a rejection as unactionable when it "names no field and carries
  no line or pointer the payload could be corrected against" (INV-125). These errors name the field,
  the line, and the remedy. They are *actionable and wrong* — the case with no handling.
- Nothing directs a load probe as the arbiter, even though Module 5 already performs a test load in
  `phase3-test-load.md`. The cheapest available ground truth is one phase later than the gate that
  needs it.

**Upstream component (Senzing MCP server), not fixable in this repository.** `sz_json_analyzer.py`
is served by `download_resource`; its verdict contradicts the Entity Specification served by the
same server. Correct fix at the source: detect the sub-list format and downgrade to an informational
notice, or add a strictness flag. This was offered upstream and **declined**, so the plugin-side
mitigation below is the durable one, not a stopgap.

## Proposed change

1. **Classify the analyzer's findings before acting on them.** In `phase2-data-mapping.md`, split
   the analyzer's output into two kinds:
   - **Structural invalidity** — malformed JSON, missing `DATA_SOURCE`/`RECORD_ID`, unparseable
     records. Blocking; fix before proceeding.
   - **Conformance-to-recommendation** — the record loads and resolves, but does not use the
     recommended shape. Report as an informational notice, never as a reason to remap.

   The `Missing or non-array FEATURES` / `must be inside FEATURES array` family is the named,
   currently-observed instance of the second kind. State the Entity Specification's own wording —
   the sub-list format is **still supported** — and cite it as MCP-sourced (INV-080), re-confirmed at
   implementation time rather than carried from this spec.

2. **Make an empirical load probe the tiebreaker.** When the analyzer reports errors that a
   specification served by the same server says are supported, resolve it by loading one record and
   inspecting the extracted features — not by trusting either document. If the features come back
   extracted, the data is loadable and the finding is conformance advice. Record the probe's result
   and the conclusion in the checkpoint (INV-125 already requires recording the raw failure and the
   concluded cause).

3. **Never let a conformance finding trigger a rewrite.** State plainly that hand-writing a mapper
   to convert a supported format into the recommended one is not required to proceed, and is a real
   cost — five sources in the observed session. Offer the conversion as an optional improvement with
   its rationale (the recommended shape is what new Senzing work should target), never as remediation
   of a defect.

4. **Correct the `No NAME features found` reading.** Add it by name: this warning accompanies the
   sub-list format and does **not** mean names are absent. It is the line most likely to be believed,
   because a bootcamper cannot distinguish "the analyzer did not look in the sub-list" from "there
   are no names".

5. **Keep the exit code out of the gate.** The analyzer's non-zero exit must not by itself stop
   Module 5. Pair this with the existing availability handling so the gate has three outcomes —
   passes, structurally invalid (blocking), conformance-only (informational) — instead of two.

## Acceptance criteria

- [ ] `phase2-data-mapping.md` distinguishes structural invalidity from conformance-to-recommendation
      in the analyzer's output, and only the former blocks.
- [ ] A `Missing or non-array FEATURES` / `Feature attribute … must be inside FEATURES array` report
      over data that loads is handled as informational, with the Entity Specification's
      "we still support that" statement cited and MCP-re-confirmed at implementation time (INV-080).
- [ ] `No NAME features found` is documented as a sub-list-format artifact, not evidence that names
      are missing.
- [ ] When the analyzer and a same-server specification disagree, the guidance requires a
      one-record load probe and records its result and the concluded cause in the checkpoint
      (INV-125).
- [ ] A non-zero analyzer exit alone does not block Module 5, and no guidance directs remapping a
      source solely to satisfy a conformance finding.
- [ ] Running the bootcamp over `get_sample_data`'s CORD sources reaches the test load without a
      hand-written format conversion.
- [ ] No Senzing fact in the new text is asserted from training data — the supported-format claim is
      quoted from the MCP-served specification (INV-080).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      classification is about record shape, not about the mapper's implementation language.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — the
  validation stack at `:284-300` (three outcomes, not two) and the ⛔ rejection block at `:303-312`
  (add the actionable-but-wrong case beside the unactionable one).
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md` — reference
  the load probe as the arbiter already available in this module.
- `tests/` — a test asserting the guidance names the sub-list format as supported and never
  instructs a remap on a conformance-only finding.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "sz_json_analyzer reports the still-supported
  sub-list record format as 200+ structural errors" (2026-07-26, Module Data Quality, Mapping, and
  Transformation; `Source: self-observed (assistant retrospective)`; `Routing: mcp-server`;
  `Upstream: offered, declined`)
- Priority: High
- Related specs: `specs/mapping-workflow-truncated-validation-errors.md` (INV-125 — the
  unactionable-rejection path this sits beside), `specs/post-load-match-key-semantic-audit.md` (the
  same validation stack, and the audit that catches what these gates cannot),
  `specs/mcp-grounding-in-every-skill.md` (INV-080), `specs/detect-dynamic-key-document-shaped-sources.md`

## Invariants introduced

- `INV-144` — A validator's non-zero exit MUST NOT by itself gate a step; findings are classified
  into structural invalidity (blocking) and conformance-to-recommendation (informational), a
  conformance finding never triggers a rewrite, and a tool-vs-specification disagreement is resolved
  by an empirical load probe whose result is recorded (recorded in `specs/INVARIANTS.md`).
- `INV-145` — A record-shape check MUST accept every shape the Entity Specification supports — the
  `FEATURES` array and the legacy flat structure — and MUST determine shape by sampling records
  rather than inferring it from provenance (recorded in `specs/INVARIANTS.md`).

## Correction applied during implementation (2026-07-26)

This spec described the legacy shape as the "per-feature sub-list format". That is **half of it**.
Verified against the MCP server at implementation time: the Entity Specification's wording is "a
flat JSON structure **with** a separate sub-list for each feature that had multiple values" — the
sub-lists are a *part* of the legacy shape, not the whole. A source with no repeating feature is in
that shape with **no sub-list at all**, which is exactly what Las Vegas/`PPP_LOANS` returns
(root-level `BUSINESS_NAME_ORG`, `RECORD_TYPE`, no `FEATURES`). A check keyed on sub-lists would
still have misjudged it. The shipped guidance describes the flat shape correctly.

Also corrected: this spec framed the analyzer as contradicting the Entity Specification. It does
not. The same specification section's *Schema Validation Rules* state `FEATURES (required, array)`;
the analyzer applies the **recommended** schema's rules while the prose grants continued support for
the **legacy** shape. Both are true and answer different questions — the analyzer measures
conformance, the module needs loadability. The guidance says that rather than calling the analyzer
wrong.

Two further call sites the spec did not name were found and fixed: `phase3-test-load.md` instructed
"Fix the structural errors ... in the transformation program" for the flat format (the rewrite this
spec exists to prevent), and `phase1-quality-assessment.md`'s CORD fast-path readiness check
required a `FEATURES` array, classifying every legacy-shaped CORD source as not-ready at the
earliest gate.
