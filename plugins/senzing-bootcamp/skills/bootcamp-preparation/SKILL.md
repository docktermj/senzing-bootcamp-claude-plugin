---
name: bootcamp-preparation
description: 'Bootcamp preparation (first, mandatory module): choose Core vs Customized, select which modules to run, and set verbosity, programming language, version control, software integration, and deployment target. Use right after the onboarding WELCOME preface, before the entity-resolution primer / Module 1.'
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
programming language, version control, and the software-integration and deployment-target questions
(relocated here from Module 1, INV-088).

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
  `selected_modules` list for the consolidated write in Step 6; skip Step 2.
- **Customized** → go to Step 2.

## 2. Select modules (Customized only)

Show the full module list above (as statements, so the bootcamper sees everything and what is
always included) — present only the module **names** and their required/optional status; do NOT
render the internal "#" or "Maps to" columns (catalog numbers and skill-directory names are
internal — INV-079/INV-012). Then end the turn on this single pinned 👉 question, verbatim (INV-056):

> 👉 **Which optional modules would you like to include? Reply with the numbers from the list below, comma-separated (or reply none):**
>
> 1. **Entity Resolution Concepts** — a short primer on how entity resolution works.
> 2. **System verification** — end-to-end checks that Senzing works on your machine.
> 3. **Truth Set visualization** — an interactive web app of the resolved Truth Set (requires System verification).

Apply the prerequisite rules when recording the selection:

- All Required modules (Bootcamp preparation, Discover the Business Problem, SDK setup, Data collection, Data
  quality & mapping, Data processing, Query/Visualize/Discover, Graduation) are always included.
- If the bootcamper chooses **Truth Set visualization** (3) without **System verification** (2),
  tell them Truth Set visualization requires System verification, and include System verification
  too (do not silently drop the choice; state what you included and why).
- "none" → include only the Required modules.

**Hold** `path: customized` and the resolved ordered `selected_modules` list for the consolidated
write in Step 6. Keep the list in module order so the journey map and transitions follow it.

## 3. Level of detail (verbosity)

> 👉 **How much detail would you like in the bootcamp output? Reply with a number:**
>
> 1. **minimal** — near-zero output: only questions, results, and required banners/summaries; no explanations, code walkthroughs, or step recaps. Best for experts who want to move fast.
> 2. **concise** — minimal explanations, brief recaps. Best for experienced developers.
> 3. **standard** *(recommended)* — balanced what-and-why, block-level code summaries.
> 4. **detailed** — full explanations, line-by-line walkthroughs, SDK internals.

Wait for the answer, then **hold** the chosen verbosity for the consolidated write in Step 6 — do
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
not a ⛔ gate, but it is still a 👉 question the bootcamper answers (INV-007): wait for their reply.
If they explicitly decline to choose (e.g. "no preference", "you pick", "skip"), treat that decline
as choosing the recommended `standard` and say so — never assume a level before they have replied.

## 4. Programming language selection (gate)

- **Detect the platform first (do not ask).** Determine the OS and architecture from the
  environment/system context (else run `uname`/`systeminfo`), and state it in one line
  ("Detected macOS on Apple Silicon"). Hold the detected `os`/`arch` for the Step 6 consolidated
  write so Module 2 can reuse it instead of re-asking (INV-061). **Only if detection is genuinely
  unavailable or ambiguous**, ask this pinned fallback question, verbatim (INV-056), and hold the
  answer:

  👉 **Which operating system and processor architecture are you using? Reply with a number:**

  1. Linux (x86-64)
  2. Linux (ARM64)
  3. macOS (Apple Silicon)
  4. macOS (Intel)
  5. Windows (x86-64)

  *(Internal: end the turn on this single 👉 question and wait — INV-005.)*

- **Detect the bootcamper's name silently (do not ask).** Best-effort: read a display name from
  `git config user.name` (else the environment). If found, hold it as `name` for the Step 6
  consolidated write so the recap and graduation report can address the bootcamper by name; if
  none is available, leave `name` unset. Never ask for it and never block on it.
- Call `get_capabilities` or `sdk_guide` on the Senzing MCP server for the supported programming
  languages on that platform.
- Always say "**programming language**", never the bare word "language" (avoids confusion with
  spoken languages).
- Present the MCP-returned options as a **numbered list**, annotating each option with its install path for the detected
  platform so the trade-off is visible at the decision point — e.g. on macOS Apple Silicon:
  "Python — runs via Docker (the SDK is Linux-only); Java / C# — native." Use the Module 2 routing
  rules (`../module-02-sdk-setup/SKILL.md`, "Determine Platform") as the source of the per-platform
  paths. If the MCP server flags a language as discouraged/unsupported on the platform, relay that
  and suggest alternatives.

  👉 **Which programming language would you like to use for the bootcamp? Reply with a number:**

- This is a ⛔ gate whose wording is pinned — present the 👉 question above verbatim (INV-056); wait for the bootcamper's real choice. Do NOT assume or say "I'll go with X."
- **Hold** the chosen programming language for the Step 6 consolidated write (do not write it now).

## 4a. Software integration (optional)

Optional forward-looking context (not a ⛔ gate) that helps tailor the problem statement (Module 1)
and the graduation production project. Ask this as a single pinned 👉 question, verbatim (INV-056),
and end the turn on it (INV-005):

👉 **Will your entity-resolution results need to interface with other software (CRM, search engine, data warehouse, API gateway, downstream app)?**

*(Internal: end the turn and wait.)* On **yes**, ask one follow-up on the next turn — "👉 **Which
systems do you expect to integrate with?**" — and **hold** the named systems (e.g. Elasticsearch,
Salesforce) as `integration_targets` for the consolidated write. On **no**, hold `integration_targets: []`.
Module 1's problem statement and graduation read `integration_targets` from
`config/bootcamp_preferences.yaml` (INV-088).

## 4b. Deployment target (optional)

Deployment is addressed for every bootcamper in the graduation production project and migration
checklist, so capturing a target now is optional — it just helps tailor that output. Ask this as a
single, separate pinned 👉 question, verbatim (INV-056), neutral lead + numbered list (INV-051):

👉 **Where do you plan to deploy the final solution? Reply with a number:**

1. A cloud hyperscaler (AWS/Azure/GCP).
2. A container platform (Kubernetes/Docker Swarm).
3. Local / on-premises.
4. Not sure yet.

*(Internal: end the turn and wait.)* Reassure: "We'll develop everything locally first; deployment is
addressed in the graduation production project and migration checklist." **Hold** `deployment_target`
(`aws`/`azure`/`gcp` — also hold `cloud_provider`; `kubernetes`/`docker_swarm`; `local`/
`on_premises`; or `undecided` for option 4) for the consolidated write. Graduation and Module 1
Phase 2 read `deployment_target` from `config/bootcamp_preferences.yaml` (INV-088).

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

Persist all setup choices collected in Steps 1-5 (including 4a/4b) to
`config/bootcamp_preferences.yaml` in a **single** write (INV-058) — `path` (`core`/`customized`),
`selected_modules`, `verbosity`, the programming language, the detected `name` (if any), the detected
`os`/`arch`, the `git_init` outcome, and the relocated setup answers `integration_targets` (list;
`[]` if none) and `deployment_target` (plus `cloud_provider` when a hyperscaler was chosen). (`path`
replaces the old `track` preference; downstream readers — graduation, the recap header — read
`path`.) This is the only setup write of this module; the gates only held their answers, so the
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
- Otherwise → invoke `module-01-business-problem` to begin Module 1 — **Discover the Business Problem** (name it to the bootcamper, never "Module 1").

The selected numbered modules then run in order per `selected_modules`, each ending with the
standard module completion process in `../bootcamp-onboarding/module-completion.md`, and the
journey map (per `ground-rules.md`) shows only the selected modules.
