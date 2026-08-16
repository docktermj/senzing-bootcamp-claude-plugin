# `download_resource` returns a URL, not the specification — Step 3 says to save content it never gets

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-05-data-quality-mapping/phase1-quality-assessment.md` Step 3 reads:

> Call `download_resource(filename="senzing_entity_specification.md")` to retrieve the current
> Senzing Generic Entity Specification. Use this as the authoritative reference for all attribute
> names, types, and structures in this step and every subsequent step. **Save the downloaded
> specification** to the single canonical copy at `docs/reference/senzing_entity_specification.md`

The tool does not return the specification. Verified live on **MCP server 1.32.9, 2026-08-14**, the
default response carries `mode: "url"` and a URL:

```json
{"instructions":"Download each resource from its 'url' and save to disk. …",
 "mode":"url",
 "resources":[{"filename":"senzing_entity_specification.md",
               "size_bytes":73051,
               "url":"https://mcp.senzing.com/resources/senzing_entity_specification.md",
               "on_failure":"Requires mcp.senzing.com as an allowed domain. … Fallback: call
                             download_resource with this filename and inline=true."}]}
```

So there is no "downloaded specification" to save. A guide following the step literally either
writes the JSON response (or the URL) into
`docs/reference/senzing_entity_specification.md` — leaving every later step reading attribute names
out of a file that has none — or stalls. Steps 4, 5, 5a and 6 all cite "the Entity Specification
retrieved in Step 3", and Step 5a explicitly says "do not download it again", so the damage
propagates through the whole phase from one unstated fetch.

### This is the third instance of a shape the plugin has already learned twice

The plugin carries an explicit ⛔ for both sibling tools:

- `module-02-sdk-setup/SKILL.md` Step 4 — *"⛔ `generate_scaffold` returns a **listing**, not code
  — you must fetch each file."*
- `ground-rules.md` → *"Working examples: search mode is the reliable route… **File retrieval does
  not return content at all — by design.**"* (INV-160), and
  `module-03-system-verification/phase1-verification.md` Step 3 repeats it for its own call.

`download_resource` has the same shape and no such warning anywhere in the plugin.

### The sharper half: `inline` is sanctioned here and forbidden for the siblings

Both existing ⛔s also say **never pass `inline=true`**, because the parameter is **undeclared** in
those tools' schemas and only advertised in their response prose (INV-160):

> ⛔ **Never pass `inline=true` to `generate_scaffold`.** Its own `access_steps` step 3 advertises
> that parameter as a "last resort", but the tool's **declared schema has no `inline` parameter at
> all**.

For `download_resource` the opposite is true. `inline` **is** in the declared schema, and the
tool's own guidance names it as the correct fallback:

> `inline` — *"Returns resource content inline instead of URLs. ALWAYS try with inline=false
> (default) first — only set inline=true if the URL fetch fails. Inline responses consume more
> context tokens."*

and each resource's `on_failure` says *"Fallback: call download_resource with this filename and
inline=true."*

So a guide that has correctly internalized the plugin's blanket never-inline rule will refuse the
one call where inline is the documented remedy. **That leaves a firewalled Bootcamper with no route
at all** — exactly the reader the `on_failure` text exists for — on a step every later step depends
on. The plugin currently teaches a rule that is right twice and wrong once, and never distinguishes
the cases.

## Root cause

Two causes, and the second is the one worth fixing structurally:

1. `phase1-quality-assessment.md:57-62` was written as though `download_resource` returns content.
   It predates the `find_examples` / `generate_scaffold` findings and was never revisited when those
   produced their ⛔s.
2. **The never-inline rule is stated per-tool, as a prohibition, with the reason (an undeclared
   parameter) buried in each instance.** Stated that way it generalizes wrongly. The rule that
   actually holds is *"only declared parameters may be passed"* (INV-136) — from which
   `generate_scaffold`/`find_examples` inherit a prohibition and `download_resource` inherits a
   permission. Nothing says this, so the prohibition reads as being about the word `inline`.

## Proposed change

1. **Fix Step 3 to describe the two-step retrieval.** State that the response is a **listing**
   (`mode: "url"`) carrying a URL and `size_bytes` and **no content**; that the guide must fetch
   that URL and save the body to `docs/reference/senzing_entity_specification.md`; and that it must
   **verify the saved size against the response's `size_bytes`** before using it, so a truncated or
   error-body fetch is caught here rather than surfacing as missing attribute names in Step 4. (The
   same count-check discipline INV-228 applies to dataset fetches, applied to a resource fetch.)

2. **Name `inline=true` as the sanctioned fallback for this tool, and say why it differs.** One
   clause: `inline` is **declared** in `download_resource`'s schema, unlike `generate_scaffold`'s
   and `find_examples`', so INV-136 permits it here; use it only when the URL fetch fails, per the
   tool's own `on_failure`, and note that it costs context.

3. **State the distinction once, centrally, in `ground-rules.md`'s MCP-first section** — next to the
   existing `find_examples` material — so it is not re-derived per module: three tools return
   listings rather than content, and the `inline` escape hatch is available on exactly the one whose
   schema declares it. Phrase the general rule as INV-136 ("only declared parameters may be
   passed") with the per-tool consequence, rather than as a ban on a parameter name.

4. **Sweep for other `download_resource` citations** and give each the same treatment. `Module 4`'s
   registry/analyzer references and any `sz_json_analyzer.py` retrieval are candidates — the tool
   serves seven resources and the same listing-not-content shape applies to all of them.

## Acceptance criteria

1. Step 3 states that `download_resource` returns a URL listing with no content, instructs the
   fetch-then-save sequence, and requires the saved file's size to be checked against the
   response's `size_bytes`.
2. Step 3 names `inline=true` as the fallback when the URL fetch fails, states that it is permitted
   here because the parameter is declared (INV-136), and notes its context cost.
3. `ground-rules.md` carries the three-tool distinction once, phrased as INV-136's consequence
   rather than as a ban on the word `inline`; the existing `generate_scaffold` and `find_examples`
   prohibitions are asserted **unchanged**.
4. Every other `download_resource` call site in `plugins/` either describes the two-step retrieval
   or cites the central statement; a test sweeps for call sites that do neither.
5. A test asserts the two sibling prohibitions still forbid `inline` and that the new permission is
   scoped to `download_resource` only — negative-controlled by widening the permission to all three.
6. Cross-platform (the fetch must not assume `curl`: state it as "fetch the URL", with the
   language-appropriate client, per this bootcamp's chosen-language rule) and language-agnostic.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`
- any other `plugins/` file citing `download_resource` (sweep required by criterion 4)
- `tests/test_download_resource_is_a_listing.py` (new)
- `specs/IMPLEMENTED.md`

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-14, executing Module 5 Phase 1 Step 3
  against the live server and receiving `mode: "url"` with `size_bytes: 73051` instead of the
  specification (`Source: self-observed (assistant retrospective)`). The URL was then fetched
  manually and the saved file byte-compared against `size_bytes` — 73,051 bytes, exact match — which
  is the check the step should require.
- Priority: **Medium-High.** It breaks a documented path in a way that degrades silently: a file
  containing a URL still exists at the canonical location, so Steps 4–6 proceed while reading
  attribute names from nothing. The `inline` half additionally strands the firewalled Bootcamper
  the fallback exists for.
- MCP re-check: **confirmed, server 1.32.9, 2026-08-14.** `download_resource(filename=…)` returns
  `mode: "url"`; the declared schema carries `filename`, `filenames`, `inline` and `version`, so
  `inline` is a declared parameter for this tool (contrast `generate_scaffold`, whose schema carries
  only `language`, `version` and `workflow`).

## Invariants introduced

- `INV-234` — Where an MCP tool answers a content request with a **listing** (metadata plus a URL
  rather than the bytes), every shipped call site MUST either state that shape or cite the single
  central statement of it, and a per-tool prohibition that follows from a general rule MUST state
  the general rule and the property that triggers it rather than only the forbidden token
  (recorded in `specs/INVARIANTS.md`).

## Deviations from this spec, and why (2026-08-14)

- **Every Senzing fact was re-confirmed this session rather than copied from this file.** The spec's
  citations all held on server 1.32.9, 2026-08-14: `download_resource(filename=…)` returns
  `mode: "url"` with `size_bytes: 73051` and no content, and the three declared schemas are
  `download_resource` → `filename`/`filenames`/`inline`/`version`, `generate_scaffold` →
  `language`/`version`/`workflow`, `find_examples` →
  `query`/`repo`/`file_path`/`list_files`/`language`/`max_lines`. The sibling schemas were read
  directly rather than relayed, because the shipped bullet asserts a negative about them.
- **Criterion 6's "chosen-language rule" is cited as INV-002 (language-agnostic) with INV-001
  (platforms).** The spec named the rule without an ID; those are the two that carry it.
- **The criterion-4 sweep is per-call-site, not per-file, because the first version escaped its own
  mutation.** Stripping both accountability clauses from `phase2-data-mapping.md` left the guard
  green: a bare case-insensitive `listing` matched an unrelated OFAC field name ("Listing Date (EO
  14024 Directive N)") elsewhere in the file. The rewritten sweep examines a window around each
  `download_resource(` call and requires both halves — the shape *and* what it means for the caller —
  or a citation of the central statement. This is the assert-a-token-appears-somewhere failure the
  ledger already records repeatedly; the escape is what found it.
- **Step 3 was rewritten once, jointly with
  `step3-makes-the-73kb-spec-authoritative-while-the-workflow-forbids-reading-it`**, which targets
  the same step and asked that the second-landing spec reconcile the duplicate-copy question.

## Invariants introduced — updated 2026-08-14 on maintainer review

The single invariant first recorded here was **split into two**, so each states one condition
(`INVARIANTS.md` rule 4):

- `INV-234` — the **MCP-listing case**: where a tool answers a content request with metadata plus a
  URL, every shipped call site states that shape or cites the single central statement of it.
- `INV-240` — the **general rule** extracted from it: a prohibition that follows from a general rule
  states that rule and the property which triggers it, never only the forbidden token. Filed beside
  INV-183 rather than under MCP sourcing, because it governs any derived prohibition anywhere in the
  plugin — a reader looking for it would not have found it under a tool-contract heading.

⚠️ **The original text was not cut down.** `INVARIANTS.md` rule 1 forbids deleting an invariant's
text and rule 2 allows editing only for wording that does not change meaning, so removing the clause
would itself have been a violation. INV-234 keeps it and carries a dated forward pointer naming
INV-240 as the general statement and the one to cite outside this tool family — the annotate-forward
mechanic INV-107→INV-184 and INV-050→INV-202 already established here.
