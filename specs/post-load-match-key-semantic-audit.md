# Add a post-load match-key audit — static mapping validation cannot detect semantic errors

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A real mapping defect passed **every** static gate the bootcamp runs, and was caught only by reading match
keys after loading.

EQUIFAX `EFX_YREST` ("Year ESTablished") and ENFORMION `FilingDate` (state incorporation filing date) were
both mapped to the Senzing `REGISTRATION_DATE` feature. They measure different things — a business commonly
operates before it incorporates — so Senzing was told a conflict existed where none did, on up to 676
records. The symptom was `-REGISTRATION_DATE` on nearly every cross-source match key, **suppressing
legitimate merges**.

What did **not** catch it:

| Gate | Verdict |
|---|---|
| `sz_json_analyzer.py` | exit 0, no critical errors |
| `sz_verbatim_check.py` | pass — "all emitted values are verbatim from source" |
| `sz_routing_report.py` | no flag (the field *was* mapped to a feature) |
| Quality re-score | 86.3%, 100% format conformance |
| `mapping_workflow` step-3/step-4 server validation | approved |

Every one is structurally correct and **semantically blind**. The defect was a *claim about meaning*, and
none of these gates evaluates meaning.

Correcting it (routing `EFX_YREST` to payload) and reloading, with no other change: cross-source merges
**1 → 4**, links **160 → 170**, records collapsed **11 → 14**, and the `-REGISTRATION_DATE` suppressor
eliminated from every sampled link.

Why it matters, in the reporter's words: "Mapping is where resolution quality is decided, and the bootcamp's
mapping validation is entirely static. That leaves a whole defect class — two source fields meaning
different things mapped to one feature, or one field's meaning misread — invisible until someone inspects
results. **A bootcamper who finishes the mapping module with all gates green reasonably believes the mapping
is correct. It may be silently suppressing matches.**"

They add: the Entity Specification already states the governing rule — *verify the source field's meaning
matches the feature's definition* — and nothing verifies compliance.

## Root cause

**Confirmed: all mapping validation is static, single-source, and structural.**

`module-05-data-quality-mapping/phase2-data-mapping.md:166-177` defines the validation stack:

> 1. **`sz_json_analyzer.py` (primary validation):** structural + Entity-Specification …
> 2. **`sz_verbatim_check.py` (verbatim-fidelity, optional/best-effort) …**
> 3. **`sz_routing_report.py` (routing-coverage, optional/best-effort) …**
> In short: anchor validation on `sz_json_analyzer.py`; degrade the verbatim and routing checks …

Each is a structural check over **one source at a time**. Nothing compares how two sources populate the
*same* feature — which is precisely the shape of this defect. The quality score
(`phase1-quality-assessment.md:144-152`) measures completeness and format consistency, not semantics.

Downstream, `module-06-data-processing/phaseD-validation.md` never reads match keys. Grep confirms: the
phase's steps 21-28 cover match accuracy, UAT, cross-source counts, and documentation, and the
**Iterate vs. proceed decision gate** (`phaseD-validation.md:159-175`) routes purely on aggregate UAT /
match-accuracy percentages. A suppressor appearing on nearly every cross-source comparison never surfaces,
because nothing tabulates suppressors at all.

So the defect had a clear signal available — `-REGISTRATION_DATE` on almost every cross-source match key —
and no gate looked at it.

## Proposed change

**Add an explicit match-key audit to Module 6 Phase D, before the iterate-vs-proceed gate**
(`phaseD-validation.md:159`):

1. **Extract match keys** from the resolved output (export, or `getEntity` over loaded records).
2. **Tabulate suppressors** — features appearing with a leading `-`, i.e. features that *disagreed* —
   ranked by frequency, separated by single-source vs. cross-source comparisons.
3. **For any suppressor appearing on a large share of cross-source comparisons, require checking whether the
   two sources' fields for that feature genuinely measure the same thing.** Present it as a **finding, not a
   pass/fail** — the reporter is explicit on this, and it matters: a suppressor can be entirely legitimate
   (two records really do disagree), so a hard gate here would produce false failures and train bootcampers
   to dismiss it.
4. **Feed the finding into the iterate-vs-proceed gate** as information the bootcamper sees before deciding.
   Today that gate routes on percentages alone; a high-share cross-source suppressor is exactly the evidence
   that should inform an "iterate now" choice — and this defect is invisible to the UAT number (86.3% quality,
   all gates green).

**Two supporting changes in Module 5:**

5. **Prompt on shared-feature collisions.** When two or more sources map different source fields to the
   **same** Senzing feature, ask for confirmation that they measure the same quantity — especially for date
   and identifier features, where near-miss semantics are common (`year established` vs `filing date`;
   `BID` vs `EFX_ID`). This is a **cross-source** check, which is precisely what the current single-source
   validation stack structurally cannot do, so it needs to live where the per-source mapping decisions are
   collected rather than inside any existing analyzer.
6. **State the limitation plainly.** Add to Module 5 that passing the analyzer, the verbatim gate, and the
   quality score does **not** establish semantic correctness, and that the mapping is not truly validated
   until data is loaded and match keys are read. This session's `EFX_YREST` case is the worked example and is
   worth recording as such — a bootcamper told "all gates green" needs to know what those gates do not cover.

**Implementation notes:**

- Source the match-key extraction method, export flags, and the suppressor notation from the Senzing MCP
  server at implementation time (`search_docs`, `get_sdk_reference`, `reporting_guide`) — not from this spec.
  In particular, confirm the leading-`-` suppressor convention rather than asserting it.
- Read the match keys through generated SDK code / `reporting_guide`, never direct SQL against
  `database/G2C.db`, per Module 6/7's existing rule.
- The audit's findings are natural content for the discoveries document
  (`specs/always-produce-data-discoveries-document.md`), whose required content includes "every merge with
  its match key" and "what was NOT found, and why" — the suppressor table answers the latter directly.
  Implement them so the audit is computed once and consumed by both.

## Acceptance criteria

- [ ] Module 6 Phase D runs a match-key audit before the iterate-vs-proceed gate, extracting match keys via
      MCP-sourced SDK calls (no direct SQL).
- [ ] The audit tabulates suppressor features by frequency, separating single-source from cross-source
      comparisons.
- [ ] A suppressor on a large share of cross-source comparisons is surfaced as a **finding** with a
      prompt to verify the two sources' fields measure the same thing — never as an automatic pass/fail.
- [ ] The finding is presented to the bootcamper before the iterate-vs-proceed decision, alongside the
      existing UAT/match-accuracy percentages.
- [ ] Module 5 prompts for confirmation when two or more sources map different fields to the same Senzing
      feature, calling out date and identifier features specifically.
- [ ] Module 5 states that the static gates do not establish semantic correctness and that mapping is not
      validated until match keys are read post-load.
- [ ] Re-running the reported scenario (two date fields with different meanings mapped to one feature)
      produces a visible finding rather than five green gates.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the audit runs
      through the bootcamper's chosen language via MCP-sourced SDK calls, and the suppressor tabulation is
      not tied to the Python helper scripts.

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — new match-key audit
  step before the Iterate vs. proceed decision gate (line ~159); the gate itself consumes the finding
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — the validation
  stack description (lines ~166-177): state the semantic-blindness limitation; add the shared-feature
  collision prompt where per-source mappings are collected
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` — lines
  ~144-152: note that the quality score does not measure semantic correctness

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Static mapping validation cannot detect semantic
  errors — add a post-load match-key audit" (2026-07-25, cross-cutting; `Source: self-observed (assistant
  retrospective)`)
- Priority: **High**
- Related specs: `specs/always-produce-data-discoveries-document.md` (**shares the match-key analysis —
  compute once, consume twice**), `specs/pin-iterate-proceed-decision-gate.md` (the gate this feeds),
  `specs/detect-dynamic-key-document-shaped-sources.md` (the other mapping-profiling gap),
  `specs/production-volume-question-clarity-and-threading-cutover.md`,
  `specs/graduation-assistant-retrospective-feedback.md` (the retrospective that surfaced this)

## Invariants introduced

- `INV-117` — Before the iterate-vs-proceed gate in Data processing validation, the guide MUST audit
  resolved-entity match keys for semantic correctness (extract `RESOLVED_ENTITY.RECORDS[].MATCH_KEY`
  via MCP-generated SDK code, tabulate `+`/`-`, separate single-source from cross-source) and present
  the result as a finding that feeds the gate's routing, never a pass/fail that blocks; structural
  mapping validation MUST state it is structural, not semantic (recorded in `specs/INVARIANTS.md`).
