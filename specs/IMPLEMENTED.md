# Implemented Specs

Record of specs under `specs/` that have been implemented. This file is the
**source of truth** for the `implement-spec` skill: a spec is considered done
**iff** it has a `## <name>` heading below whose text matches the spec's
filename without the `.md` suffix.

Entries are newest first. Do not delete history; append or update in place.

<!-- New entries go directly below this line. Format:

## <spec-name>

- **Implemented:** YYYY-MM-DD
- **Files changed:** `path/one`, `path/two`
- **Summary:** <what was done and how the acceptance criteria were satisfied>
- **Commit:** <hash, or "uncommitted">

-->

## cross-platform-hook-execution

- **Implemented:** 2026-07-15
- **Files changed:** `plugins/senzing-bootcamp/hooks/hooks.json`, `plugins/senzing-bootcamp/hooks/README.md`; **added** `plugins/senzing-bootcamp/scripts/{session-start,feedback-capture,write-gate,stop-nudge}.py`; **removed** the four corresponding `.sh` scripts.
- **Summary:** Removed the hooks' shell dependency entirely (spec Option 2, "make the hooks portable, avoiding a hard bash dependency") by porting all four hooks from POSIX-sh to **Python** and invoking them in Claude Code **exec form** (`{"command":"python3","args":["${CLAUDE_PLUGIN_ROOT}/scripts/<hook>.py"]}`). Authoritative Claude Code doc research established that exec form spawns the interpreter **directly with no shell on any platform** (documented), and that stdin, `${CLAUDE_PLUGIN_ROOT}` substitution in `args`, and exit-code/stdout/stderr semantics are all identical across forms — so exec-form Python eliminates the Windows "needs Git Bash/WSL" requirement that a shell-form (`.sh`) hook has. Python is **not a new dependency**: the bootcamp already requires `python3` (Module 3's always-shown viz server `senzing_viz_server.py` and the graduation recap `generate_recap_pdf.py`). Native `json` parsing also made `write-gate`/`stop-nudge` cleaner and more robust than the prior grep/sed extraction; hook *behavior* (messages, exit codes, gates) is preserved verbatim. `hooks/README.md` rewritten to document the exec-form/Python model and per-platform prerequisites (`python3` on PATH; the one caveat — Claude Code does not guarantee the `python3` command name on Windows, matching the rest of the plugin's `python3` convention). Verified: `hooks.json` valid JSON; `py_compile` clean; all four hooks pass their behavior scenarios via the exact `python3 <script.py>` exec-form invocation — write-gate allows in-project (relative/absolute), blocks system-temp/Downloads/`%TEMP%`/`$TMPDIR`/AKIA-key/PEM-marker and fails open on unparseable input; stop-nudge honors all three gates (stop_hook_active, no-bootcamp, 👉-already-pending) and blocks once otherwise; session-start/feedback-capture emit/stay-silent correctly; all hooks no-op outside a bootcamp.
- **Note:** Superseded the initial in-session attempt (explicit `sh "<path>"` + `bash`→`sh` shebangs) after the maintainer asked whether Python could cover *all* platforms — it can, and better, because exec-form Python needs no shell at all on Windows.
- **Commit:** uncommitted

## interaction-or-questions

- **Implemented:** 2026-07-15
- **Files changed:** `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md`, `plugins/senzing-bootcamp/skills/graduation/SKILL.md`, `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md`, `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md`, `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md`, `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md`, `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md`, `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`, `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`, `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md`, `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md`, `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md`, `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md`
- **Summary:** Systemic cleanup of "or"-joined 👉 questions, enforcing INV-009 and the `ground-rules.md:22-24` "neutral lead + numbered list" pattern (reference model: `onboarding-flow.md`). The spec's enumerated line list had drifted, so I re-derived the full current set with `grep -rn '👉.* or ' skills/`. Converted every multi-choice question to a neutral lead ending "… Reply with a number:" plus a numbered list (module-01 license/record-type/outcome/deploy, module-02 OS/license-form/license-path/database, module-04 load-choice, module-05 quality-gate/mapping-mode/baseline/path questions, module-07 discover transitions, feedback priority, graduation overwrite/merge/abort). Split the compound feedback questions ("what happened, or what would you change?"; "fix or improvement?") into single asks, and reworded noun-phrase "or" questions ("discuss or explore", "team or manager", "add or change", "data sources or systems", the module-03 city parenthetical) to drop "or". Left the two sanctioned exceptions unchanged: `ground-rules.md:21-22` convention text and the module-02 EULA "respond yes or no" answer-format hint. Verified all four acceptance criteria: the criterion-#3 grep over `skills/` now returns only that rule text + the yes/no hint (no multi-choice questions). Also fixed 6 pre-existing `**Label**:` → `**Label:**` markdown violations flagged by the repo's CommonMark hook in the two touched files (`phase1-quality-assessment.md`, `phase2b-discover.md`).
- **Commit:** uncommitted

## migrate-kiro-power

- **Implemented:** 2026-07-15 (verified at outcome level; residuals split into follow-up specs)
- **Files changed:** `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` (preface I4/I5 backfill)
- **Summary:** Verify/backfill audit of the umbrella migration spec against @invariants.md (~50 invariants across 4 groups). Result: SATISFIED ~50, PARTIAL 7, GAP 0 — every enumerated outcome is met (preface, per-module structure, Modules 1–7, graduation, project layout) with no missing referenced files, and Module 3's "always a dynamic web-app truth-set visualization" was confirmed real (`scripts/senzing_viz_server.py` — live ThreadingHTTPServer + D3 force graph + JSON APIs, not a static image). Backfilled the two preface questions (`onboarding-flow.md:114,139`) to a neutral-lead + numbered-list form, removing the "or"-joined choices that violated invariant I5 and the plugin's own `ground-rules.md:22-24`. Recorded as implemented at the outcome level; the 7 residual PARTIALs were split into dedicated follow-up specs rather than blocking the umbrella.
- **Follow-up specs:** `interaction-or-questions.md` (systemic I5/I4 "or" cleanup, ~15+ questions), `module-step-overview.md` (M4), `hook-to-message-convention.md` (Q1), `cross-platform-hook-execution.md` (T1), `doc-consistency-audit.md` (Q2+T4). The transformed→senzing-ready naming (S1) is already tracked in `specs/todo.md`.
- **Commit:** uncommitted (working-tree change to `onboarding-flow.md`)

## stop-hook-issue

- **Implemented:** 2026-07-15
- **Files changed:** `plugins/senzing-bootcamp/scripts/stop-nudge.sh`
- **Summary:** Fixed the Stop-hook loop where the nudge re-fired every turn (re-asking the same "👉 …explore concepts…?" question) until Claude Code's 9x block cap force-ended the turn. The hook now applies three deterministic gates in order: (1) `stop_hook_active == true` → exit 0 immediately — the loop-breaker, so a block never re-fires on the continuation it caused; (2) no `config/bootcamp_progress.json` → exit 0, never touching non-bootcamp sessions; (3) the last assistant turn already ended with a 👉 pointer question (parsed from the transcript) → stay silent, honoring "ask each question once." Only when none short-circuit does it block exactly once to request a single closing question. Verified end-to-end against the spec's repro: a pending 👉 question stays silent (no re-ask), `stop_hook_active=true` is always released, an absent closing question nudges once, and a block→continuation sequence blocks at most once (no loop). Cross-platform (POSIX sh + grep/sed, optional python3 with a documented safe fallback) and language-agnostic per @invariants.md.
- **Commit:** uncommitted (working-tree change to `stop-nudge.sh`, atop `615b9a7`)

## PreToolUseWriteError

- **Implemented:** 2026-07-15
- **Files changed:** `plugins/senzing-bootcamp/scripts/write-gate.sh`
- **Summary:** The write-gate no longer matches `/tmp/` (or `/Downloads/`, `%TEMP%`) as a floating substring in the payload. It now extracts only the target `file_path`, resolves it to an absolute path, and exempts the project directory (CWD-containment) FIRST, then blocks genuine system-temp/Downloads targets — Option 1 from the spec. Verified end-to-end against all acceptance criteria via a project rooted under a `/tmp/`-containing path: project-relative and in-project absolute writes to `config/bootcamp_preferences.yaml` are allowed (no heredoc workaround); genuine `/tmp/` and `~/Downloads/` targets are still blocked; the secret-detection branch still fires; content that merely mentions `/tmp/` is allowed; and an unexpanded Windows `%TEMP%` target is blocked.
- **Commit:** uncommitted (working-tree change to `write-gate.sh`)
