# Senzing Bootcamp Claude Plugin Development

## Conventions

### Spelling: US English, not British English

**US English is the preferred spelling throughout this repository** — shipped
plugin prose, specs, invariants, tests, code comments, and identifiers alike.
Prefer `-ize`/`-yze` over `-ise`/`-yse`, `-or` over `-our`, `-er` over `-re`,
`license` over `licence`, and a single `l` before a suffix (`labeled`,
`modeled`, `traveled`).

| British (avoid) | US (use)     | British (avoid) | US (use)     |
| --------------- | ------------ | --------------- | ------------ |
| analysed        | analyzed     | judgement       | judgment     |
| artefact        | artifact     | labelled        | labeled      |
| behaviour       | behavior     | licence         | license      |
| catalogue       | catalog      | millimetre      | millimeter   |
| centre          | center       | normalise       | normalize    |
| colour          | color        | organisation    | organization |
| defence         | defense      | recognise       | recognize    |
| favour          | favor        | sanitise        | sanitize     |
| honoured        | honored      | summarise       | summarize    |

Two deliberate exceptions, both verified rather than assumed:

- `plugins/senzing-bootcamp/scripts/vendor/d3.v7.min.js` — a vendored
  third-party bundle whose `grey` is a CSS color-name key, not prose.
- `D:\Programme` in `tests/test_windows_browser_discovery.py` (and where
  `specs/IMPLEMENTED.md` records it) — a *German* localized `%ProgramFiles%`
  fixture proving environment expansion. It is not English.

`SCOPE_VERBS` in `.claude/skills/compact-dev-environment/widened_scope.py`
deliberately carries both `"generalis"` and `"generaliz"` so the scanner stays
tolerant of either spelling in text it reads.

⚠️ This is a convention, not yet an invariant: no test enforces it, so a
British spelling reintroduced in a future edit will not fail the suite.

## Claude development skills

### Create specifications

1. `/feedback-to-specs` - Extract spec/ files from SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md files.

### Development loop

1. `/implement-spec` - Implement specifications in the `spec/` directory.
1. `/delegate-to-mcp-server` - Determine if there are instructions that are in the MCP server
1. `/compact-dev-development` - Try to compact the plugin.
1. `/production-ready-review` - Do a thorough static review.
1. `/dry-run` - Do a thorough runtime review.

### Publish

1. `/auto-test` -
1. `/retrofit-from-public`
1. `/propagate-to-public`
