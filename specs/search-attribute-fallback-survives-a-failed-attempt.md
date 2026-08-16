# A failed name-attribute attempt must not foreclose the attributes after it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issues:

## Problem

`Model.search` in `plugins/senzing-bootcamp/scripts/senzing_viz_server.py:465-487` walks
`SEARCH_NAME_ATTRS = ("NAME_FULL", "NAME_ORG")` and is the implementation of INV-164 — the rule
that a name search must try `NAME_ORG` as well, because an organization name sent as `NAME_FULL`
matches nothing and raises no error. On a half-organization dataset that defect made about half
the population unsearchable, which is why the fallback exists at all.

The fallback is foreclosed by the loop's error handling:

```python
for attr in self.SEARCH_NAME_ATTRS:
    tried.append(attr)
    try:
        resp = self._search_one(engine, flags, attr, query)
    except Exception as exc:
        # A later attribute failing must not discard a hit an earlier one
        # already produced; only report the error if nothing matched at all.
        if not items:
            return {"results": [], "error": str(exc), "attributes_tried": tried}
        break
    ...
```

`items` is unconditionally empty on the **first** iteration, so `if not items` is always true
there. Any exception raised while searching `NAME_FULL` returns immediately with
`attributes_tried == ["NAME_FULL"]`, and `NAME_ORG` — the whole point of the list — is never
called. The comment states the intended rule correctly; the guard implements only half of it. It
protects a hit already collected from a **later** failure, and silently converts an **earlier**
failure into "the search is over".

The consequence is the exact failure INV-164 was written to prevent, on a different path: an
organization the Bootcamper can see in their own data comes back unfound, this time with an
engine message attached that points at `NAME_FULL` rather than at the attribute that would have
matched. `search_by_attributes` is a live engine call — a transient error, a per-attribute
rejection, or a binding raising on the first shape it is handed are all enough to trigger it.

The same shape reaches the example chips. `loadProbes`
(`senzing_viz_server.py:1157-1163`) verifies each candidate chip through `/api/search` and drops
any that returns no results, so a first-attribute error additionally deletes chips that a
`NAME_ORG` search would have confirmed — the failure propagates from one query into the app's
own suggestions.

The gap is untested. `tests/test_organization_search.py::EngineErrorsAreSurfaced` pins the
mirror-image case (`test_a_hit_is_not_discarded_by_a_later_failure`: `NAME_FULL` hits, `NAME_ORG`
raises, the hit survives) and the all-attributes-raise case
(`test_error_is_reported_when_nothing_matched`), but nothing covers raise-then-hit, which is the
ordering the bug lives in.

## Root cause

The short-circuit condition tests "has anything matched **so far**" when the rule it means to
express is "are there attributes **left to try**". Those two coincide on the last attribute and
diverge on every earlier one.

## Proposed change

In `Model.search`, treat a failed attempt as an attempt, not as the end of the search:

- On an exception, record the attribute and its message and **continue to the next attribute**.
  Do not return from inside the loop.
- After the loop, if `items` is non-empty, return the results with no `error` key, regardless of
  how many attempts failed — a hit is a hit, and a failure behind it is not the Bootcamper's
  problem. (Preserves `test_a_hit_is_not_discarded_by_a_later_failure`.)
- After the loop, if `items` is empty **and** at least one attempt raised, return
  `{"results": [], "error": ..., "attributes_tried": tried}` where the error names each attribute
  that failed and its message, so "could not run" is distinguishable from "ran and matched
  nothing" and points at the right attribute (INV-115 — an empty result is a probable wrong
  query, never proven absence).
- After the loop, if `items` is empty and nothing raised, return the existing no-match response
  unchanged.
- `attributes_tried` MUST list every attribute actually attempted, including the failed ones — a
  failed attempt is still an attempt, and the UI at `senzing_viz_server.py:1138-1141` renders that
  list to the Bootcamper.

Keep the early `break` on first success: a person name must still cost one call
(`test_name_full_is_tried_before_name_org`).

This is the bundled Python reference implementation, and INV-164 binds a query or visualization
program in **any** language (INV-090/INV-124). The rule is currently written in
`plugins/senzing-bootcamp/skills/*/visualization-api-reference.md` and the visualization contract
as "try `NAME_ORG` too"; it must also say that an attribute that **errors** is retried past, not
returned on — otherwise a generated program in another language reproduces this bug from a
faithful reading of the guidance, which is how the original `NAME_FULL`-only defect spread.

## Acceptance criteria

- [ ] An engine that raises on `NAME_FULL` and matches on `NAME_ORG` returns the `NAME_ORG` hit,
      with `attributes_tried == ["NAME_FULL", "NAME_ORG"]` and no `error` key.
- [ ] An engine that raises on **every** attribute returns `results == []` with an `error` naming
      each failed attribute and its message, and `attributes_tried` listing all of them.
- [ ] An engine that raises on `NAME_FULL` and matches nothing on `NAME_ORG` returns
      `results == []` **with** the `error` present — a failed attempt must not be reported as a
      clean no-match.
- [ ] `test_a_hit_is_not_discarded_by_a_later_failure`, `test_name_full_is_tried_before_name_org`,
      `test_falls_through_to_name_org_only_when_name_full_finds_nothing`,
      `test_reports_which_attributes_were_tried` and `test_empty_query_short_circuits` still pass
      unchanged.
- [ ] `search` contains no `return` inside the attribute loop's `except` handler.
- [ ] The any-language guidance states that a **failed** attribute is retried past rather than
      returned on, so INV-164 is reproducible outside the Python reference.
- [ ] The example-chip verification in `loadProbes` inherits the fix (a chip whose entity matches
      under `NAME_ORG` survives a `NAME_FULL` error), covered by
      `tests/test_organization_search.py::ChipsAreVerifiedBeforeBeingOffered`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — `Model.search` (~465-487).
- `tests/test_organization_search.py` — new cases under `EngineErrorsAreSurfaced` for the
  raise-then-hit and raise-then-no-match orderings.
- The visualization contract / `visualization-api-reference.md` — the any-language wording.

## Source

- Claude Code Review, `Senzing/senzing-bootcamp-claude-plugin` PR #7 (comment 5135083534),
  Part 2, actionable item 1 ("an exception on the first search attribute skips the `NAME_ORG`
  fallback entirely"). Confirmed against the code on 2026-07-30.
- Priority: Medium — correctness; silently reinstates the INV-164 defect on the error path.
- Related specs: `specs/organization-search-requires-name-org.md` (established INV-164),
  `specs/pr7-review-minor-fixes.md` (the remaining PR #7 findings).

## Deviations from this spec, and why (2026-07-30)

- **The chip-verification criterion is satisfied by construction, not by the test it names.**
  The criterion cites `tests/test_organization_search.py::ChipsAreVerifiedBeforeBeingOffered` as
  covering "a chip whose entity matches under `NAME_ORG` survives a `NAME_FULL` error". That
  class asserts only that the drop-and-warn strings are present in the source; it does not drive
  the chip path. The inheritance is nonetheless real and structural — the chips verify through
  `GET /api/search`, which is `Model.search`, so there is one code path and no second fix to
  make. It was exercised behaviorally by running the rendered page's `loadProbes` under Node
  with a stubbed `/api/search` (six chips offered in merge order; one erroring candidate dropped
  only itself), but **not** against a live engine with loaded data, which this environment does
  not have. Recorded as implemented-but-not-runtime-verified rather than ticked.
- **`search_by_attributes` re-verified, unchanged.** The spec's implicit assumption that
  `_search_one`'s `TypeError` retry is still needed was checked: server 1.32.2 gives the Python
  signature as `search_by_attributes(attributes: str, flags: int = SZ_SEARCH_BY_ATTRIBUTES_ALL,
  search_profile: str = '') -> str`, so both the 2-arg and 3-arg calls remain valid and the
  retry was left exactly as it was. The C# binding takes 2 arguments where Python takes 3, which
  is why the any-language wording stays about *behavior* and not about a call shape.

## Invariants introduced

- `INV-190` — Where a lookup tries a **list** of candidates in order, an attempt that **fails**
  MUST be recorded and retried past, never treated as the end of the list; an error is reported
  only after every candidate has been attempted and none produced a result, and the report MUST
  name which candidates were tried and which failed. A guard phrased as "nothing has matched
  yet" is not a guard for "there is nothing left to try" — the two coincide only on the final
  candidate, so the defect hides on exactly the first one. (Hardens INV-164 on the error path;
  complements INV-115.) Recorded in `specs/INVARIANTS.md` on 2026-07-30, wording confirmed with
  the maintainer.
