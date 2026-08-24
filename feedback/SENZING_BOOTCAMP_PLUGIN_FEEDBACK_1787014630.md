# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp. Every entry is saved here, whatever it turns
out to be about. Entries routed `mcp-server` may **also** have been forwarded to Senzing —
only ever with your explicit yes, and with identifying details stripped; each entry's
`Upstream:` field records what happened.

**Started:** 2026-08-17

## Your Feedback

## Improvement: Stop hook throws NameError: name 'false' is not defined

**Date:** 2026-08-17
**Module:** Discover the Business Problem
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — a bootcamp-shipped Stop hook script is raising a Python `NameError` on the lowercase JSON literal `false` instead of Python's `False`; unrelated to the Senzing MCP server.
**Upstream:** not applicable

### What happened

The bootcamper keeps seeing a non-blocking Stop hook error:

```
Stop hook error: Failed with non-blocking status code: Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'false' is not defined. Did you mean: 'False'?
```

### Why it matters

It's distracting and makes the bootcamper think something is broken when, from their point of
view, nothing else is failing.

### Suggested fix

None provided.

### Context when reported

- **Time:** 2026-08-17 14:37 local
- **Plugin version:** 0.5.1
- **Workstation:** Linux 6.8.0-136-generic (x86_64)
- **Model / effort:** claude-sonnet-5 / medium
- **Context size:** Unknown
- **Module / step:** business_problem / null (Phase 1, Step 1/2 pending — "Would you like to see examples of common business problems...")
- **Recent questions:** "Would you like to see examples of common business problems that entity resolution can solve?"
- **Bootcamper responses:** Not yet answered (feedback interrupted this pending question).
- **Behind the scenes:** A plugin `Stop` hook (a `type: command` hook, run as a deterministic script, not a Claude turn) errored with a non-blocking status. The traceback shows a bare Python one-liner executed with the lowercase JSON boolean `false` where Python's `False` was required — consistent with a hook script passing a JSON-formatted value directly into a Python `eval`/`-c` context without translating JSON booleans to Python booleans.
- **Observed problem:** The `NameError` traceback above, appearing repeatedly.
- **Expected behavior:** The Stop hook should run without raising an error, or fail silently/log without surfacing a traceback to the bootcamper.
- **Divergence:** The hook script itself has a bug (JSON/Python literal mismatch); this is a defect in the shipped hook code, not something the bootcamper's session state caused.

## Improvement: sdk_guide(topic='configure') ignores its own data_sources parameter

**Date:** 2026-08-17
**Module:** Data processing
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the tool declares a `data_sources` parameter and does not apply it to the returned snippet; nothing in the plugin can fix this.
**Upstream:** forwarded to Senzing on 2026-08-17 via `submit_feedback` (category `bug`), batched with the other mcp-server finding from this session, with identifying details stripped; the server confirmed submission and noted that submissions are anonymous, so no follow-up is possible on it.

### What happened

Called `sdk_guide(topic='configure', language='python', data_sources=["ECOMMERCE_ORDERS", "POS_LOYALTY", "EMAIL_MARKETING"])`.
The tool's declared schema documents the parameter as *"Data sources to register (for configure
topic)"*, but the returned snippet still carried the hardcoded sample tuple:

```python
for data_source in ("CUSTOMERS", "REFERENCE", "WATCHLIST"):
    sz_config.register_data_source(data_source)
```

with a `notes` entry saying "Replace sample data source names with your own". The supplied
`data_sources` values appear nowhere in the response.

### Why it matters

A parameter that is declared, accepted, and then silently ignored is worse than an absent one: a
caller reasonably assumes the snippet is parameterized and may hand it straight to a build step.
The failure is silent — the code compiles and runs, and registers three data sources the
bootcamper does not have, so the first load fails later with `SENZ2207` for the codes they *do*
have. Every bootcamper registers their own codes at this step, so the path is universal.

### Suggested fix

Either substitute the supplied `data_sources` into the returned snippet, or drop the parameter
from the schema and keep the "replace these" note as the only contract.

### Context when reported

- **Time:** 2026-08-17 evening, local
- **Plugin version:** 0.5.1
- **Workstation:** Linux 6.8.0-136-generic (x86_64)
- **Model / effort:** claude-sonnet-5 / medium (finding), filed under claude-opus-5 / high
- **Module / step:** data_processing / Phase A step 4a (register the data source codes)
- **Observed problem:** `data_sources` argument absent from the returned code and from every other field of the response.
- **Expected behavior:** the returned snippet iterates the supplied codes, or the parameter is not offered.
- **Divergence:** declared schema vs. returned payload, within a single call.

## Improvement: register_data_source() does not raise on an already-registered code (Python), contrary to the indexed SDK reference

**Date:** 2026-08-17
**Module:** Data processing
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — an indexed SDK reference documents an error condition the Python binding does not raise; the divergence is in the served documentation, not in plugin code.
**Upstream:** forwarded to Senzing on 2026-08-17 via `submit_feedback` (category `bug`), batched with the other mcp-server finding from this session, with identifying details stripped; the server confirmed submission and noted that submissions are anonymous, so no follow-up is possible on it.

### What happened

Module 6 Phase A step 4a requires the generated registration code to be **idempotent**. To find
the documented failure mode, ran
`search_docs(query='register_data_source already exists idempotent duplicate', category='sdk')`,
which returned the Rust SDK reference for `SzConfig::register_data_source`:

> **Errors** — `SzError::BadInput` - Data source code is invalid **or already exists**

Wrote the Python registration script to catch `SzBadInputError` per code on that basis. Running it
twice against the same config printed all three codes as newly registered both times, with an
identical new config ID (`3975847437`) — i.e. `register_data_source()` raised nothing on the
second pass, and the `except SzBadInputError` branch never executed. The net result was still
idempotent, but by a different mechanism (registering an identical config returns the existing
config ID) than the one the code was written to rely on.

### Why it matters

The step's requirement is idempotency, so every bootcamper's guide has to reason about what
"already registered" does. Coding to the documented `BadInput` yields a script whose idempotency
handling is dead code — it appears to work, and would fail in exactly the case it was written for
if the surrounding behavior ever changed. The reference is also cross-binding: it is the Rust
trait doc, surfaced for a Python question, which is the documented cross-binding hazard
(`get_sdk_reference` warns about name/type divergence, but not about *error-condition*
divergence).

### Suggested fix

State the per-binding behavior for re-registering an existing data source code, or note on the
Rust entry that the raised-error contract is binding-specific.

### Context when reported

- **Time:** 2026-08-17 evening, local
- **Plugin version:** 0.5.1
- **Workstation:** Linux 6.8.0-136-generic (x86_64)
- **Senzing SDK:** 4.3.4 (build 4.3.4.26210)
- **Model / effort:** claude-sonnet-5 / medium (finding), filed under claude-opus-5 / high
- **Module / step:** data_processing / Phase A step 4a
- **Observed problem:** no exception on re-registration; documented `BadInput` never raised.
- **Expected behavior:** either the documented error, or documentation that says it is not raised here.
- **Divergence:** indexed SDK reference vs. observed Python-binding behavior.

## Improvement: Module 4's example quality gaps do not produce the quality band Module 4 asks for

**Date:** 2026-08-17
**Module:** Data collection
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — a cross-module inconsistency between Module 4's generation guidance and Module 5's scoring formula, both plugin-authored.
**Upstream:** not applicable

### What happened

On the generated-scenario path, Module 4 requires the synthesized data to put "**at least one
source in the 70-79% band**" so that Module 5's remediation branch is reachable, and illustrates
the gaps with examples like *"a phone absent on roughly a third of its records, an address missing
on a handful"*.

Generating to those example rates and then scoring with Module 5's formula
(`0.70 × completeness + 0.25 × format_consistency + 0.05 × (100 − duplicate_rate)`) produced
**94.9%** — squarely in the `>=80` band, not 70-79. The reason is arithmetic: completeness is the
mean per-record share of *applicable* fields present, so gapping one field out of seven at 30%
moves completeness by only ~4 points. Landing in 70-79 required gapping five of seven fields far
more aggressively (phone ~55% missing, address ~45%, city ~35%, zip ~25%, state ~20%) to reach
72.9% completeness / **79.5%** overall.

Because Module 4 records the intended band as `quality_intent` in `config/data_sources.yaml`
*before* Module 5 ever scores the data, the mismatch is invisible at generation time and only
surfaces a module later — where, as Module 4 itself notes, it is indistinguishable from a scoring
fault.

### Why it matters

Module 4 states the reachability of Module 5's remediation branches as the whole point of the
quality-gap requirement: a bootcamper who sees `100% ✅` (or `94.9% ✅`) three times "reasonably
concludes the quality step is a formality". Following the example rates literally defeats the
requirement they illustrate, on the path where the plugin generates the data itself and so fully
controls the outcome.

### Suggested fix

State the gap rates in terms of the target *completeness* rather than per-field absence — e.g.
"gap enough non-key fields that mean per-record completeness lands near 72-75%" — or give a worked
example showing the arithmetic for a seven-field source. Optionally have the generation step score
its own output and re-generate if the band is missed, since Module 5's formula is already fully
specified.

### Context when reported

- **Time:** 2026-08-17 evening, local
- **Plugin version:** 0.5.1
- **Workstation:** Linux 6.8.0-136-generic (x86_64)
- **Model / effort:** claude-sonnet-5 / medium (finding), filed under claude-opus-5 / high
- **Module / step:** data_collection / step 2 (synthesized provenance), surfacing at data_quality_mapping / step 6
- **Observed problem:** example gap rates yield ~95%, not the required 70-79% band.
- **Expected behavior:** following Module 4's stated gap guidance lands a source in the band Module 4 requires.

## Improvement: Module 7's possible-match bands can route a bootcamper into a remap with nothing to fix

**Date:** 2026-08-17
**Module:** Query, Visualize and Discover
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the quality-gate banding and its Module 5 feedback loop are plugin-authored guidance.
**Upstream:** not applicable

### What happened

Module 7 step 3b bands the possible-match rate into Acceptable (<5%), Marginal (5-15%) and Poor
(>15%), and routes Poor to *"The results suggest mapping improvements would help"* plus the
Module 5 feedback loop.

This session measured **48.9%** of entities carrying a `POSSIBLY_SAME` relation. The sampled
evidence the same step requires showed the cause was *not* a mapping defect: roughly half the
near-misses came from one source's genuinely empty contact fields (PHONE 45.7% / ADDRESS_LINE1
55% populated — correctly mapped, values simply absent from the source file), and the rest from
coincidental full-name collisions in the synthetic generator's limited name pool. Neither is
fixable by remapping.

The band was followed anyway, the feedback loop was offered, the bootcamper accepted it, and the
remap had nothing to change — same source file, same already-correct field mappings. It took an
extra confirmation to establish that re-running `mapping_workflow` would reproduce the identical
mapping, and to return to Module 7.

### Why it matters

Module 6's match-key audit has an explicit guard for exactly this shape — *"Report a high-share
cross-source suppressor as a FINDING, never a pass/fail … a hard failure here would produce false
alarms and train bootcampers to dismiss the signal"* — but step 3b's possible-match bands carry no
equivalent caveat, even though the possible-match rate is even more strongly driven by data
characteristics the mapping cannot change (field sparsity, name commonality, dataset size). The
result is a documented route into wasted work at the very end of the bootcamp, and a bootcamper
who is told their mapping needs improvement when the evidence in front of them says otherwise.

### Suggested fix

Give the Poor branch the same finding-not-gate framing the match-key audit already has: require
the sampled evidence to identify a *mapping-actionable* cause before the Module 5 loop is offered,
and name the two common non-actionable causes (source field sparsity, name-only collisions in
small or synthetic datasets) so they are recognized rather than rediscovered. A band alone should
not be sufficient to trigger the loop.

### Context when reported

- **Time:** 2026-08-17 evening, local
- **Plugin version:** 0.5.1
- **Workstation:** Linux 6.8.0-136-generic (x86_64)
- **Model / effort:** claude-sonnet-5 / medium (finding), filed under claude-opus-5 / high
- **Module / step:** query_visualize_discover / step 3b (quality evaluation)
- **Observed problem:** a 48.9% possible-match rate routed to "mapping improvements would help" when the evidence showed no mapping-actionable cause.
- **Expected behavior:** the gate distinguishes a mapping-actionable cause from a data characteristic before recommending a remap.

## Improvement: why_* MATCH_INFO scalars are WHY_KEY / WHY_ERRULE_CODE, and the docs warn only about WHY_KEY_DETAILS

**Date:** 2026-08-17
**Module:** Query, Visualize and Discover
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — an addition to a warning the plugin already carries in two places.
**Upstream:** not applicable

### What happened

Module 7's Phase 1 and Phase 2a both warn, correctly and at length, that a why response's
match-key breakdown lives at `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS` and **not** at
`MATCH_KEY_DETAILS`. Neither mentions that the *sibling scalar fields* in the same object are
also differently named: they are `WHY_KEY` and `WHY_ERRULE_CODE`, where the analogous
`get_entity` / export paths use `MATCH_KEY` and `ERRULE_CODE`.

Wrote a `why_explain` program using `MATCH_KEY` / `ERRULE_CODE` by habit from the entity-side
shape, and caught it only because Module 7 separately requires reading
`get_sdk_reference(topic='response_schemas', filter='<method>')` before writing any parser
(INV-115). Uncaught, both fields would have rendered blank with no error — the exact silent
failure the surrounding guidance exists to prevent, one field over from where it points.

### Why it matters

The existing warning teaches the reader that the *details object* is differently named, which
implicitly reassures them that the neighbouring fields are not. Anyone building the "explain this
match" deliverable Module 7 asks for touches these two fields first, and a blank match key in an
explainability feature reads as "Senzing gave no reason" rather than as a wrong field name.

### Suggested fix

Extend the existing `WHY_KEY_DETAILS` warning by one clause naming `WHY_KEY` and
`WHY_ERRULE_CODE` alongside it — the trap and the fix are identical, so it needs no new block.

### Context when reported

- **Time:** 2026-08-17 evening, local
- **Plugin version:** 0.5.1
- **Workstation:** Linux 6.8.0-136-generic (x86_64)
- **Senzing SDK:** 4.3.4 (build 4.3.4.26210)
- **Model / effort:** claude-sonnet-5 / medium (finding), filed under claude-opus-5 / high
- **Module / step:** query_visualize_discover / step 2 (create query programs)
- **Observed problem:** `MATCH_KEY` / `ERRULE_CODE` are absent from `WHY_RESULTS[].MATCH_INFO`; the names are `WHY_KEY` / `WHY_ERRULE_CODE`.
- **Expected behavior:** the existing warning names all three differently-named fields, not just the details object.

## Improvement: the bundled capture_screenshots.py is not named at the point of use, and screenshot capture was skipped as a result

**Date:** 2026-08-17
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the script ships with the plugin; the gap is that the steps requiring capture do not name its path where they require it.
**Upstream:** not applicable

### What happened

Module 3b and Module 7 both require capturing one screenshot per visualization tab, pointing at
`module-completion.md` → "Capturing visualization screenshots" for the procedure. At Module 7
step 3c, after verifying all six tabs served correctly, capture was **skipped** on the stated
grounds that driving the app's tab switching needed browser automation that was unavailable —
without first checking whether the plugin already shipped a tool for it.

It does: `capture_screenshots.py`, alongside the visualization server in the plugin's `scripts/`
directory, taking `--url` / `--html`, `--tabs`, `--name` and `--query`, and writing both the PNGs
and a `<name>-tabs.json` coverage manifest. It ran first try against plain headless Chrome and
captured 6/6 tabs with real search results.

Recovered at graduation: the Module 7 server was briefly restarted for a live capture (all six
tabs, Search / Probe showing real results), and the Truth Set module's six tabs were captured from
its retained static snapshot — 12 images that the recap PDF would otherwise not have carried. The
Truth Set live capture was **permanently lost**, since its records were purged at that module's
close exactly as its own guidance warns.

### Why it matters

The skip was silent and self-justified, and the requirement is stated in a different file from the
capability, so nothing in the reading path contradicts a guide that concludes capture is
impossible. Module 3b states the consequence plainly — a missed capture there cannot be re-taken
after teardown — so a reachable-but-unnamed tool costs the keepsake its most visual content in a
way that is unrecoverable for one module and only luckily recoverable for the other.

### Suggested fix

Name the bundled script and its resolution rule at the two points that require capture (Module 3b
2.2 and Module 7 3c), the way `senzing_viz_server.py`, `generate_recap_pdf.py`,
`generate_discoveries_pdf.py` and `normalize_docs_markdown.py` are already named with their
`${CLAUDE_PLUGIN_ROOT}` / skill-relative fallback paths. A one-line invocation at the point of use
would have prevented the skip entirely.

### Context when reported

- **Time:** 2026-08-17 evening, local
- **Plugin version:** 0.5.1
- **Workstation:** Linux 6.8.0-136-generic (x86_64)
- **Model / effort:** claude-sonnet-5 / medium (the skip), recovered under claude-opus-5 / high
- **Module / step:** query_visualize_discover / step 3c; also truthset_visualization / 2.2
- **Observed problem:** capture skipped as unavailable while a working bundled capture script shipped with the plugin.
- **Expected behavior:** the step that requires capture names the tool that performs it.
