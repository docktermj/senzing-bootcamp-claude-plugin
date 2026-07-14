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

## Run Claude Code

1. Download and install [Claude Code].
1. For "smoothest ride", run Claude with "auto".
   Example:

    ```console
    mkdir senzing-bootcamp
    cd senzing-bootcamp
    claude --permission-mode auto
    ```

## Install plugin

This repository is both the plugin and its own marketplace.

1. Install Senzing Bootcamp plugin.

    ```console
    /plugin marketplace add docktermj/senzing-bootcamp-claude-plugin
    /plugin install senzing-bootcamp@senzing-bootcamp
    ```

1. Activate the plugin.

    ```console
    /reload-plugins
    ```

1. Start the bootcamp.

    ```console
    /start-bootcamp
    ```

  or just tell Claude "start the bootcamp".

### Uninstall plugin

```console
claude plugin uninstall senzing-bootcamp@senzing-bootcamp
```

[Claude Code]: https://claude.com/product/claude-code
[Senzing MCP server]: https://mcp.senzing.com/mcp
