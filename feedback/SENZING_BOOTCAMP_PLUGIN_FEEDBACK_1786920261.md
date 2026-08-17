# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp. Every entry is saved here, whatever it turns
out to be about. Entries routed `mcp-server` may **also** have been forwarded to Senzing —
only ever with your explicit yes, and with identifying details stripped; each entry's
`Upstream:` field records what happened.

**Started:** 2026-08-16

## Your Feedback

## Improvement: Licence-budget question gives no path to applying a Senzing licence

**Date:** 2026-08-16
**Module:** Data processing
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — Phase B tells the guide to restate licence expansion "as a choice" but supplies no apply-a-licence procedure and no reminder that a licence requested in Data collection arrives by email; a perfect MCP server would not change this.
**Upstream:** not applicable

### What happened

At the licence-budget decision point in Data processing (Phase B, before the full load), the guide
presented three options for spending a 500-record evaluation limit:

1. Build an overlap-preserving 500-record subset and load that now (recommended)
2. Wait until the evaluation licence is applied, then load all 7,718
3. Load the first 500 records as they come, no overlap selection

Nothing in that turn reminded the bootcamper that the free evaluation licence they had already
requested during Data collection (Step 8a, via the MCP server's `submit_feedback` /
`license_request` path) is delivered **by email** and may already have arrived. Option 2 named the
outcome — "until the evaluation licence is applied" — but gave no instructions for applying one:
no file location, no environment variable, no verification step, and no offer to help do it.

### Why it matters

The bootcamper is asked to choose between working around a limit and waiting for something they
may already possess, with no route to the better outcome. Applying the licence removes the
constraint entirely and lets the full dataset load, which is what Modules 6 and 7 need in order to
demonstrate cross-source resolution. Instead the recommended path is a 500-record workaround.

The timing makes it worse: this is the first moment in the bootcamp where the licence limit has a
real, visible consequence, so it is exactly when the bootcamper would act on a reminder — and
exactly when they are least likely to think of their inbox unprompted.

### Suggested fix

At this decision point, remind the bootcamper that their evaluation licence may have arrived by
email, and guide them through applying it — where the licence file goes, how the engine
configuration references it, and how to confirm the new record limit took effect (re-read
`SzProduct.getLicense()` and check `recordLimit`). Make "I have the licence, help me apply it" a
first-class option in the question rather than something the bootcamper has to think of.

### Context when reported

- **Time:** 2026-08-16 14:58 EDT
- **Plugin version:** 0.5.1
- **Workstation:** Darwin 25.5.0 (arm64), macOS on Apple Silicon
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown (long session, one compaction boundary already crossed)
- **Module / step:** `data_processing` / `4a` (Phase B, step 7 — full load pending)
- **Recent questions:** (a) "In production, how many records do you expect to load?" (b) "Loading this data volume into SQLite may slow entity resolution as the database grows. How would you like to proceed?" (c) "How would you like to spend the 500-record licence budget?"
- **Bootcamper responses:** (a) 3 — medium production; (b) 1 — proceed on SQLite; (c) feedback submitted instead of an answer
- **Behind the scenes:** `module-06-data-processing` / `phaseB-load-first-source.md` step 7, "License capacity before loading". `license_record_limit` had been re-measured live via `SzProduct.getLicense()` (`recordLimit: 500`, EVAL, expires 2027-06-12) and reconciled against a 7,718-record dataset, landing on the "positive and below the dataset size" branch. `config/bootcamp_preferences.yaml` records `license: evaluation` from Data collection Step 8a, where the request was sent.
- **Observed problem:** The licence question offered no way to apply a licence and no reminder that one may have been delivered by email.
- **Expected behavior:** Phase B step 7's branch says to "restate that a larger license lets the full load proceed, as a choice, not a wall". Restating an option the bootcamper cannot act on is not a real choice — the branch needs to carry the apply-a-licence procedure, and to check the `license: evaluation` marker as a signal that a request is outstanding and may have landed.
- **Divergence:** The phase text specifies what to *say* about licence capacity but not what to *do* about it. Module 4 Step 8a owns the request path; nothing owns the apply path, so it falls in the gap between the two modules. The `license: evaluation` preference records that a request was made but is never re-read later as a prompt to follow up.

## Improvement: WHY_KEY_DETAILS absent from why_records responses on SDK 4.3.2

**Date:** 2026-08-16
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the reference documents a response path the installed SDK does not return; a perfect plugin would still have written the parser against it, because the plugin is correctly relaying what the tool says.
**Upstream:** submitted 2026-08-16

### What happened

`phase2-discover.md` step 4b states, citing `get_sdk_reference(topic='response_schemas',
filter='why_records')` on server 1.32.9, that the why-key breakdown "sits at
`WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS` — an object whose `CONFIRMATIONS[]` entries each name the
feature that contributed (`FTYPE_CODE`, `TOKEN`, `SOURCE`) with its `SCORE` and `SCORE_BUCKET`".

A parser written against exactly that path returned nothing. Dumping the raw keys of the response
showed `MATCH_INFO` carrying only:

```
CANDIDATE_KEYS, DISCLOSED_RELATIONS, FEATURE_SCORES, MATCH_LEVEL_CODE, WHY_ERRULE_CODE, WHY_KEY
```

No `WHY_KEY_DETAILS`, with `SZ_WHY_RECORDS_DEFAULT_FLAGS | SZ_ENTITY_INCLUDE_ENTITY_NAME` in force.
Note the same run found `MATCH_KEY_DETAILS` (with `CONFIRMATIONS[]`/`DENIALS[]`) documented and
populated on the `search_by_attributes` response — so the structure exists in this SDK, just not on
the why path.

### Why it matters

The plugin goes to unusual lengths to warn that a blank field has three causes and that a wrong
field name renders blank rather than raising. This is a fourth situation the guidance does not
anticipate: the documented path is right, the flags are right, and the field is simply not returned
by this SDK build. A guide following the instruction exactly gets an empty section and no signal
that anything is wrong.

It is also self-defeating in a specific way: step 4b instructs the guide NOT to reach for
`SZ_INCLUDE_MATCH_KEY_DETAILS` because `WHY_KEY_DETAILS` "is already there without it" — advice that
is correct in intent but rests on a field that was not present here.

### Suggested fix

Confirm which SDK versions populate `WHY_KEY_DETAILS` on `why_records` and note the floor in the
step. Until then, tell the guide to fall back to `FEATURE_SCORES` (which carries the same
per-feature evidence and was fully populated) and to dump the `MATCH_INFO` keys before parsing,
rather than presenting `WHY_KEY_DETAILS` as reliably present.

### Context when reported

- **Time:** 2026-08-16 16:20 EDT
- **Plugin version:** 0.5.1
- **Workstation:** Darwin 25.5.0 (arm64), macOS on Apple Silicon
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown (long session, one compaction boundary crossed)
- **Module / step:** `query_visualize_discover` / `4b`
- **Recent questions:** the Discover-phase opt-in and the post-demonstration "what next" transitions
- **Bootcamper responses:** yes; 1; 1
- **Behind the scenes:** `Discover.why()` calling `whyRecords(SzRecordKey, SzRecordKey, Set<SzFlag>)` on Senzing SDK 4.3.2, parsing `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS`
- **Observed problem:** the CONFIRMATIONS/DENIALS breakdown printed nothing; raw key dump showed the object absent
- **Expected behavior:** per the step's own citation, `WHY_KEY_DETAILS` present with `CONFIRMATIONS[]`
- **Divergence:** documented response shape does not match what this SDK build returns on this method

## Improvement: Count-mismatch rule would file a successful load as failed

**Date:** 2026-08-16
**Module:** Data processing
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the rule is stated in `phaseB-load-first-source.md`; no MCP behaviour is involved.
**Upstream:** not applicable

### What happened

`phaseB-load-first-source.md` step 7 states, as a ⛔ rule: "If the two disagree, write the
discrepancy rather than the count (INV-245): leave the existing `record_count` in place, set
`load_status` to `failed`, record both figures in the `issues` entry, and do not present the loaded
count as a result."

PPP_LOANS loaded 3,727 records from a source `record_count` of 3,488. The two disagree, and the
disagreement is entirely expected and documented: the mapper emits 239 distinct lenders as embedded
masters, exactly as `docs/mapping/PPP_LOANS_mapper.md` specifies. Every input record loaded and
there were zero errors.

Following the rule literally would have set `load_status: failed` on a completely successful load.

### Why it matters

The rule's stated rationale is that overwriting on a mismatch "destroys the input baseline and files
a partial load as a complete one". Both halves are right, but the prescribed remedy over-fires: it
also files a *complete* load as a *failed* one, which is the mirror-image misreport. Downstream,
Phase C step 12 reads `load_status` back and presents it, and Phase D writes it into
`docs/loading_strategy.md`, so a false failure propagates exactly as far as a false success.

An embedded master is not an edge case — it is a mapping pattern the bootcamp actively teaches in
Data Quality, Mapping, and Transformation, and it necessarily changes the record count.

### Suggested fix

Split the branch. On a mismatch, ask whether the delta is *explained by the mapping*: if the source's
mapping specification documents a record-multiplying disposition (embedded master) or a
denormalizing fold, record `load_status: loaded` with both figures and a `load_reconciliation` note,
and mark the check `expected_delta`. Reserve `failed` for a mismatch with no documented explanation
— which is the case the rule was written for. The step already anticipates the fold direction
("a legitimate denormalizing fold reduces the count and is fine" appears in Phase A's coverage note),
so the concept exists; it just is not carried into this rule.

### Context when reported

- **Time:** 2026-08-16 16:20 EDT
- **Plugin version:** 0.5.1
- **Workstation:** Darwin 25.5.0 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** `data_processing` / Phase B step 7
- **Recent questions:** production volume tier; SQLite volume prompt
- **Bootcamper responses:** 3 (medium); 1 (proceed on SQLite)
- **Behind the scenes:** writing `config/data_sources.yaml` after the PPP_LOANS load
- **Observed problem:** the only compliant action was to mark a clean 3,727-record load as failed
- **Expected behavior:** a documented, expected delta should be recordable as such
- **Divergence:** the rule tests for equality without an exemption for mapping-explained deltas

## Improvement: Module 7 visualization inherits Truth Set scale defaults that misrepresent real data

**Date:** 2026-08-16
**Module:** Query, Visualize and Discover
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the behaviour is in the shipped reference server and the step-3c instructions.
**Upstream:** not applicable

### What happened

Step 3c says to build the results app "modeled on the shipped Truth Set visualization server", and
warns to "mind the scale", noting the graph label defaults are scale-aware above ~150 nodes. Two
defaults below that warning are not scale-aware and produce actively misleading output:

1. **The graph endpoint emits every entity.** With 5,678 entities (3,692 of them unconnected
   singletons) this is an unreadable hairball and a very large embedded snapshot. Only the *label*
   threshold is scale-aware; the node set is not.
2. **Nodes are filled with `colorFor(d.data_sources[0])`** — the first data source alphabetically.
   On the Truth Set, where most entities sit in one source, this reads correctly. On this data every
   cross-source entity begins with `GLEIF`, so all 1,951 of them rendered in the *single-source*
   GLEIF colour. The headline result of the entire bootcamp — vendors found in more than one system
   — was invisible in the tab built to show it, with a legend that positively implied they were
   GLEIF-only.

Both were fixed by hand: cap the graph and rank by source span, and allocate colours over source
*combinations* (in one allocation, since two separate `colorForSources()` calls each restart at the
top of the palette and reproduce the collision).

### Why it matters

Step 3c states the operative risk itself — "the bootcamper cannot tell a bad default from bad data"
— and then ships defaults that fail exactly that test. The colour bug is the more serious of the
two because it does not look broken: the graph renders, the legend is populated, and the picture is
simply wrong. A guide who follows the instruction to model on the reference server, and does not
independently check what the colours are encoding, hands over a keepsake that understates the
result.

### Suggested fix

Move both fixes into the shipped reference server so every bootcamp gets them: cap the graph node
set with the count reported in the payload (so the UI can state what it is showing), rank
candidates by source span before connectivity, and fill nodes by the sorted source-combination key
with combination entries in the legend. All three are small and none changes Truth Set behaviour,
where entities are mostly single-source and the combination key degenerates to the single source.

### Context when reported

- **Time:** 2026-08-16 16:20 EDT
- **Plugin version:** 0.5.1
- **Workstation:** Darwin 25.5.0 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** `query_visualize_discover` / `3c`
- **Recent questions:** the step-3c visualization offer
- **Bootcamper responses:** yes
- **Behind the scenes:** `src/server/VizServer.java`, ported from `scripts/senzing_viz_server.py` in the Truth Set module, repointed at 7,718 loaded records
- **Observed problem:** 5,678-node graph; all cross-source entities rendered in the single-source colour
- **Expected behavior:** a graph legible at the bootcamper's actual entity count, encoding cross-source membership visibly
- **Divergence:** the scale warning covers labels only, and the colour encoding was written for single-source entities

## Improvement: howEntity resolution-step field names are undocumented and easy to get wrong

**Date:** 2026-08-16
**Module:** Query, Visualize and Discover
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the plugin records MCP-confirmed response paths for the analogous find_network case but not for this one.
**Upstream:** not applicable

### What happened

Step 4c demonstrates How Analysis but does not name the fields inside
`HOW_RESULTS.RESOLUTION_STEPS[]`. A parser written against the plausible
`INBOUND_VIRTUAL_ENTITY` / `CANDIDATE_VIRTUAL_ENTITY` produced a merge sequence with the steps and
match keys present and **no records named at all** — the output looked complete and simply had
nothing to say about which records merged, which is the entire point of How Analysis. Dumping the
step's keys showed the real names:

```
STEP, MATCH_INFO, INBOUND_VIRTUAL_ENTITY_ID, RESULT_VIRTUAL_ENTITY_ID,
VIRTUAL_ENTITY_1, VIRTUAL_ENTITY_2
```

### Why it matters

This is the same failure mode the plugin already protects against elsewhere: `phase2b-discover.md`
carries a detailed ⚠️ that `find_network` link endpoints are `MIN_ENTITY_ID`/`MAX_ENTITY_ID` rather
than the `ENTITY_ID`/`RELATED_ENTITY_ID` pairing one would guess, and records those names in the
visualization API reference as MCP-confirmed. The `how_entity` step has no equivalent, despite
`VIRTUAL_ENTITY_1`/`VIRTUAL_ENTITY_2` being just as counter-intuitive — and note the step object
*also* carries `INBOUND_VIRTUAL_ENTITY_ID`, so the wrong guess is actively suggested by a real
neighbouring key.

### Suggested fix

Add the step's field names to step 4c the way `find_network`'s are given in step 4d, and record them
in the visualization API reference's "MCP-confirmed response paths" section.

### Context when reported

- **Time:** 2026-08-16 16:20 EDT
- **Plugin version:** 0.5.1
- **Workstation:** Darwin 25.5.0 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** `query_visualize_discover` / `4c`
- **Recent questions:** the post-Why-Analysis transition
- **Bootcamper responses:** 1 (continue to How Analysis)
- **Behind the scenes:** `Discover.how()` calling `howEntity(long, Set<SzFlag>)` on SDK 4.3.2
- **Observed problem:** merge steps printed with no member records
- **Expected behavior:** each step naming the records on either side
- **Divergence:** field names guessed from a plausible convention; the real ones are undocumented in the plugin
