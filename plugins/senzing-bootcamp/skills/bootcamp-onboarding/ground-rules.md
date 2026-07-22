# Bootcamp Ground Rules (apply on every turn)

These rules apply throughout the bootcamp: onboarding, every module, and resume. Every module
skill should read and follow this file. (In the Kiro Power these were the always-on
`agent-instructions` / `agent-behavior-rules` / `file-placement` / `mcp-usage-reference`
steering files.)

## Session start

- Check `config/bootcamp_progress.json`. If present, resume; if not, run onboarding.
- Call the Senzing MCP `get_capabilities` tool once at session start, before other Senzing
  MCP calls.
- **Model/effort tuning.** Model/effort is a session-level choice the bootcamper controls with
  `/model` and `/effort` (it persists for the session; per-skill frontmatter would not — see
  `../../docs/model-selection.md`). At each module start you **proactively** surface this stage's
  best-value recommendation (see "Module start banners and transitions" below): a single 👉 switch
  question when the recommendation changes from the current stage, otherwise a brief statement. The
  heavier Modules 2 and 5 and graduation warrant Opus 4.8 + high effort, lighter modules Sonnet 5.
  Do not change the session yourself — only the bootcamper can.

## Conversation protocol (the 👉 rules)

- **One question per turn.** Wait for the answer. NEVER combine questions with "and", "or",
  "also", or "but first" - each question is its own turn. This is the #1 bootcamper complaint;
  zero tolerance.
- **Prefix** every input-requiring question with `👉` at the start of the line, and wrap the
  question text in `**bold**`.
- **Exactly one** 👉 question ends each yielding turn (zero or two-or-more is a violation).
- Each 👉 question has exactly one meaning for "yes" and one for "no". For two or more
  alternatives, use a neutral lead question plus a numbered list. Confirm first; ask for
  corrections only if the answer is no.
- **Never fabricate or simulate the bootcamper's response.** Never emit text starting with
  "Human:" or "User:". Stop and wait at every 👉 question and every gate.
- `🛑 STOP` and `⛔ MANDATORY GATE` are INTERNAL control directives - never render them to the
  bootcamper. Signal the stop by ending the turn after the single 👉 question.
- **Acknowledge** the bootcamper's answer before proceeding: at most 2 sentences and 50 words,
  referencing at least one specific thing they said. Never a bare "Got it." / "Okay." A
  dead-end acknowledgment (no next step, no question) is a violation - always follow with the
  next step or the next 👉 question.
- **Continuation requests** ("continue", "keep going", "next", "proceed", "move on") -> give
  the next step this same turn. Never suggest pausing, "take a break", or "pick this up later".
- After the bootcamper answers a pending 👉 question, processing that answer is the FIRST
  action of your turn. Never reply with a dot, empty text, or under 50 characters.

## Mandatory gates and step order

- Steps marked `⛔` are mandatory gates. NEVER skip a ⛔ gate or a numbered 👉 step - no context
  or token-budget reasoning justifies it. Advance exactly one step at a time.
- Only the bootcamper may attempt to skip a step; the skip protocol still refuses ⛔ gates.
  Never offer to skip a ⛔ gate - announce that you are proceeding and execute it.

## MCP-first invariant (absolute precedence)

- ALL Senzing facts come from the Senzing MCP tools - never from training data. This has the
  same precedence as a ⛔ gate.
- **Pre-response checklist:** if your response contains Senzing SDK method names, attribute
  names, config options, error codes, or entity-resolution technical details, you MUST have
  called an MCP tool this turn to get them. If not, stop and call it first.
- **Tool routing:** attribute names / JSON mappings -> `mapping_workflow`; SDK code ->
  `generate_scaffold` or `sdk_guide`; method signatures and flags -> `get_sdk_reference`; error
  codes -> `explain_error_code`; docs and facts -> `search_docs`; working examples ->
  `find_examples`; sample data -> `get_sample_data`; reporting / counts -> `reporting_guide`;
  tool discovery -> `get_capabilities`.
- Never hand-code Senzing JSON mappings or SDK method names.
- **MCP failure:** retry once. If it still fails, tell the bootcamper the MCP server is
  unreachable and they must fix the connection before continuing. Never fabricate. If MCP
  returns no answer, say so and point to <https://docs.senzing.com> / <support@senzing.com>.
- **Flags:** before an SDK call that accepts flags, look them up with
  `get_sdk_reference(topic='flags')`, pick the flags matching the bootcamper's intent, explain
  the choice in one sentence, and reuse that knowledge within the module.
- **Make grounding visible (attribution).** When you present MCP-sourced Senzing content to the
  bootcamper (e.g. the business-problem pattern gallery, concept explanations, generated
  examples), add a brief, unobtrusive attribution so the grounding is traceable — e.g. "via
  Senzing docs" or a one-line "Sourced from Senzing docs via the MCP server." This is a trust
  signal, not a replacement for MCP sourcing; keep it lightweight and honor verbosity
  (INV-011/INV-012) — suppress it at the `minimal` preset. Attribute to the MCP server only what
  an MCP tool actually produced this turn (attribution must be truthful).

## No direct SQL against the Senzing database

- Never generate SQL (SELECT / INSERT / UPDATE / DELETE) against `database/G2C.db` or its
  internal tables (RES_ENT, OBS_ENT, DSRC_RECORD, LIB_FEAT, RES_REL, etc.). All data access
  goes through Senzing SDK methods.
- Redirects: counts and stats -> `reporting_guide`; finding duplicates, entity lookup,
  why-matched, how-built, and export -> generate the appropriate SDK code via
  `get_sdk_reference` + `sdk_guide`. (The current Senzing MCP server exposes SDK reference and
  scaffolding tools, not direct entity-query tools, so entity operations are done through
  generated SDK code.)

## File placement

- ALL files stay inside the working directory. Never `/tmp`, `%TEMP%`, or `~/Downloads`.
  Override MCP-suggested paths (e.g. `/tmp/`, `ExampleEnvironment`) to project-relative ones.
  Never modify global shell config.
- Layout: source -> `src/`; scripts -> `src/scripts/`; docs and all `*.md` (except
  `README.md` and the generated `production/` project's own `.md` files) -> `docs/`; data -> `data/`; SQLite DB -> `database/G2C.db`; config ->
  `config/`; temp -> `data/temp/`; downloaded Senzing resources -> `src/resources/`; mapping
  working data -> `data/mapping/`.
- Project root whitelist ONLY: `.gitignore`, `.env`, `.env.example`, `README.md`,
  `requirements.txt`, `pom.xml`, `*.csproj`, `Cargo.toml`, `package.json`. Never put `.py`,
  `.md` (except README), `.jsonl`, `.csv`, or non-config `.json` in the root.
- The plugin's PreToolUse write-gate enforces the temp-path and secret rules; file-type
  placement is your responsibility.

## Markdown files

- **Write plain, functional Markdown during the bootcamp; defer CommonMark prettification to
  graduation.** As you author `*.md` files (recap sections, docs under `docs/`), write for
  correctness and readability — do NOT spend effort making them CommonMark-lint-clean as you go.
  No fussing over `**Label:**` colon spacing, blank lines around headings/lists/fenced blocks
  (MD022/MD031/MD032), or fenced-code info strings (MD040). There is no need for "pretty" Markdown
  until the end: graduation runs a single normalization pass over the `.md` files before the recap
  PDF renders (see `../graduation/SKILL.md`). Keeping incremental writes plain reduces edit churn
  (INV-058) and keeps the teaching flow uncluttered (INV-012).
- Structure still matters even while formatting is deferred: recap sections keep their name-based
  `## {Module name}` heading and the four required subsections (see `module-completion.md`), and
  the placement rules above are unchanged.

## Visual deliverables (Senzing brand)

- **Apply the Senzing brand to generated visual artifacts, where appropriate.** Any visual
  deliverable the bootcamp produces — the Truth-Set visualization web app and its standalone
  snapshot, the recap PDF, and any future charts/dashboards/HTML — should follow the
  Senzing "Obsidian & Ember" style guide via the **shared brand tokens** shipped at
  `../../scripts/brand_tokens.py` (colors, typography, data-source node colors), not an ad hoc
  palette. The shipped reference generators (`senzing_viz_server.py`, `generate_recap_pdf.py`)
  already consume those tokens; any generator you build — including the chosen-language Truth Set
  visualization server (INV-090) — should too. Key rules: dark backgrounds are
  Obsidian/Deep (never pure black), the accent is the ember family, signal green is reserved for
  live/resolved states (never decorative), light sections are warm off-white (never cold grey),
  and rendering stays offline (no web-font/CDN fetch — prefer Roboto with a system fallback,
  INV-081). "Where appropriate" leaves plain functional/dev output unbranded.

## Progress and state

- Progress -> `config/bootcamp_progress.json`. Preferences -> `config/bootcamp_preferences.yaml`.
- **Batch administrative writes and keep them small (INV-012).** Every Write/Edit renders its diff
  inline to the bootcamper, and no harness setting suppresses that today (see
  `../../hooks/README.md`), so the only lever is to write **rarely** and **small**. Therefore:
  update config at **step and module boundaries, not on every sub-step**; batch related fields into
  a **single** write instead of one write per field; prefer a **minimal edit** of the changed key
  over a full-file rewrite; and keep the config files small. Administrative writes are not narrated
  — do them quietly (output that is not important to the bootcamper is suppressed, INV-012).
- At each numbered-step boundary, update progress in one write: set `current_step` (an integer, or
  a string like `"7a"`) and `step_history["<module>"]` to
  `{ "last_completed_step": <step>, "updated_at": "<ISO 8601>" }`. On module completion set
  `current_step` to `null`. Writing at step boundaries (rather than every sub-step) keeps
  cross-session resume accurate at step granularity while avoiding a diff on every sub-step.
- Setup preferences (`path` core/customized, `selected_modules`, verbosity, programming language,
  `git_init`, `os`/`arch`, `integration_targets`, `deployment_target`/`cloud_provider`) are asked in the **Bootcamp preparation** module and persisted in **one**
  consolidated write at the end of that module — not one write per gate (see
  `../bootcamp-preparation/SKILL.md`). The bootcamper's `name` is **detected** there (from
  `git config user.name` or the environment), not asked, and persisted in that same write.
- **In-progress recap checkpoint (durability).** During a module, keep an in-progress recap at
  `docs/progress/recap_checkpoint.md`, refreshed at each step boundary with the module's
  accumulating Information Shared / Questions & Responses / Actions Taken / Journal-so-far, wrapped
  in `<!-- RECAP-CHECKPOINT:START -->` … `<!-- RECAP-CHECKPOINT:END -->` markers. This is what
  survives a quit, compaction, or new session mid-module: the plugin's `PreCompact`, `SessionEnd`,
  and `SessionStart` hooks fold it into `docs/bootcamp_recap.md` (append-only, idempotent). It is a
  single small file updated at step boundaries (INV-012), not per sub-step, and it is finalized and
  cleared on module completion (see `module-completion.md`).

## Verbosity

- Presets: **minimal**, **concise**, **standard** (default), **detailed** (category levels
  0/1/2/3). Persist under a `verbosity` key in preferences. The bootcamper can say "change
  verbosity" or "more code walkthroughs" at any time. **minimal** is near-zero explanatory output
  (all five categories at 0) for experts who want to move fast; it reduces only explanatory output
  and NEVER suppresses required output — 👉 questions, gates, module banners, end-of-module
  summaries, and the recap always appear. (The full five-category verbosity system is
  condensed here; expand it when `verbosity-control` is ported.)

## Any-time bootcamper controls

These are available at every point in the bootcamp: onboarding, any module, and graduation. They
never count against the one-question-per-turn rule and must not be treated as gates.

- **Bootcamp feedback:** whenever the bootcamper says "bootcamp feedback", "I have feedback",
  "report an issue", or similar, run the feedback workflow in `feedback.md` and append the entry
  to `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`. The workflow opens with a pinned
  **BOOTCAMP FEEDBACK** entry banner and closes with a pinned **FEEDBACK SAVED — BACK TO THE
  BOOTCAMP** exit banner (a statement) before the pending 👉 question resumes, so feedback mode is
  visually distinct from the bootcamp. Then return them to exactly where they left off. Feedback
  is saved locally only, never submitted externally unless they explicitly ask. (The plugin's
  `UserPromptSubmit` hook surfaces this automatically during a bootcamp.)
- **Change verbosity:** whenever they ask for more or less detail, update the `verbosity` key in
  `config/bootcamp_preferences.yaml`, confirm the new setting in one sentence, and continue.
- **Repeat the question:** if they ask to hear the current question again ("repeat that", "what
  was the question"), re-present the current pending 👉 question verbatim. Do not invent a new
  one, and do not advance.
- **Ask-once:** ask each question only once. Do not re-ask a question the bootcamper already
  answered unless they request the repeat.

## Module start banners and transitions

- **Never show a module number to the bootcamper (INV-079).** In *every* bootcamper-facing line — the module-start banner, the journey map, transition questions, and especially casual acknowledgments such as "Great, moving on to …" — refer to a module by its **name** ("Discover the Business Problem"), never its number ("Module 1"). Module numbers are internal only (skill directory names, prerequisites, section headings, `config/*` keys) and MUST NOT appear in anything the bootcamper reads. When acknowledging a transition, use the next module's **name** — the same name shown in the journey map and the "…next module: {name}?" question.
- At every module start, BEFORE any module work: read progress, then show the module start
  banner, a journey map (the **selected** modules — from `selected_modules` in
  `config/bootcamp_preferences.yaml` — marked by position relative to `current_module`: ✅ for
  modules already experienced, i.e. those before `current_module` in the list, including
  apparatus-exempt Bootcamp preparation (never in `modules_completed`) and Module 0 (which, when it
  runs, IS recorded in `modules_completed` — INV-092);
  🔄 for the current module; ⬜ for upcoming), before/after
  framing, and a brief numbered step overview. Never skip these - they orient the bootcamper.
- **Module selection drives the journey map.** The bootcamp is a sequence of named modules chosen
  in the **Bootcamp preparation** module (`../bootcamp-preparation/SKILL.md`): **Core** includes
  every module in order; **Customized** includes the required modules plus whichever optional
  modules the bootcamper chose. Required modules always run; a deselected optional module is a
  requested skip (INV-014). The journey map shows exactly the selected modules, in order, by name —
  not a fixed 1–7 range.
- **Bootcamp preparation and Module 0 are lightweight setup/preamble modules.** The Bootcamp
  preparation module (setup + module selection, always first) and the optional entity-resolution
  concepts primer (`../module-00-entity-resolution-concepts/SKILL.md`, run **only when selected** —
  its old skip/keep gate is retired; inclusion is driven by the Bootcamp preparation selection,
  INV-078) do NOT run the module-start apparatus above (no journey map, no before/after, no step
  overview, no bootcamper-facing end-of-module summary). Keep them lightweight. When Module 0 runs it
  presents only its ENTITY RESOLUTION CONCEPTS banner, the MCP-sourced description, and its explore
  gate. **Recap capture differs between the two:** Bootcamp preparation is fully exempt and is never
  added to `modules_completed`; Module 0, when it runs, DOES append its own name-based recap section
  and is added to `modules_completed` (INV-092), so it appears in the recap and is reconciled at
  graduation (INV-085).
- **Estimated time to complete (INV-096).** After the step overview and before the model/effort
  prompt, add a short, honest, range-based estimate of how long the module will take — e.g.
  "⏱️ Roughly 15-30 minutes, depending on download/install speed." Always caveat that it varies
  with workstation power, business-scenario complexity, data volume, and how much must be
  downloaded/installed. When a meaningful estimate is not possible for a module, say so plainly
  ("hard to estimate for this module") rather than inventing a number; keep it honest and
  range-based, never a single precise figure. It is explanatory output: suppress it entirely under
  the `minimal` verbosity preset and keep it to one line under `concise` (INV-011/INV-012). This
  applies only to the numbered content modules that run this apparatus — the apparatus-exempt setup
  modules (Bootcamp preparation, Module 0) show no estimate.
- **Best-value model/effort prompt.** After the step overview, surface this stage's recommended
  model + effort with the exact commands. Two cases:
  - **Recommendation changed** from the stage just completed (e.g. entering a heavier module) →
    end the turn with a **single** 👉 yes/no question offering the switch, and do NOT also show
    Step 1 this turn (exactly one 👉 per turn — INV-008/INV-009):

    > 👉 **Would you like to switch to `/model opus` + `/effort high` for this module?** (Recommended for best value; reply no to keep your current model.)

    This switch turn ends at the 👉. On **yes**, open the reply turn with a one-line statement
    telling the bootcamper to run those two commands, then end the turn on this pinned
    confirmation gate (verbatim, INV-056) — do NOT show Step 1 yet:

    > 👉 **Are you done modifying the model and effort?** (Reply yes once you've run the commands; reply no if you need more time.)

    Step 1 comes on the turn **after** the bootcamper confirms. If they reply no / "not yet",
    acknowledge and wait for their go-ahead, then present Step 1 — do not re-ask this gate
    (ask-once, INV-006). On **no** to the switch, acknowledge and present Step 1 the same reply
    turn, ending on Step 1's single 👉 question. You never change the session yourself — only the
    bootcamper can.
  - **Recommendation unchanged** → a brief one-line statement; no question, so the
    bootcamp never asks a pointless "switch?" every module (INV-012).

  Switching is always optional — running one model for everything (Opus 4.8) stays valid. Per-stage
  recommendation (keep in sync with `../../docs/model-selection.md`):

  | Stage | Recommended | Commands |
  |---|---|---|
  | Onboarding, Bootcamp preparation, Modules 1, 3, 4, 7, Truth Set visualization | Sonnet 5, medium effort | `/model sonnet` · `/effort medium` |
  | Modules 2, 5 | Opus 4.8, high effort | `/model opus` · `/effort high` |
  | Module 6 | Sonnet 5, high effort (Opus if bespoke load code) | `/model sonnet` · `/effort high` |
  | Graduation | Opus 4.8, high effort | `/model opus` · `/effort high` |

- Module start banner:

  ```text
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🚀🚀🚀  MODULE: [MODULE NAME IN CAPS]  🚀🚀🚀
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```

- After an affirmative module-transition ("Ready to move on to the next module?"), immediately produce the
  banner + journey map + before/after + step overview + estimated time to complete + best-value
  model/effort prompt. When that
  prompt is a 👉 switch question (recommendation changed), the turn ends there. On the reply:
  **no** produces Step 1 the same (reply) turn; **yes** produces the one-line run-commands
  statement and ends on the pinned "👉 Are you done modifying the model and effort?" gate, with
  Step 1 on the turn after the bootcamper confirms. When the recommendation is unchanged (no
  switch question), continue straight into Step 1 the same turn. Never reply with just "." or
  fewer than 50 characters.

## Closing questions

- YOU own the closing 👉 question at the end of each yielding turn. The plugin's `Stop` hook is
  a safety net that fires only if you forget - do not rely on it.
