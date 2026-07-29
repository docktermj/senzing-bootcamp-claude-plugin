# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp.

**Started:** 2026-01-01

## Your Feedback

## Improvement: A precious entry that must survive graduation untouched

**Date:** 2026-01-01
**Module:** Data collection
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — the banner did not appear
**Upstream:** not applicable

### What happened

If graduation's normalization pass rewrites, empties or deletes this file, INV-067 is
broken and this sentence will be missing.

## Improvement: search_by_attributes and find_network_by_entity_id's own default flags omit RECORDS[], populate RECORD_SUMMARY[] instead

**Date:** 2026-07-29
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the flags/response_schemas documentation is technically correct but did not make this specific default-composite distinction obvious enough to prevent the mistake even after following the plugin's own INV-115 lookup discipline (call `get_sdk_reference(topic='flags'|'response_schemas')` before parsing).
**Upstream:** submitted 2026-07-29 via submit_feedback (category=bug)

### What happened

Writing a watchlist-screening query program, I called `search_by_attributes(attributes, SzEngineFlags.SZ_SEARCH_BY_ATTRIBUTES_ALL)` and read `entity.get("RECORDS", [])` from each result to determine which data sources an entity belonged to. It came back as an empty list for every result, even for entities known to have 4+ records across 4 sources. The same pattern — calling `find_network_by_entity_id` with its own default flags (`SZ_FIND_NETWORK_DEFAULT_FLAGS`) and reading `RECORDS[]` from the returned entities — produced the same silent empty result.

### Why it matters

Both failures were silent: valid JSON came back, the code ran without error, and the wrong field name simply rendered as an empty list rather than raising. A bootcamper debugging this would very plausibly conclude "my data doesn't have the field I expect" or "the search found nothing useful" rather than "I used the wrong response field name" — exactly the failure mode INV-115 exists to prevent, and it still happened despite explicitly looking up flags and response schemas beforehand.

### Suggested fix

`SZ_SEARCH_BY_ATTRIBUTES_ALL`'s composite_members list (returned by `get_sdk_reference(topic='flags', filter='SZ_SEARCH_BY_ATTRIBUTES_ALL')`) includes `SZ_ENTITY_INCLUDE_RECORD_SUMMARY` but not `SZ_ENTITY_INCLUDE_RECORD_DATA` — same for `SZ_FIND_NETWORK_DEFAULT_FLAGS`. This is discoverable by reading the composite_members array carefully, but the flags/response_schemas tools could make it more prominent: e.g., when a method has its own named default-flags composite that differs from `SZ_ENTITY_DEFAULT_FLAGS`, explicitly flag the fields that are *excluded* by that default (particularly `RECORDS[]` vs `RECORD_SUMMARY[]`), since that is exactly the distinction that renders blank instead of erroring.

### Context when reported

- **Time:** 2026-07-29 14:46 local
- **Plugin version:** 0.5.0
- **Workstation:** Linux 6.17.0-35-generic (x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** query_visualize_discover / step 3 (query programs)
- **Recent questions:** "Based on your business problem, here are the query requirements I've derived. Is there anything you'd like to adjust?"
- **Bootcamper responses:** "Use these as-is"
- **Behind the scenes:** writing `src/query/watchlist_screening.py` and `src/query/corporate_360.py`, following `phase1-query-visualize.md` step 2's flag/response-shape lookup instructions.
- **Observed problem:** `entity.get("RECORD_SUMMARY", [])` reads correctly under those same default flags; `entity.get("RECORDS", [])` reads as an empty list every time, for both `search_by_attributes` and `find_network_by_entity_id`.
- **Expected behavior:** per INV-115, a wrong field name should be caught by the response-schema lookup before the code is trusted — the lookup was done, but the specific default-vs-explicit distinction was easy to miss on first read.
- **Divergence:** the composite_members list technically documents this, but not in a form that jumps out as "this default omits full record data" without cross-referencing each member flag's own response_paths individually.

## Improvement: query code iterating raw source rows must deduplicate by (data_source, record_id) when a source has known duplicate rows

**Date:** 2026-07-29
**Module:** Query, Visualize and Discover
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — `phase1-query-visualize.md`'s find-duplicates query pattern does not warn about this interaction with a Module 5 mapping decision (accepting a source's duplicate rows since `add_record` upserts them by RECORD_ID).
**Upstream:** not applicable

### What happened

Writing an over-matching review query (`find_duplicates.py`) that iterates every row in each source's mapped JSONL file and groups by resolved `ENTITY_ID`, I did not deduplicate `(data_source, record_id)` pairs before counting. OFAC's source data has verified byte-identical duplicate rows (documented at mapping time, in Module 5) — the same RECORD_ID appears multiple times in the file. The query counted each duplicate row as a separate constituent record, inflating two entities' apparent record counts (23 and 15) and falsely flagging both for manual over-matching review. Spot-checking both entities directly via `get_entity_by_entity_id` showed only 2 real records each; `add_record` had correctly upserted the duplicates into one Senzing record all along.

### Why it matters

The false flag would have sent a bootcamper down an "investigate over-matching" path for entities that were never actually over-matched — a wasted review cycle, and in a KYC context, a wrong signal about which entities need analyst attention.

### Suggested fix

When a query program iterates a source's raw/mapped file rows to associate them with resolved entities (rather than reading record identities from Senzing itself), the plugin's query-program guidance could note that a source's mapped file may contain more rows than distinct RECORD_IDs (when the mapping decision was to keep verified duplicate rows rather than pre-deduplicate them), and that per-record analysis code should deduplicate by `(data_source, record_id)` before counting, matching how `add_record`'s own upsert behavior already treats them as one record.

### Context when reported

- **Time:** 2026-07-29 14:46 local
- **Plugin version:** 0.5.0
- **Workstation:** Linux 6.17.0-35-generic (x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** query_visualize_discover / step 3 (query programs)
- **Recent questions:** "Based on your business problem, here are the query requirements I've derived. Is there anything you'd like to adjust?"
- **Bootcamper responses:** "Use these as-is"
- **Behind the scenes:** writing and running `src/query/find_duplicates.py` against all 6 loaded sources.
- **Observed problem:** two entities flagged as containing 23 and 15 records; direct inspection showed 2 real records each.
- **Expected behavior:** the over-matching review should only flag entities that are genuinely large in Senzing's own resolved view.
- **Divergence:** the query counted physical file rows rather than distinct records, and the source's own duplicate-row characteristic (already known from Module 5) was not carried forward into this module's query-writing guidance.

## Improvement: End-of-Module Summary blocks in bootcamp_recap.pdf are not formatted as bulleted lists / left-justified

**Date:** 2026-07-29
**Module:** Graduation
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — `scripts/generate_recap_pdf.py` (bundled with the plugin) renders the PDF; this is not a Senzing MCP server tool or fact.
**Upstream:** not applicable

### What happened

In the rendered `docs/bootcamp_recap.pdf`, within each module's "End-of-Module Summary"
subsection: the "What you accomplished:" and "Files produced:" content should render as
bulleted lists but do not, and the "Why it matters:" text should appear beneath the "Why it
matters:" label, left-justified, but does not.

### Why it matters

The recap PDF is the keepsake deliverable the bootcamper shares with their team — it should be
readable and professionally formatted. This affects every module section in the PDF.

### Suggested fix

Render "What you accomplished:" and "Files produced:" as bulleted lists (one bullet per line
from the source Markdown). Render "Why it matters:" as a label followed by its text on the
line(s) beneath it, left-justified.

### Context when reported

- **Time:** 2026-07-29 15:02 local
- **Plugin version:** 0.5.0
- **Workstation:** Linux 6.17.0-35-generic (x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** graduation / null (graduation complete)
- **Recent questions:** "Is there anything else you would like to explore?"
- **Bootcamper responses:** "No, that's all"
- **Behind the scenes:** graduation's Step 1b PDF render (`generate_recap_pdf.py`) had just completed and been verified for content/image count; the bootcamper then asked "Where is bootcamp_recap.pdf?" and reviewed the rendered PDF.
- **Observed problem:** End-of-Module Summary bullets and "Why it matters:" text are not formatted as described above.
- **Expected behavior:** a professionally designed PDF (per the plugin's own INV-048 requirement) renders list-shaped content as actual bulleted lists and keeps label/text placement consistent and left-justified.
- **Divergence:** the renderer's End-of-Module Summary formatting logic does not currently split "What you accomplished:"/"Files produced:" lines into bullets or place "Why it matters:" text on its own left-justified line(s).

## Improvement: "Why it matters:" in bootcamp_recap.pdf needs a blank line and an indented text block

**Date:** 2026-07-29
**Module:** Graduation
**Priority:** Low
**Source:** bootcamper-reported
**Routing:** plugin — `scripts/generate_recap_pdf.py`, same rendering path just fixed for this label.
**Upstream:** not applicable

### What happened

Follow-up to the prior "Why it matters" fix (label now on its own line, text left-justified at
the margin): the bootcamper asked for a blank line between the "Why it matters:" label and the
text below it, and for the text block itself to be indented rather than flush against the page
margin.

### Why it matters

Refines the same keepsake-readability concern as the earlier fix — spacing and indentation make
the label/text relationship clearer at a glance.

### Suggested fix

After rendering the "Why it matters:" label on its own line, add a small vertical gap before the
text, and indent the text block (consistent with the indent used elsewhere for bulleted content).

### Context when reported

- **Time:** 2026-07-29 15:19 local
- **Plugin version:** 0.5.0
- **Workstation:** Linux 6.17.0-35-generic (x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** graduation / null (graduation complete)
- **Recent questions:** none — sent as a follow-up mid-turn message.
- **Bootcamper responses:** n/a
- **Behind the scenes:** the bootcamper had just reviewed the regenerated `bootcamp_recap.pdf` from the prior fix.
- **Observed problem:** "Why it matters:" text sits directly beneath its label with no gap, flush against the left margin.
- **Expected behavior:** a blank line beneath the label, and the text block indented.
- **Divergence:** the prior fix addressed the hanging-indent/inline-continuation problem but did not add spacing or an indent for the new line-broken layout.

## Improvement: bootcamp_data_discoveries.md content with Cyrillic org names corrupts silently in the PDF

**Date:** 2026-07-29
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** both — `generate_discoveries_pdf.py` uses Latin-1-only core fonts (same class of limitation already known for the recap's certificate name handling), and the content I authored into `bootcamp_data_discoveries.md` put real Cyrillic organization names into a fenced ASCII diagram and prose without checking whether the renderer could display them.
**Upstream:** not applicable

### What happened

The "Relationship networks" section's fenced diagram, and three other spots in the document,
contained literal Cyrillic organization names (e.g. `Акционерное общество "Газпром-Медиа
Холдинг"`) and Unicode box-drawing connectors (`│`, `▼`). Rendered to PDF, these silently
corrupted into garbage characters (`"_ "`, `""`) — valid PDF, no error, exit 0, "content
retained: 100%" — with no indication anything was lost.

### Why it matters

This is real content loss in a keepsake report the bootcamper is meant to share. It reads as
correct at every automated check (exit code, retention percentage) and only shows up on visual
inspection of the rendered page — exactly the class of defect the graduation retrospective step
exists to catch, but this document is produced in Module 7, before that retrospective runs.

### Suggested fix

When authoring content destined for `generate_discoveries_pdf.py` (or `generate_recap_pdf.py`),
prefer each entity's verified Latin-script name/alias (already present in the loaded Senzing
data for organizations from multi-source sanctions/registry data) over its Cyrillic primary
name, especially inside fenced/monospace diagram blocks. Consider having the generator itself
warn on stderr when a block contains characters outside its core font's range, mirroring the
bootcamper-name handling already in `generate_recap_pdf.py` (INV-143).

### Context when reported

- **Time:** 2026-07-29 15:25 local
- **Plugin version:** 0.5.0
- **Workstation:** Linux 6.17.0-35-generic (x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** graduation / null (found while regenerating a Module 7 deliverable during graduation)
- **Recent questions:** "How should I fix the Cyrillic corruption in the Relationship Networks diagram in bootcamp_data_discoveries.pdf?"
- **Bootcamper responses:** "Use the entity's English/Latin name" — verified live against the loaded source records (GLEIF/OFAC/OPEN-SANCTIONS aliases) rather than guessed.
- **Behind the scenes:** regenerating `bootcamp_data_discoveries.pdf` after an unrelated recap-formatting fix; visual verification (pdftoppm raster) caught the corruption that `content retained: 100%` did not.
- **Observed problem:** Cyrillic text and Unicode connectors rendered as garbled ASCII fragments.
- **Expected behavior:** either render the actual characters, transliterate to a verified Latin form, or fail loudly — never drop content silently.
- **Divergence:** the renderer has no fallback-font or warn-on-drop mechanism for non-Latin-1 text in body/code blocks; fixed by rewriting the four affected passages to use each entity's already-verified English name/alias and ASCII-safe diagram connectors (`|`, `v`).

## Improvement: generate_discoveries_pdf.py had the same long-label hanging-indent issue as the recap generator

**Date:** 2026-07-29
**Module:** Query, Visualize and Discover
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — `scripts/generate_discoveries_pdf.py`, the discoveries-PDF sibling of `generate_recap_pdf.py`.
**Upstream:** not applicable

### What happened

While regenerating `bootcamp_data_discoveries.pdf`, the same defect just fixed in the recap
generator (a `**Label:** long paragraph` callout continuing inline after the label, wrapping
with a hanging indent under wherever the label ended) was also present here, on the "Near-miss
(the one that teaches more):" and "Measurement:" callouts.

### Why it matters

Same readability concern as the recap fix, in the sibling generator.

### Suggested fix

Applied the same fix as the recap generator, scoped to an explicit allowlist of long-form
labels (`_NEW_LINE_LABELS`) rather than every `**Label:**` block — a blanket change broke two
existing tests (`test_consecutive_paragraphs_have_a_blank_line_between_them` and
`test_a_soft_wrapped_label_is_not_split_mid_sentence`) because short labels like "Cross-source
overlap:" are meant to stay inline with their wrapped continuation.

### Context when reported

- **Time:** 2026-07-29 15:25 local
- **Plugin version:** 0.5.0
- **Workstation:** Linux 6.17.0-35-generic (x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** graduation / null
- **Recent questions:** n/a — found during the same regeneration pass as the Cyrillic finding above.
- **Bootcamper responses:** n/a
- **Behind the scenes:** visual verification (pdftoppm raster) of the regenerated discoveries PDF.
- **Observed problem:** long labels wrapped with a hanging indent instead of a left-justified paragraph.
- **Expected behavior:** consistent with the just-fixed recap generator's "Why it matters" formatting.
- **Divergence:** the two PDF generators share this rendering pattern but had drifted; fixed in both, with the existing test suite (`tests/test_discoveries_pdf.py`, 34/34) confirmed still passing after the fix.
