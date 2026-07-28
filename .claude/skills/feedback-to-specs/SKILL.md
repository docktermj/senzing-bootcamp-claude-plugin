---
name: feedback-to-specs
description: 'Analyze a Senzing Bootcamp plugin feedback file and turn it into one or more improvement specs under specs/, re-verifying every Senzing fact against the live Senzing MCP server first and reporting confirmed server-side defects upstream via submit_feedback. Use when the maintainer wants to process SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md, triage bootcamper feedback, or generate/refresh specs from collected feedback. Maintainer tool — not part of the bootcamper experience.'
---

# Feedback → Specs

This is a **maintainer** tool for developing the Senzing Bootcamp Claude Plugin
(SBCP). It reads a feedback file collected during bootcamps, analyzes and triages
each item against the codebase, the **live Senzing MCP server** and the existing
specs, and writes **one or more improvement specs** into `specs/`. It does **not**
implement the fixes — it turns raw feedback into actionable, deduplicated specs a
developer (or a follow-up session) can act on.

**Feedback is a snapshot; the server is not.** Every entry records how Senzing and
its MCP server behaved on the day it was written, and the server is released
independently of this plugin. So triage always re-asks the server before writing
(Step 4): a defect may already be fixed, a claim may have been wrong all along, or
the server may now contradict guidance the plugin still ships. Where the current
server is itself the defect, the finding goes back to Senzing (Step 7).

It is unrelated to the bootcamper-facing `/bootcamp-feedback` flow, which only
*captures* feedback. This skill *consumes* that captured feedback.

## Scope and guardrails

- **Write only under `specs/`.** Never modify plugin code, hooks, scripts, skills, or the feedback file itself. Generating specs is the deliverable; implementing them is a separate, later step. The single permitted action outside `specs/` is the upstream notification in Step 6 — an MCP call, not a file write, and gated on the maintainer's explicit yes.
- **Never invent feedback.** Every spec must trace to a real entry in the feedback file. If an entry is too vague to spec, mark it *needs clarification* rather than guessing.
- **Re-verify every Senzing fact against the live MCP server before writing a spec (Step 4).** Feedback is a snapshot of how the server behaved on the day it was filed, and the server ships independently of this plugin — so a spec written from the report alone can encode a defect that is already fixed, or miss that the server now contradicts the plugin. Never carry a Senzing fact from a feedback entry into a spec without re-asking the server (INV-080).
- **Deduplicate.** If an existing spec already covers a feedback item, do not create a second one. Note it as already-tracked (and optionally enrich the existing spec).
- **Respect the invariants.** Every generated spec references `@INVARIANTS.md` and must not propose anything that violates it (cross-platform Linux/macOS/Windows, language-agnostic, production-ready, consistent/coherent/complete). If feedback conflicts with an invariant, say so in the spec instead of silently overriding it.

## Step 1: Locate and read the feedback file

Resolve the feedback file in this order:

1. An explicit path the maintainer gave (argument or message).
2. `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` at the repo root.
3. `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` (a bootcamper project's file, if copied into the repo).

If more than one candidate exists and none was named, ask which to use. If none is
found, say so and stop — there is nothing to analyze.

Read the whole file.

## Step 2: Parse the feedback into discrete items

Feedback is usually a series of `## Improvement: <title>` blocks with subsections
(**What happened**, **Why it matters**, **Suggested fix**, **Context when
reported**), plus **Date**, **Module**, **Priority**, and **Source** lines. Handle
free-form prose too — bootcampers do not always follow the template.

For each item, extract: `title`, `symptom` (what happened, with any verbatim
error/output), `impact` (why it matters), `suggested_fix`, `priority`, `module`,
`date`, and `source`. Skip the file's header/placeholder sections (e.g. an empty
"Your Feedback" heading with no content).

**`Source:` — who noticed it.** Two values (absent means `bootcamper-reported`):

- **`bootcamper-reported`** — a human hit this and said so. It is real, felt
  friction: someone's experience was degraded enough that they stopped to report
  it. Weight impact accordingly.
- **`self-observed (assistant retrospective)`** — the graduation retrospective
  filed it. These skew toward the defect class a bootcamper *cannot* report:
  silently-wrong output, undocumented environment gotchas, tools behaving
  differently than documented. A bootcamper never files "the field name was wrong
  so the section rendered empty," because on screen that looks like no data.

Do **not** treat self-observed items as lower priority by default — they are
often more severe precisely because nobody would otherwise catch them. Do use the
distinction when a spec's `## Problem` needs to say who experienced what: attribute
bootcamper-reported items to the bootcamper's experience, and self-observed ones to
what the assistant hit, without implying a user complained. Record the value in the
spec's `## Source` block so the provenance survives into implementation.

## Step 3: Load triage context (do this before writing anything)

- **Read `specs/INVARIANTS.md`.** This is the ruleset every spec must respect.
- **List and skim every existing `specs/*.md`.** Record each spec's title and the problem it covers so you can deduplicate. (For example, a feedback item about the write-gate blocking `/tmp/` paths is already covered by `specs/PreToolUseWriteError.md`.)
- **Skim `specs/todo.md`** — the lightweight idea backlog, so you can route minor items there instead of into a full spec.

## Step 4: Re-verify every Senzing fact against the live MCP server

**Do this before analyzing, and before writing anything.** The Senzing MCP server is
versioned and released independently of this plugin, so an entry filed weeks or months
ago describes a server that may no longer behave that way. Three outcomes are all
common, and each changes the spec:

- **Still reproduces** → the spec stands, and now carries a current citation instead of
  a stale field report.
- **Fixed upstream** → do **not** write a spec proposing a plugin workaround for a
  defect the server no longer has. Record it as resolved-upstream in the triage table
  and, if the plugin carries a workaround added for it, spec the *removal* instead.
- **The server now contradicts the plugin** → the plugin is the thing that is wrong, and
  the spec's subject changes from "the server is broken" to "our guidance is stale".

Record the server version first — `get_capabilities` returns `server_info.server_version`
— so every claim you write can be dated and attributed. Then, for each item touching
Senzing behavior, re-ask the tool that owns the fact:

| The entry claims something about… | Re-ask |
|---|---|
| an SDK method, its arguments, or its response shape | `get_sdk_reference(topic='parameters' \| 'response_schemas', filter='<method>', language='<binding>')` |
| a flag, what it applies to, or what it returns | `get_sdk_reference(topic='flags', filter='<FLAG_NAME>')` |
| an attribute or mapping rule | `search_docs(query='…', category='data_mapping')` |
| an error code or its symptom | `explain_error_code('<SENZnnnn>')` |
| export, reporting, evaluation or graph behavior | `reporting_guide(topic='…')` |
| install, configuration or platform paths | `sdk_guide(topic='install' \| 'configure', platform='…')` |
| an example file or repository | `find_examples(...)` |

Rules for this step:

- **Ask the tool that owns the fact, not `search_docs` for everything.** A flag's
  `applies_to` is authoritative in `topic='flags'`; prose found by search is not.
- **Quote what the server returned** into the spec, rather than paraphrasing it. A future
  reader must be able to tell your claim from the server's.
- **A single field observation does not outrank the server, and the server does not
  outrank a reproducible observation.** When they disagree, say so plainly and record
  both with their conditions — flag set, SDK version, binding, platform (INV-169). Most
  "contradictions" turn out to be two different conditions, and a spec that flattens
  them into one absolute is the defect this repo has already had to retract twice.
- **Where the server cannot reach** (a field name below the shape `response_schemas`
  documents, a value only a live engine returns), say that explicitly and mark the fact
  as observation-only with its version and date — never launder it into an MCP-sourced
  claim (INV-080/INV-149).
- **If the network is unavailable**, do not guess and do not fall back to training data:
  write the spec with the fact marked "unverified — MCP unreachable at triage time" and
  say so in the report, so it can be re-checked before implementation.

## Step 5: Analyze each item (go beyond the feedback text)

For every parsed item:

1. **Classify** it: bug / false-positive, UX or wording, missing feature, invariant gap, documentation, or unclear.
2. **Confirm the root cause in the codebase**, don't just restate the report. Open the code the feedback implicates — `plugins/senzing-bootcamp/hooks/`, `scripts/`, `skills/`, `commands/` — and verify what actually causes the symptom. Cite `file:line`. If you cannot confirm it, label the root cause "Unverified — needs investigation" rather than asserting one.
3. **Reconcile the code against what Step 4 returned.** Where the plugin's text or code states a Senzing fact the server now answers differently, the plugin is the defect — even when the entry blamed the server, and even when the plugin's claim was correct when written. Check both directions: text the server contradicts, *and* a workaround the plugin still carries for a defect the server has since fixed.
4. **Decide the routing** — `plugin` or `mcp-server` — from what Step 4 established, not from what the entry guessed. An entry may be routed `mcp-server` and still need a plugin spec (our reference should record the confirmed shape), and one routed `plugin` may turn out to be a server defect worth reporting upstream (Step 6).
5. **Deduplicate** against existing specs (Step 3). Mark the item `already-tracked → specs/<file>.md` when covered.
6. **Group**: merge items that share one root cause or one fix into a single spec; keep unrelated items in separate specs. The number of specs per run is whatever the analysis warrants — one, several, or (if everything is already tracked or too vague) none.

## Step 6: Write the spec(s)

For each new spec, write `specs/<kebab-case-title>.md` using the template in
`spec-template.md` (in this skill's directory). Rules:

- **Pick a filename that does not collide** with an existing spec. Match the terse, developer-facing tone of the current specs.
- **Ground it in code.** Root cause cites real `file:line`; affected-files lists real paths.
- **Ground every Senzing fact in Step 4's result, with its provenance.** Name the tool and parameters that established it, the server version, and the date — e.g. "`get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_RECORD_JSON_DATA')` reports `applies_to: ["get_record"]` (server 1.32.1, verified 2026-07-28)". Where the entry and the server disagree, state both and which governs. Where the fact is observation-only, mark it so.
- **Say when the current server changed the spec.** If re-verification narrowed, widened, redirected or cancelled what the entry asked for, put that in the spec rather than silently writing the corrected version — the next reader needs to know the report and the spec differ, and why.
- **Make acceptance criteria observable and testable**, and always include a criterion that the change holds on Linux, macOS, and Windows and stays language-agnostic (the invariants). For a fact that only a live engine can confirm, say so in the criterion rather than writing one that cannot be run.
- **Link the source**: name the feedback file, the entry title, its date, module, and priority.

For minor items that don't warrant a full spec, propose a one-line addition to
`specs/todo.md` (append only) and ask before writing it.

## Step 7: Notify Senzing when the defect is theirs

An item belongs upstream when Step 4 confirms the **current** server is what is wrong —
a wrong or unobtainable documented path, a flag whose `applies_to` contradicts the
schema, a missing response shape, guidance that produces code the SDK rejects. A plugin
spec and an upstream report are not alternatives: file both when the plugin also needs to
record the confirmed behavior.

1. **Check the entry's `Upstream:` field first.** The bootcamper-facing feedback flow may
   already have sent it (`sent <date> via submit_feedback`), in which case do not
   re-file the same finding. A **follow-up** is worth sending only when you now have
   something the first submission lacked — that it still reproduces on a newer server
   version, or a confirmed field name/shape they can act on. Say in the message that it
   is a follow-up.
2. **Draft the message as a technical bug report Senzing can act on without context from
   this repo:** the tool and parameters called, what came back, what was expected, the
   contradiction (quote both sides), the server version and SDK version, and the impact
   in one line. Include a minimal reproduction.
3. **Strip everything identifying.** No bootcamper name, employer, email, file paths from
   their machine, host names, dataset contents, or record values — the MCP server's own
   notice forbids sending PII, and submissions are anonymous, so nothing in the message
   can be followed up with you. Describe data shape, never data.
4. **Show the maintainer the exact message and get an explicit yes before sending.** This
   is required by `submit_feedback` itself and is the only outward-facing action this
   skill takes; a decline costs nothing and the spec still stands. Then call
   `submit_feedback(category='bug', message='<the approved text>')` — `category='feature'`
   for a coverage gap that is a request rather than a defect.
5. **Record what happened** in the triage report: sent (with the date and category),
   declined, or already-filed. Note that the submission is anonymous, so no reply is
   possible — if the finding needs a conversation, it needs a channel other than this tool.

⛔ **Never send under `category='license_request'`.** That path takes personal details and
is for evaluation licenses only; a defect report there is both wrong and a PII leak
(INV-135).

## Step 8: Report the triage

Present a compact table so the maintainer sees every item's disposition, including
what the live server said about it:

| Feedback item | Classification | MCP re-check | Action |
|---|---|---|---|
| <title> | <bug/UX/feature/…> | still reproduces | New spec → `specs/<file>.md` |
| <title> | <…> | server now contradicts the plugin | New spec → `specs/<file>.md` (subject redirected) |
| <title> | <…> | fixed upstream | No spec — resolved on server <version> |
| <title> | <…> | n/a (no Senzing fact) | Already tracked → `specs/<file>.md` |
| <title> | unclear | not checked | Needs clarification |

State the server version every re-check ran against, once, above the table.

Then list the spec files created (as clickable `specs/<file>.md` paths), note
anything routed to `todo.md` or left for clarification, report each upstream
submission's outcome (sent / declined / already-filed), and offer next steps
(e.g. "I can implement `specs/<file>.md` next" or "want me to open the questions
for the unclear items?"). Do not start implementing unless asked.

**Call out anything the re-check changed.** If the current server narrowed, redirected or
cancelled what an entry asked for, say so in the report as well as in the spec — that is
the highest-value output of a triage run, and it is invisible if it only lives in a file
the maintainer has not opened yet.
