# `MCP-NEGATIVE` markers carry a rationale that the re-ask procedure never re-verifies, and three have gone stale under a still-true claim

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

An `MCP-NEGATIVE` marker has two halves that age at different rates:

1. **the claim** — "tool X does not contain Y", which `coverage_reports.py negatives` lists
   and `/dry-run` phase 1 re-asks against the live server; and
2. **the rationale** — the `owner:` clause plus the descriptive detail that says *why* the
   claim is the answer rather than a miss (how many hits came back, what they were, what a
   sibling route returns instead).

Phase 1's re-ask procedure only exercises half (1). When the claim still holds, the marker is
left alone — date, server version and rationale untouched — so a rationale that has quietly
stopped reproducing keeps standing behind a true claim, and reads as freshly reviewed.

On the 2026-08-31 sweep (server 1.35.1) **all 25 DUE claims still held**, and **three of their
rationales did not reproduce**:

| Marker | Rationale as written | What the server returned 2026-08-31 |
|---|---|---|
| `skills/module-02-sdk-setup/SKILL.md:107` | "all **four** hits are `SzProduct.get_version()`/`engine_version` SDK examples" | **ten** hits, of which three are neither — a Rust `build.rs`, `brianmacy/sz_spark: docs/BUILD.md`, and `SNAPSHOT_FORMAT_VERSION` |
| `skills/module-07-query-visualize-discover/phase1-query-visualize.md:407` | "the same call returns those three names on the entity side under `RESOLVED_ENTITY.RECORDS[]` and `RELATED_ENTITIES[]`, **which is what makes the absence a rename rather than a gap**" | neither path appears anywhere in the four schemas the call returns; the `why_entities` schema carries only `ENTITIES[].RESOLVED_ENTITY.ENTITY_ID` |
| `skills/module-07-query-visualize-discover/phase1-query-visualize.md:207` | the flag row "carries `applies_to`, `composite_members`, `description`, `name`, `response_paths` and `source_file`" | the row now also carries `depends_on` |

The 407 row is the one that costs something. Its stale half is the *entire* evidence for
calling the absence a **rename** rather than a **gap** — and that distinction is what the
plugin acts on. "Rename" means send the reader to `WHY_KEY` / `WHY_ERRULE_CODE` /
`WHY_KEY_DETAILS`; "gap" means the field is genuinely unavailable and the step needs a
different plan. The claim ("no `MATCH_KEY`, `ERRULE_CODE` or `MATCH_KEY_DETAILS` under
`WHY_RESULTS[]`") is still exactly true, and the renamed trio is still there — so the
conclusion survives. But it now survives on a justification a reader cannot reproduce, which
is indistinguishable, from the outside, from a conclusion that has gone wrong.

## Root cause

`.claude/skills/dry-run/phase1-mcp-contracts.md:41-58` (step 5) tells the sweep to "call that
tool and see whether **the claim** still holds", and gives instructions only for the case where
it does not ("correct the claim AND invert or rescope the guard"). There is no instruction for
the far more common case — the claim holds, the rationale has drifted — so a conforming sweep
leaves it, and nothing else looks at it: the offline suite cannot (INV-108), and
`coverage_reports.py negatives` reports marker **well-formedness and staleness by version**,
not whether the rationale still describes the response.

`coverage_reports.py`'s own preamble makes the same split visible — it prints the `owner:`
line for the reader to act on but validates only the claim's shape and date.

## Proposed change

1. **`.claude/skills/dry-run/phase1-mcp-contracts.md`, step 5** — add the third outcome. A
   re-ask has three, not two:
   - claim false → correct the prose and invert/rescope the guard (already written);
   - claim true, rationale reproduces → restamp server version + date;
   - **claim true, rationale does NOT reproduce → correct the rationale in the same edit as
     the restamp, and say in the report which rationales were rewritten.** A restamp that
     carries a rationale forward unchecked certifies text nobody read.

   State the reason at the step: the rationale is what a later reader uses to decide whether
   the routing conclusion still stands, so a marker whose date says "checked 2026-08-31" is
   asserting the whole comment was checked, not just its first sentence.

2. **Correct the three markers above**, each with today's re-ask as the evidence:
   - `SKILL.md:107` — "all four hits are …" → describe the current result set (ten hits, none
     giving the file's path on any platform; the version fact the corpus serves is the SDK's
     `get_version()`). The routing conclusion is unchanged.
   - `phase1-query-visualize.md:407` — drop the `RESOLVED_ENTITY.RECORDS[]` /
     `RELATED_ENTITIES[]` sentence and replace it with what actually establishes the rename:
     the same response's `why_entities` schema carries `WHY_KEY`, `WHY_ERRULE_CODE` and
     `WHY_KEY_DETAILS` (the last two gated on `SZ_INCLUDE_MATCH_KEY_DETAILS`) at the same
     depth the absent names would occupy.
   - `phase1-query-visualize.md:207` — add `depends_on` to the enumerated field list. The
     negative (no field naming a binding type) is unaffected.

3. **Prefer a property over an enumeration where the marker allows it.** Two of the three
   drifted because they pinned a *count* or an *exhaustive field list* — the shape most likely
   to age. Where the negative does not depend on it, write the discriminating property ("no
   field names a binding type") rather than the census ("carries exactly these six fields").
   This is the same lesson as `counting-the-writers-of-license-record-limit-is-the-wrong-invariant`.

## Acceptance criteria

- [ ] `phase1-mcp-contracts.md` step 5 names all three re-ask outcomes, and the
      claim-true-rationale-drifted branch says to correct the rationale in the same edit as the
      date restamp.
- [ ] The three markers above carry rationales that reproduce against server 1.35.1, restamped
      to 2026-08-31.
- [ ] A repo-level test asserts that every `MCP-NEGATIVE` marker whose rationale enumerates a
      **hit count** ("all four hits", "10 hits") is flagged by `coverage_reports.py` for
      re-description, since a count is the marker shape that cannot survive an index rebuild.
      Negative-controlled: reintroduce "all four hits" at `SKILL.md:107` and confirm the test
      fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/dry-run/phase1-mcp-contracts.md` — step 5 gains the third outcome
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — marker at :107 re-described
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — markers at :207 and :407 re-described
- `.claude/skills/dry-run/coverage_reports.py` — flag count-shaped rationales
- `tests/test_mcp_negative_rationale_shape.py` — new guard

## Source

- Feedback: none — found by `/dry-run` phase 1 on 2026-08-31, re-asking all 25 DUE negatives
  against server 1.35.1 (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — no shipped claim is wrong today; the defect is that the evidence behind
  three of them can no longer be checked, and the procedure guarantees more will follow
- MCP re-check: server 1.35.1, 2026-08-31 — **all 25 DUE claims still reproduce**; three
  rationales do not. Tools called: `get_capabilities`; `sdk_guide` (`install` × `macos_arm` /
  `windows` / `linux_apt`, `install`+`macos_arm`+`python`, `load`+`python`+`record_count=1000`,
  `configure`+`python`+`data_sources`, `configure`+`linux_apt`+`python`); `search_docs` ×5;
  `get_sdk_reference` (`flags`+`SZ_ENTITY_INCLUDE_ALL_RELATIONS`+`java`,
  `response_schemas`+`why_entities`+`python`); `generate_scaffold`(`python`,`initialize`);
  `explain_error_code`(`SENZ9000`); `mapping_workflow` (`start`, `advance` ×2).
  owner-checked: for the 407 row, `get_sdk_reference(topic='response_schemas', filter='why_entities')`
  IS the route that owns the why response document — it returned `WHY_KEY`, `WHY_ERRULE_CODE`
  and `WHY_KEY_DETAILS` and no `MATCH_KEY`/`ERRULE_CODE`/`MATCH_KEY_DETAILS`, so the claim holds
  and only its stated justification has expired.
- Upstream: not applicable — this is a plugin/skill bookkeeping defect, no Senzing-side bug
- Related specs: `counting-the-writers-of-license-record-limit-is-the-wrong-invariant.md`
