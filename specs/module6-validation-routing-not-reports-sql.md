# Module 6 routes validation to `reporting_guide` without naming a topic, and `reports` is a dead end

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

> **⚠️ Subject redirected by re-verification (2026-07-28).** The feedback entry framed this as an MCP
> defect — that `reporting_guide` fails to say its SQL assumes a separately-built data mart. The
> current server **does** say exactly that, unprompted. What survives is a plugin-side routing
> imprecision. See [What the re-check changed](#what-the-re-check-changed). Relevant because the entry
> records `Upstream: submitted 2026-07-28`, so a report was sent containing a claim the server refutes.

## Problem

Module 6 sends post-load counts and statistics to `reporting_guide`, and the ground rules forbid direct
SQL against `database/G2C.db`. A bootcamper following that routing called
`reporting_guide(topic='reports')` and received SQL querying `sz_dm_record`, `sz_dm_entity`,
`sz_dm_relation` and `sz_dm_report` — an analytical data mart the bootcamp never builds.

So the sanctioned route for the load module's validation step returned queries that cannot run against
anything in the workspace. Validation was instead built from SDK calls (one `getEntity` per loaded
record), which works and honors the no-SQL rule — but that is not what the module points at.

A bootcamper following the routing literally reaches the validation step and has no obvious next move:
the tool answered, the answer is well-formed, and it is unusable against a single-database evaluation
setup.

## Root cause

**The plugin's routing names the tool but not the topic.** `module-06-data-processing/SKILL.md:63` and
`phaseD-validation.md:6` say counts and stats come from `reporting_guide`, and `:34` repeats
"(`reporting_guide` for counts.)" — with no topic. Elsewhere the same file *is* specific:
`topic='graph'` (`:49`), `topic='evaluation'` (`:66`, `:191`, `:214`) and `topic='quality'` (`:67`,
`:175`). So the two references that matter for counts are the vague ones, and `topic='reports'` is the
name a reader would pick for "counts and statistics".

**`topic='reports'` is genuinely the wrong topic for this workspace** — but not because the server
hides that. Verified on server 1.32.1, 2026-07-28, `reporting_guide(topic='reports', scale='small')`
returns its schema with this description, unprompted:

> **IMPORTANT: These tables are NOT part of the Senzing SDK and do NOT exist out of the box. They must
> be created and maintained by a separate data mart replication pipeline that YOU build and operate.**
> … Building this pipeline requires: consuming INFO messages from every SDK write operation
> (addRecord, deleteRecord, reevaluateRecord, reevaluateEntity, processRedo), implementing entity
> refresh with hash-based change detection, computing deltas, and aggregating report statistics.

It also carries an anti-pattern stating SQLite is "suitable for POC and development only". And not all
of its SQL targets the data mart: several `Validation:` patterns run against **exported entity JSON**
(`json_each(exported_entities)`, "Run this against exported entity JSON", "Run against the export
output, not the raw database") — which the bootcamp does produce.

So the server is candid about the prerequisite and does offer export-based patterns. The residual
problem is that the data-mart SQL **dominates** the response, and the plugin sent the reader there
without saying which topic answers the bootcamp's question.

## Proposed change

1. **Name the topic wherever Module 6 routes counts and statistics.** Replace the bare
   `reporting_guide` references at `SKILL.md:63`, `phaseD-validation.md:6` and `:34` with the topics
   that answer the question in this workspace — `topic='evaluation'` for the single-pass export
   statistics the module actually needs, and `topic='export'` for extraction patterns.
2. **Say what `topic='reports'` is for, rather than leaving it to be discovered.** One line: its SQL
   targets a data mart you build and operate separately (the tool says so in its own schema notes), so
   it is the production-reporting answer, not the bootcamp's. This turns a dead end into a signpost —
   and the tool's own text backs it, so nothing is asserted on the plugin's authority.
3. **Point at the export-based `Validation:` patterns** in that response as the usable subset if a
   reader is already there, so "wrong topic" does not read as "nothing here is usable".
4. **Keep the no-SQL rule intact.** The alternative is not "write SQL against `G2C.db`" — it is SDK
   calls and export iteration, which is what the reporting guide's evaluation topic already documents
   (INV-117).

## Acceptance criteria

- [ ] Every Module 6 reference that routes counts or statistics to `reporting_guide` names a topic.
- [ ] The module states in one line what `topic='reports'` assumes and why it is not the bootcamp's
      route, attributed to the tool's own schema notes rather than asserted.
- [ ] The export-based `Validation:` patterns are named as the usable subset for a reader who lands on
      `topic='reports'`.
- [ ] No guidance suggests direct SQL against `database/G2C.db` (INV-117 unchanged).
- [ ] A bootcamper following Module 6's validation routing reaches guidance runnable against a
      single-database SQLite evaluation setup.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): topic
      selection is independent of platform, and the reporting guide takes the bootcamper's chosen
      language.

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/SKILL.md` — `:63`.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — `:6` and `:34`.
- `tests/` — assert no bare `reporting_guide` count/stat routing remains in Module 6, and that
  `topic='reports'` is characterized rather than merely absent.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "reporting_guide SQL targets a data mart the
  bootcamp never builds" (2026-07-28, Module Data processing;
  `Source: self-observed (assistant retrospective)`; `Routing: both`;
  `Upstream: submitted 2026-07-28`)
- Priority: Medium
- MCP re-check: **server contradicts the entry; subject redirected.** Server 1.32.1, 2026-07-28.
  `reporting_guide(topic='reports', scale='small')` states in its own `schema.description` that the
  `sz_dm_*` tables "are NOT part of the Senzing SDK and do NOT exist out of the box… must be created
  and maintained by a separate data mart replication pipeline that YOU build and operate", carries an
  anti-pattern about SQLite being POC-only, and includes `Validation:` SQL that runs against exported
  entity JSON rather than the data mart. The entry's suggested MCP-side fix — "have `reporting_guide`
  state plainly that its SQL assumes a separately-built data mart" — is therefore **already
  satisfied**. The routing half of its suggested fix stands and is what this spec implements.
- Upstream: already submitted 2026-07-28 per the entry. **Not re-filed, and worth flagging to the
  maintainer:** the submitted report asserted the tool does not disclose the data-mart prerequisite,
  which the current server refutes. If that submission is to be corrected, it needs a deliberate
  follow-up rather than a new report — and since submissions are anonymous there is no thread to
  correct, so the practical options are a fresh note or nothing.
- Related specs: `specs/export-related-entities-is-flag-conditional.md` (INV-169 — the same class of
  over-stated report, and the reason this one was re-checked rather than implemented as filed),
  `specs/post-load-match-key-semantic-audit.md` (INV-117 — the no-SQL rule this preserves),
  `specs/mcp-grounding-in-every-skill.md` (INV-080)

## What the re-check changed

The entry's premise — that `reporting_guide` returns data-mart SQL without saying so — is false on the
current server, which says so prominently and unprompted in the same response. Implementing the spec as
filed would have produced a plugin note "warning" readers about something the tool already tells them,
and an upstream report asking for a change already made.

What the re-check did *not* excuse is the reader's experience: they followed the plugin's routing, chose
the topic its wording implied, and landed on a response whose bulk is unusable here. That is a plugin
defect, and it is the one this spec fixes.

Recorded because the entry says `Upstream: submitted 2026-07-28`: a report was sent on the refuted
premise. Nothing here re-files it — Step 8 forbids re-filing the same finding — but the maintainer
should know a submitted report contains a claim the server does not support.
