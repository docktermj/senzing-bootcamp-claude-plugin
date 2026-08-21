# Module 1's threshold check says "the Senzing MCP server" where Module 2 names the exact route, and the guide filled the gap with the wrong license's capacity

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

At Discover the Business Problem, Step 5a (the record-count threshold check), the guide told the
Bootcamper their planned volume was

> "comfortably inside the built-in evaluation license's 250K-record capacity, so there's no license
> concern to flag"

and accordingly left `license_guidance_deferred` unset. The real built-in capacity is **500**
records. The figure was off by a factor of 500, and it was not invented: 250K is the capacity of
the *requestable* evaluation license, read earlier in the session from `submit_feedback`'s tool
description. Two different licenses, one number, attributed to the wrong one.

The error was caught two modules later at SDK setup Step 5, where the same fact is sourced
properly and returns the actual limit.

**The consequence is a suppressed gate, not just a wrong sentence.** The generated scenario plans
"a few hundred to low thousands of records" across four sources — above 500. `license_guidance_deferred`
is precisely the signal Module 4's volume-gated License Key gate reads
(`module-04-data-collection/SKILL.md:736-741`), so leaving it unset on a "no license concern"
assessment disables the one prompt that would have warned the Bootcamper before they met
`SENZ9000|LIMIT` mid-load.

## Root cause

**Step 5a names the server; it does not name the route.**
`plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:243-245`:

> **Absent/null:** compare the total against the built-in evaluation capacity, confirmed via the
> Senzing MCP server (never a hardcoded figure). If the total exceeds it, record
> `license_guidance_deferred: true`; otherwise leave it unset.

"Confirmed via the Senzing MCP server" is a rule with no operation attached. There are thirteen
tools; the capacity lives in exactly one place, and a guide that has already read a 250K figure
from a *different* tool's description in the same session has no prompt to go anywhere.

**Module 2 does it correctly, in the same repository, for the same fact.**
`module-02-sdk-setup/SKILL.md:942` names the call outright —

```text
sdk_guide(topic='load', language='<chosen_language>', platform='<user_platform>', record_count=1000)
```

— and `:945` carries the `MCP-NEGATIVE` marker recording that `search_docs` returns no figure and
that `sdk_guide(topic='load', record_count=<above the limit>)` is the owning route. Module 1 asks
for the same number with none of that. The asymmetry is the defect: two steps, one fact, one of
them runnable.

This is **INV-194's** shape applied to a positive claim. INV-194 governs concluding an absence
from the wrong route; here the guide concluded a *value* from the wrong route, and the step gave it
nothing better to do. INV-080 forbids the remembered figure and was violated — but a step that
says only "ask the server" makes that violation the path of least resistance rather than a lapse.

**Both figures re-confirmed on server 1.33.0, 2026-08-21, and they are genuinely two licenses:**

- `sdk_guide(topic='load', language='python', platform='linux_apt', record_count=1000)` —
  `engine_config_notes`: *"IMPORTANT: Without a license, Senzing is limited to 500 Distinct Source
  Records (DSRs). Loading record 501 fails with SENZ9000|LIMIT."* Its `compatibility_notes` add
  *"LICENSE REQUIRED: You have 1000 records, which exceeds the default Senzing license limit of
  500."*
- `submit_feedback`'s tool description, via `get_capabilities` — *"A 10-day, 250K-record eval
  license is generated and emailed with a download link"*, granted on
  `category='license_request'`.

So the 250K figure is real, current, and belongs to a license nobody has yet requested at Module 1.

⚠️ **Note for the implementer: Step 5a's `Absent/null` branch also brushes INV-244.** It reads an
absent `license_record_limit` and compares against the *built-in* capacity, which assumes no custom
license is installed — the inference INV-244 forbids. It is defensible here because Step 5a is
explicitly a pre-check that only sets a deferral flag for a later gate to resolve, and INV-093
forbids a license prompt at this point. Make that reasoning explicit in the text rather than
leaving the branch looking like the Module 6 branch INV-244 was written against.

## Proposed change

1. **Name the route in Step 5a, as Module 2 does.** Replace "confirmed via the Senzing MCP server
   (never a hardcoded figure)" with the call that carries the number —
   `sdk_guide(topic='load', language=<chosen>, platform=<detected>, record_count=<a value above the
   limit>)` — and say that the figure comes from its `compatibility_notes` /
   `engine_config_notes`. Re-verify the call at implementation time rather than copying it from
   here (INV-080).

2. **Name the confusable figure, so the conflation is closed rather than merely avoided.** One
   clause: the 250K/10-day figure describes the evaluation license a Bootcamper can *request* via
   `submit_feedback(category='license_request')`, not the built-in license active by default. This
   is the specific mistake that was made; a step that names only the right route still leaves the
   wrong number sitting in context from a tool description read minutes earlier.

3. **Generalize the lesson where it belongs.** Wherever a step instructs the guide to source a
   Senzing fact "from the MCP server", it must name the tool and parameters that own it. Register
   this as an invariant at implementation time if the sweep finds other instances — INV-080 says
   *do not state it from memory*, and INV-194 says *scope a negative to the route asked*; neither
   says *a positive instruction must name its route*, which is the gap this entry found.

4. **Make the deferral flag's stake visible at the point it is written.** Step 5a should state that
   leaving `license_guidance_deferred` unset suppresses Module 4's License Key gate, so the cost of
   getting the comparison wrong is legible where the comparison happens.

## Acceptance criteria

- [ ] `phase1-discovery.md` Step 5a names the tool and parameters that carry the built-in capacity,
      not "the Senzing MCP server".
- [ ] Step 5a distinguishes the built-in capacity from the requestable evaluation license's
      capacity, and names which tool carries each.
- [ ] Step 5a states that leaving `license_guidance_deferred` unset suppresses Module 4's Step 8a
      gate.
- [ ] Step 5a's `Absent/null` branch states why comparing against the built-in capacity is correct
      here and not the INV-244 inference.
- [ ] A guard asserts that no shipped step instructs the guide to confirm a Senzing figure "via the
      MCP server" without naming a tool.
- [ ] A sweep of every shipped "source this from MCP" instruction is recorded, with each instance
      either naming its route or listed with a reason it cannot.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — Step 5a
  (`:232-250`): name the route, name the confusable figure, state the gate consequence, justify the
  `Absent/null` branch
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — reference only; `:942` and `:945`
  are the pattern to copy
- `specs/INVARIANTS.md` — a new invariant if the sweep finds this is a class rather than one site
- `tests/` — new guard for route-less MCP sourcing instructions

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Joel.md` → "Improvement: Assistant asserted the wrong
  built-in evaluation license capacity" (2026-08-18, Module Discover the Business Problem;
  `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: server 1.33.0, 2026-08-21 — **still reproduces**. Both figures confirmed and
  confirmed distinct: `sdk_guide(topic='load', language='python', platform='linux_apt',
  record_count=1000)` gives the 500-DSR built-in limit and `SENZ9000|LIMIT`; `get_capabilities`'
  `submit_feedback` entry gives the 250K/10-day requestable license. No absence is asserted against
  the server.
- Upstream: not applicable — the plugin is the defect; the server answers correctly when asked the
  right route.
- Related specs: `specs/license-limit-assumed-when-it-could-be-measured.md`,
  `specs/generated-dataset-is-sized-before-anything-measures-the-license.md`,
  `specs/mcp-negative-markers-must-name-the-owning-route.md`,
  `specs/a-spec-asserting-server-absence-must-name-the-owning-route.md`,
  `specs/single-license-gate-at-data-processing.md`

## Deviations from this spec, and why (2026-08-21)

**Implemented PARTIALLY, by maintainer decision.** Changes 1, 2 and 4 shipped; change 3 — the
repo-wide sweep of every "source this from MCP" instruction, plus the possible new invariant for the
class — was held for review, on the grounds that the sweep could cascade into many edits and that an
invariant is permanent. The `specs/IMPLEMENTED.md` entry records which acceptance criteria are met
and which are not, and the guard's docstring states its own scope so it is not mistaken for
corpus-wide coverage.

**The unregistered rule is named rather than left implicit.** The class this spec identified —
INV-194's shape applied to a *positive* claim, where a **value** rather than an absence is concluded
from the wrong route — is not in `INVARIANTS.md`. INV-080 forbids stating a Senzing fact from memory
and INV-194 requires scoping a negative to the route asked; neither says *a positive instruction must
name its route*, which is precisely the gap the reported failure walked through.
