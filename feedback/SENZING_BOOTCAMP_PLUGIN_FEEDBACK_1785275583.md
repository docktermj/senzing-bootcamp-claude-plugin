# Senzing Bootcamp Plugin Feedback

Feedback collected during bootcamp sessions. Saved locally only; never submitted
externally unless the bootcamper explicitly asks.

## Your Feedback

## Improvement: Random sampling silently destroys cross-source overlap, producing a zero-finding load

**Date:** 2026-07-28
**Module:** Data collection
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — Module 4's license-driven sampling (step 6) offers no overlap-preserving guidance, while the equivalent guidance does exist in step 8b's load-time branch.
**Upstream:** not applicable

### What happened

Module 4 step 6 offers sampling when a dataset exceeds the license limit, listing "sampling, a CORD subset, or a smaller substitute dataset" with no guidance on strategy. The natural instinct — a random sample is representative — is correct for profiling and wrong for entity resolution. A random 300-record slice was drawn from each of five sources; the load was flawless (1,147 records, zero errors, redo drained) and produced ZERO cross-source matches outside one already-fully-included pair. The KYC business problem returned no findings from a technically perfect pipeline.

Measuring the full files showed the overlap was real but sparse: 507 shared names across 21,284 x 63,193 candidates for the largest pair. Random slices of large disjoint sets share essentially nothing.

Notably, step 8b (the SQLite load-time warning branch) DOES offer "an entity-resolution-demonstrating strategy that preserves cross-source overlaps and known match clusters". That guidance is correct but lives only in the branch that fires on load-time concerns, not in the license-driven sampling at step 6.

### Why it matters

This failure is invisible by every operational signal a bootcamper is taught to check: records loaded, zero errors, redo queue drained, quality scores 94-100%. It only surfaces in the cross-source matrix, and only if someone thinks to compare it against what the business problem needed. A bootcamper who trusted the green load would conclude Senzing found nothing in their data.

### Suggested fix

Move the overlap-preserving strategy guidance from step 8b into step 6, or cross-reference it. When a dataset is sampled for ANY reason and 2+ sources are present, state plainly that random sampling removes the signal entity resolution exists to find, and offer overlap-aware selection as the default.

### Context when reported

- **Time:** 2026-07-28 14:30 local
- **Plugin version:** 0.4.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** graduation / retrospective (friction occurred in data_collection step 6, surfaced in data_processing)
- **Recent questions:** "My random sample destroyed the cross-source overlap. How would you like to fix it?"
- **Bootcamper responses:** Rebuild an overlap-aware sample
- **Behind the scenes:** Module 4 step 6 license-limit sampling; Module 6 Phase D validation exposed the consequence
- **Observed problem:** Zero cross-source entities outside the OFAC/OpenSanctions pair, from a load reporting complete success
- **Expected behavior:** Sampling guidance that warns random selection destroys cross-source overlap when multiple sources are present
- **Divergence:** The correct guidance exists in step 8b but not in step 6, so the license-driven path silently takes the harmful default

## Improvement: Quality scoring must be per-record-type, or organizations are penalized for having no date of birth

**Date:** 2026-07-28
**Module:** Data Quality, Mapping, and Transformation
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — Phase 1 step 6 defines the presence test rigorously but says nothing about feature applicability differing by record type.
**Upstream:** not applicable

### What happened

Phase 1 step 6 defines "present" with great care (false and 0 count as present; presence is a property of the value, not the key) and warns to sanity-check any 0% or 100% figure. It does not address a different failure: averaging feature coverage across record types where the feature does not apply.

Scoring completeness by aggregate feature percentages rated OFAC — a sanctions list with NAME and ADDRESS on 100% of records — at 52% completeness and 69% overall, landing it in the "Recommend fixing before mapping" band. The cause was averaging DOB (32%), PASSPORT (14%) and GENDER (25%) across a source where 71 of 110 records are ORGANIZATIONS, which have no date of birth or passport by definition. Rescoring per record against features applicable to that record's type gave 97%.

Had the first figure been trusted, the bootcamper would have been sent to remediate data with nothing wrong with it.

### Why it matters

Mixed person/organization sources are the norm in KYC, AML, sanctions screening, vendor MDM and beneficial-ownership work — several of the plugin's own headline use cases. A scoring method that penalizes organizations for lacking person attributes will misreport most real compliance datasets, and it fails toward false alarm: it tells bootcampers to fix data that is fine.

### Suggested fix

Add to Phase 1 step 6: completeness must be measured per record against features applicable to that record's RECORD_TYPE, not as an aggregate across the source. Include the OFAC-style case as the worked example, alongside the existing empty-container example.

### Context when reported

- **Time:** 2026-07-28 13:40 local
- **Plugin version:** 0.4.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** graduation / retrospective (friction occurred in data_quality_mapping Phase 1 step 6)
- **Recent questions:** None — caught before presenting the verdict
- **Bootcamper responses:** N/A
- **Behind the scenes:** Phase 1 step 6 quality thresholds routing the proceed/iterate gate
- **Observed problem:** OFAC scored 69% ("Recommend fixing before mapping") despite NAME and ADDRESS on 100% of records
- **Expected behavior:** A score reflecting that organizations legitimately lack person-only features
- **Divergence:** The documented presence test governs individual values but not cross-record-type applicability, so the aggregate silently mixes inapplicable features into the denominator

## Improvement: Search/Probe example chips are not verified before being offered, contradicting the visualization contract

**Date:** 2026-07-28
**Module:** Truth Set visualization
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the shipped page template does not implement its own stated contract.
**Upstream:** not applicable

### What happened

visualization-api-reference.md states that the Search / Probe example chips are "generated per-dataset from the loaded data and verified live to return at least one match before being offered — a hint that returns nothing is worse than no hint."

The shipped page template (`scripts/senzing_viz_server.py`'s PAGE constant, `loadProbes()`) takes `m.entities.slice(0,6)` from `/api/merges` with no verification. On the bootcamper's own organization-heavy data, the largest merged entity was `A & J MUCKLOW NOMINEES LTD`, whose name returns zero results — `search_by_attributes` is an entity search, not a substring search, and that name does not resolve as a query. The chip shipped dead.

The Truth Set masks this: its entities are mostly persons with names that happen to search cleanly, so the defect does not appear in the module where the app is first built. It appears in Module 7, on real data.

### Why it matters

The dead chip is the first thing a bootcamper is invited to click on the tab designed to showcase search. It fails silently — no error, just an empty result set — and reads as "Senzing could not find its own data".

### Suggested fix

Have the server verify candidate chips against the live search at model-build time and expose only verified names (e.g. a `probe_chips` field on `/api/merges`), with the page preferring that field. Verification cost is a handful of searches per build.

### Context when reported

- **Time:** 2026-07-28 15:20 local
- **Plugin version:** 0.4.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** graduation / retrospective (friction occurred in query_visualize_discover step 3c)
- **Recent questions:** None — caught during agent-side verification before handing the app over
- **Behind the scenes:** loadProbes() in the shipped PAGE template
- **Observed problem:** 1 of 6 offered chips returned zero results
- **Expected behavior:** Per the contract, every offered chip returns at least one match
- **Divergence:** The contract specifies verification; the shipped implementation does not perform it

## Improvement: getRecordPreview requires the data source code to be registered first

**Date:** 2026-07-28
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** both — SDK behavior is undocumented in the indexed reference, and the plugin's readiness-check guidance does not mention the prerequisite.
**Upstream:** submitted 2026-07-28

### What happened

`SzEngine.getRecordPreview(recordDefinition)` returns Senzing's own interpretation of a record without loading it — the authoritative way to check whether an attribute name will actually participate in matching. Used it during Phase 1's Senzing-readiness check and it failed with `SENZ2207|Data source code [ICIJ] does not exist`.

Preview does not persist anything, so requiring prior configuration registration is non-obvious. The fix is trivial once known (register the codes first), but the readiness check naturally runs before registration, since registration belongs to the loading phase.

### Why it matters

Minor, but it sits directly on the path of the most valuable verification available in the mapping module: asking Senzing how it interprets a record, rather than inspecting field names against the specification text. Anything discouraging that check costs more than the two minutes it takes to diagnose.

### Suggested fix

Plugin: note in Phase 1 step 5a that a preview-based readiness check requires the source codes to be registered first. MCP server: document the prerequisite on `getRecordPreview` in the SDK reference.

### Context when reported

- **Time:** 2026-07-28 13:10 local
- **Plugin version:** 0.4.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** graduation / retrospective (friction occurred in data_quality_mapping Phase 1 step 5a)
- **Behind the scenes:** Senzing-readiness check via getRecordPreview
- **Observed problem:** SENZ2207 on a method that performs no write
- **Expected behavior:** Either preview works without registration, or the prerequisite is documented
- **Divergence:** The SDK reference documents the signature and response but not the configuration prerequisite

## Improvement: reporting_guide SQL targets a data mart the bootcamp never builds

**Date:** 2026-07-28
**Module:** Data processing
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** both — the MCP tool returns SQL for a schema that does not exist in a bootcamp workspace, and the plugin routes post-load validation to that tool.
**Upstream:** submitted 2026-07-28

### What happened

Module 6 routes counts and statistics to `reporting_guide`, and the ground rules forbid direct SQL against `database/G2C.db`. `reporting_guide(topic='reports')` returns SQL patterns querying `sz_dm_record`, `sz_dm_entity`, `sz_dm_relation` and `sz_dm_report` — an analytical data mart built separately from exports, which the bootcamp never creates.

So the sanctioned route for post-load validation returns queries that cannot run against anything present. Post-load validation was instead built from SDK calls (one getEntity per loaded record), which works and honors the no-SQL rule, but that is not what the module points at.

### Why it matters

A bootcamper following the routing literally hits a dead end at the validation step of the load module and has no obvious next move — the tool answered, the answer is well-formed, and it is unusable.

### Suggested fix

Either have `reporting_guide` state plainly that its SQL assumes a separately-built data mart and offer an SDK-only alternative for small deployments, or have the plugin route Module 6 validation to `reporting_guide(topic='export')` plus SDK code rather than `topic='reports'`.

### Context when reported

- **Time:** 2026-07-28 14:05 local
- **Plugin version:** 0.4.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** graduation / retrospective (friction occurred in data_processing Phase D)
- **Behind the scenes:** reporting_guide(topic='reports', language='java')
- **Observed problem:** Returned SQL against sz_dm_* tables absent from the workspace
- **Expected behavior:** Guidance runnable against the bootcamp's actual SQLite repository
- **Divergence:** The tool assumes a data-mart deployment; the bootcamp is a single-database evaluation setup

## Improvement: BASH_SOURCE is bash-only, so a sourced env script breaks under zsh (macOS default)

**Date:** 2026-07-28
**Module:** SDK setup
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the module mandates a project-local env script and a source-then-launch pattern, but does not warn that the obvious path-resolution idiom is shell-specific.
**Upstream:** not applicable

### What happened

Module 2 requires a project-local `src/scripts/senzing-env.sh` and instructs sourcing it before running tasks. Resolving the project root inside that script with `${BASH_SOURCE[0]}` — the standard idiom — works when the script is sourced from bash (as the module's own launcher-script pattern does) and expands to EMPTY under zsh, which is macOS's default shell and the shell a bootcamper uses when they follow the "source src/scripts/senzing-env.sh" instruction literally.

The failure is silent: the script still runs, the project root resolves to the wrong directory, the engine configuration comes back empty, and the JVM fails later with "Unable to get settings" — an error that points at the SDK, not at the shell.

### Why it matters

macOS on Apple Silicon is a first-class supported platform for the Java and C# paths, and zsh is its default shell. Any bootcamper who sources the env script directly, as instructed, hits this.

### Suggested fix

Note the shell-portability requirement where the module specifies `senzing-env.sh`, with a working idiom (e.g. branch on `${ZSH_VERSION}` and use `${(%):-%x}` for zsh, `${BASH_SOURCE[0]}` otherwise).

### Context when reported

- **Time:** 2026-07-28 12:15 local
- **Plugin version:** 0.4.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-sonnet-5 / high
- **Context size:** Unknown
- **Module / step:** graduation / retrospective (friction occurred in sdk_setup, surfaced in system_verification)
- **Behind the scenes:** senzing-env.sh sourced directly from zsh rather than via the bash launcher
- **Observed problem:** SENZING_ENGINE_CONFIGURATION_JSON empty; JVM failed with "Unable to get settings"
- **Expected behavior:** The documented "source src/scripts/senzing-env.sh" works in the platform's default shell
- **Divergence:** The idiom the module's own launcher pattern encourages is bash-specific and fails silently under zsh
