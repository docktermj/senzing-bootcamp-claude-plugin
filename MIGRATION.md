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

---

# Porting roadmap (Kiro Power -> Claude plugin)

**Status:** the plugin is a v0.1.0 scaffold. Onboarding is condensed and only a simplified
Module 1 exists. The Kiro payload has 116 steering files, 29+ hooks, ~100 Python scripts,
9 config files, and 10 templates. The bulk of the curriculum is not yet ported.

Each phase below is ordered so the plugin stays usable end-to-end for the modules covered.

- **Phase 1 - Onboarding + core agent parity.** Port the onboarding flow and always-on agent
  rules so the guided experience (the leading-question protocol, MCP-only rules, file
  placement, progress tracking) matches Kiro. Deliverable: `/start-bootcamp` runs a faithful
  onboarding and can hand off to modules.
- **Phase 2 - Module 1 full port.** Replace the simplified sample with the real Module 1
  (business problem -> discovery -> document/confirm), plus its completion artifacts and hooks.
- **Phase 3 - Modules 2 through 11.** One skill per module in curriculum order; multi-phase
  modules keep their phases as supporting files in the skill directory. Port each module's
  steering + module-specific hooks + config together.
- **Phase 4 - Runtime support.** Session resume/handoff, mistake recovery, track switching,
  completion/graduation artifacts, and the runtime-candidate scripts (progress dashboard,
  recap/transcript/certificate generation, backup/restore, rollback).
- **Phase 5 - Deployment + language guides + reference.** The 5 deployment guides, 5 language
  guides, and cross-cutting reference material, delivered as on-demand reference skills.

**Cross-cutting, port alongside the phase that first needs them:** hooks (registries ->
`hooks/hooks.json`), config files, templates, and slash commands.

## Decisions to make while porting

- **Skill granularity:** one skill per module. Multi-phase modules (e.g. Module 6 A-D) keep
  phases as supporting `.md` files in the skill dir, referenced from `SKILL.md`.
- **Python scripts:** decide per script whether to (a) bundle the Python and invoke it from a
  skill/hook, or (b) reimplement as a skill instruction. Many `scripts/*.py` are Kiro-repo
  dev/build tooling (validators, doc generators, hook installers) and should NOT be ported as
  features; see the scripts checklist below for runtime candidates vs dev tooling.
- **Hooks:** Kiro `action.type: "agent"` maps to Claude `type: "prompt"`/`"agent"`;
  deterministic gates map to `type: "command"` scripts.

## Per-file checklist

Legend: `[ ]` not started, `[~]` partial, `[x]` done. Update as you migrate.

### Phase 1 - Onboarding + core agent parity

- [x] `steering/onboarding-flow.md` -> `skills/bootcamp-onboarding/` (SKILL.md + supporting files)
- [x] `steering/onboarding-phase1b-intro-language.md` -> `skills/bootcamp-onboarding/` (SKILL.md + supporting files)
- [x] `steering/onboarding-phase2-track-setup.md` -> `skills/bootcamp-onboarding/` (SKILL.md + supporting files)
- [x] `steering/agent-behavior-rules.md` -> onboarding skill ground-rules / plugin instructions
- [ ] `steering/agent-context-management.md` -> onboarding skill ground-rules / plugin instructions  _NOT ported (Phase 1): Kiro steering load/unload model; N/A in Claude Code (compaction handles context)_
- [x] `steering/agent-instructions.md` -> onboarding skill ground-rules / plugin instructions
- [ ] `steering/complexity-estimator.md` -> onboarding skill ground-rules / plugin instructions  _NOT ported (Phase 1): deferred to Module 4/5 content_
- [~] `steering/conversation-examples.md` -> onboarding skill ground-rules / plugin instructions
- [~] `steering/conversation-protocol.md` -> onboarding skill ground-rules / plugin instructions
- [x] `steering/entity-resolution-intro.md` -> onboarding skill ground-rules / plugin instructions
- [x] `steering/file-placement.md` -> onboarding skill ground-rules / plugin instructions
- [ ] `steering/inline-status.md` -> onboarding skill ground-rules / plugin instructions  _NOT ported (Phase 1): deferred (status command) - small, revisit_
- [ ] `steering/mcp-response-caching.md` -> onboarding skill ground-rules / plugin instructions  _NOT ported (Phase 1): Kiro agent-executed file cache; revisit if needed_
- [~] `steering/mcp-tool-decision-tree.md` -> onboarding skill ground-rules / plugin instructions
- [x] `steering/mcp-usage-reference.md` -> onboarding skill ground-rules / plugin instructions
- [~] `steering/module-prerequisites.md` -> onboarding skill ground-rules / plugin instructions
- [~] `steering/module-transitions.md` -> onboarding skill ground-rules / plugin instructions
- [ ] `steering/phase-loading-guide.md` -> onboarding skill ground-rules / plugin instructions  _NOT ported (Phase 1): Kiro steering sub-file load/unload; N/A in Claude Code_
- [~] `steering/project-structure.md` -> onboarding skill ground-rules / plugin instructions
- [~] `steering/skip-step-protocol.md` -> onboarding skill ground-rules / plugin instructions
- [ ] `steering/steering-index.yaml` -> onboarding skill ground-rules / plugin instructions
- [~] `steering/verbosity-control.md` -> onboarding skill ground-rules / plugin instructions

### Phase 2 - Module 01 (currently PARTIAL: simplified sample only)

- [ ] `steering/module-01-business-problem.md` -> `skills/module-01-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-01-phase1-discovery.md` -> `skills/module-01-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-01-phase2-document-confirm.md` -> `skills/module-01-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 02

- [ ] `steering/module-02-sdk-setup.md` -> `skills/module-02-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 03

- [ ] `steering/module-03-phase1-verification.md` -> `skills/module-03-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-03-phase2-visualization.md` -> `skills/module-03-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-03-phase3-report-close.md` -> `skills/module-03-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-03-system-verification.md` -> `skills/module-03-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-03-visualization-api-reference.md` -> `skills/module-03-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 04

- [ ] `steering/module-04-data-collection.md` -> `skills/module-04-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 05

- [ ] `steering/module-05-data-quality-mapping.md` -> `skills/module-05-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-05-phase1-quality-assessment.md` -> `skills/module-05-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-05-phase2-data-mapping.md` -> `skills/module-05-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-05-phase3-test-load.md` -> `skills/module-05-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 06

- [ ] `steering/module-06-data-processing.md` -> `skills/module-06-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-06-phaseA-build-loading.md` -> `skills/module-06-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-06-phaseB-load-first-source.md` -> `skills/module-06-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-06-phaseC-multi-source.md` -> `skills/module-06-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-06-phaseD-validation.md` -> `skills/module-06-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 07

- [ ] `steering/module-07-phase1-query-visualize.md` -> `skills/module-07-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-07-phase2-discover.md` -> `skills/module-07-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-07-phase2b-discover.md` -> `skills/module-07-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-07-query-visualize-discover.md` -> `skills/module-07-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 08

- [ ] `steering/module-08-performance.md` -> `skills/module-08-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-08-phaseA-requirements.md` -> `skills/module-08-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-08-phaseB-benchmarking.md` -> `skills/module-08-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-08-phaseC-optimization.md` -> `skills/module-08-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 09

- [ ] `steering/module-09-phaseA-assessment.md` -> `skills/module-09-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-09-phaseB-hardening.md` -> `skills/module-09-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-09-security.md` -> `skills/module-09-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 10

- [ ] `steering/module-10-monitoring.md` -> `skills/module-10-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-10-phaseA-setup.md` -> `skills/module-10-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-10-phaseB-operations.md` -> `skills/module-10-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 11

- [ ] `steering/module-11-deployment.md` -> `skills/module-11-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-11-phase1-packaging.md` -> `skills/module-11-<slug>/SKILL.md` (+ phase supporting files)
- [ ] `steering/module-11-phase2-deploy.md` -> `skills/module-11-<slug>/SKILL.md` (+ phase supporting files)

### Phase 2/3 support - Module completion & graduation

- [ ] `steering/completion-summary-offer.md` -> `skills/` completion flow + runtime scripts
- [ ] `steering/graduation.md` -> `skills/` completion flow + runtime scripts
- [ ] `steering/module-completion-artifacts.md` -> `skills/` completion flow + runtime scripts
- [ ] `steering/module-completion-error-handling.md` -> `skills/` completion flow + runtime scripts
- [ ] `steering/module-completion-next-steps.md` -> `skills/` completion flow + runtime scripts
- [ ] `steering/module-completion-track.md` -> `skills/` completion flow + runtime scripts
- [ ] `steering/module-completion.md` -> `skills/` completion flow + runtime scripts

### Phase 4 - Runtime support (steering)

- [ ] `steering/recovery-from-mistakes.md` -> `skills/session-resume/` + `hooks/` + scripts
- [ ] `steering/session-handoff.md` -> `skills/session-resume/` + `hooks/` + scripts
- [ ] `steering/session-resume-phase2-mapping.md` -> `skills/session-resume/` + `hooks/` + scripts
- [ ] `steering/session-resume-phase2-setup-recovery.md` -> `skills/session-resume/` + `hooks/` + scripts
- [ ] `steering/session-resume-phase2-state-repair.md` -> `skills/session-resume/` + `hooks/` + scripts
- [ ] `steering/session-resume.md` -> `skills/session-resume/` + `hooks/` + scripts
- [ ] `steering/track-switching.md` -> `skills/session-resume/` + `hooks/` + scripts

### Phase 5 - Deployment guides

- [ ] `steering/deployment-aws.md` -> `skills/deploy-<provider>/` (on-demand reference skill)
- [ ] `steering/deployment-azure.md` -> `skills/deploy-<provider>/` (on-demand reference skill)
- [ ] `steering/deployment-gcp.md` -> `skills/deploy-<provider>/` (on-demand reference skill)
- [ ] `steering/deployment-kubernetes.md` -> `skills/deploy-<provider>/` (on-demand reference skill)
- [ ] `steering/deployment-onpremises.md` -> `skills/deploy-<provider>/` (on-demand reference skill)

### Phase 5 - Language guides

- [ ] `steering/lang-csharp.md` -> `skills/lang-<language>/` (on-demand reference skill)
- [ ] `steering/lang-java.md` -> `skills/lang-<language>/` (on-demand reference skill)
- [ ] `steering/lang-python.md` -> `skills/lang-<language>/` (on-demand reference skill)
- [ ] `steering/lang-rust.md` -> `skills/lang-<language>/` (on-demand reference skill)
- [ ] `steering/lang-typescript.md` -> `skills/lang-<language>/` (on-demand reference skill)

### Phase 5 - Reference / cross-cutting

- [ ] `steering/cloud-provider-setup.md` -> reference skill / folded into relevant module skill
- [ ] `steering/common-pitfalls.md` -> reference skill / folded into relevant module skill
- [ ] `steering/data-lineage.md` -> reference skill / folded into relevant module skill
- [ ] `steering/data-processing-reference.md` -> reference skill / folded into relevant module skill
- [ ] `steering/design-patterns.md` -> reference skill / folded into relevant module skill
- [ ] `steering/environment-setup.md` -> reference skill / folded into relevant module skill
- [ ] `steering/feedback-workflow.md` -> reference skill / folded into relevant module skill
- [ ] `steering/lessons-learned.md` -> reference skill / folded into relevant module skill
- [ ] `steering/qa-transcript.md` -> reference skill / folded into relevant module skill
- [ ] `steering/security-privacy.md` -> reference skill / folded into relevant module skill
- [ ] `steering/troubleshooting-commands.md` -> reference skill / folded into relevant module skill
- [ ] `steering/troubleshooting-decision-tree.md` -> reference skill / folded into relevant module skill
- [ ] `steering/uat-framework.md` -> reference skill / folded into relevant module skill
- [ ] `steering/visualization-guide.md` -> reference skill / folded into relevant module skill
- [ ] `steering/visualization-web-service.md` -> reference skill / folded into relevant module skill
- [ ] `steering/whats-new.md` -> reference skill / folded into relevant module skill

### Cross-cutting - Hook registry steering (-> hooks/hooks.json)

- [ ] `steering/hook-architecture.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-critical.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-01.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-02.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-03.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-04.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-05.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-06.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-07.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-08.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-09.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-10.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-11.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry-module-any.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)
- [ ] `steering/hook-registry.md` -> informs `hooks/hooks.json` + hook scripts (not a skill)

### Cross-cutting - Slash commands

- [ ] `steering/slash-backup-project.md` -> `commands/backup-project.md`
- [ ] `steering/slash-commonmark-validation.md` -> `commands/commonmark-validation.md`
- [ ] `steering/slash-git-commit.md` -> `commands/git-commit.md`

### Cross-cutting - Payload hooks (senzing-bootcamp/hooks/*.json)

- [ ] `hooks/analyze-after-mapping.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/ask-bootcamper.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/backup-before-load.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/code-style-check.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/data-quality-check.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/deployment-phase-gate.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/enforce-critical-artifacts.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/enforce-gate-on-stop.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/enforce-mandatory-gate.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/enforce-mapping-spec.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/enforce-visualization-offers.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/error-recovery-context.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/gate-module3-visualization.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/module-completion-celebration.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/review-bootcamper-input.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/run-tests-after-change.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/security-scan-on-save.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/session-log-events.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/validate-alert-config.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/validate-benchmark-results.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/validate-business-problem.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/validate-data-files.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/verify-demo-results.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/verify-generated-code.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/verify-sdk-setup.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)
- [ ] `hooks/write-policy-gate.json` -> entry in `hooks/hooks.json` (translate trigger/matcher/action)

### Cross-cutting - Config files (senzing-bootcamp/config/)

- [ ] `config/bootcamp_preferences.yaml.example` -> plugin config referenced by skills
- [ ] `config/bootcamp_progress.json.example` -> plugin config referenced by skills
- [ ] `config/data_sources.yaml.example` -> plugin config referenced by skills
- [ ] `config/er_baseline_vendors.json.example` -> plugin config referenced by skills
- [ ] `config/example-coverage.yaml` -> plugin config referenced by skills
- [ ] `config/fallback_sources.yaml` -> plugin config referenced by skills
- [ ] `config/governance-rules.yaml` -> plugin config referenced by skills
- [ ] `config/module-artifacts.yaml` -> plugin config referenced by skills
- [ ] `config/module-dependencies.yaml` -> plugin config referenced by skills

### Cross-cutting - Templates (senzing-bootcamp/templates/)

- [ ] `templates/data_collection_checklist.md` -> `templates/` used by completion/artifact skills
- [ ] `templates/deployment_plan.md` -> `templates/` used by completion/artifact skills
- [ ] `templates/lessons_learned.md` -> `templates/` used by completion/artifact skills
- [ ] `templates/module-steering-template.md` -> `templates/` used by completion/artifact skills
- [ ] `templates/monitoring_runbook.md` -> `templates/` used by completion/artifact skills
- [ ] `templates/performance_report.md` -> `templates/` used by completion/artifact skills
- [ ] `templates/security_checklist.md` -> `templates/` used by completion/artifact skills
- [ ] `templates/stakeholder_summary.md` -> `templates/` used by completion/artifact skills
- [ ] `templates/team.yaml.example` -> `templates/` used by completion/artifact skills
- [ ] `templates/transformation_lineage.md` -> `templates/` used by completion/artifact skills
- [ ] `templates/uat_test_cases.md` -> `templates/` used by completion/artifact skills

### Phase 4 - Scripts: RUNTIME candidates (decide: bundle Python vs reimplement)

- [ ] `scripts/backup_project.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/baseline_status.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/business_case_offer.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/check_database.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/compare_results.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/completion_artifacts.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/data_sources.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/detect_license_limit.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/ensure_graduation_artifacts.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/export_results.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/fetch_fallback_truthset.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/generate_artifact_inventory.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/generate_completion_summary.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/generate_directory_index.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/generate_graduation_certificate.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/generate_recap_pdf.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/generate_recap_pdf_inline.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/generate_standalone_demo.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/generate_transcript.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/preferences_utils.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/progress_dashboard.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/progress_utils.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/recap_html_render.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/recap_pdf_render.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/reconcile_transcript.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/record_count_backfill.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/record_export.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/repair_progress.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/restore_project.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/rollback_module.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/session_logger.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/status.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/track_switcher.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/visualize_dependencies.py` -> runtime feature (skill/hook-invoked)
- [ ] `scripts/volume_utils.py` -> runtime feature (skill/hook-invoked)

### Scripts: DEV/BUILD tooling (review, most likely NOT ported)

- [ ] `scripts/analyze_sessions.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/answer_binding.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/assess_entry_point.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/bootcamp_analytics.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/capture_hook_safeguard.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/check_cord_readiness.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/compose_hook_prompts.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/cord_metadata.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/eval_conversations.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/example_coverage_report.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/fpdf2_preflight.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/generate_docs_index.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/generate_power_docs.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/generate_spec_catalog.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/hook_matcher.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/hook_prompt_fragments.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/hook_renames.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/install_hooks.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/lint_steering.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/load_time_warning.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/log_write_event.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/mcp_tool_inventory.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/measure_steering.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/merge_feedback.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/migrate_hooks.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/normalize_markdown.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/optimize_steering.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/organize_mapping_files.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/parse_business_problem.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/preflight.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/run_bundled_script.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/scan_brittle_assertions.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/split_steering.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/sync_hook_registry.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/team_config_validator.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/team_dashboard.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/test_dashboard.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/test_hooks.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/triage_feedback.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/update_readme_index.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_behavior_rules.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_commonmark.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_completion_artifacts.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_data_files.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_dependencies.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_doc_references.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_governance_rules.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_handoff_summary.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_links.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_mandatory_gates.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_module.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_no_legacy_hooks.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_power.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_preferences_ci.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_prerequisites.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_progress_ci.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/validate_yaml_schemas.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/verbosity.py` -> dev tooling; port only if a plugin build/CI needs it
- [ ] `scripts/version.py` -> dev tooling; port only if a plugin build/CI needs it

---

# Phase 1 status (onboarding + core agent parity)

**Done.** The `bootcamp-onboarding` skill now ports the onboarding flow and core agent rules:

- `skills/bootcamp-onboarding/SKILL.md` - entry + fresh-vs-resume + sequence.
- `skills/bootcamp-onboarding/onboarding-flow.md` - steps 0-7 (MCP health check, setup, ER
  intro, language gate, welcome + verbosity, track gate, hand off to Module 1).
- `skills/bootcamp-onboarding/ground-rules.md` - always-apply rules (👉 conversation protocol,
  mandatory gates, MCP-first invariant, no-SQL, file placement, progress/state, verbosity,
  module banners, closing questions). Every module skill should load this file.
- `skills/bootcamp-onboarding/entity-resolution-intro.md` - ER intro with MCP-sourced facts and
  the exploration gate.

**Translation decisions applied:**

- Adopted Kiro `config/` conventions (`config/bootcamp_progress.json`,
  `config/bootcamp_preferences.yaml`); updated the session-start hook, `/start-bootcamp`
  command, and Module 1 skill to match (replaced the scaffold's `.bootcamp/`).
- Dropped the Kiro `createHook` / hook-install onboarding step: hooks ship with the plugin.
- `🛑 STOP` / `⛔ MANDATORY GATE` kept as internal, never-rendered directives.
- Reconciled MCP tool routing to the tools the current Senzing MCP server actually exposes;
  entity-query operations go through generated SDK code (`get_sdk_reference` + `sdk_guide`)
  rather than direct query tools.

**Condensed (marked `[~]`), full port later:** conversation-protocol (385 lines -> core rules),
conversation-examples, project-structure (full tree), verbosity-control (5-category system),
mcp-tool-decision-tree, skip-step-protocol, module-prerequisites (gate table),
module-transitions (banner/journey-map ported; quality-loop and sub-step convention pending).

**Deliberately not ported in Phase 1:** agent-context-management and phase-loading-guide (Kiro
steering load/unload model; Claude Code manages context via compaction), mcp-response-caching
(Kiro agent-executed file cache), inline-status (small; revisit), complexity-estimator
(deferred to Module 4/5).

**Runtime-untested:** the onboarding has not been exercised by installing the plugin and running
`/start-bootcamp`. Smoke-test before considering Phase 1 closed.
