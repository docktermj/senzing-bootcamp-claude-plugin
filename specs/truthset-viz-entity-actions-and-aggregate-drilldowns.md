# Require consistent entity actions and drill-down on every aggregate view in the visualization app

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Across two bootcamps, nine separate feedback entries reported the same shape of gap in the Truth Set
visualization app: an entity is shown, but you cannot get at the records behind it; an aggregate is
shown, but you cannot get at the entities behind it.

- **Cross-Source** overlap matrix cells show counts; clicking does nothing (reported twice).
- **Match Keys** rows show `match_key` + count; clicking does nothing.
- **Record Merges** cards list constituent records as static text — clicking a record ("CUSTOMERS
  record 1063") shows nothing.
- **Search / Probe** results carry **Why?**/**How?** but no way to see the entity's constituent
  records ("I want a way to see all 4 records for that entity").
- **Search / Probe** never got the **Records** button that the Merge Statistics bucket drill-down
  received, because they are separate rendering code paths.
- **Record Merges** later showed the *inverse* problem: once a Records button existed, the card
  printed the same records inline **and** behind the button — pure duplication.
- The **Search / Probe** tab opens as a blank search box with no known-good example queries, so a
  bootcamper exploring a Truth Set they did not build has no idea what to type; a failed first
  search is a bad first impression of the product.

The bootcamper's own framing: "Every other aggregate view in this app already drills down to the
underlying entities; *this* was the one remaining dead end" — written three separate times about
three different tabs. Each was patched ad hoc during a session, so a first-time bootcamper who does
not think to ask gets the plainer build.

## Root cause

The visualization contract specifies **data and tabs**, not the **interaction set**, so each
entity-rendering code path is wired independently and drifts.

1. **Two aggregate endpoints carry no entity references.**
   `visualization-api-reference.md:251-265` — `/api/overlap` returns only `sources` + `matrix`.
   `visualization-api-reference.md:267-282` — `/api/matchkeys` returns only `match_keys`,
   `distinct`, `capped`. Neither has the per-bucket entity list that `/api/stats` has
   (`bucket_entities`, cited at `visualization-api-reference.md:319`), so there is no data to wire a
   drill-down to. Both Cross-Source and Match Keys drill-down requests are therefore **spec gaps,
   not implementation bugs**.
2. **The action set is specified per-tab, in prose, and inconsistently.**
   `visualization-api-reference.md:318` gives Record Merges "cards with **Why?**/**How?** actions";
   `:332-335` says "The Record Merges tab and each Search / Probe result carry **Why?** and **How?**
   actions" and separately that Merge Statistics bars drill down "each linking to its **How?**
   explanation". Nowhere is a single canonical per-entity action set defined, so **Records** was
   never required anywhere and appears wherever an implementer happened to add it.
3. **No records endpoint exists.** There is no `/api/records?entity_id=` in the endpoint list
   (`visualization-api-reference.md:20-308`). `/api/merges` (`:95-110`) already returns per-record
   `name`/`address`/`phone`/`identifiers`, but only for multi-record entities and only as that tab's
   payload — nothing backs a Records action from Search / Probe, Cross-Source, or Match Keys.
4. **Inline listings are specified.** `phase1-visualization.md:238-240` specifies Record Merges as
   "cards showing each multi-record entity's constituent records", which is what a Records button
   makes redundant. The spec mandates the duplication it later reads as unfinished.
5. **Search hints are unspecified.** `visualization-api-reference.md:324` lists the Search / Probe
   tab's endpoints only; nothing requires example queries, so they exist only when asked for.

## Proposed change

Specify the interaction contract once, in `visualization-api-reference.md`, so it binds every
language implementation instead of the one that happened to receive the feedback.

1. **One canonical per-entity action set.** Define **Records · Why? · How?** as the action set shown
   wherever an entity appears with actions — Entity Graph node detail, Relationship Network, Record
   Merges cards, Merge Statistics bucket drill-down, Cross-Source cell drill-down, Match Keys row
   drill-down, and Search / Probe results. Never a subset. State it once and have each tab's
   description reference it rather than re-listing buttons.
2. **Add `/api/records?entity_id=<id>`** returning the entity's constituent records with the fields
   `/api/merges` already carries (`data_source`, `record_id`, `name`, `address`, `phone`,
   `identifiers`). It backs the Records action everywhere, including for single-record entities.
   Its data MUST also be embedded in the standalone snapshot so Records works offline (unlike
   `why`/`how`, which degrade per `visualization-api-reference.md:337-343`).
3. **Extend both aggregate endpoints with a parallel entity list**, capped like the existing
   patterns and with the cap surfaced, never silent:
   - `/api/overlap` → `cell_entities`, keyed by source pair (and by the diagonal single-source
     cell).
   - `/api/matchkeys` → `match_key_entities`, keyed by match key.
   Then require Cross-Source cells and Match Keys rows to be **clickable**, opening the underlying
   entity list with the canonical action set — the pattern `/api/stats`'s `bucket_entities` already
   establishes.
4. **No redundant inline record listings.** Where an entity list offers a Records action, it MUST
   NOT also print constituent records inline. Record Merges cards show entity name, record count,
   and match key plus the actions. Update `phase1-visualization.md:238-240` accordingly.
5. **Require pre-verified search hints.** The Search / Probe tab MUST ship a small set of example
   queries as clickable chips that fill the box *and* run the search on click. They are generated
   per-dataset from the loaded data and **verified live to return at least one match** before being
   offered — a hint that returns nothing is worse than no hint. Never leave the tab as a bare box.
6. **Record the onclick/`JSON.stringify` pitfall.** Add an implementation note: when building
   `onclick="…"` attributes by string concatenation, never embed `JSON.stringify()` output inside a
   double-quoted attribute — the browser truncates the attribute at the first embedded quote and the
   handler silently never fires. This bug masks itself because calling the same function from the
   console works. It is language-agnostic front-end JS, so it belongs in the shared contract, not in
   one language's build notes. (Distinct from `specs/escape-viz-snapshot-script-payload.md`, which
   covers escaping the snapshot's embedded `<script>` payload.)

Cap-and-degrade behavior follows the existing `/api/features` precedent
(`visualization-api-reference.md:298-307`): bound the cost, surface the cap, and never let a
failure block the artifact (INV-077).

## Acceptance criteria

- [ ] `visualization-api-reference.md` defines the **Records · Why? · How?** action set once, and
      every tab that renders an entity with actions references it; no tab specifies a subset.
- [ ] `/api/records?entity_id=<id>` is specified with its response shape, and is required to be
      embedded in the standalone snapshot (Records works with no network access).
- [ ] `/api/overlap` specifies `cell_entities` and `/api/matchkeys` specifies `match_key_entities`,
      each with an explicit cap and a `capped`-style signal that the client MUST surface.
- [ ] The Cross-Source and Match Keys tab descriptions require clickable cells/rows that open the
      underlying entities with the canonical action set.
- [ ] The Record Merges tab description states constituent records are NOT rendered inline;
      `phase1-visualization.md` matches.
- [ ] The Search / Probe tab description requires per-dataset example-query chips that both fill and
      run the search, generated from the loaded data and verified to return ≥1 match before being
      offered.
- [ ] The onclick/`JSON.stringify` quoting pitfall is documented in the shared contract as a
      language-agnostic requirement.
- [ ] A build following the spec alone — with no bootcamper requests — yields Records on every
      entity surface and a working drill-down from every aggregate view.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      contract is stated as data + interaction requirements, with no dependency on the Java or
      Python reference build.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — add `/api/records`; extend `/api/overlap` and `/api/matchkeys`; define the canonical action set;
  require search hints and aggregate drill-downs; add the onclick pitfall note
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — tab
  descriptions (lines ~231-250): drop inline record listings, add Records to every entity surface,
  add search hints
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  the step-3c build inherits the same contract (lines ~203-224); confirm no local re-listing of a
  narrower action set
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — the shipped reference implementation
  that Module 7's build is modeled on must satisfy the extended contract

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Bake this session's Truth Set visualization
  polish into the module spec as the default baseline" (2026-07-24, Truth Set visualization) —
  points 1, 2, 3, 6, 8
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Make clickable, pre-verified search hints a
  standard part of the Search / Probe tab spec" (2026-07-24)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Add a 'Records' button to Search / Probe
  results, matching Merge Statistics" (2026-07-24)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Make Cross-Source heatmap cells clickable,
  drilling down to entities with Records/Why?/How?" (2026-07-24)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Drill down from a Match Keys row to the
  entities carrying that match key" (2026-07-24)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Remove redundant inline record listing from
  Record Merges cards now that a Records button exists" (2026-07-24)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_12.md` → "Cross-Source matrix cells aren't clickable
  for drill-down" (2026-07-23)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_12.md` → "Record Merges tab doesn't let you view an
  individual record's data" (2026-07-23)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_12.md` → "Search / Probe results don't let you view an
  entity's constituent records" (2026-07-23)
- Priority: Medium (nine convergent reports)
- Related specs: `specs/visualization-why-how-and-clickable-histogram.md` (established the
  `bucket_entities` drill-down this generalizes), `specs/snapshot-static-search-results.md`,
  `specs/escape-viz-snapshot-script-payload.md`,
  `specs/truthset-viz-readable-why-how-and-modal-polish.md`,
  `specs/truthset-viz-graph-label-toggles-and-scale-aware-defaults.md`
