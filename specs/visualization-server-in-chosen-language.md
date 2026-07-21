# Truth Set visualization server: bundled Python vs. the bootcamper's chosen language

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The Truth Set visualization server (`scripts/senzing_viz_server.py`) is always Python, regardless
of the bootcamper's chosen programming language. In a Java bootcamp the visualization backend still
ran as a Python script. The bootcamper wants the server generated in their chosen language for
consistency with the rest of the generated code, using the MCP resource
`@plugin:senzing-bootcamp:senzing:senzing://privacy-policy` as an example of the expected output.

## Root cause

By design, not a defect. `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md:112-158`
mandates the bundled Python app as the deterministic, tested path ("Do NOT hand-write a server or
HTML page for the normal path: run the bundled app"); the hand-build fallback
(`:258-269`) is also Python (`http.server`). This is intentional infrastructure:

- The bundled app guarantees the "wow moment" **deterministically every time** (INV-077).
- It renders **offline** with vendored D3 inlined into the live page and the standalone snapshot
  (INV-071; `scripts/vendor/d3.v7.min.js`).
- It applies the shared **Senzing brand tokens** from `scripts/brand_tokens.py` (INV-081).

## Invariant tension (surface it — do not silently override)

Generating the server per-run in an arbitrary language conflicts with the plugin's architecture:

- **INV-077** — the visualization MUST always be produced when selected; the bundled tested app is
  precisely what makes it deterministic. Per-run generation reintroduces the failure modes the
  bundled app exists to eliminate.
- **INV-071** — offline rendering depends on the Python server inlining vendored D3; a
  language-native server would have to replicate offline inlining or it breaks.
- **INV-081** — the palette/typography come from the shipped `brand_tokens.py` (a Python module) a
  non-Python server cannot import.
- **INV-003 / INV-004** — coherent, complete, production-ready; a bespoke per-language server is a
  large new surface to author and test on every language × platform.
- **INV-002 (the bootcamper's argument)** — language-agnostic. But INV-002 means the bootcamp
  *works* regardless of chosen language, not that every shipped plugin tool is *authored* in it.
  The viz server is plugin **infrastructure** — like the hooks, which are ALWAYS Python by INV-052
  — not a bootcamper deliverable. `python3` is already a bootcamp prerequisite (INV-052 / INV-066).

## Proposed change

Maintainer decision required. Recommended reconciliation (do **not** replace the bundled server):

1. **Framing.** In `phase2-visualization.md` (and the Step 9.5 tour) briefly explain — verbosity
   aware (INV-012) — that the visualization server is a **bundled plugin tool** (like the Python
   hooks) that guarantees the deterministic, offline, brand-consistent "wow moment", and is
   separate from the bootcamper's generated deliverables. This resolves the perceived
   inconsistency without weakening any guarantee.
2. **Optional opt-in learning artifact.** Offer (pinned verbatim, INV-056; MCP-sourced, INV-080) to
   also generate a minimal viz-server **stub** in the chosen language as a learning exercise,
   modeled on the referenced MCP resource and `sdk_guide`/`generate_scaffold` — while the bundled
   snapshot remains the guaranteed artifact (INV-077) and the option never blocks the module.

If the maintainer instead wants a language-native server as the **default**, that is a large
architecture change that must first re-establish INV-071/INV-081/INV-077 per language, and is
out of scope for a coherent, low-risk change — call that out rather than attempting it piecemeal.

## Acceptance criteria

- [ ] `phase2-visualization.md` explains (verbosity-aware) that the bundled viz server is plugin infrastructure, not part of the bootcamper's generated deliverable, resolving the perceived language inconsistency.
- [ ] If an opt-in language-native stub is added, the bundled deterministic snapshot remains the guaranteed artifact (INV-077), rendering stays offline (INV-071) and brand-consistent (INV-081), the offer is pinned verbatim (INV-056), and it never blocks the module.
- [ ] No change weakens INV-077/INV-071/INV-081; any Senzing/SDK specifics for a generated stub come from the MCP tools (INV-080), never training data.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md` — framing note (and, if adopted, the opt-in stub offer with pinned wording).
- `plugins/senzing-bootcamp/skills/module-03-system-verification/SKILL.md` — Phase 2 bullet, if the opt-in is added.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Build the Truth Set visualization server in the bootcamper's chosen language, not always Python" (2026-07-20, Module 3)
- Feedback (recurrence): `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Truth Set visualization server should run in the Bootcamper's chosen language, not Python" (2026-07-20 21:50 UTC, Truth Set Visualization module; Rust session). Explicitly asks that the **running** server — not just an optional learning stub — be generated in the chosen language, i.e. the "replace as default" path this spec's maintainer decision below declined. See the Recurrence note.
- Priority: Medium
- Related specs: `vendor-d3-offline-visualization.md` (INV-071), `apply-senzing-style-guide-to-deliverables.md` (INV-081), `customizable-module-selection.md` (INV-077), `cross-platform-hook-execution.md` (INV-052), `mcp-grounding-in-every-skill.md` (INV-080)

## Maintainer decision (2026-07-20)

Chose the **reframe + opt-in stub** path (not replacing the bundled server; "replace as default" was
declined as out of scope for the invariant reasons above). Implemented in the standalone Truth Set
visualization module (`module-03b-truthset-visualization/`, since the split): a Step 9 framing note
plus an optional Step 9.6 offer to generate a language-native stub as a learning exercise, with the
bundled snapshot remaining the guaranteed deliverable. No new invariant — the change honors
INV-071/077/081/080/052.

## Recurrence (2026-07-20)

A second bootcamper (Rust session) independently raised this and is **explicitly asking for the
"replace as default" path** — the live, running visualization server generated and run in the chosen
language, with the optional stub called out as insufficient. That is the option the maintainer
decision above already declined for the INV-071/INV-081/INV-077 tension (offline vendored-D3
inlining, `brand_tokens.py` being a Python module, and the determinism the bundled tested app
guarantees). No new spec is warranted — the topic and both options are fully documented here.
**Maintainer signal:** the request is recurring; revisit only if you want to reopen the declined
default, which remains a large per-language × per-platform architecture change that must first
re-establish INV-071/INV-081/INV-077 in each chosen language.

## Maintainer decision — REVERSED (2026-07-21)

The maintainer **reopened and reversed** the 2026-07-20 decision: the Truth Set visualization server
is now **built and run in the Bootcamper's chosen programming language** as the sole path, modeled on
`scripts/senzing_viz_server.py` and `visualization-api-reference.md`. The bundled Python
`senzing_viz_server.py` is run directly **only** when the chosen language is Python; for any other
language it is a reference model and is never run during the bootcamp. The optional Step 3 stub is
removed (the whole server is now language-native).

The invariant tensions were resolved by carrying the guarantees into the language-native server,
not dropping them:

- **INV-071 → INV-091:** the generated server still renders offline — it inlines the vendored
  `scripts/vendor/d3.v7.min.js` into the live page and the standalone snapshot (D3 is browser JS,
  independent of the backend language). INV-071 is superseded by INV-091.
- **INV-081:** the generated server replicates the shipped Senzing brand token *values*
  (`scripts/brand_tokens.py`) since it cannot import the Python module — covered by INV-081's
  existing "fall back gracefully if the token module is absent" clause; never an ad-hoc palette.
- **INV-077:** the visualization is still always produced when the module is selected — the
  snapshot-first build and the `phase2-close.md` completion gate enforce it; the module iterates the
  generated server until the snapshot exists (no Python safety-net snapshot for non-Python).
- **INV-002:** strengthened — the visualization is now in the chosen language like every other
  deliverable.

Implemented in `module-03b-truthset-visualization/` (rewrote Step 2, removed Step 3, updated the
fallback, `SKILL.md`, `phase2-close.md`, and `visualization-api-reference.md`). Establishes INV-090
(language-native server) and INV-091 (offline rendering generalized; supersedes INV-071).

## Invariants introduced

- `INV-090` — The Truth Set visualization server MUST be built and run in the Bootcamper's chosen programming language, modeled on `scripts/senzing_viz_server.py`; the bundled Python server runs directly only when Python is chosen (recorded in `specs/INVARIANTS.md`).
- `INV-091` — The Truth Set visualization server (language-native, or the Python reference when Python is chosen) MUST render offline with vendored D3 inlined; supersedes INV-071 (recorded in `specs/INVARIANTS.md`).
