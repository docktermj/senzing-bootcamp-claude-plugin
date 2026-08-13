# Onboarding Flow (fresh bootcamp)

Follow these steps in order. Follow `ground-rules.md` throughout. Do not narrate administrative
work in detail: do the setup quietly, then present the WELCOME banner.

The bootcamper-facing preface is deliberately short — it welcomes the bootcamper and orients them,
then hands off to the first module. It follows this order:

1. **Welcome + overview** (WELCOME banner + overview) — step 3.
2. **Any questions** — step 4.

Steps 0-2 are administrative and mostly silent; they run before the WELCOME banner.

**Setup questions live in the Bootcamp preparation module, not the preface.** The
Core-vs-Customized path choice, per-module selection, level of detail (verbosity), and programming
language are asked in
the first module — **Bootcamp preparation**
(`../bootcamp-preparation/SKILL.md`) — which the preface hands off to at step 5. That module also
initializes version control (git, no prompt — INV-095). (The
software-integration and deployment-target questions are asked later, in Module 1 Phase 2, per
INV-097 — not in the preface and not in Bootcamp preparation.) Entity resolution
concepts are also **not** part of the preface: they are an optional module
(`../module-00-entity-resolution-concepts/SKILL.md`) run only when selected during Bootcamp
preparation.

## 0. Setup preamble

Tell the bootcamper, in your own words:

"I'm going to do some quick administrative setup: creating your project directory and checking
your environment."

Read the plugin version from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` (the `version`
field; use "Unknown" if unreadable) and hold it to display with the WELCOME banner (step 3) and to
record in the recap.

## 0b. MCP health check (required)

Confirm the Senzing MCP server is reachable before starting. It is required: it generates SDK
code in the chosen language, looks up Senzing facts, and provides working examples.

- **Probe:** call `get_capabilities` (about a 10-second timeout). This is the call
  `ground-rules.md` → "Session start" already requires once before any other Senzing MCP call, so
  it doubles as the reachability probe and the preface makes **one** MCP call here, not two. Its
  response is also the tool manifest the guide needs anyway.
  - Do **not** probe with `search_docs`. It was specified here as "a lightweight call such as
    `search_docs(query="health check")`", which it is not: that query returns a multi-page FAQ
    article (~5 KB) for a question that only needed "did the server answer at all".
- **Success** (any response, even empty results): proceed silently.
- **Failure** (timeout or error): display a blocking message and STOP. ⛔ **Two different blockers
  produce this same symptom, and only one of them is a network problem** — so separate them before
  giving advice. Present the message, then end the turn on the single 👉 question below.

  ```text
  The Senzing MCP server is unreachable.

  The MCP server is required for the bootcamp - it generates SDK code, looks up Senzing facts,
  and provides working examples. The bootcamp cannot proceed without it.

  Troubleshooting:
  1. Verify internet connectivity.
  2. Confirm the "senzing" MCP server is configured and enabled in Claude Code
     (it ships with this plugin's .mcp.json, pointing at https://mcp.senzing.com/mcp).
  3. If behind a corporate proxy, allowlist mcp.senzing.com.
  ```

  👉 **Are you allowed to add an external MCP server on this machine? (respond yes or no)**

  - **Yes**, or an unsure answer → treat it as a **connectivity** failure: the troubleshooting above
    is the right advice. Ask them to fix it and say "retry", and wait.
  - **No** — "my employer blocks that", "security policy" → it is a **policy** failure, which no
    amount of proxy configuration fixes. Go to step 0c.

## 0c. Blocked by policy rather than by the network

At many companies, adding a new external MCP server is restricted or prohibited outright. A
bootcamper in that position did everything right, and network troubleshooting is the wrong answer to
give them. Say so plainly, then give them the only thing that helps: what to ask for, and who to ask.

⛔ **Name only what the server documents *now*, and attribute it** (INV-080). At server **1.32.9,
2026-08-13**, `get_capabilities`' tool manifest — inside its `get_sample_data` entry — names a
**private deployment** as a supported configuration: *"For full record access, call the MCP server
endpoint directly (https://mcp.senzing.com/mcp) or use the private deployment."* That is the route to
ask about. The same manifest notes the server *"hosts official Senzing SDK .deb packages at
/downloads/ … eliminating the need to configure apt/yum repositories in firewalled environments"* —
relevant to restricted **egress**, but be precise with the bootcamper: it addresses package
*download*, not MCP access, so on its own it does not clear this blocker.

⛔ **The plugin cannot supply or configure a private deployment, and must not imply it can.**
`search_docs` returns no documentation for obtaining or running one, re-verified on the current corpus
(**index_built 2026-08-11, 14,240 documents**) two ways: by keyword query, and by asking the document
that owns the subject — `senzing.com/docs/agentic`, the MCP server's own page, which describes what
the server *is* and carries no setup or self-hosting content. So the honest message is "this
configuration exists, here is who to ask", never invented setup steps.
<!-- MCP-NEGATIVE: search_docs — no documentation for obtaining or running a private MCP deployment — owner: search_docs(query='Agentic Entity Resolution MCP server configuration setup connect assistant') reaches senzing.com/docs/agentic, the MCP server's own page in the corpus, which returns an overview only and no setup content — server 1.32.9, 2026-08-13 -->

⚠️ **A second route was named at server 1.32.3 and is NOT named at 1.32.9 — do not cite it.** At
1.32.3 `sdk_guide`'s description described a **stdio mode** whose package URL was a local
`sz-mcp-coworker extract` command. At 1.32.9 neither "stdio" nor `sz-mcp-coworker` appears in that
description or anywhere in the `get_capabilities` manifest. Whether the mode was retired or the text
merely trimmed cannot be told from here, so it MUST NOT be offered as an available route: a fact the
server no longer states is not a fact the plugin may assert (INV-080). Re-check on a later server, and
if it returns, add it here with its attribution.
<!-- MCP-NEGATIVE: sdk_guide(description) — no longer names a stdio mode or the sz-mcp-coworker binary, which it did at 1.32.3 — owner: sdk_guide's own description is where that claim lived, and get_capabilities' manifest entry for the tool agrees it is absent — server 1.32.9, 2026-08-13 -->

Tell the bootcamper, in your own words:

- This is a policy restriction, not something wrong with their machine or their setup — and not
  something they did.
- A **private deployment** of the Senzing MCP server is a configuration Senzing recognises, and it may
  satisfy a policy that forbids adding a public external endpoint. Attribute it: it comes from the MCP
  server's own tool manifest, read this session.
- The plugin cannot set one up, and Senzing's indexed documentation does not currently cover how to
  obtain one — so the next step is a person: their **Senzing contact**, or **support@senzing.com**.
- ⛔ **Never offer to continue without the server.** Every Senzing fact in this bootcamp comes from it
  (INV-080); there is no offline mode, and a bootcamp answering Senzing questions from training data
  is worse than one that does not start. Saying this plainly respects their time.

⚠️ **Do not present a private deployment as verified to satisfy any particular policy.** Whether a
given configuration is permitted is their organisation's decision, not a fact the plugin can assert.
Offer it as the thing to ask about.

Then end the turn on this single 👉 question and wait:

👉 **Would you like me to stop here so you can follow that up? (respond yes or no)**

- **Yes** → acknowledge what they are following up, and stop. Do not loop.
- **No**, or "let me try something first" → return to 0b's troubleshooting and wait for "retry".

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
If the Senzing SDK is not yet installed, note that SDK setup covers installation - do not block.

(A full preflight script is a later porting phase; keep this check lightweight for now.)

## 3. Welcome and overview (preface item 1)

State that setup is complete ("Administrative setup is complete. The bootcamp is starting."),
then display the WELCOME banner:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓🎓🎓  WELCOME TO THE SENZING BOOTCAMP!  🎓🎓🎓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then show the plugin version as a one-line statement (INV-105): `Senzing Bootcamp vX.Y.Z`.

**Verbosity applies here only if a preset already exists.** Read `verbosity` from
`config/bootcamp_preferences.yaml`: when it is `minimal`, suppress this line; otherwise show it.
⛔ On a **fresh** bootcamp there is no preset yet — verbosity is chosen in Bootcamp preparation
(INV-075 moved it out of the preface, superseding INV-024), and step 4 below writes no preferences —
so the line is simply shown, and that is correct rather than an oversight. The suppression path is
reachable only on a resumed run, or when the bootcamper pre-seeded the file (INV-133). Do not stall
trying to honor a preference that cannot exist yet, and do not ask for verbosity here.

Then give the overview (cover naturally, do not ask a question yet).

⛔ **Every bullet below has a verbosity treatment — none is unconditional.** Two carry their own
(the version line above and the feedback-trigger bullet below); the rest are governed as a group,
so there is no bullet whose behaviour under a preset is left to guesswork:

| Preset | The overview is |
|---|---|
| `minimal` | the **module list** plus the **how-long-it-takes** bullet, and nothing else — orientation only |
| `concise` | all bullets except *guided discovery* and *unfamiliar terms*, each trimmed to one line |
| `standard` / `detailed` | all ten, as written |

The split is orientation versus encouragement: the module list and the resume-and-time facts are
what a bootcamper needs to navigate, and the rest is framing an expert moving fast does not. On a
**fresh** bootcamp no preset exists yet, so all ten are shown and that is correct rather than an
oversight (INV-075/INV-133) — the reduced forms are reachable only on a resumed run or a pre-seeded
file.

- This is a **guided discovery** of how to use Senzing. It is not a race - take it slow, read
  what the bootcamp tells you, and ask questions any time. Be curious.
- Goal: get comfortable generating Senzing SDK code, finishing with running code you can build on.
- You finish with a professional **recap PDF** — a keepsake of everything you built, module by
  module, to keep and share with your team.
- The bootcamp is a sequence of named modules: **Bootcamp preparation**, *Entity Resolution
  Concepts* (optional), **Discover the Business Problem**, **SDK setup**, *System verification* (optional),
  *Truth Set visualization* (optional), **Data collection**, **Data Quality, Mapping, and Transformation**, **Data
  processing**, **Query, Visualize and Discover**, and **Bootcamp graduation**.
- Right after this welcome, the first module — **Bootcamp preparation** — lets you pick how to run
  the bootcamp: **Core** (every module, in order) or **Customized** (you choose which optional
  modules to include). It also sets your level of detail and programming language, and sets up
  version control for you automatically (no question). Required modules always run; the optional
  ones are yours to include or skip.
- One thing to know if you customize: *Truth Set visualization* is the interactive web app that
  shows Senzing working on your machine — if you deselect it, you won't see that visual
  verification.
- Licensing: a built-in evaluation license covers the bootcamp's demos; more capacity options
  exist and SDK setup walks through them.
- If you hit unfamiliar terms (Entity Specification, DATA_SOURCE, entity resolution), ask and
  I'll look up the current definition from the Senzing docs on demand.
- **How long it takes:** the bootcamp is **module-sized, not clock-sized** — each module tells you
  its own time estimate right before it starts, so you always know what the next stretch costs.
  There is no fixed total: it depends on whether you pick Core or Customized (still to come, in
  Bootcamp preparation) and on how fast the SDK downloads and installs on your machine. **You do
  not have to finish in one sitting** — progress is saved as you go, and you can stop and pick up
  where you left off.
- **If anything about the bootcamp itself is confusing, broken, or missing, tell me the moment you
  notice it:** start a message with **"bootcamp feedback:"** and I will capture it. You do not lose
  your place — the note is saved under `docs/feedback/`, then the bootcamp question you were on
  comes straight back and we carry on. No need to save it for the end.

**The feedback-trigger bullet is verbosity-aware, exactly like the version line above**
(INV-011/INV-012 — the treatment INV-096 gives the time estimate): under `minimal`, suppress it;
under `concise`, one line ("Say \"bootcamp feedback:\" any time — it is captured and you keep your
place."); otherwise the full bullet. ⛔ Same caveat as the version line: on a **fresh** bootcamp no
preset exists yet, so the full bullet is simply shown and that is correct, not an oversight
(INV-075/INV-133). ⛔ **State it; never make it a 👉 question** — it needs no answer, and INV-012
forbids output the bootcamper cannot act on. ⛔ **Do not repeat it at every module start** — the
module-start apparatus is already dense (INV-028-031, INV-096, the model/effort nudge), and this is
an always-available control (INV-010). Once, here, is the point; graduation's closing invitation
(`../graduation/SKILL.md`, Step 7) stays as it is.

## 4. Any questions (preface item 2)

Before continuing, invite final questions:

👉 **Do you have any questions before we get started?**

- A clarification question: answer it (using the MCP server for any Senzing facts), then ask once
  more whether they have other questions before continuing.
- A readiness signal ("no", "let's go", "ready", "start"): proceed to step 5.

This is NOT a hard gate: if they say they are ready, advance.

⛔ **"How long will this take?" is the single most likely question here — answer it from step 3's
overview, and NEVER invent a total.** Say what is true: the bootcamp is module-sized, each module
states its own estimate at its start, the total depends on the Core-vs-Customized choice they have
not made yet and on install/download speed, and progress is saved so it can be done across
sittings. ⛔ **Do not offer a figure like "about 4-6 hours."** No per-module estimates exist in this
plugin to sum — the modules state the *requirement* to give an estimate, not values — so any total
would be fabricated, which is exactly what INV-096 exists to prevent. A number invented here is
worse than no number: it sets an expectation the rest of the bootcamp did not agree to.

(No preferences are written in the preface. All setup choices — path, module selection, verbosity,
programming language, git — are captured and persisted in the Bootcamp preparation module in a
single consolidated write, INV-058.)

## 5. Hand off to the Bootcamp preparation module

Invoke the `bootcamp-preparation` skill. Bootcamp preparation is the **first, mandatory module**:
it asks the Core-vs-Customized path choice, per-module selection, verbosity, and programming
language, initializes version control (git, no prompt — INV-095), persists these in one
consolidated write, then hands off to the first selected
content module (the optional Entity Resolution Concepts primer if selected, otherwise Discover the Business Problem).
The selected modules then run in the order recorded in `selected_modules`, each ending with the
standard module completion process in `module-completion.md`.
