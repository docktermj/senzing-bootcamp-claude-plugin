# `mapping_workflow` step 2 tells you to set `record_type: "MIXED"` and the same response's schema forbids it — the plugin must pre-empt a warning the server hands to anyone who follows its instructions

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Following `mapping_workflow`'s step-2 instructions exactly produces a server warning saying you did
something non-standard. Observed twice in one run (WATCHLIST_PEP, and REMITTANCE's embedded
beneficiary), and **reproduced during this triage on server 1.33.0**.

The step-2 prose:

> record_type must be PERSON or ORGANIZATION. If a schema has mixed entity types discriminated by a
> field (e.g., type=person/company), **set record_type to "MIXED"** and note the discriminator field.
> Type discriminator = conditional logic, NOT separate masters. The type_discriminator details will
> be defined in Step 3 mapping.

The **same response's** `advance_schema`:

```json
"record_type": { "enum": ["PERSON", "ORGANIZATION", "VESSEL", "AIRCRAFT"] }
```

Send `MIXED` and it is accepted — `status: "ok"`, advanced to step 3 — with:

```text
warnings: ["schema_plan[0] (watchlist_pep): record_type 'MIXED' is non-standard —
           expected one of: PERSON, ORGANIZATION, VESSEL, AIRCRAFT"]
```

**A mapper cannot satisfy both.** Follow the prose and every discriminated source warns; follow the
schema and the "this source is mixed" signal is lost at the step whose purpose is to record it. And
the warning's wording — *non-standard* — reads as *you did something wrong*, addressed to someone who
did exactly what they were told two paragraphs earlier.

**Why the plugin has to act on a server contradiction it did not cause.** Module 5 routes every
Bootcamper through `mapping_workflow`, and a discriminated source is common in the bootcamp's own
data (watchlists, sanctions lists, company registries all mix persons and organizations). So this
warning reaches a Bootcamper on a normal path, in a step the plugin presents as authoritative, and
the plugin currently says nothing about it. INV-179's shape: a response that is *half* an
endorsement, where the missing half looks like the Bootcamper's fault.

## Root cause

**Three independent contradictions in one response, all confirmed on server 1.33.0, 2026-08-21**, by
running `mapping_workflow` start → step 1 → step 2 and reading the step-2 response against itself:

1. **Prose prescribes `MIXED`; the `advance_schema` enum excludes it.** Quoted above, same response.
2. **The typed `payload` branch for `for_step 2` carries the same enum**, so a client using
   constrained decoding *cannot emit* `MIXED` at all — the documented instruction is unreachable
   through the preferred channel.
3. **The prose also says "must be PERSON or ORGANIZATION" while the enum admits VESSEL and
   AIRCRAFT.** A second, opposite disagreement between the same two halves, in the same sentence
   that introduces the first.

And the server's own step-2 reference text, in that same response, describes VESSEL and AIRCRAFT as
real record types ("watchlists also VESSEL, AIRCRAFT"), so the prose's narrower claim is wrong on its
own terms.

**The plugin side: nothing mentions any of it.** `MIXED` has **zero** occurrences across
`plugins/senzing-bootcamp/skills/`. Module 5's step-10 guidance
(`module-05-data-quality-mapping/phase2-data-mapping.md`) walks the Bootcamper into step 2 and leaves
them to meet the contradiction unaided — unlike the mapping-workflow limitations the same file
documents at length (the verbatim-check entries, the field-count counter), which is the established
pattern for exactly this situation.

⚠️ **Both readings are defensible, which is why the plugin must choose one rather than describe the
conflict.** `MIXED` is accepted and preserves the signal at the cost of a warning; the majority type
plus a `type_discriminator` at step 3 is enum-clean and carries the same information one step later,
since step 3's `type_discriminator` is what actually determines `RECORD_TYPE` per record. Leaving the
guide to decide mid-mapping is how one source gets one treatment and the next gets the other.

## Proposed change

1. **Prescribe one value and say why.** Recommend sending an enum-valid `record_type` at step 2 —
   the majority or most representative type — and declaring the mixture through step 3's
   `type_discriminator`, which is the field the server actually reads to type each record. This
   avoids a warning on every discriminated source and loses nothing: the prose itself says "the
   type_discriminator details will be defined in Step 3 mapping".

2. **Say that the step-2 prose contradicts its own schema, and that the warning is not the
   Bootcamper's error.** Quote both halves and the warning text. A guide who has already sent `MIXED`
   — or who reads the prose and wonders why the plugin disagrees with it — needs to know this is a
   known server contradiction, so the warning is recorded as expected and the mapping proceeds
   (INV-048/INV-173: a tool limitation must not become an iterate-forever loop).

3. **Do not tell the guide to suppress or ignore step-2 warnings generally.** Same discipline the
   field-count block already applies: this is one known-bad interaction, not a noisy step. Name it
   specifically.

4. **Record the VESSEL/AIRCRAFT half too.** The prose's "must be PERSON or ORGANIZATION" is wrong
   against its own enum and its own reference text, and a watchlist source in this bootcamp can
   legitimately need VESSEL. A guide who reads the prose will not know those are available.

5. **Re-verify all three legs at implementation time (INV-080), and treat the fix as retirable.**
   If the prose and the enum have been reconciled by then, this guidance becomes stale in the way
   `the-eval-license-duration-tools-now-agree-so-retire-the-note-and-its-guard` describes — so write
   the note with its retirement condition stated: retire it once step 2's prose and its
   `advance_schema` agree.

## Acceptance criteria

- [ ] Module 5's step-10 guidance prescribes an enum-valid `record_type` at step 2 with the mixture
      declared via step 3's `type_discriminator`, and says why.
- [ ] The guidance quotes the step-2 prose, the `advance_schema` enum, and the warning text, and
      states that the warning does not indicate a Bootcamper error.
- [ ] The guidance names VESSEL and AIRCRAFT as enum-valid despite the prose.
- [ ] The note carries an explicit retirement condition (prose and schema agree) and its server
      version and date.
- [ ] The guidance does not license ignoring step-2 warnings generally.
- [ ] All three legs re-verified live at implementation time and recorded; if the contradiction is
      gone, the spec closes as not-applicable rather than shipping stale guidance.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — step-10
  guidance gains the `record_type` prescription and the contradiction note, alongside the existing
  mapping-workflow limitation blocks
- `tests/` — guard that the note carries its retirement condition, matching the pattern used for
  other dated server-contradiction notes

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Matthew.md` → "Improvement: step-2 prose prescribes
  record_type \"MIXED\", which the typed schema forbids and the server warns about" (2026-08-18,
  Module Data Quality, Mapping, and Transformation; `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: server 1.33.0, 2026-08-21 — **still reproduces**, independently reproduced during
  triage. A live `mapping_workflow` run returned step-2 prose reading *"set record_type to
  \"MIXED\""* alongside an `advance_schema` whose `record_type` enum is
  `["PERSON","ORGANIZATION","VESSEL","AIRCRAFT"]`; advancing with `MIXED` returned `status: "ok"`
  plus `"schema_plan[0] (watchlist_pep): record_type 'MIXED' is non-standard — expected one of:
  PERSON, ORGANIZATION, VESSEL, AIRCRAFT"`. The typed `payload` branch for `for_step 2` carries the
  same enum. No absence is asserted against the server.
- Upstream: already offered and **declined by the maintainer** (per the entry's `Upstream:` field).
  The plugin-side pre-emption is what this spec delivers.
- Related specs: `specs/mapping-workflow-step1-prose-contradicts-its-own-advance-schema.md`,
  `specs/the-field-count-miscounts-type-discriminator-half-is-confirmed-not-un-re-run.md`,
  `specs/mapping-workflow-tells-the-guide-not-to-ask-and-the-plugin-never-reconciles-it.md`,
  `specs/the-eval-license-duration-tools-now-agree-so-retire-the-note-and-its-guard.md`

## Deviations from this spec, and why (2026-08-21)

**Implemented as one commit with its two sibling Module 5 specs, not three.** All three edit
`phase2-data-mapping.md`, and their changes interleave inside one block — the freshness header, the
field-count block, limitation 2 and step 10. Splitting them into three commits would have produced
**red intermediate commits**: each prose change has a guard pinning the claim it replaces, so a
commit carrying the prose without its guard update (or the reverse) fails the suite. The repo's
one-commit-per-spec pattern assumes specs touch disjoint files; here it would trade a clean history
for commits that do not individually pass. The commit message names all three specs.

**Eight guard assertions were inverted rather than deleted.** Across
`tests/test_verbatim_check_limitation.py` and `tests/test_verbatim_check_limitations_freshness.py`,
assertions pinning "limitation 2 is un-re-run", "the field-count warning no longer fires" and the
retired `MCP-NEGATIVE` marker asserted claims these changes disprove. Each was rewritten to assert
the new claim with a docstring recording what changed and why keeping the old one would be worse
than no guard — the freshness guard had even written down its own trigger condition (*"needs a source
with disclosed relationships, which was not available"*), and that condition was met on 2026-08-18.
