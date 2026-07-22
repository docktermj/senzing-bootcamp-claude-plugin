# Invariants

The following is the canonical list of invariants for the Senzing Bootcamp
Claude Plugin (SBCP). They are aspects of the SBCP that must **ALWAYS** be true.
Every spec under `specs/` begins "Maintain the invariant conditions in
@INVARIANTS.md" — no spec may be implemented in a way that violates any invariant
below.

Each invariant has a **stable ID** (`INV-NNN`). The ID is a permanent address:
specs, feedback triage, and audits reference invariants by ID, so IDs are never
renumbered or reused. New invariants are appended (see
[Maintaining this file](#maintaining-this-file)); existing ones are only edited
in place, never removed.

For hints when implementing the features these invariants describe, the Senzing
Bootcamp for Kiro Power may be consulted. Use the appropriate Claude Plugin
techniques to implement the features captured in the Kiro Power hook files and
steering files.

- Repository: <https://github.com/docktermj/senzing-bootcamp-kiro-powers/tree/main>
- Kiro Power: <https://github.com/docktermj/senzing-bootcamp-kiro-powers/tree/main/senzing-bootcamp>

## Maintaining this file

This file is machine-extended: as specs are implemented, the guarantee a spec
establishes becomes an invariant that all future work must maintain. The
`implement-spec` skill appends those invariants here. To keep the file
deterministically extensible, follow these rules:

1. **Never delete or renumber an existing invariant.** IDs are permanent
   references. If an invariant becomes obsolete, mark it (e.g. append
   "(superseded by INV-NNN)") rather than removing it.
2. **Editing an existing invariant** is allowed only to clarify wording without
   changing its meaning. A change of meaning is a *new* invariant with a new ID.
3. **To add an invariant**, append it under
   [Invariants added from implemented specs](#invariants-added-from-implemented-specs)
   using the **next unused `INV-NNN`** — that is, one greater than the highest
   `INV-NNN` anywhere in this file (zero-padded to three digits). Record its
   provenance (the spec that established it and the date).
4. **Phrase every invariant as a single, testable MUST/ALWAYS condition.** If a
   spec establishes several, add one invariant per condition.
5. The `## Invariants added from implemented specs` heading and its append marker
   below must be preserved so tooling can locate the insertion point.

---

## INV-001 – INV-004: Foundational constraints

These apply to the SBCP as a whole and to every module, spec, and artifact.

- **INV-001** — The SBCP MUST run on the following platforms: Linux, macOS, and Windows.
- **INV-002** — The SBCP MUST be programming-language agnostic.
- **INV-003** — The SBCP MUST be consistent, coherent, and complete.
- **INV-004** — The SBCP MUST be production-ready.

## INV-005 – INV-015: Whole-Bootcamp outcomes

When the Bootcamper runs the SBCP, these MUST hold across the entire Bootcamp.

- **INV-005** — Each question to the Bootcamper is preceded by "👉".
- **INV-006** — Each question is asked only once, unless the Bootcamper asks to have the question repeated.
- **INV-007** — All questions MUST be answered by the Bootcamper. The plugin cannot answer questions nor assume answers.
- **INV-008** — Questions are not ambiguous with respect to a "Yes" or "No" answer.
- **INV-009** — Questions are not "complex". The use of "or" is discouraged.
- **INV-010** — At any time, a Bootcamper can submit "Bootcamp feedback:".
- **INV-011** — At any time, a Bootcamper can change the verbosity of the Bootcamp.
- **INV-012** — All output MUST be relative to the Bootcamper's point of view. Output that is not important to the Bootcamper is suppressed.
- **INV-013** — All shipped modules are performed in order: Module 1 → 2 → 3 → 4 → 5 → 6 → 7. (Advanced Topics — performance, security, monitoring, deployment — ship as production-hardening follow-ups delivered at graduation, not as separate numbered Modules 8-11.) (An optional, non-counted Module 0 preamble is exempt from this ordering — see INV-072.) (Superseded by INV-076: Core runs all modules in order; Customized runs the selected subset in prerequisite order.)
- **INV-014** — Modules are not skipped unless requested by the Bootcamper. (Skipping the optional Module 0 preamble is a permitted, requested skip — see INV-072.) (Customized module selection is such a request: an optional module the Bootcamper does not select is a requested skip — see INV-076.)
- **INV-015** — Submitted bootcamp feedback is captured in `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`.

## INV-016 – INV-018: Bootcamp administration outcomes

- **INV-016** — Every hook's documented purpose begins with the word "to" (e.g. "to process your request", "to review what you said"), as recorded in the hooks' README Purpose column (the Kiro named-hook convention). This governs the hook's stated purpose/name, not necessarily the runtime string a hook emits to the model. (Wording clarified in place, no meaning change; Source: `audit-polish-cleanup`, 2026-07-19.)
- **INV-017** — All Markdown files (`.md`) are kept in appropriate places in the `docs/` directory. Exception: the generated `production/` project deliverable carries its own Markdown files (e.g. `README.md`, `MIGRATION_CHECKLIST.md`, `GRADUATION_REPORT.md`).
- **INV-018** — All code files (e.g. `.py`, `.java`, etc.) are kept in appropriate places in the `src/` directory.

## INV-019 – INV-027: Bootcamp preface outcomes

INV-019–INV-021 (the entity-resolution concepts outcomes) have been relocated out of the preface
into the optional **Module 0** (superseded by INV-073; see INV-072). The preface proper now begins
at INV-022 and presents INV-022–INV-027 in order.

- **INV-019** — A banner is presented, "ENTITY RESOLUTION CONCEPTS". (superseded by INV-073.)
- **INV-020** — A description of Entity Resolution is given. (superseded by INV-073.)
- **INV-021** — The Bootcamper is asked if they want to discuss/explore Entity Resolution before beginning. (superseded by INV-073.)
- **INV-022** — A banner is presented, "WELCOME TO THE SENZING BOOTCAMP!".
- **INV-023** — An overview of the Bootcamp is given.
- **INV-024** — The Bootcamper is asked what level of detail they would like in the Bootcamp output. (Superseded by INV-075: now asked in the Bootcamp preparation module, not the preface.)
- **INV-025** — The Bootcamper is asked to choose a track. (Superseded by INV-076: the track question is replaced by the Core-vs-Customized path choice plus module selection, asked in the Bootcamp preparation module.)
- **INV-026** — The Bootcamper is asked which programming language they would like to use. (Superseded by INV-075: now asked in the Bootcamp preparation module, not the preface.)
- **INV-027** — The Bootcamper is asked if they have any questions at this point.

## INV-028 – INV-032: Per-module outcomes

These hold at the boundaries of every module.

- **INV-028** — At the beginning of each module, a banner is presented "MODULE n: [title]". (Superseded by INV-079: the banner is "MODULE: [title]", name only, no number.)
- **INV-029** — At the beginning of each module, show modules completed, the current module, and upcoming modules.
- **INV-030** — At the beginning of each module, explain what is true before the module and what will be true after completing the module.
- **INV-031** — At the beginning of each module, enumerate the steps that will be taken in the module.
- **INV-032** — At the end of each module, give the Bootcamper a list of what was accomplished, what files were produced, why it matters, and what's next.

## INV-033 – INV-046: Module-specific outcomes

**Module 1**

- **INV-033** — The Bootcamper is asked if they want to see a gallery of common business problems that Entity Resolution solves.
- **INV-034** — The Bootcamper describes the business issue requiring Entity Resolution.

**Module 2**

- **INV-035** — The Senzing SDK is installed.
- **INV-036** — A Senzing license is established, by one of:
  - Using the built-in evaluation license.
  - Identifying an existing, owned Senzing license.
  - Requesting a temporary Senzing license via the Senzing MCP server.
  - (The interactive custom-License-Key prompt is relocated out of Module 2 to Module 4 and volume-gated by **INV-093**; the built-in evaluation license is still established here in Module 2 with no prompt, so this invariant remains satisfied at Module 2. Clarification: `single-license-gate-at-data-processing`, 2026-07-22.)
- **INV-037** — A database is initialized for use by Senzing.

**Module 3**

- **INV-038** — The Bootcamper **ALWAYS** sees a dynamic web-app visualization of the Truth Set to verify that Senzing works on the Bootcamper's workstation. (Superseded by INV-077: the visualization is delivered by the selectable Truth Set visualization module — guaranteed when selected, always in Core.)

**Module 4**

- **INV-039** — Data sources to be loaded into Senzing are identified. This is known as the "raw" data.

**Module 5**

- **INV-040** — The "raw" data is analyzed to see if mapping and transformation is needed. (CORD data does not require mapping nor transformation.)
- **INV-041** — The "raw" data undergoes mapping to determine how to transform data into "Senzing-ready" data. (CORD fast-pathed sources are exempt — they route directly to loading with no mapping, per INV-040; the already-Senzing-ready fast-path class is CORD, offered only for `provenance: cord`, so a non-CORD source that looks Senzing-ready still goes through mapping. Clarified 2026-07-19 to mirror INV-040's caveat, and 2026-07-20 to state the fast-path class is CORD (`module5-fastpath-cord-only-vs-senzing-ready`); no meaning change.)
- **INV-042** — Code is created to transform data according to mapping rules. (CORD fast-pathed sources need no transformation, so no transform code is created for them, per INV-040; the fast-path class is CORD, offered only for `provenance: cord`. Clarified 2026-07-19 to mirror INV-040's caveat, and 2026-07-20 to state the fast-path class is CORD (`module5-fastpath-cord-only-vs-senzing-ready`); no meaning change.)
- **INV-043** — Using the code, the "raw" data is transformed to Senzing-ready data. (CORD fast-pathed sources are already Senzing-ready and route directly to loading with no transformation, per INV-040; the fast-path class is CORD, offered only for `provenance: cord`. Clarified 2026-07-19 to mirror INV-040's caveat, and 2026-07-20 to state the fast-path class is CORD (`module5-fastpath-cord-only-vs-senzing-ready`); no meaning change.)

**Module 6**

- **INV-044** — Code is created to load the transformed data.
- **INV-045** — Using the code, the transformed data is loaded into Senzing.

**Module 7**

- **INV-046** — Code is created to query, visualize, and discover the results of Senzing Entity Resolution. Query code is always created; visualization and discovery are **offered**, and their code/artifacts are created when the Bootcamper accepts — a Bootcamper's decline is a requested skip (INV-014). (Clarified 2026-07-19 to reflect the offered/opt-in reality permitted by INV-014; no meaning change.)

## INV-047 – INV-049: Graduation outcomes

- **INV-047** — A banner is presented, "GRADUATION".
- **INV-048** — A recap PDF, `docs/bootcamp_recap.pdf`, is **always** created. It must be very professional looking (iterate to make it look professional) and contains "Information Shared", "Questions & Responses", "Actions Taken", and "Journal". (Wording clarified in place 2026-07-20; no meaning change. Source: `drop-trophy-wording`.)
- **INV-049** — The `production/` directory is populated.

## INV-050: Project layout

- **INV-050** — The generated Bootcamp project MUST follow this layout:

  ```text
  senzing-bootcamp/
  ├── README.md                          # Project overview
  ├── config/                            # Configuration & progress tracking
  │   ├── bootcamp_preferences.yaml      # Bootcamp settings (language, options)
  │   ├── bootcamp_progress.json         # Current module + completed modules
  │   ├── data_sources.yaml              # Registered data source definitions
  │   ├── engine_config.json             # Senzing engine configuration
  │   ├── license.json                   # Detected Senzing license capacity (written in Module 2)
  │   ├── cord_metadata.yaml             # CORD dataset provenance snapshot (written in Module 4)
  │   ├── session_log.jsonl              # Session activity log (reserved)
  │   └── visualization_tracker.json     # Visualization run tracking (reserved)
  ├── data/                              # All data artifacts
  │   ├── raw/                           # Source data as received
  │   ├── senzing-ready/                 # Senzing-mapped JSONL output
  │   ├── mapping/                       # Mapping working data (specs, samples, intermediates)
  │   ├── samples/                       # Sample fixtures
  │   ├── temp/                          # Scratch/intermediate working files
  │   └── backups/                       # Data backups (reserved)
  ├── database/                          # SQLite Senzing repository
  ├── src/                               # Source code
  │   ├── transform/                     # Source-to-Senzing mappers
  │   ├── load/                          # Loading & redo processing
  │   ├── query/                         # Query, search & discovery
  │   ├── server/                        # Truth Set viz server, generated in the chosen language (INV-090; Python runs the bundled reference)
  │   ├── system_verification/           # Pipeline verification (synthetic VERIFY data) + Truth Set viz artifacts
  │   ├── scripts/                       # Setup & data-generation utilities
  │   ├── resources/                     # Downloaded Senzing resources
  │   └── utils/                         # Shared helpers
  ├── docs/                              # Documentation
  │   ├── README.md
  │   ├── business_problem.md
  │   ├── data_source_evaluation.md
  │   ├── bootcamp_journal.md            # (legacy; superseded by the consolidated bootcamp_recap.md, INV-085)
  │   ├── bootcamp_recap.md
  │   ├── bootcamp_recap.pdf
  │   ├── completion_summary.md          # (reserved)
  │   ├── stakeholder_summary_module{n}.md
  │   ├── mapping/                       # Per-source mapping docs
  │   ├── reference/
  │   ├── progress/
  │   ├── visualizations/                # Generated HTML visualizations
  │   └── feedback/
  │       └── SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md
  ├── licenses/
  │   └── g2.lic                         # Senzing license
  ├── logs/                              # Run logs & result summaries
  ├── backups/                           # Project backups/archives (reserved)
  ├── monitoring/                        # Monitoring assets (reserved; Advanced Topics follow-up)
  ├── tests/                             # Test suite (reserved)
  └── production/                        # Production project (generated at graduation)
  ```

  The tree lists the canonical/primary artifacts, not an exhaustive whitelist: additional
  per-source and per-module working files the flow creates — e.g. `config/mapping_state_*.json`,
  `config/er_current_*.json` / `config/er_baseline_*.json`, `config/fallback_sources.yaml`, and the
  per-module `docs/*.md` write-ups (`docs/data_source_locations.md`, `docs/loading_strategy.md`,
  `docs/results_validation.md`, etc.) — live under the enumerated directories and are consistent
  with this layout. (Clarified 2026-07-20 per the final-review audit; no meaning change.)

## Invariants added from implemented specs

Invariants below were established by implemented specs and are maintained by the
`implement-spec` skill. Append new entries directly beneath the marker using the
next unused `INV-NNN` (see [Maintaining this file](#maintaining-this-file)).

<!-- New invariants go directly below this line. Format:

- **INV-NNN** — <single testable MUST/ALWAYS condition.> (Source: `<spec-name>`, YYYY-MM-DD.)

-->

- **INV-051** — Every 👉 question to the Bootcamper that offers two or more choices MUST use a neutral lead question followed by a numbered list; the choices are never joined with "or" (a testable hardening of INV-009). Legitimate yes/no answer-format hints (e.g. "respond yes or no") are exempt. (Source: `interaction-or-questions`, 2026-07-15.)
- **INV-052** — All plugin hooks MUST be Python 3 scripts invoked in Claude Code exec form (`command: "python3"` plus the script path in `args`), so hook execution has no shell dependency on Linux, macOS, or Windows. Hooks may require only `python3` on `PATH` (already a bootcamp prerequisite via the Module 3 visualization server and the graduation recap); any other runtime MUST be optional with a graceful fallback. A hook added as a shell script, or via shell-form invocation, is a violation. (Source: `cross-platform-hook-execution`, 2026-07-15.)
- **INV-053** — Every bootcamp feedback entry written to `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` MUST include a diagnostic "Context when reported" section — capturing, where available, the time, plugin version, current module and step, recent questions and the Bootcamper's responses, behind-the-scenes state, the observed problem, the expected behavior, and the expected-vs-actual divergence — gathered silently (no extra question), with "Unknown" for missing sources. (Source: `enrich-feedback-context`, 2026-07-15.)
- **INV-054** — The Stop-hook closing-question safety net MUST NEVER cause the Bootcamper to see the same 👉 question twice; it MUST block only when it can positively determine the current turn ended without a 👉 question, and MUST stay silent whenever that determination is not decisive (no readable transcript, or the turn's assistant text is not yet flushed). (Source: `stop-hook-false-positive`, 2026-07-16.)
- **INV-055** — The Stop-hook nudge MUST be disableable via a documented opt-out — the `SENZING_BOOTCAMP_DISABLE_STOP_NUDGE` environment variable or a `disable_stop_nudge` key in `config/bootcamp_preferences.yaml`. (Source: `stop-hook-false-positive`, 2026-07-16.)
- **INV-056** — Every mandatory (⛔) gate question presented to the Bootcamper MUST have its exact wording pinned verbatim in the skill file, not left to the model to improvise, so it cannot drift into an INV-008/INV-051 violation at runtime. (Source: `onboarding-explore-gate-wording`, 2026-07-16.)
- **INV-057** — A terminal "END OF SENZING BOOTCAMP" banner MUST be presented exactly once, as the final output, after the Bootcamper declines further exploration at the end of graduation, and never while exploration continues. (Source: `end-of-bootcamp-banner`, 2026-07-16.)
- **INV-058** — Administrative config writes (progress and preferences) MUST be batched to step and module boundaries rather than performed on every sub-step, preferring minimal single writes, and the onboarding preface MUST persist all preface choices in one consolidated write (a concrete hardening of INV-012). (Source: `suppress-admin-write-noise`, 2026-07-16.)
- **INV-059** — The in-progress module recap MUST be checkpointed to `docs/progress/recap_checkpoint.md` at step boundaries and folded — append-only, idempotently, and never rewriting a completed `## Module N:` section — into `docs/bootcamp_recap.md` by the `PreCompact`, `SessionEnd`, and `SessionStart` hooks, so a module interrupted mid-way never loses its recap narrative. (Source: `recap-durability`, 2026-07-16.)
- **INV-060** — CommonMark prettification of bootcamp-authored `*.md` files MUST be deferred to graduation: during the bootcamp the guide writes functional, plain Markdown without incremental lint compliance, and graduation MUST perform a single best-effort, structure- and content-preserving CommonMark normalization pass over `docs/*.md` (before the recap PDF renders) and the generated `production/*.md`, never reordering, removing, or rewriting completed `## Module N:` recap sections or their four required subsections. (Source: `defer-commonmark-to-graduation`, 2026-07-16.)
- **INV-061** — The bootcamp MUST auto-detect the operating system and architecture (from the environment, else `uname`/`systeminfo`), persist them during onboarding, and reuse them in later modules rather than re-asking; a platform question may be presented only as a fallback when detection is genuinely unavailable or ambiguous, and its wording stays pinned verbatim (INV-056). (Source: `auto-detect-platform`, 2026-07-16.)
- **INV-062** — At every module start, and at graduation start, the guide MUST surface the recommended session model and reasoning effort as a concise, non-blocking suggestion carrying the exact `/model` and `/effort` commands — never as a 👉 question or ⛔ gate, and never blocking progress. The specific per-stage model/effort values are advisory (maintained in `docs/model-selection.md`) and are not part of the invariant. (Source: `module-start-model-nudge`, 2026-07-16.) (Superseded by INV-063.)
- **INV-063** — At every module start and graduation start, the guide MUST surface the recommended session model and reasoning effort with the exact `/model` and `/effort` commands. When the recommendation **changes** from the current stage, it MUST pause with a single 👉 yes/no question offering the switch — its own yielding turn, never combined with another 👉 question; when unchanged, it remains a concise, non-blocking statement. The guide MUST never change the session itself and MUST never block beyond that one optional question. The specific per-stage model/effort values are advisory (maintained in `docs/model-selection.md`) and are not part of the invariant. (Supersedes INV-062.) (Qualified by INV-098: the "exact commands" apply to the Claude Code CLI surface; on Desktop, web, or IDE surfaces, or when the surface is unknown, the nudge phrases the recommendation by intent.) (Source: `model-effort-change-prompt`, 2026-07-16.)
- **INV-064** — When the Bootcamper accepts a recommended model/effort switch at a module start or graduation start, the guide MUST continue the accepted path in a **single** turn: a one-line statement instructing the `/model`/`/effort` commands, immediately followed by the stage's first step, ending that turn on that step's single 👉 question. It MUST NOT insert a separate confirmation-only gate between the switch and the first step, and MUST NOT defer the first step to a later turn. (Hardens INV-005/INV-054 for the accepted-switch continuation; complements INV-063.) (Source: `model-switch-single-turn-continuation`, 2026-07-16.) (Superseded by INV-069.)
- **INV-065** — A sanitized, non-PII example recap MUST ship inside the plugin — a source `.md` fixture at `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` and its rendered `bootcamp_recap.example.pdf` — the PDF MUST remain regenerable from the `.md` via `generate_recap_pdf.py`, and neither MUST contain real personal data. (Complements INV-048; hardens INV-004 for shipped example assets.) (Source: `example-recap-reference`, 2026-07-17.)
- **INV-066** — Any Python package install the plugin instructs MUST use an explicit interpreter (`python3 -m pip`, never bare `pip`) and be robust to PEP 668 externally-managed environments (prefer a project-local virtualenv), and MUST NOT modify the global/system Python; where a working fallback exists (e.g. the recap PDF's stdlib renderer), an install failure MUST degrade to it rather than block. (Hardens INV-052/INV-048 and the file-placement rules.) (Source: `robust-fpdf2-install`, 2026-07-17.)
- **INV-067** — When bootcamp feedback is appended to `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`, the write MUST be verified to have landed (re-read and confirm the entry is present, re-appending if not) before the bootcamper is told it was saved, and no later bootcamp step (CommonMark normalization, production build, cleanup) may delete or empty that file. (Hardens INV-015; mirrors the recap verify of INV-059.) (Source: `feedback-file-durability`, 2026-07-17.)
- **INV-068** — Module 3 MUST register the TruthSet data source codes (CUSTOMERS, REFERENCE, WATCHLIST for the standard TruthSet, or the codes present in the acquired data for the Step 2a substitute) and commit them as the default engine config **before** the Step 6 data load runs, so the load never fails with SENZ2207 for those codes on the first attempt. (Upholds INV-038.) (Superseded by INV-083.) (Source: `module3-register-truthset-data-sources`, 2026-07-17.)
- **INV-069** — When the Bootcamper accepts a recommended model/effort switch at a module start or graduation start, the guide MUST end that reply turn on a single confirmation gate whose wording is pinned verbatim (INV-056) — "👉 Are you done modifying the model and effort?" — presented after the one-line `/model`/`/effort` run-commands statement, and MUST defer the stage's first step to the turn after the Bootcamper confirms. The gate is asked only once (INV-006); the switch-offer question remains its own prior yielding turn (INV-063). On a declined switch, the first step lands on the reply turn with no gate. (Supersedes INV-064.) (Source: `model-effort-switch-done-confirmation`, 2026-07-17.)
- **INV-070** — Every generated HTML visualization the bootcamp produces MUST be written under the generated project's `docs/visualizations/` directory, never the `docs/` root or another `docs/` subdirectory. (Hardens INV-050.) (Source: `layout-tree-reconciliation`, 2026-07-17.)
- **INV-071** — The bundled visualization (`scripts/senzing_viz_server.py`) MUST render with no network access: D3 is vendored inside the plugin (`scripts/vendor/d3.v7.min.js`) and inlined into both the live page and the standalone snapshot, with the `d3js.org` CDN referenced only as a fallback when the vendored asset is missing. (Hardens INV-004/INV-038; complements INV-052.) (Superseded by INV-091: the offline-rendering guarantee now covers the Truth Set visualization server built in the Bootcamper's chosen language, not only the bundled Python one.) (Source: `vendor-d3-offline-visualization`, 2026-07-17.)
- **INV-072** — Entity Resolution Concepts is delivered as an optional "Module 0", presented after the onboarding preface and before Module 1, offered via a pinned-verbatim (INV-056) 👉 skip/keep gate. It is NOT counted among the mandatory numbered Modules 1–7 (exempt from INV-013's ordering) and skipping it is a permitted, requested skip (exempt from INV-014); it does NOT run the per-module completion apparatus (no journey map, before/after, step overview, `docs/bootcamp_recap.md` section, or `modules_completed` entry). (Source: `entity-resolution-module-zero`, 2026-07-17.) (Superseded by INV-078: Module 0 inclusion is driven by Bootcamp preparation selection; the skip/keep gate is retired.)
- **INV-073** — When the Bootcamper chooses to run Module 0 (does not skip it), Module 0 MUST present the ENTITY RESOLUTION CONCEPTS banner, a Senzing-MCP-sourced description of entity resolution, and the pinned-verbatim explore gate ("Are you ready to move on to the next module: Discover the Business Problem?") before handing off to Module 1. (Supersedes INV-019, INV-020, INV-021.) (Source: `entity-resolution-module-zero`, 2026-07-17.)
- **INV-074** — The bootcamp feedback workflow MUST be bracketed by pinned-verbatim banners: a "BOOTCAMP FEEDBACK" entry banner before its first 👉 question, and a "FEEDBACK SAVED — BACK TO THE BOOTCAMP" exit banner (a statement, not a question) after the entry is confirmed saved and before the pending bootcamp 👉 question is re-presented. (Complements the bookend banners INV-022/INV-047/INV-057; upholds INV-005/INV-006 on resume.) (Source: `feedback-flow-boundary-banner`, 2026-07-17.)
- **INV-075** — Bootcamp preparation is the first, mandatory module, run after the onboarding WELCOME preface. It presents the Core-vs-Customized path choice, per-module selection, the level-of-detail (verbosity) question, the programming-language question, and the version-control (git-init) question, and persists them in one consolidated write (INV-058). It is a lightweight setup module, exempt from the per-module completion apparatus (no journey map, before/after framing, step overview, `docs/bootcamp_recap.md` section, or `modules_completed` entry). (Relocates the verbosity and programming-language outcomes out of the preface; supersedes INV-024 and INV-026.) (See also INV-088: the software-integration and deployment-target questions were relocated into this module, then moved back to Module 1 Phase 2 by INV-097.) (The version-control/git-init **question** is removed by INV-095 — git is initialized automatically with no prompt; the git-init action and its persisted `git_init` value are retained.) (INV-099 relaxes this exemption to add a bootcamper-facing setup-choices recap at handoff; prep is still never added to `modules_completed` and still writes no recap-file section.) (Source: `customizable-module-selection`, 2026-07-18.)
- **INV-076** — In Bootcamp preparation the Bootcamper chooses a path: Core (every module, in order) or Customized (the required modules plus whichever optional modules the Bootcamper selects, run in prerequisite/dependency order). Required modules are always included and cannot be deselected; an optional module the Bootcamper does not select is a requested skip (INV-014). (Supersedes INV-013 and INV-025.) (Source: `customizable-module-selection`, 2026-07-18.)
- **INV-077** — The guaranteed Truth Set web-app visualization is delivered by the selectable "Truth Set visualization" module (a standalone module, `module-03b-truthset-visualization`; formerly Module 3, Phase 2 — see INV-087): it MUST be produced whenever that module is selected (always in Core; in Customized only if chosen); when it is not selected, no workstation-verification visualization is produced. (Supersedes INV-038; INV-070/INV-071 on how the visualization renders still apply when it runs.) (Source: `customizable-module-selection`, 2026-07-18; standalone-module location clarified by `split-truthset-visualization-into-standalone-module`, 2026-07-20.)
- **INV-078** — The optional Entity Resolution Concepts primer (Module 0) runs if and only if it was selected during Bootcamp preparation (Core always includes it; Customized includes it only if chosen); it has no separate skip/keep gate. When it runs it still presents the ENTITY RESOLUTION CONCEPTS banner, an MCP-sourced description, and the pinned explore gate (INV-073), and remains a lightweight preamble exempt from the per-module completion apparatus. (Supersedes the skip/keep-gate mechanism of INV-072.) (Amended by INV-092: Module 0 now appends its own name-based recap section and is added to `modules_completed` at its close, though it stays exempt from the rest of the module-start apparatus and the bootcamper-facing end-of-module summary.) (Source: `customizable-module-selection`, 2026-07-18.)
- **INV-079** — Bootcamper-facing module references use the module NAME, not a fixed number: the module-start banner is "MODULE: [NAME IN CAPS]" (no number); module-transition/readiness 👉 questions name the next module ("Are you ready to move on to the next module: {name}?"); and the end-of-module completion line is "✅ Module complete: {Module name}" (no number), lightly highlighted (bold, wrapped in a thin `─` rule — more visible than plain prose, lighter than the module-start banner). Internal references (module titles, prerequisites, cross-references, recap `## Module N:` headings, progress keys) may still use numbers. (Supersedes INV-028.) (The recap `## Module N:` heading clause is superseded by INV-085: recap headings are name-based.) (Source: `module-references-by-name-not-number`, 2026-07-18.)
- **INV-080** — Every bootcamp skill that can produce bootcamper-facing Senzing content MUST carry, prominently near the top of its `SKILL.md`, an explicit MCP-grounding / no-speculation clause — stating that all Senzing facts (SDK method and attribute names, config options, error codes, and entity-resolution specifics) come from the Senzing MCP tools and never from training data or speculation, and including the pre-response checklist — not merely a passing reference to "MCP-first". The canonical rule and tool routing remain the "MCP-first invariant" in `ground-rules.md`. (Source: `mcp-grounding-in-every-skill`, 2026-07-18.)
- **INV-081** — Every bootcamper-facing visual deliverable the bootcamp generates (the Truth-Set visualization web app and its standalone snapshot, the recap PDF, and any future generated charts/dashboards/HTML/PDF) MUST take its palette and typography from the shared Senzing brand tokens shipped at `plugins/senzing-bootcamp/scripts/brand_tokens.py` — the single shipped source (extracted from `resources/senzing-style-reference.pdf`, which is NOT required at runtime) — never an ad hoc per-generator palette. Consumers MUST fall back gracefully if the token module is absent and MUST keep rendering offline (no web-font/CDN fetch; upholds INV-071). (Source: `apply-senzing-style-guide-to-deliverables`, 2026-07-18.)
- **INV-082** — System Verification (Module 3) MUST verify with synthetic records that are deterministic **by construction** (designed to resolve into a known number of entities), and MUST NOT acquire, load, or visualize the Senzing Truth Set. The Truth Set is used exclusively by the selectable Truth Set visualization module (a separate, standalone module — see INV-087), which acquires and loads it itself. (Supersedes the Truth-Set coupling of INV-038/INV-068; the visualization guarantee itself remains INV-077.) (Source: `module3-synthetic-verification-data`, 2026-07-19; standalone-module location clarified by `split-truthset-visualization-into-standalone-module`, 2026-07-20.)
- **INV-083** — For both the System Verification load and the Truth Set visualization load, the data source code(s) present in the data about to be loaded MUST be registered as the default engine config **before** each load — the synthetic `VERIFY` code before the System Verification load (Module 3), and the Truth Set codes before the Truth Set visualization load (in the standalone Truth Set visualization module) — so no load fails with `SENZ2207` on the first attempt. (Supersedes INV-068, generalizing its register-before-load guarantee to the synthetic and Truth-Set loads.) (Source: `module3-synthetic-verification-data`, 2026-07-19; module locations clarified by `split-truthset-visualization-into-standalone-module`, 2026-07-20.)
- **INV-084** — Module 5's mapping/transformation output (Senzing-ready, load-ready JSONL) MUST be written to `data/senzing-ready/`, and every consumer (Module 6 loaders, graduation, the visualization server) MUST read it from there — never the former `data/transformed/`. (Renames the mapping-output directory; the INV-050 layout tree is updated to match.) (Source: `rename-transformed-to-senzing-ready`, 2026-07-19.)
- **INV-085** — Recap section headers in `docs/bootcamp_recap.md` and the rendered PDF MUST be name-based (`## {Module name} — {timestamp}`, no catalog module number), appended in the bootcamper's experienced (module-completion) order, and every module in `modules_completed` MUST have its own section by graduation; the recap PDF renderer (`generate_recap_pdf.py`) MUST parse name-based headers, still tolerating legacy `## Module N:` headers. (Amends the recap-heading clause of INV-079.) (Source: `recap-sections-name-based-and-complete`, 2026-07-19.)
- **INV-086** — When the Truth Set visualization module (Module 3, Phase 2) runs, the Module 3 close MUST record `truthset_visualization` as its own `modules_completed` entry (a module name token, placed after `system_verification` in experienced order) and append its own name-based `## Truth Set visualization` recap section — so it is a first-class module produced by the flow, not only recovered by graduation's reconcile backfill. `modules_completed` entries are module name tokens, never catalog numbers. As a first-class module it also receives the **full per-module apparatus**: at its Phase 2 start it presents a module-start banner ("MODULE: TRUTH SET VISUALIZATION"), a journey map with it shown `🔄` current, before/after framing, a step overview (INV-028–031/INV-079), and the model/effort nudge (INV-063); at Module 3 close it gets its own end-of-module summary and `✅ Module complete: Truth Set visualization` line (INV-032). It is NOT apparatus-exempt — contrast the explicitly-exempt Bootcamp preparation (INV-075) and Module 0 (INV-078). (The "Phase 2 start" / "Module 3 close records both" recording-location framing is **superseded by INV-087**, which makes Truth Set visualization a standalone module that presents its apparatus at its own module start and records itself at its own close; the first-class-module, full-apparatus, not-apparatus-exempt guarantee stated here otherwise stands.) (Hardens INV-077/INV-085; the full-apparatus clause clarified in place 2026-07-19, no meaning change — a "first-class module" always implied INV-028–032.) (Source: `record-truthset-visualization-completion`, 2026-07-19; full-apparatus clarification: `truthset-visualization-full-apparatus`, 2026-07-19.)
- **INV-087** — Truth Set visualization is a **standalone module** in its own skill directory (`module-03b-truthset-visualization`), separate from System Verification (Module 3): it presents its full per-module apparatus at its **own** module start and runs its **own** module-completion at its **own** close — recording `truthset_visualization` in `modules_completed` and appending its own name-based recap section there (not at the System Verification / Module 3 close), then asking its own transition question; System Verification records only `system_verification` at its own close. (Supersedes the "Phase 2 start" / "Module 3 close records both" recording-location framing of INV-086; INV-086's first-class-module, full-apparatus, not-apparatus-exempt guarantee otherwise stands.) (Source: `split-truthset-visualization-into-standalone-module`, 2026-07-20.)
- **INV-088** — The software-integration question ("will your entity-resolution results need to interface with other software") and the deployment-target question ("where do you plan to deploy the final solution") are asked in the **Bootcamp preparation** module (not in Module 1 / Discover the Business Problem), each as its own pinned-verbatim (INV-056) 👉 question, and their answers (`integration_targets`, `deployment_target`/`cloud_provider`) are persisted in Bootcamp preparation's single consolidated write (INV-058) and read from `config/bootcamp_preferences.yaml` by Module 1's problem statement and by graduation. (Extends the Bootcamp-preparation setup set of INV-075.) (Superseded by INV-097: these two questions are moved back to Module 1 Phase 2 (Step 10a), asked after the scenario and before the artifacts; Bootcamp preparation no longer asks them.) (Source: `relocate-setup-questions-to-bootcamp-preparation`, 2026-07-20.)
- **INV-089** — For every load into the Senzing repository — the System Verification and Truth Set visualization loads already covered by INV-083, **and** the Module 5 Phase 3 test load and the Module 6 production load(s) — the `DATA_SOURCE` code(s) present in the data MUST be registered as the default engine config, idempotently, **before** that load runs, so no load fails with `SENZ2207` on the first attempt. (Generalizes INV-083's register-before-load guarantee to the production load.) (Source: `module6-register-data-sources-before-load`, 2026-07-20.)
- **INV-090** — The Truth Set visualization server MUST be built and run in the Bootcamper's chosen programming language (`programming_language` in `config/bootcamp_preferences.yaml`), modeled on the shipped reference `scripts/senzing_viz_server.py` and the `visualization-api-reference.md` contract; the bundled Python `scripts/senzing_viz_server.py` is run directly ONLY when the chosen language is Python, and for any other language is a reference model that is never run during the bootcamp. (Reverses the earlier "bundled Python server as the running default" decision; strengthens INV-002; the produced-when-selected guarantee remains INV-077, offline rendering INV-091, brand tokens INV-081.) (Source: `visualization-server-in-chosen-language`, 2026-07-21.)
- **INV-091** — The Truth Set visualization server — the language-native one generated in the module, or the bundled Python `scripts/senzing_viz_server.py` when Python is chosen — MUST render with no network access: D3 is vendored at `scripts/vendor/d3.v7.min.js` and inlined into both the live page and the standalone snapshot, with the `d3js.org` CDN referenced only as a fallback when the vendored asset is missing. (Generalizes INV-071 — which named only the bundled Python server — to the chosen-language server; supersedes INV-071.) (Source: `visualization-server-in-chosen-language`, 2026-07-21.)
- **INV-092** — When the Entity Resolution Concepts module (Module 0) runs, it MUST — notwithstanding its module-start apparatus exemption (INV-078) — add `entity_resolution_concepts` to `modules_completed` and append its own name-based recap section (`## Entity Resolution Concepts — {timestamp}`, with the four subsections Information Shared / Questions & Responses / Actions Taken / Journal) to `docs/bootcamp_recap.md` at its close, so it is captured in the recap and reconciled at graduation (INV-085). It remains exempt from the rest of the module-start apparatus (no module-start banner beyond its ENTITY RESOLUTION CONCEPTS banner, no journey map of its own, no before/after framing, no step overview, and no bootcamper-facing end-of-module summary). Bootcamp preparation stays fully exempt and is never added to `modules_completed`. (INV-099 relaxes "fully exempt" to add a bootcamper-facing setup-choices recap at Bootcamp preparation's handoff; prep is still never added to `modules_completed` and still appends no recap section.) (Amends the "no recap section / not in `modules_completed`" clause of INV-072/INV-078.) (Source: `capture-entity-resolution-concepts-in-recap`, 2026-07-21.)
- **INV-093** — The Senzing License Key prompt MUST be presented at most once across the entire bootcamp — at the start of Data collection (Module 4), after the Bootcamper's data volume is known and before any load, and only when that volume exceeds the active license's record limit. SDK setup (Module 2) MUST establish only the built-in evaluation license with no license prompt, and every other module MUST read the persisted result (`license_record_limit` in `config/bootcamp_progress.json`, or `license` in `config/bootcamp_preferences.yaml`) rather than re-asking (INV-006). (Relocates the custom-License-Key gate of INV-036 to Module 4; INV-036's "a license is established" remains satisfied in Module 2 by the built-in evaluation license.) (Source: `single-license-gate-at-data-processing`, 2026-07-22.)
- **INV-094** — Graduation MUST produce a silent, non-blocking revisit/resume bundle before the terminal banner, comprising: (a) a database backup under the reserved top-level `backups/` directory (a `pg_dump` for PostgreSQL — via `docker exec` when the database runs in a container — or a file copy of the SQLite repository), (b) a `RESUME_STATE` manifest snapshotting the resume-critical state (`config/bootcamp_progress.json`, `config/bootcamp_preferences.yaml`, `config/data_sources.yaml`, `config/engine_config.json`, `config/license.json`, and `docs/mapping/`), and (c) a `docs/REVISIT_BOOTCAMP.md` return guide covering how to restore the database, re-initialize the engine, and re-run the pipeline. Every part warns-and-continues on failure (never blocking graduation) and asks before overwriting an existing bundle or performing any destructive action; the bundle lives outside `production/`, so the Step 2 "never copy the eval database into `production/`" rule is preserved. (Source: `graduation-revisit-resume-bundle`, 2026-07-22.)
- **INV-095** — In Bootcamp preparation, when the working directory is not already a git repository, the bootcamp MUST initialize one automatically (`git init`) as a quiet administrative action with **no 👉 question**, recording `git_init: true` (or `git_init: existing` when already a repo, or `git_init: unavailable` when `git` is absent) in the single consolidated preference write (INV-058); it MUST NOT prompt about version control. (Removes the git-init *question* from INV-075's enumerated Bootcamp-preparation questions; the git-init *action* and its persisted `git_init` value are retained.) (Source: `auto-initialize-git-without-prompt`, 2026-07-22.)
- **INV-096** — Every numbered content module's start apparatus MUST include an estimated time-to-complete, placed after the step overview and before the model/effort prompt: honest and range-based, explicitly caveated as varying with workstation power, business-scenario complexity, data volume, and download/install time, and stated as "hard to estimate" rather than fabricated when no meaningful estimate is possible. It is explanatory output — suppressed under the `minimal` verbosity preset and one line under `concise` (INV-011/INV-012) — and does NOT apply to the apparatus-exempt setup modules (Bootcamp preparation INV-075, Module 0 INV-078). (Source: `module-preface-time-estimate`, 2026-07-22.)
- **INV-097** — The software-integration question ("will your entity-resolution results need to interface with other software") and the deployment-target question ("where do you plan to deploy the final solution") are asked in Module 1 (Discover the Business Problem), Phase 2, after the scenario is identified (Step 10) and before the problem-statement artifacts are written (Step 11), each as its own pinned-verbatim (INV-056) 👉 question; their answers (`integration_targets`, `deployment_target`/`cloud_provider`) are persisted to `config/bootcamp_preferences.yaml` there and read by the Module 1 problem statement and by graduation. Bootcamp preparation does NOT ask them. (Supersedes INV-088, reversing the relocation into Bootcamp preparation; the programming-language question remains in Bootcamp preparation per INV-075.) (Source: `relocate-integration-deployment-questions-to-module1`, 2026-07-22.)
- **INV-098** — The module/graduation-start model/effort nudge MUST adapt to the Claude application surface: on Claude Code (CLI) it presents the exact `/model` and `/effort` commands (INV-063); on Desktop, web, or an IDE extension — or when the surface is unknown — it phrases the recommendation by intent (naming the recommended model and reasoning-effort level and directing the bootcamper to their Claude app's model/effort controls), never presenting CLI-only commands as the sole instruction and never hardcoding a UI control label that may drift. The pinned switch question and confirmation gate (INV-063/INV-069) keep their surface-neutral core wording; only the command/instruction detail and the gate's answer hint adapt. (Qualifies INV-063's "exact commands" clause to the CLI surface.) (Source: `surface-aware-model-effort-instructions`, 2026-07-22.)
- **INV-099** — Bootcamp preparation MUST close, before handing off to the first content module, with a concise bootcamper-facing recap of the setup choices it collected (path, selected modules, verbosity, programming language, and git status), read from the consolidated preference write and respecting the active verbosity preset. It otherwise remains apparatus-exempt: it is NOT added to `modules_completed` and appends NO `docs/bootcamp_recap.md` section (INV-092 preserved), so it never appears in the graduation recap PDF. (Relaxes only the "no bootcamper-facing end-of-module summary" part of Bootcamp preparation's exemption in INV-075/INV-092.) (Source: `bootcamp-preparation-end-of-module-recap`, 2026-07-22.)
- **INV-100** — The recap PDF (`docs/bootcamp_recap.pdf`) MUST end with a Certificate of Completion page carrying the bootcamper's name, the bootcamp date, and the modules completed, rendered in **landscape** orientation while every other page stays portrait — in both the fpdf2 renderer and the stdlib fallback (INV-066). The certificate takes its palette and typography from `brand_tokens` (INV-081) and renders offline; the four required recap subsections and `--check` remain satisfied (INV-048). (Source: `landscape-certificate-of-completion`, 2026-07-22.)
- **INV-101** — Any Docker container the bootcamp starts MUST be recorded in `config/bootcamp_progress.json` (a `docker_containers` list, each entry carrying at least the container name), and the python3 `SessionEnd` hook MUST stop those recorded containers when the bootcamp is active and the `docker` CLI is available (`docker stop`, not remove, so they can be restarted), while the python3 `SessionStart` hook surfaces the recorded containers on resume for the guide to restart or regenerate. All Docker interaction is optional and gated on `docker` availability: when `docker` is absent or errors, every step warns-and-continues and never blocks the hook (INV-052/INV-001/INV-002). (Source: `docker-container-lifecycle-teardown-and-resume`, 2026-07-22.)
