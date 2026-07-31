# The recommended ICIJ samples are sliced independently, so the one relationship exercise resolves to nothing

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 4 recommends the free-data catalog at
`module-04-data-collection/SKILL.md:190` and `:664`
(<https://github.com/docktermj/senzing-bootcamp-free-data>). Its
`samples/raw/icij-offshore-leaks/` directory ships four files whose ids do not overlap:

```text
officers       node_id        12000001-12000010
entities       node_id        10000001-10000010
addresses      node_id        24000001-24000010
relationships  node_id_start  10002580, 10004460, …   node_id_end  14091822, 14092925, …
=> resolvable relationship rows: 0 of 10
```

**Zero of ten** relationship rows reference any node present in the samples. Every row is
`rel_type=registered_address`, so no officer↔entity ownership link exists even in principle. And
`nodes-addresses.csv` has `name` 0% populated — those are address nodes, not entities, so they cannot
be loaded as records at all.

**Why this particular source matters.** ICIJ Offshore Leaks is the one entry in that catalog whose
distinguishing value is **disclosed relationships** — the `REL_ANCHOR`/`REL_POINTER` pattern that
nothing else in the catalog exercises, and which the Senzing Entity Specification documents as its
own feature family (verified via `search_docs`, server 1.32.3, docs index 2026-07-31 20:21 UTC: the
specification's *Feature: REL_ANCHOR* and *Feature: REL_POINTER* sections define
`REL_ANCHOR_DOMAIN`/`KEY` and `REL_POINTER_DOMAIN`/`KEY`/`ROLE` with rules and examples). As sampled,
that exercise is impossible.

**The failure is silent.** A bootcamper who follows the join keys in good faith gets zero resolved
relationships and no error — the files parse, the mapping is valid, the load succeeds, and nothing
relates. The reporting bootcamper recovered by modelling the `service_provider` column instead, which
is present on all ten entity rows, but that is a different exercise from the one the source was
chosen for.

## Root cause

The four files were sliced **independently** — the first N rows of each — rather than from a
connected subgraph. In a graph export, taking the head of a node file and the head of an edge file
is almost guaranteed to produce a disjoint set, because edge rows reference ids drawn from the whole
population, not the first ten.

The defect is in `senzing-bootcamp-free-data`, a **sibling repository under the same owner as this
plugin** (`docktermj`), not in the plugin's skills and not in the MCP server. So the entry's
"routing: unclear" resolves: the fix is available to the same maintainer, in a different repo — which
this spec cannot change, since `feedback-to-specs` writes only under `specs/` and `feedback/`.

## Proposed change

Two halves, in different repositories. **Only the second is in this repo's gift**, and the spec must
not pretend otherwise.

1. **In `senzing-bootcamp-free-data` (out of scope here, recorded so it is not lost):** re-slice from
   a connected subgraph — choose N relationship rows first, then include exactly the nodes they
   reference. Add a line to the sample README stating whether the files join. Exclude
   `nodes-addresses.csv` from the loadable set, or document that it is address nodes rather than
   entities.
2. **In this plugin, now:** Module 4 recommends the catalog, so it should say what the ICIJ sample
   currently supports. Either (a) note at the recommendation that the shipped slices do **not** join
   and the relationship exercise is unavailable until the upstream fix, pointing at
   `service_provider` as the workable alternative; or (b) drop ICIJ from the recommended set until it
   joins. **(a) is preferred** — the source is still usable for entity mapping, and a documented
   limitation teaches more than a removal.

⚠️ **Do not have the plugin re-slice or repair the data.** Module 4 recommends a catalog; it does not
own it. A plugin that rewrites sample data creates a second, divergent copy and hides the upstream
defect — the same reasoning INV-173 applies to forking an MCP-delivered validator.

⚠️ **Do not describe the sample as broken.** Three of the four files are fine and the entity mapping
exercise works. What is unavailable is specifically the disclosed-relationship exercise.

## Acceptance criteria

- [ ] Module 4's recommendation of the free-data catalog states that the ICIJ sample's four files do
      not currently join, and that the disclosed-relationship exercise is therefore unavailable from
      it.
- [ ] It names `service_provider` as the workable alternative on that source, so the recommendation
      stays useful rather than becoming a warning with no path.
- [ ] It says `nodes-addresses.csv` carries address nodes with `name` unpopulated and is not loadable
      as records.
- [ ] The note is dated and marked as an upstream condition to re-check, so it can be retired when
      the samples are re-sliced — not left as a permanent claim about a repo that may have changed.
- [ ] The plugin does not modify, re-slice, or vendor the sample data.
- [ ] A test asserts the ICIJ caveat is present wherever the catalog is recommended (`:190`, `:664`)
      — both sites, checked by opening the file (INV-182).
- [ ] **Not runtime-verified:** the id ranges above are the bootcamper's observation of 2026-07-27.
      Confirming them means fetching the four files from the free-data repo, which this triage did not
      do. The plugin text must present the finding as dated and re-checkable, not as a current fact.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — the catalog recommendation
  at `:190` and `:664`.
- `tests/` — the caveat-at-both-sites assertion.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "free-data ICIJ Offshore Leaks samples were
  sliced independently, so the relationships file joins to nothing" (2026-07-27, Module: Data
  collection / Data Quality, Mapping, and Transformation; Priority: Medium; `Source: self-observed
  (assistant retrospective)`).
- Priority: **Medium**, as filed. Nothing errors; a bootcamper loses the one exercise that source
  exists to provide, and learns it only by getting zero results.
- MCP re-check: **n/a for the defect (server 1.32.3, docs index 2026-07-31 20:21 UTC).** The sample
  data is not served by the MCP server — `get_sample_data` serves CORD datasets, a different catalog.
  The one Senzing fact this spec touches, that `REL_ANCHOR`/`REL_POINTER` is a documented feature
  family, was confirmed via `search_docs` this session. Tools called: `get_capabilities`,
  `search_docs`.
- Upstream: **not applicable to Senzing.** The entry routed this "unclear"; it resolves to
  `docktermj/senzing-bootcamp-free-data`, a sibling repo under the same owner as this plugin. That is
  a maintainer action in another repository, outside what this skill may write.
- Related specs: none. `specs/record-preview-requires-registered-source.md` touches ICIJ only
  incidentally.
