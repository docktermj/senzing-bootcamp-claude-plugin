# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp. Every entry is saved here, whatever it turns
out to be about. Entries routed `mcp-server` may **also** have been forwarded to Senzing —
only ever with your explicit yes, and with identifying details stripped; each entry's
`Upstream:` field records what happened.

**Started:** 2026-07-27

## Your Feedback

## Improvement: Document a workaround for companies that restrict adding new MCP servers

**Date:** 2026-07-27
**Module:** Entity Resolution Concepts
**Priority:** High
**Source:** bootcamper-reported
**Routing:** plugin — the bootcamp's onboarding flow hardcodes a dependency on the public `mcp.senzing.com` endpoint with no documented alternative; a perfect Senzing MCP server would not change the fact that many corporate policies block adding *any* new external MCP server, so the fix belongs in the bootcamp's own guidance/config, not upstream.
**Upstream:** not applicable

### What happened

The bootcamper noted that the bootcamp currently assumes the bootcamper can freely add and connect to the public Senzing MCP server (`https://mcp.senzing.com/mcp`, shipped via the plugin's `.mcp.json`). At commercial companies, adding a brand-new external MCP server is often restricted by security policy, and some organizations may prohibit it outright — which could block an employee from participating in the bootcamp at all.

### Why it matters

Bootcampers at policy-restricted companies have no documented path to participate if they can't get the public MCP server approved/connected — this could stop adoption before it starts for exactly the commercial users Senzing wants to reach.

### Suggested fix

Add a step to the bootcamp guide (likely in onboarding, near the MCP health check) that offers a workaround for bootcampers who can't add the public MCP server — e.g., pointing to a private/self-hosted Senzing MCP server deployment option, or another sanctioned alternative — so the bootcamp isn't a dead end for them.

### Context when reported

- **Time:** 2026-07-27 08:58 PDT
- **Plugin version:** 0.4.1
- **Workstation:** macOS (Darwin), arm64 (Apple Silicon)
- **Model / effort:** claude-sonnet-5 / Unknown
- **Context size:** Unknown
- **Module / step:** `entity_resolution_concepts` / `null` (no modules completed yet)
- **Recent questions:** "Do you have any questions about entity resolution before we continue?" (pending, unanswered when feedback was raised)
- **Bootcamper responses:** Raised this feedback instead of answering the pending question; when asked why it matters, replied by giving the suggested fix directly; priority: High (1)
- **Behind the scenes:** The plugin's `UserPromptSubmit` hook detected a feedback request mid-primer (Entity Resolution Concepts module, `module-00-entity-resolution-concepts`) and triggered the feedback workflow per `bootcamp-onboarding/feedback.md`.
- **Observed problem:** No documented workaround exists in the bootcamp guide for bootcampers whose company will not permit adding the public Senzing MCP server.
- **Expected behavior:** `ground-rules.md`'s MCP-first invariant requires the Senzing MCP server for all Senzing facts, but neither `ground-rules.md` nor `onboarding-flow.md` document an alternative for bootcampers who cannot use the public endpoint.
- **Divergence:** The onboarding flow's MCP health check (`onboarding-flow.md` step 0b) only covers connectivity troubleshooting (internet, proxy allowlisting) — it does not address organizational policy restrictions on adding new MCP servers at all, which is a different kind of blocker with a different kind of fix (e.g., private deployment, IT-approved config).

## Improvement: Proactively tell bootcampers about the "bootcamp feedback:" trigger phrase

**Date:** 2026-07-27
**Module:** Entity Resolution Concepts
**Priority:** Not specified — the bootcamper moved directly to a new feedback item before this was asked.
**Source:** bootcamper-reported
**Routing:** plugin — the feedback trigger phrase is documented only in `ground-rules.md` (a developer-facing skill file), never surfaced to the bootcamper in the welcome/overview or any module banner; this is a bootcamp content gap, not an MCP server issue.
**Upstream:** not applicable

### What happened

The bootcamper wants a note added somewhere in the bootcamp flow letting bootcampers know upfront that they can say "bootcamp feedback:" at any time to report issues or suggestions that help improve the bootcamp.

### Why it matters

Not answered — the bootcamper moved on to a new, unrelated feedback item (about the Senzing web app) before responding to this question.

### Suggested fix

Add a note (e.g., in the WELCOME banner/overview during onboarding, or another prominent early point) informing the bootcamper that saying "bootcamp feedback:" at any time opens the feedback workflow.

### Context when reported

- **Time:** 2026-07-27 09:08 PDT
- **Plugin version:** 0.4.1
- **Workstation:** macOS (Darwin), arm64 (Apple Silicon)
- **Model / effort:** claude-sonnet-5 / Unknown
- **Context size:** Unknown
- **Module / step:** `entity_resolution_concepts` / `null` (no modules completed yet)
- **Recent questions:** "Do you have any questions about entity resolution before we continue?" (still pending from before the first feedback detour); "Why does this matter to you — what would change if that note existed?" (asked for this item, left unanswered)
- **Bootcamper responses:** Described the topic and suggested fix in the opening message; did not answer the "why it matters" follow-up before starting a new feedback item
- **Behind the scenes:** The plugin's `UserPromptSubmit` hook detected a second feedback request while still inside the Entity Resolution Concepts primer (`module-00-entity-resolution-concepts`), before the first feedback item's exit banner had returned the bootcamper to the pending bootcamp question.
- **Observed problem:** Nothing in the bootcamper-facing onboarding content (WELCOME banner, overview) mentions the "bootcamp feedback:" trigger phrase — it only appears in `ground-rules.md`, which the bootcamper never sees.
- **Expected behavior:** Per `ground-rules.md` → "Any-time bootcamper controls," the feedback mechanism is meant to be available and known to the bootcamper throughout — but the onboarding preface (`onboarding-flow.md` step 3, the overview) never mentions it.
- **Divergence:** The feature exists and works (as this very entry demonstrates), but its discoverability relies on the bootcamper already knowing the trigger phrase — which nothing in the bootcamper-facing flow teaches them.

## Improvement: Consider adding the Senzing web app as a curriculum option

**Date:** 2026-07-27
**Module:** Entity Resolution Concepts
**Priority:** Not specified — the bootcamper chose to return to the bootcamp before this was asked.
**Source:** bootcamper-reported
**Routing:** plugin — this is a request about the bootcamp's own curriculum/module design (what tools the curriculum offers), not a defect in any Senzing MCP tool.
**Upstream:** not applicable

### What happened

The bootcamper suggested the bootcamp curriculum consider offering an option to use the Senzing web app (rather than, or alongside, generated SDK code) as part of the modules.

### Why it matters

Not answered — the bootcamper chose to return to the bootcamp before elaborating.

### Suggested fix

Not answered — the bootcamper's opening message is the suggestion itself (add a web-app option to the curriculum); no further detail was given before they returned to the bootcamp.

### Context when reported

- **Time:** 2026-07-27 09:09 PDT
- **Plugin version:** 0.4.1
- **Workstation:** macOS (Darwin), arm64 (Apple Silicon)
- **Model / effort:** claude-sonnet-5 / Unknown
- **Context size:** Unknown
- **Module / step:** `entity_resolution_concepts` / `null` (no modules completed yet)
- **Recent questions:** "Do you have any questions about entity resolution before we continue?" (still pending, from before the feedback detours); "What happened — is this something you ran into, or a general suggestion for the curriculum's design?" (asked for this item, left unanswered)
- **Bootcamper responses:** Gave the topic/suggestion in the opening message, then said "ready to continue the bootcamp" instead of answering the follow-up
- **Behind the scenes:** The plugin's `UserPromptSubmit` hook detected a third feedback request in a row, still inside the Entity Resolution Concepts primer (`module-00-entity-resolution-concepts`), before returning to the still-pending "any questions" gate.
- **Observed problem:** N/A — this is a suggestion, not a defect.
- **Expected behavior:** N/A.
- **Divergence:** N/A — captured as a curriculum enhancement suggestion for the module list (currently SDK-code-focused: `business_problem`, `sdk_setup`, `data_processing`, etc., with `truthset_visualization` as the one existing web-app-based module).

## Improvement: Rebrand the optional "quiz" as a "Q&A" or "knowledge check"

**Date:** 2026-07-27
**Module:** Entity Resolution Concepts
**Priority:** Not specified — the bootcamper moved on to the next module before this was asked.
**Source:** bootcamper-reported
**Routing:** plugin — this is wording/framing used in the bootcamp's own module content (`module-00-entity-resolution-concepts/concepts.md`), not an MCP server issue.
**Upstream:** not applicable

### What happened

The bootcamper suggested renaming the optional post-primer "quiz" to something softer, like "Q&A" or "knowledge check," and framing the offer as something that improves the bootcamper's experience and learning rather than as a test/evaluation.

### Why it matters

Not answered — the bootcamper moved on to the next module before elaborating. Their opening message did note that words like "quiz," "test," or "evaluation" can cause people to recoil.

### Suggested fix

Rename the pinned offer question and any references to "quiz" (in `concepts.md`'s "Optional knowledge-check quiz" section and the pinned "Would you like to test your knowledge of entity resolution with a short quiz?" question) to friendlier language such as "Q&A" or "knowledge check," and frame it as a positive, curiosity-driven learning offering rather than an evaluation.

### Context when reported

- **Time:** 2026-07-27 09:29 PDT
- **Plugin version:** 0.4.1
- **Workstation:** macOS (Darwin), arm64 (Apple Silicon)
- **Model / effort:** claude-sonnet-5 / Unknown
- **Context size:** Unknown
- **Module / step:** `entity_resolution_concepts` / `null` (module not yet marked complete)
- **Recent questions:** "Are you ready to move on to the next module: Discover the Business Problem?" (pending when feedback was raised); "Why does this matter to you — what impact do you think the word 'quiz' has on bootcampers right now?" (asked for this item, left unanswered)
- **Bootcamper responses:** Gave the topic and suggested fix in the opening message; replied "move to next module" instead of answering the follow-up (also serves as their answer to the pending readiness gate)
- **Behind the scenes:** The plugin's `UserPromptSubmit` hook detected a feedback request immediately after the bootcamper completed the optional entity-resolution quiz and the pinned readiness gate was presented.
- **Observed problem:** The module's optional assessment is currently labeled "quiz" throughout (`concepts.md`'s "Optional knowledge-check quiz" section header, and the pinned question text), which the bootcamper felt could read as a test rather than an engaging learning aid.
- **Expected behavior:** N/A — this is a wording/framing suggestion, not a defect.
- **Divergence:** N/A.

## Improvement: SENZ7426 transliteration failure on the official macOS Homebrew Senzing SDK cask

**Date:** 2026-07-27
**Module:** SDK setup / System verification
**Priority:** High
**Source:** bootcamper-reported
**Routing:** mcp-server — the Senzing MCP server's `sdk_guide(topic='install', platform='macos_arm')` guidance recommends this cask as the correct native install path for Java/C# on Apple Silicon with no caveat, but the installed SDK produced from following that guidance exactly does not match what the guidance implies (a working engine); the actual defect is in the cask/`.pkg` payload Senzing publishes, which this MCP-mediated install path is the only channel to report through.
**Upstream:** submitted 2026-07-27 (via `submit_feedback`, category=bug; anonymous submission, no reply path except support@senzing.com)

### What happened

Following the Senzing MCP server's own install guidance exactly (official `senzing/senzingsdk` Homebrew tap, `brew install --cask senzingsdk`, EULA accepted via the cask's actual required variable `HOMEBREW_SENZING_ACCEPT_EULA=i_accept_the_senzing_eula`), the resulting install (SDK 4.3.3.26191) is only partially functional from Java:

- `SzProduct` (version/license) and bare `SzConfigManager`/`SzEngine` object handles work fine.
- Any real native call through **`SzDiagnostic`** or **`SzEngine`** (e.g. `getDiagnostic()`, `getEngine()` follow-up calls, `addRecord()`) fails immediately with `SENZ7426` — `EAS_ERR_XLITERATOR_FAILED: Transliteration failed: No transliteration rules found! Transliteration requires at least one module.`

This was isolated methodically: tested each `SzEnvironment` hub individually, confirmed reproducible on a completely freshly wiped and re-schema'd SQLite database (ruling out corrupted project state), and traced to the cask's installed support-data directory (`/opt/homebrew/opt/senzing/er/data`, only ~14MB) containing transliteration rule files for Burmese, Khmer, and Thai only — no generic/Latin module. Inspected the cask's own Ruby definition (`senzing/homebrew-senzingsdk`): it downloads a single `.pkg` from Senzing's official S3 bucket and stages it verbatim — there is no separate "data" package being omitted by Homebrew; the sparse payload is the complete official artifact for this cask/version. The tap's own README also self-labels this as `Preview Release — Unsupported`.

### Why it matters

This blocks the entire SDK setup / System verification path for any bootcamper on macOS Apple Silicon using Java or C# (the two officially-supported native languages there) via the sanctioned install method the MCP server itself recommends — with no working entity resolution possible until working around it (e.g. switching to Docker for the Senzing runtime).

### Suggested fix

None provided by the bootcamper — flagging for the plugin authors to route upstream to Senzing (the defect is in Senzing's own published cask/`.pkg`, not in the bootcamp plugin's own skills).

### Context when reported

- **Time:** 2026-07-27 10:34 PDT
- **Plugin version:** 0.4.1
- **Workstation:** macOS (Darwin), arm64 (Apple Silicon)
- **Model / effort:** claude-sonnet-5 / high (switched from claude-opus-5 at the start of this module per the best-value nudge)
- **Context size:** Unknown
- **Module / step:** `system_verification` / mid-Phase-1 (Step 3, SDK Initialization check)
- **Recent questions:** "Switch the Java Senzing runtime to Docker now?" (pending, unanswered when feedback was raised); "Do you have a suggested fix, or should I just flag it for the plugin authors to route upstream to Senzing?"; "What priority would you give this?"
- **Bootcamper responses:** Asked whether Senzing/the Java SDK were properly installed, then asked whether the assistant could fix the incomplete functionality, then requested this be recorded as feedback; no suggested fix; priority: High (1)
- **Behind the scenes:** Module 3 (System Verification), Phase 1, Step 3 (SDK Initialization). `generate_scaffold`/`sdk_guide` calls were all MCP-sourced and correct; the failure is in the actual installed runtime, not in code generation.
- **Observed problem:** `SENZ7426` on every real engine/diagnostic call, reproducible from a clean database.
- **Expected behavior:** Following the MCP server's own recommended native macOS install path for Java should produce a fully functional Senzing engine, per `sdk_guide`'s framing of `macos_arm` as a supported native platform for Java/C#.
- **Divergence:** The MCP server's install guidance is accurate as far as it goes (commands, EULA variable, paths all correct), but does not and could not know that Senzing's own currently-published cask artifact for this platform ships an incomplete support-data payload; the guidance and the artifact it points to have diverged.

## Improvement: bootcampers can skip mapping entirely — need non-pre-mapped data, and a readiness check that distinguishes "structurally loadable" from "fully mapped"

**Date:** 2026-07-27
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — this is about the bootcamp's own data-selection path and the logic of its Senzing-readiness / fast-path check (`module-05-data-quality-mapping/phase1-quality-assessment.md` step 5a). The MCP server correctly serves the data it has, including partially-mapped sources; the bootcamp is what routes a learner around the mapping exercise.
**Upstream:** not applicable

### What happened

Reaching the Data Quality/Mapping module, all three data sources (CUSTOMERS, WATCHLIST, REFERENCE — the `truthset` CORD collection, which is what a bootcamp-generated business case is backed by) were already fully mapped to the Senzing Entity Specification: spec attribute names inside a `FEATURES` array, with `DATA_SOURCE` and `RECORD_ID` at the root. The module therefore offered the **fast-path**: skip the mapping phase entirely and go straight to loading.

The bootcamper wants to practice **mapping and configuration changes for different use cases** — arguably the core skill this module teaches — and the current data path routes them around it.

Investigation while capturing this feedback surfaced a **second, related defect**. The other CORD collections are only *partially* mapped. A real `las-vegas` / `PPP_LOANS` record (via `get_sample_data`) mixes spec attributes with raw source columns:

- Spec attributes: `DATA_SOURCE`, `RECORD_ID`, `RECORD_TYPE`, `BUSINESS_NAME_ORG`, `BUSINESS_ADDR_LINE1/CITY/STATE/POSTAL_CODE`
- Unmapped raw columns: `Business_Type`, `CD`, `DateApproved`, `JobsReported`, `Lender`, `Loan_Range`, `NAICS_Code`, `NonProfit`, `OwnedBy`, `OwnedByRaceEthnicity`, `OwnedByVeteran`

That source *is* a genuine mapping exercise. But step 5a's readiness check tests only **structural** indicators (valid JSON, `DATA_SOURCE`/`RECORD_ID` present or derivable, a recognized feature shape). `PPP_LOANS` satisfies all of them, so it would also be classified `senzing_ready: true` and offered the fast-path — skipping the very decisions those 11 unmapped columns demand. **Structurally loadable is not the same as fully mapped, and the check currently conflates the two.**

Notably, the module's own text already anticipates this distinction ("It says nothing about whether a field will be mapped to a feature that **means** the same thing"), but the readiness gate does not act on it.

### Why it matters

The bootcamper specifically wants to practice mapping and configuration changes across different use cases. As it stands, a bootcamper who takes the generated-business-case path (the default when they have no data of their own) can complete the entire bootcamp without ever writing a mapping — the one skill this module exists to teach. The partial-mapping defect means even choosing a richer CORD collection would not reliably reintroduce the exercise.

### Suggested fix

From the bootcamper: provide CORD datasets that are **not** pre-mapped to the Senzing format, so mapping can actually be practiced.

Additional suggestions from the investigation above:

1. Make the readiness check distinguish **structurally loadable** from **fully mapped** — e.g. report the proportion of a record's fields that correspond to Entity Specification attributes, and do not offer the fast-path when a meaningful share are unmapped source columns (`PPP_LOANS` would then correctly route to mapping).
2. When every selected source is fully pre-mapped, offer mapping practice explicitly rather than silently skipping it — e.g. a raw/unmapped variant of the same data, or one of the raw samples from the free-data repository, so the fast-path stays available without costing the learner the skill.
3. Consider making the generated-business-case path prefer a partially-mapped or raw source, since that path is precisely the one taken by bootcampers with no data of their own — the people most likely to need the mapping exercise.

### Context when reported

- **Time:** 2026-07-27 12:22 PDT
- **Plugin version:** 0.4.1
- **Workstation:** macOS (Darwin), arm64 (Apple Silicon)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** `data_quality_mapping` / Phase 1 step 5a (Senzing-readiness check and fast-path offer)
- **Recent questions:** "Your CORD sources CUSTOMERS, WATCHLIST, and REFERENCE are already in Senzing-loadable form ... Would you like to skip the mapping phase and proceed directly to loading in the Data processing module?" (pending when the feedback was raised); "Why does this matter to you — is it that you specifically wanted to practice mapping, or more that any bootcamper on this path silently misses that skill?"; "What priority would you give this?"
- **Bootcamper responses:** "we need CORDs that are not pre-mapped to the senzing format so that the bootcamper can learn how to map data"; "specifically want to practice the mapping and configuration changes based on different use cases"; priority: Medium (2)
- **Behind the scenes:** Phase 1 steps 1-6 had just completed. All three sources scored >=96% quality and passed the readiness check (all 159 records: valid JSON, `DATA_SOURCE` + `RECORD_ID` present, `FEATURES` array shape), so `senzing_ready: true` was written to `config/data_sources.yaml` for each and the fast-path offer was presented.
- **Observed problem:** The only mapping-teaching module offers to skip itself, because the default data for a generated business case arrives fully pre-mapped; and the readiness check would fast-path partially-mapped sources too.
- **Expected behavior:** A module whose stated purpose is data mapping and transformation should ensure the bootcamper encounters a real mapping task, or at minimum make the trade-off explicit rather than presenting skipping as the efficient default.
- **Divergence:** The fast-path (step 5a) is correct for genuinely load-ready data and exists to avoid pointless work — but combined with (a) `truthset` being fully pre-mapped and (b) a readiness test that checks only structure, it can eliminate the module's core learning objective without ever telling the bootcamper that is what happened.


## Improvement: sz_verbatim_check.py rejects two documented Senzing mechanisms, and cannot run on a CSV source at all

**Date:** 2026-07-27
**Module:** Data Quality, Mapping, and Transformation (re-entered from Query, Visualize and Discover)
**Priority:** High
**Source:** assistant-observed during four full `mapping_workflow` runs
**Routing:** mcp-server — `sz_verbatim_check.py` and `sz_routing_report.py` are shipped by `mapping_workflow` step 1 as required step-4 gate scripts, so the MCP server is both the delivery channel and the owner.
**Upstream:** submitted 2026-07-27 (via `submit_feedback`, category=bug; anonymous submission, no reply path except support@senzing.com)

### What happened

Three defects in the step-4 fidelity gate, found while mapping four raw sources
(`OPENSANCTIONS_PEP`, `OFAC_SDN`, `ICIJ`, `UK_COMPANIES_HOUSE`) end to end.

**Defect 1 — the gate rejects the `extract` disposition the same workflow documents.**
Step 3 documents `extract` for prose fields and names OFAC SDN `REMARKS` as its
canonical example. Step 4 then rejects the output. Repro: `ent_num=306`,
`Remarks = "a.k.a. 'BNC'."` → correct extraction emits `NAME_ORG="BNC"` → gate
reports `rec2 NAME_ORG='BNC'` as a violation. `allowed_values()` accepts only a
whole value, a `|`/`;` segment, or a whitespace token; the tokens here are
`a.k.a.` and `'BNC'.`, so **any** correct extraction from prose fails. The
workflow's "Do NOT proceed until it passes" then leaves only bad options: emit
`'BNC'.` (quotes and a period inside a name field), or drop a real alias.

**Defect 2 — the gate rejects `REL_ANCHOR` / `REL_POINTER`.** 31 offenders across
21 records, every one `REL_ANCHOR_DOMAIN`, `REL_POINTER_DOMAIN`, or
`REL_POINTER_ROLE`. `REL_ANCHOR_KEY` and `REL_POINTER_KEY` **pass**, because those
carry real source values — so the objection is precisely and only to the
structural constants, which cannot originate in source data.

Shared cause: `is_exempt()` covers `DATA_SOURCE`, `RECORD_ID` and any `*_TYPE`
attribute, but not `REL_*_DOMAIN` or `REL_POINTER_ROLE`.

**Defect 3 — the gate cannot run on a CSV source.** Both `sz_verbatim_check.py`
and `sz_routing_report.py` call `load_jsonl(source_path)`; usage is
`<source.jsonl> <output.jsonl>`. `mapping_workflow` accepts CSV inputs and step 4
presents both as gates for any source. On CSV both crash with
`json.decoder.JSONDecodeError: Extra data: line 1 column 5 (char 4)`.

### Why it matters

Defects 1 and 2 mean the gate blocks two mechanisms the Entity Specification itself
documents — so a mapper doing the right thing is told it has a code bug, and the
instruction not to proceed pushes toward degrading data quality to satisfy a
heuristic. Defect 3 is quieter but broader: most raw sources are CSV, so for many
bootcampers the fidelity gate probably never runs at all, and a crash reads as
environment trouble rather than a tool limitation.

### Suggested fix

Extend `is_exempt()` to cover `REL_ANCHOR_DOMAIN`, `REL_POINTER_DOMAIN` and
`REL_POINTER_ROLE`. For `extract`, add a substring mode for fields the mapping spec
marks `extract`, or exclude those fields from the equality check. Accept CSV input
(or state the JSONL-only constraint at step 4 so the crash is expected).

### Context when reported

- **Time:** 2026-07-27 ~15:10 PDT
- **Plugin version:** 0.4.1
- **Workstation:** macOS (Darwin) arm64; Senzing runtime in a Linux `container`
- **SDK:** 4.3.3.26191, Java bindings
- **Module / step:** `data_quality_mapping` Phase 2 step 4, across four sources
- **Recent questions:** "Would you like me to submit those two verbatim-gate defects to Senzing as bootcamp feedback?" → yes; "Send this as written?" → yes
- **Bootcamper responses:** approved submission; approved including defect 3 (added by the assistant, flagged as out of the originally-approved scope)
- **Observed problem:** gate fails on correct output for `extract` and relationship mappings; crashes outright on CSV sources
- **Expected behavior:** a fidelity gate should pass output produced by the dispositions and features the same workflow documents, and should run against the input formats the workflow accepts
- **Divergence:** the gate's model of a "faithful" value (whole value / delimiter segment / whitespace token) is correct for plain field-to-attribute mapping but has no representation for extracted substrings or structural relationship scaffolding
- **Workaround used:** `src/scripts/mapping/csv_to_jsonl_shim.py` adapts CSV→JSONL and then calls the checker's own `verify()`, so the executed logic is upstream's, unmodified. Both overrides documented in `config/bootcamp_progress.json` → `mcp_divergences`, and reversible.
- **Evidence the overrides were right:** both rejected constructs were kept and the relationship links resolved in Senzing — `entity "Mossack Fonseca" — level DISCLOSED — matched on +ICIJ_SP(REGISTERED_AGENT:)`. `UK_COMPANIES_HOUSE` passed the gate cleanly because it needs neither mechanism, which is itself evidence the gate breaks only on those two features.

## Improvement: mapping_workflow step-3 field-count warning fires spuriously on every mapping that uses derived entries or a type_discriminator

**Date:** 2026-07-27
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the warning is emitted by `mapping_workflow`'s own step-3 validator.
**Upstream:** offered at graduation

### What happened

Every one of four independent `mapping_workflow` runs exited step 3 with a warning of the form
"mapped N fields ... but profile reported M fields", despite every source field being dispositioned:

| Source | Warning | Reality |
|---|---|---|
| `OPENSANCTIONS_PEP` | mapped 14 vs 16 reported | 6 ignore + 3 feature + 2 payload + 1 discriminator + 4 overrides = 16 |
| `OFAC_SDN` | mapped 13 vs 12 reported | 12, all dispositioned |
| `ICIJ` | mapped 10 vs 7, and 26 vs 21 | 7 and 21, all dispositioned |
| `UK_COMPANIES_HOUSE` | mapped 58 vs 55 reported | 55, all dispositioned |

The counter includes `derived` entries — `RECORD_ID`, `DATA_SOURCE`, `RECORD_TYPE`, `REL_ANCHOR`,
`REL_POINTER` — which are **not source fields**, while excluding fields declared only inside
`type_discriminator.field_overrides`, which **are**. The two errors do not cancel, so the count
is wrong in both directions (12 → 13 high, 16 → 14 low).

### Why it matters

Every mapping that follows the workflow's own guidance trips it: `derived` DATA_SOURCE/RECORD_ID
are mandatory for every master schema, and `type_discriminator` is the prescribed way to handle a
per-record entity type. A warning that fires on all correct output trains the reader to ignore
warnings — which is expensive, because the same step's other warnings are real.

### Suggested fix

Count only entries that reference a source field, and include `type_discriminator.field` plus
every key of `type_discriminator.field_overrides`. Equivalently: compare the set of source-field
names covered against the profiled field set, rather than summing disposition counts.

### Context when reported

- **Time:** 2026-07-27, four runs between ~14:30 and ~15:00 PDT
- **Plugin version:** 0.4.1 · **SDK:** 4.3.3.26191, Java bindings
- **Observed problem:** a spurious count mismatch on every run
- **Expected behavior:** no warning when every source field carries a disposition
- **Divergence:** the count conflates "mapping entries" with "source fields covered"

## Improvement: mapping_workflow emits two profiler commands writing to the same output path for a multi-file source

**Date:** 2026-07-27
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the command list is generated by `mapping_workflow` step 1.
**Upstream:** offered at graduation

### What happened

Starting a mapping run with two input files returned:

```text
python3 data/mapping/sz_schema_generator.py data/raw/icij/nodes-officers.csv -o data/mapping/profile_report.md
python3 data/mapping/sz_schema_generator.py data/raw/icij/nodes-entities.csv -o data/mapping/profile_report.md
```

Both write the **same** `-o` path, so running them as given leaves only the second file's profile.
Step 3 then instructs the reader to consult `profile_report.md` for how "each source file" is
structured — and half of it is gone, silently. Worked around by profiling to separate paths and
concatenating.

### Why it matters

Multi-file sources are exactly the case where the profile matters most (join keys, per-schema
field sets). The failure is silent: the file exists, is well-formed, and describes one schema, so
a mapper written against it looks fine until fields from the lost schema come back blank.

### Suggested fix

Derive a distinct output path per input (e.g. `profile_report_<stem>.md`), or pass all inputs to
one invocation and have the profiler emit one section per file.

### Context when reported

- **Time:** 2026-07-27 ~14:47 PDT · **Plugin version:** 0.4.1
- **Trigger:** `mapping_workflow(action='start', file_paths=[<two CSVs>])`
- **Expected behavior:** each input's profile survives the commands as issued

## Improvement: sz_schema_generator.py cannot profile a headerless CSV, and the plugin's own free-data catalog offers one

**Date:** 2026-07-27
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — `sz_schema_generator.py` is delivered by `mapping_workflow` step 1.
**Upstream:** offered at graduation

### What happened

`samples/raw/ofac-sdn/sdn-sample.csv` from the free-data repository is **headerless** — its own
README documents 12 positional columns. The profiler assumes a header row, so profiling it
directly consumes the first data row as column names: one sanctioned party disappears and every
column is mislabeled with a value from that row.

Worked around by writing a headered copy for profiling only, using the documented column order,
while the mapper still reads the raw headerless file positionally.

### Why it matters

The profile is the basis for every step-3 mapping decision. A mislabeled profile does not fail —
it produces a confident, wrong mapping, and the lost record is a *sanctioned party* silently
absent from a screening list.

Secondary observation from the same file: `-0-` is OFAC's null sentinel, and because it is a
value, the profiler reports **100% population on all 12 columns** when 8 carry no information.
Any completeness score derived from population % rates this source perfect. Worth a note in the
profiler output when a single non-empty token dominates a column.

### Suggested fix

Add a `--no-header` flag (with positional names supplied or generated), and detect the likely case
— a first row whose cell types match the rows below. Optionally flag a dominant sentinel token.

### Context when reported

- **Time:** 2026-07-27 ~14:52 PDT · **Plugin version:** 0.4.1
- **Expected behavior:** a documented headerless source in the recommended free-data catalog can be
  profiled without hand-built scaffolding

## Improvement: free-data ICIJ Offshore Leaks samples were sliced independently, so the relationships file joins to nothing

**Date:** 2026-07-27
**Module:** Data collection / Data Quality, Mapping, and Transformation
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** unclear — the defect is in the `senzing-bootcamp-free-data` sample data, which Module 4
recommends but which is neither the plugin's skills nor the MCP server; routing it to whoever owns
that repository.
**Upstream:** offered at graduation

### What happened

`samples/raw/icij-offshore-leaks/` ships four files. Verified id coverage:

```text
officers   node_id 12000001-12000010
entities   node_id 10000001-10000010
addresses  node_id 24000001-24000010
relationships  node_id_start 10002580, 10004460, …  node_id_end 14091822, 14092925, …
=> resolvable relationship rows: 0 of 10
```

Zero of ten relationship rows reference any node present in the samples, and every row is
`rel_type=registered_address`, so no officer↔entity ownership link exists even in principle.
`nodes-addresses.csv` also has `name` 0% populated, so those rows are address nodes rather than
entities and cannot be loaded as records at all.

### Why it matters

ICIJ Offshore Leaks is the one source in that catalog whose distinguishing value is **disclosed
relationships** — the `REL_ANCHOR`/`REL_POINTER` pattern that nothing else in the catalog
exercises. As sampled, that exercise is impossible, and a bootcamper following the join keys
in good faith gets a silent zero rather than an error. (Recovered here by modeling the
`service_provider` column instead, which is present on all 10 entity rows.)

### Suggested fix

Slice the four files from a connected subgraph: choose N relationship rows first, then include
exactly the nodes they reference. Add a line to the sample README stating whether the files join.

### Context when reported

- **Time:** 2026-07-27 ~14:58 PDT · **Plugin version:** 0.4.1
- **Expected behavior:** a multi-file sample whose join keys resolve, or documentation saying they
  do not

## Improvement: container-lifecycle tracking assumes Docker, so the SessionStart/SessionEnd hooks are inert for a bootcamp running on Apple's `container` CLI

**Date:** 2026-07-27
**Module:** SDK setup (surfacing at every session boundary)
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the `docker_containers` progress key and the hook wording/behavior are the
plugin's.
**Upstream:** n/a (plugin-side)

### What happened

Module 2's Docker path records containers under a `docker_containers` key in
`config/bootcamp_progress.json`, and the session hooks act on it — `SessionEnd` stops recorded
containers with `docker stop`, `SessionStart` surfaces them for restart. This bootcamp ran the
Senzing runtime in **Apple's `container` CLI** (chosen after Docker Desktop could not be installed
non-interactively), which the plugin has no path for, so the container was recorded under the
Docker-shaped key with `runtime: container` noted alongside.

Consequence: every session-boundary message reads "This bootcamp uses Docker container(s):
senzing-bootcamp (unknown)" and offers a restart that would be attempted with `docker`, a binary
not present on this machine. The container in fact survived across a session resume, so nothing
broke — but the hook's report and its remediation are both wrong for this runtime.

### Why it matters

macOS Apple Silicon is a first-class platform in Module 2's routing, and Apple's `container` is a
reasonable choice there when Docker Desktop cannot be installed (it needs interactive
administrator privileges, which an agent cannot supply). A bootcamper in that position gets a
persistent, confidently-worded message naming the wrong tool, and any hook-driven start/stop
silently does nothing.

### Suggested fix

Store the runtime alongside the container (`{"name": …, "runtime": "docker" | "container" | "podman"}`)
and have the hooks dispatch on it, wording the message with the actual runtime. Renaming the key to
`containers` would be clearer; keeping `docker_containers` readable preserves compatibility.

### Context when reported

- **Time:** observed across the whole session; filed 2026-07-27 at graduation
- **Plugin version:** 0.4.1 · **Workstation:** macOS, arm64
- **Observed problem:** hook messages name Docker for a non-Docker runtime; remediation would call a
  missing binary
- **Expected behavior:** the runtime that was actually used is recorded and acted on

## Improvement: the certificate name lives in two places with different consumers, so following the pre-check instruction alone still prints "Bootcamper" on the certificate

**Date:** 2026-07-27
**Module:** Graduation
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — both the pre-check wording and `scripts/generate_recap_pdf.py` are the plugin's.
**Upstream:** n/a (plugin-side)

### What happened

Graduation's Pre-checks step 4 (INV-113) says: when `name` is unusable, ask the pinned question and
"persist the answer as `name` in `config/bootcamp_preferences.yaml`". Did exactly that, then
rendered. The generator reported:

```text
PDF generated: docs/bootcamp_recap.pdf (renderer: fpdf2, rendered 50892 of 51166 source characters (99%))
```

Exit 0, 99% retention, and the `--check --expect-modules` pass reported "Recap complete". The
certificate page nevertheless read:

```text
This certifies that Bootcamper has completed the Senzing Bootcamp on July 27, 2026
```

`generate_recap_pdf.py` reads the name from a **`**Bootcamper:** <name>` preamble meta line in
`docs/bootcamp_recap.md`**, not from `config/bootcamp_preferences.yaml`. Worse, the recap header
already carried the literal line `**Bootcamper:** Bootcamper`, written during an earlier module — so
an idempotent "add the line if absent" fix is a no-op, and the placeholder survives. The fix is to
**replace the value** of an existing line.

### Why it matters

Every success signal was green — exit 0, high retention, completeness check passed — while the
single most visible field on a signed, shareable keepsake was permanently wrong. This is precisely
the class of defect the skill's own "verify the artifact, not the exit code" caution describes, and
it sits in the step that warns about it. A bootcamper who follows the instruction as written, and
trusts the success line, ships a certificate with a placeholder name.

The generator does define `CERTIFICATE_NAME_PLACEHOLDER = "Bootcamper"` and comments that `main()`
warns when it is used — but the warning did not appear in the captured output, and a stderr warning
is weak protection for an irreversible keepsake.

### Suggested fix

Pick one, ideally both:

1. Have `generate_recap_pdf.py` fall back to `name` in `config/bootcamp_preferences.yaml` when the
   recap's `**Bootcamper:**` value is missing **or equal to the placeholder**. One source of truth,
   and the pre-check instruction becomes sufficient on its own.
2. Amend the Pre-checks wording to say explicitly: persist to preferences **and** set
   `**Bootcamper:**` in `docs/bootcamp_recap.md`, replacing an existing placeholder value rather
   than only inserting when absent.

Additionally: make the placeholder warning loud in stdout next to the `PDF generated:` line, since
that is the line the reader trusts.

### Context when reported

- **Time:** 2026-07-27, during graduation Step 1b
- **Plugin version:** 0.4.1 · renderer: fpdf2 2.8.4 (project-local venv)
- **Observed problem:** certificate printed the placeholder despite the documented persistence step
- **Expected behavior:** the answered name reaches the certificate
- **How it was caught:** extracting text from the rendered PDF and probing for the expected name —
  not by trusting the generator's success line
