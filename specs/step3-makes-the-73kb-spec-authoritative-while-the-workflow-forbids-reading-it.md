# Step 3 makes the 73 KB specification authoritative while the workflow forbids reading it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 5 Phase 1 Step 3 retrieves the Senzing Generic Entity Specification and makes it the working
reference for the rest of the module:

> Call `download_resource(filename="senzing_entity_specification.md")` … **Use this as the
> authoritative reference for all attribute names, types, and structures in this step and every
> subsequent step.**

Step 4 then instructs the comparison that consumes it — *"Using the Entity Specification retrieved in
Step 3 as the reference, compare each data source's fields against the specification's attribute
names"* — and Step 5a reuses the same copy, with *"do not download it again"*.

**The file is 73,051 bytes**, and `mapping_workflow` — which owns the mapping phase this module hands
off to — says the opposite, twice, in its own step-2 and step-3 responses (verbatim, server 1.32.9,
2026-08-14):

> You do **NOT** need to open the full 73KB entity specification to plan or map; it is available only
> as an optional deep-dive…

> **OPTIONAL DEEP-DIVE (do NOT read in full** — reference specific sections only if needed): …
> The inline reference above is distilled from it and is sufficient for almost all mappings. Open
> this file only to resolve a specific edge case the inline reference does not cover. **Do NOT
> attempt to read it end-to-end — that is unnecessary and will overflow limited context windows.**

Both instructions can be obeyed at once — by consulting the specification *selectively* (grep, or
section lookup) rather than reading it end to end. **That is what the walk did**, and it worked well:
targeted lookups produced exactly the two rules this dataset turned on (`NAME_FULL` for a
single-field name, `ADDR_FULL` for a single-string address). But the plugin never says to do it that
way. Read literally, "use this as the authoritative reference … in this step and every subsequent
step" invites the end-to-end read the workflow explicitly warns will overflow the context window.

### Why this is worth fixing rather than filing as a nitpick

**Context exhaustion is the documented reason no phase-3 dry run has ever reached the later
modules.** `.claude/skills/dry-run/phase3-conversational.md` says so as the rationale for its entire
start-at-a-chosen-module design:

> A run that analyses from the onboarding preface exhausts its context somewhere around Discover the
> Business Problem and stops there. That is why every walk to date has re-covered the same opening
> stretch, and why Data processing, Query/Visualize/Discover and graduation have never been walked at
> all.

A module that instructs an end-to-end read of a 73 KB reference is a direct contributor to the
failure the maintainer tooling is built around. It is also a hazard for the **bootcamper's** session,
not only a dry run's: they are in one long conversation too, and a context overflow mid-module costs
them the run.

⚠️ **Confidence note, stated deliberately.** This is a *lower-confidence* finding than the others
from the same walk. The instruction is ambiguous rather than wrong — a competent guide reads
selectively, as this walk did, and nothing observably broke. It is filed because the ambiguity has a
known, expensive failure mode and a one-paragraph fix, not because a failure was reproduced. If a
reviewer concludes the literal reading is uncharitable, the right outcome is to close this rather
than implement it — and to say so, so the question is settled rather than re-asked next run.

## Root cause

`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`,
Step 3 — it names the artifact and its authority but not the **access pattern**, and it was written
before `mapping_workflow` began shipping the distilled inline reference at step 2. The two are now
redundant for the mapping phase, and only Phase 1 still needs the file at all.

Contributing: nothing tells the reader that the workflow's inline reference exists and supersedes the
file from step 2 onward, so a guide holding both has no basis for preferring either.

## Proposed change

1. **State the access pattern at Step 3.** Keep the file as the authority for Phase 1's comparison,
   and say **how** to consult it: look up the specific feature or attribute in question (grep or
   section lookup), never read it end to end. Give the reason in one clause — it is 73 KB, and the
   tool that owns mapping states that an end-to-end read will overflow limited context windows.
2. **Name the handoff.** Add one sentence saying that from `mapping_workflow` step 2 onward the
   workflow delivers a **distilled inline mapping reference** (feature catalog,
   identifier-classification workflow, exact attribute keys) which is the working reference for
   mapping, and that the 73 KB file is the deep-dive for edge cases it does not cover. This is the
   workflow's own framing; relaying it keeps the two from competing.
3. **Scope Step 3's "every subsequent step" claim to Phase 1**, where the file genuinely is the
   reference (Steps 4, 5, 5a and 6 all compare against it). Phase 2's steps have the inline reference
   and cite it already.
4. **Keep the single-canonical-copy rule** (`docs/reference/senzing_entity_specification.md`, no
   duplicates) — unchanged, and now more clearly worth having, since selective lookup needs a stable
   local path. ⚠️ Note the interaction with
   `specs/download-resource-returns-a-url-not-the-specification.md`: the workflow's own step-1
   resource list writes the same file to `data/mapping/`, so a run legitimately ends up with two
   copies at different paths. Whichever spec lands second should reconcile that rather than leaving
   the no-duplicates rule reading as violated by the tool.

## Acceptance criteria

1. Step 3 states that the specification is consulted by targeted lookup, never read end to end, and
   gives the size and the reason.
2. Step 3 names the workflow's distilled inline reference as the working reference for the mapping
   phase, with the 73 KB file as the edge-case deep-dive.
3. Step 3's authority claim is scoped to Phase 1 rather than "every subsequent step"; Phase 2's
   existing citations of the inline reference are asserted unchanged.
4. The single-canonical-copy rule survives, and the two-path situation created by the workflow's own
   resource list is acknowledged.
5. A test asserts that no instruction in the module directs an end-to-end read of the specification —
   negative-controlled by restoring the current "every subsequent step" wording.
6. Cross-platform, language-agnostic; no Senzing fact changes.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`
- `tests/test_entity_specification_access_pattern.py` (new)
- `specs/IMPLEMENTED.md`

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-14, walking Module 5 Phase 1 Step 3 and
  then reading the contradicting instruction in `mapping_workflow`'s step-2 and step-3 responses
  (`Source: self-observed (assistant retrospective)`). The walk consulted the file selectively and
  reported the tension rather than reproducing an overflow.
- Priority: **Low-Medium.** Nothing breaks and the ambiguity is resolvable by a careful reader; what
  it costs is context, in the module where context is already the binding constraint on reaching the
  end of the bootcamp.
- MCP re-check: **confirmed, server 1.32.9, 2026-08-14.** `download_resource(filename=
  'senzing_entity_specification.md')` reports `size_bytes: 73051`; `mapping_workflow` step 2 and
  step 3 both carry the do-not-read-in-full instruction quoted above.
