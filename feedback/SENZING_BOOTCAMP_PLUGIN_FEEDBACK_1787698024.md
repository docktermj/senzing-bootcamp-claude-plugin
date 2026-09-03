# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp. Every entry is saved here, whatever it turns
out to be about. Entries routed `mcp-server` may **also** have been forwarded to Senzing —
only ever with your explicit yes, and with identifying details stripped; each entry's
`Upstream:` field records what happened.

**Started:** 2026-08-25

## Your Feedback

## Improvement: Guide presented an unsourced inference about employer licensing as fact

**Date:** 2026-08-25
**Module:** Data collection
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — the License Key gate (Step 8a / 6a) gives the guide no rule about the bootcamper's identity or email domain, so the guide improvised an advisory that no MCP tool or skill file supports.
**Upstream:** not applicable

### What happened

At the Senzing License Key gate (Step 8a), after the bootcamper selected option 4 (request a free
evaluation license in-flow), the guide volunteered — before collecting any values — that the
bootcamper's account email was on the `senzing.com` domain, and that "if you're at Senzing, you
very likely have access to a license through internal channels, which would be faster and wouldn't
consume the one-per-email public evaluation request."

The bootcamper asked whether that was correct. It was only partly:

- **Sourced and correct:** "one per email, re-requestable after 30 days" (and the 10-day /
  250,000-record terms) came verbatim from the Senzing MCP server's `get_capabilities` description
  of `submit_feedback`'s `license_request` category.
- **Unsourced:** "you very likely have access to a license through internal channels" was the
  guide's own inference. No MCP tool, skill file, or documentation supports any claim about
  Senzing's internal licensing practices. It was asserted with unwarranted confidence and used to
  steer a decision the bootcamper had already made one turn earlier.

A secondary concern: the bootcamper's email address is supplied to identify them, not as a fact to
reason from. Inferring an employer from the domain and redirecting a decision on that basis goes
beyond identification.

### Why it matters

"I don't want assumptions presented as fact."

The bootcamp's entire design premise is that Senzing facts come from the MCP server and never from
the guide's own knowledge (the MCP-first invariant). A guide that follows that rule scrupulously for
attribute names and SDK signatures — and then improvises a confident claim about licensing at a
consent gate — teaches the bootcamper that the sourcing discipline is selective. It is worst
precisely here: the License Key gate is a decision point with real consequences (a one-per-email
request, a 30-day lockout), and it sits immediately before the only step in the bootcamp that
transmits personal details off the machine.

### Suggested fix

**Bootcamper's suggestion:** "Just don't say things as fact that you are assuming."

_Assistant-proposed (not the bootcamper's words):_

1. State the rule explicitly in `ground-rules.md`: an assertion that is not MCP-sourced, not in a
   skill file, and not measured on the machine must be labeled as an inference at the point it is
   made — or not made at all. The existing MCP-first invariant covers *Senzing facts*; this case
   was an assertion about Senzing's *business practices*, which fell through the gap.
2. In `module-04-data-collection/SKILL.md` Step 8a/6a, add a directive that the guide must not
   infer anything about the bootcamper's employer, affiliation, or entitlements from their email
   address or any other identifying context, and must not use such an inference to steer the
   license choice. The gate's options are the options.
3. Consider a general rule that the bootcamper's identifying context (email, name, account details)
   is for identification and for fields a tool explicitly requires — never an input to the guide's
   reasoning about what the bootcamper should choose.

### Context when reported

- **Time:** 2026-08-25 09:50 local (MDT)
- **Plugin version:** 0.5.2
- **Workstation:** macOS 26.6.2 (arm64, Apple Silicon)
- **Model / effort:** claude-opus-5 / effort not exposed to the session (bootcamper switched to Opus 5 at SDK setup)
- **Context size:** Unknown (not exposed to the session)
- **Module / step:** `data_collection` / `current_step` null — mid-module at Step 8a (Senzing License Key gate), sub-step 6a value collection
- **Recent questions:**
  - "Which best describes your Senzing License Key situation?" (four-option form)
  - "What name should the evaluation-license request be in?"
- **Bootcamper responses:**
  - "4" (request a free evaluation license now through the bootcamp)
  - "Julie Huff" (supplied mid-turn, after raising this feedback)
- **Behind the scenes:** Module 4 Step 8a fired because the collected total (94,143 records across
  NPI-PROVIDERS, PPP_LOANS and ENFORMION) exceeds the measured `license_record_limit` of 500.
  `get_capabilities` confirmed `submit_feedback` available, so the four-option form was presented.
  Sub-step 6a's consent discipline was active: collect firstname / work email / how_heard one
  question per turn, then show the exact payload and gate the send.
- **Observed problem:** Before the first value question, the guide inserted an unsolicited advisory
  inferring the bootcamper's employer from their email domain and asserting, without any source,
  that they likely had internal license access — implicitly recommending they abandon the option
  they had just chosen.
- **Expected behavior:** Sub-step 6a specifies exactly what precedes the value questions: confirm
  the tool's current requirements, then ask for the values one 👉 per turn, stating that a work
  email is required. Nothing in it authorizes an advisory about the bootcamper's employer, and the
  MCP-first invariant forbids asserting Senzing specifics that no tool produced.
- **Divergence:** The MCP-first invariant is written in terms of "Senzing facts" — SDK methods,
  attribute names, config options, error codes, entity-resolution specifics. A claim about how
  Senzing employees obtain licenses is a claim about the *company's business practices*, which no
  rule in the plugin currently covers, so the guide treated it as ordinary conversational
  helpfulness rather than as an assertion requiring a source. INV-247 ("never originate a 👉
  question") governs questions but not volunteered advisories, leaving this class ungoverned.

---

## Improvement: Module transition "yes" is not acknowledged before the next module loads

**Date:** 2026-08-25
**Module:** Query, Visualize and Discover (transition into it, from Data processing)
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — the module-completion / transition guidance does not require any visible
acknowledgment between the bootcamper answering the transition 👉 and the next skill beginning
its own file reads. Nothing here involves the Senzing MCP server or the Claude interface.
**Upstream:** not applicable

### What happened

The bootcamper answered **yes** to the pinned transition question *"Are you ready to move on to
the next module: Query, Visualize and Discover?"*, then had to answer **yes** a second time.

Verifiable from the transcript: after the first `yes`, the guide made three consecutive tool
calls — invoking the `module-07-query-visualize-discover` skill, then two `Bash` reads of that
skill's own `.md` files to find its step list and 👉 questions — and emitted **no user-visible
text at all** between the bootcamper's answer and the eventual module-start banner. The
bootcamper's next message arrived as `[Request interrupted by user]` followed by `yes`.

Not verifiable, and recorded as inference rather than fact: that the silence is what prompted
the second `yes`. The guide cannot observe the bootcamper's screen and does not know whether a
permission prompt, a spinner, or nothing at all was displayed during those tool calls.

### Why it matters

> "I lost my place and had to re-confirm"

The transition gate is the one moment per module where the bootcamp deliberately stops and waits
for the bootcamper. Answering it and then seeing nothing change makes the answer look unregistered.
The cost is not the extra keystroke — it is losing your place in a multi-hour guided flow, and
having to reconstruct where you were and what you had just agreed to.

### Suggested fix

> "acknowledge the yes immediately before loading the module"

Emit a short visible line the moment an affirmative transition answer is received — before
invoking the next module's skill and before any file reads. One line naming the module being
started is enough.

### Context when reported

- **Time:** 2026-08-25 11:48 CDT
- **Plugin version:** 0.5.2
- **Workstation:** Darwin 25.6.0 (arm64), macOS on Apple Silicon
- **Model / effort:** claude-opus-5 / effort not exposed in this session (Unknown)
- **Context size:** Unknown
- **Module / step:** `query_visualize_discover` / `current_step: null` (module just starting;
  8 modules recorded in `modules_completed`)
- **Recent questions:**
  - 👉 *"Are you ready to move on to the next module: Query, Visualize and Discover?"*
  - (earlier, same close) 👉 *"The numbers are strong overall, but this defect damages the fraud
    use case specifically. What would you like to do?"*
- **Bootcamper responses:** `yes` → [interrupted] → `yes`; earlier `1` (fix the defect now)
- **Behind the scenes:** Module 6 completion had just run (progress written, recap section
  appended, `current_module` set to `query_visualize_discover`, `current_step` set to null). On
  the affirmative reply the guide called `Skill(senzing-bootcamp:module-07-query-visualize-discover)`,
  which returned the SKILL.md body, then ran two `Bash` calls (`wc -l` + `grep` over the phase
  files, then `sed -n` over `phase1-query-visualize.md`) to locate the step list and its 👉
  questions before composing the module-start apparatus.
- **Observed problem:** the bootcamper answered the transition question and, seeing no visible
  response, answered it again — interrupting the in-flight tool call to do so.
- **Expected behavior:** `phaseD-validation.md` → "Module completion and transition to Module 7"
  says that on an affirmative reply the guide should "produce the Module 7 start banner, journey
  map, before/after framing, and step overview per the ground rules". It specifies *what* to
  produce but sets no expectation about *when* the bootcamper first sees something, and the
  ground rules' 👉 protocol governs how questions are asked rather than how answers are
  acknowledged.
- **Divergence:** the guidance is silent on the interval between the answer and the banner. A
  new module's skill loads and then reads its own documentation before it can compose the
  banner, so that interval is not incidental — it is structural, and it will recur at every one
  of the ten module transitions. Nothing in the plugin currently requires the answer to be
  acknowledged first, so the gap is in the instructions rather than in this particular run.

---

## Improvement: business_problem.md records only the refined phrasing, losing the bootcamper's exact words

**Date:** 2026-08-25
**Module:** Discover the Business Problem (surfaced in Query, Visualize and Discover)
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — the `docs/business_problem.md` template and the interview flow that fills it
are defined by `module-01-business-problem/phase2-document-confirm.md`. Nothing about the Senzing
MCP server or the Claude interface is involved.
**Upstream:** not applicable

### What happened

`docs/business_problem.md` captures the guide's *refined* rendering of each answer and does not
preserve what the bootcamper actually said. The bootcamper asked that the verbatim language be
kept alongside the refined version.

Checking the document against the transcript surfaced a live instance rather than a hypothetical
one. Asked about downstream integration, the bootcamper said:

> "Yes. **possible fraud** needs to feed our fraud tool and possible matches need to feed into
> service now."

`business_problem.md` line 43 renders that as:

> "Internal fraud tool (**confirmed fraud cases**); ServiceNow (possible matches for review)."

*Possible* became *confirmed*. That is a different routing rule — it changes which entities reach
the fraud tool and how large that queue is. Line 37 of the same document kept "Possible-fraud
entities routed to the internal fraud tool", so the document now contradicts itself, and it
contains nothing that would settle which reading is correct.

The drift then propagated: Module 7 step 1 derives query requirements *from this document*, and
requirement 7 was consequently titled "Confirmed-fraud candidate list for the internal fraud
tool" — three modules downstream of the sentence that was reworded.

### Why it matters

> "It's good to have captured for later use."

The document is the durable record of the business problem and is read by every later module —
Module 7 derives its query requirements from it directly, and graduation carries it into the
production project. Once the original phrasing is gone there is no way to check a refinement
against what was meant, and a single substituted word propagates silently into requirements,
queries and deliverables.

### Suggested fix

> "capture the exact language of the user in the bootcamp in addition to the refined version"

Keep both. For each interview answer, record the bootcamper's own words verbatim alongside the
refined prose — e.g. a short "In your words" block per section, or a `> "…"` blockquote beneath
each refined statement. The refined version stays the working text; the verbatim line makes any
drift visible and correctable.

### Context when reported

- **Time:** 2026-08-25 11:53 CDT
- **Plugin version:** 0.5.2
- **Workstation:** Darwin 25.6.0 (arm64), macOS on Apple Silicon
- **Model / effort:** claude-opus-5 / effort not exposed in this session (Unknown)
- **Context size:** Unknown
- **Module / step:** `query_visualize_discover` / step `1` complete, building step 2 query programs
- **Recent questions:**
  - 👉 *"Is there anything you'd like to adjust?"* (the seven derived query requirements)
  - 👉 *"Why does it matter to you?"* / 👉 *"What priority would you give this?"* (this feedback)
- **Bootcamper responses:** `no` (requirements accepted as derived — including the mis-titled
  requirement 7); then `It's good to have captured for later use.`; then `2`
- **Behind the scenes:** Module 7 Phase 1 step 2. `MasterList.java` had just run (5,674 entities);
  `FraudLeads.java` compiled and pending. Step 1 had derived seven query requirements *from
  `docs/business_problem.md`*, which is the mechanism by which the reworded phrase reached the
  query layer.
- **Observed problem:** the bootcamper's own wording is absent from the document that records
  their business problem, and at least one refinement changed the meaning of a routing rule.
- **Expected behavior:** `module-01-business-problem/phase2-document-confirm.md` writes
  `docs/business_problem.md` from the interview answers and ends with a bootcamper confirmation
  step. The confirmation gate is what is supposed to catch a bad refinement.
- **Divergence:** the confirmation gate asks the bootcamper to approve the *refined* document,
  with the original phrasing no longer visible anywhere for comparison — so the check is against
  a plausible-sounding rewrite rather than against what they said. It was confirmed as accurate
  at the time ("yes, that's accurate"), and the substitution still went through. A gate that
  cannot show both versions cannot reliably catch a one-word change, which is why preserving the
  verbatim text is a correctness measure and not only an archival nicety.

---

## Improvement: The visualization reference colours graph nodes by their FIRST source, and the Truth Set cannot expose it

**Date:** 2026-08-25
**Module:** Truth Set visualization (defect surfaced in Query, Visualize and Discover)
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the visualization contract and the shipped reference implementation
(`scripts/senzing_viz_server.py`, `visualization-api-reference.md`) define the node encoding. The
Senzing MCP server is not involved.
**Upstream:** not applicable

### What happened

The visualization server built in Truth Set visualization coloured each graph node from
`data_sources[0]` — the entity's **first** data source. Module 7 points the same app at the
bootcamper's own loaded data, where 294 of 5,619 entities span two or more sources. Every one of
them would have rendered in a single-source colour, beneath a legend stating they were
single-source.

Nothing errors, nothing looks broken, and the headline finding of the whole bootcamp — the same
organisation found in more than one system — is invisible in the tab built to display it.

Module 7's own skill text warns about exactly this and reports a prior run that rendered 1,951
cross-source entities in a single-source colour. The warning is in the right place; the **shipped
reference it warns about still contains the defect**, so every bootcamper who builds from the
reference reproduces it and only catches it if they read that paragraph and act on it.

### Why it matters

The Truth Set structurally cannot catch this: nearly all of its entities sit in one source, so
first-source colouring looks correct there and misreports only on the bootcamper's own data — after
the module that could have tested it has closed. It is a defect whose test data guarantees a pass.

The cost is not cosmetic. The cross-source count is the number every preceding module exists to
produce, and the entity graph is where a bootcamper looks at it.

### Suggested fix

Colour by the entity's **whole source set**, keyed on the sorted source codes joined (e.g.
`NPI-PROVIDERS+PPP_LOANS`), and build the legend from the same keys so it matches what is drawn.
That is what this run did, and it produced seven distinct encodings for three sources. Fixing it in
the reference means it is right by default rather than right only when the warning is read.

Consider also giving the Truth Set module a check that would fail on it — e.g. asserting the legend
key count equals the distinct source-set count — since the data alone will never provoke it.

### Context when reported

- **Time:** 2026-08-25 14:20 CDT
- **Plugin version:** 0.5.2
- **Workstation:** macOS 26.6.2 (arm64)
- **Model / effort:** claude-opus-5 / effort not exposed in this session (Unknown)
- **Context size:** Unknown
- **Module / step:** `query_visualize_discover` step 3c, building the visualization app
- **Recent questions:** the visualization offer, accepted
- **Bootcamper responses:** yes
- **Behind the scenes:** `Html.java` lines 459-461 read
  `SRC[(d.data_sources||[])[0]]` for fill, stroke and stroke width; `Model.graph()` already emitted
  the full `data_sources` list per node, so the data was present and only the client-side encoding
  was wrong.
- **Observed problem:** all 294 cross-source entities would have been coloured as single-source.
- **Expected behavior:** `phase1-query-visualize.md` step 3c requires colouring by the whole source
  set and explicitly forbids first-source colouring.
- **Divergence:** the requirement exists in Module 7's prose but not in the reference
  implementation Module 3b builds from, so the defect is introduced two modules before the rule is
  stated, and survives unless the reader connects the two.

---

## Improvement: Module 7 embeds no screenshots of its own visualization app in the recap

**Date:** 2026-08-25
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — screenshot capture and embedding are defined by
`module-completion.md` and the Truth Set module's capture script; Module 7's flow has no equivalent
step.
**Upstream:** not applicable

### What happened

Truth Set visualization captures its six tabs, writes a `<name>-tabs.json` manifest, and embeds the
PNGs into its recap section. Graduation then verifies tab coverage against that manifest.

Module 7 builds a second, larger interactive app over the bootcamper's *own* resolved data — nine
tabs in this run — and captures nothing. At graduation the recap PDF carries six screenshots of the
demo Truth Set and none of the application built on the bootcamper's real results.

The coverage check passed (`6 of 6 captured tabs reached the recap`) because it measures against the
only manifest that exists. No manifest is written for Module 7's app, so its absence is not a
shortfall the check can see.

### Why it matters

The recap PDF is the keepsake and the artifact most likely to be shown to someone else. It currently
illustrates the bootcamp with pictures of the sample dataset while the bootcamper's own results —
their cross-source entities, their fraud leads — appear only as prose. That inverts which work was
theirs.

### Suggested fix

Have Module 7's visualization step run the same capture-and-embed path Truth Set visualization uses,
writing its own `<name>-tabs.json` so graduation's coverage check covers it too. The capture script
already takes the app's base name, so this is reuse rather than new machinery.

### Context when reported

- **Time:** 2026-08-25 14:25 CDT
- **Plugin version:** 0.5.2
- **Workstation:** macOS 26.6.2 (arm64)
- **Model / effort:** claude-opus-5 / effort not exposed in this session (Unknown)
- **Context size:** Unknown
- **Module / step:** `graduation`, Step 1a recap reconcile
- **Recent questions:** the graduation offer, accepted
- **Bootcamper responses:** yes
- **Behind the scenes:** `docs/visualizations/` holds `truthset_verification-*.png` (6) and
  `truthset_verification-tabs.json`, plus `entity_resolution.html` with no PNGs and no manifest.
- **Observed problem:** the keepsake shows the demo dataset, not the bootcamper's results.
- **Expected behavior:** `module-completion.md` makes embedding captured visualizations a required
  step for a module that produces one.
- **Divergence:** Module 7 produces a visualization but its phase files never invoke the capture
  step, so there is nothing for the embed to find and the omission is silent.

---

## Improvement: SZ_ENTITY_INCLUDE_ALL_RELATIONS is a composite Set, not an enum constant, and nothing says so

**Date:** 2026-08-25
**Module:** Query, Visualize and Discover
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — `get_sdk_reference(topic='flags')` returns composites and single flags in
the same shape, with `composite_members` the only distinction, and does not state that a composite
is a `Set<SzFlag>` in the Java binding rather than an `SzFlag`.
**Upstream:** not yet offered - the forward is offered once, batched with the feedback reminder at the end of graduation

### What happened

Building an explicit flag set for `getEntity` in Java, following the SDK reference's own production
guidance to request exactly the flags consumed rather than a `*_DEFAULT_FLAGS` composite:

```java
EnumSet.of(SzFlag.SZ_ENTITY_INCLUDE_ENTITY_NAME, ..., SzFlag.SZ_ENTITY_INCLUDE_ALL_RELATIONS)
```

fails to compile: `no suitable method found for of(SzFlag,SzFlag,SzFlag,SzFlag,Set<SzFlag>,...)`.
`SZ_ENTITY_INCLUDE_ALL_RELATIONS` is itself a `Set<SzFlag>` composite and must be added with
`addAll`, not listed among enum constants.

`get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_RECORD')` returns composites and
individual flags in the same JSON shape. `composite_members` is present on composites, which is the
only signal, and no field or note states the Java type difference.

### Why it matters

Small, and it costs one compile cycle — but it sits directly on the path the reference itself
recommends. The same response that says "request exactly the flags whose output you consume"
returns a list in which some entries cannot be used the way the others can, without saying which.
Anyone following that advice in Java hits it.

### Suggested fix

Note the binding type on composite entries — that in Java a composite is a `Set<SzFlag>` and must be
merged with `addAll` rather than passed to `EnumSet.of`. A single line on the composite rows would
do it.

### Context when reported

- **Time:** 2026-08-25 14:28 CDT
- **Plugin version:** 0.5.2 · MCP server as configured for this session
- **Workstation:** macOS 26.6.2 (arm64)
- **Model / effort:** claude-opus-5 / effort not exposed in this session (Unknown)
- **Context size:** Unknown
- **Module / step:** `query_visualize_discover`, building the entity evidence viewer
- **Recent questions:** none pending
- **Bootcamper responses:** n/a
- **Behind the scenes:** `get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_RECORD', language='java')`.
- **Observed problem:** compile error on an expression built directly from the reference's own list.
- **Expected behavior:** the reference distinguishes flags that can be listed together from those
  that cannot.
- **Divergence:** `composite_members` implies it for a reader who already knows the Java binding's
  representation; nothing states it.
