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

## stop-hook-false-positive

- **Implemented:** 2026-07-16
- **Files changed:** `plugins/senzing-bootcamp/scripts/stop-nudge.py`, `plugins/senzing-bootcamp/hooks/README.md`
- **Summary:** Reopened the Stop-hook false-positive that re-asked a closing 👉 question the guide had already asked (the #1, zero-tolerance complaint). Root cause confirmed empirically against **real** bootcamp transcripts in `~/.claude/projects/`: assistant `message.content` is **always** a list (so the string-shape suspect #2 does not occur), but the old Gate 3 keyed only on the *last text-bearing assistant record* — which (a) misses a 👉 that lives in an earlier record of the same multi-record turn (confirmed on 1 real turn: old parser would nudge, new stays silent) and (b) is defeated by the flush/timing race where the final 👉 message is not yet on disk when the Stop hook reads it (suspect #1 — the reason it fired on "nearly every yielding turn" yet looks fine in a completed transcript). Fix, three parts: **(1) hardened detection** — Gate 3 now scans the whole *current turn* (all non-sidechain assistant records since the last real user prompt), handles `content` as a string **and** a list, and blocks ONLY when it can positively read a current turn that has assistant text but no 👉; every undecided case (no transcript path, missing/unreadable file, or a turn whose text is not yet flushed) biases to **silence**, because a missed nudge is far cheaper than a duplicate. **(2) harmless block** — the `decision: block` reason now tells the model to re-read its own last message first and repeat nothing it already asked, so even a residual false block cannot surface as a duplicate 👉 question. **(3) disable switch** — a new opt-out gate honors `SENZING_BOOTCAMP_DISABLE_STOP_NUDGE` (env var) or `disable_stop_nudge: true` (top-level key in `config/bootcamp_preferences.yaml`, parsed line-by-line with no third-party dependency), documented in `hooks/README.md`. Gate 1 (`stop_hook_active`) loop-breaker preserved. Verified end-to-end against two real transcripts (18/18 checks each) by truncating the transcript at genuine turn boundaries to simulate the Stop firing: 5 real 👉-ending turns stay silent (incl. 👉 followed by a numbered option list, and the multi-record blind-spot turn); 4 genuine no-👉 turns nudge exactly once and never loop (`stop_hook_active=true` → silent); env-var and preferences-key disable both quiet it (`disable_stop_nudge: false` does not); non-bootcamp and missing-transcript sessions stay silent. `py_compile` clean; pure Python 3 stdlib, exec form, no shell (INV-052); cross-platform and language-agnostic.
- **Commit:** uncommitted

## enrich-feedback-context

- **Implemented:** 2026-07-15
- **Files changed:** `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md`, `plugins/senzing-bootcamp/scripts/feedback-capture.py`
- **Summary:** Enriched bootcamp-feedback capture so each entry in `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` carries enough context for `feedback-to-specs` to reconstruct the specific situation. Expanded `feedback.md` Step 0 (silent capture) and the Step 3 "Context when reported" template from just current-module + free-text to nine fields: time, plugin version (from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`), module + step (`current_module`/`current_step` from `config/bootcamp_progress.json`), recent 👉 questions and the bootcamper's responses, behind-the-scenes state (active hook/skill/phase/gate), observed problem, expected behavior (per active hooks/skills/`ground-rules.md`), and the expected-vs-actual divergence. Capture is silent (no new 👉 question — INV-005/INV-012), append-only and local-only (INV-010/INV-015), with "Unknown"/"Unavailable" for missing sources (no fabrication). Updated the `feedback-capture.py` hook's injected workflow guidance to name the same enriched capture so hook and skill stay consistent. Verified: `feedback.md` Step 3 lists all nine fields; Step 0 states the silent/no-extra-question/Unknown rules; `feedback-capture.py` `py_compile`-clean and still emits `additionalContext` naming the enriched fields (plugin version, current_step, behind-the-scenes, expected behavior).
- **Commit:** `b2a0f6d`

## hook-to-message-convention

- **Implemented:** 2026-07-15
- **Files changed:** `plugins/senzing-bootcamp/hooks/README.md`
- **Summary:** Resolved the INV-016 ambiguity ("all hooks begin with the word 'to'") by adopting the maintainer-selected **purpose reading** (Option A): the convention applies to each hook's documented **purpose** (the README Purpose column), not the runtime text a hook emits. All four hooks already carry "to …" purposes (to resume / to capture / to keep / to review), so no hook code changed and there is no UX/behavior change. Recorded the interpretation explicitly as a note under the hooks table in `hooks/README.md` — mandating a "to …" purpose entry for every current and future hook, and citing INV-016's own examples ("to process your request", "to review what you said") as evidence for the purpose reading (acceptance criterion #3: recorded in `hooks/README.md`). Verified: all four Purpose rows begin with "to"; the interpretation note is present. Doc-only; cross-platform and language-agnostic. (The hook files are now `.py` after `cross-platform-hook-execution`, so the spec's `write-gate.sh:NN` line references are stale — moot under Option A, which touches no hook code.)
- **Commit:** `0ba39df`

## doc-consistency-audit

- **Implemented:** 2026-07-15
- **Files changed:** `MIGRATION.md`, `specs/INVARIANTS.md` (INV-050 tree + INV-017), `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`
- **Summary:** Reconciled three documentation inconsistencies (INV-003). (1) Fixed the stale `MIGRATION.md` note that said "Module 1 transitions to Module 4" — it now states Module 1 hands off to Module 2 with the chain in strict ascending order 1→…→7, noting the earlier Kiro artifact was corrected in v0.2.0, so the doc no longer contradicts itself. (2) With maintainer confirmation, renamed the feedback file in the INV-050 project-layout tree from `SENZING_BOOTCAMP_POWER_FEEDBACK.md` (a Kiro-heritage typo) to `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`, so INV-050 now matches INV-015 and every read/write in the plugin. (3) Added a `production/` carve-out to the `.md`-under-`docs/` rule in `ground-rules.md:81` (the generated production project legitimately writes `README.md`/`MIGRATION_CHECKLIST.md`/`GRADUATION_REPORT.md` outside `docs/`), and — with maintainer confirmation — added the matching exception to INV-017 so the invariant and the operational rule stay coherent. Both INVARIANTS.md edits are clarifications/corrections of existing invariants (no renumbering, no new IDs). Verified: no remaining Module 1→4 contradiction in `MIGRATION.md`; `INVARIANTS.md` and the plugin are uniformly `_PLUGIN_`; the production/ exception is present in both `ground-rules.md` and INV-017.
- **Out of scope (noted):** the historical `specs/migrate-kiro-power.md` layout snapshot still shows `_POWER_`; left untouched as an implemented-spec record (editing spec content is `feedback-to-specs`' job), and it is not one of this spec's targeted files.
- **Commit:** `f1947bd`

## module-step-overview

- **Implemented:** 2026-07-15
- **Files changed:** `plugins/senzing-bootcamp/skills/module-0{1..7}/SKILL.md` (the `First:` start instruction in all seven Core-track module SKILLs)
- **Summary:** Enforced INV-031 ("at the beginning of each module, enumerate the steps") — which `ground-rules.md:126-128` mandates but each module's own `First:` instruction omitted (it listed only banner, journey map, and before/after framing). Appended the missing element to every module's start instruction so it now reads "…show the module start banner, journey map, before/after framing, **and a brief numbered overview of this module's steps**, before any module work." The wording is identical across all seven modules (module-01 … module-07) and keeps the existing "(per ground-rules)" reference, satisfying the consistency criterion. Verified: all seven `SKILL.md` files contain the new phrase; the sequence matches the `ground-rules.md` order (banner → journey map → before/after → numbered step overview). Doc-only change; trivially cross-platform and language-agnostic.
- **Incidental:** editing `module-04-data-collection/SKILL.md` surfaced pre-existing CommonMark debt flagged by the repo's markdown hook; fixed in the same file to keep it compliant — 8 `**Label**:` → `**Label:**` list-item labels (format list + two blockquoted labels) and 5 MD032 blank-lines-before-lists (the Option A–D blocks and the smaller-slice block). No behavior change.
- **Commit:** `370f906`

## cross-platform-hook-execution

- **Implemented:** 2026-07-15
- **Files changed:** `plugins/senzing-bootcamp/hooks/hooks.json`, `plugins/senzing-bootcamp/hooks/README.md`; **added** `plugins/senzing-bootcamp/scripts/{session-start,feedback-capture,write-gate,stop-nudge}.py`; **removed** the four corresponding `.sh` scripts.
- **Summary:** Removed the hooks' shell dependency entirely (spec Option 2, "make the hooks portable, avoiding a hard bash dependency") by porting all four hooks from POSIX-sh to **Python** and invoking them in Claude Code **exec form** (`{"command":"python3","args":["${CLAUDE_PLUGIN_ROOT}/scripts/<hook>.py"]}`). Authoritative Claude Code doc research established that exec form spawns the interpreter **directly with no shell on any platform** (documented), and that stdin, `${CLAUDE_PLUGIN_ROOT}` substitution in `args`, and exit-code/stdout/stderr semantics are all identical across forms — so exec-form Python eliminates the Windows "needs Git Bash/WSL" requirement that a shell-form (`.sh`) hook has. Python is **not a new dependency**: the bootcamp already requires `python3` (Module 3's always-shown viz server `senzing_viz_server.py` and the graduation recap `generate_recap_pdf.py`). Native `json` parsing also made `write-gate`/`stop-nudge` cleaner and more robust than the prior grep/sed extraction; hook *behavior* (messages, exit codes, gates) is preserved verbatim. `hooks/README.md` rewritten to document the exec-form/Python model and per-platform prerequisites (`python3` on PATH; the one caveat — Claude Code does not guarantee the `python3` command name on Windows, matching the rest of the plugin's `python3` convention). Verified: `hooks.json` valid JSON; `py_compile` clean; all four hooks pass their behavior scenarios via the exact `python3 <script.py>` exec-form invocation — write-gate allows in-project (relative/absolute), blocks system-temp/Downloads/`%TEMP%`/`$TMPDIR`/AKIA-key/PEM-marker and fails open on unparseable input; stop-nudge honors all three gates (stop_hook_active, no-bootcamp, 👉-already-pending) and blocks once otherwise; session-start/feedback-capture emit/stay-silent correctly; all hooks no-op outside a bootcamp.
- **Note:** Superseded the initial in-session attempt (explicit `sh "<path>"` + `bash`→`sh` shebangs) after the maintainer asked whether Python could cover *all* platforms — it can, and better, because exec-form Python needs no shell at all on Windows.
- **Commit:** `7e906e2`

## interaction-or-questions

- **Implemented:** 2026-07-15
- **Files changed:** `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md`, `plugins/senzing-bootcamp/skills/graduation/SKILL.md`, `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md`, `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md`, `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md`, `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md`, `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md`, `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`, `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`, `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md`, `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md`, `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md`, `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md`
- **Summary:** Systemic cleanup of "or"-joined 👉 questions, enforcing INV-009 and the `ground-rules.md:22-24` "neutral lead + numbered list" pattern (reference model: `onboarding-flow.md`). The spec's enumerated line list had drifted, so I re-derived the full current set with `grep -rn '👉.* or ' skills/`. Converted every multi-choice question to a neutral lead ending "… Reply with a number:" plus a numbered list (module-01 license/record-type/outcome/deploy, module-02 OS/license-form/license-path/database, module-04 load-choice, module-05 quality-gate/mapping-mode/baseline/path questions, module-07 discover transitions, feedback priority, graduation overwrite/merge/abort). Split the compound feedback questions ("what happened, or what would you change?"; "fix or improvement?") into single asks, and reworded noun-phrase "or" questions ("discuss or explore", "team or manager", "add or change", "data sources or systems", the module-03 city parenthetical) to drop "or". Left the two sanctioned exceptions unchanged: `ground-rules.md:21-22` convention text and the module-02 EULA "respond yes or no" answer-format hint. Verified all four acceptance criteria: the criterion-#3 grep over `skills/` now returns only that rule text + the yes/no hint (no multi-choice questions). Also fixed 6 pre-existing `**Label**:` → `**Label:**` markdown violations flagged by the repo's CommonMark hook in the two touched files (`phase1-quality-assessment.md`, `phase2b-discover.md`).
- **Commit:** `90bd4c2`

## migrate-kiro-power

- **Implemented:** 2026-07-15 (verified at outcome level; residuals split into follow-up specs)
- **Files changed:** `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` (preface I4/I5 backfill)
- **Summary:** Verify/backfill audit of the umbrella migration spec against @invariants.md (~50 invariants across 4 groups). Result: SATISFIED ~50, PARTIAL 7, GAP 0 — every enumerated outcome is met (preface, per-module structure, Modules 1–7, graduation, project layout) with no missing referenced files, and Module 3's "always a dynamic web-app truth-set visualization" was confirmed real (`scripts/senzing_viz_server.py` — live ThreadingHTTPServer + D3 force graph + JSON APIs, not a static image). Backfilled the two preface questions (`onboarding-flow.md:114,139`) to a neutral-lead + numbered-list form, removing the "or"-joined choices that violated invariant I5 and the plugin's own `ground-rules.md:22-24`. Recorded as implemented at the outcome level; the 7 residual PARTIALs were split into dedicated follow-up specs rather than blocking the umbrella.
- **Follow-up specs:** `interaction-or-questions.md` (systemic I5/I4 "or" cleanup, ~15+ questions), `module-step-overview.md` (M4), `hook-to-message-convention.md` (Q1), `cross-platform-hook-execution.md` (T1), `doc-consistency-audit.md` (Q2+T4). The transformed→senzing-ready naming (S1) is already tracked in `specs/todo.md`.
- **Commit:** `9391bf1`

## stop-hook-issue

- **Implemented:** 2026-07-15
- **Files changed:** `plugins/senzing-bootcamp/scripts/stop-nudge.sh`
- **Summary:** Fixed the Stop-hook loop where the nudge re-fired every turn (re-asking the same "👉 …explore concepts…?" question) until Claude Code's 9x block cap force-ended the turn. The hook now applies three deterministic gates in order: (1) `stop_hook_active == true` → exit 0 immediately — the loop-breaker, so a block never re-fires on the continuation it caused; (2) no `config/bootcamp_progress.json` → exit 0, never touching non-bootcamp sessions; (3) the last assistant turn already ended with a 👉 pointer question (parsed from the transcript) → stay silent, honoring "ask each question once." Only when none short-circuit does it block exactly once to request a single closing question. Verified end-to-end against the spec's repro: a pending 👉 question stays silent (no re-ask), `stop_hook_active=true` is always released, an absent closing question nudges once, and a block→continuation sequence blocks at most once (no loop). Cross-platform (POSIX sh + grep/sed, optional python3 with a documented safe fallback) and language-agnostic per @invariants.md.
- **Commit:** `9391bf1`

## PreToolUseWriteError

- **Implemented:** 2026-07-15
- **Files changed:** `plugins/senzing-bootcamp/scripts/write-gate.sh`
- **Summary:** The write-gate no longer matches `/tmp/` (or `/Downloads/`, `%TEMP%`) as a floating substring in the payload. It now extracts only the target `file_path`, resolves it to an absolute path, and exempts the project directory (CWD-containment) FIRST, then blocks genuine system-temp/Downloads targets — Option 1 from the spec. Verified end-to-end against all acceptance criteria via a project rooted under a `/tmp/`-containing path: project-relative and in-project absolute writes to `config/bootcamp_preferences.yaml` are allowed (no heredoc workaround); genuine `/tmp/` and `~/Downloads/` targets are still blocked; the secret-detection branch still fires; content that merely mentions `/tmp/` is allowed; and an unexpanded Windows `%TEMP%` target is blocked.
- **Commit:** `9391bf1`
