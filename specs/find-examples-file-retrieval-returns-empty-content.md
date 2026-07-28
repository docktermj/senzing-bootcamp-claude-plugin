# Guard against `find_examples` file retrieval returning empty content

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`find_examples` documents three modes, the third being **"File retrieval: pass `repo` + `file_path`"**.
That mode currently returns an **empty `content` field** while reporting a correct non-zero
`content_length` and `truncated: false`.

Verified against server version 1.32.1 on 2026-07-28, four calls:

| Call | `content` | `content_length` | `truncated` |
| --- | --- | --- | --- |
| `repo` + `file_path` (`LoadRecords.java`) | `""` | 6741 | `false` |
| `repo` + `file_path` + `max_lines=10` | `""` | 6741 | `false` |
| `repo` + `file_path` + `max_lines=30` (`LoadWithInfoViaFutures.java`) | `""` | 12876 | `false` |
| `repo` + `file_path` + `inline=true` | full source | 6741 | `false` |

So `max_lines` is **not** the trigger — the undeclared `inline` parameter is the switch. Two further
details compound it:

- **`inline` is not in the tool's input schema.** The declared properties are `file_path`, `language`,
  `list_files`, `max_lines`, `query`, and `repo`. The response's own `access_steps` names `inline=true`
  as step 3 ("Last resort"), so the remedy is advertised in prose but absent from the contract. A client
  that validates arguments against the declared schema cannot reach it.
- **`truncated: false` with a non-zero `content_length` actively asserts completeness.** There is no
  signal that anything is missing, so the natural reading of the response is "this file is empty."

The same `inline=true` prose appears in `generate_scaffold`'s `access_steps`, whose schema likewise
declares only `language`, `version`, and `workflow`.

## Root cause

Two parts, one outside this repository:

- **The empty-content behavior is the Senzing MCP server's.** The plugin cannot fix it. **Upstream
  request FILED 2026-07-28** via `submit_feedback` as category `bug`, at the maintainer's direction,
  after the exact message text was reviewed and approved: it reports the empty `content` alongside the
  non-zero `content_length` and `truncated: false`, names both reproducing files, states that `max_lines`
  is irrelevant, and notes that the advertised `inline=true` remedy is undeclared in the schema. It
  carried no hostname, username, email, or path (INV-065 discipline). Submissions are anonymous, so there
  is no reply channel.
- **The plugin has no guidance for it.** This is what this spec delivers. The exposure is *latent, not
  active*: all six `find_examples` references in the plugin use search mode (`query=`), and **none** uses
  `repo` + `file_path`, so no bootcamp path hits the failure today —

  - `module-07-query-visualize-discover/phase1-query-visualize.md:431-432` — `query='REST API'`, `query='batch report'`
  - `module-05-data-quality-mapping/phase3-test-load.md:78` — named alongside `generate_scaffold`
  - `module-04-data-collection/SKILL.md:182` — `query='XML data loading'`
  - `module-06-data-processing/phaseC-multi-source.md:107` — `query="multi-source"`
  - `bootcamp-onboarding/ground-rules.md:95` — the routing rule

  The risk is `ground-rules.md:95`, which routes "working examples -> `find_examples`" **generically**.
  An assistant needing one specific file's source can reasonably improvise `repo` + `file_path`, get an
  empty string back, and — because `truncated: false` says the payload is complete — report to the
  bootcamper that an example file is empty, or silently skip the example. That is a wrong statement about
  Senzing content, which the MCP-grounding rules exist to prevent.

## Proposed change

1. **Add a retrieval note to the `find_examples` routing in `ground-rules.md`.** When the source of one
   specific file is needed, prefer the `raw_url` the search results already return and fetch that, rather
   than relying on `content` from `repo` + `file_path` retrieval.
2. **State the durable rule: an empty `content` is never evidence that a file is empty.** If `content` is
   empty while `content_length` is non-zero, treat the retrieval as **failed**, not as an empty file —
   regardless of what `truncated` says. Fall back (fetch `raw_url`, or clone per the response's
   `access_steps`) and never tell the bootcamper an example is empty on this basis.
3. **Do not add `inline=true` to any documented plugin call.** It is undeclared in the tool's schema, so
   depending on it would couple the plugin to an unversioned parameter that a schema-validating client may
   reject. It belongs in this spec as diagnosis, not in the plugin as a documented call.
4. **Keep the note scoped and small.** This is a latent-risk guardrail, not an active defect — it should
   read as one caution on an existing routing line, not a new subsection, and must not imply the tool is
   broken for the search mode the plugin actually uses.

## Acceptance criteria

- [ ] `bootcamp-onboarding/ground-rules.md` states that for one specific file's source, the `raw_url` +
      fetch path is preferred over `repo` + `file_path` retrieval.
- [ ] The guidance states that empty `content` with a non-zero `content_length` means retrieval **failed**,
      explicitly overriding `truncated: false`, and that the assistant must never report an example file as
      empty on that basis.
- [ ] No plugin file documents or instructs the use of the undeclared `inline` parameter.
- [ ] The six existing search-mode `find_examples` call sites are left unchanged — the note adds a
      condition for retrieval, and does not discourage search mode.
- [ ] The guidance is written as "verify, then handle" and does not assert the upstream bug is permanent;
      it should be trimmed once upstream lands.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the note is
      tool-level, adds no platform-specific step, and names no language.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the tool-routing block
  (line ~95, "working examples -> `find_examples`"): the retrieval caution and the empty-content rule

## Source

- Self-observed 2026-07-28 while verifying whether the Senzing MCP server's `submit_feedback` tool was
  disabled; found incidentally when reading a Java scaffold to confirm a separate report. Server version
  1.32.1.
- Priority: Low — latent risk only; no current bootcamp path uses the affected mode.
- Related specs: `specs/java-scaffold-json-dependency-gap.md` (the report filed in the same pass, and the
  reason the scaffold was being read), `specs/mcp-grounding-in-every-skill.md` (the grounding rules this
  guardrail protects)

## Invariants introduced

- `INV-160` — Where an MCP tool's response carries both a payload field and metadata describing that
  payload's size or completeness, a payload that contradicts its own metadata MUST be treated as a
  **failed retrieval**, never as a real empty result; the documented access path (`raw_url`, or clone per
  `access_steps`) is the fallback, an undeclared parameter is not, and the Bootcamper MUST NOT be told an
  example file is empty on that basis. Bounded against INV-149: an empty result with no contradicting
  metadata is coverage, not failure. (Recorded in `specs/INVARIANTS.md`.)
