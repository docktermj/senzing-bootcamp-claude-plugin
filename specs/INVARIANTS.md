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
- **INV-013** — All modules are performed in order: Module 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11.
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
- **INV-048** — A trophy document, `docs/bootcamp_recap.pdf`, is **always** created. It must be very professional looking (iterate to make it look professional) and contains "Information Shared", "Questions & Responses", "Action Taken", and "Journal".
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
  │   ├── session_log.jsonl              # Session activity log
  │   └── visualization_tracker.json     # Visualization run tracking
  ├── data/                              # All data artifacts
  │   ├── raw/                           # Source data as received
  │   ├── transformed/                   # Senzing-mapped JSONL output
  │   ├── samples/                       # Sample fixtures
  │   ├── temp/                          # Scratch/intermediate working files
  │   └── backups/                       # Data backups
  ├── database/                          # SQLite Senzing repository
  ├── src/                               # Source code
  │   ├── transform/                     # Source-to-Senzing mappers
  │   ├── load/                          # Loading & redo processing
  │   ├── query/                         # Query, search & discovery
  │   ├── server/                        # Visualization web server
  │   ├── system_verification/           # Pipeline verification (truth set)
  │   ├── scripts/                       # Setup & data-generation utilities
  │   └── utils/                         # Shared helpers
  ├── docs/                              # Documentation
  │   ├── README.md
  │   ├── business_problem.md
  │   ├── data_source_evaluation.md
  │   ├── bootcamp_journal.md
  │   ├── bootcamp_recap.md
  │   ├── bootcamp_recap.pdf
  │   ├── completion_summary.md
  │   ├── stakeholder_summary_module1.md
  │   ├── mapping/                       # Per-source mapping docs
  │   ├── reference/
  │   ├── progress/
  │   ├── visualizations/                # Generated HTML visualizations
  │   └── feedback/
  │       └── SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md
  ├── licenses/
  │   └── g2.lic                         # Senzing license
  ├── logs/                              # Run logs & result summaries
  ├── backups/                           # Project backups/archives
  ├── monitoring/                        # Monitoring assets
  ├── tests/                             # Test suite
  └── production/                        # Production hardening (Modules 8-11)
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
