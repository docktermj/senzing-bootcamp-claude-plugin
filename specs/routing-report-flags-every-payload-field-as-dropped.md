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
