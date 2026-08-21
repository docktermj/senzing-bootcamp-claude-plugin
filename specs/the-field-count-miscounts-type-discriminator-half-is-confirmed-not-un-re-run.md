# The field-count miscount's `type_discriminator` half is confirmed on server 1.33.0 — the note's "only re-run half" caveat can be retired, and the counter's own arithmetic now names the uncounted field

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`phase2-data-mapping.md` records the step-3 field-count miscount as **half-settled**: the `derived`
half appears fixed upstream, and the `type_discriminator` half is *"the only one still NOT re-run"*.
The note names precisely the experiment that would settle it —

> a source with a per-record entity-type field, mapped with a `type_discriminator` whose
> `field_overrides` declare at least one source field.

A 2026-08-18 run had exactly that source (WATCHLIST_PEP) and the warning fired:

```text
Schema 'watchlist_pep': mapping covers 7 of the 8 profiled source fields
```

`entity_name` was declared only inside `type_discriminator.types.*.field_overrides` and was excluded
from the count. **Every source field was dispositioned.** A later source with no discriminator
(DEVICE_REGISTRY, 8 fields) produced no warning, isolating the cause.

**It is a benign warning and it is not a harmless one.** An unexplained "covers 7 of 8" on a
complete mapping invites the mapper to hunt for a missing field that is correctly mapped — at the
gate whose job is to catch genuinely undispositioned fields. The plugin's own instruction not to
start ignoring this step's warnings generally is right, and it is exactly why this one needs to be
explained rather than tolerated.

## Root cause

**Confirmed live on server 1.33.0, 2026-08-21, by running the experiment the note specifies.** An
8-field mixed-type source, mapped with a `type_discriminator` on `kind` whose `field_overrides`
declare `entity_name`, advanced from step 3 and returned:

```text
Schema 'watchlist_pep': mapping covers 7 of the 8 profiled source fields
(dispositions: feature=2, payload=3, ignore=1, extract=0, code_mapping=0,
 discriminator=1; derived=2 are synthesized and not source fields)
```

The response's own arithmetic settles both halves at once:

- `2 + 3 + 1 + 0 + 0 + 1 = 7` against a `field_count` of 8. The missing field is `entity_name`.
- `discriminator=1` counts the discriminator field (`kind`) **only**. A field declared solely in
  `type_discriminator.types.*.field_overrides` is counted by nothing.
- `derived=2 are synthesized and not source fields` — the counter now says so explicitly, which
  **confirms the `derived` half is genuinely fixed** rather than merely quiet. The plugin's caution
  that "an absent warning today is not proof it never fires" was the right call to make at the time;
  the current response resolves it in the plugin's favor.

So the diagnosis the plugin recorded on 2026-07-31 was correct in both directions, one direction has
been fixed upstream, and the other reproduces today with the server printing the evidence.

**The plugin's affected text:**
`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md:672-677`:

> ⚠️ **Only the `derived` half was re-run.** The 2026-08-14 walk used a single-type source, so it
> carried no `type_discriminator` and settles nothing about that half of the original claim. What
> would confirm or retire it: a source with a per-record entity-type field, mapped with a
> `type_discriminator` whose `field_overrides` declare at least one source field.

That paragraph has done its job and is now stale. The surrounding block (`:645-682`) is written as a
conditional — *"Read the rest of this block as a conditional: it tells you what the warning meant, if
you ever see it"* — which is no longer the right framing for the half that fires.

⚠️ **One thing did improve and should be captured.** On 1.32.9 the warning was a bare count. On
1.33.0 it carries the full disposition breakdown, which makes the cause **diagnosable from the
warning text itself** — a mapper can see `discriminator=1` against their two discriminator-declared
fields and know immediately what is uncounted. That is worth relaying, because it converts the
plugin's explanation from *take our word for it* into *read the parenthetical*.

## Proposed change

1. **Retire the "only the `derived` half was re-run" paragraph** (`:672-677`) and replace it with the
   confirmation: the `type_discriminator` half fires on server 1.33.0 (2026-08-21), reproduced with
   the experiment that paragraph asked for.

2. **Re-frame the block from conditional to split.** The `derived` half is fixed — the counter now
   states that derived entries are synthesized and excluded. The `field_overrides` half is current.
   Say which is which, so a reader meeting the warning knows it is the known-bad counter and not a
   regression of the fixed half.

3. **Quote the 1.33.0 breakdown and show the arithmetic.** Give the reader `feature + payload +
   ignore + extract + code_mapping + discriminator` summing short by the number of
   `field_overrides`-only fields, and tell them to check that sum against their own mapping. That is
   a one-line confirmation the mapper can run themselves, and it replaces an explanation they have to
   trust.

4. **Keep the operative instruction unchanged.** `:679-682` — confirm every source field carries a
   disposition, record the mismatch as expected, proceed, and do **not** generalize to this step's
   other warnings — is correct and is the whole point. Only its supporting freshness prose changes.

5. **Retire the `MCP-NEGATIVE` marker at `:656` or re-scope it.** It records that a three-derived-entry
   mapping produced no warning on 1.32.9. That remains true and is now better stated as a positive:
   the counter explicitly excludes derived entries. Do not leave a dated negative standing where the
   server now gives an affirmative answer (the class `guards-pinning-a-dated-negative-outlive-it`
   covers).

## Acceptance criteria

- [ ] `phase2-data-mapping.md` no longer describes the `type_discriminator` half as un-re-run, and
      records its confirmation with the server version and date.
- [ ] The block distinguishes the fixed `derived` half from the current `field_overrides` half.
- [ ] The 1.33.0 disposition breakdown is quoted, with the arithmetic a mapper can check against
      their own mapping.
- [ ] The operative instruction (confirm dispositions, record, proceed, do not generalize) is
      unchanged.
- [ ] The `:656` `MCP-NEGATIVE` marker is retired or re-scoped to the affirmative the server now
      gives.
- [ ] A guard asserts no shipped file calls the `type_discriminator` field-count half unverified.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — the
  field-count block (`:645-682`): the conditional framing, the `:656` marker, and the `:672-677`
  un-re-run paragraph
- `tests/` — guard against the un-re-run claim persisting

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Matthew.md` → "Improvement: step-3 field-count warning
  still miscounts type_discriminator.field_overrides" (2026-08-18, Module Data Quality, Mapping, and
  Transformation; `Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: server 1.33.0, 2026-08-21 — **still reproduces**, independently reproduced during
  triage rather than taken from the entry. A live `mapping_workflow` run (start → step 1 → step 2 →
  step 3) on an 8-field mixed-type source with `type_discriminator.field_overrides` declaring
  `entity_name` returned `"Schema 'watchlist_pep': mapping covers 7 of the 8 profiled source fields
  (dispositions: feature=2, payload=3, ignore=1, extract=0, code_mapping=0, discriminator=1;
  derived=2 are synthesized and not source fields)"`. The same response confirms the `derived` half
  is fixed. No absence is asserted against the server.
- Upstream: already offered and **declined by the maintainer** (per the entry's `Upstream:` field).
- Related specs: `specs/step3-field-count-warning-no-longer-fires.md`,
  `specs/guards-pinning-a-dated-negative-outlive-it.md`,
  `specs/step-2-prose-prescribes-a-record-type-its-own-schema-rejects.md`
