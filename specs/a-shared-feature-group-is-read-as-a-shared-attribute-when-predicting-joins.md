# A shared feature *group* is read as a shared *attribute* when predicting cross-source joins

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two sources both scored **IDENTIFIER 100%** on the module's completeness metric, which counts the
group as present when *any* of `NATIONAL_ID` / `PASSPORT` / `TAX_ID` / `LEI` / `TRUSTED_ID` is
populated. On that basis the guide wrote into `docs/data_source_evaluation.md` that they would be
the highest-confidence cross-source pair, "both carrying LEI".

They do not. One source carries **2,375 LEIs**; the other carries **one**, in 137 records — its
identifiers are national IDs and passports. Exactly one LEI value is shared across the entire
dataset. The prediction was wrong by a factor of ~38x on the attribute it named, and it was only
disproved **after loading**, when the match-key distribution showed LEI in a single match key.

The metric is right for what it measures. Completeness asks *does this record carry an identifier at
all*, and grouping is the correct answer to that. The failure is that the same number was then used
to answer a different question — *will these two sources join* — for which presence-of-any is not
evidence. A join needs presence-of-**same**.

## Root cause

**The module defines the group metric carefully and never scopes what it may be used for.**

`module-05-data-quality-mapping/phase1-quality-assessment.md` is unusually rigorous about how the
figure is computed. It already forbids three adjacent measurement errors:

- presence is a property of the **value**, not the key (`:486-490`) — with a worked example of
  `IDENTIFIER_LIST` reading 100% when the true figure was 0%;
- ⛔ sanity-check any 0% or 100% figure before it routes the gate (`:492-497`);
- ⛔ measure per record against the features that apply to that record's `RECORD_TYPE` (`:499-502`).

⚠️ **Every one of those guards the number's accuracy. None guards its interpretation.** The figure
here was *correct* — both sources genuinely carry identifiers in every record. It was then read as a
statement about which identifier, and nothing in the module says it is not one. The
`:492-497` sanity-check is the closest, and it fires on suspiciously uniform figures as a probable
**measurement failure** — here the 100% was real, so a guide following that instruction confirms the
number and proceeds with the wrong inference intact.

**The prediction is a documented deliverable, which is what gives it reach.** It went into
`docs/data_source_evaluation.md` and shaped a load-order rationale before measurement corrected it.
Nothing between writing the prediction and loading re-examines it.

## Proposed change

1. **Scope the metric where it is defined.** One sentence at the completeness definition: a group
   score answers *is an identifier present*, and it is **not** evidence that two sources share an
   identifier — a shared group does not imply a shared attribute.
2. **Require a per-attribute overlap count for any pair whose join is being predicted.** Where the
   module or the evaluation document names an expected cross-source pair, the claim must be backed
   by a count of distinct values shared on the *named* attribute, not by the group scores. It is a
   cheap measurement — the profiling pass already has the values in hand — and it is what would have
   caught this before it was written down.
3. **Say what to write when the overlap is not measured.** A prediction is still useful; an
   unmarked one is what caused the damage. If the per-attribute count was not run, the evaluation
   document says the pair is a *candidate on group coverage, overlap unmeasured*, so a later reader
   knows which kind of claim they are holding.
4. ⚠️ **Do not replace the group metric with a per-attribute one.** It is correct for completeness
   and the quality gate depends on it; per-record-type scoping (`:499-502`) already constrains it
   properly. This adds a second measurement for a second question rather than redefining the first.

## Acceptance criteria

- [ ] The completeness definition states that a group score is not evidence of a shared attribute
      between sources.
- [ ] Any named cross-source join prediction requires a per-attribute distinct-value overlap count
      on the attribute named.
- [ ] An unmeasured prediction is written as a candidate with its overlap explicitly unmeasured,
      rather than as a confidence ranking.
- [ ] The group metric, its per-record-type scoping and the quality gate's routing are unchanged —
      a test asserts the gate still computes the same score on a fixture.
- [ ] A test covers the reported shape: two sources at 100% group coverage whose named attribute
      overlaps in one value, and asserts the guidance does not license the join prediction.
- [ ] Stated as behavior, not as a Python helper, so any implementation language satisfies it
      (INV-002).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  the completeness definition and its consequences block (`:478-502`), and the step that writes the
  source evaluation.
- The step producing `docs/data_source_evaluation.md`, wherever it states a cross-source outlook.
- `tests/` — the group-vs-attribute guard.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "group-based completeness invites reading group coverage as per-identifier coverage" (2026-08-17, Module Data Quality, Mapping, and Transformation, phase 1 step 7; `Source: self-observed (assistant retrospective)`)
- Priority: **Medium.** No data is corrupted and loading corrects it, but a wrong, confident prediction reaches a written deliverable the Bootcamper keeps, and it shaped a load-order decision. It is the class a Bootcamper cannot report — the document reads authoritative and the correction arrives silently in the match keys.
- MCP re-check: **n/a (no Senzing fact).** The completeness metric and its grouping are the plugin's own construct; the feature names it groups (`NATIONAL_ID`, `PASSPORT`, `TAX_ID`, `LEI`, `TRUSTED_ID`) are already-recorded Entity Specification attributes and this spec asserts nothing new about them, nor any absence about the server. Server **1.32.9** (`get_capabilities`, 2026-08-17) recorded for this run.
- Upstream: not applicable — routed `plugin` by the entry, and confirmed.
- Related specs: `specs/completeness-denominator-has-two-readings-on-a-raw-source.md` (the adjacent question of what the figure is computed *over*), `specs/quality-score-per-record-type.md` (the per-record-type scoping this must not disturb), `specs/module5-quality-gate-demands-a-question-its-best-branch-lacks.md`, `specs/step3b-quality-lookup-misroutes-and-omits-the-evidence-requirement.md`, and INV-002.

## Deviations from this spec, and why (2026-08-17)

1. ⚠️ **The `MCP re-check: n/a` line was not taken at face value, and re-asking changed one name.**
   The spec reasons that the grouped feature names are "already-recorded Entity Specification
   attributes" asserting nothing new — true of the spec, but the implementation writes those names
   into **shipped guidance**, which INV-080 forbids doing from a spec without re-confirming this
   session. `search_docs(query='identifier attributes NATIONAL_ID PASSPORT TAX_ID LEI TRUSTED_ID
   exclusive identifier features', category='data_mapping')` on server **1.32.9, 2026-08-17**
   returned the Entity Specification's **Identifiers** section with `TAX_ID`, `NATIONAL_ID` and
   `LEI_NUMBER` as distinct features.

   - **Confirmed** — the group/attribute distinction this spec rests on is the specification's own
     structure, not a plugin construct, which strengthens the case for the guard.
   - **Corrected** — the spec's group list names the member `LEI`. The specification's attribute is
     **`LEI_NUMBER`** ("Legal Entity Identifier"). Shipped guidance uses `LEI_NUMBER`; the bare
     "LEI" survives only inside the quoted worked example, where it reports what a past run wrote.

2. **The evaluation report gained a `## Cross-Source Outlook` section.** The spec requires the two
   labels and the overlap count but does not say where they live, and the existing template had no
   place for a cross-source claim at all — which is part of why one was written into free prose.
   Giving it a named section with the count as a field makes the unmeasured case visible by its
   absence rather than by an editor remembering to add a caveat.

3. **No invariant was drafted or minted.** The rule here ("a group score may not be read as a join
   prediction") is a plausible candidate, but the wording would be mine rather than the maintainer's,
   so it is reported as a candidate instead — consistent with how this session handled every other
   spec that drafts no invariant.
