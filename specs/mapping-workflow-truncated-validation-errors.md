# Handle a `mapping_workflow` rejection whose error text is truncated

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`mapping_workflow` completed end to end for the first data source (PPP_LOANS). For NOMINO-RISK, its
step-3 validation **rejected the submitted mapping payload twice**, and the returned error text was
truncated before the part naming *what* was invalid. With no readable reason, a third attempt would
have been guesswork, so the bootcamper was offered a choice and elected to have the remaining two
mappers written directly against the Entity Specification instead — still running all three real
quality gates (analyzer, verbatim check, routing report), which passed.

The MCP server instructions are explicit that JSON mappings should come from `mapping_workflow`
rather than being hand-coded, and `phase2-data-mapping.md:13` repeats it: "NEVER hand-code or guess
Senzing attribute names". When the validator rejects a payload without a legible reason, **the
documented path is unusable and the fallback is exactly the hand-authoring the tool exists to
prevent** — for two of three sources, in the module where mapping correctness matters most.

## Root cause

**Primary cause is upstream, in the Senzing MCP server, and is not fixable in this repository.**
`mapping_workflow`'s step-3 validation returns a truncated error string rather than the full
validation output or a structured list of per-field problems. Nothing in the returned text names the
offending field, so the payload cannot be corrected and resubmitted. Marked **Unverified from this
repository** — the truncation was observed once, in a live session; reproducing it requires calling
the MCP server with a payload it rejects, which is outside this repo's test surface.

**The plugin-side gap is real and is fixable here.**
`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md:207-222`
already carries an **"Availability-aware mapping validation"** pattern for one failure mode — a
validation script that is *unavailable* (HTTP 404) degrades to optional/best-effort so the bootcamper
is never blocked "because of a 404". There is **no equivalent handling for a validator that runs and
rejects with an unusable reason.** The skill assumes a rejection is actionable, so the agent's only
documented options are to retry blindly or to improvise — as happened here.

Nor is there guidance on capturing the raw rejection for the maintainer: the truncated text was the
only evidence, and it was not preserved in a form that would help diagnose the upstream defect.

## Proposed change

Two tracks: the upstream request, and the plugin-side handling that makes the situation recoverable
regardless of when upstream lands.

**Upstream (Senzing MCP server) — file and track, do not block on**

Request via `submit_feedback` that `mapping_workflow` step-3 validation failures return the **full**
validation error, or a structured list of per-field problems, rather than a truncated string. Even a
bounded list — "first 10 problems, N total" — would make the tool recoverable. This is the actual fix;
everything below is mitigation.

**Plugin-side (this repo)**

1. **Extend the availability-aware pattern to cover unusable rejections.** Add a third failure mode
   alongside "script unavailable": *the validator rejected the payload and the reason is not
   actionable* (truncated, empty, or naming no field). Define it observably — the rejection text
   contains no field name and no line/pointer the payload can be corrected against — so the agent is
   not left judging "unhelpful".

2. **Bound the retry.** After **two** rejections with no actionable reason for the same source, stop
   retrying. A third attempt is guesswork, and guessing at a mapping payload is worse than the
   documented alternative because it burns the bootcamper's time with no convergence signal.

3. **Pin the fallback question.** The bootcamper made this decision in-session with an ad hoc
   question; pin it verbatim (INV-056/INV-051, numbered, no "or" per INV-009) so the routing is
   consistent, e.g.:

   > 👉 **The mapping validator rejected this source twice without saying why. How would you like to proceed? Reply with a number:**
   >
   > 1. **Write the mapper against the Senzing Entity Specification** *(recommended)* — all three quality gates still run.
   > 2. **Try the mapping workflow once more** — it may succeed with a different payload.
   > 3. **Skip this source** — continue with the sources that mapped successfully.

4. **Make the fallback path legitimate and bounded, not an exception.** When option 1 is taken, state
   plainly what is and is not preserved:
   - attribute names still come from the Senzing Entity Specification in `docs/reference/`
     (`phase2-data-mapping.md:391`) — **never** from training data, so the MCP-first invariant
     (INV-080) and the "never guess attribute names" rule hold;
   - **all three quality gates still run** (analyzer, verbatim check, routing report) with the same
     availability-aware handling;
   - the shared-feature collision check (`:184-197`) still runs — it is cross-source and the
     validator never performed it anyway;
   - the mapping is still only **structurally** validated, so Data processing's match-key audit
     remains the semantic check (INV-117).

   Record the fallback and its reason in the source's `config/mapping_state_[datasource].json`
   checkpoint and in `docs/mapping/` so the deliverable says how each mapper was produced. A reader
   of the recap should be able to tell which sources went through `mapping_workflow` and which did
   not.

5. **Capture the rejection for the maintainer.** When a rejection is unactionable, write the raw
   returned text verbatim to the source's mapping-state checkpoint before falling back. That is the
   evidence the upstream fix needs, and it is lost today.

## Acceptance criteria

- [ ] `phase2-data-mapping.md` documents the unactionable-rejection failure mode alongside the
      existing unavailable-script mode, with an observable definition of "unactionable".
- [ ] After two unactionable rejections for one source, the flow stops retrying and presents the
      pinned fallback question verbatim (INV-005/INV-051/INV-056), with numbered options and no "or"
      (INV-009).
- [ ] Choosing the Entity Specification path still runs the analyzer, verbatim check, and routing
      report with unchanged availability-aware handling, and still runs the cross-source
      shared-feature collision check.
- [ ] No attribute name in the fallback path comes from training data — all are read from the Entity
      Specification reference in `docs/reference/` (INV-080).
- [ ] The raw rejection text is recorded verbatim in `config/mapping_state_[datasource].json` before
      falling back.
- [ ] `docs/mapping/` and the recap record, per source, whether the mapper came from
      `mapping_workflow` or the Entity Specification fallback, and why.
- [ ] A source whose validation succeeds is unaffected — `mapping_workflow` remains the default and
      documented path, and the fallback is never offered pre-emptively.
- [ ] Reporting a passing fallback mapping still states it is structurally, not semantically,
      validated (INV-117).
- [ ] An upstream request is filed via `submit_feedback` for full or structured step-3 validation
      errors.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — add the
  unactionable-rejection mode to the availability-aware validation block (`:207-222`); bound the
  retry; pin the fallback question; define what the fallback preserves; require capturing the raw
  rejection to the checkpoint (`:56-65`).
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/SKILL.md` — reference the new
  failure mode from the error-handling section.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "`mapping_workflow` step-3 validation errors are
  truncated, making the rejection unfixable" (2026-07-26, Module Data Quality, Mapping, and
  Transformation; `Source: self-observed (assistant retrospective)`)
- Priority: High
- Related specs: `specs/mcp-grounding-in-every-skill.md` (INV-080 — the invariant the fallback must
  not break), `specs/post-load-match-key-semantic-audit.md` (INV-117 — the semantic check that still
  applies), `specs/verify-sdk-parameter-shapes-and-flag-families.md` and
  `specs/java-scaffold-json-dependency-gap.md` (other upstream MCP-server findings),
  `specs/quality-scoring-presence-test.md` (the other Module 5 finding from this session).

## Invariants introduced

- `INV-125` — When a documented MCP-first path fails unrecoverably, the sanctioned fallback MUST
  preserve every quality gate the primary path would have run, record the raw failure verbatim,
  and record which path produced each artifact (recorded in `specs/INVARIANTS.md`).
