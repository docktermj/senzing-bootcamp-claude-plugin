# Tab coverage has no denominator for a visualization that wrote no manifest, so a skipped capture reads as a pass

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

At graduation on **2026-08-25, plugin 0.5.2**, the recap PDF carried six screenshots of the demo
Truth Set and **none** of the nine-tab application built over the Bootcamper's own resolved data.
`docs/visualizations/` held `truthset_verification-*.png` (6) and `truthset_verification-tabs.json`,
plus `entity_resolution.html` with no PNGs and no manifest.

The coverage check reported:

```text
6 of 6 captured tabs reached the recap
```

⛔ **A clean pass, measured against the only manifest that existed.** No manifest was written for
Module 7's app, so its absence was not a shortfall the check could see. The keepsake — the artifact
most likely to be shown to someone else — illustrates the bootcamp with pictures of the sample
dataset while the Bootcamper's own results, their cross-source entities and their fraud leads,
appear only as prose. That inverts which work was theirs.

## Root cause

⚠️ **The entry's diagnosis — *"Module 7's flow has no equivalent step"*, *"its phase files never
invoke the capture step"* — is false, and correcting it moves this spec somewhere more useful.**

Module 7 has required capture since **2026-07-23** (`08302b7`), hardened **2026-08-21** (`e805e57`).
`module-07-query-visualize-discover/phase1-query-visualize.md:567-583`:

```text
  After generating it, capture screenshots for the recap per
  `../bootcamp-onboarding/module-completion.md` → "Capturing visualization screenshots" […]
  `{name}` = `results_visualization`. Capture **one image per tab** from the running server […]

  ⛔ **The capture tool is bundled — run it, do not assess whether automation exists.**
```

It even names this exact failure mode as one already paid for:

```text
  ⛔ **"No headless capability" is a conclusion the helper reaches and reports, never one you reach
  first.** […] A guide that skipped capture here on that assumption, without running this script,
  lost twelve recap images
```

So the step exists, names the script, names the manifest, and carries a ⛔ against skipping it. The
guide skipped it anyway. That half is a runtime adherence failure with no static remedy.

**What is a real, fixable gap is the second half: nothing noticed.**
`graduation/SKILL.md:502-522` sources the captured count externally, and correctly:

```text
   Get the captured count from an external source, never from the recap:
   - **Preferred — the capture manifest.** `capture_screenshots.py` writes
     `docs/visualizations/<name>-tabs.json` […] if `--check` reported
     `SKIPPED: tab-coverage check`, no manifest was found and this check has **not** run — say so
     rather than treating it as passed (INV-163).
```

⛔ **But that is a per-name check, and its denominator is *the manifests that exist*.** It answers
"did every captured tab reach the recap?" for each manifest it finds. It cannot answer "should there
have been another manifest?" — and with `truthset_verification-tabs.json` present, `--check` found a
manifest, ran, and passed. The `SKIPPED` branch never fires when *some* manifest exists.

This is **INV-193** one level up. INV-193 required a completeness denominator to come from outside
the artifact being measured, and the fix moved the count off the recap Markdown and onto the
manifest. The manifest is external to the recap — but the **set of manifests** is derived from
whatever capture happened to produce, which is the same self-referential shape one layer out: a
module that captured nothing contributes no denominator, so its omission is arithmetically
invisible.

The information needed to close it is already on disk and already read at graduation:
`config/bootcamp_progress.json` records `modules_completed` (Module 7 was among the 8 recorded), and
the recap records the visualization the module produced.

## Proposed change

**1. Give tab coverage a denominator that does not come from the manifests.** Derive the set of
visualizations that *should* have been captured from the modules that ran — `modules_completed` in
`config/bootcamp_progress.json`, mapped to the visualization each producing module is specified to
build (`truthset_verification` for the Truth Set module, `results_visualization` for Module 7). Check
that set against the manifests found.

**2. Report a missing manifest as an unrun check, never as a pass.** Where an expected visualization
has no manifest, graduation must say so explicitly — naming the visualization and the module that
should have produced it — and must not print an overall coverage figure that implies completeness
(INV-163, INV-193, INV-265). The existing `SKIPPED: tab-coverage check` wording is the right shape;
it simply needs to fire per **expected** visualization rather than only when no manifest exists at
all.

**3. Offer the recovery, since it is cheap and the artifacts are still there.** A missing capture is
recoverable at graduation while the snapshot HTML is on disk: `capture_screenshots.py` accepts
`--url` against a re-started server, and the backfill path already exists
(`enforce-screenshot-embed-and-backfill`). State that the remedy is to re-start the app and capture,
not to proceed with a recap that misrepresents whose data is pictured.

⚠️ **Do not make graduation blocking on this.** INV-048 makes the recap PDF unconditional — it is
always produced. The requirement here is that graduation **states the shortfall**, not that it
refuses to graduate.

⛔ **Do not re-state Module 7's capture instruction.** It is correct, prominent, and was ignored;
adding a fourth copy is the state-it-once violation (INV-179) and would not have changed this run.
The defect this spec fixes is the silence afterward.

## Acceptance criteria

- [ ] Graduation derives the set of expected visualizations from `modules_completed` (and the
      module-to-visualization mapping), independently of which manifests exist.
- [ ] An expected visualization with no manifest is reported by name, with the module that should
      have produced it, as an **unrun** coverage check — never folded into a passing figure.
- [ ] The overall coverage line cannot read as complete while an expected visualization is
      unaccounted for (INV-163, INV-193, INV-265).
- [ ] Graduation states the backfill remedy (re-start the app, re-run `capture_screenshots.py`) when
      a manifest is missing.
- [ ] Graduation still always produces `docs/bootcamp_recap.pdf` (INV-048) — the shortfall is
      reported, not blocking.
- [ ] The existing per-manifest coverage check, the `not_applicable` handling, and the
      manifest-undercount warning are unchanged.
- [ ] A test covers: expected visualization present with manifest (passes), expected visualization
      with **no** manifest alongside another that has one (reported unrun, not passed).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — expected-visualization denominator; report
  a missing manifest as unrun; name the backfill remedy
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `--check` gains the expected set so
  `SKIPPED: tab-coverage check` fires per expected visualization rather than only on no-manifest
- `specs/INVARIANTS.md` — register the expected-visualization denominator rule
- `tests/` — coverage for the missing-manifest-alongside-present-manifest case

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: Module 7 embeds no screenshots of
  its own visualization app in the recap" (2026-08-25, Module: Query, Visualize and Discover;
  `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact). The defect is in the plugin's own capture manifest, coverage
  check and graduation reconcile; no SDK method, flag, response shape or server behavior is
  asserted. Verified against the shipped files and git history on 2026-08-25.
- Upstream: not applicable.
- Related specs: `specs/embedded-image-count-needs-an-external-denominator.md` (INV-193, the same
  mechanism one layer in), `specs/embedded-of-referenced-count-needs-external-denominator-crossref.md`,
  `specs/enforce-screenshot-embed-and-backfill.md`,
  `specs/a-targeted-re-capture-truncates-the-tab-manifest.md`,
  `specs/embed-every-captured-tab-in-tab-order.md`

## What the re-check changed in this spec

The entry proposed *"Have Module 7's visualization step run the same capture-and-embed path Truth
Set visualization uses, writing its own `<name>-tabs.json`"*. That step has been shipped since
2026-07-23 and is explicit down to `{name} = results_visualization` and the exact `capture_screenshots.py`
invocation. Implementing the request as written would have added a duplicate of an instruction that
was already there and already ignored.

The subject is redirected to the part the entry got right and did not develop: the coverage check
**passed** while a whole visualization was missing, because its denominator is the set of manifests
that happen to exist. That is INV-193's own failure shape, one level out, and it is the piece that
would have caught this run.

## Deviations from this spec, and why (2026-08-26)

No Senzing fact is involved, so nothing was re-verified against the server; this spec's own
correction (Module 7's capture step already exists) was re-confirmed by reading the shipped file,
and no instruction was duplicated.

1. **`--check` gained two flags rather than reading the progress file implicitly.** `--progress`
   (default `config/bootcamp_progress.json`) supplies the denominator, and
   `--expect-visualizations` overrides it. The override exists for two reasons the spec did not
   anticipate: the tests need to set the expected set without writing a progress file, and — more
   usefully — passing `--expect-visualizations ""` reproduces the **old** behavior exactly, which is
   what lets the suite demonstrate that the fix changes the outcome on the reported fixture rather
   than merely existing (INV-265 anti-vacuity).

2. **A missing manifest is reported as `SKIPPED:` with exit 0, not as an `INCOMPLETE:` problem.**
   The spec asks for it to be reported and explicitly not blocking (INV-048), and `--check` returns 1
   for anything in `problems`. Routing it through the existing `SKIPPED` vocabulary keeps the exit
   code at 0 while still naming the shortfall, and a mutation that makes it blocking is caught by the
   guard. The coverage figure is withheld in the same branch, so nothing prints a passing number
   beside a skipped check.

3. **The invariant is deferred, not skipped.** `## Affected files` predicts `specs/INVARIANTS.md`; it
   was deliberately left untouched because Step 5 requires maintainer sign-off and the maintainer was
   away. INV-193 is cited at the rule as the mechanism one layer in, but it does not reach the
   set-of-manifests level, which is this spec's actual finding. The drafted wording and follow-up
   actions are in this spec's `specs/IMPLEMENTED.md` entry under `DEFERRED INVARIANT`.

## Invariants introduced

- `INV-271` — A completeness check whose denominator is a set of produced artifacts MUST also establish that the **expected** set was produced, from a source independent of them; an expected artifact with no manifest is reported by name as an **unrun** check and the coverage figure is withheld, without blocking the recap (INV-048). Extends INV-193 from the artifact being measured to the set of measurements themselves. (recorded in `specs/INVARIANTS.md`, approved 2026-08-27.)
