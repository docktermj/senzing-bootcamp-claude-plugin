# A bundled file the guide READS must resolve like one it RUNS

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Six shipped instructions tell the guide to read a file that exists **only inside the plugin**,
by a bare project-relative path. Run from the Bootcamper's project — where the command actually
runs — every one of them resolves to nothing. The project layout has `src/scripts/` and never a
top-level `scripts/` (INV-050), and it has no `docs/examples/` at all.

| Site | Path named | What it is |
|---|---|---|
| `module-03b-truthset-visualization/phase1-visualization.md:206` | `scripts/vendor/d3.v7.min.js` | inline the vendored D3 |
| `module-03b-truthset-visualization/phase1-visualization.md:210` | `scripts/brand_tokens.py` | where the palette lives |
| `module-03b-truthset-visualization/visualization-api-reference.md:846` | `scripts/brand_tokens.py` | where the palette lives |
| `module-05-data-quality-mapping/phase2-data-mapping.md:1050` | `scripts/vendor/d3.v7.min.js` | inline the vendored D3 |
| `module-07-query-visualize-discover/phase1-query-visualize.md:469` | `scripts/brand_tokens.py` | where the palette lives |
| `graduation/SKILL.md:392` | `docs/examples/bootcamp_recap.example.md` | the shipped example recap |

**The D3 rows are the damaging ones, and the damage is silent.** The ⛔ sitting directly beside
both of them says what happens when the vendored file is not used: a `<script src="https://…">`
"makes the page render blank on an air-gapped workstation — which Senzing evaluations frequently
are — with no error anywhere." So the instruction that exists to keep the deliverable offline
(INV-091) names a path the guide cannot resolve, and the documented failure mode of not
resolving it is a blank page nobody is told about. Modules 3b, 5 and 7 all ship visual
deliverables this way.

**Three of the five files prove the rule was known and applied incompletely.** Each roots one
bundled artifact correctly and leaves its sibling bare:

- `module-05/phase2-data-mapping.md:1049-1050` — `${CLAUDE_PLUGIN_ROOT}/scripts/brand_tokens.py`
  on one line, bare `scripts/vendor/d3.v7.min.js` on the next, inside one sentence.
- `module-03b/phase1-visualization.md:232` roots `senzing_viz_server.py` **with** a
  skill-relative fallback, while `:206` and `:210` are bare.
- `module-07/phase1-query-visualize.md:616-617` roots `generate_discoveries_pdf.py` with both
  branches — that line is INV-185's own worked fix — while `:469` is bare.

A further three sites are rooted but carry **no fallback**, so they break the other way (an
unset `CLAUDE_PLUGIN_ROOT` leaves them unresolved):
`module-05/phase1-quality-assessment.md:619` and `:622`, and `module-05/phase2-data-mapping.md:1049`.

## Root cause

**Two rules cover this surface and neither reaches it, in the same gap.**

- **INV-185** binds "every command the SBCP tells the guide to **run** against a bundled
  script". An `import`, an inline of a `.js` file, and a pointer to an example `.md` are not
  commands and not scripts, so the invariant's text does not reach them.
- Its guard, `tests/test_bundled_script_and_production_paths.py`, is narrower still: its
  `invocation_lines()` only collects lines matching a Python-interpreter regex
  (`runner = re.compile(r"(?:^|\s)(?:python3?|py -3|…)\s")`), so a line naming
  `scripts/brand_tokens.py` with no interpreter is never swept. `brand_tokens.py` **is** in the
  guard's `BUNDLED_SCRIPTS` list; it is the interpreter requirement that filters it out.
- **INV-252**, registered 2026-08-15, does reach them — "every read of a **bundled plugin
  file**… MUST resolve inside the plugin serving the run" — but it was implemented for the
  `.claude-plugin/plugin.json` manifest only, and its guard
  (`tests/test_plugin_manifest_reads_resolve_inside_the_plugin.py`) sweeps only
  `.claude-plugin/plugin.json`. The invariant is one hour old and is already the audit's
  defect class 1: a rule applied to some of the sites it binds.

So the surface has a correct rule, a correct guard idiom, and a worked example in three of the
five files — and the reads were left out of all three.

- **MCP re-check:** n/a (no Senzing fact). This is internal path resolution; no Senzing tool
  owns any fact in it and none was called for this finding.

## Proposed change

1. **Root all six bare references**, matching the form already used in the same files:
   `${CLAUDE_PLUGIN_ROOT}/<path>` with the documented skill-relative fallback
   (`<this-skill-dir>/../../<path>`). For `graduation/SKILL.md:392`, the sibling at `:356`
   already shows the exact wording to mirror.
2. **Add the missing fallback** at the three rooted-but-unguarded sites
   (`module-05/phase1-quality-assessment.md:619`, `:622`, `module-05/phase2-data-mapping.md:1049`).
3. **Widen the INV-252 guard from the manifest to every plugin-only path.** Derive the set by
   scanning `plugins/senzing-bootcamp/` for directories that exist in the plugin and not in
   INV-050's project layout — `scripts/`, `docs/examples/`, `.claude-plugin/` — and require
   every shipped reference to one to carry `${CLAUDE_PLUGIN_ROOT}` or the skill-relative
   fallback. Derived by scanning, never a hardcoded path list (INV-246): the six sites above are
   what one sweep found, and the point of the guard is the seventh.
4. **Do not widen INV-185's text.** It is accurate about what it governs, and INV-252 already
   states the general rule. What is wrong is the implementation coverage, not the ruleset —
   so this needs no new invariant (`INVARIANTS.md` stays append-only either way).

## Acceptance criteria

- [ ] No shipped file names `scripts/vendor/…`, `scripts/brand_tokens.py`, or `docs/examples/…` by a bare project-relative path; every reference carries `${CLAUDE_PLUGIN_ROOT}` or the documented skill-relative fallback.
- [ ] Every rooted reference to a plugin-only path also documents the skill-relative fallback, so an unset `CLAUDE_PLUGIN_ROOT` resolves rather than failing.
- [ ] The INV-252 guard derives its site set by scanning for plugin-only directories, not from a hardcoded list, and fails when any of the six sites in the table above is reverted to its bare form (negative-controlled, one site at a time).
- [ ] The guard's non-vacuity assertion names at least one known site, so a broken sweep cannot pass silently.
- [ ] The three visual-deliverable modules (3b, 5, 7) each resolve the vendored D3 and the brand tokens by a path that works from the Bootcamper's project root, preserving INV-091 (offline render) and INV-081 (brand tokens).
- [ ] Full offline suite passes (`python3 -m unittest discover -s tests`), and `citations.py verify` stays clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the fallback is a relative path needing no shell.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — `:206`, `:210` root the D3 and the brand tokens.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` — `:846` root the brand tokens.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` — `:619`, `:622` add the fallback.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — `:1049` add the fallback, `:1050` root the D3.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — `:469` root the brand tokens.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — `:392` root the example recap, mirroring `:356`.
- `tests/test_plugin_manifest_reads_resolve_inside_the_plugin.py` — widen the sweep from the manifest to every plugin-only path; rename if the file's subject outgrows its name.

## Source

- Audit: `production-readiness-audit-2026-08-15o` — forward sweep of INV-252 (registered the same day) across the full set of sites it binds. Not from a feedback entry; found by asking what else "a bundled plugin file" covers beyond the manifest the spec was written for.
- Priority: High — the D3 rows break a documented path in three modules, and the documented failure mode is a silently blank deliverable.
- MCP re-check: n/a (no Senzing fact). No Senzing tool owns a fact in this finding; none was called for it.
- Upstream: not applicable — internal path resolution, nothing Senzing's to fix.
- Related specs: `plugin-version-resolves-to-the-running-plugin-root.md` (registered INV-252 and implemented it for the manifest only — this is the rest of its site set); INV-050, INV-081, INV-091, INV-185, INV-246, INV-252

## Deviations from this spec, and why (2026-08-15)

All six sites were rooted and all three fallbacks added as specified. Three narrowings, none
of which changes the finding:

- **Criterion 1 says "no shipped file"; one bare mention was deliberately left.**
  `scripts/generate_recap_pdf.py:164` names `docs/examples/bootcamp_recap.example.md` in a code
  comment explaining a retention figure. It addresses a developer reading this repo, not a guide
  resolving a path in a project, and rooting it would be actively wrong: the script resolves its
  own paths from `__file__` and never expands `${CLAUDE_PLUGIN_ROOT}`.
- **Criterion 2 says "every rooted reference"; `commands/graduate.md:19` has no fallback.** The
  skill-relative fallback is defined relative to a *skill* directory, and a command file has
  none, so `<this-skill-dir>` is undefined there. A command context has the variable set, and
  the line delegates rendering to the graduation skill, which carries the fallback at
  `SKILL.md:615-620`. Left as written.
- **The guard is scoped to guide-facing prose and to read-only asset directories**, which is
  narrower than criterion 1's "no shipped file". A sweep over all of `scripts/` returns **24**
  references, of which **18** merely *name* a script — `hooks/README.md`'s table of which script
  backs which hook, code comments pointing at sibling modules, "modeled on the shipped reference
  `senzing_viz_server.py`". None is an instruction to resolve a path, and a guard that cries
  wolf 18 times is one whose assertion gets relaxed. Those scripts are *run*, and INV-185's
  guard already sweeps every invocation. The narrowing is recorded in the constant's own comment
  so the next reader sees the reasoning rather than the boundary alone.

**Negative-controlled**, one site at a time: each of the six was reverted to its bare form with
the mutation asserted to have landed (so a missing target cannot pass as an escaped mutation),
and the guard failed on all six. Full suite `Ran 2745 tests … OK (skipped=3)`.

⚠️ **One probe error worth recording.** The sweep that found this finding, and a later
criterion check, both flagged `graduation/SKILL.md`'s recap-generator invocation as missing a
fallback. It is not: the fallback sits at `SKILL.md:615-620`, outside the line window the probe
read. The plugin was correct both times; the probe was wrong twice in the same way.
