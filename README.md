# Senzing Bootcamp (Claude Code plugin)

A guided bootcamp for learning [Senzing](https://senzing.com) entity resolution, packaged
as a Claude Code plugin. Install it, then say **"start the bootcamp"** to be guided through
a hands-on, module-by-module tutorial.

This is the Claude Code counterpart to the Kiro "Senzing Bootcamp" Power.

## Install

This repository is both the plugin and its own marketplace.

```
/plugin marketplace add docktermj/senzing-bootcamp-claude-plugin
/plugin install senzing-bootcamp@senzing-bootcamp
```

Then, in any working directory:

```
/start-bootcamp
```

or just tell Claude "start the bootcamp".

## Requirements

- Claude Code with plugin support.
- Network access to the Senzing MCP server (`https://mcp.senzing.com/mcp`). The bootcamp
  cannot proceed without it; it generates SDK code, looks up Senzing facts, and provides
  working examples.

## What's inside

```
.claude-plugin/marketplace.json        # marketplace listing (this repo)
plugins/senzing-bootcamp/
  .claude-plugin/plugin.json           # plugin manifest
  .mcp.json                            # Senzing MCP server
  commands/start-bootcamp.md           # entry point (/start-bootcamp)
  skills/bootcamp-onboarding/          # onboarding + ground rules
  skills/module-01-first-resolution/   # sample module (more to come)
  hooks/hooks.json                     # SessionStart (resume), PreToolUse (write-gate), Stop (next-step nudge)
  scripts/                             # hook scripts
```

## Status

Early scaffold (v0.1.0). One sample module is included; the remaining modules and the full
onboarding flow are being ported from the Kiro bootcamp.

## Mapping from the Kiro Power

| Kiro Power | This plugin |
| --- | --- |
| POWER.md manifest | `.claude-plugin/plugin.json` |
| Steering files (`inclusion: manual`) | Skills (`skills/<name>/SKILL.md`) |
| Steering files (`inclusion: always`) | Plugin instructions / skill ground rules |
| Agent hooks (`.kiro/hooks/*.json`) | `hooks/hooks.json` (command / prompt / agent types) |
| `mcp.json` | `.mcp.json` |
| "Start the bootcamp" | `/start-bootcamp` command + `bootcamp-onboarding` skill |
| Powers panel distribution | Plugin marketplace |
