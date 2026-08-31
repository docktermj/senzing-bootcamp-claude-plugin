# `capture_screenshots.py --url` cannot tell whether the tab actually changed, and names the default tab after every tab it failed to reach

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A chosen-language visualization server that implements the tab set correctly but omits `?tab=`
deep-linking causes `capture_screenshots.py --url` to write **N correctly-named PNGs that are all
the same tab**, report success for every one, and pass the module's completion gate. The keepsake
then embeds five wrong images presented as five different tabs.

Reproduced on this walk (2026-08-28), against a real Java visualization server built to the
`visualization-api-reference.md` contract and serving the loaded Truth Set (159 records → 84
entities):

```text
$ python3 capture_screenshots.py --url http://127.0.0.1:8080/ --out-dir docs/visualizations --name truthset
docs/visualizations/truthset-entity-graph.png     Entity Graph
docs/visualizations/truthset-merge-statistics.png Merge Statistics
docs/visualizations/truthset-match-keys.png       Match Keys
docs/visualizations/truthset-feature-scores.png   Feature Scores
docs/visualizations/truthset-cross-source.png     Cross-Source
docs/visualizations/truthset-search-probe.png     Search / Probe

$ md5sum docs/visualizations/truthset-*.png | awk '{print $1}' | sort -u | wc -l
5                      # six files, five distinct images
95474da527853907b707da16def516f1  truthset-match-keys.png
95474da527853907b707da16def516f1  truthset-search-probe.png    # byte-identical
```

Opening `truthset-cross-source.png` shows the **Entity Graph** tab, nav highlight and all. The five
"distinct" hashes differ only because the force simulation was mid-animation; every image is the
default tab.

## Root cause

Two mechanisms exist for activating a tab, and **only one of them runs on the `--url` path**:

- `_ACTIVATE_JS` (`scripts/capture_screenshots.py:220-238`) calls `activate(target)` and falls back
  to clicking `#navbtn-<id>`. Its own docstring says it is *"Injected into a temp copy of a
  snapshot"* — it is the `--html` path only.
- The `--url` path uses `_tab_url()` (`:276-282`), which appends `?tab=<id>`. That is the **sole**
  activation mechanism for a live server, and there is no fallback and no verification.

So when the page does not implement `?tab=`, every request returns the default tab, and the script —
which never inspects what it captured — names each screenshot after the tab it asked for.

⚠️ **The contract is not at fault, and that is what makes this a guard problem rather than a doc
problem.** `visualization-api-reference.md:680` is headed *"Tab identifiers and deep-linking
(required)"* and `:724-725` specifies `?tab=<id>` / `?q=<text>` applied at the end of `init()`. A
conforming implementation works. The defect is that **a non-conforming one is indistinguishable
from a conforming one in the output**, on the module that produces the bootcamper's keepsake.

**The completion gate does not reach it either.** `phase2-close.md:21-31` compares `id="tab-<name>"`
counts between the snapshot and the running server. That checks the tab *identifiers are present in
the HTML* — which they are, in the failing case — never that a captured image shows the tab it is
named for. The gate's own INV-265 clause proves the principle is already accepted here: *"A
comparison that finds ZERO identifiers on both sides has not passed — it has not run… a check that
passes by comparing nothing certifies exactly what it never looked at."* This is the same hazard one
step downstream, on the artifact rather than the markup.

⚠️ **This is adjacent to INV-122 but outside it.** INV-122 covers a tab id **not in the page** — the
script validates those up front and refuses (verified working in phase 2 of this run: `unknown tab
id(s): nosuchtab`, rc=1, nothing written). Here every id **is** in the page; what fails is
activation. The existing guard is on the wrong side of the failure.

⛔ **Disclosure: the non-conforming server was mine.** I implemented the six tabs, the nav ids and
the endpoint contract but did not implement `?tab=`, having read the tab table at
`visualization-api-reference.md:692-699` and not the deep-linking requirement twelve lines above it.
That is my error and I have since fixed my implementation. **The finding is not that I got it wrong
— it is that nothing in the toolchain noticed**, through capture, through the manifest, and through
the completion gate, on the module whose entire output is a keepsake.

## Proposed change

1. **Verify activation in `capture_screenshots.py`, on both paths.** After capturing, assert the
   rendered page's active tab is the requested one — the cheapest reliable signal is to read back
   the active nav button / active section id from the page before the screenshot is taken, rather
   than comparing images. Fail loudly for that tab (skip the file, message on stderr, non-zero exit
   for the run) rather than writing a mislabeled PNG. This is the INV-122 treatment applied to
   activation instead of to id validity.
2. **Add a cheap duplicate check as defense in depth.** Two captured tabs whose PNGs are
   byte-identical is never a legitimate outcome; report it. This catches activation failures the
   readback misses (a page that updates the nav highlight but not the section, say).
3. **Give the `--url` path the same fallback the snapshot path has.** `_ACTIVATE_JS` already knows
   how to click `#navbtn-<id>`; running it against a live page as a fallback when `?tab=` does not
   take would make a partially-conforming server work instead of silently misreport.
4. **Cross-reference the deep-linking requirement from the step that captures.** `phase1-visualization.md`
   Step 2 tells the implementer to build the server and later to capture it; the `?tab=` requirement
   lives in the on-demand reference. Name it at the step that depends on it (INV-183), so an
   implementer reading the executable file meets the requirement the capture tool assumes.

## Acceptance criteria

- [ ] `capture_screenshots.py` verifies the active tab matches the requested tab before saving, on
      both the `--url` and `--html` paths, and refuses to write a mislabeled file.
- [ ] Two byte-identical captures in one run are reported as an error rather than accepted.
- [ ] Running the capture against a page with no `?tab=` support produces a non-zero exit and a
      message naming activation as the cause — not six confidently-named PNGs.
- [ ] `phase1-visualization.md` Step 2 names the `?tab=`/`?q=` deep-linking requirement (or cites
      `visualization-api-reference.md`'s "Tab identifiers and deep-linking (required)") at the point
      the chosen-language server is built.
- [ ] A repo-level test drives the capture path against a stub page that ignores `?tab=` and asserts
      it fails rather than writing files (stdlib only, no `plugins/` import — INV-108),
      negative-controlled by restoring the current unverified behavior.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — activation readback, duplicate
  detection, and the `--url` click fallback
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` —
  name the deep-linking requirement at the build step
- `tests/` — a guard that an un-activating page fails the capture

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-28, in the analysis stretch, on the first
  phase-3 walk ever to reach Truth Set visualization and build the chosen-language server for real
  (`Source: self-observed (assistant retrospective)`). Surfaced by capturing six tabs from a live
  Java server and then actually **opening** the images — the file names, the script's success lines,
  the manifest and the completion gate were all consistent with a correct capture.
- Priority: **Medium.** No bootcamper is misled about their *data* — the aggregates, the snapshot and
  the live app are all correct — and a conforming server never hits it. It is Medium rather than Low
  because the artifact it corrupts is the **keepsake**: five wrong images reach the recap PDF
  labeled as five different tabs, and nothing at any stage says otherwise. Not High because the
  contract does specify the requirement, so the fix is a guard against non-conformance rather than a
  correction of wrong guidance.
- MCP re-check: **n/a (no Senzing fact).** The defect is entirely in a bundled script and the
  module's own verification chain. `get_capabilities` was called at the start of this run to date
  it: server **1.33.0**, 2026-08-28.
- Upstream: not applicable — plugin-side only.

## Deviations from this spec, and why (2026-08-31)

- ⛔ **Criterion 1 is NOT met as written, and this is the disclosure rather than a
  reinterpretation.** The spec asks the script to "verify the active tab matches the requested tab
  before saving" by reading back the rendered page. **No backend available to this plugin can do
  that on the `--url` path.** Playwright and Selenium can evaluate script against a live page, and
  neither is installed here or required by the bootcamp (both are optional imports that return
  `False` when missing); the backend that actually does the capturing on this machine — and the one
  the walk that found this defect used — is the **headless-Chrome CLI**, which cannot evaluate an
  expression for us. `_measure_chrome_cli` is the existing proof: to read **one number** off a page
  it has to patch a local copy of the HTML and re-serve it, and its own docstring records that "a
  remote URL cannot be patched". A rendered readback would therefore be unavailable in exactly the
  configuration where the defect occurs.
- **What shipped instead: a source-level pre-flight that catches the failure before any file is
  written.** `_supports_deep_linking` asks whether the served page's own code reads the query string
  at all — which `?tab=` activation requires — and refuses the run when it does not. It cannot prove
  a page honors `tab` *correctly*, and says so in its docstring; it cannot produce a false failure on
  a conforming server, which must read the query string to meet the contract. The spec's **outcome**
  criterion (3) is fully met — a non-conforming server now produces a non-zero exit and a message
  naming activation, instead of six confidently-named PNGs — and criterion 2 (byte-identical
  captures) is met by `_identical_groups`, which also deletes the offending files, since at most one
  can show the tab it is named for and nothing can determine which.
- **Proposed change 3 (give the `--url` path the snapshot path's click fallback) is deliberately not
  implemented.** `_ACTIVATE_JS` works by injecting a script into a temp copy of a local file; a live
  page cannot be patched, so running it against a server needs a browser-automation session driving
  navigation, activation and screenshot together — which is the optional dependency the capture step
  exists to avoid (INV-052/INV-066/INV-048 keep it dependency-optional). Refusing the run is the
  honest alternative: it tells the implementer their server is missing a required contract feature,
  where a fallback would have silently compensated for it and left the next consumer to find out.
- ⚠️ **The spec's INV-122 reading is corrected, and it means no new invariant was needed.** The spec
  says this is "adjacent to INV-122 but outside it", reasoning from INV-122's *absent-tab* clause.
  INV-122's **first** clause already forbids the outcome outright: screenshots "MUST be captured as
  one image per tab, **never as several views of one tab**, and each file MUST be named after the tab
  it shows". Six files showing one tab is precisely that. So the guarantee was registered all along
  and only the enforcement was missing for this mechanism — which is why the new rule at
  `phase1-visualization.md` cites INV-122 rather than minting an ID.
