# Step 1's "the prose form does NOT work" is stale on server 1.33.0, and its guard pins the stale date

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-05-data-quality-mapping/phase2-data-mapping.md:418-436` documents the step-1 advance-shape
contradiction — the tool's prose shows `profile_summary` as an object keyed by schema name while its
embedded JSON Schema declares an array — and labels the two forms:

```text
{"profile_summary": {"<schema_name>": {"record_count": N, "field_count": N}}}   ← prose, does NOT work
...
{"profile_summary": [{"schema_name": "<name>", "record_count": N, "field_count": N}]}   ← works
```

dated *"Verified on **MCP server 1.32.9**, first on 2026-08-12 and re-confirmed the same day"*.

**The `does NOT work` half is no longer true.** Measured on **server 1.33.0, 2026-08-23** while
implementing `mapping-workflow-terminates-after-five-grammar-violations`: that exact object-keyed
payload, sent as `data` on an advance from step 1, **advanced to step 2** with `status: "ok"`, the
message *"Profiling complete. 1 schema(s) found."*, **no `ENFORCEMENT NOTICE`**, and no
`grammar_violation_count` in the returned `state`. The server now accepts both shapes.

The cost is not that a reader sends the wrong payload — the plugin's advice to send the array is
still correct, because the array is what the embedded schema declares. The cost is that a reader who
tries the prose form and succeeds has caught the file being wrong about a dated, MCP-attributed
claim, on a page whose authority rests on exactly that kind of citation.

## Root cause

A dated server claim that went stale, in the one direction the offline suite cannot see (INV-108) —
and, unusually, **its guard pins the stale date, so correcting the claim breaks the test.**

`tests/test_tool_directives_do_not_override_interaction.py` →
`TheStepOneAdvanceShapeCautionIsCorrect`:

- `test_it_names_the_array_as_the_working_form` requires `send the ARRAY|array form advanced|array
  .{0,40}works` **and forbids** `send the OBJECT|object form advanced`.
- `test_it_carries_dated_provenance` requires the literal `1.32.9` **and** `2026-08-12`.

⛔ **The forbidding half is right and MUST NOT be inverted.** It exists so the caution can never
send readers to the shape the schema rejects, and that hazard is unchanged: the schema still declares
an array with `additionalProperties: false` and `minItems: 1`, and the prose form still carries no
`schema_name` key. What is stale is only the narrower claim that the object form **fails**.

⚠️ **This surfaced as a collision, not as a check.** Implementing the violation-budget spec on
2026-08-23, a first draft used the object-shape acceptance as its worked example of "a payload the
schema does not describe that the server still accepts" — and this guard fired on the phrase `object
form advanced`. Rightly: a true observation stated one sentence from guidance saying the opposite
reads as licensing the wrong shape. The example was removed and the finding recorded in
`specs/todo.md`; this spec promotes it. **Nothing scheduled would have re-asked the claim** —
`coverage_reports.py negatives` does not scan it, because it is not phrased as a tool-absence
negative.

## Proposed change

1. **Restate the label as a contract rather than an outcome.** The durable fact is *which shape the
   schema declares*, not *which one the server currently rejects — the second is what expired.
   Something like:

   ```text
   {"profile_summary": {"<schema_name>": {...}}}   ← the prose form; NOT what the schema declares
   {"profile_summary": [{"schema_name": "<name>", ...}]}   ← the array the schema declares — send this
   ```

   with a short dated note that on 1.33.0 the object form is **also accepted**, and that this
   changes nothing about which to send: the schema is the contract, acceptance can be withdrawn, and
   the typed `payload` branch drives constrained decoding off the array shape.

2. **Re-date the caution** to `server 1.33.0, 2026-08-23`, keeping the 1.32.9/2026-08-12 observation
   as the original finding rather than overwriting it — the file's convention elsewhere.

3. **Update the guard in the same change, and keep its forbidding half.**
   `test_it_carries_dated_provenance` must assert a **well-formed** version and date rather than the
   literals `1.32.9`/`2026-08-12` (`specs/guards-pinning-a-dated-negative-outlive-it.md`: a guard
   that punishes honest re-verification is a guard that gets worked around).
   `test_it_names_the_array_as_the_working_form` keeps forbidding `send the OBJECT`, and its
   `object form advanced` clause needs re-wording so a truthful statement of the new acceptance does
   not trip it — while a statement that the object form is the one to *send* still does.

4. ⛔ **Do not resolve this by deleting the caution.** The prose/schema contradiction is real,
   is what a reader meets first, and the array is still the answer. The caution is being corrected,
   not retired.

## Acceptance criteria

- [ ] `phase2-data-mapping.md` no longer claims the object form does not work, and still says
      unambiguously to send the array, with the reason given as the declared schema rather than as
      the server's current rejection.
- [ ] The caution carries a re-verified server version and date, with the original observation
      retained.
- [ ] `test_it_carries_dated_provenance` asserts a well-formed version and date rather than pinned
      literals, so a future honest re-verification does not fail it.
- [ ] `test_it_names_the_array_as_the_working_form` still fails on any text naming the object form
      as the one to send — negative-controlled by inverting the caution — while passing on a
      truthful statement that the object form is currently also accepted.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — shipped
      markdown plus a stdlib-only test (INV-108).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` —
  lines 418-436, the step-1 advance-shape caution.
- `tests/test_tool_directives_do_not_override_interaction.py` —
  `TheStepOneAdvanceShapeCautionIsCorrect`: unpin the provenance literals, re-word the forbidden
  phrase so it forbids the instruction and not the observation.
- `specs/todo.md` — remove the entry this spec supersedes.

## Source

- Feedback: none — measured on 2026-08-23 while implementing
  `mapping-workflow-terminates-after-five-grammar-violations`, recorded in `specs/todo.md` because
  it was outside that spec's scope, and promoted to a spec by `production-readiness-audit` the same
  day (`Source: self-observed (assistant retrospective)`)
- Priority: **Medium.** The plugin's advice is still correct, so no bootcamper is misrouted; what is
  damaged is the credibility of a dated MCP citation on a page built out of them. Raised above Low
  because the fix must touch a guard, and a later run that corrects the prose alone will hit a red
  suite and may reach for the wrong repair.
- MCP re-check: server **1.33.0**, 2026-08-23 — **server now contradicts the plugin.** Called
  `mapping_workflow(action='start', file_paths=[…one file…], data={'workspace_dir': …})` then
  `action='advance'` with `data={'profile_summary': {'crm': {'record_count': 2, 'field_count': 4}},
  'workspace_dir': …}` — the object-keyed prose form. Response: `status: "ok"`, step 2, no
  enforcement notice, no `grammar_violation_count`. The array form's correctness is unaffected and
  was not re-tested in isolation; the embedded step-1 schema still declares
  `profile_summary` as an array of objects requiring `schema_name`, with `additionalProperties:
  false` and `minItems: 1`. `owner-checked:` not applicable — this spec asserts no absence; the
  claim is a positive observation that a call succeeded.
- Upstream: not applicable — the server relaxing what it accepts is not a defect to report.
- Related specs: `specs/mapping-workflow-step1-prose-contradicts-its-own-advance-schema.md` (the
  caution's origin), `specs/mapping-workflow-terminates-after-five-grammar-violations.md` (the run
  that measured this), `specs/guards-pinning-a-dated-negative-outlive-it.md` (the guard pattern)
