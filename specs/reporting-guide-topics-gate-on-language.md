# `reporting_guide` withholds its content until `language` is supplied, and six call sites omit it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Several `reporting_guide` topics return **no content at all** until `language` is passed.
They answer with a `needs_input` decision tree instead — and `language` is **optional in
the schema**, so nothing about the call looks wrong. The plugin omits it at six sites.

Verified on server 1.32.2, docs indexed 2026-07-29 11:11 UTC, 2026-07-30:

| Call | Result |
|---|---|
| `reporting_guide(topic='evaluation')` | `needs_input` on `language`; `sdk_patterns`, `sql_patterns`, `design_concepts` all **empty** |
| `reporting_guide(topic='evaluation', language='python')` | full content, including the **4-Point ER Evaluation Framework** |
| `reporting_guide(topic='graph')` | `needs_input` on `language`; everything empty but one anti-pattern |
| `reporting_guide(topic='data_mart')` | `needs_input` on `language`, then **again** on `scale` |
| `reporting_guide(topic='quality')` | **full content** — this topic does not gate (only `sdk_patterns` is empty) |

So the gating is **per topic**, not universal, which is why it went unnoticed: the topic
the plugin passes most often without `language` (`quality`) is the one that works.

**The sharpest instance is `module-06-data-processing/phaseD-validation.md:86**, which
reads: "Use `reporting_guide(topic='evaluation', version='current')` for the **4-point ER
evaluation framework**". That framework is precisely what the bare call does not return —
it appears only once `language` is supplied. The step names the thing it fails to fetch.

The six sites that omit `language`:

1. `module-06-data-processing/phaseD-validation.md:86` — `topic='evaluation'` (names the framework)
2. `module-06-data-processing/phaseD-validation.md:45` — `topic='evaluation'`
3. `module-06-data-processing/phaseD-validation.md:215` — `topic='evaluation'`
4. `module-06-data-processing/phaseD-validation.md:238` — `topic='evaluation'`
5. `module-06-data-processing/phaseD-validation.md:60` — `topic='graph'`
6. `module-03b-truthset-visualization/visualization-api-reference.md:102` — `topic='evaluation'`

Two further references elide their parameters in prose —
`module-07-query-visualize-discover/phase2b-discover.md:14` (`topic='graph', ...`) and
`phase2-discover.md:15` (`topic='entity_views', ...`). They are informal citations rather
than call specs, but a guide may copy them literally, and `graph` is known to gate.

**Why this is not merely a wasted round-trip.** A guide that receives `needs_input` may
re-ask with a language and recover. But `phaseD-validation.md:86` and
`visualization-api-reference.md:102` both cite the response's *content* as the reason for
the call — the 4-point framework, and the documented shape of an exported row. A guide
that treats the gate as the answer proceeds with three anti-patterns and no framework,
and nothing in the response says content was withheld.

## Root cause

INV-136 requires satisfying a tool's **required parameters as the live schema states
them**, and using only its enumerated values. `language` is neither: the schema marks it
optional, and the server gates on it at runtime anyway. The invariant's shape does not
describe a parameter that is optional to the *validator* and mandatory to the *answer*, so
a call can satisfy INV-136 completely and still return nothing usable.

## Proposed change

1. **Pass `language='<chosen_language>'` at all six sites.** The Bootcamper's language is
   already established and is threaded through comparable calls — see
   `module-07-query-visualize-discover/phase1-query-visualize.md:221`, which already gets
   this right for `topic='quality'`. Keep `version='current'` where it is already passed.
2. **Make the two elided prose references name the parameter** rather than `...`, so a
   literal copy produces a working call.
3. **Record the behavior where the plugin routes `reporting_guide` calls** — one line in
   `bootcamp-onboarding/ground-rules.md`'s tool-routing entry noting that several topics
   withhold content until `language` is supplied, and that a `needs_input` response is a
   gate rather than an answer. This is the durable half: the six call sites are today's
   instances, the rule is what stops the seventh.
4. **Do not add `language` to `topic='quality'` calls as a correctness fix** — that topic
   returns its content without it. (Adding it would populate `sdk_patterns`, which is a
   separate improvement and out of scope here.)

## Acceptance criteria

- [ ] All six sites pass `language='<chosen_language>'`; the four that already pass
      `version='current'` keep it.
- [ ] The two prose references name `language` instead of `...`.
- [ ] `ground-rules.md` states that some `reporting_guide` topics gate on `language` and
      that `needs_input` is a gate, not an answer — placed with the existing tool routing.
- [ ] No `topic='quality'` call is changed on correctness grounds.
- [ ] **Re-verification clause:** implementing this requires
      `reporting_guide(topic='evaluation')` to still return `needs_input` while
      `reporting_guide(topic='evaluation', language='python')` returns the 4-Point ER
      Evaluation Framework. If the bare call now returns content, the gate is gone and
      this spec should be re-triaged rather than implemented.
- [ ] `tests/test_mcp_call_contracts.py` and `tests/test_sampling_and_validation_routing.py`
      pass; a test pins that no `topic='evaluation'` or `topic='graph'` call ships without
      `language`, so the seventh site fails the suite rather than the bootcamp.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — lines 45, 60, 86, 215, 238.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` — line 102.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md` — line 14.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md` — line 15.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — tool-routing entry.
- `tests/test_mcp_call_contracts.py` — the new guard.

## Not verified in this pass

`topic='entity_views'`, `topic='reports'`, `topic='dashboard'` and `topic='export'` were
not probed, so whether they gate is unknown. `entity_views` is referenced by the plugin
(elided) and is the one worth checking first.

## Source

- Sweep: `delegate-to-mcp-server`, 2026-07-30 — found while re-verifying the `data_mart`
  quote, and deliberately **not** specced then: "do the plugin's calls work?" is
  `dry-run` phase 1's question, not this skill's. Raised as a cross-boundary referral and
  specced at the maintainer's direction.
- MCP evidence: server 1.32.2, docs indexed 2026-07-29 11:11 UTC, 2026-07-30 —
  `reporting_guide` called for `evaluation` (bare and with `language='python'`), `graph`,
  `data_mart`, and `quality`. Quoted above.
- Priority: Medium — recoverable if the guide re-asks, silent content loss if it does not.
- Upstream: not applicable as a defect; a schema that marked `language` required for the
  gating topics would make this unmissable, which is worth raising separately.
- Related specs: none directly; complements INV-136.

## Invariants introduced

- `INV-192` — A parameter an MCP tool's schema marks **optional** may still be mandatory to
  its *answer*; a `needs_input` response is a **gate, not a result**, and MUST be re-called
  with the parameter satisfied rather than parsed as content or read as "this topic has no
  guidance". Where a tool gates on only some inputs, the guidance MUST say which. (Recorded
  in `specs/INVARIANTS.md` 2026-07-30, wording confirmed with the maintainer. Extends
  INV-136 from schema-declared requirements to runtime ones — a call can satisfy the schema
  completely, return 200, and still carry no substance.)
