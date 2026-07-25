# Add a profile sanity check that recognizes dynamic-key / document-shaped sources

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

ENFORMION's first profile returned **1,373 fields across 500 distinct field patterns** — unmappable. The
cause: the source uses **data values as attribute names**. Each disclosed relationship appears both
correctly inside `FEATURES` *and* as a dynamic root key whose name is the related organization's ID
(`"377957672922": "ADVANCED AESTHETICS THE MED"`). PERSON alone profiled at 1,224 fields, of which roughly
24 were real.

`mapping_workflow` reported the field count **without comment**. Diagnosing it required noticing the absurd
number, inspecting raw records, hypothesising the pattern, and verifying it across the file (all 1,605
dynamic keys matched a `REL_POINTER_KEY` in the same record, 0 exceptions) before pre-processing. Field
counts then collapsed to 45/18.

Why it matters, in the reporter's words: "A 1,373-field profile is not a subtle signal, yet nothing in the
tool interprets it. A bootcamper facing that output has no idea whether their source is genuinely wide,
whether they did something wrong, or whether a known pattern applies. **The plausible failure modes are both
bad: abandon the source, or attempt to map hundreds of meaningless fields.** The pattern is also
mechanically detectable, which makes leaving it to human recall wasteful."

## Root cause

**Confirmed: the profile step reports the count and never interprets it.**

`module-05-data-quality-mapping/phase2-data-mapping.md:117-129` is the whole of step 9:

> ### 9. Profile
>
> Run the profiler, then summarize columns/types/completeness/quality. Advance with
> `action='profile_summary'`.
>
> - **Verbose:** Present a full column table with types, sample values, completeness %, …
> - **Concise:** Present one summary line: N columns detected, X% overall completeness, and key issues only
>   (e.g., "12 columns, 94% complete, 2 fields need attention").

There is **no plausibility check on N**. Worse, the two presentation modes fail differently and both fail
badly at 1,373 fields: Verbose is instructed to "present a full column table" — 1,373 rows of noise — while
Concise reports "1,373 columns detected" as a neutral fact. Neither says *this number means something is
wrong*.

The workflow does sanction pre-processing for sources that "look like a document rather than a table" — but
only as prose the assistant must recall, with no detection to trigger it. Confirmed by grep: no
field-count threshold, plausibility check, or dynamic-key language exists anywhere in the module.

Note the scope boundary: `mapping_workflow` is an **MCP server tool**, so the plugin cannot change what the
profiler returns. The plugin-side fix is to interpret the returned profile — which is sufficient, since the
field count and per-field record coverage are already in the response.

## Proposed change

Add a **profile sanity check** to step 9 that fires when a schema's field count is implausible (say > 100
fields, or > 50 distinct field patterns) and reports the likely cause rather than the raw number:

1. **Detect dynamic/unbounded keys.** Many root keys appearing in only one or two records each — especially
   keys that are purely numeric or otherwise value-shaped. Report the count and a sample rather than the full
   column table.
2. **Cross-check for redundancy.** If those key *names* appear as values elsewhere in the same record (as
   here, matching `REL_POINTER_KEY`), say so — that is precisely what makes dropping them lossless, and it is
   the difference between a safe pre-process and data loss.
3. **Recommend the sanctioned route explicitly** — pre-process, then re-profile — instead of relying on the
   assistant to remember the option exists. Name it as the expected next step, not as a possibility.
4. **Require verification before and after,** as was done in the reported session: prove the removed data is
   redundant, and prove record counts and preserved features are unchanged. The reporter's own remediation
   script verified each dynamic key against the record's own `REL_POINTER_KEY` values before dropping it, and
   confirmed losslessness in both directions (2,500 → 2,500 records; 0 records changed beyond key removal;
   all 1,668 `REL_POINTER` features preserved). That before/after proof is the requirement — without it,
   pre-processing is silent data loss, which is worse than an unmappable profile.
5. **Suppress the full column table when the check fires.** Amend the Verbose presentation so it does not
   print 1,373 rows: when the sanity check trips, both verbosity modes show the diagnosis plus a sample, not
   the exhaustive table. This is a small change that prevents the profile output from being useless in
   exactly the case where the bootcamper most needs to understand it.
6. **Keep it a finding, not a gate.** A genuinely wide source exists. The check reports and recommends; the
   bootcamper decides. Do not block mapping on a field count.
7. **Consider filing upstream.** The detection would be more valuable inside `mapping_workflow` step 1 where
   the profile is computed. The Senzing MCP server exposes a `submit_feedback` tool — the natural channel.
   The plugin-side check should ship regardless, since it works with the data already returned.

## Acceptance criteria

- [ ] Step 9 applies a stated plausibility threshold (e.g. > 100 fields or > 50 distinct field patterns) to
      the profile result.
- [ ] When it trips, the output names the likely cause — dynamic/value-shaped root keys — with a count and a
      sample, instead of reporting a bare field count.
- [ ] The check reports whether those key names appear as values elsewhere in the same record, since that is
      what establishes losslessness.
- [ ] Pre-processing followed by re-profiling is recommended explicitly as the next step.
- [ ] Pre-processing requires before/after verification: removed data proven redundant, and record counts
      and preserved features proven unchanged.
- [ ] Neither verbosity mode prints an exhaustive column table when the check trips.
- [ ] The check never blocks mapping — a genuinely wide source proceeds on the bootcamper's decision.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the check
      interprets the `mapping_workflow` profile response, and any pre-processing is generated in the
      bootcamper's chosen language rather than requiring Python.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — step 9 (lines
  ~117-129): the sanity check, the diagnosis output, the pre-process/re-profile recommendation, the
  before/after verification requirement, and the column-table suppression in both verbosity modes
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` — confirm the
  quality score is not computed over hundreds of phantom fields when the check trips

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Have mapping_workflow detect dynamic-key/
  document-shaped sources proactively" (2026-07-25, Data Quality, Mapping, and Transformation; `Source:
  self-observed (assistant retrospective)`)
- Priority: Medium
- Related specs: `specs/post-load-match-key-semantic-audit.md` (the other mapping-validation blind spot),
  `specs/rename-data-quality-mapping-display-name.md` (this module's display name),
  `specs/graduation-assistant-retrospective-feedback.md` (the retrospective that surfaced this)

## Invariants introduced

- `INV-118` — An implausible profile field count (roughly >100 fields or >50 distinct patterns) MUST
  be diagnosed as likely dynamic keys rather than reported raw or rendered as a full column table,
  cross-checked for redundancy against values already in the record, and resolved by a recommended
  pre-process → re-profile with before/after proof; the check never blocks mapping (recorded in
  `specs/INVARIANTS.md`).
