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

**Status:** the plugin is at v0.2.0. The full Core track is ported and wired end to end:
onboarding preface (spec-ordered), Modules 1-7 (ascending numeric order), a shared
module-completion flow (per-module recap accumulation + end-of-module summary), graduation
(banner + always-on recap PDF trophy + `production/` project), and any-time feedback capture.
Advanced Topics (Modules 8-11), the deployment/language reference skills, and most Kiro Python
helper scripts remain unported. The Kiro payload has 116 steering files, 29+ hooks, ~100 Python
scripts, 9 config files, and 10 templates.

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

### Phase 2 - Module 01 (ported: Discover the Business Problem)

- [x] `steering/module-01-business-problem.md` -> `skills/module-01-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-01-phase1-discovery.md` -> `skills/module-01-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-01-phase2-document-confirm.md` -> `skills/module-01-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 02

- [x] `steering/module-02-sdk-setup.md` -> `skills/module-02-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 03

- [x] `steering/module-03-phase1-verification.md` -> `skills/module-03-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-03-phase2-visualization.md` -> `skills/module-03-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-03-phase3-report-close.md` -> `skills/module-03-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-03-system-verification.md` -> `skills/module-03-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-03-visualization-api-reference.md` -> `skills/module-03-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 04

- [x] `steering/module-04-data-collection.md` -> `skills/module-04-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 05

- [x] `steering/module-05-data-quality-mapping.md` -> `skills/module-05-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-05-phase1-quality-assessment.md` -> `skills/module-05-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-05-phase2-data-mapping.md` -> `skills/module-05-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-05-phase3-test-load.md` -> `skills/module-05-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 06

- [x] `steering/module-06-data-processing.md` -> `skills/module-06-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-06-phaseA-build-loading.md` -> `skills/module-06-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-06-phaseB-load-first-source.md` -> `skills/module-06-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-06-phaseC-multi-source.md` -> `skills/module-06-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-06-phaseD-validation.md` -> `skills/module-06-<slug>/SKILL.md` (+ phase supporting files)

### Phase 3 - Module 07

- [x] `steering/module-07-phase1-query-visualize.md` -> `skills/module-07-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-07-phase2-discover.md` -> `skills/module-07-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-07-phase2b-discover.md` -> `skills/module-07-<slug>/SKILL.md` (+ phase supporting files)
- [x] `steering/module-07-query-visualize-discover.md` -> `skills/module-07-<slug>/SKILL.md` (+ phase supporting files)

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

- [~] `steering/completion-summary-offer.md` -> folded into the graduation skill (recap + report)
- [x] `steering/graduation.md` -> `skills/graduation/SKILL.md` + `scripts/generate_recap_pdf.py`
- [x] `steering/module-completion-artifacts.md` -> `skills/bootcamp-onboarding/module-completion.md` (recap accumulation)
- [~] `steering/module-completion-error-handling.md` -> non-blocking rules folded into `module-completion.md`
- [x] `steering/module-completion-next-steps.md` -> end-of-module summary in `module-completion.md`
- [x] `steering/module-completion-track.md` -> track-completion + graduation offer in `module-completion.md`
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
- [x] `steering/feedback-workflow.md` -> `skills/bootcamp-onboarding/feedback.md` + `/bootcamp-feedback` command + `feedback-capture.sh` hook
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
- [~] `hooks/review-bootcamper-input.json` -> `UserPromptSubmit` -> `scripts/feedback-capture.sh` (feedback + verbosity triggers; Q&A-log/status/repeat parts deferred)
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

---

# Phase 2 status (Module 1: Discover the Business Problem)

**Done.** Replaced the incorrect `module-01-first-resolution` placeholder with a faithful port
of the real Module 1:

- `skills/module-01-business-problem/SKILL.md` - router (intro, before/after, error handling,
  phase manifest, ground-rules reference).
- `skills/module-01-business-problem/phase1-discovery.md` - steps 1-9 (git init, privacy
  reminder, design-pattern gallery, three discovery paths, Business Case Offer + CORD-via-MCP
  sourcing, six-category inference, record-count/license guidance 6a-6e, gap-filling 7a-7d,
  integration, deployment target).
- `skills/module-01-business-problem/phase2-document-confirm.md` - steps 10-18 (visuals,
  scenario ID, `docs/business_problem.md` template, README update, solution approach, value
  restatement, confirmation, stakeholder summary, transition to Module 4).

**Translation decisions:** `🛑`/`⛔` kept internal (rendered as italic "end the turn" directives,
not glyphs); `#[[file:]]` replaced with relative references; license in-flow path reconciled
(dropped the Kiro `disabledTools`/`mcp.json` edit; check `submit_feedback` via
`get_capabilities` instead). Referenced-but-not-yet-ported dependencies noted inline:
`business_case_offer.py` (scenario invariants validated directly), `templates/
stakeholder_summary.md`, `design-patterns.md`, `common-pitfalls.md`.

**Note:** Module 1 hands off to **Module 2**; the whole chain runs in strict ascending order
(1 → 2 → 3 → 4 → 5 → 6 → 7). An earlier Kiro porting artifact skipped straight to Module 4;
that was corrected in v0.2.0 (below).

**Runtime-untested:** not yet exercised via a local plugin install.

---

# Phase 3 status (Modules 2-7 ported, Core track complete)

**Done.** All Core Bootcamp modules are now ported (one skill per module, multi-phase modules
split into router + phase files, mirroring Module 1):

- `module-02-sdk-setup/` (single file) - SDK Installation and Configuration.
- `module-03-system-verification/` (router + phase1-verification + phase2-visualization +
  phase3-report-close + visualization-api-reference).
- `module-04-data-collection/` (single file) - Identify and Collect Data Sources.
- `module-05-data-quality-mapping/` (router + phase1-quality-assessment + phase2-data-mapping +
  phase3-test-load).
- `module-06-data-processing/` (router + phaseA-build-loading + phaseB-load-first-source +
  phaseC-multi-source + phaseD-validation; step numbering reconciled to a clean sequence).
- `module-07-query-visualize-discover/` (router + phase1-query-visualize + phase2-discover +
  phase2b-discover) - end of the Core track.

Ported in parallel (one subagent per module) from Kiro Power commit 2378811. Same translation
rules as Module 1: dropped `inclusion:` frontmatter; `🛑`/`⛔` kept internal; `#[[file:]]` ->
relative refs; config/ conventions; MCP tool routing reconciled to the tools the current
Senzing MCP server exposes (entity query/why/how -> generated SDK code via get_sdk_reference +
sdk_guide; counts -> reporting_guide); no direct SQL. Em dashes normalized to colons across all
skill docs (including Module 1) to match the house style.

**Reconciliations / unported deps flagged inline in the module files** (all on the checklist
for later phases): Kiro `scripts/*.py` helpers (validators, progress/volume utils, recap and
comparison scripts), `templates/*`, `common-pitfalls.md`, `design-patterns.md`,
`visualization-guide.md` / `visualization-web-service.md`, `data-processing-reference.md`, and
the per-module `docs/modules/MODULE_*.md` user references.

**Runtime-untested (all 7 modules).** Nothing has been exercised via a local plugin install.
This remains the top follow-up before relying on the bootcamp end to end.

**Advanced Topics (Modules 8-11) not started** - still on the checklist.

---

# Hook gating fix (post-port)

**Problem found live:** the `Stop` hook (prompt type) and the `PreToolUse` write-gate fired in
EVERY Claude Code session once the plugin was installed, not just during a bootcamp. The Stop
hook nagged for a 👉 closing question on unrelated turns; the write-gate would block legitimate
`/tmp` writes in non-bootcamp work.

**Fix:** gate both on a deterministic bootcamp-active signal instead of model judgment. A
bootcamp is "active" when `config/bootcamp_progress.json` exists in the working directory.

- `Stop` hook converted from `prompt` type to a `command` script (`scripts/stop-nudge.sh`):
  emits nothing unless a bootcamp is active; when active, blocks the turn once
  (`decision: block`) to request a forgotten closing 👉 question. It returns success while
  `stop_hook_active` is true (so it can never loop on its own continuation) and stays silent
  when the last assistant turn already ended with a 👉 question.
- `scripts/write-gate.sh`: no-ops (allows the write) unless a bootcamp is active.

This keeps the plugin from altering unrelated sessions. Verified both silent/allow outside a
bootcamp and active inside one.

---

# Graduation, completion, feedback, and preface (v0.2.0)

This round closed the largest remaining gaps against `specs/migrate-kiro-power.md`.

**Module ordering fixed to strict ascending order.** Module 1 previously transitioned straight
to Module 4 (a Kiro porting artifact). The spec, and the Kiro `module-prerequisites` doc
("Modules run in ascending numeric order"), require 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7. Module 1
now hands off to Module 2, and the whole chain runs in order.

**Preface reordered to the spec.** The onboarding preface now follows the spec's sequence:
(1) ENTITY RESOLUTION CONCEPTS banner + description + explore gate, (2) WELCOME banner +
overview, (3) level of detail, (4) track, (5) programming language, (6) any questions.
Previously the programming-language gate ran before the WELCOME banner. Added the missing
"ENTITY RESOLUTION CONCEPTS" banner and a final "any questions" gate.

**Shared module-completion flow.** `skills/bootcamp-onboarding/module-completion.md` is the
port of the Kiro `module-completion*` steering. Every module (1-7) now runs it at its end:
update progress, append a per-module recap section (Information Shared, Questions & Responses,
Actions Taken, Journal) to `docs/bootcamp_recap.md`, and present the end-of-module summary
(accomplished, files produced, why it matters, what's next). The final module offers graduation.

**Graduation.** `skills/graduation/SKILL.md` + `/graduate` command: GRADUATION banner, recap
reconciliation, always-on recap PDF trophy, and a populated `production/` project (src copy,
`.env.example`, `docker-compose.yml`, `.gitignore`, production README, migration checklist,
graduation report), ending with the guaranteed-recap announcement and the single closing 👉.

**Recap PDF trophy.** `scripts/generate_recap_pdf.py` (bundled, self-contained) renders
`docs/bootcamp_recap.md` -> `docs/bootcamp_recap.pdf`. Tiered strategy: a professionally
designed `fpdf2` render (cover page + per-module pages with the four labeled sections), falling
back to a stdlib-only PDF writer so a valid PDF is ALWAYS produced. Supports `--check` (verify
required sections) and warns non-blockingly on incomplete content. Tested: rich render, stdlib
fallback (fpdf2 shadowed), incomplete module, header-only recap, and missing input.

**Any-time feedback + verbosity.** `skills/bootcamp-onboarding/feedback.md`, the
`/bootcamp-feedback` command, and a `UserPromptSubmit` hook (`scripts/feedback-capture.sh`,
"to capture bootcamp feedback") route feedback and verbosity-change requests anywhere in the
bootcamp. Feedback appends to `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` (note: the
Claude plugin uses `_PLUGIN_` in the filename, not the Kiro `_POWER_`). The hook is gated on an
active bootcamp, so unrelated sessions are untouched.

**Hooks catalog.** `hooks/README.md` documents each hook with its purpose phrased beginning with
"to" (the spec's hook-naming outcome): "to resume an in-progress bootcamp", "to capture bootcamp
feedback", "to keep your files in the project", "to review what you said".

**Deliberately deferred (not in the spec's module-by-module outcomes):** Advanced Topics
(Modules 8-11), the Q&A-transcript / status / repeat parts of the input-review hook, and the
per-module completion certificates. The recap PDF is the spec-required trophy and is complete.

**Runtime-tested:** the recap PDF generator and all four hook scripts were exercised directly
(see above). The conversational flow (onboarding -> modules -> graduation) has not been driven
through a live `claude` session; that end-to-end smoke test remains the top follow-up.

---

# Module 3 visualization: bundled web app (v0.3.0)

**Problem found in a live run:** Module 3's Step 9 asked the agent to hand-write a web server,
`write_html.py`, and four builder modules every run. Being fully model-driven, it was fragile:
the visualization could be skipped or degrade to a static file, so the bootcamper's "wow moment"
(a dynamic web app showing the resolved TruthSet) sometimes never appeared.

**Fix (same pattern as the recap PDF):** ship a bundled, tested, self-contained visualization
web app and invoke it deterministically.

- `scripts/senzing_viz_server.py` (bundled): builds an entity model from the loaded records
  (one `get_entity_by_record_id` call per record with `SZ_ENTITY_DEFAULT_FLAGS`, which includes
  all relations, so nodes AND relationship edges come from real ER, never direct SQL), then
  serves a live D3 v7 web app (`/` + `/api/stats`, `/api/graph`, `/api/merges`, `/api/search`)
  with four tabs (Entity Graph, Record Merges, Merge Statistics, Search/Probe). `--snapshot`
  writes a self-contained standalone HTML (data embedded via a `fetch` shim) that renders with no
  server; `--no-serve` builds the snapshot and exits. The graph's `source_entity_id`/
  `target_entity_id` -> `source`/`target` edge-key mapping (a documented silent-failure trap) is
  baked in, correct by construction. Fixed a Senzing lifecycle bug during testing: the factory
  must be retained for the server's lifetime or the engine is destroyed and `/api/search` fails.
- `skills/module-03-system-verification/phase2-visualization.md` rewritten: Step 9 now (9.2)
  always writes the standalone snapshot first (the guaranteed deliverable), then (9.3) starts the
  live app, (9.4) verifies the four endpoints, and (9.5) gives the guided tour. Hand-building is
  demoted to an explicit fallback for when the bundled app cannot run.
- `phase3-report-close.md` completion gate strengthened: Module 3 cannot complete unless the
  snapshot artifact physically exists on disk (a progress checkpoint alone is not sufficient), so
  the visualization is guaranteed to have happened.

**Runtime-tested (live, against the real Senzing engine on this machine):** loaded the 159-record
TruthSet, built the model (159 records -> 84 entities, 55 merged, 17 cross-source, 71
relationships), served all four endpoints (verified with curl), rendered the live D3 page and the
standalone snapshot (verified with headless-Chrome screenshots), and confirmed `/api/search`
returns resolved entities with match keys and resolution rules.
