# A step names what to select without naming the route that supplies it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Four steps tell the guide to produce MCP-sourced content but leave out the one thing the
MCP-first invariant makes essential: **where the content comes from**, or **which of several
returned items to use**. In a plugin whose ⛔ rule is "never fill a Senzing fact from training
data", a step that names an outcome without naming a route is an instruction whose only
frictionless completion is the forbidden one.

Observed in a phase-3 walk on 2026-08-22, following the files as written:

1. **`module-01-business-problem/phase1-discovery.md:112-113`** — on a pattern pick, Step 3 says
   to "use it as a template (pre-fill source types, suggest matching criteria, adapt to their
   context)". No tool, no query, no source. The natural completion is to write plausible source
   types from memory; the walk instead had to invent a query (`search_docs` returned the DSR
   article, whose own examples are CRM / account system / HR / claims / files) to stay compliant.

2. **`module-02-sdk-setup/SKILL.md:1450-1465`** — Step 9 says to use
   `generate_scaffold(workflow='initialize')` and "pick the snippet that creates an engine". On
   server 1.33.0 that call returns **fourteen** snippets, none with inline code, and nothing in
   the response marks which create an engine. The walk picked
   `python/initialization/engine_priming.py` by inferring from the filename. Compare Module 3's
   Step 4 (`module-03-system-verification/phase1-verification.md:288-300`), which faces the same
   listing and **names the file** — `loading/add_records_loop.py` over `loading/add_records.py`,
   with the discriminator (reads `INPUT_FILE` vs hardcoded records) spelled out. Step 9 is the
   same problem without the answer.

3. **`module-00-entity-resolution-concepts/concepts.md:78-80`** — "How Senzing handles it" tells
   the guide to cover "principle-based matching (frequency, exclusivity, stability)", but the
   suggested-query list above it carries no query for that phrasing. A query composed from the
   step's own words (`Senzing principles frequency exclusivity stability attribute behavior`)
   returned the **A1ES custom-feature configuration article** — ~8 KB of `addFeature`,
   `sz_configtool` and stewardship material aimed at a much later audience — which is precisely
   the wrong-altitude retrieval the file's own ⛔ warns self-composed queries produce.

4. **`module-03b-truthset-visualization/phase2-close.md:20-24`** — the pre-advancement self-check
   says to "count and compare the tab identifiers in the saved HTML against the server's" without
   naming the marker they are written with. On a phase-3 walk the first attempt matched
   `data-tab="…"`, found **zero in both files**, and reported "tab sets match: True" — a vacuous
   pass. The real marker is `id="tab-<name>"`; the second attempt returned six identifiers from each
   side and compared them meaningfully. A check that passes by matching nothing is worse than no
   check, because it certifies what it never compared.

## Root cause

INV-212 requires the retrieval strategy to live **at the step**, not merely in the tool's name.
These three steps state the *what* and omit the *how*, so each leaves the guide to compose a
route. Where the plugin has done this work — `concepts.md`'s suggested-query list, Module 1
Step 14's prescribed query plus its "do not append the category" warning, Module 3 Step 4's named
snippet — the walk followed it and got the right material first time. Where it has not, the walk
either improvised a query or inferred from a filename.

This is a gap in the plugin's own instructions, not a Senzing fact. All three routes were
exercised live against **MCP server 1.33.0, docs index 2026-08-20 17:33 UTC, 2026-08-22**.

## Proposed change

Give each step its route, in the shape the plugin already uses elsewhere:

1. Module 1 Step 3: name the tool and a query for the template pre-fill, and say plainly that the
   source types and matching criteria come from that response rather than from the guide's
   knowledge of the pattern.
2. Module 2 Step 9: name the snippet to pick, with its discriminator, exactly as Module 3 Step 4
   does — and state that a count or position in the listing is not the selector.
3. `concepts.md`: add a suggested query for the frequency/exclusivity/stability material, and note
   the altitude hazard (the A1ES article is configuration guidance, not primer material).

## Acceptance criteria

- [ ] Module 1 Step 3 names the MCP route that supplies the template's source types and matching
      criteria; a reader following the step cannot satisfy it without an MCP call.
- [ ] Module 2 Step 9 names the initialization snippet that creates an engine and the property
      that identifies it, so the choice does not depend on inferring from a filename.
- [ ] `concepts.md`'s suggested-query list covers the frequency/exclusivity/stability item its
      "What to teach" section requires, and warns that the A1ES configuration article is the wrong
      altitude for this module.
- [ ] `phase2-close.md`'s tab-set comparison names the marker (`id="tab-<name>"`) the
      identifiers are written with, so a regex that matches nothing cannot pass the check.
- [ ] A test asserts that each of these four steps names its route (tool or marker), so the routes cannot be dropped
      again silently.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — Step 3's
  template-pre-fill instruction gains a route.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 9 names the snippet.
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md` — one more
  suggested query plus the altitude note.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase2-close.md` — the
  tab-set check names its marker.
- `tests/` — a guard that each of the four steps names its route.

## Source

- Feedback: `/dry-run` phase 3, analysis from Bootcamp preparation through System verification
  (2026-08-22; Entity Resolution Concepts, Discover the Business Problem, SDK setup;
  `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: server 1.33.0, 2026-08-22 — all three routes exercised live.
  `generate_scaffold(language='python', workflow='initialize')` returned 14 snippets with
  `content` absent and only `raw_url`/`size_bytes`/`line_count`, none flagged as engine-creating;
  `search_docs('Senzing principles frequency exclusivity stability attribute behavior')` returned
  the A1ES custom-feature article as its top substantive hit; `search_docs` reached the DSR
  article for Module 1 Step 3's material only via a query the file does not suggest. No plugin
  claim was contradicted by the server — the gap is in the plugin's instructions.
- Upstream: not applicable
- Related specs: `specs/overview-bullet-count-is-stale-after-the-note-bullet.md` (same walk)
