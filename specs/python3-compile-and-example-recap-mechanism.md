# Use python3 for the verify-compile command; fix the example recap's visualization mechanism

Maintain the invariant conditions in @INVARIANTS.md and fix the following issues:

## Problem

Two independent shipped-artifact defects found in the final review:

1. **Bare `python` (INV-001).** Module 3's Step-5 build-command table invokes
   `python -m py_compile src/system_verification/verify_pipeline.py`. Every other interpreter
   invocation in the plugin (viz server, recap PDF, screenshot helper, all hooks) uses `python3`,
   and `hooks/README.md` states the command name must be `python3`. On python3-only hosts (modern
   Debian/Ubuntu — the plugin's own stated prerequisite) `python` is absent, so a Python-language
   Bootcamper gets a **false compile failure** ("python: command not found"). Only the Python row is
   affected (javac/dotnet/cargo/tsc have no dual-name split).

2. **Fabricated viz script in the example recap (INV-065/071/077).** The shipped example recap
   credits a nonexistent `src/scripts/senzing_viz_fallback.py` as the visualization mechanism and as
   "What was produced." No such script ships; Phase 2 (`phase2-visualization.md`) mandates the
   bundled `${CLAUDE_PLUGIN_ROOT}/scripts/senzing_viz_server.py` and explicitly says "Do NOT
   hand-write a server or HTML page for the normal path." The example therefore depicts a hand-rolled
   fallback as the normal path, misrepresenting the flow in a reference artifact bootcampers see.

## Root cause

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md:204` — `python -m py_compile`.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md:146,157` — references `src/scripts/senzing_viz_fallback.py`.

## Proposed change

1. Change the Python build command to `python3 -m py_compile …`.
2. Reword the example recap's Actions-Taken line to attribute the visualization to the bundled
   Senzing viz server (matching the real flow), and remove `src/scripts/senzing_viz_fallback.py`
   from both the narrative and the Journal's "What was produced" list. Re-render
   `bootcamp_recap.example.pdf` from the edited `.md` (INV-065 regenerability).

## Acceptance criteria

- [x] The Module 3 Python compile command uses `python3`, matching every other interpreter invocation and `hooks/README.md`.
- [x] The example recap no longer names a nonexistent `senzing_viz_fallback.py`; it describes the bundled viz server, consistent with INV-071/077.
- [x] `bootcamp_recap.example.pdf` re-rendered from the edited `.md`; `generate_recap_pdf.py --check` passes; no PII introduced.
- [x] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md`
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` (+ re-rendered `.pdf`)

## Source

- Audit (fourth deep-dive, final review), 2026-07-19 — cross-platform + shipped-example coherence; maintainer chose "fix all verified findings".
- Priority: Medium.
- Related specs: `specs/example-recap-reference.md`, `specs/refresh-example-recap.md`.
