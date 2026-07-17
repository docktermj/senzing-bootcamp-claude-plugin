# Senzing Bootcamp Claude Code Plugin

A guided bootcamp for learning [Senzing](https://senzing.com) entity resolution,
packaged as a Claude Code plugin.
Install it, then say **"start the bootcamp"** to be guided through
a hands-on, module-by-module tutorial.

## Requirements

- Network access to the [Senzing MCP server].
  The bootcamp cannot proceed without it.
  It generates SDK code,
  looks up Senzing facts,
  and provides working examples.

## Install Claude Code and Senzing Bootcamp Claude Plugin

1. Download and install [Claude Code].
    1. To install Claude CLI via commandline on macOS or Linux:

        ```console
        curl -fsSL https://claude.ai/install.sh | bash
        ```

1. Install Senzing Bootcamp Claude Plugin.

    ```console
    claude plugin marketplace add docktermj/senzing-bootcamp-claude-plugin
    claude plugin install senzing-bootcamp@senzing-bootcamp
    ```

1. If the Senzing Bootcamp Claude Plugin is already installed, update it.

    ```console
    claude plugin update senzing-bootcamp@senzing-bootcamp
    ```

## Run Claude Code

1. Create a new directory for the bootcamp.
   Example:

    ```console
    mkdir senzing-bootcamp
    cd senzing-bootcamp
    ```

1. *Choosing a model (recommended):* run most of the bootcamp on **Sonnet 5** —
   the best value — and switch up to **Opus 4.8** for the correctness-critical
   stretches: Modules 2 and 5, and graduation.

   Before Modules 2 or 5 or graduation, switch the running session up with
   `/model claude-opus-4-8`, then back afterward with `/model claude-sonnet-5`.
   Prefer one model and no switching? Run `--model claude-opus-4-8` throughout —
   simplest, at higher cost on the lighter modules. Full per-skill breakdown:
   [`plugins/senzing-bootcamp/docs/model-selection.md`](plugins/senzing-bootcamp/docs/model-selection.md).

   For the smoothest ride, run Claude with `--permission-mode auto`.

    Example command:

    ```console
    claude --model claude-sonnet-5 --effort medium --permission-mode auto
    ```

1. *Note:* In addition to Claude Code,
   the Senzing Bootcamp Claude Plugin can also be run with:
    - [Claude Code for VSCode]

## Start the Senzing Bootcamp

1. Start the bootcamp.

    ```console
    /start-bootcamp
    ```

      or just tell Claude "start the bootcamp".

1. Other commands (available any time during a bootcamp):

    - `/bootcamp-feedback` — share feedback about the bootcamp
      (or just say "bootcamp feedback"). Saved to
      `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`.
    - `/graduate` — finish the Core track: generate the Bootcamp recap PDF
      (`docs/bootcamp_recap.pdf`) and a production-ready `production/` project.

### What you finish with

The bootcamp is a guided, module-by-module tutorial.
You end with working Senzing code and data in your project (`src/`, `data/`, `database/`),
a professional recap PDF you can keep and share (e.g. [bootcamp_recap.pdf]),
and a `production/` starter project.

### Uninstall plugin

1. Uninstall the plugin and marketplace.

    ```console
    claude plugin uninstall senzing-bootcamp@senzing-bootcamp
    claude plugin marketplace remove senzing-bootcamp
    ```

[bootcamp_recap.pdf]: docs/bootcamp_recap.pdf
[Claude Code]: https://claude.com/product/claude-code
[Claude Code for VSCode]: https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code
[Senzing MCP server]: https://mcp.senzing.com/mcp
