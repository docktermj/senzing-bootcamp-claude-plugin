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
