# Onboarding Flow (fresh bootcamp)

Follow these steps in order. Follow `ground-rules.md` throughout. Do not narrate administrative
work in detail: do the setup quietly, then present the WELCOME banner.

The bootcamper-facing preface is deliberately short — it welcomes the bootcamper and orients them,
then hands off to the first module. It follows this order:

1. **Welcome + overview** (WELCOME banner + overview) — step 3.
2. **Any questions** — step 4.

Steps 0-2 are administrative and mostly silent; they run before the WELCOME banner.

**All setup questions live in the Bootcamp preparation module, not the preface.** The
Core-vs-Customized path choice, per-module selection, level of detail (verbosity), programming
language, and version control are asked in the first module — **Bootcamp preparation**
(`../bootcamp-preparation/SKILL.md`) — which the preface hands off to at step 5. Entity resolution
concepts are also **not** part of the preface: they are an optional module
(`../module-00-entity-resolution-concepts/SKILL.md`) run only when selected during Bootcamp
preparation.

## 0. Setup preamble

Tell the bootcamper, in your own words:

"I'm going to do some quick administrative setup: creating your project directory and checking
your environment."

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

## 3. Welcome and overview (preface item 1)

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
- You finish with a professional **recap PDF** — a keepsake of everything you built, module by
  module, to keep and share with your team. A sample of a finished recap ships with the plugin at
  `docs/examples/bootcamp_recap.example.pdf` (under the plugin root, `${CLAUDE_PLUGIN_ROOT}`); point
  the bootcamper to it if they'd like to see what theirs will look like (yours will differ). This is
  a non-blocking mention, not a question or a gate.
- The bootcamp is a sequence of named modules: **Bootcamp preparation**, *Entity Resolution
  Concepts* (optional), **Business problem**, **SDK setup**, *System verification* (optional),
  *Truth Set visualization* (optional), **Data collection**, **Data quality & mapping**, **Data
  processing**, **Query, Visualize and Discover**, and **Graduation**.
- Right after this welcome, the first module — **Bootcamp preparation** — lets you pick how to run
  the bootcamp: **Core** (every module, in order) or **Customized** (you choose which optional
  modules to include). It also sets your level of detail, programming language, and version
  control. Required modules always run; the optional ones are yours to include or skip.
- One thing to know if you customize: *Truth Set visualization* is the interactive web app that
  shows Senzing working on your machine — if you deselect it, you won't see that visual
  verification.
- Licensing: a built-in evaluation license covers the bootcamp's demos; more capacity options
  exist and Module 2 walks through them.
- If you hit unfamiliar terms (Entity Specification, DATA_SOURCE, entity resolution), ask and
  I'll look up the current definition from the Senzing docs on demand.

## 4. Any questions (preface item 2)

Before continuing, invite final questions:

👉 **Do you have any questions before we get started?**

- A clarification question: answer it (using the MCP server for any Senzing facts), then ask once
  more whether they have other questions before continuing.
- A readiness signal ("no", "let's go", "ready", "start"): proceed to step 5.

This is NOT a hard gate: if they say they are ready, advance.

(No preferences are written in the preface. All setup choices — path, module selection, verbosity,
programming language, git — are captured and persisted in the Bootcamp preparation module in a
single consolidated write, INV-058.)

## 5. Hand off to the Bootcamp preparation module

Invoke the `bootcamp-preparation` skill. Bootcamp preparation is the **first, mandatory module**:
it asks the Core-vs-Customized path choice, per-module selection, verbosity, programming language,
and version control, persists them in one consolidated write, then hands off to the first selected
content module (the optional Entity Resolution Concepts primer if selected, otherwise Module 1).
The selected modules then run in the order recorded in `selected_modules`, each ending with the
standard module completion process in `module-completion.md`.
