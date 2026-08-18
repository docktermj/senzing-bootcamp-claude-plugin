# The two steps that require screenshot capture pass its flags without ever naming the script

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 3b and Module 7 both require capturing one screenshot per visualization tab, pointing at
`module-completion.md` → "Capturing visualization screenshots" for the procedure. At Module 7 step 3c,
after verifying all six tabs served correctly, capture was **skipped** on the stated grounds that
driving the app's tab switching needed browser automation that was unavailable — without first checking
whether the plugin already shipped a tool for it.

It does. `plugins/senzing-bootcamp/scripts/capture_screenshots.py` takes `--url` / `--html`, `--tabs`,
`--name` and `--query`, tries several headless backends, and writes both the PNGs and a
`<name>-tabs.json` coverage manifest. Run afterward, it captured 6/6 tabs first try against plain
headless Chrome, with real search results.

Recovered at graduation: the Module 7 server was briefly restarted for a live capture, and the Truth Set
module's six tabs were captured from its retained static snapshot — 12 images the recap PDF would
otherwise not have carried. The Truth Set **live** capture was permanently lost, since its records were
purged at that module's close exactly as its own guidance warns.

## Root cause

**Both requiring steps supply the arguments and name no executable.** They parameterize a command they
never identify, and defer the identity to another file.

`module-07-query-visualize-discover/phase1-query-visualize.md:494-500`:

> After generating it, capture screenshots for the recap per
> `../bootcamp-onboarding/module-completion.md` → "Capturing visualization screenshots" (skip silently
> with no headless capability …). `{name}` = `results_visualization`. Capture **one image per tab**
> from the running server (`--url http://localhost:<port>`, with `--query` so Search / Probe shows real
> results) …

`module-03b-truthset-visualization/phase1-visualization.md:285-295` does the same for step 2.2 —
`--url http://localhost:<port>`, the `--html` fallback, `{name}` = `truthset_verification`, one image
per tab — then "Follow `../bootcamp-onboarding/module-completion.md` → 'Capturing visualization
screenshots'".

The script is named in exactly two places, neither of which is a step that requires capture:
`bootcamp-onboarding/module-completion.md:264-265` (the shared procedure, where `<helper>` is resolved)
and `graduation/SKILL.md:504` and `:715` (which read the manifest it writes).

⚠️ **The convention the capture instruction breaks is demonstrated eight lines above it.** In the same
Module 7 bullet list, `phase1-query-visualize.md:486-487` names its bundled script with both resolution
paths inline:

> take palette/typography from `${CLAUDE_PLUGIN_ROOT}/scripts/brand_tokens.py` (INV-081;
> skill-relative fallback `../../scripts/brand_tokens.py`, INV-252).

`senzing_viz_server.py`, `generate_recap_pdf.py`, `generate_discoveries_pdf.py` and
`normalize_docs_markdown.py` are all named the same way at their points of use. `capture_screenshots.py`
is the exception, and it is the one whose absence is unrecoverable.

**Nothing in the reading path contradicts a guide that concludes capture is impossible.** The
requirement and the capability live in different files, the flags read as *what the procedure will need*
rather than *what a bundled tool accepts*, and the step's own escape hatch — "skip silently with no
headless capability" — is satisfied by a guide that never looked for one. The skip was self-justified
and produced no error.

**INV-185's guard cannot see this, and the reason generalizes.** INV-185 requires every command run
against a bundled script to resolve it inside the plugin, and
`tests/test_bundled_script_and_production_paths.py` sweeps for it — but it discovers invocations **by
script name**: `BUNDLED_SCRIPTS = sorted(p.name for p in SCRIPTS.glob("*.py"))`. An instruction that
names no script matches nothing, so the sweep passes on the one failure mode worse than an unresolvable
path: an invocation with no path at all. The guard is built to catch a *wrong* resolution, and the
defect is a *missing* one.

**The cost is asymmetric and the plugin already says so.** Module 3b's own text states that its live
capture cannot be re-taken after teardown, and Module 3b purges its records at close. So a
reachable-but-unnamed tool costs the keepsake its most visual content, unrecoverably for one module and
only luckily recoverable for the other.

## Proposed change

1. **Name the script and its resolution rule at both requiring steps** —
   `phase1-query-visualize.md:494-500` and `phase1-visualization.md:285-295` — as
   `${CLAUDE_PLUGIN_ROOT}/scripts/capture_screenshots.py` with the documented skill-relative fallback
   `../../scripts/capture_screenshots.py` (INV-185, INV-252), exactly as `brand_tokens.py` is named
   eight lines earlier in the same list.
2. **Ship a one-line invocation at each point of use**, with that step's own `--name`, `--tabs` and
   `--url`/`--html` already filled in. A parameterized command the reader can run is what would have
   prevented the skip; a pointer to a procedure was not.
3. **Keep `module-completion.md` as the authority on the procedure** and do not restate its rules at
   either step — the backends it tries, the exit-code handling, the `--single` distinction, and the
   caption-from-the-opened-image rule stay stated once (INV-179). The steps gain the *identity* of the
   tool, not a copy of its manual.
4. **Say that "no headless capability" is a conclusion the helper reaches, not one the guide may
   reach first.** The step's silent-skip path must be entered on the script's exit code — it reports
   which of three reasons applied — never on an assumption that automation is unavailable. That is the
   sentence that closes the actual failure.
5. **Widen the INV-185 guard to catch a parameterized invocation that names no script.** Sweep for the
   flag vocabulary of bundled scripts (`--tabs`, `--single`, `--out-dir`, `--url`, `--html`) and require
   any step using it to also name a resolved script path. This is the generalizable half: it catches the
   next unnamed bundled tool, not only this one.
6. **State the unrecoverability where the risk is highest.** Module 3b's capture is the one that cannot
   be re-taken; the invocation there should carry that in the same breath as the command, since the
   consequence is what makes the skip expensive rather than untidy.

## Acceptance criteria

- [ ] Both requiring steps name `capture_screenshots.py` with `${CLAUDE_PLUGIN_ROOT}` and the
      skill-relative fallback, and carry a runnable invocation with that step's own arguments.
- [ ] `module-completion.md` remains the single statement of the capture procedure; neither step
      duplicates its backend list, exit-code handling or caption rule.
- [ ] Each step's silent-skip path is conditioned on the helper's exit code, not on an assessment of
      whether automation is available.
- [ ] `tests/test_bundled_script_and_production_paths.py` (or a sibling) fails when a step uses bundled
      script flags without naming a resolved script — negative-controlled by deleting the script name
      from one invocation and confirming the mutation lands.
- [ ] The existing INV-185 sweep still passes, and every newly added invocation resolves under
      `${CLAUDE_PLUGIN_ROOT}` or the documented fallback.
- [ ] Module 3b's invocation states that its live capture cannot be re-taken after teardown.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the helper
      is a bundled `python3` script invoked the same way on all three platforms (INV-052), the backend
      discovery is the helper's own concern, and nothing added here depends on the bootcamper's chosen
      language.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  step 3c's capture instruction (`:494-500`).
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` —
  step 2.2 (`:285-295`).
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase2-close.md:90` — check the
  second pointer still resolves once the requiring step names the tool.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — unchanged as the
  procedure of record; confirm `<helper>` resolution at `:264-265` still reads as the authority.
- `tests/test_bundled_script_and_production_paths.py` — the widened sweep.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "the bundled capture_screenshots.py is not named at
  the point of use, and screenshot capture was skipped as a result" (2026-08-17, Module Query, Visualize
  and Discover, Priority Medium; `Source: self-observed (assistant retrospective)`)
- Priority: **Medium.** Nothing fails and nothing errors; the loss is the recap's most visual content,
  permanent for Module 3b's live capture, and the skip is self-justifying so it can recur on any run.
- MCP re-check: n/a (no Senzing fact) — the capability, the requirement and the guard are all
  plugin-owned. Confirmed instead against the working tree: the script exists at
  `plugins/senzing-bootcamp/scripts/capture_screenshots.py`, and it is named in three places
  (`module-completion.md:264-265`, `graduation/SKILL.md:504`, `:715`), none of them a step that requires
  capture.
- Upstream: **not applicable.**
- Related specs: `specs/capture-visualization-screenshots-for-recap.md` (established the capture step),
  `specs/per-tab-screenshot-capture-and-grounded-captions.md`,
  `specs/single-page-capture-instruction-produces-zero-images.md` and
  `specs/default-tab-capture-without-injection.md` (earlier defects in the same procedure),
  `specs/enforce-screenshot-embed-and-backfill.md` and `specs/inert-screenshot-omission-conflicts-with-embed-every-tab.md`
  (what happens to the images once captured),
  `specs/windows-headless-browser-discovery-for-screenshots.md`,
  `specs/bundled-file-reads-resolve-like-bundled-script-runs.md` (INV-252, the same
  resolve-inside-the-plugin rule this spec applies to an invocation),
  `specs/guards-enforce-class-scoped-rules-from-hardcoded-site-sets.md` (the same class of guard
  blindness item 5 addresses).
