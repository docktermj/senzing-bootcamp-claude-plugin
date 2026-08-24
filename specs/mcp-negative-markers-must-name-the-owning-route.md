# An MCP-NEGATIVE marker must name the route that OWNS the fact, not only the one that omitted it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The `MCP-NEGATIVE` marker format records the tool that was **asked and came back empty**:

```text
MCP-NEGATIVE: <tool(params)> — <what is absent> — server <version>, <YYYY-MM-DD>
```
— `.claude/skills/implement-spec/SKILL.md:167`

That correctly scopes the negative to the call actually made, which is what INV-194 requires. It
does **not** record whether the tool that would *own* the fact was ever asked — and that omission is
the entire difference between a verified negative and a confabulated one.

A negative documented with a dated tool, real parameters, and a real empty result is
**indistinguishable in the file from one that asked the wrong tool.** Both look verified. Both land
on the phase-1 worklist with equal authority. The reader re-asking the marker next quarter re-asks
the route the marker names — which, if it was the wrong route, confirms the false claim again.

This is not hypothetical; it shipped during the dry run that produced this spec (2026-08-13). The
claim "Senzing reads no license-path environment variable" was recorded with a marker citing
`sdk_guide(topic='configure', …)` and `search_docs` — both genuinely empty, both genuinely asked,
both **not the owner**. The fact lives in the `compatibility_notes` of `sdk_guide(topic='load',
language=…, record_count=<above the default limit>)`, which returns `SENZING_LICENSE_FILE`. The false
claim then became an invariant (INV-208) and a guard that banned the correct variable name, and the
suite certified it — because the guard and the claim shared a premise. See
`specs/no-license-path-environment-variable.md`.

**The marker convention made the error look reviewed.** Nothing in the format prompted the question
"which tool would carry this if it existed, and did you ask it?"

## Root cause

The format has one slot for provenance, and that slot is filled by the call that produced the
*absence*. Absence evidence and ownership evidence are different claims:

- *"`configure` returns no license variable"* — a fact about `configure`. True, and by itself
  worthless as support for a general negative.
- *"`load` above the limit is the route that would carry it, and it does / does not"* — the fact the
  negative actually rests on.

INV-194 states the rule ("ask the tool that owns it before recording a negative; scope every negative
to the tool and parameters actually asked") but nothing mechanically records that the first half was
done. The marker enforces scoping and is silent on ownership, so a conformance scan can confirm a
marker is well-formed while the claim beneath it is unfounded.

Two distinct negative shapes exist, and both need the owner named — for different reasons:

1. **Routing negative** — the fact exists, this tool just isn't where it lives. The owner must be
   named so the reader goes there instead of concluding absence. (Two of the three current markers
   are this shape.)
2. **Absence negative** — the fact is not served at all. The owner must be named *and shown to have
   been asked*, because that is the only thing distinguishing this from a wrong-route error.

## Proposed change

Add a required `owner:` clause to the marker, between the claim and the server stamp:

```text
MCP-NEGATIVE: <tool(params) asked> — <what is absent> — owner: <route that owns the fact + outcome> — server <version>, <YYYY-MM-DD>
```

1. **`coverage_reports.py`** — extend `MCP_NEGATIVE` to capture `owner`, carry it through
   `find_negatives`, and print it on its own line under each marker in `report_negatives`, with the
   report's preamble stating why it is there (re-ask the **owner**, not only the omitting route).
2. **`implement-spec/SKILL.md`** — update the documented format and say what the clause is for: name
   the route that would carry the fact and what it returned; for a routing negative that is where the
   reader should go instead, and for an absence negative it is the evidence the negative rests on.
3. **The three live markers** — add the clause. None of them changes meaning; writing the owner out
   is itself informative:
   - `bootcamp-preparation/SKILL.md` — `owner: get_capabilities carries the language set` (a routing
     negative; the surrounding prose already says so).
   - `module-02-sdk-setup/SKILL.md` — `owner: same call's compatibility_notes state the Python SDK is
     Linux-only — the absence IS the answer`.
   - `module-05-data-quality-mapping/phase2-data-mapping.md` — `owner: the step-2 validator's
     rejection names it ('embedded_master' requires 'embedded_in')`.
4. **`tests/test_dated_negatives_are_marked.py`** — require a non-empty `owner:` clause on every
   marker, and keep the existing four-field parse. Negative-control by stripping the clause.
5. **Register the rule as an invariant**, since it is a durable authoring constraint and the repo
   requires every such rule to be registered.

⛔ Do **not** make the clause optional-with-a-warning. An optional provenance field is filled in
exactly the cases where the author already knows the answer, and omitted in the cases this exists to
catch.

## Acceptance criteria

- [ ] `MCP_NEGATIVE` in `coverage_reports.py` parses `owner` as a required field; a marker lacking it
      does not match, so it surfaces as missing rather than as well-formed.
- [ ] `coverage_reports.py negatives` prints each marker's owner clause and states in its preamble
      that the owner is what must be re-asked.
- [ ] All three live markers carry an accurate `owner:` clause.
- [ ] `implement-spec/SKILL.md` documents the new format and the clause's purpose, distinguishing the
      routing case from the absence case.
- [ ] A guard fails when any live marker omits the clause; negative-controlled by stripping it from
      one marker and confirming the failure lands.
- [ ] The report remains read-only, stdlib-only, imports nothing from `plugins/`, and exits 0
      whatever it finds (INV-052/INV-108).
- [ ] A new invariant registers the rule, and its enforcing test cites it back.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/dry-run/coverage_reports.py` — the regex, `find_negatives`, `report_negatives`.
- `.claude/skills/implement-spec/SKILL.md` — the documented format.
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — marker.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — marker.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — marker.
- `tests/test_dated_negatives_are_marked.py` — the guard.
- `specs/INVARIANTS.md` — the new invariant.

## Source

- Feedback: none — dry run 2026-08-13. The defect the convention failed to catch was found in phase 3;
  this spec generalizes it at the maintainer's request. `Source: self-observed (assistant retrospective)`
- Priority: High — it is the mechanism by which a whole class of false claim passes review, and the
  class has now produced three instances (`senz7221-now-names-its-own-remedy`,
  `explain-error-code-now-owns-senz7426`, and the license-variable error), the third one reaching a
  registered invariant and a guard.
- MCP re-check: server 1.32.9, 2026-08-13 — the owner clauses written for all three live markers were
  confirmed against the server this session: `get_capabilities` carries the language set;
  `sdk_guide(topic='install', platform='macos_arm', language='python')` returns only the Linux-only
  compatibility note; and `mapping_workflow` step 2 rejects a payload lacking `embedded_in` with
  `'embedded_master' requires 'embedded_in'`.
- Upstream: not applicable — this is a plugin-authoring convention.
- Related specs: `specs/no-license-path-environment-variable.md` (the instance that motivated it),
  `specs/guards-pinning-a-dated-negative-outlive-it.md` (which established the marker).
