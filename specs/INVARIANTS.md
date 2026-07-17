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
- **INV-013** — All shipped modules are performed in order: Module 1 → 2 → 3 → 4 → 5 → 6 → 7. (Advanced Topics — performance, security, monitoring, deployment — ship as production-hardening follow-ups delivered at graduation, not as separate numbered Modules 8-11.)
- **INV-014** — Modules are not skipped unless requested by the Bootcamper.
- **INV-015** — Submitted bootcamp feedback is captured in `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`.

## INV-016 – INV-018: Bootcamp administration outcomes

- **INV-016** — All hooks begin with the word "to" (e.g. "to process your request", "to review what you said").
- **INV-017** — All Markdown files (`.md`) are kept in appropriate places in the `docs/` directory. Exception: the generated `production/` project deliverable carries its own Markdown files (e.g. `README.md`, `MIGRATION_CHECKLIST.md`, `GRADUATION_REPORT.md`).
- **INV-018** — All code files (e.g. `.py`, `.java`, etc.) are kept in appropriate places in the `src/` directory.

## INV-019 – INV-027: Bootcamp preface outcomes

The preface presents these in order.

- **INV-019** — A banner is presented, "ENTITY RESOLUTION CONCEPTS".
- **INV-020** — A description of Entity Resolution is given.
- **INV-021** — The Bootcamper is asked if they want to discuss/explore Entity Resolution before beginning.
- **INV-022** — A banner is presented, "WELCOME TO THE SENZING BOOTCAMP!".
- **INV-023** — An overview of the Bootcamp is given.
- **INV-024** — The Bootcamper is asked what level of detail they would like in the Bootcamp output.
- **INV-025** — The Bootcamper is asked to choose a track.
- **INV-026** — The Bootcamper is asked which programming language they would like to use.
- **INV-027** — The Bootcamper is asked if they have any questions at this point.

## INV-028 – INV-032: Per-module outcomes

These hold at the boundaries of every module.

- **INV-028** — At the beginning of each module, a banner is presented "MODULE n: [title]".
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
- **INV-037** — A database is initialized for use by Senzing.

**Module 3**

- **INV-038** — The Bootcamper **ALWAYS** sees a dynamic web-app visualization of the Truth Set to verify that Senzing works on the Bootcamper's workstation.

**Module 4**

- **INV-039** — Data sources to be loaded into Senzing are identified. This is known as the "raw" data.

**Module 5**

- **INV-040** — The "raw" data is analyzed to see if mapping and transformation is needed. (CORD data does not require mapping nor transformation.)
- **INV-041** — The "raw" data undergoes mapping to determine how to transform data into "Senzing-ready" data.
- **INV-042** — Code is created to transform data according to mapping rules.
- **INV-043** — Using the code, the "raw" data is transformed to Senzing-ready data.

**Module 6**

- **INV-044** — Code is created to load the transformed data.
- **INV-045** — Using the code, the transformed data is loaded into Senzing.

**Module 7**

- **INV-046** — Code is created to query, visualize, and discover the results of Senzing Entity Resolution.

## INV-047 – INV-049: Graduation outcomes

- **INV-047** — A banner is presented, "GRADUATION".
- **INV-048** — A trophy document, `docs/bootcamp_recap.pdf`, is **always** created. It must be very professional looking (iterate to make it look professional) and contains "Information Shared", "Questions & Responses", "Actions Taken", and "Journal".
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
  │   ├── session_log.jsonl              # Session activity log (reserved)
  │   └── visualization_tracker.json     # Visualization run tracking (reserved)
  ├── data/                              # All data artifacts
  │   ├── raw/                           # Source data as received
  │   ├── transformed/                   # Senzing-mapped JSONL output
  │   ├── mapping/                        # Mapping working data (specs, samples, intermediates)
  │   ├── samples/                       # Sample fixtures
  │   ├── temp/                          # Scratch/intermediate working files
  │   └── backups/                       # Data backups (reserved)
  ├── database/                          # SQLite Senzing repository
  ├── src/                               # Source code
  │   ├── transform/                     # Source-to-Senzing mappers
  │   ├── load/                          # Loading & redo processing
  │   ├── query/                         # Query, search & discovery
  │   ├── server/                        # Visualization web server (reserved; the viz server ships with the plugin)
  │   ├── system_verification/           # Pipeline verification (truth set)
  │   ├── scripts/                       # Setup & data-generation utilities
  │   ├── resources/                     # Downloaded Senzing resources
  │   └── utils/                         # Shared helpers
  ├── docs/                              # Documentation
  │   ├── README.md
  │   ├── business_problem.md
  │   ├── data_source_evaluation.md
  │   ├── bootcamp_journal.md
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
- **INV-063** — At every module start and graduation start, the guide MUST surface the recommended session model and reasoning effort with the exact `/model` and `/effort` commands. When the recommendation **changes** from the current stage, it MUST pause with a single 👉 yes/no question offering the switch — its own yielding turn, never combined with another 👉 question; when unchanged, it remains a concise, non-blocking statement. The guide MUST never change the session itself and MUST never block beyond that one optional question. The specific per-stage model/effort values are advisory (maintained in `docs/model-selection.md`) and are not part of the invariant. (Supersedes INV-062.) (Source: `model-effort-change-prompt`, 2026-07-16.)
- **INV-064** — When the Bootcamper accepts a recommended model/effort switch at a module start or graduation start, the guide MUST continue the accepted path in a **single** turn: a one-line statement instructing the `/model`/`/effort` commands, immediately followed by the stage's first step, ending that turn on that step's single 👉 question. It MUST NOT insert a separate confirmation-only gate between the switch and the first step, and MUST NOT defer the first step to a later turn. (Hardens INV-005/INV-054 for the accepted-switch continuation; complements INV-063.) (Source: `model-switch-single-turn-continuation`, 2026-07-16.) (Superseded by INV-069.)
- **INV-065** — A sanitized, non-PII example recap MUST ship inside the plugin — a source `.md` fixture at `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` and its rendered `bootcamp_recap.example.pdf` — the PDF MUST remain regenerable from the `.md` via `generate_recap_pdf.py`, and neither MUST contain real personal data. (Complements INV-048; hardens INV-004 for shipped example assets.) (Source: `example-recap-reference`, 2026-07-17.)
- **INV-066** — Any Python package install the plugin instructs MUST use an explicit interpreter (`python3 -m pip`, never bare `pip`) and be robust to PEP 668 externally-managed environments (prefer a project-local virtualenv), and MUST NOT modify the global/system Python; where a working fallback exists (e.g. the recap PDF's stdlib renderer), an install failure MUST degrade to it rather than block. (Hardens INV-052/INV-048 and the file-placement rules.) (Source: `robust-fpdf2-install`, 2026-07-17.)
- **INV-067** — When bootcamp feedback is appended to `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`, the write MUST be verified to have landed (re-read and confirm the entry is present, re-appending if not) before the bootcamper is told it was saved, and no later bootcamp step (CommonMark normalization, production build, cleanup) may delete or empty that file. (Hardens INV-015; mirrors the recap verify of INV-059.) (Source: `feedback-file-durability`, 2026-07-17.)
- **INV-068** — Module 3 MUST register the TruthSet data source codes (CUSTOMERS, REFERENCE, WATCHLIST for the standard TruthSet, or the codes present in the acquired data for the Step 2a substitute) and commit them as the default engine config **before** the Step 6 data load runs, so the load never fails with SENZ2207 for those codes on the first attempt. (Upholds INV-038.) (Source: `module3-register-truthset-data-sources`, 2026-07-17.)
- **INV-069** — When the Bootcamper accepts a recommended model/effort switch at a module start or graduation start, the guide MUST end that reply turn on a single confirmation gate whose wording is pinned verbatim (INV-056) — "👉 Are you done modifying the model and effort?" — presented after the one-line `/model`/`/effort` run-commands statement, and MUST defer the stage's first step to the turn after the Bootcamper confirms. The gate is asked only once (INV-006); the switch-offer question remains its own prior yielding turn (INV-063). On a declined switch, the first step lands on the reply turn with no gate. (Supersedes INV-064.) (Source: `model-effort-switch-done-confirmation`, 2026-07-17.)
- **INV-070** — Every generated HTML visualization the bootcamp produces MUST be written under the generated project's `docs/visualizations/` directory, never the `docs/` root or another `docs/` subdirectory. (Hardens INV-050.) (Source: `layout-tree-reconciliation`, 2026-07-17.)
- **INV-071** — The bundled visualization (`scripts/senzing_viz_server.py`) MUST render with no network access: D3 is vendored inside the plugin (`scripts/vendor/d3.v7.min.js`) and inlined into both the live page and the standalone snapshot, with the `d3js.org` CDN referenced only as a fallback when the vendored asset is missing. (Hardens INV-004/INV-038; complements INV-052.) (Source: `vendor-d3-offline-visualization`, 2026-07-17.)
