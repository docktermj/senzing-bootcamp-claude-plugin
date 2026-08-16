# The displayed plugin version must resolve to the plugin root actually serving the run

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The WELCOME banner displayed the wrong plugin version. A bootcamper on 2026-08-15 saw:

```text
Senzing Bootcamp v0.5.0
```

while the plugin actually driving the skill invocation was **v0.5.1**. `$CLAUDE_PLUGIN_ROOT`
was unset in that environment, so the guide fell back to searching the filesystem for a
`.claude-plugin/plugin.json` and used the first match — a *different* clone of the plugin
repo on the same machine, which reports `0.5.0`.

Both clones were present and both are real plugin roots (verified on the reporting machine,
2026-08-15):

```text
…/github.com/docktermj/senzing-bootcamp-claude-plugin/plugins/senzing-bootcamp/.claude-plugin/plugin.json  →  "version": "0.5.1"   (the one serving the run)
…/senzing.git/senzing-bootcamp-claude-plugin/plugins/senzing-bootcamp/.claude-plugin/plugin.json           →  "version": "0.5.0"   (a second checkout)
```

The bootcamper's stated impact: *"version mismatches make me not trust the bootcamp's status
displays."* That is the real cost — the version line exists to establish provenance (INV-105),
so a version line that can be wrong is worse than no version line, and it silently corrupts
every downstream use of the same value: the feedback entry's `Plugin version:` field, the
recap header, and the recap PDF's provenance block.

⛔ **This is not a maintainer-only condition.** Two plugin roots on one machine is the normal
state for anyone who has the plugin installed (`~/.claude/plugins/…`) *and* a clone, or who
has upgraded without removing the old copy. The search picks whichever the traversal reaches
first, which is not a property anyone controls.

## Root cause

**Every site that reads the plugin manifest names one path and documents no fallback**, so
when `$CLAUDE_PLUGIN_ROOT` is unset there is no specified next step and the guide improvises:

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:33` — "Read the
  plugin version from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` (the `version` field;
  use "Unknown" if unreadable)". The displayed line is at `onboarding-flow.md:121`.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md:22` and `:148` — the same
  bare path, for the feedback entry's captured context.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:47` — the same
  bare path, for the recap header.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md:418` — the same bare path, for the
  recap's run-environment provenance block.
- `plugins/senzing-bootcamp/scripts/feedback-capture.py:101` — the hook injects the literal
  text `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` into the guide's added context. The
  hook's *own* `args` are substituted by Claude Code (`hooks/README.md:53`), but the string it
  injects is not — so the guide receives an unexpanded variable and is back in the same spot.

"Use Unknown if unreadable" does not cover this case. The path was not *unreadable*: with
`$CLAUDE_PLUGIN_ROOT` empty it expanded to `/.claude-plugin/plugin.json`, which is simply a
different, absent file — and the guide treated a miss as licence to go looking rather than as
the "Unknown" branch.

**The fallback pattern already exists in this plugin and was never extended to manifest
reads.** `INV-185` requires every command run against a **bundled script** to resolve inside
the plugin via `${CLAUDE_PLUGIN_ROOT}` *with a documented skill-relative fallback*
(`<this-skill-dir>/../../scripts/<name>.py`), and that fallback is spelled out at
`graduation/SKILL.md:608-613`, `graduation/SKILL.md:537`, `:859`, `:899` and
`module-07-query-visualize-discover/phase1-query-visualize.md:617`. INV-185 is scoped to
*running a script*, so it does not reach *reading a file*, and its guard
(`tests/test_bundled_script_and_production_paths.py`) only sweeps lines that invoke a Python
interpreter. Reading `plugin.json` matches neither. The manifest is the one bundled file the
plugin reads by path, and it fell in the gap.

The skill-relative fallback is well-defined here for exactly the same reason it is for
scripts: the manifest sits two levels above every skill directory
(`skills/<skill>/` → `../../.claude-plugin/plugin.json`), and the skill's own directory is
given to the guide at invocation. It is not a heuristic — it is by construction the plugin
whose files are being executed.

- **MCP re-check:** none required. The entry makes no Senzing claim; the routing is `plugin`
  and no Senzing MCP tool owns any fact in it.

## Proposed change

1. **Specify the resolution once, and forbid the search.** In `onboarding-flow.md` step 0,
   replace the bare read with the three-branch resolution, in order:

   1. `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` when `CLAUDE_PLUGIN_ROOT` is set
      **and non-empty**.
   2. Otherwise `<this-skill-dir>/../../.claude-plugin/plugin.json` — the skill directory
      given at invocation, two levels up, mirroring INV-185's documented script fallback.
   3. Otherwise `Unknown`.

   Add a ⛔ line: **never search the filesystem for a `plugin.json`** (`find`, `glob`, a
   repo-wide grep) and never read one outside the resolved plugin root. A second checkout is
   a normal thing to have on a machine, and the first match is not the running plugin.

2. **Use that same resolution at every other manifest-read site**, referring back to step 0's
   rule rather than restating the path: `feedback.md:22` and `:148`, `module-completion.md:47`,
   `graduation/SKILL.md:418`. Written as a sweep, not as a fix to the one line the bootcamper
   saw — the recap header and the feedback entry carry the same value and fail the same way,
   and INV-105 covers the recap as well as the banner.

3. **Have the hook resolve the version itself** (`feedback-capture.py`). The script always
   knows where it lives, so it can read `Path(__file__).resolve().parents[1] / ".claude-plugin"
   / "plugin.json"` and inject the resolved **value** (`plugin version 0.5.1`) instead of a
   path string carrying an unexpanded variable. On any failure to read or parse, inject
   `plugin version Unknown` — never the path, and never a guess. This removes the only site
   that hands the guide an unsubstituted `${CLAUDE_PLUGIN_ROOT}`.

4. **Never display or record an unresolved version as a number.** `Unknown` is the required
   output when resolution fails — in the banner, in the feedback entry, and in the recap.
   ⛔ Do **not** record the resolved plugin *path* anywhere in the recap or the feedback entry:
   an absolute path carries a username, and both artifacts must stay PII-free (INV-065).

**On the bootcamper's suggested fix — asking which version to run — declined, and why.** The
suggestion was: *"If multiple plugin versions/checkouts are available on the machine and the
correct one can't be resolved unambiguously, ask the bootcamper which version they want to
run."* The ambiguity is manufactured by the search, not discovered by it. The guide is already
executing files from exactly one plugin root, so once resolution is deterministic there is one
candidate and nothing to ask (INV-006 forbids asking what the bootcamp can determine). Worse,
the answer could not take effect: choosing a different checkout would not change which files
the running skill loads, so a "yes, use the other one" would produce a banner that misreports
the code actually executing — the original defect, now with the bootcamper's fingerprints on
it. It would also put an installation concern to someone who has no way to evaluate it, in the
preface, as a gate the curriculum does not have (INV-247). **What is honored from the
suggestion is its core**: never show a version the bootcamp cannot stand behind — hence
`Unknown` in change 4, and the ⛔ against reading any manifest outside the resolved root.

5. **Guard it.** Add `tests/test_plugin_manifest_reads_resolve_inside_the_plugin.py`, shaped
   as a sweep like INV-185's guard: every mention of `.claude-plugin/plugin.json` across the
   shipped `skills/`, `commands/`, `hooks/` and `scripts/` trees must carry either
   `${CLAUDE_PLUGIN_ROOT}` or the documented skill-relative fallback; the sweep must assert it
   matches the known sites so it cannot pass by matching nothing; and `onboarding-flow.md` must
   ship the no-search ⛔ and the three-branch order. ⚠️ **State in the test's docstring what it
   cannot do**: a file-reading guard cannot detect a guide improvising a `find` at runtime —
   the defect the bootcamper hit existed in no file. The guard asserts the rule ships and that
   every shipped path resolves; a clean run is not evidence the search cannot recur.

## Acceptance criteria

- [ ] `onboarding-flow.md` step 0 specifies the three-branch resolution in order (`$CLAUDE_PLUGIN_ROOT` when set and non-empty → `<this-skill-dir>/../../.claude-plugin/plugin.json` → `Unknown`) and carries a ⛔ forbidding a filesystem search for `plugin.json`.
- [ ] With `CLAUDE_PLUGIN_ROOT` unset and a second plugin checkout present on the machine reporting a different version, the WELCOME banner shows the version of the plugin serving the invocation — not the other checkout's, and not a searched-for match.
- [ ] With `CLAUDE_PLUGIN_ROOT` set, the banner shows that root's version (no behavior change from today).
- [ ] When neither branch resolves, the banner, the feedback entry's `Plugin version:` field, and the recap header all read `Unknown` — never a number, never a path.
- [ ] `feedback.md:22`/`:148`, `module-completion.md:47` and `graduation/SKILL.md:418` use the step 0 resolution, so the recap header, the recap PDF provenance block (INV-105) and a feedback entry all carry the same value the banner showed.
- [ ] `feedback-capture.py` injects a resolved version string (or `Unknown`), and no shipped hook-injected context contains an unexpanded `${CLAUDE_PLUGIN_ROOT}`.
- [ ] No resolved plugin path is written into `docs/bootcamp_recap.md`, the recap PDF, or a feedback entry (INV-065, PII-free).
- [ ] `tests/test_plugin_manifest_reads_resolve_inside_the_plugin.py` passes, asserts its sweep matched the known sites, and documents in its docstring that it cannot detect a runtime-improvised filesystem search.
- [ ] The full offline suite still passes (`python3 -m unittest discover -s tests`).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md). The skill-relative fallback is a relative path, so it needs no shell and no platform-specific expansion — the same reason INV-185's script fallback works on all three.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — line 33: the three-branch resolution + the no-search ⛔; line 121's display line is unchanged and now reads a trustworthy value.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` — lines 22 and 148: resolve per step 0 instead of naming the bare path.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — line 47: same, for the recap header.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — line 418: same, for the recap provenance block.
- `plugins/senzing-bootcamp/scripts/feedback-capture.py` — line 101: resolve the version from `__file__` and inject the value, not the path.
- `tests/test_plugin_manifest_reads_resolve_inside_the_plugin.py` — new sweep guard.
- `specs/INVARIANTS.md` — record the invariant below.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: Wrong plugin version displayed in the WELCOME banner" (2026-08-15, Module: Onboarding (preface / WELCOME banner); `Source: bootcamper-reported`)
- Priority: High
- MCP re-check: n/a (no Senzing fact). Server version recorded for the run: `get_capabilities` → `server_info.server_version: 1.32.9` (2026-08-15). The entry's routing is `plugin` and it asserts nothing about Senzing or its MCP server, so no tool owns a fact in it and nothing was re-verified.
- Upstream: not applicable — the entry routes `plugin`; nothing here is Senzing's to fix.
- Related specs: `show-plugin-version-and-record-environment.md` (established INV-105 — this fixes *which* manifest that version comes from, and does not change what is displayed or recorded), `enrich-feedback-context.md` (`feedback.md`'s captured `Plugin version:` field), `example-recap-reference.md` (already required `${CLAUDE_PLUGIN_ROOT}` with a skill-relative fallback for a bundled *file* reference — the precedent this generalizes); INV-006, INV-065, INV-105, INV-185, INV-247

## Invariants introduced

- `INV-252` — Every read of a **bundled plugin file** (the `.claude-plugin/plugin.json` manifest above all) MUST resolve inside the plugin serving the run: `${CLAUDE_PLUGIN_ROOT}/…` when that variable is set and non-empty, otherwise the documented skill-relative fallback (`<this-skill-dir>/../../…`), otherwise `Unknown`. ⛔ The guide MUST NOT search the filesystem for a bundled file, and MUST NOT read one outside the resolved plugin root — a second plugin checkout is a normal thing to have on a machine (an installed plugin plus a clone, or an un-removed upgrade), and the first match a traversal reaches is not the running plugin. A value that cannot be resolved is reported as `Unknown`, never guessed, and the resolved path itself is never written into a bootcamper-facing artifact (INV-065). Extends **INV-185** from *running* a bundled script to *reading* a bundled file: INV-185's fallback pattern already shipped at five script-invocation sites, but its scope and its guard both stop at the interpreter, so the five manifest reads had no fallback specified and an unset `CLAUDE_PLUGIN_ROOT` left the guide to improvise. ⚠️ **A file-reading guard cannot see this defect happen** — the wrong version came from a runtime search that exists in no file — so `tests/test_plugin_manifest_reads_resolve_inside_the_plugin.py` asserts only that the rule ships and that every shipped path resolves; a clean run is not evidence the search cannot recur. (Observed 2026-08-15 on plugin 0.5.1: the WELCOME banner showed `v0.5.0`, read from a second checkout on the same machine, while 0.5.1 was serving the run.) (Source: `plugin-version-resolves-to-the-running-plugin-root`, 2026-08-15.) (Recorded in `specs/INVARIANTS.md`, 2026-08-15.)

## Deviations from this spec, and why (2026-08-15)

Nothing in the diagnosis or the proposed change was altered. Two things about the
implementation that this spec's text does not say:

- **Three acceptance criteria are implemented but not runtime-verified**, all the same class:
  the three that assert what the **banner displays** (with `CLAUDE_PLUGIN_ROOT` unset, with it
  set, and "Unknown" when neither branch resolves). A banner is emitted by the guide, and the
  suite is offline (INV-108), so no test can produce one. They need a `dry-run` phase-3
  conversational walk on a machine carrying two plugin checkouts. The rule they rest on ships
  and is guard-asserted, and the same resolution is runtime-proven in `feedback-capture.py`,
  whose resolved-version and "Unknown" branches are both exercised.
- **The guard is block-scoped, not file-scoped**, which the spec did not specify. A file-wide
  "does this file cite the rule?" check let two of the four pre-fix sites pass, because both
  named `onboarding-flow.md` elsewhere for unrelated reasons — a bare manifest path going
  unflagged on the strength of a cross-reference hundreds of lines away. Verified by replaying
  the predicate against the `HEAD` content of each site: block-scoped flags all three consumers
  pre-fix, file-scoped flagged one.
- **One file outside `## Affected files` was touched:** `tests/test_invariant_enforcer_citations.py`,
  whose `EXPECTED_PAIRS` counter moves 64 → 65 because INV-252 names its enforcing test. The
  test requires that update to be deliberate; the added pair was confirmed to be exactly
  `('INV-252', 'test_plugin_manifest_reads_resolve_inside_the_plugin.py')` and nothing else.
