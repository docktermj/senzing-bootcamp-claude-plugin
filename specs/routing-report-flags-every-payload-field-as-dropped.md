# `sz_routing_report.py` flags every correctly-dispositioned payload field as "dropped"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

⚠️ **This is an `mcp-server` finding, not a plugin one.** `sz_routing_report.py` is served from
`mcp.senzing.com/resources/` and delivered by `mapping_workflow` at step 1. The plugin's job here is
to relay the defect so a Bootcamper is not misled by it; the fix belongs upstream. A drafted upstream
message is at the end of this spec.

## Problem

`mapping_workflow` step 4, Phase C, instructs:

> 4. ROUTING REPORT (measurement, then self-critique ONCE):
>    `python3 data/mapping/sz_routing_report.py <input_file> data/mapping/<name>_output.jsonl`
>    … Lists … DROPPED source value-entries (present in the source, absent from the output).
>    Read it ONCE: for each dropped entry, either map it to its most specific Senzing feature or
>    state why it is NOT a feature… **Do NOT dump dropped values into OTHER_ID/payload just to
>    silence the report.**

Run exactly as instructed, the report lists **every payload field as dropped** — including fields
that are present in the output, at the root, exactly where a payload disposition puts them. The same
report prints those fields under **"Payload root keys"** three lines earlier, so it contradicts
itself within one page of output.

Measured live on 2026-08-31, MCP server **1.35.1**, mapping the 1,554-record
`las-vegas / US-LABOR-VIOLATIONS` CORD source (61 fields; 6 feature, 6 payload, 49 ignore):

| Invocation | DROPPED entries reported |
|---|---|
| As the workflow instructs (no `--payload-fields`, no manifest) | **14,480** |
| With `--payload-fields` naming the six payload fields | **5,620** |

**8,860 spurious entries — 61% of the report** — are the six correctly-dispositioned payload fields
(`case_id` 1554, `naic_cd` 1554, `findings_start_date` 1554, `findings_end_date` 1554, `ld_dt` 1553,
`naics_code_description` 1091). Verified independently that all six are present in all 1,554 output
records at the root.

**The instruction and the report combine into a contradiction the guide cannot satisfy.** It is told
to reconsider six fields it correctly routed to payload, and in the same breath told not to route
dropped values to payload. The two compliant readings are (a) recognize the tool is wrong, or (b)
start promoting payload into features to quiet the report — which is precisely the "dumping-ground"
anti-pattern the workflow's own mapping reference warns against.

## Root cause

`sz_routing_report.py` (server-served, hash `172b85ee4fbcdfb9` on 2026-08-31), lines 70–110:

```python
def routing_report(source_records, output_records, payload_fields=()):
    exempt_fields = NEVER_FROM_SOURCE | set(payload_fields)
```

The exemption is real and correct — payload fields are meant to be exempt. But `payload_fields`
is supplied by:

```python
def discover_payload_fields(output_path, override):
    if override:                      # --payload-fields
        return [...]
    manifest = Path(output_path).parent / "phase1_manifest.json"
    if manifest.exists():             # never exists
        ...
    return []                         # <- what actually happens
```

Neither source is ever populated in this workflow:

- The step-4 command the workflow prints does **not** pass `--payload-fields`.
- **No `phase1_manifest.json` is ever produced.** It is not among step 1's seven downloaded
  resources, and nothing in steps 1–4 writes one. Confirmed absent from the workspace after a
  complete steps 1–4 run.

So `payload_fields` is always `[]` and the exemption never engages.

The fix is available inside the same function: `routing_report()` **already computes** the output's
payload root keys into `payload_keys` (that is what it prints), from exactly the records it is
comparing. It simply is not used for the exemption.

## Proposed change

**Upstream (the real fix):** have `routing_report()` derive the exemption from the payload root keys
it already computes from the output, instead of relying on an argument nothing supplies. Keep
`--payload-fields` as an override. That makes the report correct with no change to how the workflow
invokes it.

**In the plugin (the relay, which is what this repo can actually ship):** add a short note to
`module-05-data-quality-mapping/phase2-data-mapping.md` at the step-4 routing-report instruction:

> ⚠️ **The routing report counts every payload field as "dropped"** — its exemption list is fed by a
> `--payload-fields` argument the workflow does not pass and a `phase1_manifest.json` the workflow
> never writes, so it is always empty (measured on server 1.35.1, 2026-08-31: 14,480 reported
> against 5,620 real, on a six-payload-field source). **Read the dropped list with the payload
> fields mentally struck out**, or re-run with
> `--payload-fields "<your payload fields, comma-separated>"` to get the real list. ⛔ Do **not**
> promote payload fields into features to quiet it — that is the dumping-ground anti-pattern the
> same step forbids, reached by believing a broken measurement.

## Acceptance criteria

- [ ] The plugin's step-4 routing-report instruction warns that payload fields are miscounted as
      dropped, names the `--payload-fields` re-run as the way to get a true list, and forbids
      promoting payload into features to silence it.
- [ ] The note carries the measured figures with the server version and date.
- [ ] The note is framed as an upstream defect being relayed, not as plugin behavior.
- [ ] No change is made to the mapping dispositions the workflow validates — this is a reporting
      defect, not a mapping one.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — step 4,
  Phase C, the routing-report instruction.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, Data Quality/Mapping step 4
  (`Source: self-observed (assistant retrospective)`) — found by running the workflow's own step-4
  command on a real CORD source and reading the report against the output.
- Priority: Medium
- MCP re-check: server **1.35.1**, 2026-08-31 — reproduced end to end. `mapping_workflow` steps 1–4
  run to completion on `data/raw/US-LABOR-VIOLATIONS.jsonl`; the analyzer and the verbatim check
  both pass (exit 0); the routing report reports 14,480 dropped, against 5,620 with the payload
  exemption supplied by hand.
  owner-checked: `mapping_workflow(action='start')`'s own `resources[]` array — the seven resources
  it delivers are `sz_schema_generator.py`, `sz_json_analyzer.py`, `sz_verbatim_check.py`,
  `sz_routing_report.py`, `senzing_entity_specification.md`, `senzing_mapping_examples.md` and
  `identifier_crosswalk.json`. **No `phase1_manifest.json`**, so the script's second exemption route
  cannot be satisfied by anything the workflow itself provides (absence negative).
- Upstream: **submitted 2026-08-31** via `submit_feedback` (`category='bug'`, anonymous), with the
  maintainer's explicit approval of the text after the dry run closed. The message below is what was sent (reproduced
  in this repository's US-English house style, per INV-253), batched with the walk's other upstream findings into one report. Submissions are
  anonymous, so there is no follow-up channel; `support@senzing.com` is the route with a return path.
- Related specs: none

## Drafted upstream message (`category='bug'`, identifying details stripped — INV-065)

> `sz_routing_report.py` (served from /resources/, delivered by mapping_workflow step 1) reports
> every payload-dispositioned source field as a DROPPED source value-entry.
>
> Observed: mapping a 1,554-record JSONL source with 61 fields (6 feature, 6 payload, 49 ignore)
> through mapping_workflow steps 1-4. Run exactly as step 4 Phase C instructs —
> `python3 sz_routing_report.py <input> <output>` — the report lists 14,480 dropped entries. Passing
> `--payload-fields` with the six payload field names by hand gives 5,620. The 8,860 difference is
> the six payload fields, all of which are present at the root of all 1,554 output records. The same
> report prints those fields under "Payload root keys" a few lines above the dropped list.
>
> Expected: payload-dispositioned fields are exempt from the dropped list. The code intends this —
> `routing_report()` computes `exempt_fields = NEVER_FROM_SOURCE | set(payload_fields)` — but
> `discover_payload_fields()` only populates `payload_fields` from a `--payload-fields` override or
> from a `phase1_manifest.json` beside the output. The step-4 command does not pass the override, and
> no `phase1_manifest.json` is among the resources mapping_workflow delivers or writes, so the list
> is always empty and the exemption never engages.
>
> Suggested fix: derive the exemption from the payload root keys `routing_report()` already computes
> from the output records it is comparing, keeping `--payload-fields` as an override.
>
> Why it matters: step 4 tells the caller to reconsider every dropped entry AND not to route dropped
> values into payload. With payload fields listed as dropped, those two instructions conflict, and the
> path of least resistance is to promote payload into features — the dumping-ground anti-pattern the
> workflow's own mapping reference warns against.
>
> Senzing SDK 4.4.0; MCP server 1.35.1; sz_routing_report.py hash 172b85ee4fbcdfb9.

## Deviations from this spec, and why (2026-09-01)

**Re-verified against server 1.35.3 — the defect is unchanged, so the relay ships.** Re-read the
delivered `sz_routing_report.py` (6,855 bytes): `discover_payload_fields()` still ends in
`return []`, still populated only from `--payload-fields` or a `phase1_manifest.json`, and
`routing_report()` still computes `payload_keys` from the output, prints it, and does not use it for
`exempt_fields`. `download_resource`'s own tool description lists the seven resources it serves, and
**`phase1_manifest.json` is still not among them** — the second exemption route remains unsatisfiable
by anything the workflow provides. Had this been fixed upstream, the relay would have been dropped
rather than shipped.

⚠️ **The spec's script hash could not be compared and was not re-stated.** It records
`172b85ee4fbcdfb9` without naming the algorithm; the delivered file's BLAKE2b-64 is
`3d975e1939acd89d` and its SHA-256 begins `328572230e6f5e25`, so the two are not comparable and a
"hash changed" claim would be unfounded. The shipped note cites the **byte size and the code** —
which are checkable — rather than a hash whose provenance is unclear. A hash without its algorithm
is the same defect class as a census without its date.

**The note went into the existing "further limitations" list rather than beside the step-4 command.**
The spec proposed a standalone note at the routing-report instruction. That file already carries a
numbered list of MCP-delivered-tool limitations sharing one handling procedure and one freshness
convention — and limitation 3 is *already* about `sz_routing_report.py`. Filing this as limitation 4
puts it where a reader meets the others, inherits the shared handling, and avoids a second parallel
convention for the same class of defect. It cites **INV-173**, which governs it exactly: a gate that
cannot represent a legitimate input MUST NOT have its finding treated as evidence about the data or
resolved by altering the data.

⛔ **This broke three existing guards, and both halves of that were real.**

1. **A genuine defect I introduced:** the block's heading is used as a **cross-reference anchor**
   three times elsewhere in the same file (*"see 'Three further limitations' below"*). Renaming it to
   "Four" broke all three pointers. Fixed by updating the references; the guards caught it, which is
   what they are for.
2. **A premise the guards had pinned:** `test_verbatim_check_limitation.py` and
   `test_verbatim_check_limitations_freshness.py` located the block with the literal strings
   `"Three further limitations"` and `"Handling is the same for all three"`, so a fourth entry took
   **19 tests down as ERRORS** rather than failures. The count is *data*; the block and its shared
   handling procedure are the *claim*. The locators now match any count (`\w+ further limitations`)
   and every substantive assertion is unchanged — nothing was relaxed. ⚠️ **A self-counting heading
   used as an anchor is a trap that will recur** the next time a limitation is added; it is left as
   it is because renaming the anchor is a wider change than this spec, and the count is now asserted
   consistent across all four of its appearances by
   `tests/test_routing_report_payload_limitation_is_relayed.py`.

**One guard was right and I was wrong:** `test_all_three_are_dated_...` pins *"First observed
2026-07-27"*, and my rewritten intro had dropped that phrasing. The date is a real claim about the
original observation, so the prose was restored to carry it rather than the assertion changed.

**The upstream half was already sent** (2026-08-31, `category='bug'`, maintainer-approved). Nothing
was re-sent.
