# `find_examples` self-describes two different coverages, and the stale half hides TypeScript — upstream

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

One tool on the **same** MCP server, read in the **same** session, describes its own coverage two
different ways. Both read from **server 1.33.0, 2026-08-27**:

**`find_examples` declared tool description (the manifest a client loads, and therefore the schema
the plugin's own MCP-NEGATIVE markers treat as authoritative):**

> Find working SOURCE CODE examples from **37** indexed Senzing GitHub repositories. […] Indexes
> source code (**.py, .java, .cs, .rs**) and READMEs — NOT build/data files. […] Covers Python,
> Java, C#, Rust SDK patterns

**`get_capabilities` (same session, same server), describing the same tool:**

> Find working source code examples from **42** indexed Senzing GitHub repositories […] Indexes
> source code files (**.py, .java, .cs, .rs, .ts, .js**) and READMEs […] 42 GitHub repos; Python,
> Java, C# official; Rust and TypeScript/Node.js community

Two numbers (37 vs 42) and two extension sets (`.ts`/`.js` absent vs present).

**An empirical call settles which is right — `get_capabilities` is.**
`find_examples(query='add record engine initialization', language='typescript')` returned a
TypeScript file:

```text
repo:        brianmacy/sz-napi
file_path:   code-snippets/initialization/engine-priming/index.ts
provenance:  community
license:     Apache-2.0
```

So `.ts` **is** indexed, and the declared tool description is the stale half.

**The plugin is not currently wrong, and that is the whole reason this is filed as it is.** Checked
2026-08-27: the one place the plugin characterizes this index quotes the accurate source explicitly —
`module-06-data-processing/phaseA-build-loading.md:332` cites *"`get_capabilities` states the index
covers 'Python, Java, C# official; Rust, TypeScript/Node.js community … not official Senzing
SDKs'"*. No shipped file states a repo count (grep for `37`/`42` near `repo` across `plugins/`
returns nothing) and no shipped file enumerates the indexed extensions. The plugin quoted the
description that is correct and declined to quote the count that turns out to be inconsistent.

**Why it still matters to this plugin.** TypeScript is an offered bootcamp language, not a
hypothetical: `bootcamp-preparation/SKILL.md:264` presents it in the language choice and `:316` calls
Rust and TypeScript *"community-supported on all platforms"*, and `module-06`/`module-03` both list
TypeScript among the compiled languages whose code gets built. A future edit that helpfully writes
"37 repositories" — or, far worse, "`find_examples` indexes `.py`, `.java`, `.cs` and `.rs`" — would
be **wrong while carrying a real MCP citation from the tool's own declared schema**, which is the
most durable kind of error this repo produces. Concretely it would send a TypeScript bootcamper past
the one route that does have examples for their binding.

**Same class, same tool family, worth fixing in one pass upstream.** `generate_scaffold`'s declared
description says *"Languages: python, java, csharp, rust"* and *"Workflows: initialize, configure,
add_records, delete, query, redo, stewardship, information, full_pipeline"* — omitting `typescript`
and `error_handling` — while that same schema's own `language` and `workflow` **property**
descriptions both list them (`typescript (or ts, node, nodejs, javascript, js)`, and
`error_handling` with aliases `error, retry`). A reader who trusts the summary line over the
property description concludes the plugin's `language='typescript'` calls are invalid; they are not.

## Root cause

Not in this repo. Each Senzing MCP tool carries two independently authored descriptions of itself —
the declared tool description in the manifest, and the summary `get_capabilities` returns — and the
two are not generated from one source, so they drift. `find_examples` grew from 37 to 42 repos and
gained `.ts`/`.js` indexing; `get_capabilities` was updated and the manifest description was not.

The plugin's exposure is structural rather than present-tense. `ground-rules.md:281-294` correctly
establishes the **declared schema** as the authority for what a tool *accepts* (INV-234), and that is
right — the schema is normative for parameters. But a declared description also carries *prose about
coverage*, which is not normative and, here, is stale. The plugin has no rule distinguishing the two,
so an editor applying the existing "the schema is the route, the prose is not" principle in reverse —
trusting manifest prose because it sits in the schema — lands on the wrong half with a citation that
looks impeccable.

## Proposed change

1. **Record the contested fact where an editor will meet it**, following the precedent set by
   `specs/mcp-tools-disagree-on-eval-license-duration.md` (which put its note in the shipped file
   rather than in `INVARIANTS.md`). Add a short note at
   `module-06-data-processing/phaseA-build-loading.md:332`, beside the existing `get_capabilities`
   citation, stating that the tool's declared description understates coverage (37 repos, no
   `.ts`/`.js`), that `get_capabilities` governs, and that the disagreement was settled by a live
   call returning a `.ts` file. ⛔ Do **not** state a repo count in shipped prose — the point of the
   note is that the count is not citeable, and pinning either number recreates the defect.
2. **Draw the line the plugin is currently missing** in `ground-rules.md`, in the same passage that
   makes the declared schema authoritative (`:281-294`): a declared schema is authoritative for the
   **parameters a tool accepts**, and is *not* authoritative for **prose describing what a tool
   covers** — counts, indexed file types, language lists. For coverage, `get_capabilities` governs,
   and an empirical call settles a conflict. This is the generalizable half and the reason to file
   rather than only patch one line.
3. **Report upstream** (maintainer's call, and **not** to be sent by a dry run — see Source): both
   halves of `find_examples`' self-description, and `generate_scaffold`'s summary line omitting
   `typescript` and `error_handling`.

## Acceptance criteria

- [ ] `phaseA-build-loading.md`'s note beside `:332` states that `get_capabilities` governs over the
      declared description for `find_examples` coverage, and names the live `.ts` result that settled
      it, dated with the server version.
- [ ] No shipped file under `plugins/` states a `find_examples` repository count, and none enumerates
      its indexed file extensions. A grep for `\b37\b`/`\b42\b` near `repo`, and for `.cs, .rs`,
      returns nothing.
- [ ] `ground-rules.md` distinguishes declared-schema authority over **accepted parameters** from
      `get_capabilities`' authority over **coverage prose**, so the existing INV-234 passage cannot be
      read as endorsing stale manifest prose.
- [ ] A test asserts the plugin states no `find_examples` repo count and no indexed-extension list,
      so a future edit reintroducing either fails rather than shipping a cited-but-wrong figure.
      Stdlib only, no `plugins/` import (INV-108).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — contested-fact
  note beside the existing `get_capabilities` citation at `:332`
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the parameters-vs-coverage
  distinction in the INV-234 passage at `:281-294`
- `tests/test_find_examples_coverage_is_uncitable.py` — new guard (name mirrors
  `tests/test_eval_license_duration_is_unciteable.py`, the same-shaped precedent)

## Source

- Feedback: none — found by `/dry-run` phase 1 on 2026-08-27 (`Source: self-observed (assistant
  retrospective)`). Surfaced while diffing every plugin MCP literal against the live declared
  schemas; the two descriptions were read in the same session, and the TypeScript probe was run to
  break the tie rather than to reason about which looked newer.
- Priority: **Low.** Nothing is broken, no bootcamper is blocked, and the plugin currently cites the
  correct half. The argument against filing it as nothing at all is that TypeScript is a *shipped*
  language choice and the stale half is the one sitting inside the artifact `ground-rules.md` declares
  authoritative — so the wrong answer is the one an editor is most likely to reach for.
- MCP re-check: **server 1.33.0, 2026-08-27** — both descriptions read this session via the loaded
  tool manifest and `get_capabilities`; the disagreement **still reproduces**. Tie broken by
  `find_examples(query='add record engine initialization', language='typescript')`, which returned
  `brianmacy/sz-napi` → `code-snippets/initialization/engine-priming/index.ts`, proving `.ts` is
  indexed and the declared description understates coverage. No absence claim about the server is
  made here — the diagnosis rests on a positive result, not an empty one — so `owner-checked:` does
  not apply.
- Upstream: **sent 2026-08-27** as `submit_feedback(category='bug')`, on the maintainer's
  explicit approval of the verbatim text — see "Upstream report sent" below.
  Not sent during the dry run itself: ⛔ A dry run must not call
  `submit_feedback` under any category (`.claude/skills/dry-run/SKILL.md`, "Absolute rules"), so this
  was deliberately not filed. Same handling as
  `specs/mcp-tools-disagree-on-eval-license-duration.md`.
- Related specs: `specs/mcp-tools-disagree-on-eval-license-duration.md` (the same shape — two tools on
  one server disagreeing, plugin not yet wrong, note placed in the shipped file);
  `specs/a-spec-asserting-server-absence-must-name-the-owning-route.md` (INV-194, why the tie was
  broken by a call rather than by argument);
  `specs/mcp-negative-markers-must-name-the-owning-route.md` (the marker convention this coverage
  claim is deliberately *not* given, since it is not an absence)

## Upstream report sent (2026-08-27)

The maintainer approved the drafted text **verbatim** and it was sent as
`submit_feedback(category='bug')` on 2026-08-27 — a separate, maintainer-authorized action, taken
after the dry run closed and therefore outside the skill's ⛔ on invoking `submit_feedback` during a
run. No text was changed between approval and sending. Nothing identifying was included: the message
carries no name, no email and no local path, and the server states submissions are anonymous in any
case (INV-065).

The server's response records that **submissions are anonymous and cannot be followed up**, so no
reply will arrive and none should be waited for. The plugin-side protections this spec proposes — the
contested-fact note beside `phaseA-build-loading.md:332` and the `ground-rules.md`
parameters-vs-coverage distinction — are **still outstanding** and remain the operative safeguard
regardless of what upstream does. Re-check the two descriptions on a later server version rather
than assuming the report was acted on; if they are reconciled, retire the note rather than
inverting it.
