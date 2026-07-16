# PreToolUseWriteError

**Status:** Implemented (2026-07-15) — `plugins/senzing-bootcamp/scripts/write-gate.sh`
rewritten to exempt the project directory before applying the temp/Downloads check
(Option 1 below). Verified against all acceptance criteria.

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

● Write(config/bootcamp_preferences.yaml)
  ⎿  Error: PreToolUse:Write hook error: [${CLAUDE_PLUGIN_ROOT}/scripts/write-gate.sh]: Write blocked: use a project-relative path, not a system temp or Downloads
     directory.

● Write(config/bootcamp_preferences.yaml)
  ⎿  Error: PreToolUse:Write hook error: [${CLAUDE_PLUGIN_ROOT}/scripts/write-gate.sh]: Write blocked: use a project-relative path, not a system temp or Downloads
     directory.

● The write-gate is blocking this specific write. Let me check the gate script to understand why.

  Read 1 file

● The gate blocks any payload containing /tmp/ — and the project path /home/senzing/tmp/... contains that substring. The progress file slipped through only because the
  gate self-disables until it exists. I'll write the preferences file via a heredoc instead, since the Write path can't avoid the substring.

  Read 1 file

---

## Root cause (confirmed)

`plugins/senzing-bootcamp/scripts/write-gate.sh:12` matches the literal substring
`/tmp/` anywhere in the tool payload:

```bash
if printf '%s' "$input" | grep -Eq '/tmp/|%TEMP%|/Downloads/'; then
```

The Write/Edit payload always carries an absolute path. When the bootcamp project
lives under a directory whose path contains `/tmp/` (e.g.
`/home/senzing/tmp/test-claude-plugin-06`), every legitimate project-relative
write serializes to an absolute path that contains `/tmp/`, so the guard fires on
the project's own required setup writes. The same substring flaw applies to
`/Downloads/` (a project under `~/Downloads/...`) and `%TEMP%`.

`write-gate.sh:8-10` also explains why the very first write (the progress file)
slipped through: the gate is a no-op until `config/bootcamp_progress.json` exists,
then activates for every subsequent write.

## Proposed change

Stop matching `/tmp/` (and friends) as a floating substring. Any one of these
resolves it; prefer the one that stays portable across Linux, macOS, and Windows:

1. **Exempt the project directory first.** Resolve the target path and, if it is
   under the current working (project) directory, allow it before applying the
   temp/Downloads check. This is the most robust: the gate's intent is "don't
   write *outside* the project," which is exactly the CWD-containment test.
2. **Compare against the real temp root**, not a substring: resolve the path and
   test whether it is under `$TMPDIR` / the OS temp directory (and the real
   Downloads directory), rather than greping for `/tmp/`.
3. **Anchor the pattern** so it only matches a path that *starts at* a temp root
   (e.g. leading `^/tmp/`, `^/private/tmp/`, `%TEMP%\`), not one that merely
   contains the segment.

## Acceptance criteria

- [x] With the project rooted under a path containing `/tmp/` (e.g. `/home/user/tmp/proj`), onboarding's writes to `config/bootcamp_preferences.yaml` succeed with no PreToolUse block and no heredoc workaround.
- [x] A write whose target is genuinely the system temp dir or Downloads is still blocked.
- [x] The secret-detection branch is unchanged and still fires.
- [x] Behavior holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).
- [x] Bonus: a `content` field that merely mentions `/tmp/` no longer trips the gate — only the resolved target path is inspected.

## Affected files

- `plugins/senzing-bootcamp/scripts/write-gate.sh` — line 12 substring match is the defect; the fix lives here.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "PreToolUse write-gate blocks writes when project path contains \"/tmp/\"" (2026-07-15, Module: Onboarding / plugin infrastructure)
- Priority: pending (bootcamper: "There were PreToolUse write errors above. Those should be fixed.")
- Related specs: this spec (`specs/PreToolUseWriteError.md`)
