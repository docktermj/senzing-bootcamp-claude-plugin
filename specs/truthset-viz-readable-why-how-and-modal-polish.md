# Render Why?/How? as a plain-language explanation, with raw JSON collapsed and the modal properly designed

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The Why? and How? modals — the surfaces whose entire purpose is to make Senzing's reasoning legible
— presented a wall of raw `JSON.stringify` output as their **only** view. The bootcamper asked for a
human-readable summary of the resolution reasoning (match keys, feature scores, resolution steps),
with the full raw JSON still available but tucked behind a collapsible twistie.

After the content was made readable, they asked again — this time about the presentation: the dialog
was functionally correct but visually plain (flat table, no score-severity color coding, minimal
header treatment), and this is the module whose whole purpose is a strong first impression.

The payloads are genuinely hard to read raw: `MATCH_INFO.FEATURE_SCORES`,
`WHY_KEY_DETAILS.CONFIRMATIONS`, `RESOLUTION_STEPS[].VIRTUAL_ENTITY_1/2`. Dumping them undercuts the
one thing the feature exists to do.

## Root cause

The contract specifies the **payload** and is silent on the **rendering**.

`visualization-api-reference.md:211` — "`result` is the SDK `why_*` response JSON verbatim."
`visualization-api-reference.md:227` — "`result` is the SDK response JSON verbatim."
`visualization-api-reference.md:332-335` — the tabs "render the explanation (match keys, feature
scores, construction steps) in a modal", with no statement of what "render" means.

The spec never distinguishes *"verbatim data must be available"* from *"verbatim data is the
rendering"*, so `JSON.stringify(result, null, 2)` into a `<pre>` satisfies it literally. The
bootcamper's own diagnosis is correct on this point.

Separately, the module's brand-tokens requirement (INV-081, applied via
`scripts/brand_tokens.py`) is understood as covering the app shell — tabs, header, dark theme — with
nothing extending it to the entity-detail modal's internal content. Nothing marks the modal as a
primary "wow moment" surface deserving that treatment.

## Proposed change

In `visualization-api-reference.md`, specify the Why?/How?/Records rendering contract:

1. **Plain-language summary is the primary view.**
   - **Why?** — match level, match key, and resolution rule, then a per-feature table:
     feature · this record · compared-to record · score · bucket.
   - **How?** — a numbered step-by-step merge narrative ("Step 1: record A from CUSTOMERS
     established the entity. Step 2: record B was added because NAME scored 97 (CLOSE) and DOB
     scored 100 (SAME)…").
2. **Color-coded score-bucket badges,** mapped from the Senzing buckets the contract already
   enumerates (`visualization-api-reference.md:298-299`): `SAME`/`CLOSE` → green,
   `PLUS`/`LIKELY`/`PLAUSIBLE` → amber, `UNLIKELY`/`NO_CHANCE` → red. Take the actual colors from
   `scripts/brand_tokens.py` (INV-081) rather than hardcoding hex values, and do not rely on color
   alone — keep the bucket name as text so the badge is readable without color perception.
3. **Raw JSON available but collapsed.** Keep the verbatim `result` reachable behind a
   `<details>`/twistie, closed by default. Restate the existing "verbatim" language as *the API
   returns verbatim; the UI summarizes and offers verbatim on demand* so it can no longer be read as
   mandating a raw dump.
4. **Modal chrome.** A real header bar (title plus a circular close button) visually separated from
   the body, a subtle entrance animation, and deliberate spacing/typography — styled from the brand
   tokens like the rest of the app. Add an explicit statement that entity-detail dialogs
   (Why?/How?/Records) are a primary "wow moment" surface and receive the same polish as the
   headline tabs, so the brand-tokens requirement is understood to reach inside the modal.
5. **Keep the failure path intact.** The `{"entity_id": …, "error": …}` 200-response contract
   (`visualization-api-reference.md:211-213`, `:229`) is unchanged: a summary view must render the
   error legibly rather than an empty table, and one entity's failure never breaks the tab.

Note for the implementer: parse these responses against
`get_sdk_reference(topic='response_schemas')` rather than inferring field names — three field-name
guesses in these exact payloads produced silently blank output in the same session (see
`specs/lookup-sdk-response-schemas-before-parsing.md`). A summary view makes that failure mode worse,
because a mis-named field renders as a blank cell instead of visibly-absent JSON.

## Acceptance criteria

- [ ] `visualization-api-reference.md` specifies a plain-language summary as the **default** Why? and
      How? view, with the field-by-field content each must show.
- [ ] The raw SDK `result` is specified as available behind a collapsed `<details>`/twistie, never
      shown by default; the "verbatim" wording no longer reads as mandating a raw dump.
- [ ] Score buckets render as color-coded badges sourced from `scripts/brand_tokens.py` (INV-081),
      with the bucket name always present as text (not color-only).
- [ ] The spec states that entity-detail dialogs are a primary "wow moment" surface and requires
      header-bar chrome, close affordance, and brand-token typography/spacing inside the modal.
- [ ] An `error`-bearing why/how response renders as a legible message in the summary view and does
      not break the tab.
- [ ] A build following the spec alone — with no bootcamper requests — produces readable Why?/How?
      modals on first run.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): stated as
      rendering requirements over the documented payloads, with no dependency on the Java or Python
      reference build, and no CDN/webfont dependency (INV-091).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — lines ~195-230 (`/api/why`, `/api/how` payload notes) and ~332-335 (tab rendering): add the
  summary-first rendering contract, the twistie requirement, badge mapping, and modal-chrome
  requirements
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — tab
  descriptions (lines ~238-243) reference the same rendering contract instead of "render Senzing's
  explanation … in a modal"
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — the shipped reference implementation
  must render the summary view, so Module 7 builds modeled on it inherit it
- `plugins/senzing-bootcamp/scripts/brand_tokens.py` — confirm score-bucket badge colors exist as
  tokens; add them if absent

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Human-readable Why?/How? modals with raw JSON
  behind a collapsible twistie" (2026-07-24, Truth Set visualization)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "More polished visual design for the
  Why?/How?/Records dialog" (2026-07-24, Truth Set visualization)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Bake this session's Truth Set visualization
  polish into the module spec as the default baseline" (2026-07-24) — points 4 and 5
- Priority: Medium
- Related specs: `specs/truthset-viz-entity-actions-and-aggregate-drilldowns.md` (defines the Records
  action these modals join), `specs/apply-senzing-style-guide-to-deliverables.md` (brand tokens,
  INV-081), `specs/visualization-why-how-and-clickable-histogram.md` (added why/how in the first
  place), `specs/lookup-sdk-response-schemas-before-parsing.md`
