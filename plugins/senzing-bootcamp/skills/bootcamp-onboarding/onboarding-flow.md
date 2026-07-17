# Onboarding Flow (fresh bootcamp)

Follow these steps in order. Follow `ground-rules.md` throughout. Do not narrate administrative
work in detail: do the setup quietly, then present the WELCOME banner.

The bootcamper-facing preface follows this order:

1. **Welcome + overview** (WELCOME banner + overview) — step 3.
2. **Level of detail** (verbosity) — step 4.
3. **Track** — step 5.
4. **Programming language** — step 6.
5. **Any questions** — step 7.

Steps 0-2 are administrative and mostly silent; they run before the WELCOME banner.

Entity resolution concepts are **not** part of the preface. They are an optional **Module 0**
(`../module-00-entity-resolution-concepts/SKILL.md`) presented after the preface and before
Module 1; step 8 hands off to it.

## 0. Setup preamble

Tell the bootcamper, in your own words:

"I'm going to do some quick administrative setup: creating your project directory and checking
your environment. Then I'll introduce entity resolution, and you'll see a big **WELCOME TO THE
SENZING BOOTCAMP** banner: that's when the guided bootcamp officially starts and I'll begin
asking you questions."

Optionally show the plugin version (from `.claude-plugin/plugin.json`): `Senzing Bootcamp vX.Y.Z`.

## 0b. MCP health check (required)

Confirm the Senzing MCP server is reachable before starting. It is required: it generates SDK
code in the chosen language, looks up Senzing facts, and provides working examples.

- **Probe:** make a lightweight call such as `search_docs(query="health check")` (about a
  10-second timeout).
- **Success** (any response, even empty results): proceed silently.
- **Failure** (timeout or error): display a blocking message and STOP. Do not proceed until the
  bootcamper fixes the connection and says "retry":

  ```text
  The Senzing MCP server is unreachable.

  The MCP server is required for the bootcamp - it generates SDK code, looks up Senzing facts,
  and provides working examples. The bootcamp cannot proceed without it.

  Troubleshooting:
  1. Verify internet connectivity.
  2. Confirm the "senzing" MCP server is configured and enabled in Claude Code
     (it ships with this plugin's .mcp.json, pointing at https://mcp.senzing.com/mcp).
  3. If behind a corporate proxy, allowlist mcp.senzing.com.

  After fixing the connection, say "retry".
  ```

## 1. Project setup

Do this silently:

1. Create the working directory structure: `src/`, `data/`, `docs/`, `config/`, `database/`
   (and subfolders as modules need them - see file placement in `ground-rules.md`).
2. Create `config/bootcamp_progress.json` and `config/bootcamp_preferences.yaml` if they do not
   exist.

(The Kiro Power installed Agent Hooks here via `createHook`. In the Claude plugin, hooks ship
with the plugin in `hooks/hooks.json` and are already active - there is no hook-install step.)

## 2. Prerequisite check

Verify the basics for the bootcamper's platform: a working shell, Python 3 (for helper
scripts), and internet access to the MCP server. Report anything missing and let them fix it.
If the Senzing SDK is not yet installed, note that Module 2 covers installation - do not block.

(A full preflight script is a later porting phase; keep this check lightweight for now.)

## 3. Welcome and overview (preface item 1-2)

State that setup is complete ("Administrative setup is complete. The bootcamp is starting."),
then display the WELCOME banner:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓🎓🎓  WELCOME TO THE SENZING BOOTCAMP!  🎓🎓🎓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then give the overview (cover naturally, do not ask a question yet):

- This is a **guided discovery** of how to use Senzing. It is not a race - take it slow, read
  what the bootcamp tells you, and ask questions any time. Be curious.
- Goal: get comfortable generating Senzing SDK code, finishing with running code you can build on.
- You finish with a professional **recap PDF** trophy — a keepsake of everything you built, module by
  module, to keep and share with your team. A sample of a finished recap ships with the plugin at
  `docs/examples/bootcamp_recap.example.pdf` (under the plugin root, `${CLAUDE_PLUGIN_ROOT}`); point
  the bootcamper to it if they'd like to see what theirs will look like (yours will differ). This is
  a non-blocking mention, not a question or a gate.
- A brief Module 1-7 overview (Core track): (1) business problem, (2) SDK setup, (3) system
  verification, (4) data collection, (5) data quality and mapping, (6) data processing, (7)
  query, visualize, and discover. The Advanced Topics track covers the same Modules 1-7 and adds
  deeper production-hardening guidance (performance, security, monitoring, deployment) as
  follow-ups at graduation rather than as separate numbered modules.
- Tracks let you focus on what matters.
- Licensing: a built-in evaluation license covers the bootcamp's demos; more capacity options
  exist and Module 2 walks through them.
- If you hit unfamiliar terms (Entity Specification, DATA_SOURCE, entity resolution), ask and
  I'll look up the current definition from the Senzing docs on demand.

## 4. Level of detail (preface item 3)

👉 **How much detail would you like in the bootcamp output? Reply with a number:**

1. **concise** — minimal explanations, brief recaps. Best for experienced developers.
2. **standard** *(recommended)* — balanced what-and-why, block-level code summaries.
3. **detailed** — full explanations, line-by-line walkthroughs, SDK internals.

Wait for the answer, then **hold** the chosen verbosity for the consolidated preface write in
step 7 — do not write it now (INV-012: one preface write, not one per gate). When persisted, the
`verbosity` key will look like:

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

Tell them they can change it any time ("change verbosity", or "more code walkthroughs"). This is
NOT a gate; if they skip, apply `standard` and tell them so.

## 5. Track selection (preface item 4, gate)

👉 **Which track would you like? Reply with a number:**

1. **Core Bootcamp** *(recommended)* — Modules 1-7. Foundation from problem definition through
   query/visualize, then graduation.
2. **Advanced Topics** — the same Modules 1-7, plus deeper production-hardening guidance
   (performance, security hardening, monitoring, packaging/deployment) delivered through the
   graduation production project and migration checklist rather than as separate numbered modules.

Tracks are not mutually exclusive; completed modules always carry forward. This is a ⛔ gate:
wait for the real choice, do not assume one. **Hold** the chosen `track` for the consolidated
preface write in step 7 (do not write it now).

(Track switching and the per-gate validation table are part of later porting phases.)

## 6. Programming language selection (preface item 5, gate)

- **Detect the platform first (do not ask).** Determine the OS and architecture from the
  environment/system context (else run `uname`/`systeminfo`), and state it in one line
  ("Detected macOS on Apple Silicon"). Hold the detected `os`/`arch` for the step-7 consolidated
  write so Module 2 can reuse it instead of re-asking.
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
- **Hold** the chosen programming language for the consolidated preface write in step 7 (do not
  write it now). (Language-specific guidance - `lang-*` - is a later porting phase.)

## 6b. Initialize version control (optional)

Group this setup-adjacent decision with the programming-language choice, before the guided
modules begin. Do the detection quietly (administrative, not narrated).

Check whether the working directory is already a git repository. `git` behaves identically on
Linux, macOS, and Windows; rely on the command's **exit status**, not a shell-specific stderr
redirect:

```bash
git rev-parse --is-inside-work-tree
```

- **Already a repo** (command succeeds / prints `true`): skip the question. **Hold**
  `git_init: existing` for the step-7 consolidated write; proceed to step 7.
- **Not a repo** (command fails / non-zero exit): ask the pinned 👉 question, verbatim (INV-056):

  👉 **If you don't know what "git" is, just skip this. It's optional: would you like me to initialize a git repository for version control?**

  *(Internal: end the turn on this single 👉 question and wait — INV-005.)* On **yes**, run
  `git init` as a quiet administrative action and **hold** `git_init: true`; on **no**, skip and
  **hold** `git_init: false`. Either way, proceed to step 7.

Do not write preferences here: `git init` is an action (run it now), but the `git_init` value is
**held** for the single consolidated preface write in step 7 — no separate write (INV-058).

## 7. Any questions (preface item 6)

Before continuing, invite final questions:

👉 **Do you have any questions before we get started?**

- A clarification question: answer it at their verbosity level (using the MCP server for any
  Senzing facts), then ask once more whether they have other questions before continuing.
- A readiness signal ("no", "let's go", "ready", "start"): proceed to Module 0.

This is NOT a hard gate: if they say they are ready, advance.

**Consolidated preference write (once, quietly).** When the bootcamper signals readiness to
continue, persist all preface choices collected in steps 4-6b — `verbosity`, `track`, programming
language, `name` if it was captured, the detected `os`/`arch`, and the `git_init` outcome — to
`config/bootcamp_preferences.yaml` in a **single**
write. This is the only preference write of the preface; the earlier gates only held the answers,
so the bootcamper sees one diff instead of one per gate (INV-012). Do not narrate this
administrative write. Then hand off to Module 0.

## 8. Hand off to Module 0

Invoke the `module-00-entity-resolution-concepts` skill. Module 0 is the **optional**
entity-resolution concepts primer: it offers the primer via a pinned skip/keep 👉 gate, runs it
if the bootcamper wants it (ENTITY RESOLUTION CONCEPTS banner + MCP-sourced description + explore
gate), and then hands off to Module 1. If the bootcamper skips it, Module 0 proceeds straight to
Module 1. The numbered modules then run in ascending order (Module 1 → Module 2 → … → Module 7),
each ending with the standard module completion process in `module-completion.md`.
