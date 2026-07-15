# Senzing Bootcamp Claude Code plugin

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

## Install Claude Code and plugin

1. Download and install [Claude Code].

1. Install Senzing Bootcamp Claude plugin.

    ```console
    claude plugin marketplace add docktermj/senzing-bootcamp-claude-plugin
    claude plugin install senzing-bootcamp@senzing-bootcamp
    ```

## Run Claude Code

1. For "smoothest ride", run Claude with "auto".
   Example:

    ```console
    mkdir senzing-bootcamp
    cd senzing-bootcamp
    claude --permission-mode auto
    ```

1. *Note:* In addition to Claude Code,
   the Senzing Bootcamp Claude plugin can also be run with:
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
    - `/graduate` — finish the Core track: generate your recap PDF trophy
      (`docs/bootcamp_recap.pdf`) and a production-ready `production/` project.

### What you finish with

The bootcamp is a guided, module-by-module tutorial (Modules 1-7 in order). You end with working
Senzing code and data in your project (`src/`, `data/`, `database/`), a professional recap PDF
you can keep and share, and a `production/` starter project.

### Uninstall plugin

1. Uninstall the plugin and marketplace.

    ```console
    claude plugin uninstall senzing-bootcamp@senzing-bootcamp
    claude plugin marketplace remove senzing-bootcamp
    ```

[Claude Code]: https://claude.com/product/claude-code
[Claude Code for VSCode]: https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code
[Senzing MCP server]: https://mcp.senzing.com/mcp
