# The source-set coloring rule is stated three times and verified nowhere, so it recurred in a generated Java app

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

On **2026-08-25, plugin 0.5.2**, a Module 7 results app built in **Java** colored each graph node
from `data_sources[0]` — the entity's **first** source. 294 of 5,619 entities spanned two or more
sources; every one of them would have rendered in a single-source color, beneath a legend saying
they were single-source.

`Html.java` lines 459-461, generated during the run:

```java
SRC[(d.data_sources||[])[0]]
```

read for fill, stroke and stroke width alike. `Model.graph()` already emitted the full
`data_sources` list per node, so the data was present and only the client-side encoding was wrong.

⛔ **This is the exact defect `graph-nodes-are-colored-by-their-first-data-source` fixed on
2026-08-17 (commit `8644bb6`), and the run was on a plugin that contained that fix.** The bundled
Python reference is correct — `senzing_viz_server.py:932` defines
`srcKeyOf(d){…s.slice().sort().join("|")…}` and `:1052-1054` use it for all three attributes, with
the explanatory comment at `:927`. The version the Bootcamper ran, 0.5.2, was tagged `881e262` on
2026-08-17 17:41, hours **after** the fix landed at 01:12 the same day (confirmed:
`git merge-base --is-ancestor 8644bb6 881e262`).

So the fix held where it was applied and the defect reappeared where the rule had to be *followed*
rather than *inherited*: in code the guide wrote in the Bootcamper's chosen language.

Nothing errors, nothing looks broken, and the headline finding of the entire bootcamp — the same
organization found in more than one system — is invisible in the tab built to display it.

## Root cause

⚠️ **The entry's diagnosis — *"the shipped reference it warns about still contains the defect"* —
is false as of 2026-08-17, and correcting it is what redirects this spec.** The reference is fixed.
The rule is also stated, prominently, in three places:

1. **The any-language contract**, under a heading that marks it required —
   `module-03b-truthset-visualization/visualization-api-reference.md:1013-1037`:

   ```text
   ### Coloring graph nodes (required — behavior, in every language, INV-259)

   ⛔ **A node is colored by its whole source set — never by one member of it (INV-259).** […]
   **Fill, stroke and stroke width all derive from that key**; leaving any one of the three
   reading the first source keeps a partial version of the same misencoding.
   ```

   It even carries the failure it prevents, with the prior run's numbers.

2. **Module 7 step 3c** — `module-07-query-visualize-discover/phase1-query-visualize.md:516-523`:

   ```text
   - ⛔ **Color each graph node by the entity's whole source SET, not by its first source** — see the
     contract's "Coloring graph nodes". ⚠️ **This is the rule the Truth Set cannot test.**
   ```

3. **INV-259** (`specs/INVARIANTS.md:351`), which binds every language.

**So the gap is not a missing rule. It is that nothing ever checks the generated app against it.**
Three prose statements and an invariant are enforced, at runtime, by the guide reading and applying
them — and on 2026-08-25 that did not happen. The Truth Set module builds the app two modules before
Module 7 states the rule at the point of use, so the reader has to connect a rule stated in module
3b's contract to code they wrote in module 3b and are now re-pointing at new data.

**The test data structurally cannot provoke it.** Nearly all Truth Set entities sit in one source,
where `data_sources[0]` *is* the entity's source and first-source coloring looks correct. The defect
is invisible in the module that builds the app and only misreports in Module 7, on the Bootcamper's
own data, after the module that could have caught it has closed. It is a defect whose test data
guarantees a pass — which is exactly what the entry observed, and what the contract's own ⚠️ already
says.

**No executable check exists.** `visualization-api-reference.md:1036` requires the legend to name
each combination it colors, and nothing verifies that requirement against a built app. There is no
counterpart to `capture_screenshots.py`'s manifest for the *encoding* — the shipped guards check
prose sites, not generated output.

## Proposed change

The rule is stated enough. Give it a check that fails.

**1. Add an encoding self-check to the visualization contract, as behavior.** Require the server —
in any language — to expose, and the build step to verify, that the number of distinct color keys
the legend names equals the number of distinct **sorted source-set keys** present in the nodes it
draws. That equality is false exactly when a node is colored by one member of its set: first-source
coloring collapses every combination onto a single-source key, so the legend key count drops below
the distinct source-set count. It is the entry's own suggestion, and it is cheap — both numbers are
already computed to draw the graph.

⚠️ **State it in the any-language contract, not only in the Python reference (INV-002).** A rule
that reaches generated code solely through the reference is the failure INV-164 and INV-190 each had
to record case by case — and it is precisely the failure that produced this recurrence.

**2. Make it a step the guide runs, not a property it asserts.** In the Truth Set module's build
step, after the app is up and before the teardown gate, verify the two counts against the running
server and report the result. On a mismatch, stop and fix the encoding — do not proceed to capture,
because the screenshots become a permanent keepsake of the wrong picture.

**3. Give the check data it can fail on.** The Truth Set cannot provoke this with its own entities.
The verification does not need cross-source *entities* to be meaningful: with a single data source
the distinct-source-set count is 1 and the check is vacuous, so state that plainly and have the step
say the check was **not exercised** rather than passed (INV-265 — an empty match is a failed or
unrun check, never agreement). Where the Truth Set registers more than one source, the check is
live.

**4. Add the pointer at the point of use.** Module 7 step 3c already states the rule; add that the
encoding check runs again when the app is re-pointed at the Bootcamper's data, where the count is
non-trivial and the defect actually shows.

## Acceptance criteria

- [ ] `visualization-api-reference.md` states the encoding self-check as **behavior in every
      language**: distinct legend color keys MUST equal distinct sorted source-set keys over the
      nodes drawn.
- [ ] The check reports **not exercised** (not "passed") when the drawn nodes carry fewer than two
      distinct source-set keys, per INV-265.
- [ ] The Truth Set module's build step runs the check against the running server before screenshot
      capture, and stops on a mismatch rather than capturing.
- [ ] Module 7 step 3c states the check re-runs when the app is re-pointed at the Bootcamper's data.
- [ ] The bundled Python reference implements the check — and continues to color by the whole source
      set (`srcKeyOf`), unchanged by this spec.
- [ ] A test asserts the check is stated in the any-language contract and invoked at both build
      sites, so it cannot come to live only in the Python reference (INV-002).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — state the encoding self-check as behavior beside the existing "Coloring graph nodes" section
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — run
  the check after the server is up, before capture
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  step 3c: re-run it on the Bootcamper's data
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — implement the check in the reference
- `specs/INVARIANTS.md` — register the verification requirement alongside INV-259
- `tests/` — a guard asserting the contract states it and both build sites invoke it

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: The visualization reference colours
  graph nodes by their FIRST source, and the Truth Set cannot expose it" (2026-08-25, Module: Truth
  Set visualization; `Source: self-observed (assistant retrospective)`)
- Priority: High
- MCP re-check: n/a (no Senzing fact). Both the rule and the defect live in the plugin's own
  reference server and its any-language contract — `data_sources` is a field `Model` builds itself.
  No SDK method, flag, response shape or server behavior is asserted. Verified against the shipped
  files and git history on 2026-08-25.
- Upstream: not applicable.
- Related specs: `specs/graph-nodes-are-colored-by-their-first-data-source.md` (implemented
  2026-08-17, `8644bb6` — established INV-259; this spec adds the verification it lacks),
  `specs/source-colors-from-discovered-data-sources.md`,
  `specs/entity-graph-legend-labels-participation-counts-as-single-source.md`,
  `specs/a-check-that-matches-nothing-must-not-report-agreement.md` (INV-265)

## What the re-check changed in this spec

The entry asked for the **reference implementation to be fixed**. It already was, eight days before
the run, and the version the Bootcamper was on contained the fix. Writing the spec from the report
would have re-specced a completed change and re-established an invariant that already exists.

The finding that survives is stronger than the one reported: **INV-259 plus three prose statements
did not prevent the defect from recurring in generated Java.** The subject is therefore redirected
from "fix the reference" to "the rule has no executable check, and the only module that builds the
app cannot provoke it with its own data" — which is the entry's *second*, unelaborated suggestion,
promoted to the substance of the spec.

## Deviations from this spec, and why (2026-08-26)

No Senzing fact is involved, so nothing was re-verified against the server; the spec's own
correction (the reference was already fixed) was re-confirmed by reading `senzing_viz_server.py`.
Two deviations.

1. **The check reuses `SOURCE_KEY_SEP` rather than the literal separator this spec's prose implies.**
   `Model.color_keys()` already builds the full single-pass key set using the module's
   `SOURCE_KEY_SEP` constant. The first implementation of `_encoding_check` hardcoded `"|"` twice,
   which would let the separator drift between the palette allocation and the check meant to
   validate it. Found while diagnosing an invalid negative control — `color_keys()` at `:564` carries
   a byte-identical source-derivation line, so a single-occurrence string replacement edited the
   wrong method.

2. **The invariant is deferred, not skipped.** `## Affected files` predicts `specs/INVARIANTS.md`;
   it was deliberately left untouched because Step 5 requires maintainer sign-off on invariant
   wording and the maintainer was away. INV-259 (the encoding) and INV-265 (not-exercised reporting)
   are cited at all three new rules, but neither registers the *verification* requirement, which is
   this spec's actual finding. The drafted wording and follow-up actions are in this spec's
   `specs/IMPLEMENTED.md` entry under `DEFERRED INVARIANT`.

## Invariants introduced

- `INV-270` — A visualization the Bootcamper's code builds MUST expose the count of distinct sorted source-set keys on its graph endpoint, and the build step MUST compare it against the legend's distinct color-key count before capture — stopping on inequality, and reporting **not exercised** rather than a pass below two keys (INV-265). Stated as behavior in the any-language contract, not only in the bundled reference (INV-002). (recorded in `specs/INVARIANTS.md`, approved 2026-08-27.)
