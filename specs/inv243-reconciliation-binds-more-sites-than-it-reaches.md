# INV-243's reconciliation requirement reaches one site and binds at least four

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

**INV-243** — *a per-source figure reported to the Bootcamper MUST be reconciled against that
source's own input count before it is shown* — and **INV-245** — *a value that failed its own
verification check MUST NOT be presented as a result* — were registered on 2026-08-14 (`68014be`,
`856e7ff`). Both are cited in exactly one place:

```
plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md:140  (INV-243)
plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md:143  (INV-245)
```

Phase C is **conditional** — its own gate skips the whole file unless the bootcamper has two or
more sources. So the invariants reach a path many bootcampers never take, while the paths everyone
takes report per-source figures with no reconciliation required:

1. **`phaseB-load-first-source.md:34-35`** — *"On success, update `load_status` to `loaded` and
   `record_count` to the **actual loaded count** in `config/data_sources.yaml`."* A per-source
   figure is **written to durable state** with nothing comparing it against that source's input
   count. Phase B runs on every path.
2. **`phaseC-multi-source.md:13-16` (step 12)** — *"Read `config/data_sources.yaml` … For each:
   source name / DATA_SOURCE identifier, **record count** … Present a summary table so the
   bootcamper can review."* This **presents** the figure written at (1) directly to the bootcamper.
   It is the clearest INV-243 site in the plugin and sits in the same file as the one citation.
3. **`phaseD-validation.md:136`** — *"Update `docs/loading_strategy.md` with: final load order and
   rationale, **per-source statistics**…"* Per-source figures written into a deliverable.

The defect INV-243 was written for is a figure that is plausible, monotonic and sums correctly.
A count written unreconciled at (1) and displayed at (2) has exactly that shape, and the audit
trail ends at a registry field nobody compared to an input file.

## Root cause

The invariant was minted from one spec, and cited only where that spec's defect appeared. This is
the `production-readiness-audit` skill's defect class 1 in its purest form — *a rule applied to
some of the sites it binds* — and the mechanism is that the implementer cited the rule at the
place the rule was **discovered** rather than sweeping for the places it **governs**.

`coverage_reports.py shipped` cannot catch this: it reports invariants cited by **no** shipped
file, and INV-243 is cited by one, so it scores as covered. The report answers "is this rule
mentioned anywhere?", never "is it mentioned everywhere it binds?" — which is the question the
forward sweep exists to ask by hand.

## Proposed change

1. **Phase B step 7** — require the loaded count to be reconciled against that source's input count
   before it is written to `config/data_sources.yaml`, and require the discrepancy to be reported
   rather than the figure written, citing INV-243 and INV-245. This is the load-bearing one: it is
   where the number enters durable state.
2. **Phase C step 12** — state that the presented record counts are the reconciled figures from the
   registry, and that an unreconciled or disputed count is shown as such rather than as a result
   (INV-245). A summary table is a presentation to the Bootcamper, which is exactly INV-243's trigger.
3. **Phase D step 28** — require per-source statistics written to `docs/loading_strategy.md` to
   carry the same reconciliation.
4. **Add a guard that sweeps rather than lists.** A test that finds every shipped site presenting or
   persisting a per-source count and asserts each cites the reconciliation requirement. Deriving the
   site set is the point — a hardcoded list of three paths reproduces the defect one level up, which
   is how this finding arose.

## Acceptance criteria

- [ ] Phase B's registry write requires reconciliation against the source's input count and cites
      INV-243/INV-245.
- [ ] Phase C step 12's summary table states that the counts shown are reconciled, and what is shown
      when one is not.
- [ ] Phase D's per-source statistics carry the same requirement.
- [ ] A test derives the set of sites that present or persist a per-source figure and asserts each
      one carries the requirement; it fails when any single site's citation is removed.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md` — step 7's
  registry write at `:34-35`.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md` — step 12 at `:13-16`.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — `:136`.
- `tests/test_module06_orchestrator_guidance.py` — or a sibling, widened from one step to a derived set.

## Source

- Feedback: `production-readiness-audit-2026-08-14b` (self-observed; found by the forward invariant
  sweep asking for the full binding set rather than the first site)
- Priority: High
- MCP re-check: **n/a (no Senzing fact).** Entirely internal consistency between INV-243/INV-245 and
  the plugin's own steps. No MCP tool was called and no Senzing claim is asserted.
- Upstream: not applicable
- Related specs: `specs/orchestrator-per-source-stats-vs-static-scaffold-counters.md` (registered
  INV-243 and, on review, INV-245)

## Deviations from this spec, and why (2026-08-14)

Implemented as proposed, all five criteria. Four things differed, and two of them made the fix
better than the spec described.

1. **A fourth site exists and was already compliant.** The derived sweep found
   `module-04-data-collection/SKILL.md` writing `record_count` into the registry — twice, in the
   registry *schema* block and in the CORD fetch instruction — and both already implement INV-243's
   discipline: they record `record_count` (measured), `expected_record_count` (provider-stated) and
   `record_count_matches_expected` under `validation_checks`, "so the comparison stays auditable
   instead of living only in the turn that ran it." That predates INV-243 and states it exactly.
   Nothing was changed there but the citation (INV-183): the rule was reachable in prose and not by
   ID. **The pattern already existed in the plugin, so Phase B was pointed at it rather than
   inventing a parallel one** (INV-003).

2. **Phase B was destroying the baseline it needed to reconcile against — the spec did not see
   this.** The spec says to compare the loaded count "against that source's input count". Phase B
   writes the loaded count into **`record_count`**, which is the *same field* Data collection used
   for the count it measured in the collected file. So the reconciliation's baseline is the value
   the write overwrites. The shipped fix therefore compares **first**, records the outcome as
   `load_count_matches_source` in the registry's own `validation_checks` idiom, and on a mismatch
   **leaves the existing `record_count` in place** rather than overwriting — because overwriting on
   a mismatch destroys the input figure *and* files a partial load as a complete one, after which
   nothing downstream can tell the difference. Reusing the registry's recorded count also keeps one
   source of truth instead of re-counting the input file at load time.

3. **The guard needed two derived signals, not one.** A per-source figure becomes durable in two
   places: the registry (`record_count` + `data_sources.yaml` + a write verb) and a deliverable
   (`per-source statistics` → `docs/loading_strategy.md`). ⚠️ The first version had only the
   registry signal, and the mutation reverting Phase D **escaped** — Phase D was outside the derived
   set entirely, so criterion 3 was unguarded. Two destinations, two signals, and the second is
   the one with the worse failure mode: nothing re-derives a number written into a document.

4. **The detector was deliberately narrowed after a false-positive pass.** A first version keyed on
   `record count` in prose and flagged seven blocks that are not INV-243 sites at all —
   `phase2-discover.md` uses "record count" for an *entity's* record count, Module 4 for a license
   limit, and `phase1-quality-assessment.md` in a source-list warning. A guard that fails on correct
   content is worse than one that misses, so the trigger is the **action** (writing the registry
   field, or writing per-source statistics to a document), not the vocabulary. That narrowing is the
   caveat INV-246 already carries, applied here.

**Mutation-tested: 7 mutations, 1 escaped and was closed, all 7 caught after.** `M1-revert-phaseB`
restores the pre-fix registry write and fails **7** tests; `M7-hardcode-sites` replaces the
derivation with a fixed list and errors, which is what proves the sweep is real (INV-246);
`M2-overwrite-on-mismatch` and `M3-drop-validation-check` pin the two halves the spec did not ask
for; `M6-drop-module4-citation` pins the fourth site.
