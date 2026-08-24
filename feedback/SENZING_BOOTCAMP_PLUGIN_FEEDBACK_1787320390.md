# Senzing Bootcamp Plugin Feedback

Findings collected during this bootcamp run. Entries marked `self-observed` were noticed by the
assistant during the session rather than reported by the bootcamper.

## Improvement: REL_* attributes fail the verbatim gate — the un-re-run limitation, now confirmed and refined

**Date:** 2026-08-18
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — `sz_verbatim_check.py` is delivered by the MCP server; the harvester's value-only scope is the cause.
**Upstream:** offered, declined

### What happened

`phase2-data-mapping.md` records limitation 2 (REL_ANCHOR_DOMAIN / REL_POINTER_DOMAIN /
REL_POINTER_ROLE rejected by the verbatim check) as the one entry **not re-run**, needing "a source
with disclosed relationships". This run had one. It fires, exactly as described.

It also **refines** the entry. The existing note says `REL_ANCHOR_KEY` and `REL_POINTER_KEY` *pass*
"because those do carry source values". That holds only when `record_id_source` names a source
field. Here the embedded master used the `RECORD_HASH` sentinel, so the key is a derived hash that
appears nowhere in the source — and both KEY attributes fail too.

Measured: 83,338 offenders, reconciling exactly to 25,000 senders x 3 pointer attributes + 4,169
beneficiaries x 2 anchor attributes. Every offender was relationship scaffolding; no data value was
implicated.

### Why it matters

The plugin asked for this confirmation explicitly, and the refinement changes the guidance: a reader
following the current text would expect the KEY attributes to pass and might treat their failure as
a mapping defect rather than the same checker limitation.

### Suggested fix

Amend limitation 2 to state that KEY attributes pass only when `record_id_source` is a source field,
and fail alongside the DOMAIN/ROLE attributes whenever the sentinel `RECORD_HASH` is used — which is
the normal case for an `embedded_master`, the very disposition that produces REL_* scaffolding.

### Context when reported

- **Time:** 2026-08-18, during Phase 2 mapping of REMITTANCE
- **Plugin version:** 0.5.1
- **Workstation:** macOS 24.4.0 (Intel x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** data_quality_mapping / step 11-15 (REMITTANCE)
- **Recent questions:** How should the beneficiary side of each transfer be modelled?
- **Bootcamper responses:** Option 2 — one master plus an embedded master
- **Behind the scenes:** `mapping_workflow` step 4 verdict gate; INV-048/INV-173 exemption path
- **Observed problem:** verbatim check exit 1 with 83,338 offenders, all REL_*
- **Expected behavior:** per the existing note, DOMAIN/ROLE fail and KEY passes
- **Divergence:** KEY also failed, because the key was a RECORD_HASH-derived value

## Improvement: step-3 field-count warning still miscounts type_discriminator.field_overrides

**Date:** 2026-08-18
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the counter lives in `mapping_workflow`'s step-3 validator.
**Upstream:** offered, declined

### What happened

`phase2-data-mapping.md` states the `derived`-entry half of the field-count miscount appears fixed,
and that the `type_discriminator` half was "the only one still NOT re-run", needing a source with a
per-record entity-type field mapped via `field_overrides`. WATCHLIST_PEP is exactly that source.

The warning fired: *"Schema 'watchlist_pep': mapping covers 7 of the 8 profiled source fields"*.
`entity_name` was declared only inside `type_discriminator.types.*.field_overrides` and was excluded
from the count. Every source field was dispositioned. A later source with no discriminator
(DEVICE_REGISTRY, 8 fields) produced no warning, isolating the cause.

### Why it matters

The plugin explicitly requested this confirmation. It is a benign warning, but an unexplained
"covers 7 of 8" invites a mapper to hunt for a missing field that is correctly mapped.

### Suggested fix

Count fields declared in `type_discriminator.field_overrides` toward the covered total. Failing
that, update the plugin note from "un-re-run" to "confirmed on 2026-08-18".

### Context when reported

- **Time:** 2026-08-18, mapping WATCHLIST_PEP
- **Plugin version:** 0.5.1
- **Workstation:** macOS 24.4.0 (Intel x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** data_quality_mapping / step 11
- **Recent questions:** How should `country` be mapped?
- **Bootcamper responses:** Option 1 — split by entity type
- **Behind the scenes:** `mapping_workflow` step-3 advance validator
- **Observed problem:** "covers 7 of the 8 profiled source fields" on a fully-dispositioned mapping
- **Expected behavior:** all 8 counted
- **Divergence:** the counter excludes `field_overrides` fields

## Improvement: step-2 prose prescribes record_type "MIXED", which the typed schema forbids and the server warns about

**Date:** 2026-08-18
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the contradiction is between `mapping_workflow`'s own step-2 prose and its own advance schema.
**Upstream:** offered, declined

### What happened

`mapping_workflow` step-2 instructions say: *"If a schema has mixed entity types discriminated by a
field ... set record_type to 'MIXED' and note the discriminator field."* But the same response's
`advance_schema` declares `record_type` as an enum of PERSON / ORGANIZATION / VESSEL / AIRCRAFT.
Sending `MIXED` is accepted, and the server then returns
`record_type 'MIXED' is non-standard — expected one of: PERSON, ORGANIZATION, VESSEL, AIRCRAFT`.

So the documented instruction produces a warning on every discriminated source. Observed twice, on
WATCHLIST_PEP and on REMITTANCE's embedded beneficiary.

### Why it matters

Following the prose warns; following the schema loses the "this source is mixed" signal. A mapper
cannot satisfy both, and the warning suggests they did something wrong when they followed the
instructions exactly.

### Suggested fix

Either add `MIXED` to the enum and suppress the warning when a `type_discriminator` follows at step
3, or change the prose to prescribe the majority type plus the discriminator.

### Context when reported

- **Time:** 2026-08-18
- **Plugin version:** 0.5.1
- **Workstation:** macOS 24.4.0 (Intel x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** data_quality_mapping / step 10
- **Recent questions:** n/a — internal to the mapping workflow
- **Bootcamper responses:** n/a
- **Behind the scenes:** `mapping_workflow` action=advance from step 2
- **Observed problem:** documented value flagged non-standard by the same tool
- **Expected behavior:** prose and schema agree
- **Divergence:** they do not

## Improvement: ENTITY_NETWORK_LINKS uses MIN/MAX_ENTITY_ID, not START/END — a second, adjacent graph-parsing trap

**Date:** 2026-08-18
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — `phase2b-discover.md` documents the array-name trap thoroughly but not this field-name trap one level down.
**Upstream:** not applicable

### What happened

`phase2b-discover.md` warns at length that `find_path` returns `ENTITY_PATH_LINKS[]` while
`find_network` returns `ENTITY_NETWORK_LINKS[]`. That warning is accurate and it was heeded.

A second trap sits one level down and is not covered: within a `find_network` response,
`ENTITY_PATHS[]` entries carry `START_ENTITY_ID` / `END_ENTITY_ID`, while the **link** elements in
`ENTITY_NETWORK_LINKS[]` carry `MIN_ENTITY_ID` / `MAX_ENTITY_ID`. Both names are real, both are in
the same response, and reading START/END off a link yields `None` for every edge with no error —
printing 16 links as `None -> None`.

### Why it matters

It is the same failure class the existing warning exists to prevent (a plausible field name that
renders blank rather than raising), reached by a different route, and the presence of the correct-looking
names elsewhere in the same document makes it more convincing, not less.

### Suggested fix

Add one line to the existing warning: within a network response, paths use START/END and links use
MIN/MAX; do not carry either pair across.

### Context when reported

- **Time:** 2026-08-18
- **Plugin version:** 0.5.1
- **Workstation:** macOS 24.4.0 (Intel x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** query_visualize_discover / step 2
- **Recent questions:** Is there anything you'd like to adjust (query requirements)?
- **Bootcamper responses:** No
- **Behind the scenes:** building `src/query/network_discovery.py`
- **Observed problem:** every network link printed `None -> None`
- **Expected behavior:** link endpoints resolve
- **Divergence:** START/END belong to ENTITY_PATHS, not to links

## Improvement: the SDK container image ships no `ps` or `pkill`, so the visualization teardown silently fails

**Date:** 2026-08-18
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the bootcamp builds this container image and owns the teardown step that assumes standard process tools.
**Upstream:** not applicable

### What happened

At the visualization teardown gate, `docker exec senzing-bootcamp pkill -f senzing_viz_server.py`
failed with `exec: "pkill": executable file not found in $PATH`, and `ps` is absent too. Both
failures are reported by the Docker runtime rather than by the command, so a teardown that checks
only for a clean exit would record the server as stopped while it kept serving — which is what
happened here until port 8080 was probed and still answered 200.

Working alternative: scan `/proc/*/cmdline` from `python3` (which the image does have) and `os.kill`
the matches.

### Why it matters

The teardown gate is bootcamper-facing and its whole promise is that the server is stopped. Silently
leaving it running contradicts what the bootcamper was just told.

### Suggested fix

Either add `procps` to the image, or have the teardown step use the `/proc` scan and verify by
probing the port rather than by trusting the kill's exit status.

### Context when reported

- **Time:** 2026-08-18
- **Plugin version:** 0.5.1
- **Workstation:** macOS 24.4.0 (Intel x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** query_visualize_discover / step 3c teardown
- **Recent questions:** Ready for me to stop the visualization server?
- **Bootcamper responses:** yes stop the visualization server
- **Behind the scenes:** viz server + port_forward inside `senzing-bootcamp`
- **Observed problem:** pkill/ps missing; port still serving after "stop"
- **Expected behavior:** processes terminated and port free
- **Divergence:** the kill never ran, and its failure surfaced as a runtime exec error

## Improvement: WHY_KEY_DETAILS.CONFIRMATIONS came back empty on every why_records call

**Date:** 2026-08-18
**Module:** Query, Visualize and Discover
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the field is documented by `get_sdk_reference`; whether it should populate here is a server/engine question.
**Upstream:** offered, declined

### What happened

`phase1-query-visualize.md` directs the step-5 match-key breakdown at
`WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS.CONFIRMATIONS[]`, and `get_sdk_reference` documents its
sub-fields in full. On this data every `why_records` call returned `WHY_KEY_DETAILS` with an empty
`CONFIRMATIONS` array, on rules `SNAME_SSTAB` and `SF1_PNAME_CFF`, with `SZ_INCLUDE_FEATURE_SCORES`
in force. `FEATURE_SCORES` populated normally, so the evidence was available by another path.

By contrast, `how_entity`'s `RESOLUTION_STEPS[].MATCH_INFO.MATCH_KEY_DETAILS.CONFIRMATIONS[]` did
populate on the same entity.

### Why it matters

A documented, empty array is indistinguishable from a parsing bug. The module makes this path the
basis of a teaching step, so a bootcamper following it sees nothing and has no way to tell whether
they mis-parsed.

### Suggested fix

State the conditions under which `CONFIRMATIONS` populates on a why response, or note that it may be
empty and that `FEATURE_SCORES` carries the same evidence.

### Context when reported

- **Time:** 2026-08-18
- **Plugin version:** 0.5.1
- **Workstation:** macOS 24.4.0 (Intel x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** query_visualize_discover / step 4b
- **Recent questions:** What would you like to do next?
- **Bootcamper responses:** 1 (continue to How Analysis)
- **Behind the scenes:** `why_records` with SZ_INCLUDE_FEATURE_SCORES
- **Observed problem:** CONFIRMATIONS empty on all calls
- **Expected behavior:** per the documented schema, populated per contributing feature
- **Divergence:** empty, while the how-response equivalent populated

## Improvement: Docker bind-mount lag on macOS makes a just-written script fail with a phantom SyntaxError

**Date:** 2026-08-18
**Module:** Query, Visualize and Discover
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** host — macOS Docker Desktop bind-mount propagation, not plugin or server logic.
**Upstream:** not applicable

### What happened

Writing a Python file on the macOS host and immediately running it inside the container via the
`szrun` helper produced `SyntaxError: unterminated string literal` at a line that was well-formed.
Re-running the identical command moments later succeeded, and `compile()` inside the container
confirmed the file parsed. The container had read a partially-synced file.

The misdiagnosis it invites is specific: the container runs Python 3.11 and the host 3.12, so the
first hypothesis was a PEP 701 f-string incompatibility — plausible, wrong, and it cost a
verification round trip.

### Why it matters

The bootcamp writes host-side files and executes them container-side constantly. A transient,
convincing syntax error attributed to a version difference sends a bootcamper editing correct code.

### Suggested fix

Have `szrun` (or the guidance around it) allow a brief settle, or note in the SDK-setup module that a
syntax error on a just-written file should be retried once before being believed.

### Context when reported

- **Time:** 2026-08-18
- **Plugin version:** 0.5.1
- **Workstation:** macOS 24.4.0 (Intel x86_64), Docker Desktop bind mount
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** query_visualize_discover / step 2
- **Recent questions:** n/a
- **Bootcamper responses:** n/a
- **Behind the scenes:** `szrun` = `docker exec ... python3 /project/<path>`
- **Observed problem:** SyntaxError on a valid file, gone on retry
- **Expected behavior:** the container sees the file as written
- **Divergence:** bind-mount propagation lag
