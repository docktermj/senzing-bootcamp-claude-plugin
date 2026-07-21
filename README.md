# Senzing Bootcamp Claude Code Plugin

A guided bootcamp for learning [Senzing] entity resolution,
packaged as a Claude Code plugin.
Install it, then say **"start the bootcamp"** to be guided through
a hands-on, module-by-module tutorial.

## What the bootcamp covers

A guided sequence of hands-on modules takes you from zero to working entity
resolution:

- Entity Resolution Concepts primer *(optional)*
- Discover the Business Problem
- SDK Installation and Configuration
- System Verification
- An interactive web app of the resolved Truth Set data. *(optional)*
- Identify and Collect Data Sources
- Data Quality & Mapping
- Data Processing
- Query, Visualize, and Discover
- Graduation

You finish with working Senzing code and data in your project, a professional
recap PDF you can keep and share, and a production starter. See
[What you finish with](#what-you-finish-with) for details.

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

In this section are instructions for
installing the Claude app,
installing the Senzing Bootcamp plugin,
and starting the Bootcamp.

1. Download and install the [Claude app].
1. Start Claude app.
1. In the Claude app,
    1. In the left-hand pane, choose "**</> Code**".
    1. In the *Code* pane, click "**New**".
1. In the Claude app, near the bottom, choose the "Working directory" (it might say "Select folder...")
    1. Create and use a new folder for the Senzing Bootcamp.
1. In the Claude app, on the bottom, click the "Add" icon (**+**) > **Add Plugins...** (Or it may be just "Plugins").
    1. In the *Directory* pane, near "Filter by" and "Sort by", click the "Add Marketplace" icon (**+**).
    1. In the *Add marketplace* pane, enter "**URL:**"

        ```console
        https://github.com/docktermj/senzing-bootcamp-claude-plugin
        ```

    1. Click the "**Sync**" button.
    1. In the *Directory* pane,
        1. Select "**Code**" tab.
        1. Select "**Senzing bootcamp**".
        1. Click on "**Install**".
        1. Close *Directory* pane.
1. In the Claude app, on the bottom,
    1. Choose the Mode: "**auto**" for a smooth ride.
    1. Choose the Model "**Sonnet 5**".
    1. Choose the Effort: "**medium**".
1. In the Claude app near the bottom in the agentic chat, enter:

    ```console
    Start the bootcamp
    ```

### Using Claude Code

In this section are instructions for
installing Claude Code,
installing the Senzing Bootcamp plugin,
and starting the Bootcamp.

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

1. *Command line options:* run most of the bootcamp on **Sonnet 5** for
   the best value and switch up to **Opus 4.8** for the correctness-critical
   stretches: Modules 2 and 5, and graduation.

   For the smoothest ride, run Claude with `--permission-mode auto`.

1. Example command:

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

    - `/bootcamp-feedback` - share feedback about the bootcamp
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
[Claude app]: https://claude.ai/download
[Claude Code for VSCode]: https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code
[Senzing MCP server]: https://mcp.senzing.com/mcp
[Senzing]: https://senzing.com
