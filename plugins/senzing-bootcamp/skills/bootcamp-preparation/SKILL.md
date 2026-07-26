---
name: bootcamp-preparation
description: 'Bootcamp preparation (first, mandatory module): choose Core vs Customized, select which modules to run, set verbosity and programming language, and initialize version control (git, no prompt). Use right after the onboarding WELCOME preface, before the entity-resolution primer / Module 1.'
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
banner, the overview, and the "any questions" step; this module consolidates the core setup in one
place: the Core-vs-Customized path choice, per-module selection, level of detail (verbosity),
programming language, and version control. (The software-integration and deployment-target
questions are asked in Module 1 Phase 2, not here, per INV-097.)

Bootcamp preparation is a **lightweight setup module**: it presents its own banner and closes with
a bootcamper-facing recap of the setup choices (INV-099), but is otherwise exempt from the
per-module completion apparatus (no journey map, no before/after framing, no
`docs/bootcamp_recap.md` section, and it is not added to `modules_completed`). It cannot show a
journey map yet — it is the module that *produces* the selection that drives the journey map from
the first content module onward. Do the administrative parts quietly (INV-012); ask the setup
questions one 👉 at a time.

Present the banner, then run the steps in order.

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧰🧰🧰  BOOTCAMP PREPARATION  🧰🧰🧰
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## The module list (source of truth for selection and the journey map)

The bootcamp is this ordered sequence. "Required" modules are always included and cannot be
deselected; "Optional" modules are chosen in Customized mode. A module with **Requires** cannot
run unless its prerequisite is also included.

The **State token** column is the exact value to write into `selected_modules` and
`modules_completed`. Copy it; never derive a token from a display name.

| # | Module | Rule | State token | Maps to |
|---|---|---|---|---|
| 1 | Bootcamp preparation | Required | `bootcamp_preparation` | this module |
| 2 | Entity Resolution Concepts | Optional | `entity_resolution_concepts` | `module-00-entity-resolution-concepts` |
| 3 | Discover the Business Problem | Required | `business_problem` | `module-01-business-problem` |
| 4 | SDK setup | Required | `sdk_setup` | `module-02-sdk-setup` |
| 5 | System verification | Optional — Requires "SDK setup" | `system_verification` | `module-03-system-verification` |
| 6 | Truth Set visualization | Optional — Requires "System verification" | `truthset_visualization` | `module-03b-truthset-visualization` |
| 7 | Data collection | Required | `data_collection` | `module-04-data-collection` |
| 8 | Data Quality, Mapping, and Transformation | Required — Requires "Data collection" | `data_quality_mapping` | `module-05-data-quality-mapping` |
| 9 | Data processing | Required — Requires "Data Quality, Mapping, and Transformation" | `data_processing` | `module-06-data-processing` |
| 10 | Query, Visualize and Discover | Required — Requires "Data processing" | `query_visualize_discover` | `module-07-query-visualize-discover` |
| 11 | Graduation | Required — Requires "Query, Visualize and Discover" | `graduation` | `graduation` |

Because **Graduation is required** and it requires "Query, Visualize and Discover", which requires
"Data processing", which requires "Data Quality, Mapping, and Transformation", which requires "Data collection", that
whole downstream chain is always included. So the genuinely deselectable modules are exactly three:
**Entity Resolution Concepts**, **System verification**, and **Truth Set visualization** (and
deselecting System verification forces deselecting Truth Set visualization, which requires it).

## 0. Read the saved preferences first — honor them, do not ask (INV-133)

⛔ **Before Step 1, read `config/bootcamp_preferences.yaml` once.** Every capture question below is
governed by the same rule, and it applies to **all** of them, not just model guidance:

> A setup preference already recorded in `config/bootcamp_preferences.yaml` MUST be honored, its
> capture question MUST NOT be asked, and the saved value MUST NEVER be overwritten with a
> recommended default (INV-133).

This is what lets a returning bootcamper settle a recurring choice permanently — put
`programming_language: Python` and `verbosity: {preset: minimal}` in the file before starting and
those two questions never appear again — without changing the default for anyone else. Asking
someone what they already told you is an INV-006 violation, and it is most galling on a second run.

| Preference | Question it suppresses | Honor when |
|---|---|---|
| `path` | Step 1 | `core`; or `customized` **and** a valid `selected_modules` list is also saved |
| `verbosity` | Step 3 | a recognized preset (`minimal`/`concise`/`standard`/`detailed`) |
| `model_guidance` | Step 3a | `advisory`, `off` or `prompt` |
| `programming_language` | Step 4 | any non-empty value |

- **`path: customized` with no `selected_modules`** is not honorable — the selection would be
  undefined. Ask Step 1 (and Step 2) in that case, and say why in one line.
- **An unrecognized or unreadable value is not honorable.** Fall through to the question rather than
  guessing what was meant.
- **Nothing here is a question.** Read the file quietly (INV-012) and hold each honored value for the
  Step 6 consolidated write, unchanged.
- **`name`, `os`/`arch` and `git_init` are detected, never asked** (INV-134/INV-061/INV-095), so they
  have no question to suppress — but a saved `name` is still honored rather than re-detected.

⛔ **State every honored value once in the Step 7 recap**, marked as coming from the saved file, so
the bootcamper can see what is in force and correct it. A silently-honored preference is
indistinguishable from a question you forgot to ask.

## 1. Choose the bootcamp path

⛔ Skip this step entirely when `path` is honorable per Step 0.

Present this pinned 👉 question, verbatim (INV-056), and end the turn on it:

> 👉 **Which bootcamp would you like? Reply with a number:**
>
> 1. **Core bootcamp** *(recommended)* — every module, in order, from preparation through graduation.
> 2. **Customized bootcamp** — you choose which optional modules to include (required modules are always in).

This is a ⛔ gate: wait for the real choice, do not assume one (INV-007).

- **Core** → **every** module is selected, in order — including all three deselectable ones.
  "Optional" describes what Customized may drop; it never means Core omits it. **Hold**
  `path: core` and this exact ordered list for the consolidated write in Step 6, then skip Step 2:

  ```yaml
  selected_modules:
    - bootcamp_preparation
    - entity_resolution_concepts
    - business_problem
    - sdk_setup
    - system_verification
    - truthset_visualization
    - data_collection
    - data_quality_mapping
    - data_processing
    - query_visualize_discover
    - graduation
  ```

  ⛔ Copy that list verbatim — all eleven tokens. Do **not** rebuild it by translating the module
  table's display names into tokens: that derivation is what silently dropped
  `entity_resolution_concepts` from a Core run, so the primer never appeared and the bootcamper was
  never told a module had been skipped (INV-014 permits only *requested* skips).
- **Customized** → go to Step 2.

## 2. Select modules (Customized only)

Show the full module list above (as statements, so the bootcamper sees everything and what is
always included) — present only the module **names** and their required/optional status; do NOT
render the internal "#" or "Maps to" columns (catalog numbers and skill-directory names are
internal — INV-079/INV-012). Then end the turn on this single pinned 👉 question, verbatim (INV-056):

> 👉 **Which optional modules would you like to include? Reply with the numbers from the list below, comma-separated — reply "none" for just the required modules:**
>
> 1. **Entity Resolution Concepts** — a short primer on how entity resolution works.
> 2. **System verification** — end-to-end checks that Senzing works on your machine.
> 3. **Truth Set visualization** — an interactive web app of the resolved Truth Set (requires System verification).

Apply the prerequisite rules when recording the selection:

- All Required modules are always included. Name them exactly as the module table above spells them
  — Bootcamp preparation, Discover the Business Problem, SDK setup, Data collection, **Data Quality,
  Mapping, and Transformation**, Data processing, **Query, Visualize and Discover**, Graduation —
  never an abbreviation, since these names are what the bootcamper reads here and in every later
  journey map and transition question (INV-079).
- If the bootcamper chooses **Truth Set visualization** (3) without **System verification** (2),
  tell them Truth Set visualization requires System verification, and include System verification
  too (do not silently drop the choice; state what you included and why).
- "none" → include only the Required modules.

**Hold** `path: customized` and the resolved ordered `selected_modules` list for the consolidated
write in Step 6. Keep the list in module order so the journey map and transitions follow it.

## 3. Level of detail (verbosity)

⛔ Skip this step entirely when `verbosity` is honorable per Step 0.

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

## 3a. Model guidance mode

Each module has a recommended model and reasoning effort. Ask once, here, how the bootcamper wants
that surfaced — then honor it for the whole run rather than re-deciding at every module boundary
(INV-006/INV-119).

⛔ Skip this step entirely when `model_guidance` is honorable per Step 0 — a valid saved value is
`advisory`, `off` or `prompt`. Honor it, carry it into the Step 6 write unchanged, and state it in
the Step 7 recap marked as saved — e.g. "Model guidance: stop and ask me each time (from your saved
preferences)."

A bootcamper who always wants the same mode can therefore set it once and never see this question
again: put `model_guidance: prompt` (or `advisory` / `off`) in
`config/bootcamp_preferences.yaml` before starting. Mention that affordance when you tell them they
can change it later — and that the same trick works for `verbosity`, `programming_language` and
`path` (Step 0).

Only when the preference is **absent or unreadable**, present this pinned 👉 question, verbatim
(INV-056), and end the turn on it:

> 👉 **How would you like model guidance handled? Reply with a number:**
>
> 1. **A one-line recommendation at each module** *(recommended)* — shown alongside the time estimate; never interrupts.
> 2. **Don't show it** — no model or effort guidance at all.
> 3. **Stop and ask me each time** — pause with a yes/no question whenever the recommendation changes.

Wait for the answer, then **hold** it for the consolidated write in Step 6 as
`model_guidance: advisory | off | prompt` (option 1 → `advisory`, 2 → `off`, 3 → `prompt`) — do not
write it now (INV-058).

If they decline to choose, take `advisory` and say so. **An absent or unreadable preference is
treated as `advisory`** everywhere it is read, so a session that skipped preparation is never left
without guidance. Tell them they can change it any time ("change model guidance") — and that
setting `model_guidance` in `config/bootcamp_preferences.yaml` makes the choice stick, so this
question is not asked again on a future run.

Whichever path produced it, the value written in Step 6 is the bootcamper's — never overwrite a
saved preference with the recommended default.

Only the bootcamper can change the session's model or effort — the guide never does, in any mode.

## 4. Programming language selection (gate)

⛔ Skip the **programming-language question** when `programming_language` is honorable per Step 0.
Platform detection and name detection below still run either way — they are detections, not
questions.

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

## 5. Initialize version control (automatic, no prompt)

Do this quietly (administrative, not narrated — **no 👉 question**, INV-095). Check whether the
working directory is already a git repository. `git` behaves identically on Linux, macOS, and
Windows; rely on the command's **exit status**, not a shell-specific stderr redirect:

```bash
git rev-parse --is-inside-work-tree
```

- **Already a repo** (command succeeds / prints `true`): **hold** `git_init: existing`.
- **Not a repo** (command fails / non-zero exit): run `git init` automatically as a quiet
  administrative action and **hold** `git_init: true`. Do not ask.
- **`git` not installed** (command not found): skip initialization, **hold**
  `git_init: unavailable`, and continue — never block on version control.

`git init` is an action (run it now when applicable), but the `git_init` value is **held** for the
single consolidated write below — no separate write (INV-058).

## 6. Consolidated preference write (once, quietly)

Persist all setup choices collected in Steps 1-5 to
`config/bootcamp_preferences.yaml` in a **single** write (INV-058) — `path` (`core`/`customized`),
`selected_modules`, `verbosity`, `model_guidance` (`advisory`/`off`/`prompt`, Step 3a), the
programming language, the detected `name` (if any), the detected `os`/`arch`, and the `git_init`
outcome. (The software-integration and deployment-target answers are
NOT collected here — they are asked in Module 1 Phase 2 and persisted there, per INV-097.) (`path`
replaces the old `track` preference; downstream readers — graduation, the recap header — read
`path`.) This is the only setup write of this module; the gates only held their answers, so the
bootcamper sees one diff instead of one per gate (INV-012). Do not narrate this administrative
write.

```yaml
path: core            # or: customized
selected_modules:     # ordered; drives the journey map and transitions
  - bootcamp_preparation
  - entity_resolution_concepts   # always in Core; omitted only if Customized drops it
  - business_problem
  - sdk_setup
  - system_verification          # always in Core; omitted only if Customized drops it
  - truthset_visualization       # always in Core; omitted only if Customized drops it
  - data_collection
  - data_quality_mapping
  - data_processing
  - query_visualize_discover
  - graduation
```

⛔ **Before handing off, verify the list you are about to write** (internal self-check, not
bootcamper-facing). When `path: core`, confirm `selected_modules` holds all eleven tokens from
Step 1 in that order; when `path: customized`, confirm it holds the eight Required tokens plus
exactly the optional ones resolved in Step 2, in module order. If a module is missing, correct it
**now** — after the handoff in Step 7 the next module has already started and the omission is
invisible.

Also record the selection into `config/bootcamp_progress.json` where module-completion and the
journey map read it (a single batched write, INV-012): the ordered `selected_modules` and the
`current_module` pointing at the first content module.

## 7. Recap the setup and hand off to the first selected content module

**First, recap the setup choices to the bootcamper** (INV-099): read them back from the
consolidated write as a concise, lightly-highlighted summary — analogous to a per-module recap, but
Bootcamp preparation stays apparatus-exempt, so this is a bootcamper-facing recap **only**: it is
NOT added to `modules_completed` and NOT written as a `docs/bootcamp_recap.md` section (INV-092).
Respect the active verbosity preset — shorten under `concise`, and keep it to a single line under
`minimal`.

Every line states the value **in force**, whether it came from a question this run or from the
saved file (INV-133). Append ` — from your saved preferences` to any line whose question Step 0
suppressed, so an honored preference is visible rather than looking like a question you skipped:

```text
✅ Bootcamp preparation complete
────────────────────────────────
• Path: Core (all modules) — or Customized (selected modules)
• Modules: {ordered selected module names}
• Detail level: {verbosity}{ — from your saved preferences}
• Model guidance: {one-line recommendation each module | not shown | stop and ask each time}{ — from your saved preferences}
• Language: {programming language}{ — from your saved preferences}
• Version control: {git initialized | existing repo | git unavailable}
→ Next: {first content module name}
```

When Step 0 honored anything, close the recap with one line telling them how to change it: "Edit
`config/bootcamp_preferences.yaml` to change any saved choice, or just tell me."

Then hand off to the first module in `selected_modules` after `bootcamp_preparation`:

- If **Entity Resolution Concepts** is selected → invoke `module-00-entity-resolution-concepts`
  (it runs the primer directly; its skip/keep gate has been retired — inclusion is driven by this
  selection).
- Otherwise → invoke `module-01-business-problem` to begin Module 1 — **Discover the Business Problem** (name it to the bootcamper, never "Module 1").

The selected numbered modules then run in order per `selected_modules`, each ending with the
standard module completion process in `../bootcamp-onboarding/module-completion.md`, and the
journey map (per `ground-rules.md`) shows only the selected modules.
