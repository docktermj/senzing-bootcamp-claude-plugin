# Senzing Bootcamp Claude Code Plugin

A guided bootcamp for learning [Senzing] entity resolution,
packaged as a Claude Code plugin.
Install it, then say **"start the bootcamp"** to be guided through
a hands-on, module-by-module tutorial.

## Requirements

- Network access to the [Senzing MCP server].
  The bootcamp cannot proceed without it.
  It generates SDK code,
  looks up Senzing facts,
  and provides working examples.

## Install and run Claude Code with the Senzing Bootcamp Claude Plugin

1. For Claude App on Mac or Windows: [Using Claude app](#using-claude-app)
1. For Claude Code on Linux or Mac: [Using Claude Code](#using-claude-code)

### Using Claude app

1. Download and install [Claude Code].
1. Start Claude app.
1. In the Claude app,
    1. In the left-hand panel, choose **</> Code**.
    1. In the *Code* panel, click **New session**.
1. In the Claude app, near the bottom, choose the "Working directory" (it might say "Select folder...")
    1. Create and use a new folder for the Senzing Bootcamp.
1. In the Claude app, on the bottom, click the "Add" icon (**+**) > **Add Plugins...** (Or it may be just "Plugins").
    1. In the *Directory* panel, near "Filter by" and "Sort by", click the "Add Marketplace" icon (**+**).
    1. In the *Add marketplace* panel, enter **URL:**

        ```console
        https://github.com/docktermj/senzing-bootcamp-claude-plugin
        ```

    1. Click the **Sync** button.
    1. In the *Directory* panel,
        1. Select **Code** tab.
        1. Select **Senzing bootcamp**.
        1. Click on **Install**.
        1. Close *Directory* panel.
1. In the Claude app, on the bottom,
    1. Choose the Mode: **auto** for a smooth ride.
    1. Choose the Model **Sonnet 5**.
    1. Choose the Effort: **medium**.
1. In the Claude App near the bottem in the agentic chat, enter:

    ```console
    Start the bootcamp
    ```

### Using Claude Code

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
1. Start the bootcamp. Tell Claude:

    ```console
    Start the bootcamp
    ```

## Additional bootcamp commands

1. Other commands (available any time during a bootcamp):

    - `/bootcamp-feedback` — share feedback about the bootcamp
      (or just say "bootcamp feedback"). Saved to
      `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`.

## What you finish with

The bootcamp is a guided, module-by-module tutorial.
You end with working Senzing code and data in your project (`src/`, `data/`, `database/`),
a professional recap PDF you can keep and share (e.g. [bootcamp_recap.pdf], but yours will differ),
and a `production/` starter project.

## Uninstall plugin

1. Uninstall the plugin and marketplace.

    ```console
    claude plugin uninstall senzing-bootcamp@senzing-bootcamp
    claude plugin marketplace remove senzing-bootcamp
    ```

[bootcamp_recap.pdf]: https://raw.githubusercontent.com/docktermj/senzing-bootcamp-claude-plugin/refs/heads/main/plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf
[Claude Code]: https://claude.com/product/claude-code
[Claude Code for VSCode]: https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code
[Senzing MCP server]: https://mcp.senzing.com/mcp
[Senzing]: https://senzing.com
