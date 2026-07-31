# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp. Every entry is saved here, whatever it turns
out to be about. Entries routed `mcp-server` may **also** have been forwarded to Senzing —
only ever with your explicit yes, and with identifying details stripped; each entry's
`Upstream:` field records what happened.

**Started:** 2026-07-30

## Your Feedback

## Improvement: Detect and capture the bootcamp's own bad or reversed decisions, during the run and at graduation

**Date:** 2026-07-30
**Module:** Query, Visualize and Discover (raised as a general, cross-module request)
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — the request is about the bootcamp's own self-assessment behavior; it would still be absent if the Senzing MCP server were perfect.
**Upstream:** not applicable

### What happened

The bootcamp made several decisions during this run that were wrong and had to be reversed, or
that were caught only just before causing damage. Nothing in the plugin detects, records, or
carries these forward: each was resolved in conversation and would be lost when the session
ends. The bootcamper asked that the bootcamp determine, both **during** the run and again **at
graduation**, whether it made any bad decisions or decisions that needed reversing, and capture
them silently as bootcamp feedback so future bootcamps avoid repeating them.

The decisions from this run that such a mechanism should have captured:

**Reversed after being acted on**

1. **`EFX_YREST` mapped to `REGISTRATION_DATE`.** Equifax's "year business established" was
   mapped onto the same Senzing feature carrying Enformion's `FilingDate` (incorporation filing
   date). The two measure different things - a business commonly trades for years before
   incorporating - so the sources systematically disagreed and Senzing correctly suppressed
   merges over a conflict that was an artifact of the mapping. It appeared on 345 of 2,651
   cross-source comparisons (13.0%). Withdrawing the mapping and reloading raised cross-source
   entities from 826 to 876.
   **Critically: every static quality gate passed while this was wrong, and the data-quality
   score went UP when the bad mapping was added.** Only the match-key audit - reading the
   engine's own output - exposed it.

2. **Three defects in the data-quality scoring implementation.** Person-oriented features were
   averaged across organization records; linkage-only records were scored as though they were
   full profiles; and partial addresses were credited as complete. All three were authored by
   the assistant. Correcting the second one honestly *lowered* the reported score.

**Caught before being acted on**

3. **A proposed `TRUSTED_ID` remap.** Presented as a fix for TRUSTED_ID comparisons scoring
   zero. Checking the Entity Specification first showed that different TRUSTED_ID *types* do
   not interact at all, and the engine's own `SCORE_BEHAVIOR` values confirm it (`A1` for the
   inert different-type case, `A1ES` for the exclusive same-type case that legitimately forces
   entities apart). Implementing the remap would have merged legally distinct entities across
   the whole dataset. No change was made.

**Smaller in-flight corrections**

4. Reused `find_network`'s flags on a `find_path` call: `SZ_FIND_NETWORK_INCLUDE_MATCHING_INFO`
   applies to `find_network` only, and `find_path` returns its edges under `ENTITY_PATH_LINKS[]`
   rather than `ENTITY_NETWORK_LINKS[]`. Result rendered entity names correctly with every edge
   blank - a half-populated row that reads as a real answer.
5. Omitted `SZ_ENTITY_INCLUDE_ENTITY_NAME` from a `why_entities` call:
   `SZ_WHY_ENTITIES_DEFAULT_FLAGS` does not carry it, so both entity names read `null` while
   every other field rendered.
6. Assumed `javax.json` was available to plain `javac`; it is neither in the JDK nor bundled
   with the SDK install.
7. A Java class/file name mismatch (`verify_init.java` containing `VerifyInit`).

### Why it matters

Future bootcamps would avoid repeating the same errors. Items 1 and 3 are the significant
ones: both are entity-resolution *semantics* mistakes - mapping two differently-meaning source
fields onto one feature, and misreading identifier-type interaction - and both are the kind of
error a bootcamper working alone would plausibly make and not catch. Item 1 actively degraded
results (50 real customer matches suppressed) while every automated indicator stayed green.

### Suggested fix

Capture bad and reversed decisions silently as bootcamp feedback, at two points:

- **During the run** - when a decision is reversed, withdrawn, or corrected, append an entry
  automatically rather than resolving it only in conversation.
- **At graduation** - the retrospective already specified in `../graduation/SKILL.md`, which
  reuses this same template with `Source: self-observed (assistant retrospective)`, should
  explicitly sweep for reversed decisions rather than relying on recall.

Two observations from this run that may help scope it:

- **The reliable detection signal was the engine's own output, never a static gate.** All three
  significant errors were found by reading match keys, `SCORE_BEHAVIOR`, or the Entity
  Specification - not by any quality score or linter. A self-check keyed to "did a match-key
  audit finding cause a mapping to be withdrawn?" would have caught item 1 automatically.
- **Items 4 and 5 share one shape** already named in the skills as the half-populated-row trap:
  a correct field name that the flags in force do not populate. They are worth capturing as
  recurring-pattern evidence, since the plugin already warns about the pattern and it still
  occurred twice in one module.

### Context when reported

- **Time:** 2026-07-30 18:47 EDT
- **Plugin version:** 0.5.0
- **Workstation:** macOS 26.5.2 (arm64, Apple Silicon)
- **Model / effort:** claude-opus-5; reasoning-effort level not exposed to the session
- **Context size:** Unknown precisely; the session has passed at least one context-compaction
  boundary, so the full early transcript is no longer in the active window (approximate only)
- **Module / step:** `query_visualize_discover` / `4d`
- **Recent questions:** (1) "What would you like to do next?" at the end of Why Analysis (4b);
  (2) the same at the end of How Analysis (4c); (3) "Would you like to continue to module
  completion now?" after Relationship Networks (4d); (4) "Ready for me to stop the
  visualization server?" (the teardown gate, still pending when feedback was raised);
  (5) "What priority would you give this?" (feedback workflow)
- **Bootcamper responses:** "1" (continue to How Analysis), "1" (continue to Relationship
  Networks), "yes" (continue to module completion), then this feedback submission before
  answering the teardown gate, then "2" (Medium priority)
- **Behind the scenes:** The `UserPromptSubmit` hook fired on the phrase "bootcamp feedback"
  and routed to `bootcamp-onboarding/feedback.md`. Active skill at the time:
  `module-07-query-visualize-discover`, Phase 1, immediately after the Data-discoveries
  deliverable convergence point and the Query Completeness Gate, with the step-3c teardown gate
  presented and awaiting an answer. The visualization server was running on port 8081 (pid
  42917). Discover phase checkpointed `completed` (4a-4d).
- **Observed problem:** No mechanism exists to record that a bootcamp decision was wrong. The
  `EFX_YREST` reversal, the three scoring defects, and the averted `TRUSTED_ID` remap were each
  handled conversationally and documented only incidentally - the `EFX_YREST` reversal survives
  because it was written into a mapper docstring by hand, and the `TRUSTED_ID` decision survives
  only in this session's transcript. Nothing routes any of them to the plugin maintainers.
- **Expected behavior:** `feedback.md` Step 3 already supports a `Source:` value of
  `self-observed (assistant retrospective)` specifically so the assistant's own stumbles can be
  filed and distinguished from bootcamper friction, and `../graduation/SKILL.md` is named as the
  place that does it. The bootcamper's expectation - that reversed decisions are captured
  silently, during the run as well as at graduation - is consistent with that design.
- **Divergence:** The mechanism is specified for graduation only, and this bootcamp had not yet
  reached graduation, so nothing had been captured at the time of the report. There is no
  in-run trigger: no gate, hook, or checkpoint fires when a decision is reversed mid-bootcamp,
  so the record depends entirely on the assistant remembering to write it down later - across a
  session that had already crossed a compaction boundary.

## Improvement: find_path returns ENTITY_PATH_LINKS where find_network returns ENTITY_NETWORK_LINKS - the divergence is unwarned

**Date:** 2026-07-31
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin - the MCP server documents both shapes correctly; the skill's graph-method guidance warns about one trap between these two adjacent methods and not this one.
**Upstream:** not applicable

### What happened

`phase2b-discover.md` step 4d introduces `find_network` and `find_path` together and carries a
detailed, hard-won warning about `find_network`'s link endpoints being `MIN_ENTITY_ID` /
`MAX_ENTITY_ID` rather than `ENTITY_ID` / `RELATED_ENTITY_ID`. Having absorbed that warning and
verified the endpoint names with a raw dump, I carried the same flags and the same parser
straight across to `find_path`. Two things were wrong:

- `SZ_FIND_NETWORK_INCLUDE_MATCHING_INFO` has `applies_to: [find_network_*]` only; `find_path`
  needs `SZ_FIND_PATH_DEFAULT_FLAGS` / `SZ_FIND_PATH_INCLUDE_MATCHING_INFO`.
- `find_path` returns its edges under **`ENTITY_PATH_LINKS[]`**, not `ENTITY_NETWORK_LINKS[]`.

The result was the exact failure mode the skill's own "half-populated row" rule describes: the
three path entities rendered with correct names and every edge printed
`(link detail not returned)`. Nothing raised. It reads as "this path has no relationship detail",
not as "wrong flags and wrong array name".

To be fair to the plugin: step 4d does say to look up `get_sdk_reference(topic='flags',
filter='find_path')` separately, and I did not do that before writing the call - I reused what I
had just looked up for `find_network`. The instruction existed; the specific trap did not.

### Why it matters

The two methods are taught side by side, in one step, minutes apart, and share both an endpoint
key shape and a conceptual purpose. That adjacency is precisely what makes the divergence easy to
miss - the closer two APIs look, the more confidently a reader carries code between them. A
bootcamper who hits this sees an empty relationship path and has no reason to suspect the array
name, because the entity names rendered fine.

### Suggested fix

Add one line to step 4d's existing endpoint-key warning, alongside the `MIN_ENTITY_ID` /
`MAX_ENTITY_ID` note it already carries: `find_network` returns `ENTITY_NETWORK_LINKS[]` and
`find_path` returns `ENTITY_PATH_LINKS[]`, and their matching-info flags are not
interchangeable - so neither the flags nor the parser can be shared between the two calls.

### Context when reported

- **Time:** 2026-07-31 (graduation retrospective; the friction occurred 2026-07-30)
- **Plugin version:** 0.5.0
- **Workstation:** macOS 26.5.2 (arm64, Apple Silicon)
- **Model / effort:** claude-opus-5; reasoning-effort level not exposed to the session
- **Context size:** Unknown precisely; the session has passed at least one compaction boundary
- **Module / step:** `query_visualize_discover` / `4d`
- **Recent questions:** N/A - self-observed, not prompted by a question
- **Bootcamper responses:** N/A
- **Behind the scenes:** Writing `src/query/RelationshipNetwork.java`'s `path` subcommand, having
  just written and verified its `net` subcommand against `find_network`.
- **Observed problem:** `find_path` returned a valid 2-degree path whose every edge printed
  `(link detail not returned)`.
- **Expected behavior:** Per `phase1-query-visualize.md`'s defensive-parsing rule, a blank field
  should be diagnosed as wrong-name / wrong-flags / genuinely-absent before being reported.
- **Divergence:** Both wrong-name *and* wrong-flags applied simultaneously, and the skill's
  detailed warning for this pair covers a different trap, so the reused code looked pre-validated.

## Improvement: get_sdk_reference returns SZ_WHY_ENTITIES_DEFAULT_FLAGS with no composite_members, so the plugin's own default-flags procedure cannot be run for it

**Date:** 2026-07-31
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** both - the MCP server omits the composite's membership, and the plugin's default-flags rule instructs reading a `composite_members` list that, for this flag, is not returned.
**Upstream:** submitted 2026-07-31

### What happened

`phase1-query-visualize.md` carries an explicit rule: "Before parsing an entity field out of a
response, read the composite's `composite_members` and confirm the flag that populates *that*
field is in it," with a table covering `SZ_SEARCH_BY_ATTRIBUTES_ALL`,
`SZ_FIND_NETWORK_DEFAULT_FLAGS` and `SZ_ENTITY_DEFAULT_FLAGS`.

Calling `why_entities` with `SZ_WHY_ENTITIES_DEFAULT_FLAGS | SZ_INCLUDE_FEATURE_SCORES |
SZ_INCLUDE_MATCH_KEY_DETAILS` returned both entity names as `null` while every other field -
match level, why key, ER rule, all feature scores and buckets, CONFIRMATIONS and DENIALS -
rendered correctly. Adding `SZ_ENTITY_INCLUDE_ENTITY_NAME` explicitly fixed it.

Checking afterwards, `get_sdk_reference(topic='flags', filter='SZ_WHY_ENTITIES_DEFAULT_FLAGS',
language='java')` returns that flag with **no `composite_members` key and no `response_paths`** -
only a one-line description, "Replaces `G2_WHY_ENTITY_DEFAULT_FLAGS`, focused on the
`whyEntities*` functions", sourced from the V3-to-V4 breaking-changes document. Every sibling
composite in the same response - `SZ_ENTITY_DEFAULT_FLAGS`, `SZ_ENTITY_CORE_FLAGS`,
`SZ_ENTITY_INCLUDE_ALL_RELATIONS` - carries a full `composite_members` list, as do
`SZ_FIND_PATH_DEFAULT_FLAGS`, `SZ_FIND_NETWORK_DEFAULT_FLAGS` and
`SZ_HOW_ENTITY_DEFAULT_FLAGS`. The gap is specific to the `why_*` default composites.

### Why it matters

The plugin's rule is the right rule, and it is unrunnable here: there is no membership list to
check, so the only way to discover that this composite omits `SZ_ENTITY_INCLUDE_ENTITY_NAME` is
to call it, notice the nulls, and guess. That inverts the whole point of the lookup-before-parse
discipline (INV-115) - the reference is supposed to prevent the empirical discovery, not require
it.

It is also the more deceptive shape of the half-populated-row failure: the *analytical* content
of a why_entities response is complete and correct, and only the human-readable labels are
missing, so the output looks like an unnamed-data problem rather than a flags problem.

### Suggested fix

- **Upstream:** populate `composite_members` (and `response_paths`) for
  `SZ_WHY_ENTITIES_DEFAULT_FLAGS` and its `why_records` / `why_record_in_entity` siblings, as is
  already done for the entity, find-path, find-network and how-entity composites.
- **Plugin:** add a row to the default-flags table in `phase1-query-visualize.md` -
  `SZ_WHY_ENTITIES_DEFAULT_FLAGS` does not carry `SZ_ENTITY_INCLUDE_ENTITY_NAME`, so
  `ENTITY_NAME` reads null - and note that when a composite is returned *without* a
  `composite_members` list, the procedure cannot be run and the sub-flags must be OR-ed in
  explicitly rather than assumed.

### Context when reported

- **Time:** 2026-07-31 (graduation retrospective; the friction occurred 2026-07-30)
- **Plugin version:** 0.5.0
- **Workstation:** macOS 26.5.2 (arm64, Apple Silicon)
- **Model / effort:** claude-opus-5; reasoning-effort level not exposed to the session
- **Context size:** Unknown precisely; the session has passed at least one compaction boundary
- **Module / step:** `query_visualize_discover` / `4d` (near-miss worked example for the
  data-discoveries deliverable)
- **Recent questions:** N/A - self-observed, not prompted by a question
- **Bootcamper responses:** N/A
- **Behind the scenes:** Running `src/query/WhyEntities.java` against a POSSIBLY_SAME pair to
  produce the near-miss example required by the data-discoveries deliverable.
- **Observed problem:** Both entity names printed as `null`; all other fields correct.
- **Expected behavior:** The composite's `composite_members` should reveal whether
  `SZ_ENTITY_INCLUDE_ENTITY_NAME` is included, before any parsing code is written.
- **Divergence:** The MCP reference returns no membership for this composite, so the check the
  plugin prescribes has nothing to read.

## Improvement: graduation's PDF-verification guidance assumes poppler is present on macOS; on a stock macOS machine none of it is

**Date:** 2026-07-31
**Module:** Graduation
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** plugin - the platform expectation is stated in the graduation skill's own verification section.
**Upstream:** not applicable

### What happened

`graduation/SKILL.md` Step 1b says, of the PDF-verification toolchain: "**Linux / macOS:** poppler
is usually present (`pdftoppm` / `pdftotext` / `pdfinfo` / `pdfimages`), so the full check set
normally runs," and reserves the missing-poppler case for Windows ("Windows: poppler is typically
absent").

On this machine - macOS 26.5.2 on Apple Silicon, with Homebrew installed and in active use for
the Senzing SDK itself - **all four poppler binaries are absent**, and poppler is not installed
as a Homebrew formula. macOS ships none of them; they arrive only via an explicit
`brew install poppler`, which a bootcamper has no reason to have run.

That removes exactly the two checks the skill itself identifies as irreplaceable: the page raster
(the only check that catches border-clipped glyphs) and `pdftotext` (the only check that catches
content positioned outside the page box). Both were unavailable, and the skill's own priority
guidance for a reduced check set - "keep the positive `pdftotext` content probe" - is not
actionable here either, because `pdftotext` is one of the missing four.

### Why it matters

The guidance sets the expectation that macOS gets the full check set, so an agent following it
may report the keepsake as verified having silently run fewer checks than it thinks it did -
which is the precise overstatement the same section forbids ("Say what you could not verify").
Since the skill correctly rules out installing a tool to satisfy a verification step (INV-129),
macOS needs the same reduced-check-set treatment Windows already gets, rather than being grouped
with Linux.

### Suggested fix

Reword the platform note so macOS is not grouped with Linux for poppler availability: on macOS
poppler is **not** part of the base system and is present only if the user installed it
explicitly, so the missing-poppler path is the expected case on both macOS and Windows. Then say
what remains available on macOS: `fpdf2` brings in Pillow, so the image count via Pillow works,
and the generator's own `embedded N of M images` line needs no tool at all.

### Context when reported

- **Time:** 2026-07-31
- **Plugin version:** 0.5.0
- **Workstation:** macOS 26.5.2 (arm64, Apple Silicon), Homebrew present
- **Model / effort:** claude-opus-5; reasoning-effort level not exposed to the session
- **Context size:** Unknown precisely; the session has passed at least one compaction boundary
- **Module / step:** `graduation` / Step 1b pre-check
- **Recent questions:** N/A - self-observed
- **Bootcamper responses:** N/A
- **Behind the scenes:** Probing the verification toolchain before rendering the recap PDF.
- **Observed problem:** `pdftoppm`, `pdftotext`, `pdfimages` and `pdfinfo` all absent; `fpdf2`
  2.8.4 present.
- **Expected behavior:** Per the skill, macOS should normally run the full check set.
- **Divergence:** poppler is not part of macOS and was not installed; the skill's platform note
  treats its absence as a Windows-specific case.

## Improvement: nothing ever creates docs/progress/recap_checkpoint.md, though two documents describe maintaining and clearing it

**Date:** 2026-07-31
**Module:** General (cross-module)
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** plugin - the in-progress checkpoint is referenced by ground-rules and by module completion, but no step instructs creating or updating it.
**Upstream:** not applicable

### What happened

`module-completion.md` Step 2d opens "During the module you kept an in-progress recap at
`docs/progress/recap_checkpoint.md`", and `graduation/SKILL.md` Step 1a describes folding a
leftover checkpoint into its module section. Both are written as though the file routinely
exists.

Across all ten completed modules of this run it was never created, and `docs/progress/` does not
exist. No step in any module skill says to write or update it - it is only ever referenced as
something to clear or fold in - so the clean-up half of the contract is specified and the
maintenance half is not. Nothing failed as a result, because the finalized `## {Module name}`
sections were appended at each module's close as designed.

### Why it matters

Low impact while sessions complete normally, which is why it went unnoticed for ten modules. It
matters for the case it was designed for: a module interrupted mid-way. Graduation's recovery
path for that case reads the checkpoint, and the checkpoint will not be there, so the narrative
it was meant to preserve is lost exactly when the safety net is needed. It is also the kind of
gap that reads as an assistant omission during review when it is actually an unspecified step.

### Suggested fix

Either specify where the checkpoint is written - a line in `ground-rules.md` naming the point in
each module at which it is updated - or drop the references from `module-completion.md` Step 2d
and `graduation/SKILL.md` Step 1a and rely on the append-at-close design that is already working.
Keeping the clean-up instructions for a file nothing creates is the state most likely to mislead
a future reader.

### Context when reported

- **Time:** 2026-07-31
- **Plugin version:** 0.5.0
- **Workstation:** macOS 26.5.2 (arm64, Apple Silicon)
- **Model / effort:** claude-opus-5; reasoning-effort level not exposed to the session
- **Context size:** Unknown precisely; the session has passed at least one compaction boundary
- **Module / step:** `graduation` / Step 1a (noticed while checking for a leftover checkpoint)
- **Recent questions:** N/A - self-observed
- **Bootcamper responses:** N/A
- **Behind the scenes:** Graduation Step 1a checks for a leftover
  `docs/progress/recap_checkpoint.md` to fold into a module section.
- **Observed problem:** `docs/progress/` does not exist and never did during this run.
- **Expected behavior:** Two skills describe the file as routinely maintained during a module.
- **Divergence:** No skill step instructs creating or updating it; only clearing and folding it in
  are specified.

## Improvement: nothing verifies that every visualization tab reached the recap PDF - the "embedded N of M images" metric is self-referential

**Date:** 2026-07-31
**Module:** Graduation (mechanism spans Truth Set visualization, Query/Visualize/Discover, and Module completion)
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin - the capture helper, the recap generator, its `--check` mode, and the module-completion embed step are all plugin-bundled; no Senzing MCP tool is involved.
**Upstream:** not applicable

### What happened

The bootcamper reported that `docs/bootcamp_recap.pdf` did not appear to contain visualizations
of all tabs for the Truth Set visualization or Query, Visualize and Discover sections, and asked
what guarantees the tab images reach the PDF.

Two findings, and they are separate.

**On this particular PDF, the images were all present.** Verified four ways rather than by the
generator's success line: 12 image XObjects at 1440x900; 12 distinct SHA-1 hashes (no repeated
tab); 12 `Do` paint operations, each exactly once, so every one is drawn and not merely embedded;
and all 12 placed inside the A4 page box (tallest top edge 813.5 of 841.89 pt). Six per section,
in app tab order. The likely source of the impression is layout rather than absence - images
render two per page at ~368 pt wide, so they land on their own pages shortly after each
section's Actions Taken bullets rather than inline between them.

**On the guarantee, the bootcamper is right and there is a real hole.** No step in the pipeline
ever compares the number of tabs captured against the number of tabs the app actually has:

1. Screenshot capture is best-effort and non-blocking by contract (INV-122). A tab that fails to
   capture is reported on stderr and everything downstream proceeds.
2. `generate_recap_pdf.py --check` validates that each `![](...)` reference resolves to a file on
   disk. It cannot know how many tabs existed.
3. The success line `embedded N of M images` is **self-referential**. In
   `scripts/generate_recap_pdf.py` line 720 it is built as
   `f"embedded {embedded} of {referenced} images"`, where `referenced` counts the image links
   present in `docs/bootcamp_recap.md`. If only four of six tabs were ever captured and embedded,
   the line reads `embedded 4 of 4 images` - a perfect score against an incomplete set.

Graduation Step 1a does add a check for "a visualization-producing module with no image", but it
triggers only at **zero** images in a section. A section with 4 of 6 passes every check in the
chain.

I also over-trusted that metric when reporting to the bootcamper: I cited `embedded 12 of 12` as
evidence the screenshots were complete, when by construction it could not have detected the
failure being described. It was correct here by luck of the input, not by measurement.

### Why it matters

The recap PDF is the keepsake - the artifact the bootcamper keeps and is explicitly encouraged
to share with their team. A silently incomplete one misrepresents both the work done and the
app's breadth, and this is exactly the failure class the plugin already has scar tissue for: the
skill notes a prior run whose recap "showed the same three tabs in both visualization sections
and the app looked narrower than it was".

The deeper issue is that the one number an agent naturally reaches for to confirm completeness
is structurally incapable of detecting incompleteness. That makes it worse than having no metric,
because it produces confident, wrong reassurance - which is precisely what happened in this
session.

### Suggested fix

Give the count an **external** denominator - the number of tabs the app actually rendered, not
the number of links the Markdown happens to contain:

- Have `capture_screenshots.py` write a small sidecar manifest next to the PNGs (e.g.
  `<name>-tabs.json`: tabs requested, tabs captured, tabs that produced nothing and why).
- Have `generate_recap_pdf.py --check` read that manifest and fail the check when a section
  embeds fewer images than its manifest recorded as captured, naming the missing tab slugs.
- Change the success line to report against the manifest when one exists, e.g.
  `embedded 12 of 12 images (12 of 12 captured tabs)`, so the denominator is not derived from
  the same file being measured.
- Extend Graduation Step 1a's zero-image check to a **count** check: compare each visualization
  section's embedded images against the PNGs on disk carrying that visualization's `<name>-`
  prefix, and warn on any shortfall rather than only on zero.
- In the interim, add a line to Step 1b's verification guidance stating plainly that
  `embedded N of M` measures Markdown references, not tab coverage, so it must not be cited as
  evidence of completeness.

### Context when reported

- **Time:** 2026-07-31 09:05 EDT
- **Plugin version:** 0.5.0
- **Workstation:** macOS 26.5.2 (arm64, Apple Silicon)
- **Model / effort:** claude-opus-5; reasoning-effort level not exposed to the session
- **Context size:** Unknown precisely; the session has passed at least one compaction boundary
- **Module / step:** `graduation` / `current_step: null` (9 modules completed; graduation past
  its closing announcement, awaiting the final "anything else to explore" reply)
- **Recent questions:** (1) "Ready for me to stop the visualization server?"; (2) "Would you
  like to graduate now and generate your production project and recap?"; (3) "This looks like an
  issue in the Senzing MCP server rather than the bootcamp. Send the report above to Senzing?";
  (4) "What name would you like printed on your Certificate of Completion?"; (5) "Is there
  anything else you would like to explore?"
- **Bootcamper responses:** "yes"; "yes"; "1" (send upstream); "Michael Dockter"; then this
  feedback submission in place of answering the closing question; then "2" (Medium priority)
- **Behind the scenes:** Graduation's mandatory closing step had already run. The recap PDF was
  rendered once by `generate_recap_pdf.py` (fpdf2 renderer, 99% content retention,
  `embedded 12 of 12 images`), and `--check --expect-modules` had passed.
- **Observed problem:** The bootcamper did not see all tab visualizations for the two
  visualization sections in the PDF.
- **Expected behavior:** Per INV-122/INV-146, capture is one image per tab and every captured
  image must be embedded, with graduation backfilling any that were missed - so the keepsake
  should show every tab of every visualization app.
- **Divergence:** The images were in fact all present and painted in this PDF, so the immediate
  report is a layout/discoverability issue rather than missing content. The underlying concern
  is valid and unaddressed: no check in the chain compares captured tabs to the app's tab count,
  and the metric that appears to do so counts the Markdown's own references.

## Improvement: recap PDF bullet lists need inter-item spacing everywhere - "Files produced" and "Questions & Responses" are excluded and run together

**Date:** 2026-07-31
**Priority:** Medium
**Module:** Graduation (affects every module's recap section)
**Source:** bootcamper-reported
**Routing:** plugin - `scripts/generate_recap_pdf.py` is bundled with the bootcamp plugin; no Senzing MCP tool is involved.
**Upstream:** not applicable

### What happened

The bootcamper asked that bulleted lists in `docs/bootcamp_recap.pdf` carry a blank line between
each list element, so a reader can tell one bullet from the next.

The generator already implements exactly this, and applies it to only three of the five bullet
lists in a module section. `scripts/generate_recap_pdf.py` defines `_ITEM_GAP_MM = 2.4` and emits
it after a bullet when the next content-bearing line is also a bullet - but only for
`_SPACED_SUBSECTIONS = ("information shared", "actions taken")` and
`_SPACED_LABELS = ("what you accomplished",)`.

Two lists are deliberately excluded, with the reasons stated in the source:

- **"Files produced"** - excluded as "a short reference list of paths".
- **"Questions & Responses"** - excluded because "its responses are indented sub-bullets under
  their questions; spacing every bullet would separate each answer from its question and read
  worse, not better."

The first rationale does not hold against real recap content. Because
`../bootcamp-onboarding/module-completion.md` requires each entry to be a path **plus a short
"- what it is" gloss**, "Files produced" is neither short nor one line per item. Measured in this
run's recap:

| Section | Items | Longest item | Items likely to wrap |
|---|---|---|---|
| Truth Set visualization | 12 | 110 chars | ~2 |
| Query, Visualize and Discover | 11 | 188 chars | ~4 |
| Data Quality, Mapping, and Transformation | 8 | 147 chars | ~4 |
| Data processing | 8 | 121 chars | ~3 |
| Data collection | 5 | 145 chars | ~4 |

The generator's own comment explains why this matters: "a bullet ends with a `multi_cell` at line
height 5.5 and no trailing gap, so the space between two separate items equals the space between
a wrapped item's own lines, and multi-line items run together." That is the exact condition
present in "Files produced" in seven of nine sections - and the one list where the fix is
switched off.

The "Questions & Responses" rationale is sound as far as it goes: spacing the `- **R:**`
sub-bullets would push each answer away from its question. But it argues only against spacing
*sub*-bullets, not against spacing the top-level `- **Q:**` items. Those blocks run 4 to 14 lines
per section and currently have no visual separation between one question-and-answer pair and the
next.

### Why it matters

The recap PDF is the keepsake the bootcamper keeps and shares. "Files produced" is also one of
its most *referenced* lists - it is the index a reader uses to find what the bootcamp actually
built - so it is the worst list to render as an undifferentiated block. A reader scanning eleven
wrapped paths cannot tell where one entry ends and the next begins.

The fix is already written, tested and in use three lines away; this is a matter of extending its
scope, not building anything.

### Suggested fix

- Add `"files produced"` to `_SPACED_LABELS`. This is a one-token change and reuses the existing
  `_ITEM_GAP_MM` machinery and its "never after the last item" behavior.
- For "Questions & Responses", space **top-level bullets only** - apply the gap when the current
  line is a top-level `- ` bullet and the next content-bearing line is also top-level, leaving
  indented `- **R:**` sub-bullets tight against their question. This satisfies the bootcamper's
  request without the regression the original exclusion was guarding against.
- Update the "Deliberately NOT spaced" comment block so it reflects the new behavior, and correct
  the "short reference list of paths" characterization - with the required "- what it is" gloss,
  these lists routinely run 8-12 wrapped items.
- Consider making the default "space every bullet list" with an explicit opt-out, rather than an
  opt-in list of three names: the current shape means any list added later is unspaced by
  default, which is how this one was missed.

### Context when reported

- **Time:** 2026-07-31 09:21 EDT
- **Plugin version:** 0.5.0
- **Workstation:** macOS 26.5.2 (arm64, Apple Silicon)
- **Model / effort:** claude-opus-5; reasoning-effort level not exposed to the session
- **Context size:** Unknown precisely; the session has passed at least one compaction boundary
- **Module / step:** `graduation` / `current_step: null` (9 modules completed; graduation past
  its closing announcement, awaiting the final "anything else to explore" reply)
- **Recent questions:** (1) "Is there anything else you would like to explore?"; (2) "What
  priority would you give this?" for the preceding screenshot-guarantee entry; (3) "What priority
  would you give this?" for this entry
- **Bootcamper responses:** the screenshot-coverage feedback in place of answering the closing
  question; "2" (Medium); then this feedback; then "2" (Medium)
- **Behind the scenes:** The recap PDF had already been rendered once by
  `generate_recap_pdf.py` (fpdf2 renderer, 99% retention, 12 of 12 images) during graduation
  Step 1b, and `--check --expect-modules` had passed. No re-render has been made for this issue.
- **Observed problem:** Bulleted lists in the PDF have no visual separation between items.
- **Expected behavior:** Each bullet reads as a distinct item; the generator already provides
  inter-item spacing for this purpose.
- **Divergence:** The spacing is opt-in per subsection/label and covers only three of the five
  bullet lists. "Files produced" was excluded on the assumption that it is a short list of bare
  paths, but the recap template requires a descriptive gloss per entry, so its items wrap and
  run together - the precise failure the spacing feature exists to prevent.

## Improvement: graduation should render business_problem.md and data_source_evaluation.md as styled PDFs - the renderer already can, but a hardcoded section list refuses them

**Date:** 2026-07-31
**Priority:** Medium
**Module:** Graduation
**Source:** bootcamper-reported
**Routing:** plugin - `scripts/generate_discoveries_pdf.py` and the graduation skill are both bundled with the bootcamp plugin; no Senzing MCP tool is involved.
**Upstream:** not applicable

### What happened

The bootcamper asked that the graduation module also produce PDFs of `docs/business_problem.md`
and `docs/data_source_evaluation.md`, styled to match `docs/bootcamp_data_discoveries.pdf` and
`docs/bootcamp_recap.pdf`.

Graduation currently renders exactly two PDFs: the recap (Step 1b, via
`generate_recap_pdf.py`) and, earlier in Module 7, the data-discoveries document (via
`generate_discoveries_pdf.py`). Every other document the bootcamp produces stays Markdown-only.

**The renderer is already general-purpose.** `generate_discoveries_pdf.py` accepts `--input` and
`--output`, and its layout engine - cover page, section styling, tables, typography - contains
nothing specific to the discoveries document.

**One hardcoded content guard blocks it.** `REQUIRED_SECTIONS` (module level, near line 142) lists
the six discoveries headings, and `audit_discoveries` treats "none of these headings present" as
fatal. Tested directly, both documents are refused:

```text
Refusing to render docs/business_problem.md: none of the required findings sections
is present (looked for: headline numbers, merges and match keys, review queue,
why and how, relationship networks, what was not found)
No PDF was written. Fix the document and re-run - an empty deliverable is worse than none.
```

The same refusal occurs for `docs/data_source_evaluation.md`. The CLI exposes only `--input`,
`--output` and `--check`, so the guard cannot be relaxed from outside the script.

The guard itself is sound and worth keeping - it is what stops the script being pointed at an
unrelated Markdown file and silently emitting a near-empty PDF (INV-110). The problem is that it
is expressed as one document's section names rather than as a parameter, which makes a renderer
that is otherwise fully generic usable for exactly one file.

### Why it matters

These two documents are among the most shareable the bootcamp produces, and both currently leave
it as Markdown only:

- `business_problem.md` is the document a stakeholder is most likely to be shown - the problem
  statement, data sources, matching criteria, success criteria and deployment target on one page.
- `data_source_evaluation.md` carries the engine-verified readiness findings, the two scoring
  defects that were found and corrected, and the definitive unmapped-field audit with its
  rejected-field rationale. That audit is the reference a team returns to when someone asks "why
  wasn't field X mapped?".

The bootcamp already treats "render it as a styled PDF" as the signal that a document is a
keepsake rather than a working file. Applying that to two documents that qualify costs one
argument change and one skill step, and the styling work is already done.

### Suggested fix

- Make the required-section list a parameter rather than a constant: add
  `--require-sections "a;b;c"` (semicolon-separated, since section names contain commas) and/or
  `--no-section-check`, defaulting to the current `REQUIRED_SECTIONS` so the discoveries call is
  unchanged. Keep every other guard - the 60% content-retention floor is the real protection
  against rendering the wrong file, and both documents score ~99% against it.
- Consider renaming the script to reflect what it actually is - a general styled-Markdown-to-PDF
  renderer - or add a thin `generate_document_pdf.py` wrapper, so the next person looking for
  "how do I render a doc in the house style" finds it.
- Add a graduation step, after Step 5a and before the revisit bundle, that renders
  `docs/business_problem.pdf` and `docs/data_source_evaluation.pdf`, verifies each by extracting
  text as Step 1b requires, and announces them in the closing summary. Non-blocking like every
  other graduation step: warn and continue if either fails.
- Both documents already pass the Latin-1 constraint the PDF fonts impose, so no character
  handling is needed for them - but the new step should keep the same em-dash caution the
  discoveries deliverable carries, since a future document may not.

### Context when reported

- **Time:** 2026-07-31 09:26 EDT
- **Plugin version:** 0.5.0
- **Workstation:** macOS 26.5.2 (arm64, Apple Silicon)
- **Model / effort:** claude-opus-5; reasoning-effort level not exposed to the session
- **Context size:** Unknown precisely; the session has passed at least one compaction boundary
- **Module / step:** `graduation` / `current_step: null` (9 modules completed; graduation past
  its closing announcement, awaiting the final "anything else to explore" reply)
- **Recent questions:** (1) "Is there anything else you would like to explore?"; (2) "What
  priority would you give this?" for the bullet-spacing entry; (3) "What priority would you give
  this?" for this entry
- **Bootcamper responses:** bullet-spacing feedback, "2" (Medium); then this feedback, "2" (Medium)
- **Behind the scenes:** Graduation had completed all steps through the closing announcement.
  Two PDFs existed: `docs/bootcamp_recap.pdf` and `docs/bootcamp_data_discoveries.pdf`. Test
  invocations of `generate_discoveries_pdf.py --input docs/business_problem.md` and
  `--input docs/data_source_evaluation.md` were run against a scratch output directory; both were
  refused and wrote no file.
- **Observed problem:** Graduation produces no PDF for `business_problem.md` or
  `data_source_evaluation.md`, and the existing styled renderer refuses both.
- **Expected behavior:** The bootcamper expects the documents that summarize the problem and the
  data-source findings to be shareable artifacts in the same visual style as the other two PDFs.
- **Divergence:** The renderer is generic apart from a module-level constant listing one
  document's section headings, which `audit_discoveries` treats as fatal when absent, and which no
  CLI flag can override. Graduation has no step that renders any document other than the recap.
