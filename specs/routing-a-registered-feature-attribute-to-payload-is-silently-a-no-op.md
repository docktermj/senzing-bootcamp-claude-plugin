# Routing a registered feature attribute to "payload" does nothing unless it is also renamed

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A Bootcamper was asked how to route a field and answered **payload**. The mapper honored the answer
in form only: the key was kept under its own name at the record root, where it is a *registered
feature attribute*, so Senzing extracted it as a feature regardless of the routing decision. The
Bootcamper's explicit answer was silently not honored.

The same field also passed through `payload_from_list`, which joins values, so **13,803 of 19,050
records** carried `"XXX; VGB; GBR"` as one literal value. Renaming the key cleared the analyzer's
SCHEMA warning.

⛔ **Every static gate passed.** The analyzer, the verbatim check and the routing report all
approved the mapping, because each checks *structure and faithfulness to the plan* — not whether the
plan achieved what the Bootcamper asked for. The defect surfaced only while writing the per-source
documentation, a step the module treats as a deliverable rather than a check.

A second, related mapping was reversed in the same run for a different reason: a rules file with no
`OTHER_ID` group correctly dropped 123 self-referential rows and silently dropped 6 `swiftBic` and
2 `imoNumber` values with them. The two designs are indistinguishable in output whenever the
excluded rows dominate — which is why all three gates passed there too.

## Root cause

**Nothing in the mapping module checks a routing decision against what the routing will actually
do.** Searched `module-05-data-quality-mapping/`: no shipped text mentions `payload_from_list`, a
root-level payload key colliding with a registered feature attribute, or the rule that a registered
attribute name at the record root is extracted whatever the mapper intended. The Bootcamper's answer
is recorded and carried into the plan; nothing re-reads it against the attribute catalog.

**The analyzer already knew.** Its SCHEMA warning fired and cleared on the rename — so the signal
existed and arrived in the *output analysis*, after the mapping gate had already passed. The check
is in the wrong place in the flow, not missing.

⚠️ **The mechanism is observation-only and must be marked as such.** One run, one SDK build, the
analyzer's own warning as the corroborating instrument. `search_docs(query='payload attribute versus
registered feature attribute record root extracted as feature', category='data_mapping')` on
**server 1.32.9, 2026-08-17** returns the Entity Specification's *Payload attributes (optional)*
section (payload attributes "are not used in matching") and its *Mapping identifiers* section
(*"Route to a registered feature when appropriate; otherwise use payload attributes or omit"*).
Those establish that payload and registered features are **distinct categories** and that the
choice between them is a mapping decision — they do **not** state the precedence rule when a
registered attribute name appears at the record root under a payload intent. That specific rule is
this run's observation and is written as one (INV-080/INV-149).

## Proposed change

1. **Add a mapping-time check: a root-level payload key MUST NOT be a registered feature
   attribute.** Run it where the routing decision is made, against the attribute catalog the module
   already consults — before the plan is accepted, not after the output is analyzed.
2. **On a collision, say what will actually happen and offer the rename**, rather than rejecting the
   Bootcamper's answer. Their intent (do not match on this) is achievable; only the key name is
   wrong. The remedy that worked here was renaming to a non-registered name.
3. **Surface the analyzer's SCHEMA warning at the mapping gate**, not only in the output analysis.
   It is the instrument that already detects this, one step too late to prevent it.
4. **Warn that a list-valued payload route joins its values** into a single literal, so a
   multi-valued field becomes one meaningless string. `"XXX; VGB; GBR"` in 72% of records is the
   observable signature.
5. ⚠️ **Name the general shape at the gate, since it is what the gates structurally cannot see:**
   static checks confirm the output matches the plan and the plan is faithful to the source. They do
   not confirm the plan does what the Bootcamper asked. Where an answer selects a *behavior* rather
   than a *value*, something must verify the behavior was obtained.

## Acceptance criteria

- [ ] A root-level payload key that is a registered feature attribute is detected at the mapping
      gate, before the plan is accepted.
- [ ] The collision message states what Senzing will do with the key and offers the rename; it does
      not silently override the Bootcamper's routing answer (INV-006).
- [ ] A list-valued payload route warns that values are joined into one literal.
- [ ] The analyzer's SCHEMA warning is visible at the mapping gate.
- [ ] Negative control: a payload key that is **not** a registered attribute passes unchanged, so
      the check does not become a blanket objection to payload routing.
- [ ] The precedence mechanism is marked **observation-only** wherever it is stated, with its date
      and the instrument that showed it — never presented as MCP-sourced (INV-080/INV-149).
- [ ] Stated as behavior so any implementation language satisfies it (INV-002); the attribute
      catalog lookup is a data question, not a Python one.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — the
  routing decision and the mapping gate.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md` — where the
  analyzer's output is read, to move the SCHEMA warning forward.
- `tests/` — the collision check and its negative control.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "two mappings were reversed after loading, and neither was filed when it happened" (2026-08-17, Module Data Quality, Mapping, and Transformation, phase 2; `Source: self-observed (assistant retrospective)`)
- Priority: **Medium.** It silently discards a Bootcamper's explicit answer and writes a degenerate joined value into most records of a source, and every existing gate approves it. Rated below High only because the resolution impact is bounded — an extra feature and a junk payload value, not lost identifiers.
- MCP re-check: **n/a for the plugin defect; observation-only for the mechanism.** No Senzing fact is *asserted* by the proposed change — the check is a lookup against the attribute catalog the module already uses. The precedence behavior described in `## Root cause` is marked observation-only above, with the route that was asked and what it returned. owner-checked: `search_docs(category='data_mapping')` over the Entity Specification is the route that would carry a payload-versus-registered-attribute precedence rule; it returned the *Payload attributes* and *Mapping identifiers* sections, which distinguish the categories but state no precedence for a colliding root-level key. Server **1.32.9**, docs index 2026-08-11 20:52 UTC, checked 2026-08-17.
- Upstream: **not applicable as filed, but there is a candidate here.** If the precedence rule is real and undocumented, "the Entity Specification does not say what happens when a payload-intended key at the record root is a registered feature attribute" is an actionable documentation gap. ⚠️ It needs a second confirmation first — one run is not enough to file a behavior claim upstream, and the entry does not route this upstream at all.
- Related specs: `specs/capture-reversed-decisions-during-the-run.md` (**implemented** — it covers the entry's first half, the requirement to file a reversal when it happens; this run reports that mechanism not firing, which is a separate concern from its absence), `specs/verbatim-check-rejects-extract-and-relationship-scaffolding.md` and `specs/verbatim-check-numeric-source-values.md` (the gate whose faithfulness checks pass here), `specs/module5-quality-gate-demands-a-question-its-best-branch-lacks.md`, and INV-006, INV-080, INV-149, INV-002.

## One split of the feedback entry

This entry reports **two** findings under one title. The first — that both reversals went unfiled
until the retrospective — is **already tracked**: `specs/capture-reversed-decisions-during-the-run.md`
is implemented and requires filing a reversal when it happens. What this run adds there is evidence
that the shipped mechanism **did not fire twice in one session**, which is a follow-up on that spec
rather than a new one, and is recorded in the triage report instead of duplicated here.

This spec covers only the second finding — the non-honored payload routing — because it is a defect
no existing spec addresses and it has a concrete, testable remedy. The `OTHER_ID` case is included
in `## Problem` as corroboration of the same "all gates passed" shape, not as a separate proposal:
its remedy (`exclude_when`) was a mapping fix, not a plugin change.
