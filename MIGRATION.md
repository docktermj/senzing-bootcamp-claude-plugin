# Keeping this plugin in sync with the Kiro Power

This Claude Code plugin is a port of the Senzing Bootcamp **Kiro Power**
(`docktermj/senzing-bootcamp-kiro-powers`). Improvements usually land in the Kiro repo
first, then get migrated here.

- The last-migrated Kiro commit is recorded in [`.sync-state.json`](.sync-state.json).
- Run [`scripts/sync-check.sh`](scripts/sync-check.sh) to see what changed in the Kiro
  Power since that commit, scoped to the content that maps into this plugin.

## Path mapping (Kiro Power -> Claude plugin)

The Kiro payload lives in the Kiro repo's `senzing-bootcamp/` directory (plus `.kiro/hooks/`).

| Kiro Power | Claude plugin | How to translate |
| --- | --- | --- |
| `senzing-bootcamp/POWER.md` (frontmatter) | `plugins/senzing-bootcamp/.claude-plugin/plugin.json` | Map manifest fields (name, version, description). |
| `senzing-bootcamp/steering/module-*.md` | `plugins/senzing-bootcamp/skills/module-*/SKILL.md` | `inclusion:` frontmatter -> skill `description`; resolve `#[[file:]]` refs into the skill body or links. |
| `senzing-bootcamp/steering/onboarding-*.md` | `plugins/senzing-bootcamp/skills/bootcamp-onboarding/SKILL.md` | Same as modules. |
| `senzing-bootcamp/steering/agent-instructions.md` (`inclusion: always`) | Skill ground rules / plugin instructions | Fold always-on rules into the onboarding skill's ground-rules section. |
| `.kiro/hooks/*.json` (v1) + steering hook logic | `plugins/senzing-bootcamp/hooks/hooks.json` + `scripts/` | Kiro `trigger`/`matcher`/`action` -> Claude `event`/`matcher`/`type`. Kiro `action.type: "agent"` -> Claude `type: "prompt"` or `"agent"`. Deterministic gates -> `type: "command"` scripts. |
| `senzing-bootcamp/mcp.json` | `plugins/senzing-bootcamp/.mcp.json` | Drop Kiro-only keys (`autoApprove`, `disabled`, `disabledTools`); those belong in Claude Code settings, not `.mcp.json`. |
| `senzing-bootcamp/config/*.yaml` | plugin config referenced by skills | Port as needed; keep project-relative. |

### Not migrated (Kiro-specific / dev infrastructure)

- `.kiro/specs/**` (Kiro spec-driven dev artifacts)
- `.kiro/steering/**` (repo-development steering, not bootcamp payload)
- `tests/**`, `pyproject.toml`, `hypothesis_profiles.py` (Kiro repo's Python test harness)

## Migration procedure

1. Run `scripts/sync-check.sh` to list changed content since the last sync.
2. For each changed path, port the change per the mapping table above.
3. Smoke-test the plugin (install locally, run `/start-bootcamp`).
4. Update `syncedCommit` / `syncedCommitShort` / `syncedDate` in `.sync-state.json` to the
   Kiro HEAD you just migrated from.
5. Bump the plugin `version` in `plugin.json` if the change is user-facing.
6. Commit (mention the migrated Kiro commit in the message).
