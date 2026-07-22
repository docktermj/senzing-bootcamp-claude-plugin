# Senzing Bootcamp Claude Code Plugin

A guided bootcamp for learning [Senzing] entity resolution,
packaged as a Claude Code plugin.
Install it, then say **"start the bootcamp"** to be guided through
a hands-on, module-by-module tutorial.

## What the bootcamp covers

A guided sequence of hands-on modules takes you from zero
to working entity resolution:

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

### Using Claude app

In this section are instructions for
installing the Claude app,
installing the Senzing Bootcamp plugin,
and starting the Bootcamp.

1. Download and install the [Claude app].
1. Start Claude app.
    1. If asked, install `git`.
1. In the Claude app,
    1. In the left-hand pane, choose "**</> Code**".
    1. In the *Code* pane, click "**New**".
1. In the Claude app, near the bottom, choose the "Working directory" (it might say "Select folder...")
    1. Create and use a new folder for the Senzing Bootcamp.
1. In the Claude app, on the bottom, click the "Add" icon (**+**) > **Add Plugins...** (Or it may be just "Plugins").
    1. In the *Directory* pane, near "Filter by" and "Sort by", click the "Add Marketplace" icon (**+**).
        1. If the plus sign is missing, see [Troubleshooting: Claude Code inoperative](#claude-code-inoperative)
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

## What you finish with

The bootcamp is a guided, module-by-module tutorial.
You end with working Senzing code and data in your project (`src/`, `data/`, `database/`),
a professional recap PDF you can keep and share (e.g. [bootcamp_recap.pdf], but yours will differ),
and a `production/` starter project.

### Troubleshooting

### Claude code inoperative

If you are unable to enter and process prompts in Claude Desktop
or if you are unable to add a Claude Marketplace or Claude plugin,
the issue may be with an incomplete installation of Claude Desktop.

- Claude Desktop requires `git` to be installed.

[bootcamp_recap.pdf]: https://raw.githubusercontent.com/docktermj/senzing-bootcamp-claude-plugin/refs/heads/main/plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf
[Claude app]: https://claude.ai/download
[Senzing MCP server]: https://mcp.senzing.com/mcp
[Senzing]: https://senzing.com
