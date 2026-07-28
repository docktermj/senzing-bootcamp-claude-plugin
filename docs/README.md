# Senzing Bootcamp Claude Code Plugin

## Using the Claude Code CLI

In this section are instructions for
installing the Claude Code CLI,
installing the Senzing Bootcamp plugin,
and starting the Bootcamp.

For the desktop application instead, see
[Using Claude Desktop](../README.md#using-claude-desktop).

1. To install the Claude Code CLI on macOS or Linux:

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
   the best value and switch up to **Opus 5** for the correctness-critical
   stretches: **SDK setup**, **Data Quality, Mapping, and Transformation**,
   and **Graduation**. The bootcamp surfaces the recommendation at the start of
   each module, so you never have to remember which is which.

   For the smoothest ride, run the Claude Code CLI with `--permission-mode auto`.

1. Example command:

    ```console
    claude --model claude-sonnet-5 --effort medium --permission-mode auto
    ```

1. *Note:* besides the Claude Code CLI and Claude Desktop,
   the Senzing Bootcamp Claude Plugin can also be run in a Claude IDE extension:
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

## Uninstall plugin

1. Uninstall the plugin and marketplace.

    ```console
    claude plugin uninstall senzing-bootcamp@senzing-bootcamp
    claude plugin marketplace remove senzing-bootcamp
    ```

[Claude Code for VSCode]: https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code
