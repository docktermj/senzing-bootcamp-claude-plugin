# The required-parameter guard covers two of the nine MCP tools the plugin calls

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`tests/test_mcp_call_contracts.py` is the guard against the defect class that once made Module 5's
mapping workflow unexecutable — a call the plugin documents without a parameter the schema marks
required. Its coverage is a hand-maintained pair:

```python
# Tools whose schema marks a parameter REQUIRED, and where the plugin must show it.
REQUIRED_PARAMS = {
    "mapping_workflow": ("file_paths", "workspace_dir"),
    "analyze_record": ("workspace_dir",),
}
```

The plugin calls **nine** MCP tools that mark parameters required. Checked against the live schemas,
server **1.32.8, 2026-08-11**:

| Tool the plugin calls | Required by schema | In `REQUIRED_PARAMS`? |
|---|---|---|
| `mapping_workflow` | `file_paths`, `workspace_dir` (on `start`) | ✅ |
| `analyze_record` | `workspace_dir` | ✅ |
| **`generate_scaffold`** | **`language`, `workflow`** | ❌ |
| **`get_sdk_reference`** | **`topic`** | ❌ |
| **`sdk_guide`** | **`topic`** | ❌ |
| **`reporting_guide`** | **`topic`** | ❌ |
| **`search_docs`** | **`query`** | ❌ |
| **`explain_error_code`** | **`error_code`** | ❌ |
| **`get_sample_data`** | **`dataset`** | ❌ |

`grep -c generate_scaffold tests/test_mcp_call_contracts.py` returns **0** — the tool is not
mentioned in the contract test at all, despite the plugin calling it at 16 sites.

**The plugin is currently correct**, which is why this is a guard defect rather than a live one. Both
`generate_scaffold(workflow='initialize')` shorthand sites —
`module-03-system-verification/phase1-verification.md:196` and `module-02-sdk-setup/SKILL.md:1098` —
sit in files that name `language=` elsewhere (1 and 4 occurrences respectively), so a reader has the
parameter available. Nothing is broken today.

**What is missing is the tripwire.** If a future edit introduced a `sdk_guide()` with no `topic`, or
a `generate_scaffold` call in a file that never names `language`, the suite would stay green — the
same silence that let the original `workspace_dir` defect survive three audits and 399 tests.

**Severity is bounded by one thing worth stating:** a call missing a required parameter is rejected
at the client's schema-validation layer before it reaches Senzing, so the failure mode is a broken
step, not a wrong answer. That is a loud failure — but it happens in front of a Bootcamper, mid-module.

**INV-169 applied.** Not a conditions mismatch: the required lists were read from the live schemas
this session, and the plugin's call sites were counted against those same lists.

## Root cause

`REQUIRED_PARAMS` was written to fix the two tools that had a *known* defect —
`dry-run`'s originating finding was `mapping_workflow`'s missing `workspace_dir`, and
`analyze_record` shares the parameter. It was never generalised to the other seven, and its comment
(*"Tools whose schema marks a parameter REQUIRED"*) reads as though it enumerates them all. A guard
that names its subject in the general and covers a subset is the "guard narrower than the invariant
it claims to enforce" class, here in a test rather than an invariant.

Nothing catches it: the dict is data, so no assertion fails when a tool is absent from it, and the
test's own name (`test_mcp_call_contracts`) promises the whole contract.

## Proposed change

**Extend `REQUIRED_PARAMS` to every tool the plugin calls, and make the omission visible.**

1. Add the seven missing entries with their schema-required parameters as tabulated above.
2. **Add a completeness assertion** — the real fix. Derive the set of MCP tools the plugin actually
   calls (the test already scans skill text for tool names when checking action enums) and assert
   every one of them appears as a key in `REQUIRED_PARAMS`, or in an explicit
   `NO_REQUIRED_PARAMS` set for tools that genuinely have none (`get_capabilities`,
   `submit_feedback`, `download_resource`, `find_examples` — whose requirement is conditional on
   mode and needs its own check or an explicit exemption with a reason).
   Without this, the next tool the plugin starts calling is silently uncovered again.
3. **Record `find_examples` deliberately.** Its schema requires *one of* `query`, `repo`+`file_path`,
   or `repo`+`list_files` — a conditional the flat dict cannot express. Either give it a bespoke
   check or list it in the exemption set **with the reason**, so a later reader does not read its
   absence as an oversight.

**What stays.** Everything the test already does: the action-enum check against
`VALID_WORKFLOW_ACTIONS`, the `FORBIDDEN_WORKSPACE_DIRS` check (INV-200), and the existing two
entries. This widens coverage; it removes nothing.

**No plugin change is required** — the call sites are correct today. If extending the guard surfaces
a site that is *not*, that is a second finding and needs its own spec rather than a quiet fix here.

## Acceptance criteria

- [ ] `REQUIRED_PARAMS` names every MCP tool the plugin calls that has required parameters, matching
      the live schemas — the nine in the table above.
- [ ] A completeness assertion fails when the plugin calls a tool absent from both `REQUIRED_PARAMS`
      and an explicit exemption set, so a newly-called tool cannot be silently uncovered.
- [ ] `find_examples`'s conditional requirement is either checked or exempted **with its reason
      recorded in the code**, never merely omitted.
- [ ] **Re-verification clause:** implementing this requires the live schemas to still mark these
      parameters required — re-read them via the loaded tool definitions before trusting the table
      above. If a tool's required list has changed, use the server's, not this spec's.
- [ ] The test is negative-controlled per tool: removing a required parameter's mention from a
      calling file fails the suite. Verify the mutation actually landed.
- [ ] The existing action-enum and `FORBIDDEN_WORKSPACE_DIRS` checks still pass unchanged.
- [ ] Stdlib-only, no `plugins/` import (INV-108).

## Affected files

- `tests/test_mcp_call_contracts.py` — `REQUIRED_PARAMS` and the new completeness assertion.

## Source

- Dry run: `dry-run` phase 1 (MCP call contracts), 2026-08-11. Server **1.32.8**, docs index
  **2026-08-11 13:35 UTC**.
- Suite green at the time of the finding: 1596 passed, 3 skipped, 1263 subtests.
- **Verified correct in the same pass, so the next run need not re-check:** every `action=`,
  `topic=`, `category=`, `workflow=`, `platform=` and `dataset=` literal the plugin uses is in its
  schema's enum — 34 distinct literals across all tools, including the alias topics `methods` and
  `functions` which resolve to `parameters`. That is the class that originally broke Module 5, and
  it is clean.
- Priority: **Medium.** No live defect; the cost is that the tripwire for the highest-severity
  MCP defect class covers two of nine tools while reading as though it covers all.
- MCP re-check: the required-parameter lists were read from the live tool schemas this session; no
  Senzing *documentation* claim is asserted.

## Invariants introduced

- `INV-201` — Every MCP tool the plugin calls MUST be classified in
  `tests/test_mcp_call_contracts.py` (`REQUIRED_PARAMS` / `CONDITIONALLY_REQUIRED` with a
  reason / `NO_REQUIRED_PARAMS` with a reason), the three sets MUST partition the server's
  tool list exactly, and a required parameter whose name is a substring of its own tool
  MUST be matched on a token boundary (recorded in `specs/INVARIANTS.md`).

## Deviations from this spec, and why (2026-08-11)

Implemented as specified in substance; four things differed, all on the server's evidence.

**1. Server is 1.32.9, not 1.32.8.** Re-read this session from the loaded tool schemas and
`get_capabilities`. Every required list in the spec's table is unchanged, so the seven
additions went in as tabulated.

**2. `mapping_workflow`'s requirement is not schema-required.** The spec's table column
reads "Required by schema" and puts `file_paths`, `workspace_dir` under it. The live
schema's `required` array for `mapping_workflow` is **empty**, and `workspace_dir` is
nested inside the free-form `data` object — the requirement is prose/contract-level
("The call WILL FAIL without both") and conditional on `action='start'`. It stays in
`REQUIRED_PARAMS`, because it is the defect that made Module 5 unexecutable and no schema
field would ever have caught it, but the dict now marks provenance per entry
(schema-required vs contract-required) rather than implying all nine are schema-required.

**3. `submit_feedback` is classified conditional, not "no required params".** The spec
lists it among tools that "genuinely have none". Its schema marks none required, but its
prose requirements are conditional on `category`: `license_request` needs firstname + work
email + how_heard, the other categories need `message`. That is the same shape as
`find_examples`, so it went into `CONDITIONALLY_REQUIRED` with the reason recorded, and the
consent guard (INV-135) is named as what actually covers its risky branch.

**4. One defect the spec did not predict, found while implementing.** The existing check
was `param in text` — a plain substring test. `error_code` is a substring of
`explain_error_code`, so that tool's entry could **never fail**: every calling file
contains the tool's own name. Matching is now token-boundary
(`mentions()`), and `test_the_param_scan_is_not_satisfied_by_the_tool_name` pins it. Had
the spec's seven entries been added under the old matcher, `explain_error_code` would have
been a guard that reads as coverage and cannot fail.

**Kept deliberately:** the `any()`-across-calling-files semantics. The spec said "What
stays. Everything the test already does", and per-file matching would reject legitimate
sites — a file calling `mapping_workflow(action='status')` needs no `file_paths`. The
per-tool negative control therefore strips the token from *every* calling file, not one.

**No plugin change was required**, as the spec predicted: all 11 tool+param mutations only
failed after redaction, so every call site is correct today.
