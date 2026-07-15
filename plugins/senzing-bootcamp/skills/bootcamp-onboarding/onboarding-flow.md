# Onboarding Flow (fresh bootcamp)

Follow these steps in order. Follow `ground-rules.md` throughout. Do not narrate administrative
work in detail: do the setup quietly, then present the ENTITY RESOLUTION CONCEPTS banner, and
later the WELCOME banner.

The bootcamper-facing preface follows this order:

1. **Entity resolution concepts** (banner + description + explore gate) — steps 3.
2. **Welcome + overview** (WELCOME banner + overview) — step 4.
3. **Level of detail** (verbosity) — step 5.
4. **Track** — step 6.
5. **Programming language** — step 7.
6. **Any questions** — step 8.

Steps 0-2 are administrative and mostly silent; they run before the concepts banner.

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

## 3. Entity resolution concepts (preface item 1-3)

Teach the core idea of entity resolution first, so the bootcamper has context before the guided
bootcamp begins. Follow `entity-resolution-intro.md`:

1. Present the **ENTITY RESOLUTION CONCEPTS** banner (defined in `entity-resolution-intro.md`).
2. Give the description of entity resolution, pulling all Senzing-specific facts from the MCP
   server (never from memory).
3. End on the mandatory exploration gate: ask whether they want to explore entity resolution
   before beginning. Do not advance until the bootcamper signals they are ready.

## 4. Welcome and overview (preface item 4-5)

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
- A brief Module 1-7 overview (Core track): (1) business problem, (2) SDK setup, (3) system
  verification, (4) data collection, (5) data quality and mapping, (6) data processing, (7)
  query, visualize, and discover. The Advanced Topics track adds Modules 8-11 (performance,
  security, monitoring, deployment).
- Tracks let you focus on what matters.
- Licensing: a built-in evaluation license covers the bootcamp's demos; more capacity options
  exist and Module 2 walks through them.
- If you hit unfamiliar terms (Entity Specification, DATA_SOURCE, entity resolution), ask and
  I'll look up the current definition from the Senzing docs on demand.

## 5. Level of detail (preface item 6)

👉 **How much detail would you like in the bootcamp output? Reply with a number:**

1. **concise** — minimal explanations, brief recaps. Best for experienced developers.
2. **standard** *(recommended)* — balanced what-and-why, block-level code summaries.
3. **detailed** — full explanations, line-by-line walkthroughs, SDK internals.

Wait for the answer, then persist it under the `verbosity` key in
`config/bootcamp_preferences.yaml`:

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

## 6. Track selection (preface item 7, gate)

👉 **Which track would you like? Reply with a number:**

1. **Core Bootcamp** *(recommended)* — Modules 1-7. Foundation from problem definition through
   query/visualize.
2. **Advanced Topics** — Modules 1-11. Adds performance, security hardening, monitoring, and
   packaging/deployment.

Tracks are not mutually exclusive; completed modules always carry forward. This is a ⛔ gate:
wait for the real choice, do not assume one. Persist `track` to
`config/bootcamp_preferences.yaml`.

(Advanced-track knowledge check, track switching, and the per-gate validation table are part of
later porting phases.)

## 7. Programming language selection (preface item 8, gate)

- Detect the platform, then call `get_capabilities` or `sdk_guide` on the Senzing MCP server for
  the supported programming languages on that platform.
- Always say "**programming language**", never the bare word "language" (avoids confusion with
  spoken languages).
- Present the MCP-returned list. If the MCP server flags a language as discouraged/unsupported
  on the platform, relay that and suggest alternatives.

  👉 **Which programming language would you like to use for the bootcamp?**

- This is a ⛔ gate: wait for the bootcamper's real choice. Do NOT assume or say "I'll go with X."
- Persist the choice to `config/bootcamp_preferences.yaml`. (Language-specific guidance -
  `lang-*` - is a later porting phase.)

## 8. Any questions (preface item 9)

Before starting Module 1, invite final questions:

👉 **Do you have any questions before we begin Module 1?**

- A clarification question: answer it at their verbosity level (using the MCP server for any
  Senzing facts), then ask once more whether they have other questions before continuing.
- A readiness signal ("no", "let's go", "ready", "start"): proceed to Module 1.

This is NOT a hard gate: if they say they are ready, advance.

## 9. Hand off to Module 1

Invoke the `module-01-business-problem` skill to begin Module 1, applying the module-start
banner and journey map from `ground-rules.md`. Modules then run in ascending numeric order
(Module 1 → Module 2 → … → Module 7), each ending with the standard module completion process
in `module-completion.md`.
