# `sz_verbatim_check` is unsatisfiable for a numeric source value

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The verbatim check harvests the allowed value set from the source record by collecting **only string
values**. Any source value stored as a JSON **number** therefore can never appear in the allowed set,
and both ways of emitting it fail:

- emit it faithfully, as a number → invisible to the checker;
- emit it as a string → fails the gate.

ICIJ stores `REL_POINTER_KEY` as a number, so the gate failed on **all 53,321 relationship rows**
whichever choice was made. The gate is not strict here — it is *unsatisfiable*, and it blocks a
mapping that is correct.

Resolving it took an empirical engine test to confirm Senzing links disclosed relationships for both a
string and a numeric pointer key — work a bootcamper should not have to do to get past a validation
step.

## Root cause

**Upstream, in the MCP server's workflow resource — re-verified 2026-07-28** by fetching
`sz_verbatim_check.py` (5,042 bytes) from the URL `download_resource` returns, so this is current
behavior and not a stale report.

`collect_strings()` appends only on a string test:

```python
if isinstance(obj, str):
    out.append(obj)
```

It recurses through lists and dicts but captures no other primitive, so numeric and boolean source
values are never harvested. The collected strings feed `allowed_values()`, which normalizes and splits
them into a set; validation is then:

```python
if v.strip() not in allowed:
    violations.append(...)
```

Membership is whole-value, not substring — which is the right design (it stops `"M"` matching inside
`"Male"`) and is exactly what makes the numeric case impossible: a stringified number has no
counterpart in a set built only from strings.

**Plugin-side gap.** The plugin routes bootcampers through this gate — `phaseD-validation.md:162`
names "the verbatim check" among the structural checks the module relies on — but nowhere records that
the check cannot express a numeric source value. So a bootcamper whose data has numeric identifiers
meets an unsatisfiable gate with no guidance, and the natural readings are both wrong: "my mapping is
broken" or "I must stringify everything".

## Proposed change

**Upstream (report, do not silently work around) — see `## Source`.** Ask Senzing to harvest
numeric and boolean source values too (stringified for comparison), or to exempt an emitted value whose
JSON type matches the source's.

**In the plugin, meanwhile:**

1. **Record the limitation where the gate is used.** State that the verbatim check's allowed set is
   built from string source values only, so a numeric or boolean source value cannot satisfy it — and
   that this is a limitation of the checker, **not** evidence that the mapping is wrong.
2. **Say what to do about it, in this order:** confirm the emitted value is faithful to the source
   (same value, type chosen deliberately); record the exemption and its reason in the mapping notes;
   proceed. A checker limitation MUST NOT become an iterate-forever loop or a blocked module
   (INV-048) — and it MUST NOT be "resolved" by corrupting the data to satisfy the tool, which is the
   tempting move and the one that damages the load.
3. **Do not fork the resource.** The checker is delivered by the MCP server; the plugin documents the
   exemption path rather than shipping a patched copy, so the fix arrives from upstream when it lands
   (INV-080).
4. **Keep the gate's value intact.** The check exists to stop invented values reaching Senzing, and it
   is right about strings. The exemption is narrow — a value whose source form is non-string — and must
   be stated as such, not as licence to skip the gate.

## Acceptance criteria

- [ ] The plugin states that the verbatim check harvests only string source values and that a
      numeric/boolean source value therefore cannot satisfy it.
- [ ] The guidance names the exemption path — verify faithfulness, record the reason, proceed — and
      states that the mapping is not presumed wrong.
- [ ] The guidance explicitly forbids altering source values (e.g. stringifying a numeric identifier
      solely to pass the gate) to satisfy the checker.
- [ ] A numeric-identifier source does not block the module: the check reports, the reason is recorded,
      and the flow continues (INV-048).
- [ ] The plugin ships no forked copy of `sz_verbatim_check.py`; the resource still comes from the MCP
      server (INV-080).
- [ ] The upstream report is sent (or explicitly declined) and its outcome recorded here.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      limitation is a property of the checker's harvesting logic, independent of platform, and the
      guidance is about mapping decisions rather than any one language.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — where
  mapped output is validated: the limitation and the exemption path.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md` — the same, at
  the sandbox validation step.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — `:162` names the
  verbatim check among the structural checks; note the limitation so an unsatisfiable gate is not read
  as a mapping defect.
- `tests/` — assert the limitation and the no-altering-source-values rule are stated where the gate is
  used.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "sz_verbatim_check cannot pass a non-string source
  value" (2026-07-28, Module Data Quality, Mapping, and Transformation;
  `Source: self-observed (assistant retrospective)`; `Routing: mcp-server`)
- Priority: High (not stated by the reporter; assessed from impact — the gate is unsatisfiable rather
  than strict, it blocked 53,321 rows of a correct mapping, and the tempting "fix" corrupts the data)
- MCP re-check: **still reproduces on server 1.32.1, verified 2026-07-28.** `sz_verbatim_check.py`
  fetched from the `download_resource` URL still collects values under `isinstance(obj, str)` only, with
  no numeric or boolean branch, and validation is still whole-value membership
  (`if v.strip() not in allowed`).
- Upstream: **sent 2026-07-28 via `submit_feedback` (`category='bug'`)** — the entry recorded it as
  "offered to the bootcamper as a batch" (not yet sent); the maintainer approved the drafted message
  at triage and it was submitted. The submission is **anonymous** — the server captures no sender
  identity, so no follow-up on it is possible; `support@senzing.com` is the channel if this needs a
  conversation. The plugin-side change below stands regardless of whether upstream acts.
- Related specs: `specs/mapping-workflow-truncated-validation-errors.md` (the sibling
  mapping-gate reporting defect), `specs/analyzer-legacy-sublist-format-false-errors.md` (the
  precedent: an MCP-delivered validator reporting false errors, documented plugin-side while upstream
  was notified), `specs/mcp-grounding-in-every-skill.md` (INV-080),
  `specs/detect-dynamic-key-document-shaped-sources.md`

## Deviations from this spec, and why (2026-07-28)

**Re-verification confirmed the defect and added two facts the spec did not have.**

Re-fetched the current `sz_verbatim_check.py` (server 1.32.1, 2026-07-28) rather than trusting the
report. `collect_strings()` still harvests under `isinstance(obj, str)` only and the test is still
whole-value membership (`if v.strip() not in allowed`) — so the spec's root cause stands. Two
additions:

1. **There *is* an exemption hook, and it cannot help.** `is_exempt(attr)` waives an attribute when
   it is in `EXEMPT_KEYS = {"DATA_SOURCE", "RECORD_ID"}` or ends with `_TYPE`. It is **key**-based, so
   no *value* can be exempted, and `REL_POINTER_KEY` matches neither rule. The shipped guidance states
   this, because a reader who finds `is_exempt` would otherwise reasonably expect a way out.
2. **The Entity Specification does not mandate a JSON type for the relationship keys.** Confirmed via
   `search_docs(category='data_mapping')`: every `REL_POINTER_KEY` example is a string (`"ORG1001"`,
   `"ACME-1001"`, `"PER1002"`) while the `REL_ANCHOR_KEY` guidance column shows a bare `1001`. So the
   emission choice is a specification question, not a checker question — which is how the guidance now
   frames it, rather than recommending a type of its own.

**One of the spec's claims is deliberately NOT shipped.** The spec's `## Problem` records that
resolving this "required an empirical engine test to confirm Senzing links disclosed relationships for
both a string and a numeric pointer key". That is a live-engine observation which cannot be repeated
here and is not in any MCP source, so writing it into the plugin would assert an unverified Senzing
fact (INV-080). The guidance instead tells the reader to confirm the attribute's expected form via
`search_docs` at mapping time. A test asserts that sentence is *not* present, so a future edit cannot
quietly promote it.

**One affected file needed no change.** The spec listed `phase3-test-load.md` as needing the same
note "at the sandbox validation step". That file does not reference the verbatim check at all — its
only "verbatim" occurrence is the unrelated "pinned verbatim" phrasing — so adding a caveat there
would have invented a reference to a gate that step does not run. The gate is invoked from
`phase2-data-mapping.md` (mapping_workflow step 4), where the mitigation went, and mentioned in
`phaseD-validation.md`, which now carries the caveat so an unresolved violation list arriving in
Module 6 is not misread as a mapping defect.

**Acceptance criteria status.** All met. Nothing here required a live engine: the checker's behavior
was verified from the current resource, and the specification question from `search_docs`.

## Invariants introduced

- `INV-173` — Where a validation gate cannot represent a legitimate input, its finding MUST NOT be
  treated as evidence about the data, MUST NOT block the flow, and MUST NOT be resolved by altering
  the data to satisfy the gate; the limitation is named with its provenance, the exemption path is
  stated, and an MCP-delivered validator is never forked (recorded in `specs/INVARIANTS.md`).
