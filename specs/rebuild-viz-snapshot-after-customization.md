# Rebuild the visualization snapshot after any customization, before the purge

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Found while capturing per-tab screenshots to fix the recap-PDF defect reported alongside it.

During the Truth Set visualization module the bootcamper asked for two design simplifications.
They were implemented, verified on the live server, and confirmed by the bootcamper as looking
good: the "Record Merges" tab removed, and the standalone "Relationship Network" tab replaced by
a "Show only entities with relationships" toggle on Entity Graph — six tabs instead of eight.

The standalone snapshot at `docs/visualizations/truthset_verification.html` was built **before**
those changes and was never regenerated. Comparing the two directly:

- snapshot `ALL_TABS`: `graph, network, merges, stats, matchkeys, features, overlap, probe` (8)
- customized server `ALL_TABS`: `graph, stats, matchkeys, features, overlap, probe` (6)

The snapshot also contains no `Show only entities with relationships` control, so it lacks the
replacement functionality as well as carrying the removed tabs.

Because the module purges the Truth Set records at close, the snapshot **cannot be regenerated
later** — by the time the discrepancy surfaced at graduation, the data it needed was gone.
Deleting the two tabs from the saved HTML would not fix it either: that removes the relationship
view without providing the toggle that replaced it.

The snapshot is the artifact the bootcamper keeps and the one embedded in the recap; the live
server is torn down at module close. So the permanent record shows a UI the bootcamper explicitly
asked to have changed, and it **contradicts the recap prose in the same section**, which states
both tabs were removed. Anyone reading the recap sees a claim and a screenshot that disagree.

Generalizing: any in-module customization to a visualization is silently lost from the keepsake
unless the snapshot is rebuilt, and the purge makes the loss irreversible.

## Root cause

Three ordering and verification gaps, all in the Truth Set visualization module.

1. **The snapshot is built once, before the live server.**
   `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md:163`
   — "### 2.2 Always produce the standalone snapshot **first** (the guarantee)" — builds it at
   2.2 and starts the live server at 2.3. That ordering is correct for the INV-077 guarantee
   (the artifact exists even if the server never runs), but nothing re-enters 2.2 after a later
   change. A customization made during the guided tour lands on the server only.

2. **The completion gate checks existence, not agreement.**
   `phase2-close.md:6-25` verifies the checkpoints, that the snapshot file is present and
   non-empty, and that it was built from `records_total > 0`. It never compares the snapshot
   against the server it is supposed to represent, so an eight-tab snapshot beside a six-tab
   server passes every check.

3. **The purge runs before the snapshot could ever be rebuilt.** `phase2-close.md:71-77` purges
   the Truth Set data at close; `:79` then "retains visualization artifacts". Once the purge has
   run, `phase1-visualization.md:170-178`'s build command has no `--records` source
   (`src/system_verification/truthset_data.jsonl` records are gone from the database), so
   regeneration is impossible and the defect is permanent.

## Proposed change

**1. Re-enter the snapshot build after any visualization customization.**

In `phase1-visualization.md`, add an explicit rule to the customization path: when the
visualization's code changes for any reason after 2.2 — a bootcamper request, a bug fix, a
styling change — re-run the build-only snapshot step (2.2) **and** re-verify, not just re-verify
the live server. Make it a numbered step of the customization flow rather than a note, so it is
not skipped when the change "only" affected the UI.

**2. Make the completion gate compare snapshot and server.**

Extend the `phase2-close.md` pre-advancement verification to check that the snapshot's tab set
matches the running server's current tab set, and warn when they diverge — pointing at step 2.2
as the remedy. Non-blocking, consistent with the rest of the module's gates: warn and continue,
never strand the bootcamper. This is a cheap textual comparison (both are generated from the
same source), and it is the check that would have caught this.

**3. Order teardown strictly after regeneration.**

Make the purge the **last** action of the module. Sequence `phase2-close.md`'s Step 4 so that:
snapshot rebuild-if-needed → snapshot/server agreement check → screenshot capture (which needs
the live server for Search / Probe — see
`specs/per-tab-screenshot-capture-and-grounded-captions.md`) → server termination → purge. The
snapshot must never be left un-rebuildable while the data is still present.

**4. State the constraint where the customization happens.**

Add one line to the guided-tour/customization guidance: the snapshot is the keepsake and the
live server is disposable, so a change that is not in the snapshot did not happen as far as the
bootcamper's permanent record is concerned.

## Acceptance criteria

- [ ] After any change to the visualization's code following step 2.2, the standalone snapshot is
      rebuilt before the module closes, and the rebuilt file reflects the change.
- [ ] The completion gate compares the snapshot's tab set against the live server's and warns on
      divergence, naming step 2.2 as the fix; the warning never blocks module completion.
- [ ] The Truth Set data purge is the final action of the module — after any snapshot rebuild,
      after the snapshot/server agreement check, and after screenshot capture.
- [ ] A run in which the bootcamper requests a visualization change ends with a snapshot whose
      tab set and controls match what they approved on the live server, and with recap prose that
      does not contradict the embedded screenshots.
- [ ] The INV-077 guarantee is unweakened: the snapshot is still built **before** the live server
      starts, so it exists even if the server never runs, and is still built from a non-empty
      record set.
- [ ] The snapshot remains self-contained and offline (INV-091) after a rebuild.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      rebuild is the language's own build-only/snapshot mode (INV-090), not a Python-only path.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` —
  require re-entering step 2.2 after any post-2.2 visualization change (`:163-184`); state the
  snapshot-is-the-keepsake constraint in the customization/guided-tour guidance.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase2-close.md` — add the
  snapshot/server tab-set comparison to the pre-advancement verification (`:6-25`); reorder Step 4
  so the purge is last (`:41-79`).
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  same rebuild-after-change rule for the Module 7 results visualization, whose snapshot is also a
  retained artifact.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "The Truth Set standalone snapshot is not
  regenerated after a live visualization customization, so it preserves the pre-change UI"
  (2026-07-26, Module Truth Set visualization;
  `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- Related specs: `specs/consolidate-truthset-viz-merges-and-network-tabs.md` (the customization
  that exposed this), `specs/fix-truthset-snapshot-empty.md` (the existing artifact-exists gate),
  `specs/docker-container-lifecycle-teardown-and-resume.md` and
  `specs/visualization-server-lifetime-and-teardown-gate.md` (teardown ordering),
  `specs/per-tab-screenshot-capture-and-grounded-captions.md` (capture must also precede the
  purge), `specs/artifact-level-verification-for-deliverables.md`.
