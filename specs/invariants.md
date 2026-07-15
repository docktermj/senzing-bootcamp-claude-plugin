# Invariants

The following is a list of invariants for the Senzing Bootcamp Claude Plugin (SBCP).
They are aspects of the SBCP that must ALWAYS be true.

For hints, the Senzing Bootcamp for Kiro Power may be consulted.
Use the appropriate Claude Plugin techniques to implement the features captured in the Kiro Power hook files and steering files.

- Repository: <https://github.com/docktermj/senzing-bootcamp-kiro-powers/tree/main>
- Kiro Power: <https://github.com/docktermj/senzing-bootcamp-kiro-powers/tree/main/senzing-bootcamp><>

The SBCP MUST run on the following platforms: Linux, MacOS, and Windows.

The SBCP MUST be programming-language agnostic.

The SBCP MUST be consistent, coherent, and complete.

The SBCP MUST be production-ready.

When the Bootcamper runs the SBCP, these are the expected outcomes:

- Outcomes of the entire Bootcamp:
  - Each question to the Bootcamper is preceeded by "👉"
  - Each question is only asked once unless the Bootcamper asks to have the question repeated.
  - All questions must be answered by the Bootcamper.  The plugin cannot answer questions nor assume answers.
  - Questions should not be ambiguous with respect to a "Yes" or "No" answer.
  - Questions should not be "complex".  The use of "or" is discouraged.
  - At any time, a Bootcamper can submit "Bootcamp feedback:"
  - At any time, a Bootcamper can change the verbosity of the bootcamp.
  - All output must be relative to the Bootcamper's point-of-view.
    - Output that is not important to the Bootcamper is suppressed.
  - All modules performed in order.  i.e. Module 1 -> Module 2 -> Module 3 -> Module 4 -> Module 5 -> Module 6 -> Module 7 - Module 8 -> Module 9 -> Module 10 -> Module 11
  - Modules are not skipped unless requested by the Bootcamper.
  - At any time a Bootcamper can submit bootcamp feedback which is captured in:
    - docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md

- Outcomes of the Bootcamp administration:
  - All hooks begin with the word "to"  (e.g. "to process your request", "to review what you said")
  - All Markdown files (`.md`) are kept in appropriate places in the docs/ directory
  - All code files (e.g. `.py`, `.java`, etc) are kept in appropriate places in the src/ directory

- Outcomes of the Bootcamp preface:
  1. A banner is presented, "ENTITY RESOLUTION CONCEPTS".
  2. A description of Entity Resolution is given.
  3. The Bootcamper is asked if they want to discuss/explore Entity Resolution before beginning.
  4. A banner is presented, "WELCOME TO THE SENZING BOOTCAMP!"
  5. An overview of the Bootcamp is given.
  6. The Bootcamper is asked what level of detail they would like in the Bootcamp output.
  7. The Bootcamper is asked to choose a track.
  8. The Bootcamper is asked which programming language they would like to use.
  9. The Bootcamper is asked if they have any questions at this point.

- Outcomes of each module of the Bootcamp:
  - At the beginning of each module, a banner is presented "MODULE n: [title]".
  - At the beginning of each module, show modules completed, the current module, and upcoming modules.
  - At the beginning of each module, explain what is true before the module and what will be true after completing the module.
  - At the beginning of each module, enumerate the steps that will be taken in the module.
  - At the end of each module, give the Bootcamper a list of what was accomplished, what files were produced, why it matters, and what's next.

- Outcomes in Module 1:
  - The Bootcamper is asked if they want to see a gallery of common business problems that Entity Resolution solves.
  - The Bootcamper describes the business issue requiring Entity Resolution.

- Outcomes of Module 2:
  - Senzing SDK is installed.
  - Senzing license:
    - Use the built-in evaluation license.
    - Identify an existing own Senzing license.
    - A Bootcamper can request a temporary Senzing license via the Senzing MCP server
  - A database is initialized for use by Senzing

- Outcomes of Module 3:
  - The Bootcamper ALWAYS sees a dynamic web app visualization of the Truth Set
    to verify that Senzing works on the Bootcampers workstation.

- Outcomes of Module 4:
  - Data sources to be loaded into Senzing are identified.
  - This is known as the "raw" data.

- Outcomes of Module 5:
  - The "raw" data is analyzed to see if mapping and transformation is needed.
    - CORD data does not require mapping nor transformation.
  - The "raw" data undergoes mapping to determine how to transform data into "Senzing-ready" data.
  - Code is created to transform data according to mapping rules.
  - Using the code, the "raw" data is transformed to senzing-ready data.

- Outcomes of Module 6:
  - Code is created to load the transformed data.
  - Using the code, the transformed data is loaded into Senzing.

- Outcomes of Module 7:
  - Code is created to query, visualize, and discover the results of Senzing Entity Resolution.

- Outcomes of graduation:
  - A banner is presented, "GRADUATION".
  - A trophy document, `docs/bootcamp_recap.pdf` is always created.
    - It must be very professional looking. Iterate to make it look professional.
    - It contains "Information Shared", "Questions & Responses", "Action Taken", and "Journal".
  - The `production/` directory is populated.

Additionally,

- Project layout

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
 │       └── SENZING_BOOTCAMP_POWER_FEEDBACK.md
 ├── licenses/
 │   └── g2.lic                         # Senzing license
 ├── logs/                              # Run logs & result summaries
 ├── backups/                           # Project backups/archives
 ├── monitoring/                        # Monitoring assets
 ├── tests/                             # Test suite
 └── production/                        # Production hardening (Modules 8-11)
 ```
