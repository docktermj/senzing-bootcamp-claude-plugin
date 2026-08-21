# The dry-run skill says "all six hooks" where seven hook scripts exist, so a literal phase-2 run leaves one untested

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`plugins/senzing-bootcamp/hooks/hooks.json` declares **seven** hook entries across **six** distinct
events — `UserPromptSubmit` carries two:

| Event | Script |
|---|---|
| `SessionStart` | `session-start.py` |
| `UserPromptSubmit` | `feedback-capture.py` |
| `UserPromptSubmit` | `checkpoint-tick.py` |
| `PreToolUse` | `write-gate.py` |
| `Stop` | `stop-nudge.py` |
| `PreCompact` | `precompact-recap.py` |
| `SessionEnd` | `session-end.py` |

The dry-run skill says **six** in two places, and both are instructions to execute:

- `.claude/skills/dry-run/phase2-hooks-and-scripts.md:3` — *"Execute all six hooks and every bundled
  script…"*
- `.claude/skills/dry-run/phase2-hooks-and-scripts.md:38` — *"all six must exit 0 and emit nothing"*
- `.claude/skills/dry-run/phase3-conversational.md:227` — *"executes all six directly instead"*

**A run that follows the instruction literally executes six scripts and leaves one untested**, and
the one most likely dropped is the second `UserPromptSubmit` — a reader who counts *events* runs one
script per event and never reaches `checkpoint-tick.py`. That script drives the durability
checkpoint the fold hooks depend on, so the gap is not cosmetic.

⚠️ **"Six" is defensible as an event count and the sentence does not say events.** It says "six
hooks", then "all six must exit 0", which is a per-process claim. The ambiguity is the defect: both
readings are available and one of them silently under-covers.

## Root cause

**A count in prose, of a set that lives in a JSON file, with nothing comparing them.** This is the
stale-enumeration class the audit's Step 7 lists as class 4 — an exact count that reads
authoritative and breaks the moment a member is added. `UserPromptSubmit`'s second entry is exactly
such an addition.

⛔ **The shipped `hooks/README.md` is correct** and enumerates all seven scripts by name rather than
stating a count, which is the form that cannot rot. The defect is confined to the maintainer-side
skill.

## Proposed change

1. **Replace the count with the source.** Say "every hook entry in
   `plugins/senzing-bootcamp/hooks/hooks.json`" and give the one-liner that lists them, so the
   instruction cannot disagree with the file:

   ```bash
   python3 -c "import json;d=json.load(open('plugins/senzing-bootcamp/hooks/hooks.json'));t=d.get('hooks',d);print('\n'.join(h['args'][0].split('/')[-1] for es in t.values() for e in (es if isinstance(es,list) else [es]) for h in (e.get('hooks') or [e])))"
   ```

2. **Say explicitly that one event carries two hooks**, since that is the whole trap — a reader who
   iterates events rather than entries misses one.
3. **Fix the same count in `phase3-conversational.md:227`.**
4. ⛔ **Do not simply change "six" to "seven".** That is the same defect with a fresher number, and
   the next hook addition reproduces it. The count must come from the file or not be stated.
5. **Guard it**, deriving the expected number from `hooks.json` rather than hardcoding: no dry-run
   phase file may state a hook count that disagrees with the file, and a stated count must be an
   entry count rather than an event count.

## Acceptance criteria

- [ ] Neither phase file states a bare hook count; each names the file or the command that produces
      the list.
- [ ] The two-hooks-on-one-event case is called out where the enumeration is described.
- [ ] `phase3-conversational.md:227` no longer says "six".
- [ ] A test asserts no dry-run phase file states a hook count contradicting `hooks.json`, deriving
      the true count from the JSON — negative-controlled by reinstating "six" and confirming failure.
- [ ] `plugins/senzing-bootcamp/hooks/README.md` is unchanged; it is already correct.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      maintainer-side markdown plus a stdlib-only test; `.claude/` does not ship (`propagate.sh`
      mirrors `plugins/`, `.claude-plugin/`, `docs/` and `README.md` only).

## Affected files

- `.claude/skills/dry-run/phase2-hooks-and-scripts.md` — lines 3 and 38.
- `.claude/skills/dry-run/phase3-conversational.md` — line 227.
- `tests/` — the count guard.

## Source

- Dry run: phase 2, 2026-08-21. Found by executing the gating test and noticing seven scripts ran
  where the instruction had said six.
- Priority: **Low-Medium.** Nothing bootcamper-facing is wrong and the shipped README is correct. It
  degrades the maintainer tool whose entire value is executing *every* hook, and it does so
  silently: a run that tested six of seven reports phase 2 complete.
- MCP re-check: n/a (no Senzing fact) — the subject is the plugin's own hook manifest.
- Upstream: not applicable.
- Related specs: `specs/the-audit-skills-baselines-and-required-reading-are-stale.md` (the same
  class in the audit skill), `specs/scaffold-snippet-count-and-group-list-are-stale.md`
