# Keep every captured tab in the recap, and embed them in the app's tab order

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two bootcamper-reported defects in the same instruction block, both about which screenshots reach the
recap and in what sequence.

**(a) Half of every visualization is deleted before it reaches the recap.** Both visualization
modules captured **one image per tab** for all six tabs — Entity Graph, Merge Statistics, Match Keys,
Feature Scores, Cross-Source, Search / Probe — exactly as required. `module-completion.md` then says
to keep the **2-3 most representative** and delete the rest. Following it, three of six were deleted
in each module, so `docs/bootcamp_recap.pdf` showed only Entity Graph, Cross-Source and Search /
Probe — the same three tabs in both sections — while **Merge Statistics, Match Keys and Feature
Scores appeared nowhere**. The bootcamper noticed the omission in the PDF and reported it.

Two consequences, both raised in the report:

1. *The recap under-represents the app.* The prose in both sections describes a six-tab
   visualization; the images show three. The same three repeating across two modules makes the app
   look narrower than it is.
2. *The dropped tabs carry the analysis.* Merge Statistics (entity-size distribution), Match Keys
   (which feature combinations drove resolutions) and Feature Scores (how tightly each feature
   agreed) are the quantitative views. Entity Graph and Cross-Source are the most *visually*
   striking — which is what "most representative" pulls toward. The rule systematically discards the
   analytical content in favour of the decorative.

**(b) Screenshots appear in capture/append order, not tab order.** Both sections presented their six
images as Entity Graph, Cross-Source, Search / Probe, Merge Statistics, Match Keys, Feature Scores.
The app's own left-to-right tab order is Entity Graph, Merge Statistics, Match Keys, Feature Scores,
Cross-Source, Search / Probe. The recap is a walkthrough of the app; a reader cannot line the images
up against the interface, and the analytical tabs land after the search screenshot rather than in the
sequence the app presents them.

The order was an artefact of how the images got there — three embedded first, three appended later
when the pruning was reversed. Nothing in the guidance specifies an order, so append order won by
default. The session's own recap was reordered by hand; the guidance is unchanged and would produce
append order again next time.

## Root cause

**(a) The 2-3 cap survived the change that made capture per-tab, and now contradicts it.**

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:148` states the rule:

> The app is a **tabbed** artifact, so capture is **one image per tab** — never several shots of one
> tab.

and `:175`, twenty-seven lines later, undoes it:

> …each file is named `{name}-<tab-slug>.png`. Keep the **2-3 most representative** (delete the
> rest) …

The cap predates per-tab capture. It made sense when `capture_screenshots.py` produced three viewport
variants of a single tab and two of them were redundant; `specs/per-tab-screenshot-capture-and-grounded-captions.md`
replaced viewport variants with one image per tab (INV-122) and rewrote the caption half of that
sentence, leaving the count half in place. Now every capture is distinct by construction, so the cap
can only delete unique content.

`plugins/senzing-bootcamp/skills/graduation/SKILL.md:277` carries the same cap into the
orphaned-screenshot backfill — "embed it into the matching `## {Module name}` section's **Actions
Taken** — 2-3 best per module" — so the safety net cannot restore what the capture step deleted, and
would itself prune a full set.

**(b) No ordering rule exists, and the source of truth is one file away.**

- `module-completion.md:175-180` requires embedding the images but says nothing about sequence.
- `graduation/SKILL.md:275-288` scans `docs/visualizations/*.png` and appends whatever is unreferenced
  — **discovery order**, which is filesystem order, not tab order.
- The tab order is already defined, once, as contract:
  `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md:446-456`
  — the tab table listing Entity Graph, Merge Statistics, Match Keys, Feature Scores, Cross-Source,
  Search / Probe with their ids and screenshot slugs. Both call sites can sort against it; neither
  is told to.

## Proposed change

1. **Drop the 2-3 cap. Keep one image per tab.** In `module-completion.md:175`, replace "Keep the
   **2-3 most representative** (delete the rest)" with: keep **every** captured tab. Each capture is
   a distinct view by construction (INV-122), so there is nothing to prune; delete only a genuine
   duplicate — two images of the same tab — which per-tab capture should not produce anyway. This is
   the bootcamper's stated position: captured tabs are retained, not pruned.

2. **Remove the selection judgement entirely.** "Most representative" is what biased the outcome
   toward the visual tabs. With every tab kept there is no selection to make, so the phrase and its
   pull disappear rather than being re-tuned.

3. **Apply the same to graduation's backfill.** `graduation/SKILL.md:277`: back-fill **all**
   unreferenced PNGs for a module, not "2-3 best". Append-only and idempotent as today (INV-085), and
   still non-blocking (INV-048).

4. **State the ordering rule in both places: the app's tab order.** Sort embedded images by the tab
   table in `visualization-api-reference.md` — Entity Graph, Merge Statistics, Match Keys, Feature
   Scores, Cross-Source, Search / Probe — never by capture, append or filename-discovery order. The
   table is the single source; cite it rather than restating the list, so a future tab change updates
   one file. Tabs absent from a run are skipped without disturbing the order of the rest, and the
   table's reserved **REMOVED** rows keep their positions so an older snapshot's images still sort
   deterministically.

5. **Make the backfill order-aware, not just append-aware.** Graduation appends by discovery, which
   is what produced the observed sequence when the restored images were added. It must insert
   according to tab order within the section's Actions Taken, while remaining append-only with
   respect to *prose* (INV-085) — it reorders only the image lines it is responsible for.

6. **Captions are unaffected.** Every retained image still gets a caption derived from the opened
   image and its tab (INV-123). Keeping six instead of three means six captions, each verified the
   same way — the retention change must not become an excuse to caption from the tab table.

## Acceptance criteria

- [ ] No instruction anywhere in the plugin directs deleting captured screenshots to meet a count;
      a grep for "most representative" and for "2-3" in the screenshot guidance returns nothing.
- [ ] A six-tab visualization yields six embedded images in that module's recap section, and a
      module with two visualizations does not lose either one's tabs.
- [ ] Merge Statistics, Match Keys and Feature Scores appear in the rendered recap PDF whenever they
      were captured.
- [ ] Embedded images in a section appear in the tab order defined by
      `visualization-api-reference.md`, in both the module-completion embed and graduation's backfill.
- [ ] The ordering rule references the tab table rather than restating the tab list, so changing the
      table changes the order in one place.
- [ ] A tab that produced no image is skipped without reordering the others.
- [ ] Graduation's backfill restores **all** unreferenced PNGs for a module, remains idempotent
      (INV-085), skips missing/unreadable images, and never blocks the PDF (INV-048).
- [ ] Every retained image carries a caption derived from the opened image and its tab (INV-122/INV-123).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the tab
      table is the any-language contract, so ordering is identical whatever the server is written in
      (INV-090/INV-124).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — `:175`: drop the 2-3
  cap and "most representative"; add the tab-order embedding rule to the procedure at `:141-195`.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — `:275-288`: back-fill all unreferenced
  PNGs, inserted in tab order.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — `:446-456`: state explicitly that the table's row order **is** the recap embedding order, so both
  call sites have something to cite.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` — `:182` ("kept the most
  representative one for this recap") models the retired behaviour; update it and keep
  `tests/test_example_recap_sync.py` passing.
- `tests/` — assert the guidance carries no keep-N cap and that both call sites reference the tab
  table for ordering.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "'keep the 2-3 most representative' discards most
  captured tabs, so the recap under-represents the visualization" (2026-07-26, Modules Truth Set
  visualization and Query, Visualize and Discover; `Source: bootcamper-reported`; `Routing: plugin`)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "recap screenshots appear in capture/append order
  rather than the app's tab order" (2026-07-26, same modules; `Source: bootcamper-reported`;
  `Routing: plugin`) — also listed as known remaining issue 1 of the session's implementation report.
- Priority: Medium (the first entry Medium, the second Low; merged because both are the same
  instruction block and the same two call sites)
- Related specs: `specs/per-tab-screenshot-capture-and-grounded-captions.md` (INV-122/INV-123 — made
  capture per-tab and left the cap behind), `specs/capture-visualization-screenshots-for-recap.md`
  (introduced the 2-3 cap when captures were viewport variants),
  `specs/enforce-screenshot-embed-and-backfill.md` (the backfill this reorders),
  `specs/consolidate-truthset-viz-merges-and-network-tabs.md` (which tabs exist),
  `specs/artifact-level-verification-for-deliverables.md` (INV-129)
