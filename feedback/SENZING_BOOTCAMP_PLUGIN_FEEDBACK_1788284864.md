# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp. Every entry is saved here, whatever it turns
out to be about. Entries routed `mcp-server` may **also** have been forwarded to Senzing —
only ever with your explicit yes, and with identifying details stripped; each entry's
`Upstream:` field records what happened.

**Started:** 2026-08-26

## Your Feedback

## Improvement: Resumed-session recap checkpoint injects phantom module headings into the recap PDF

**Date:** 2026-08-26
**Module:** Bootcamp graduation
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the fold is performed by the plugin's own SessionStart:resume hook, and the recap generator's module parser is also the plugin's.
**Upstream:** not applicable

### What happened

The session was paused mid-module and resumed the next day. On resume, the hook folded
`docs/progress/recap_checkpoint.md` into `docs/bootcamp_recap.md` verbatim, inside
`<!-- RECAP-CHECKPOINT:START/END -->` markers. The checkpoint file's own internal structure used
`## ` headings (`## Where we are`, `## What is done in this module`, `## Still to do`,
`## To restart the visualization`, `## Headline results to carry in`).

The recap generator parses **every** `## ` heading as a module section. Had graduation rendered
without intervention, the keepsake PDF would have contained five phantom "modules" alongside the
nine real ones.

### Why it matters

It reaches the crown-jewel deliverable, and it is silent: no error, no warning, and the generator's
content-retention figure would have reported ~100% because no characters were lost — they were
merely mis-parsed. `--expect-modules` checks that expected modules are *present*, not that
unexpected ones are absent, so it would not have caught this either.

The pause/resume path is common, and the graduation skill already anticipates exactly this hazard
for a different input: it fences the bootcamper's notes in `<!-- BOOTCAMP-NOTES:START/END -->` and
states that the fence "is what makes this safe, not the heading text", because "a Bootcamper's
private note [is] one heading away from being printed on their Certificate of Completion". The
checkpoint fold has the same fence but the generator does not appear to lift it out before module
parsing, as it does for the notes block.

### Suggested fix

Make the recap generator lift the `RECAP-CHECKPOINT` block out before module parsing, exactly as it
already does for `BOOTCAMP-NOTES`. Alternatively, have the resume hook demote the checkpoint's
headings on fold, or write `recap_checkpoint.md` with `### ` headings so a verbatim fold cannot
create module-level headings.

### Context when reported

- **Time:** 2026-08-26 09:45 local
- **Plugin version:** 0.5.2
- **Workstation:** macOS 26.5.2 (Apple Silicon, arm64)
- **Model / effort:** claude-opus-5 / high

## Improvement: Java loading and configuration scaffolds import javax.json, which plain javac cannot resolve

**Date:** 2026-08-26
**Module:** Data processing
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the uncompilable import is in the code the MCP server returns.
**Upstream:** offered, awaiting the Bootcamper's decision

### What happened

`sdk_guide(topic='load', language='java', record_count=19584)` returned the threaded production
loader (`LoadViaFutures`), which opens with `import javax.json.*;`. JSON-P ships neither with the
JDK nor inside `sz-sdk.jar`, and the bootcamp installs no build tool to fetch it, so the returned
code cannot be compiled as delivered by a bootcamper following the Java path.

The same pattern appears in the system-verification scaffolds earlier in the bootcamp.

### Why it matters

Java is an officially supported binding, and `generate_scaffold`/`sdk_guide` are presented — rightly
— as the authoritative source that must not be hand-written around. A bootcamper who trusts the
returned code hits a raw import error in code they were told was canonical, at the exact moment
they are least equipped to judge whether the tool or their environment is at fault.

The plugin already anticipates this (Module 2's "launch environment" note, and Module 6 Phase A's
instruction to check imports *before* compiling), and the workaround is sound: swap only the JSON
reader, keep every Senzing call verbatim. But the workaround is applied on the bootcamper's side
each time, in every Java session.

### Suggested fix

Either emit Java snippets using a dependency-free JSON read for the two fields actually needed
(`DATA_SOURCE`, `RECORD_ID`), or state the `javax.json` dependency and its coordinates in the
response's `compatibility_notes` so it is visible before the compile rather than after.

### Context when reported

- **Time:** 2026-08-26 09:45 local
- **Plugin version:** 0.5.2
- **Workstation:** macOS 26.5.2 (Apple Silicon, arm64)
- **Model / effort:** claude-opus-5 / high

## Improvement: Visualization server model build does one getEntity per record, which does not scale to Module 7 volumes

**Date:** 2026-08-26
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the reference implementation and the "model it on the Truth Set server" instruction are both the plugin's.
**Upstream:** not applicable

### What happened

The Truth Set visualization server builds its model by reading a records file and calling
`getEntity` once per record — correct and fast at the Truth Set's 84 entities. Module 7 instructs
that the same server be pointed at the bootcamper's own data, which here was 19,584 records, making
19,584 round trips to build one page.

Rebuilding it on the export stream (`exportJsonEntityReport` / `fetchNext` / `closeExportReport`)
built the full model in ~15 seconds. The change was small because each export row carries the same
shape a `getEntity` response does, so the existing absorb step needed no modification.

### Why it matters

Every Module 7 bootcamper with real data hits this, and it degrades with dataset size — the case
the module explicitly steers toward. A second benefit is correctness, not just speed: the
records-file build can only see entities that have a record in the file it was handed, whereas the
export stream yields every resolved entity, including embedded-master records the mapper emitted
that appear in no input file.

### Suggested fix

Give the reference server an export-stream build path and prefer it when the target is the
bootcamper's own datastore rather than the Truth Set.

### Context when reported

- **Time:** 2026-08-26 09:45 local
- **Plugin version:** 0.5.2
- **Workstation:** macOS 26.5.2 (Apple Silicon, arm64)
- **Model / effort:** claude-opus-5 / high

## Improvement: Vendored D3 resolves only through the plugin cache, so the live visualization breaks after a plugin update

**Date:** 2026-08-26
**Module:** Query, Visualize and Discover
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the lookup order is in the generated server, and the asset lives in the plugin.
**Upstream:** not applicable

### What happened

The visualization server resolves its offline D3 asset from `CLAUDE_PLUGIN_ROOT/scripts/vendor/` or
`SENZING_VENDOR_D3`, and refuses to render without one (correctly, since a CDN fallback would break
the offline guarantee). Neither is set in a plain shell, so re-running the server later fails with
"vendored D3 not found" even though the project is otherwise intact.

### Why it matters

Module 7 frames the visualization as something to keep and return to, and Step 6c's return guide
tells the bootcamper how to restart it. But the asset it depends on lives in a versioned plugin
cache directory that a plugin update can move or remove, so the documented restart path can stop
working for reasons unrelated to the project.

The standalone snapshot is unaffected — D3 is inlined there — so only the live app is at risk.

### Suggested fix

Have the generated server also look for a project-local `vendor/d3.v7.min.js`, and copy the asset
into the project when the visualization is first built. Applied locally in this run.

### Context when reported

- **Time:** 2026-08-26 09:45 local
- **Plugin version:** 0.5.2
- **Workstation:** macOS 26.5.2 (Apple Silicon, arm64)
- **Model / effort:** claude-opus-5 / high

## Improvement: WHY_KEY_DETAILS absent from why_records under its own default flags (confirms an observation-only note)

**Date:** 2026-08-26
**Module:** Query, Visualize and Discover
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the question is which flag populates a documented response field.
**Upstream:** offered, awaiting the Bootcamper's decision

### What happened

`whyRecords(...)` called with `SZ_WHY_RECORDS_DEFAULT_FLAGS | SZ_ENTITY_INCLUDE_ENTITY_NAME`
returned a complete `FEATURE_SCORES` block and no `WHY_KEY_DETAILS`, so the confirmations breakdown
could not be shown and the presentation fell back to feature scores. The same field *was* returned
through a different call path in the same session that used a different flag set.

This matches the plugin's existing observation-only note that populating `WHY_KEY_DETAILS` may
require `SZ_INCLUDE_MATCH_KEY_DETAILS` plus a relations flag, with no flag documented as populating
it. Filing as a second data point on a supported binding (Java) rather than as a new finding.

### Why it matters

The field is in the documented response schema, so a parser written against the schema renders an
empty section rather than raising — the silent-blank failure mode the module warns about
repeatedly. Knowing which flag populates it would close the last of these.

### Suggested fix

Document the flag that populates `WHY_KEY_DETAILS` in the `why_*` flag reference, or note in the
response schema that the field is conditional on flags outside the method's default composite.

### Context when reported

- **Time:** 2026-08-26 09:45 local
- **Plugin version:** 0.5.2
- **Workstation:** macOS 26.5.2 (Apple Silicon, arm64)
- **Model / effort:** claude-opus-5 / high
