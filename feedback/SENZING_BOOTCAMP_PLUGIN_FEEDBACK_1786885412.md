# Senzing Bootcamp Plugin Feedback

## 2026-08-15 — Data collection: dataset sized against an assumed limit before measuring the real one

**Source:** self-observed (assistant retrospective)
**Plugin version:** 0.5.1
**Module:** Data collection

**What happened.** While generating the synthetic Meridian Retail Co. sources, I sized the dataset
down from 538 to 466 records specifically to stay under the 500-record built-in evaluation limit,
reasoning that an absent `license_record_limit` meant no custom license was configured. I then
reached Step 8a, followed its instruction to *measure* the limit rather than assume it, and found
the workstation carries a custom EVAL license with `recordLimit: 0` — no record cap at all.

**The decision that was withdrawn.** The downsizing was unnecessary. Had I measured first, the
dataset could have been any size the scenario called for.

**Why it is worth recording.** This is exactly the failure mode INV-244 describes — treating an
absent `license_record_limit` as "no custom license" rather than "never measured" — and I walked
into it despite the module stating the rule, because the sizing decision happens in Step 2 (data
generation) while the measurement instruction lives in Step 8a, six steps later. The ordering makes
the mistake natural: by the time you are told to measure, you have already sized the data.

**Suggestion.** Consider surfacing the measure-the-license instruction *before* the generation
branch in Step 2, or having Step 2's synthesized path read `license_record_limit` and measure it if
absent, so a generated scenario is sized against the real capacity rather than the default.

**Impact here:** none to the bootcamper's outcome — 466 records with 60 three-way and 93 two-way
cross-source overlaps is ample for the Customer 360 scenario. Recorded so it is not rediscovered.

## 2026-08-15 — Data Quality/Mapping: planned to parse single-field names; the Entity Specification forbids it

**Source:** self-observed (assistant retrospective)
**Plugin version:** 0.5.1
**Module:** Data Quality, Mapping, and Transformation (Phase 1, Step 4)

**The decision that was withdrawn.** In Data collection I recorded, in both
`config/data_sources.yaml` and `docs/data_source_locations.md`, that the CRM's `full_name` field
"needs splitting into NAME_FIRST / NAME_LAST" and that the loyalty file's `member_name` in
`"Last, First"` form needs "a different split". Reading the Entity Specification's NAME feature at
Step 4 reversed both:

> "Use parsed person names (NAME_FIRST/NAME_LAST/...) only when the source provides separate
> fields; do NOT attempt to parse a single name field—use NAME_FULL for single-field names (even if
> they appear parseable, like "Smith, Robert")."

The specification names the `"Smith, Robert"` shape explicitly — the exact form the loyalty source
uses. Both fields map to `NAME_FULL`; neither is split.

**Why it is worth recording.** This is the cheap kind of reversal — it happened before any mapper
was written, so nothing had to be undone in code. But the wrong plan had already been committed to
two documents a module earlier, where it read as settled fact. Splitting the names would have
produced a mapping that loads and validates cleanly while degrading resolution quality silently,
which is precisely the class of fault the module warns a quality score cannot detect.

**Corrected:** the `structural_complexity` notes for MERIDIAN_CRM and MERIDIAN_LOYALTY in
`config/data_sources.yaml`, and `docs/data_source_locations.md`.

**Observation for the plugin.** Data collection asks the guide to describe each generated source's
"mapping complexity" while the Entity Specification is not fetched until Module 5 Step 3. Describing
transformations before reading the rules that govern them invites exactly this. Consider having the
synthesized-generation branch describe *shape differences* only, and leave the "what it maps to"
claim to Module 5.

## 2026-08-15 23:52 EDT — Two consecutive self-answered confirmations in Data processing Phase C

**Source:** bootcamper
**Priority:** Medium
**Routing:** plugin — Phase C steps 13 and 15 each pin their own confirm-style question on the
generated-scenario path. Neither depends on the Senzing MCP server, and neither involves the Claude
interface; a perfect MCP server would not change this. The behaviour is exactly what the skill files
prescribe, so it is a design issue in the plugin rather than a deviation from it.

### Context

- **Plugin version:** 0.5.1
- **Workstation:** Linux 7.0.0-28-generic, x86_64, 16 CPUs
- **Model / effort:** Opus 5, high effort
- **Context size:** approximately 45k tokens of a 15M-token budget consumed at the time of report (approximate)
- **Module / step:** `data_processing`, Phase C (step 15 pending); `current_step` recorded as 1
- **Completed modules:** entity_resolution_concepts, business_problem, sdk_setup,
  system_verification, truthset_visualization, data_collection, data_quality_mapping
- **Behind the scenes:** `UserPromptSubmit` feedback hook fired. Active skill
  `module-06-data-processing`, `phaseC-multi-source.md`. Both questions come from that phase's
  provenance branch, which fires because all three sources are `provenance: synthesized` and
  `docs/business_problem.md` carries the `> 🤖 Bootcamp-generated business case` marker.

### Recent questions and responses

1. 👉 "The generated sources have no load-order dependencies — shall I proceed with none?" -> yes
2. 👉 "I recommend the Sequential loading strategy for this generated dataset — shall I use it?" -> (interrupted by this feedback)

### Observed problem

Two consecutive yes/no questions, each of which states its own answer before asking. On the
generated-scenario path the plugin has already established both facts from provenance — that
agent-selected sources have no load-order dependencies, and that Sequential is right for a small
generated dataset — so each question is a rubber stamp. The bootcamper's words: "it slows the flow
with pointless confirmations."

### Expected behavior

`ground-rules.md` (INV-012) says output the bootcamper cannot act on should be suppressed, and
warns elsewhere against confirmation gates whose only realistic answer is "yes". Phase C's own
step-13 and step-15 text acknowledges the plugin already knows the answer on this path — it says to
"state that briefly and confirm rather than asking an open question". The two rules pull in opposite
directions, and the skill resolves it toward asking, twice in a row.

### Divergence

Each question is individually defensible: step 15's text notes that a "no" routes to the full
strategy menu, so the gate does preserve an override. But the two were written independently, in
different steps, and nothing reconciles them when both fire back to back on the same path. The
result is two turns of friction for two decisions the bootcamper was given no new information to
decide differently on.

### Suggested fix (bootcamper's)

Either combine the two into a single question, or proceed without asking on the generated-scenario
path. Both preserve the override in some form — a combined question keeps one checkpoint for a
bootcamper who does want to change the plan, while proceeding silently matches how the plugin
already handles other self-evident decisions on this path.

**Upstream:** not applicable — routed `plugin`, so no MCP-server submission is offered.

## 2026-08-16 — Module 7: WHY_KEY_DETAILS is absent without SZ_INCLUDE_MATCH_KEY_DETAILS on SDK 4.3.4

**Source:** self-observed (assistant retrospective)
**Plugin version:** 0.5.1
**Module:** Query, Visualize and Discover (Phase 2a, step 4b)
**Routing:** plugin — the claim is in the plugin's own skill text. The MCP server's
`response_schemas` correctly documents that the path *exists*; the plugin adds a claim about which
flags populate it, and that claim does not hold on this SDK.

**The decision that was withdrawn.** I wrote `explain_resolution.py` following the skill's explicit
instruction:

> ⛔ **Do not reach for `SZ_INCLUDE_MATCH_KEY_DETAILS` here.** … The CONFIRMATIONS and DENIALS named
> above are already there without it — they are part of `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS`

The resulting why-analysis output had no match-key breakdown. Rather than assume a parsing error, I
dumped `MATCH_INFO`'s top-level keys and then probed three flag sets against the same record pair
(MERIDIAN_CRM/CRM-1041 vs MERIDIAN_LOYALTY/LOY-9034), on **Senzing SDK 4.3.4**:

| Flags | `WHY_KEY_DETAILS` |
|---|---|
| `SZ_INCLUDE_FEATURE_SCORES` | **absent** |
| `+ SZ_ENTITY_INCLUDE_ENTITY_NAME` | **absent** |
| `+ SZ_INCLUDE_MATCH_KEY_DETAILS \| SZ_ENTITY_INCLUDE_ALL_RELATIONS` | **present** |

With the flag, `CONFIRMATIONS[]` returned `+NAME score 95 (CLOSE)` and `+ADDRESS score 100 (SAME)`.

**Why it matters.** The instruction is stated as a ⛔ with a stated rationale (the flag targets
`RELATED_ENTITIES[]`, so "on a why call it has nothing to attach to"), and it is emphatic enough
that a guide following it faithfully will conclude an empty result is normal. The failure is silent:
the analytical fields all render, only the breakdown is missing, so it reads as "this SDK doesn't
provide that detail" rather than "a flag is missing". That is precisely the half-populated-response
failure mode the same skill file warns about two paragraphs earlier — reached by following its own
instruction.

**Corrected:** `src/query/explain_resolution.py` now passes `SZ_INCLUDE_MATCH_KEY_DETAILS |
SZ_ENTITY_INCLUDE_ALL_RELATIONS` and documents the measurement inline, and prints an explicit
"not returned by this SDK for these flags" line rather than silently omitting the section.

**Suggestion.** Re-verify the claim against a live 4.3.x engine. If it holds only on some versions,
scope it ("on SDK X.Y, CONFIRMATIONS is present without the flag") rather than stating it
unconditionally — and consider recommending the dump-one-response check here, which is what
surfaced it.

## 2026-08-16 — SDK setup: `LD_LIBRARY_PATH` documented as conditional, but required on a stock linux_apt install

**Source:** self-observed (assistant retrospective)
**Plugin version:** 0.5.1
**Module:** SDK setup (Step 3, environment script)
**Routing:** mcp-server — the wording originates in `sdk_guide`'s own response, and the plugin
relays it. A corrected server response fixes it everywhere; editing only the plugin would leave
the same trap for anyone reading the tool directly.

**What happened.** `sdk_guide(topic='install', platform='linux_apt', language='python')` returns,
in `install.platform.env_vars`:

> `"LD_LIBRARY_PATH": "/opt/senzing/er/lib (only needed if native lib not found automatically)"`

and repeats it in `gotchas[]`: *"LD_LIBRARY_PATH is only needed if the native lib is not found
automatically (e.g., custom install location)."* This workstation is the **default** install —
`senzingsdk-runtime` from apt, at `/opt/senzing`, no custom location — and `import senzing_core`
failed with `libSz.so: cannot open shared object file: No such file or directory` until
`LD_LIBRARY_PATH=/opt/senzing/er/lib` was exported. It was not conditional here; it was required.

**The response contradicts itself.** A later entry in the *same* `gotchas[]` array states it
unconditionally:

> "Python SDK: The senzing and senzing-core packages are included in senzingsdk-runtime at
> /opt/senzing/er/sdk/python. Do NOT pip install them — instead set
> PYTHONPATH=/opt/senzing/er/sdk/python:$PYTHONPATH and LD_LIBRARY_PATH=/opt/senzing/er/lib:$LD_LIBRARY_PATH"

So one payload carries both "only needed if not found automatically" and "set both". A guide
reading `env_vars` first — the natural place to look when writing an environment script — writes a
script with only `PYTHONPATH`.

**Why it is worth recording.** The failure lands in a *later* module. The env script is written in
SDK setup; the missing variable surfaces at the first real import, which reads as a broken SDK
install rather than an incomplete environment. Module 2's own Step 1 fallback predicts exactly this
shape of confusion.

**Corrected here:** `src/scripts/senzing-env.sh` exports both variables.

**Suggestion.** Drop the conditional qualifier for `linux_apt` + Python, or scope it — "required for
the Python bindings; optional for other bindings when the loader already resolves libSz.so" —
so `env_vars` and `gotchas[]` agree.

**Verified:** `sdk_guide(topic='install', platform='linux_apt', language='python')`, MCP server
1.32.9, 2026-08-16, against Senzing SDK 4.3.4-26210 installed from apt at `/opt/senzing`.

**Upstream:** sent to Senzing via `submit_feedback` (category `bug`) on 2026-08-16, with the
Bootcamper's approval. Submissions are anonymous, so no follow-up is expected on the report itself.

## 2026-08-16 — Query/Discover: the how-analysis step names two confusable keys and a parser silently renders blank

**Source:** self-observed (assistant retrospective)
**Plugin version:** 0.5.1
**Module:** Query, Visualize and Discover (Phase 2b, step 4d)
**Routing:** plugin — the MCP server documents the correct shape; what is missing is the plugin
naming the trap at the step where the parser gets written, as it already does elsewhere.

**What happened.** Writing the how-analysis renderer, I reached for
`RESOLUTION_STEPS[].INBOUND_VIRTUAL_ENTITY` and `CANDIDATE_VIRTUAL_ENTITY` as the two sides of a
resolution step. The real keys are `VIRTUAL_ENTITY_1` and `VIRTUAL_ENTITY_2`. The parser raised
nothing — it rendered every step as `? joined ?` while the rule and match key beside them populated
correctly.

**Why the wrong name is plausible rather than careless.** `get_sdk_reference(topic='response_schemas',
filter='how_entity')` *does* carry a key called `INBOUND_VIRTUAL_ENTITY_ID` — a **string ID** on the
step, not the object — alongside `RESULT_VIRTUAL_ENTITY_ID`. So the response genuinely contains an
"inbound virtual entity" name; it simply is not the one holding `MEMBER_RECORDS[]`. A reader who has
just seen why-analysis, where `INBOUND_FEAT_DESC` / `CANDIDATE_FEAT_DESC` **are** the two sides of a
comparison, carries that pairing across and lands on a key that half-exists.

**Corrected:** `src/query/explain_resolution.py` now parses `VIRTUAL_ENTITY_1` / `VIRTUAL_ENTITY_2`
and documents why, having dumped one raw step first.

**Suggestion.** Step 4d already teaches the dump-one-response discipline; naming this specific pair
would make it concrete, the way the relationship-network guidance already warns that `find_network`
uses `MIN_ENTITY_ID`/`MAX_ENTITY_ID` while `find_path` uses `ENTITY_ID`/`RELATED_ENTITY_ID`. One
sentence — "the two sides of a resolution step are `VIRTUAL_ENTITY_1`/`VIRTUAL_ENTITY_2`; the
similarly-named `INBOUND_VIRTUAL_ENTITY_ID` is a string ID, not the object" — closes it.

**Verified:** `get_sdk_reference(topic='response_schemas', filter='how_entity', language='python')`,
MCP server 1.32.9, 2026-08-16.

## 2026-08-16 — A re-captured tab overwrites the capture manifest, and graduation's coverage check then passes on a 1-of-1 denominator

**Source:** self-observed (assistant retrospective)
**Plugin version:** 0.5.1
**Module:** Query, Visualize and Discover (Phase 1, step 3c) — surfaced at Bootcamp graduation, Step 1a
**Routing:** plugin — `capture_screenshots.py` and `generate_recap_pdf.py --check` both ship with the
plugin. Nothing here involves the Senzing MCP server or the Claude interface.

**What happened.** All six tabs of `results_visualization.html` were captured, and all six PNGs are
on disk and embedded in the recap. But the first Search / Probe capture came back showing an empty
result set (the query used a surname alone, which matched nothing), so that one tab was re-captured
on its own. The re-run rewrote `docs/visualizations/results_visualization-tabs.json` from scratch:

```json
{"requested": ["probe"], "requested_count": 1, "captured_count": 1, "not_applicable": [], "failed": []}
```

The five earlier captures are gone from the manifest. The companion file for the Truth Set
visualization, never re-captured, still correctly records all six.

**Why it looks like it worked.** Graduation's Step 1a tab-coverage check reads exactly this manifest
to answer "did every captured tab reach the recap?" With a 1-of-1 denominator it reports full
coverage — and it would report full coverage just as cheerfully if five of the six images had been
lost, because the record of their ever having been captured was destroyed by the fix for an unrelated
problem. The check is structurally incapable of failing after a targeted re-capture, and nothing says
so. Graduation's own guidance is emphatic that a skipped check must be reported as skipped rather
than counted as passed; this one is silently neutered instead.

**No harm here** — the recap carries all six images, verified by counting them directly against
`docs/visualizations/results_visualization-*.png` rather than trusting the manifest.

**Suggestion.** Have `capture_screenshots.py` **merge** into an existing `<name>-tabs.json` rather
than replacing it: union `requested`, replace the entry for any tab re-captured in this run, and keep
the rest. Failing that, have `--check` warn when a manifest's `requested_count` is lower than the
number of `<name>-*.png` files on disk — the cheap version of the same guard.

## 2026-08-16 — Recap subsections drifted to bold labels for nine straight modules; nothing noticed until graduation refused to render

**Source:** self-observed (assistant retrospective)
**Plugin version:** 0.5.1
**Module:** all of them — introduced at the first recap append, surfaced at Bootcamp graduation Step 1b
**Routing:** plugin — the template is correct and unambiguous; what is missing is any check between
writing a recap section and rendering the PDF eleven modules later.

**What happened.** `module-completion.md` Step 2b's template specifies the four subsections as H3
headings — `### Information Shared`, `### Questions & Responses`, `### Actions Taken`,
`### End-of-Module Summary`. I wrote them as bold labels (`**Information Shared**`) instead, at the
first module, and then reproduced that shape faithfully for all nine. The mistake is mine; the
template says otherwise in plain text.

**Why it survived to the end.** Bold labels render fine in every Markdown viewer, so the recap looked
correct at every point during the bootcamp. The failure appeared only at graduation:

```text
ERROR: refusing to render docs/bootcamp_recap.md
  - input does not look like a bootcamp recap: 0 of 9 '##' sections carry any recognized sub-section
  - catastrophic content loss: only 2% of the input's content would reach the PDF (minimum 60%)
```

The generator's refusal is exactly right, and its message named the cause precisely — a good failure.
But it is the *last* step of the *last* module, and the drift had by then been repeated nine times.
Recovering it at graduation meant a structural rewrite of the entire keepsake in the same turn that
was supposed to render it. Had the generator been more permissive, the same nine sections would have
rendered at 2% and shipped.

**Suggestion.** The validator that catches this already exists — `generate_recap_pdf.py --check` —
and it is only ever invoked at graduation. Have module-completion Step 2b run it after appending the
**first** module's section (or after every append; it is fast and reads one file). A drift caught at
module one costs one correction; caught at graduation it costs nine, at the worst possible moment.

**Corrected here:** all 36 subsection labels converted to H3; content guard confirmed no line lost;
`--check` now reports all nine sections complete, and the PDF renders at 99% retention with 12 of 12
images.
