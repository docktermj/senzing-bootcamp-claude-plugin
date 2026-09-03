# The export flag set is coupled to what `_absorb` reads, and no test can see them diverge

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`senzing_viz_server.py`'s export build requests an explicit flag set (correctly — Module 7 forbids
pinning a `*_DEFAULT_FLAGS` composite there):

```python
export_flags = (
    SzEngineFlags.SZ_EXPORT_INCLUDE_ALL_ENTITIES
    | SzEngineFlags.SZ_ENTITY_INCLUDE_ENTITY_NAME
    | SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_DATA
    | SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO
    | SzEngineFlags.SZ_ENTITY_INCLUDE_ALL_RELATIONS
    | SzEngineFlags.SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO
)
```

Its **source of truth is `Model._absorb`**, ~500 lines away, which reads ten field names:
`RESOLVED_ENTITY`, `ENTITY_ID`, `ENTITY_NAME`, `RECORDS`, `DATA_SOURCE`, `RECORD_ID`, `MATCH_KEY`,
`RELATED_ENTITIES`, `MATCH_LEVEL_CODE`, `ERRULE_CODE`. **Nothing connects the two.** A field added to
`_absorb` without its flag added here comes back **absent from a real engine**, and the model renders
it blank.

⛔ **That is the silent-blank failure mode this repo has already paid for twice**, and it is
governed by an invariant the code does not cite: **INV-179** — a blank field has three causes, and
"a correct field name the flags in force do not populate" is the one nothing warns about. It is also
exactly the `WHY_KEY_DETAILS` shape fixed earlier the same day.

⚠️ **The guard cannot catch it, and reads as though it can.**
`tests/test_visualization_model_build_scales.py::test_the_two_builds_agree_on_entities_and_edges`
compares the per-record and export models and asserts they are identical — which looks like exactly
the right check. But `FakeExportEngine.export_json_entity_report(flags)` **ignores `flags`
entirely** and yields the same documents regardless, so the assertion would pass with
`export_flags = 0`. The one thing most likely to go wrong with an explicit flag set is the one thing
that test structurally cannot see.

⚠️ **The two paths would also diverge asymmetrically.** The per-record build uses
`SZ_ENTITY_DEFAULT_FLAGS`, a broad composite, so a newly-read field probably *works* there — and
fails only on the export path, which is the path Module 7 mandates for real Bootcamper data. The
Truth Set would look fine and a Bootcamper's own run would not.

## Root cause

`the-export-stream-build-is-unreachable-in-the-shipped-server` (2026-09-01) introduced the explicit
flag set to satisfy Module 7's no-DEFAULT-composite rule — correctly — and thereby replaced a broad
composite with a hand-maintained list, without recording the coupling that list now carries.

This is the **inlined constant diverging from its source of truth** class
(`production-readiness-audit` Step 7, class 7): the flag list *is* a constant whose truth lives
somewhere else, and nothing re-derives it.

## Proposed change

1. **Record the coupling at both ends, in one line each** — the cheapest fix that works, and the one
   the repo already uses for this shape:
   - beside `_absorb`: reading a new field here requires adding its flag to `export_flags` in
     `build_model`, or the export path returns it blank (INV-179);
   - beside `export_flags`: each flag is here because `_absorb` reads what it populates — the
     comment already says this; add that the list must be revisited when `_absorb` changes.
2. **Cite INV-179 at the flag set.** The rule that governs the failure is registered and named
   nowhere near the code that can cause it, which is what INV-183 exists to prevent.
3. **Make the fake engine flag-aware, or say plainly that it is not.** Either have
   `FakeExportEngine` omit flag-gated fields when the corresponding flag is absent — turning
   `test_the_two_builds_agree_on_entities_and_edges` into a real check of the flag set — or add a
   docstring saying the fake ignores flags so the test's scope is not overread. ⛔ **Leaving it
   silent is the option to avoid**: a guard that looks like it validates the flag set and does not
   is worse than no guard, which is this repo's own recorded lesson about the INV-146 guard.
4. ⚠️ **Do not "fix" this by reverting to `SZ_EXPORT_DEFAULT_FLAGS`.** The server's own production
   caution and Module 7's rule both forbid it, and the composite's membership can change between
   versions with no error raised — which is the same silent failure one level up.

## Acceptance criteria

- [ ] `_absorb` and `export_flags` each name the other as the thing to revisit when they change.
- [ ] The flag set cites INV-179 at the line.
- [ ] `FakeExportEngine` either honors flags, or documents that it does not and what that means for
      the tests built on it.
- [ ] If the fake is made flag-aware: a test asserts that dropping a flag from `export_flags` makes
      the two build paths disagree. Negative-controlled — drop `SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO`
      and confirm the match-key comparison fails.
- [ ] The explicit flag set is retained; no DEFAULT composite is reintroduced into the export call.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — `Model._absorb` and `build_model`'s
  `export_flags`.
- `tests/test_visualization_model_build_scales.py` — `FakeExportEngine` and the agreement test.

## Source

- Feedback: none — found by `production-readiness-audit` on 2026-09-01, checking whether the guard
  written with the export path could actually see the failure that path is most exposed to
  (`Source: self-observed (assistant retrospective)`).
- Priority: Low — nothing is wrong today; the flag set matches what `_absorb` reads, verified field
  by field against the installed SDK enum. What is missing is anything that keeps them matched, on
  a path whose failure mode is a silently blank field rather than an error.
- MCP re-check: **n/a for the defect** — the coupling is internal. The flag names themselves were
  verified against server **1.35.3** and the installed `senzing.SzEngineFlags` (4.4.0.26242) on
  2026-09-01 when the set was written, and are not in dispute.
- Upstream: not applicable
- Related specs: `the-export-stream-build-is-unreachable-in-the-shipped-server.md` (introduced the
  list); `why-key-details-is-documented-now-so-the-no-flag-claim-is-stale.md` (the same
  flag-gated-silent-blank class, on the why response).

## Deviations from this spec, and why (2026-09-01)

**Criterion 4 was not implemented, because implementing it as written would have written a
Senzing claim into the suite that the server does not support.**

The criterion asks for a test that drops `SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO` from
`export_flags` and confirms the match-key comparison then fails. Making that assertion
requires a flag→field mapping for `export_json_entity_report` — specifically "without
`SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO`, `RESOLVED_ENTITY.RECORDS[].MATCH_KEY` is absent
from the export document".

Re-verifying against the live server (Step 3.3) found no support for that mapping, in
either direction:

- `get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO')` —
  server 1.35.4, 2026-09-01 — returns `applies_to` naming the `get_entity` / `why_*` /
  `find_*` family and **not** `export_json_entity_report`.
- `get_sdk_reference(topic='response_schemas', filter='export_json_entity_report',
  language='python')` — the route that owns the export document — lists
  `RESOLVED_ENTITY.RECORDS[].MATCH_KEY` with **no** `requires_flags`. The only flag-gated
  paths in the entire export response are the `MATCH_KEY_DETAILS` subtree
  (`SZ_INCLUDE_MATCH_KEY_DETAILS`).

So the premise the criterion rests on — that this flag gates that field on this method —
is contradicted by the flag's own `applies_to` and unsupported by the export schema. A
test asserting it would have been an offline suite certifying a fact the server does not
state, which is the INV-080 failure mode this repo has already had to retract twice.

**What shipped instead**, satisfying criterion 3's second branch and going past it:

- `FakeExportEngine` documents plainly that it does not interpret real flag bits, so no
  test built on it can be read as validating the flag set.
- It records `flags_seen`, and `test_the_flags_argument_reaches_the_engine` asserts the
  flags argument actually reaches `export_json_entity_report` — the most direct form of
  the coupling defect, and previously unguarded.
- It gained a `strip` parameter, and `AMissingFieldIsSilentNotLoud` demonstrates the
  consequence INV-179 names: a field the engine did not return degrades to blank without
  raising. That is the mechanism that makes a missing flag invisible, asserted without
  claiming which flag would cause it.
- `EveryAbsorbedFieldIsAccountedFor` is the tripwire the spec's item 1 wanted a comment to
  be: `_absorb`'s field reads are derived by scanning (INV-246), and a new one fails the
  suite until it is looked up in the export response schema and, if flag-gated there,
  added to `export_flags`.

The contradiction itself is recorded as `MCP-NEGATIVE` at `senzing_viz_server.py:1873` and
specced separately as `export-flags-are-not-documented-against-the-export-method.md`, which
is where the question of *which* flag set should ship is put to the maintainer. Criterion 5
was honored: the explicit list is unchanged and no DEFAULT composite was reintroduced.
