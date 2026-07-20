---
name: bootcamp-preparation
description: 'Bootcamp preparation (first, mandatory module): choose Core vs Customized, select which modules to run, and set verbosity, programming language, and version control. Use right after the onboarding WELCOME preface, before the entity-resolution primer / Module 1.'
---

# Bootcamp Preparation (first module, mandatory)

> **MCP grounding (mandatory — applies to this entire skill).** Every Senzing fact you present —
> SDK method and attribute names, config options, error codes, and entity-resolution specifics —
> MUST come from the Senzing MCP tools, never from training data, memory, or speculation.
> **Pre-response checklist:** if a reply contains any Senzing specific, you MUST have called an MCP
> tool this turn to obtain it; if not, stop and call it first. This has the same precedence as a ⛔
> gate. The full rule and tool routing are the "MCP-first invariant" in
> `../bootcamp-onboarding/ground-rules.md`.

Follow `../bootcamp-onboarding/ground-rules.md` throughout (👉 one-question-at-a-time,
MCP-first, file placement, checkpointing). This is the **first, mandatory module**. The
onboarding preface (`../bootcamp-onboarding/onboarding-flow.md`) hands off here after the WELCOME
banner, the overview, and the "any questions" step; this module consolidates **all setup** in one
place: the Core-vs-Customized path choice, per-module selection, level of detail (verbosity),
programming language, and version control.

Bootcamp preparation is a **lightweight setup module**: it presents its own banner but is exempt
from the per-module completion apparatus (no journey map, no before/after framing, no
`docs/bootcamp_recap.md` section, and it is not added to `modules_completed`). It cannot show a
journey map yet — it is the module that *produces* the selection that drives the journey map from
the first content module onward. Do the administrative parts quietly (INV-012); ask the setup
questions one 👉 at a time.

Present the banner, then run the steps in order.

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧰🧰🧰  BOOTCAMP PREPARATION  🧰🧰🧰
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## The module list (source of truth for selection and the journey map)

The bootcamp is this ordered sequence. "Required" modules are always included and cannot be
deselected; "Optional" modules are chosen in Customized mode. A module with **Requires** cannot
run unless its prerequisite is also included.

| # | Module | Rule | Maps to |
|---|---|---|---|
| 1 | Bootcamp preparation | Required | this module |
| 2 | Entity Resolution Concepts | Optional | `module-00-entity-resolution-concepts` |
| 3 | Discover the Business Problem | Required | `module-01-business-problem` |
| 4 | SDK setup | Required | `module-02-sdk-setup` |
| 5 | System verification | Optional — Requires "SDK setup" | `module-03-system-verification` |
| 6 | Truth Set visualization | Optional — Requires "System verification" | `module-03b-truthset-visualization` |
| 7 | Data collection | Required | `module-04-data-collection` |
| 8 | Data quality & mapping | Required — Requires "Data collection" | `module-05-data-quality-mapping` |
| 9 | Data processing | Required — Requires "Data quality & mapping" | `module-06-data-processing` |
| 10 | Query, Visualize and Discover | Required — Requires "Data processing" | `module-07-query-visualize-discover` |
| 11 | Graduation | Required — Requires "Query, Visualize and Discover" | `graduation` |

Because **Graduation is required** and it requires "Query, Visualize and Discover", which requires
"Data processing", which requires "Data quality & mapping", which requires "Data collection", that
whole downstream chain is always included. So the genuinely deselectable modules are exactly three:
**Entity Resolution Concepts**, **System verification**, and **Truth Set visualization** (and
deselecting System verification forces deselecting Truth Set visualization, which requires it).

## 1. Choose the bootcamp path

Present this pinned 👉 question, verbatim (INV-056), and end the turn on it:

> 👉 **Which bootcamp would you like? Reply with a number:**
>
> 1. **Core bootcamp** *(recommended)* — every module, in order, from preparation through graduation.
> 2. **Customized bootcamp** — you choose which optional modules to include (required modules are always in).

This is a ⛔ gate: wait for the real choice, do not assume one (INV-007).

- **Core** → all modules are selected, in order. **Hold** `path: core` and the full ordered
  `selected_modules` list for the consolidated write in Step 5; skip Step 2.
- **Customized** → go to Step 2.

## 2. Select modules (Customized only)

Show the full module list above (as statements, so the bootcamper sees everything and what is
always included), then end the turn on this single pinned 👉 question, verbatim (INV-056):

> 👉 **Which optional modules would you like to include? Reply with the numbers, comma-separated, or "none":**
>
> 1. **Entity Resolution Concepts** — a short primer on how entity resolution works.
> 2. **System verification** — end-to-end checks that Senzing works on your machine.
> 3. **Truth Set visualization** — an interactive web app of the resolved Truth Set (requires System verification).

Apply the prerequisite rules when recording the selection:

- All Required modules (Bootcamp preparation, Business problem, SDK setup, Data collection, Data
  quality & mapping, Data processing, Query/Visualize/Discover, Graduation) are always included.
- If the bootcamper chooses **Truth Set visualization** (3) without **System verification** (2),
  tell them Truth Set visualization requires System verification, and include System verification
  too (do not silently drop the choice; state what you included and why).
- "none" → include only the Required modules.

**Hold** `path: customized` and the resolved ordered `selected_modules` list for the consolidated
write in Step 5. Keep the list in module order so the journey map and transitions follow it.

## 3. Level of detail (verbosity)

> 👉 **How much detail would you like in the bootcamp output? Reply with a number:**
>
> 1. **minimal** — near-zero output: only questions, results, and required banners/summaries; no explanations, code walkthroughs, or step recaps. Best for experts who want to move fast.
> 2. **concise** — minimal explanations, brief recaps. Best for experienced developers.
> 3. **standard** *(recommended)* — balanced what-and-why, block-level code summaries.
> 4. **detailed** — full explanations, line-by-line walkthroughs, SDK internals.

Wait for the answer, then **hold** the chosen verbosity for the consolidated write in Step 5 — do
not write it now (INV-058: one setup write, not one per gate). Each preset maps its five
`categories` to a single level — `minimal` = 0, `concise` = 1, `standard` = 2, `detailed` = 3.
When persisted, the `verbosity` key will look like (here, `standard`):

```yaml
verbosity:
  preset: standard
  categories:
    explanations: 2
    code_walkthroughs: 2
    step_recaps: 2
    technical_details: 2
    code_execution_framing: 2
```

For `minimal`, every category is `0`. `minimal` reduces only *explanatory* output; it NEVER
suppresses required output — every 👉 question (INV-005), gate, module banner (INV-079),
end-of-module summary (INV-032), and the recap (INV-048) still appear.

Tell them they can change it any time ("change verbosity", or "more code walkthroughs"). This is
NOT a gate; if they skip, apply `standard` and tell them so.

## 4. Programming language selection (gate)

- **Detect the platform first (do not ask).** Determine the OS and architecture from the
  environment/system context (else run `uname`/`systeminfo`), and state it in one line
  ("Detected macOS on Apple Silicon"). Hold the detected `os`/`arch` for the Step 5 consolidated
  write so Module 2 can reuse it instead of re-asking (INV-061).
- Call `get_capabilities` or `sdk_guide` on the Senzing MCP server for the supported programming
  languages on that platform.
- Always say "**programming language**", never the bare word "language" (avoids confusion with
  spoken languages).
- Present the MCP-returned list, and **annotate each option with its install path for the detected
  platform** so the trade-off is visible at the decision point — e.g. on macOS Apple Silicon:
  "Python — runs via Docker (the SDK is Linux-only); Java / C# — native." Use the Module 2 routing
  rules (`../module-02-sdk-setup/SKILL.md`, "Determine Platform") as the source of the per-platform
  paths. If the MCP server flags a language as discouraged/unsupported on the platform, relay that
  and suggest alternatives.

  👉 **Which programming language would you like to use for the bootcamp?**

- This is a ⛔ gate: wait for the bootcamper's real choice. Do NOT assume or say "I'll go with X."
- **Hold** the chosen programming language for the Step 5 consolidated write (do not write it now).

## 5. Initialize version control (optional)

Do the detection quietly (administrative, not narrated). Check whether the working directory is
already a git repository. `git` behaves identically on Linux, macOS, and Windows; rely on the
command's **exit status**, not a shell-specific stderr redirect:

```bash
git rev-parse --is-inside-work-tree
```

- **Already a repo** (command succeeds / prints `true`): skip the question. **Hold**
  `git_init: existing`; proceed to the consolidated write.
- **Not a repo** (command fails / non-zero exit): ask the pinned 👉 question, verbatim (INV-056):

  👉 **If you don't know what "git" is, just skip this. It's optional: would you like me to initialize a git repository for version control?**

  *(Internal: end the turn on this single 👉 question and wait — INV-005.)* On **yes**, run
  `git init` as a quiet administrative action and **hold** `git_init: true`; on **no**, skip and
  **hold** `git_init: false`.

`git init` is an action (run it now), but the `git_init` value is **held** for the single
consolidated write below — no separate write (INV-058).

## 6. Consolidated preference write (once, quietly)

Persist all setup choices collected in Steps 1-5 to `config/bootcamp_preferences.yaml` in a
**single** write (INV-058) — `path` (`core`/`customized`), `selected_modules`, `verbosity`, the
programming language, `name` if it was captured, the detected `os`/`arch`, and the `git_init`
outcome. (`path` replaces the old `track` preference; downstream readers — graduation, the recap
header — read `path`.) This is the only setup write of this module; the gates only held their answers, so the
bootcamper sees one diff instead of one per gate (INV-012). Do not narrate this administrative
write.

```yaml
path: core            # or: customized
selected_modules:     # ordered; drives the journey map and transitions
  - bootcamp_preparation
  - entity_resolution_concepts   # optional — present only if selected
  - business_problem
  - sdk_setup
  - system_verification          # optional
  - truthset_visualization       # optional
  - data_collection
  - data_quality_mapping
  - data_processing
  - query_visualize_discover
  - graduation
```

Also record the selection into `config/bootcamp_progress.json` where module-completion and the
journey map read it (a single batched write, INV-012): the ordered `selected_modules` and the
`current_module` pointing at the first content module.

## 7. Hand off to the first selected content module

Hand off to the first module in `selected_modules` after `bootcamp_preparation`:

- If **Entity Resolution Concepts** is selected → invoke `module-00-entity-resolution-concepts`
  (it runs the primer directly; its skip/keep gate has been retired — inclusion is driven by this
  selection).
- Otherwise → invoke `module-01-business-problem` to begin Module 1.

The selected numbered modules then run in order per `selected_modules`, each ending with the
standard module completion process in `../bootcamp-onboarding/module-completion.md`, and the
journey map (per `ground-rules.md`) shows only the selected modules.
