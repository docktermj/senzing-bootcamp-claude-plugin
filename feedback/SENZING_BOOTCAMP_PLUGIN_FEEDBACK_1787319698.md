# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp. Every entry is saved here, whatever it turns
out to be about. Entries routed `mcp-server` may **also** have been forwarded to Senzing —
only ever with your explicit yes, and with identifying details stripped; each entry's
`Upstream:` field records what happened.

**Started:** 2026-08-18

## Your Feedback

## Improvement: Python-on-Windows unsupported, discovered only at SDK setup

**Date:** 2026-08-18
**Module:** SDK setup
**Priority:** High
**Source:** bootcamper-reported
**Routing:** both — the bootcamp's programming-language gate noted Python's Windows caveat but understated its cost (WSL2/Docker install, admin rights, reboot), and Senzing's own v4 System Requirements lists Windows and Python as supported in two separate tables with no OS-by-language matrix and no stated rationale
**Upstream:** submitted 2026-08-18

### What happened

The bootcamper chose Python as their programming language during Bootcamp preparation, on Windows 11. Two modules later, at SDK setup, platform routing revealed that the Senzing Python SDK is supported on Linux only — not on Windows or macOS. Proceeding with Python required installing WSL2, rebooting the machine, and creating an Ubuntu user account before any Senzing work could begin. The bootcamper asked why Windows is not supported with Python.

Senzing's v4 System Requirements page lists Windows >= 11 as a supported operating system (marked "Limited Availability") and Python >= 3.10 as a supported language, in two separate tables with no OS-by-language matrix. Read on its own, that page makes Python-on-Windows look supported. The exclusion surfaces only from `sdk_guide(topic='install', platform='windows', language='python')`. No rationale for the exclusion appears anywhere in the indexed documentation.

### Why it matters

In the bootcamper's words: it wasted their time installing WSL2 halfway through the bootcamp. The cost (a system-level virtualization install, a reboot, and a new Linux user account) landed after they had already committed to Python and completed two modules, rather than at the point of choosing.

### Suggested fix

None provided by the bootcamper. Bootcamp-side options: state the full cost of the Python-on-Windows/macOS choice at the programming-language gate in Bootcamp preparation (that it means installing WSL2 or Docker, with admin rights and a reboot), rather than the shorter "runs via Docker" annotation currently shown; and/or detect the absence of Docker/WSL2 at that gate and surface it before the language is chosen rather than at SDK setup.

### Context when reported

- **Time:** 2026-08-18
- **Plugin version:** 0.5.1
- **Workstation:** Windows 11 Pro 10.0.26200 (x86-64); WSL2 with Ubuntu 26.04 (amd64) installed during this module
- **Model / effort:** claude-opus-5 / high
- **Context size:** approximately 100-120k tokens (estimate; exact usage not exposed to the assistant)
- **Module / step:** `sdk_setup` / step 2 recorded, actually mid-step 3 (SDK install)
- **Recent questions:** "How would you like to proceed with the Senzing SDK?"; "Do you accept the Senzing End User License Agreement (EULA)?"
- **Bootcamper responses:** Chose option 1 (install WSL2 and keep Python); accepted the EULA
- **Behind the scenes:** `/senzing-bootcamp:bootcamp-feedback` command invoked during `module-02-sdk-setup` Step 3 (Install Senzing SDK), after Phase 2 EULA acceptance and while awaiting the bootcamper to run the sudo install commands. Platform routing rule 1 (Python + Windows -> Docker) had fired at Step 2; the bootcamper chose WSL2 instead, resolving the platform to `linux_apt`.
- **Observed problem:** The consequence of the Python + Windows combination — an unplanned WSL2 install and reboot — was not visible at the point the language was chosen, two modules earlier.
- **Expected behavior:** The Bootcamp preparation language gate's per-option annotation rules (module-02 routing rules 1 and 4) require Windows options to be annotated where the platform forces a language into a container. The annotation was shown ("Python — official SDK; runs via Docker (the SDK doesn't install natively on Windows)"), but it conveyed a routing detail rather than a setup cost, and no check was made for whether Docker or WSL2 existed on the machine.
- **Divergence:** The annotation rule is satisfied literally but not in effect: it names the mechanism (Docker) without naming the price (install virtualization software, obtain admin rights, reboot), and nothing at that gate inspects the machine for the prerequisite it implies. Upstream, Senzing's own System Requirements page presents the two dimensions independently, so a bootcamper verifying the choice against the official docs is confirmed in the wrong conclusion.

## Improvement: Assistant asserted the wrong built-in evaluation license capacity

**Date:** 2026-08-18
**Module:** Discover the Business Problem
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the assistant stated a Senzing capacity figure without sourcing it from the MCP route that owns it, which the module's own Step 5a requires
**Upstream:** not applicable

### What happened

During Discover the Business Problem (Phase 1, Step 5a — the record-count threshold check), the assistant told the bootcamper the planned scenario volume was "comfortably inside the built-in evaluation license's 250K-record capacity, so there's no license concern to flag," and accordingly left `license_guidance_deferred` unset.

At SDK setup Step 5, the figure was sourced properly from `sdk_guide(topic='load', language='python', platform='linux_apt', record_count=1000)`, whose `compatibility_notes` and `engine_config_notes` both state the actual limit: "Without a license, Senzing is limited to 500 Distinct Source Records (DSRs). Loading record 501 fails with SENZ9000|LIMIT."

The 250K figure was real but belonged to a different thing — the free evaluation license that can be *requested* via `submit_feedback` with `category='license_request'` (10 days, 250K records) — not the built-in license active by default. The two were conflated.

### Why it matters

The correction moves the limit down by a factor of 500, and it changes a decision that was already recorded. The generated scenario plans "a few hundred to low thousands of records" across four sources, which the real 500-record built-in limit does not cover. The earlier "no license concern" assessment therefore suppressed the very signal (`license_guidance_deferred`) that the Data collection module's volume-gated License Key gate reads. Left uncorrected, the bootcamper would have met SENZ9000 mid-load with no prior warning.

### Suggested fix

`license_guidance_deferred: true` has now been written to `config/bootcamp_preferences.yaml` so the Data collection gate fires as designed. More generally, Module 1 Step 5a says the built-in capacity must be "confirmed via the Senzing MCP server (never a hardcoded figure)" — the step would be harder to get wrong if it named the specific route that carries the number, as SDK setup Step 5 does (`sdk_guide(topic='load', ...)` with a `record_count` above the limit), rather than referring to the MCP server generally.

### Context when reported

- **Time:** 2026-08-18
- **Plugin version:** 0.5.1
- **Workstation:** Windows 11 Pro 10.0.26200 (x86-64); WSL2 with Ubuntu 26.04 (amd64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** approximately 100-120k tokens (estimate; exact usage not exposed to the assistant)
- **Module / step:** reversal originated in `business_problem` / step 5a; caught in `sdk_setup` / step 5
- **Recent questions:** not applicable — filed silently, with no bootcamper involvement
- **Bootcamper responses:** not applicable
- **Behind the scenes:** `module-01-business-problem` Phase 1 Step 5a (record-count threshold check) versus `module-02-sdk-setup` Step 5a (built-in evaluation license confirmation)
- **Observed problem:** Two different Senzing license capacities (500 built-in, 250K requestable) were conflated into one figure attributed to the built-in license.
- **Expected behavior:** Module 1 Step 5a requires the built-in evaluation capacity to be confirmed via the MCP server rather than asserted, and INV-080 forbids stating a Senzing fact from memory.
- **Divergence:** No MCP call was made for the capacity figure at Step 5a; the number came from the `submit_feedback` tool description read earlier in the session, which describes the requestable evaluation license rather than the built-in one.

## Improvement: License-request flow asks "how did you hear about Senzing" unnecessarily

**Date:** 2026-08-18
**Module:** Data collection
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — the bootcamp chose to ask a dedicated question for a field it could reasonably infer from context, rather than the Senzing MCP server requiring that specific interaction
**Upstream:** not applicable

### What happened

During the Step 8a License Key gate's in-flow evaluation-license request, the plugin asked the bootcamper a dedicated question — "How did you hear about Senzing?" — as one of three separate turns (first name, work email, how-heard) before showing the draft request and asking for consent to send it. The bootcamper said this question did not need to be asked.

### Why it matters

In the bootcamper's words: "no need to ask." The context already answers it — they are, self-evidently, taking the Senzing bootcamp at the moment the request is made, so asking adds a turn without adding information.

### Suggested fix

The bootcamper's implied fix: skip the question. The `submit_feedback` tool's `license_request` category requires a `how_heard` value for the call to succeed, but nothing requires that value to come from a dedicated question — the plugin could default it to a fixed string such as "Senzing Bootcamp" (or "Claude Code / Senzing Bootcamp plugin") and only ask if the bootcamper wants to override it, saving a turn on every in-flow request.

### Context when reported

- **Time:** 2026-08-18
- **Plugin version:** 0.5.1
- **Workstation:** Windows 11 Pro 10.0.26200 (x86-64); WSL2 with Ubuntu 26.04 (amd64)
- **Model / effort:** claude-sonnet-5 / (effort not exposed)
- **Context size:** approximately 140-160k tokens (estimate; exact usage not exposed to the assistant)
- **Module / step:** `data_collection`, Step 8a sub-step 6a (in-flow license request), reported just after module close during the transition to `data_quality_mapping`
- **Recent questions:** "What first name should I use for the license request?"; "What work email address should the license be sent to?"; "How did you hear about Senzing?"; "Send this evaluation-license request ... to Senzing?"
- **Bootcamper responses:** Joel; joel.lim@ncs.com.sg; "I am taking the bootcamp"; yes, send it
- **Behind the scenes:** `module-04-data-collection/SKILL.md` Step 8a sub-step 6a, which asks for `firstname`, `email`, and `how_heard` as three separate 👉 questions per the `submit_feedback` tool's `license_request` field requirements (`how_heard` is documented as required in the property description, not the schema's `required` array).
- **Observed problem:** A dedicated question for a field whose answer is fixed by the bootcamp context itself.
- **Expected behavior:** N/A — no rule requires this to be a question; it is a design choice available to the module.
- **Divergence:** The module treats every field the tool schema accepts as something to ask the bootcamper, without distinguishing a field whose value is contextually fixed (how they heard about Senzing, while taking the Senzing bootcamp) from one that is genuinely bootcamper-specific (name, email).


## Reversed decision: two mappings changed after the Discover phase read the engine's output

**Date:** 2026-08-18
**Module:** Query, Visualize and Discover (findings), Data Quality, Mapping, and Transformation (fixes)
**Priority:** Medium
**Source:** agent-observed
**Routing:** local — a record of what the static gates could not see, kept so the corrected mapping does not arrive without the reasoning behind it
**Upstream:** not submitted

Two mappings approved by every static gate in Module 5 were changed after querying the loaded
data. Filing at the moment it happened, because by graduation only the corrected mappers would
survive and not the account of what was wrong with the originals or how it was caught.

**1. OPEN-SANCTIONS `PASSPORT_NUMBER` carries annotations, not numbers.**
5 of 65 values across 3 records hold Japanese-language issuance/expiry notes — e.g.
`（1990年11月6日発行、1995年9月13日失効）`, which contains no passport number at all. Loaded as a
PASSPORT feature these produce a `-PASSPORT` conflict that blocked entity 200025 (OFAC) from
resolving with 700034 (OPEN-SANCTIONS) — the same sanctioned individual, with NAME, DOB, ADDRESS,
PLACE_OF_BIRTH and RECORD_TYPE all scoring 100. A confirmed false negative.

*Why the gates missed it:* every Module 5 gate is structural. The analyzer saw a well-formed
string in a valid attribute; the verbatim check confirmed it was faithful to the source (it was —
faithfully wrong); the routing report saw the field reach a feature. Nothing evaluates whether a
value is the KIND of thing the feature means. Only `why_entities` on the loaded data exposed it.

*Suggestion for the plugin:* Module 5's null-sentinel guidance is framed around codes and
identifiers with recognisable sentinels (`n.a.`, `XXX`). It could add a shape check for identifier
features — a value carrying no digits at all, or script outside the expected range, is an
annotation rather than an identifier. The Entity Specification already states the rule ("do NOT
put dates or free-text notes in any identifier"); the gates just do not test for it.

**2. ICIJ `THE BEARER` is a null-name sentinel, not a person.**
30 records merged into entity 800049 on `+NAME+ADDRESS`. "The bearer" is the offshore-leaks
placeholder for bearer shares, where no owner is named.

*Why it was missed:* the sentinel checks applied in Module 5 covered codes and identifiers. This
sentinel is a **name**, and nothing prompted a check for sentinel values in name fields. Module 5's
profiler had it in plain sight — the single most frequent name in the source at 73 occurrences —
which suggests a useful heuristic: a name value repeating far above the source's own name-frequency
distribution is a placeholder until proven otherwise.

## Improvement: WSL2 + project on /mnt/c makes the datastore ~300x slower, and nothing warns

**Date:** 2026-08-18
**Module:** SDK setup (datastore placement), surfaced in Data processing
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the bootcamp chooses `database/G2C.db` inside the project directory, which on the Windows+WSL2 path is the slow one; the SDK is behaving correctly
**Upstream:** not submitted

On Windows with the Senzing SDK in WSL2 and the project on the Windows filesystem (`/mnt/c/...`),
the datastore is reached over the 9p protocol. Measured with `check_repository_performance(5)`:

| Location | Inserts in 5s |
|---|---|
| `/mnt/c/...` (project directory) | 1,112 |
| `~/senzing-bootcamp/` (WSL-native ext4) | 326,606 |

End-to-end load throughput was **3 records/second**, which projected to ~7.5 hours for 83,338
records. After relocating the datastore: **138–180 records/second**, ~9 minutes. Same code, same
data, same machine.

This is the documented low-IOPS-storage anti-pattern (`search_docs(query='loading',
category='anti_patterns')` → "Do Not Use Low-IOPS Storage"), but nothing in the bootcamp connects
it to the WSL2 setup it recommends on Windows. A bootcamper who does not think to benchmark simply
experiences the bootcamp as very slow and has no reason to suspect storage.

**Suggestion:** SDK setup already knows it is on WSL2 (it records
`host: WSL2 Ubuntu ... on Windows 11`). When that is true and the project is under `/mnt/`, either
default the datastore to a WSL-native path, or run `check_repository_performance` once at setup and
show the number. The check takes 5 seconds and the difference is two orders of magnitude.

**Context when reported:** Windows 11 + WSL2 Ubuntu 26.04, Senzing SDK 4.3.4, SQLite, 83,338
records across four sources.

## Improvement: three SDK response field names guessed wrong, each rendering blank rather than erroring

**Date:** 2026-08-18
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — `reporting_guide`'s `entity_views` and `graph` patterns show the CALL but not the RESPONSE shape, and the natural field names are wrong in all three cases
**Upstream:** not submitted

Writing the query programs, three parsers were written against plausible field names and each
produced blank output at exit 0:

| Method | Guessed | Actual |
|---|---|---|
| `how_entity_by_entity_id` | `INBOUND_VIRTUAL_ENTITY` / `CANDIDATE_VIRTUAL_ENTITY` | `VIRTUAL_ENTITY_1` / `VIRTUAL_ENTITY_2` |
| `find_network_by_entity_id` links | `START_ENTITY_ID` / `END_ENTITY_ID` | `MIN_ENTITY_ID` / `MAX_ENTITY_ID` (normalised, not directed) |
| `why_entities` | `MATCH_KEY` / `ERRULE_CODE` | `MATCH_INFO.WHY_KEY` / `MATCH_INFO.WHY_ERRULE_CODE` |

All three are recoverable from `get_sdk_reference(topic='response_schemas', filter=…)`, and the
module skill does say to look up the response shape before parsing (INV-115). The gap is that
`reporting_guide`'s worked patterns — which are what an implementer copies — show the call and the
parse of `RESOLVED_ENTITY`, but say nothing about these three shapes. An implementer following the
pattern has no prompt to go and check.

The third is the sharpest: `MATCH_KEY` **is** a real field name, on `RESOLVED_ENTITY.RECORDS[]`.
Reusing it on a why response is the natural mistake, and it renders `(none)`.

**Suggestion:** have `reporting_guide(topic='entity_views')` and `(topic='graph')` name the
top-level response keys their patterns produce, or link the matching `response_schemas` filter.

**Context when reported:** Python binding, Senzing SDK 4.3.4, MCP server 1.32.9.

## Improvement: an SzAbstractFactoryCore kept as a local destroys its engine when it goes out of scope

**Date:** 2026-08-18
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the shipped `senzing_viz_server.py` already documents this in a code comment, but the module skill that tells you to write query programs does not
**Upstream:** not submitted

A shared helper that created the factory as a local and returned only the engine failed on the
first call with `SzSdkError - engine object has been destroyed and can no longer be used, create a
new one`. The factory had been garbage-collected.

The bundled `scripts/senzing_viz_server.py` knows this — it carries a comment saying the factory
must stay referenced for the caller's lifetime — so the knowledge exists in the plugin, just not
where a bootcamper writing their own query program will meet it. Factoring engine setup into a
helper is the obvious first move when writing five query programs, and it is exactly the shape that
triggers this.

**Suggestion:** add one line to the module-07 query-program guidance: keep the factory referenced
for as long as any engine created from it is in use.

**Context when reported:** Python binding, Senzing SDK 4.3.4.

## Improvement: the PDF renderer's CJK-dropping advice does not fit a finding whose evidence IS non-Latin

**Date:** 2026-08-18
**Module:** Query, Visualize and Discover (data-discoveries PDF)
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the warning itself is good; only its suggested remedy is unusable in this case
**Upstream:** not submitted

`generate_document_pdf.py` correctly warned that 38 CJK characters were dropped from
`bootcamp_data_discoveries.pdf`, and its remedy is: *"use each entity's verified Latin-script name
or alias instead of its non-Latin primary name."* That fits a non-Latin **entity name**. It does not
fit this case, where the finding was *about* Japanese text wrongly stored in a `PASSPORT_NUMBER`
field — the CJK string was the evidence, not a name, and there is no Latin alias for it. Following
the advice literally would have deleted the finding.

The document was rewritten to describe each value in ASCII alongside the verbatim form, which keeps
the evidence in both the Markdown and the PDF. That generalises.

**Suggestion:** extend the warning's remedy with the case where the non-Latin text is the subject
rather than a label: describe the value in ASCII next to it, so the PDF still carries the meaning.

**Context when reported:** stdlib renderer (no fpdf2 installed), Latin-1 core fonts.
