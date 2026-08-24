# Thirteen interaction-layer defects the phase-3 walk found from the preface through Module 1

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

> **Found by a `/dry-run` phase 3 walk, 2026-07-29** — the maintainer answering as the Bootcamper
> through: onboarding preface → Bootcamp preparation (all four gates) → Module 0 primer → questions
> invitation → quiz offer → the quiz itself. Choices: Core, `standard` verbosity, Python, Linux
> x86-64 detected, git initialized. These are the defects static analysis and phases 1–2 structurally
> cannot reach: four are prose that does not survive contact with the one-👉-per-turn rule or with the
> live MCP schemas, one is a content gap on the highest-traffic question in the bootcamp, two are
> behaviors the quiz rules never define, two are gaps in how the per-module apparatus (the
> model/effort nudge, the write-batching pattern) extends to a live session and to a second module,
> and two — found only because this walk continued into a real SDK install — are `generate_scaffold`
> defects confirmed by actually running the corrected calls against a live engine: a workflow
> mis-citation, and the same undeclared-parameter trap INV-160 already names for a sibling tool,
> recurring here unrecorded.
>
> **Items 5 through 13 were added mid-walk**, as the walk proceeded — which is the discipline this run
> also changed the dry-run skill to require: a finding held in conversation until the end is a finding
> risked on there being an end.
>
> They are grouped in one spec because each is a two-to-five-line edit in one of four files, and
> splitting thirteen small prose corrections into thirteen specs is bureaucracy. Each carries its own
> acceptance criteria and can be implemented and reverted independently.

## Problem

### 1. The preface has no answer for "how long will this take?" (Medium)

Asked at `onboarding-flow.md` step 4 — *"Do you have any questions before we get started?"* — which
is the preface's only question, making this close to the single most likely thing a Bootcamper says
at that point. The plugin has nothing for it:

- Step 3's overview covers goal, modules, licensing, the recap PDF, and terminology help. **No
  duration.**
- Step 4 gives no instruction for answering a duration question.
- **INV-096's estimate rule is per-module and module-start-only.** `ground-rules.md:416` places it
  "after the step overview and before the model/effort prompt" and explicitly exempts the setup
  modules. It never contemplates the preface.
- **No per-module figures exist to sum.** The module skills state the *requirement* to give an
  estimate, not values. The only number anywhere in the plugin is ground-rules' illustrative
  `"Roughly 15-30 minutes, depending on download/install speed"` — an example of the *form*.

So the guide must improvise a duration at exactly the moment INV-096 exists to stop it inventing
one. The walk's assistant applied INV-096's spirit by refusing a total and leaning on the resume
machinery — but that was a rule written for somewhere else, reached for under improvisation. A
different assistant plausibly answers "about 4–6 hours".

The honest answer is also genuinely conditional: the total depends on the Core-vs-Customized choice
the Bootcamper has **not yet made**, and on install/download speed.

### 2. Bootcamp preparation Step 4 routes a language lookup to a tool that cannot answer it (Low-Medium)

`bootcamp-preparation/SKILL.md:248-249`: *"Call `get_capabilities` or `sdk_guide` on the Senzing MCP
server for the supported programming languages on that platform."* Verified against the live server
(1.32.2, 2026-07-29):

- `sdk_guide(topic='install', platform='linux_apt')` returns platform install detail — commands, env
  vars, default paths, gotchas. **No language list.**
- `sdk_guide(topic='install')` with no platform returns the **platform** decision tree, not a
  language one.

The language set lives in `get_capabilities`, and in the server's model it is
**platform-independent**: Python, Java and C# official; Rust and TypeScript/Node.js
community-maintained wrappers. What varies per platform is the install *mechanism* — which this same
step already tells the guide not to invent, deferring it to Module 2's routing rules and to
`sdk_guide(topic='install', platform=…, language=…)` at the point of need.

So "on that platform" mis-frames the fact: there is no per-platform language list to fetch. The one
genuine platform↔language constraint the server does state sits in the platform decision tree —
`docker` is the *"Fallback for Intel Mac, Windows without Scoop, or Python on macOS/Windows (the
Python SDK is only supported on Linux)"* — and is reachable without a platform argument.

This is the same class as the Truth Set finding fixed in `7683d61`: a documented step naming a call
that does not do what the step says.

### 3. Module 0's "re-present" plus a pinned wording produces a literal repeat (Low)

`module-00-entity-resolution-concepts/SKILL.md:46` instructs: answer the Bootcamper's question via
`search_docs`, verified with a second confirming call, *"then re-present"* the pinned 👉 — whose
wording INV-056 fixes verbatim:

> 👉 **Do you have any questions about entity resolution before we continue?**

So immediately after the Bootcamper has asked something and had it answered, the guide asks the
identical string again, which reads as though their question did not register.

**The preface solves this same situation the other way.** `onboarding-flow.md:139-140` says *"ask
once more whether they have **other** questions"*. Module 0 cannot do that without paraphrasing a
pinned string, so two files handle one conversational case incompatibly and Module 0's version is the
one that reads worse.

Narrower than it first appears: `concepts.md:83-85` deliberately stops this loop leaking into the
readiness gate, so the repeat is bounded to within the invitation.

### 4. Step 3's instruction order cannot be followed as written (Low)

`bootcamp-preparation/SKILL.md:179-200` sequences the verbosity step as: *"Wait for the answer, then
**hold** the chosen verbosity…"* → the yaml → *"Tell them they can change it any time… This is not a
⛔ gate, but it is still a 👉 question the bootcamper answers: wait for their reply."*

Followed literally, "tell them they can change it any time" lands **after** the answer, when it can
no longer inform the choice. Followed usefully, it must precede the question — because INV-005
requires the 👉 to end the turn, so nothing may follow it. Re-stating "wait for their reply" *after*
the tell is what makes the ordering read as if both were possible.

### 5. Module 0's quiz has no wrong-answer guidance (Low-Medium)

`concepts.md`'s quiz rules specify difficulty ("start at moderate, not the easiest tier"), sourcing
(every question and its correct answer MCP-sourced and verified), count (about 3–5), one 👉 per turn,
the exit path, and the wrap-up. On evaluating a reply it says only: *"evaluating the bootcamper's
answer each turn before asking the next."*

**Nothing says what to do when the answer is wrong** — and in a module whose stated purpose is to
"reinforce the concepts and drive curiosity", the wrong answer is the highest-value moment in the
whole quiz. Undefined: whether to state plainly that it was wrong, whether to re-teach the concept or
just give the right letter, whether to re-ask or move on, and whether a miss should change the
difficulty of what follows.

Observed in the walk: the Bootcamper answered question 2 incorrectly, and the guide had to invent the
whole correction shape. It chose to name the answer as wrong, explain *why* the chosen option was
wrong (it described the contrasting method), and re-teach the concept before moving on — a reasonable
choice, but a choice with no support in the file. A guide optimizing for encouragement could as
easily produce "good thinking!" followed by the right answer and no re-teaching, which is the failure
mode a learning module can least afford.

### 6. The quiz's answer shape is undefined (Low)

The same rules never say what form a quiz answer takes. A quiz item is a 👉 question, so INV-051
applies the moment options exist ("every 👉 question that offers two or more choices MUST use a
neutral lead question followed by a numbered list"), and INV-008 frames questions around yes/no
answerability. But an open-ended item — "explain why principle-based matching beats hand-written
rules" — is a legitimate conceptual quiz question that is neither yes/no nor a numbered list.

The walk used numbered options for every item, which is the compliant reading and makes evaluation
unambiguous. But the file permits the open-ended form by silence, and a guide taking it would be
producing 👉 questions that sit outside both INV-051's and INV-008's shapes.

### 7. A missed `search_docs` query is indistinguishable from thin documentation (Low)

`concepts.md` supplies five suggested queries for the primer's material, which is good practice and
exists precisely because BM25 phrasing matters. What it does not say is **prefer them**, or what to do
when a query returns nothing relevant.

Observed in the walk: sourcing the final quiz item, the guide invented the query *"principles versus
rules brittle maintenance ingest new data sources without experts"* instead of using the supplied
*"Senzing principle-based entity resolution approach"*. It missed completely — BM25 latched onto "data
sources" and "ingest" and returned record-loading snippets and `add_record` flags. Re-querying with the
documentation's own phrasing returned the material immediately, from two independent sources.

The hazard is the failure's *shape*, not the extra call: **a query that misses looks exactly like
documentation that does not cover the topic.** The honest-seeming conclusion is "the docs are silent",
which under INV-080 leaves the guide with nothing to say — or, worse, tempts a fallback to training
data on the grounds that MCP "had no answer". A guide under context pressure will not reliably
distinguish a bad query from a real gap.

One line fixes it: prefer the suggested queries, and when a query returns nothing relevant, re-query
with the documentation's own phrasing before concluding the material is not covered. Scoped here to
`concepts.md` because that is where the suggested-query list lives, but the reasoning generalizes to
every skill that reaches for `search_docs`.

### 8. INV-138's fallback resolves the current model/effort setting as one unit, but the two dials are independently determinable (Low-Medium)

INV-138 compares the stage's recommendation against "the model and reasoning effort the Bootcamper is
**currently running**", with the previous stage's row as "a fallback used ONLY where the current
setting cannot be determined." It treats *the current setting* as one thing to determine or not.

In a live session it is not one thing. The **model** in use is knowable to the assistant; the
**reasoning effort** is not exposed anywhere and cannot be determined by any means available this
session. So the two dials sit in different epistemic states at the same moment: model — determined,
compare directly; effort — undeterminable, fall back to the previous stage's row.

Observed at the Module 1 start nudge (turn 16): the Bootcamper was on Opus 5 (determinable, differs
from the recommended Sonnet 5 → correctly asked) at an effort level this session could not read
(undeterminable → correctly fell back to the previous stage's recommendation, medium, which matched
the current stage's recommendation → correctly not asked). The per-dial resolution produced the right
outcome, but INV-138's text never sanctions resolving the fallback **per dial** — read as an
all-or-nothing comparison of "the current setting," it would need model and effort to be either both
determinable or both not, and applying the previous-stage row to the *model* dial (which was in fact
determinable) would have found Sonnet 5 unchanged and suppressed the switch offer entirely — silently
defeating the purpose of the invariant it superseded, for a Bootcamper who is demonstrably on a
different model.

This is INV-137/138's own "model and effort are **separate dials**" principle, just not carried into
the fallback clause that determines whether to ask about them.

### 9. Module 1 Phase 2 Step 10a has no write-batching instruction, unlike the pattern it echoes (Low)

Step 10a asks two pinned questions — software integration, then deployment target — and instructs
"persist the answers to `config/bootcamp_preferences.yaml`" per question, with no "hold for a single
write" language. Bootcamp preparation's Steps 1–5 are explicit that their answers are *held* and
written once, consolidated, in Step 6 (INV-058) — precisely so the Bootcamper does not watch one
config diff per gate. Step 10a has no equivalent instruction, so a literal reading writes the
preferences file twice across the pair (once after the integration answer, once after the deployment
answer), which is the same one-write-per-gate pattern INV-058 exists to prevent, just in a different
module capturing different preferences.

Narrower than INV-058 itself — that invariant governs Bootcamp preparation's setup writes specifically
— so this is a gap in scope rather than a defect in the existing rule: nothing in Step 10a or in
ground-rules' general write-discipline section extends the batching reasoning to Module 1's own
preference writes.

### 10. Module 2 Step 4 names the wrong `generate_scaffold` workflow for what it asks for (Medium)

`module-02-sdk-setup/SKILL.md`, Step 4 (Verify Installation): *"Generate a verification script...
using `generate_scaffold(language='<chosen_language>', workflow='initialize', version='current')`.
**The script should initialize the Senzing engine and print the version** to confirm the SDK is
working."*

Verified live against the server (1.32.2, 2026-07-29) and against the actual, running SDK on this
machine (v4.3.3): `generate_scaffold(language='python', workflow='initialize')` returns
factory/engine-**lifecycle** snippets only — `abstract_factory.py`, `engine_priming.py`,
`purge_repository.py`, `factory_destroy.py`, `signal_handler.py`, and three more. **None of them
prints the version.** The version-printing snippet — `python/information/get_version.py`, which
calls `SzProduct.get_version()` — lives under a **different** workflow entirely:
`generate_scaffold(language='python', workflow='information')`.

So Step 4's single named call cannot produce what the step asks for. A guide following it literally
gets engine-lifecycle code with no version print, and has to either invent the missing half (a
training-data risk INV-080 forbids) or discover on its own — unprompted by this step — that a second
call with a different `workflow` value is needed.

**This is the same defect class the plugin has already caught and fixed once, one step later.** Step
8a carries exactly this warning for a different need: *"`generate_scaffold(workflow='initialize')`
does not do this. Its snippets cover factory and environment lifecycle... Use it for Step 9's
connection test; use `init_default_config` for seeding."* Step 9, in turn, correctly cites
`workflow='initialize'` for its own need (creating and exercising an `SzEngine`), which the
lifecycle snippets *do* provide. So the plugin has, in the same file, one correct use of this
workflow (Step 9), one previously-broken use that was fixed with a warning (Step 8a), and one
still-broken use that was never checked (Step 4) — the general lesson ("check what a workflow's
snippets actually contain before citing it for a specific need") was captured as a fact about
seeding, not as a rule, so it didn't generalize to the next citation of the same workflow.

Confirmed by actually running it: a script written against `SzProduct.get_version()` (the real
signature, confirmed via `get_sdk_reference(topic='methods', filter='get_version', language='python')`
→ `get_version() -> str`, no arguments) initialized against the live engine and printed
`Senzing SDK version: 4.3.3`. The fix is not hypothetical — the corrected call produces working code
on the first try.

### 11. `generate_scaffold` never inlines code, and its own response advertises an undeclared `inline` parameter — the same INV-160 trap in a sibling tool (Medium)

Module 3 Steps 3 and 4 (and Module 2 Steps 4 and 9) instruct: call `generate_scaffold(...)`, then
**"save the generated code"** to a file — phrased as though the tool returns code directly.

Verified live, twice, against the running server (1.32.2, 2026-07-29): `generate_scaffold` —
unlike `sdk_guide`, which always inlines a `code.code` string — returns only a **snippet listing**:
`file_path`, `source_url`, `raw_url`, `size_bytes`, `line_count` per file, no code text. Its own
`access_steps` field says to `fetch` the `raw_url`, and step 3 of those same `access_steps` says,
verbatim: *"Last resort: call again with workflow='full_pipeline', language='python',
version='current', **inline=true**"*. **`generate_scaffold`'s declared JSON schema has no `inline`
parameter at all** — only `language`, `version`, and `workflow` — so that last-resort call is not
merely undesirable, it is not a real option: passing it would either be silently ignored or
rejected, and a caller who tries it learns nothing about why.

**This is INV-160's exact shape, in a different tool.** INV-160 was written narrowly — for
`find_examples` file retrieval advertising `inline=true` when that tool's own schema doesn't declare
it either. The rule that survives that finding (*"An undeclared parameter MUST NOT be adopted as the
remedy even when the response's own prose advertises one — only parameters the live schema declares
may be passed"*) is general, but it was recorded and enforced against one tool. The same defect
class exists, unrecorded, in `generate_scaffold`.

**Confirmed reachable and confirmed fixable, not merely theoretical.** `access_steps`' *first*
option — `fetch` the `raw_url` — does work: `WebFetch` against
`raw.githubusercontent.com/senzing/code-snippets-v4/...` returned real, runnable source both times
it was tried this walk (`abstract_factory.py`, `add_records.py`). So the tool's own fallback chain
degrades gracefully to a working option; the defect is that **the plugin's module steps never
mention needing it**. A guide following Step 3/4 literally, without independently realizing a
second fetch is required, has three ways to go wrong: stall waiting for code that never arrives
inline, try the undeclared `inline=true` and get nothing back, or — worst — reconstruct the code
from memory of "what a scaffold like this usually looks like," which is exactly the training-data
fallback INV-080 forbids.

**A second problem in the same steps, and this one is not merely cosmetic — it was reproduced
live.** `workflow='full_pipeline'` returned **16 separate files** (initialization, loading,
searching), not the one script Step 4's phrasing implies ("save **the** generated code to
`verify_pipeline.[ext]`" — singular). Step 4's own structural validation (non-whitespace content,
one structural element) is satisfiable from *any* file in that set, so a guide has no signal telling
it picked the wrong one — and picking wrong breaks a **later** step, not Step 4 itself.

Concretely: `python/loading/add_records.py` is a self-contained demo — five hardcoded `RECORDS`,
no file input. `python/loading/add_records_loop.py` is a general-purpose loader — it opens
`INPUT_FILE` and iterates it line by line. Both satisfy Step 4's bar equally. But Step 6 says
*"Execute the generated `verify_pipeline.[ext]` script... pointing it at
`src/system_verification/verification_data.jsonl`"* — an instruction that presupposes the
file-reading shape. Saving `add_records.py` as `verify_pipeline.py` at Step 4 (the natural first
pick — it is the first "loading" file in the returned list) satisfies Step 4 and then makes Step 6
**impossible to satisfy without rewriting the file**, because there is no file argument to "point"
at: the records are hardcoded in the source. Reproduced this walk: Step 4 was completed with
`add_records.py`, and Step 6 could not proceed until the file was swapped for
`add_records_loop.py` (fetched via the same `access_steps` path) and its hardcoded
`INPUT_FILE = Path("../../resources/data/load-500.jsonl")` was overridden to the synthetic data
path — otherwise Step 6 either loads the wrong five demo records or crashes on a path that does not
exist in the project. Once swapped, the corrected script loaded all 4 synthetic records with 0
errors, exit 0 — confirming the fix, not just the diagnosis.

### 12. Module 4 re-asks a data-provision question Module 1's generated scenario already answered (Medium)

Module 1's Business Case Offer (`phase1-discovery.md` Step 4, option 3 — *"I don't have my own
data — generate a scenario for me"*) is a fully supported, documented path: on acceptance it names
real, CORD-backed data sources, records `provenance: cord` for each in
`config/data_sources.yaml`, and writes them into `docs/business_problem.md` with a `🤖
Bootcamp-generated business case` marker.

Module 4 Step 2 has no branch that recognizes this. It opens every source with the pinned
question *"How would you like to provide the data for this source?"* — five options: upload,
URL/path, database, API, or *"I don't have my own data — generate/synthesize it for me"* — with
no check for whether Module 1 already answered this for all of the Bootcamper's sources. Neither
`SKILL.md` nor `phase1-discovery.md` cross-references the other's handling of a generated
scenario: grep for "Business Case Offer" or "generated scenario" in Module 4's file returns
nothing.

Reproduced live: with a Business-Case-Offer scenario naming six real Moscow CORD sources
(GLEIF, ICIJ, NominoData, OFAC, Open Ownership, OpenSanctions, provenance `cord`, already in
`config/data_sources.yaml`), Module 4 Step 2 would ask, once per source, a question whose honest
answer is "you already told me this in Module 1." Option 5 restates a decision already made rather
than asking anything new about *that* source — it is not a textually identical question, so it
escapes a literal INV-006 violation, but it re-litigates the same decision six times over.

This is a seam defect: both modules are internally coherent, and the gap only appears when a
Bootcamper who took the generated-scenario path in Module 1 reaches Module 4's per-source loop.

### 13. `database_type` is read by two modules and written by none (Medium)

Module 4 Step 8b's SQLite load-time warning fires only when *"the database is SQLite **and** the
collected total is above the load-time threshold"*, and its stated read is: *"Read... `database_type`
from `config/bootcamp_preferences.yaml`."* Module 6's `phaseA-build-loading.md:278` separately reads
the same key for its own SQLite heads-up.

**No step anywhere in the plugin writes `database_type` to `config/bootcamp_preferences.yaml`.**
Grepped the whole skills tree: the two reads above are the only occurrences of the string in the
entire plugin. Module 2 Step 7 — the step where SQLite vs. PostgreSQL is actually chosen — checkpoints
to `config/bootcamp_progress.json` with **no specified JSON shape at all** (*"Checkpoint: write step 7
to `config/bootcamp_progress.json`"*, no key names given), so there is nothing for a later reader to
even fall back to under a different name.

The practical consequence: followed literally, Step 8b's own instruction — *"If the registry cannot
be read or parsed, treat the total as indeterminate: do not fail"* — is the closest applicable branch
for a missing `database_type` too, and *"indeterminate... any non-SQLite engine... say nothing about
load time"* collapses to the same outcome. **The warning can never fire**, regardless of database
choice or dataset size, because the one fact its trigger condition depends on has no writer.

Reproduced live: this walk chose SQLite in Module 2 Step 7, collected 26,308 records in Module 4 —
exactly the scenario this warning exists for — and reached Step 8b with `database_type` absent from
`config/bootcamp_preferences.yaml` (Module 2 recorded the choice under an ad hoc shape in
`bootcamp_progress.json` instead, since Step 7 names no schema). Module 6's copy of the same read
fails identically when that module is reached.

## Root cause

Items 1, 3 and 4 are all **prose written without the one-👉-per-turn constraint in view**: an
overview that never anticipated the question its own gate invites; a "re-present" verb that assumes
paraphrase is available when INV-056 forbids it; a step whose narrative order puts an
answer-informing sentence after the answer. Item 2 is **MCP routing imprecision** — a tool named for
a fact it does not carry, with a platform qualifier the server's model does not apply to that fact.

None of the four is detectable by reading the plugin against itself, which is why 937 tests and four
static audits missed them: each requires either a live schema call (item 2) or an actual
conversational turn (items 1, 3, 4).

## Proposed change

1. **Give the preface a duration answer.** Add one line to step 3's overview: the bootcamp is
   module-sized, each module states its own estimate at its start, and the total depends on the
   Core-vs-Customized choice and on install/download speed. Add a step-4 note that a duration
   question is answered that way and **never** with an invented total — citing INV-096's
   no-fabricated-number rule as the reason. Mention that progress is saved and the bootcamp can be
   resumed across sittings (INV-059/INV-094), which is the genuinely useful part of the answer.
2. **Fix the language-lookup routing.** In Step 4, name `get_capabilities` as the call for the
   supported programming languages, drop `sdk_guide` from that sentence, and state that the language
   set is platform-independent while the install mechanism is not. Keep the existing per-platform
   annotation rules and the existing prohibition on inventing install detail — both are correct.
3. **Pin a follow-up variant for the re-present.** Add a second pinned question to `concepts.md` for
   use after a question has been answered — e.g. *"Do you have any other questions about entity
   resolution before we continue?"* — and have `SKILL.md:46` name it, so the re-present satisfies
   INV-056 without repeating the first-ask wording verbatim. Do not loosen INV-056.
4. **Reorder Step 3's changeability note** so it precedes the question: "Before asking, tell them
   they can change it any time."

## Acceptance criteria

- [ ] Step 3's overview states that the bootcamp is module-sized, that each module estimates itself,
      and that the total depends on path and install/download speed.
- [ ] Step 4 instructs that a duration question is answered without a fabricated total, and says
      progress is saved across sittings.
- [ ] `bootcamp-preparation/SKILL.md` no longer routes a supported-programming-languages lookup to
      `sdk_guide`, and states that the language set is platform-independent.
- [ ] The existing per-platform annotation rules and the do-not-invent-install-detail prohibition are
      unchanged.
- [ ] `concepts.md` pins a follow-up ("other questions") variant, and `module-00/SKILL.md`'s
      re-present instruction names it rather than the first-ask wording.
- [ ] Module 0's first-ask wording is unchanged, and the gate still does not re-issue the invitation
      (`concepts.md:83-85` preserved).
- [ ] Step 3's changeability note precedes its 👉 question.
- [ ] `concepts.md`'s quiz rules say what to do with an incorrect answer: name it as incorrect
      without false praise, re-teach the concept rather than only giving the right option, and state
      whether to move on or re-ask.
- [ ] `concepts.md` states the quiz's answer shape — numbered options, so INV-051 and INV-008 both
      apply cleanly — or explicitly sanctions the open-ended form and says how it satisfies them.
- [ ] `concepts.md` says to prefer its suggested queries, and to re-query with the documentation's own
      phrasing before concluding `search_docs` does not cover the material.
- [ ] INV-138's fallback clause states explicitly that "cannot be determined" is evaluated **per
      dial** (model, effort), not for the setting as a whole — so a determinable model is compared
      directly even when effort is not, and vice versa.
- [ ] Module 1 Phase 2 Step 10a either batches its two preference writes into one, or states
      explicitly why it does not need to (e.g. the two answers are asked far enough apart, or the
      writes are cheap enough, that INV-058's reasoning does not transfer) — a decision, not a
      silent gap.
- [ ] Module 2 Step 4 names `generate_scaffold(workflow='information')` (or an additional call to
      it) for the version-print half of its verification script, alongside `workflow='initialize'`
      for the engine half — and a test asserts a script built from Step 4's instructions actually
      contains a call reachable to `get_version`.
- [ ] Every step that calls `generate_scaffold` and expects to save code states that the response is
      a **listing** requiring a follow-up `fetch` of each file's `raw_url`, and none of them
      instructs (or permits) passing `inline=true` — a test asserts no skill passes an undeclared
      parameter to `generate_scaffold` or `find_examples`.
- [ ] Module 2 Step 7 writes `database_type` (`sqlite` or `postgresql`) to
      `config/bootcamp_preferences.yaml` as part of its checkpoint, and Module 4 Step 8b /
      Module 6's `phaseA-build-loading.md` both read that same key successfully — a test asserts
      the write and both reads use identical key names.
- [ ] Module 4 Step 2 checks whether the current source's provenance is already `cord` (or
      otherwise already resolved) in `config/data_sources.yaml` from a Module 1 Business Case
      Offer, and if so proceeds straight to collecting/downloading that source rather than asking
      the five-option provision question again.
- [ ] Module 3 Step 4 (and any step citing `workflow='full_pipeline'`) names which file to save —
      specifically the **file-reading** loader (`add_records_loop.py`-shaped, not the hardcoded
      `add_records.py` demo) — since Step 6 presupposes a script that takes a data-file path, and a
      test confirms a script built from Step 4's instructions actually reads an external file rather
      than hardcoding records.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): all four
      are interaction prose and MCP routing, independent of platform and of the Bootcamper's chosen
      programming language.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — step 3 overview, step 4
  note (item 1).
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — `:248-249` (item 2),
  `:179-200` (item 4).
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md` — `:46` (item 3).
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md` — the pinned
  follow-up variant (item 3), the wrong-answer and answer-shape rules (items 5, 6), the prefer-the-
  suggested-queries rule (item 7).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — INV-138's per-dial fallback
  clause (item 8).
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — Step 10a's
  write-batching decision (item 9).
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 4's `generate_scaffold`
  workflow citation (item 10), Steps 4/9's "save the generated code" framing (item 11).
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — Steps 3
  and 4's `generate_scaffold` framing (item 11).
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — Step 2's per-source
  provisioning question (item 12), Step 8b's `database_type` read (item 13).
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 7's unspecified checkpoint
  shape (item 13).
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — the same
  `database_type` read (item 13).
- `tests/` — items 1, 2 and 3 are assertable; item 4 is a prose-order fix whose test would be
  brittle, so fix it without one and say so.

## Source

- Dry run phase 3, 2026-07-29, maintainer answering as the Bootcamper. `Source: self-observed
  (assistant retrospective)`; `Routing: plugin`; `Upstream: not applicable`.
- Priority: Medium (items 1, 10, 11, 12 and 13); Low-Medium (items 2, 5 and 8); Low (items 3, 4, 6, 7 and 9)
- MCP re-check: **server 1.32.2**, 2026-07-29 — item 2's claim established live by calling both
  `sdk_guide` shapes and observing neither returns a language list; item 10's claim established live
  by calling `generate_scaffold` with both `workflow='initialize'` and `workflow='information'` and
  observing the version-print snippet sits only under the latter, then confirmed further by running
  a corrected script against a real Senzing 4.3.3 installation on this machine (printed
  `Senzing SDK version: 4.3.3`, exit 0). Items 1, 3, 4, 8 and 9 assert no Senzing fact. Items 5, 6 and
  7 concern the quiz's MCP-sourcing discipline but assert no fact of their own. Note the server moved
  1.32.1 → 1.32.2 *during* this session, and the doc index rebuilt (13,884 → 13,899 documents), so
  re-verify item 2 rather than trusting this note.
- Upstream: not applicable — all four are plugin-side.
- Related specs: `specs/dry-run-mcp-call-contracts.md` (INV-136 — item 2 is the same class),
  `specs/module-preface-time-estimate.md` (INV-096 — item 1 is the gap its per-module rule leaves),
  `specs/onboarding-explore-gate-wording.md` (INV-056 — the pinning item 3 must not loosen),
  `specs/guarantee-quiz-offer-is-presented.md` (INV-112 — items 5 and 6 concern the quiz that
  invariant guarantees is *offered*; it says nothing about how the quiz then behaves)

## Also observed, needing no change

- **The originating dry run's canonical unsatisfiable-rule finding is fixed and works.**
  `ground-rules.md:60-65` carves out the contentless answer and states outright that the requirement
  "is unsatisfiable as literally written" for a bare readiness signal. Exercised three times in this
  walk; correct each time.
- **INV-058 held:** two writes total (one per file) after four answered gates. The walk cannot check
  write *noise* — writes went via `Bash` — only the count.
- **Step 6's ⛔ self-check earns its place:** it asserted eleven tokens with
  `entity_resolution_concepts` present, the guard against the derivation that once silently dropped
  the primer from a Core run.
- **INV-112, INV-075/078, INV-056, INV-061/134, INV-095** all verified correct in the walk; see the
  `IMPLEMENTED.md` entry for the itemized list.
- **INV-080 held under pressure** on a general question ("is entity resolution known by other
  names?") where training data felt sufficient — the rule produced *added* precision (record linkage
  1946, Christen 2012, survivorship framing, and the MDM-is-not-a-synonym distinction).

## Deviations from this spec, and why (2026-07-29)

- **Implemented against the acceptance criteria, because `## Proposed change` covers only items
  1-4.** Items 5-13 were added mid-walk (the spec's own header says so) and never got proposed
  changes, a root-cause paragraph, or affected-file notes; the closing criterion still reads *"all
  four are interaction prose"*. The 17 acceptance criteria are complete and were treated as the
  contract. Nothing in the spec was edited to reconcile this — correcting spec content is
  `feedback-to-specs`' job.
- **Done in two passes, at the maintainer's direction:** items 2, 10, 11, 12, 13 (MCP-gated and
  Medium) first, then 1, 3-9 (interaction prose). The spec notes the items are independently
  revertable, which is what made the split safe.
- **Item 2 re-verified rather than trusted, as the spec instructed.** It still holds on 1.32.2:
  `sdk_guide(topic='install', platform='linux_apt')` returns install commands, env vars, default
  paths, gotchas and direct-download packages — and **no language list at all**.
- **Item 11b: the file count differs from the spec.** It says `workflow='full_pipeline'` returned
  "16 separate files"; on server 1.32.2 (2026-07-29) it returns **18** for Python — ten
  `initialization/*`, six `loading/*`, two `searching/*`. Both files the spec names are present
  (`loading/add_records.py` hardcoded, `loading/add_records_loop.py` file-reading), so the finding
  stands; only the count moved. The implemented text cites 18 with its date.
- **Item 11b gained a stronger justification than the spec had.** `full_pipeline`'s response carries
  its own `anti_patterns`, and two apply directly at severity **`error`**: *"Hardcoded John Doe /
  TEST / 1001 records"* → *"Records read line-by-line from JSONL"*, and
  *"/opt/senzing/er/testdata/truth-sets/..."* → *"User's input_file"*. So picking the hardcoded demo
  violates **Senzing's own stated anti-pattern for that workflow**, not merely Module 3's later step.
  That is now the citation the guidance leads with.
- **Item 8 required amending an existing invariant's text and one existing test.** INV-138's fallback
  clause in `ground-rules.md` was reworded per-dial with the maintainer's explicit approval of the
  wording. `tests/test_model_guidance_behavior.py::test_the_previous_stage_is_only_a_fallback` pinned
  the superseded phrase *"only when the current setting cannot be determined"*; its regex was updated
  to the new phrasing and its docstring records why, and a new
  `test_the_fallback_is_resolved_per_dial` pins the half the old wording left unsanctioned. The
  test's **intent** — previous stage is a fallback, never the primary rule — is unchanged.
- **Item 9 was a decision, and the decision was to batch.** The criterion allowed either batching or
  documenting why INV-058's reasoning does not transfer. It transfers: same file, same
  bootcamper-visible write noise, and the two questions are consecutive turns inside one numbered
  step (three when the integration follow-up fires). Step 10a now holds both answers and writes once
  at its checkpoint, and says why the scope gap is a gap rather than a violation.
- **Item 4 is fixed without a precise test, as the spec directed.** Its assertion checks only that
  the reassurance precedes the 👉 question and that the reason is stated; pinning prose *order* more
  tightly would break on any rewording.
- ⚠️ **A working-tree accident during pass 1, recorded because it cost real work.** A mutation-test
  backup keyed on `$(basename)` collided — `module-02-sdk-setup/SKILL.md` and
  `bootcamp-preparation/SKILL.md` are both named `SKILL.md` — and the restore wrote preparation's
  content into module-02, clobbering a shipped skill file. Caught in the diff stat (1138 changed
  lines), restored from `HEAD`, and the two module-02 edits were redone. Net damage nil, but only
  because `HEAD` was clean.
