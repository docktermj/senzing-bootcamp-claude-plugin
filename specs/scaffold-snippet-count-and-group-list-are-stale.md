# Scaffold snippet count and group list are stale

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 3 Step 4 describes what `generate_scaffold(workflow='full_pipeline')` returns
using two figures that have both drifted since they were recorded:

> The response is a **listing** of snippets across initialization, loading and searching — 18 of
> them for Python on server 1.32.2 (verified 2026-07-29) — not "the" generated script.

On MCP server **1.32.9**, **2026-08-13**, the same call for Python returns **22**
snippets across **four** groups, not 18 across three. The omitted group is
`configuration`, which carries 4 snippets (`get_config_registry.py`,
`get_data_source_registry.py`, `init_default_config.py`, `register_data_sources.py`).

The consequence is small and worth stating honestly: **no instruction in the step
depends on either figure.** The count is illustrative framing for "This returns MANY
files", and the step's actual selection rule is explicitly count-independent and
position-independent — "match on the **shape** — does it open a data file? — never on
position in the list." Everything load-bearing in the block was re-verified as still
correct on 1.32.9 (see below). This is stale prose, not a broken path.

It is still worth correcting, because the drift is evidence *for* the rule the step
teaches. A count that moved 18 → 22 while the two named snippets stayed put is the
concrete demonstration of why the step says never to match on position, and a reader
who checks the stated count against a live response and finds it wrong has been given
a reason to distrust the paragraph that contains the correct instruction.

## Root cause

`plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md:244-245`
records a point-in-time observation of a response whose size the server is free to
change. The claim is correctly version-stamped and dated, which is the plugin's
existing mitigation and is why this is a low-severity finding rather than a wrong
fact — the prose does not assert the count is current.

The group list has no such defense: "across initialization, loading and searching" is
written as a description of the response's shape rather than as a dated observation,
so it reads as durable while being an enumeration that a new snippet group
invalidates. That is the same failure mode the skill's `unmarked` report exists to
catch for tool-absence claims, in a claim shape that report does not scan for.

### What the live server returns

`generate_scaffold(language='python', workflow='full_pipeline')` — MCP server
**1.32.9**, **2026-08-13** — 22 snippets:

| Group | Count |
|---|---|
| `initialization` | 10 |
| `configuration` | 4 |
| `loading` | 6 |
| `searching` | 2 |

Re-verified as **still correct** in the same response, and unchanged from the
1.32.2 observation:

- `loading/add_records_loop.py` and `loading/add_records.py` are both present, so the
  named pair the step tells you to choose between still exists.
- The `anti_patterns[]` array still returns both quoted entries verbatim at
  `severity: error` — *"Hardcoded John Doe / TEST / 1001 records"* → *"Records read
  line-by-line from JSONL"*, and *"/opt/senzing/er/testdata/truth-sets/..."* →
  *"User's input_file from mapping_workflow"*.
- The response is still a listing with no source text: each snippet carries
  `file_path`, `source_url`, `repo`, `raw_url`, `size_bytes`, `line_count` and no
  `content` field, and `access_steps` still orders fetch-`raw_url` before `git clone`
  with `inline` still undeclared in the schema (INV-160 holds).

Not re-verified: the claim that Python's `add_records_loop.py` ships
`INPUT_FILE = Path("../../resources/data/load-500.jsonl")`. That is a claim about file
*content*, which `generate_scaffold` elides by design, so confirming it requires
fetching `raw_url` from `raw.githubusercontent.com`. The step's instruction —
"**Override any hardcoded input path** the snippet ships with" — is robust to the
literal path being different, so this was left unverified rather than treated as a
blocker.

## Proposed change

1. Update the count to 22 with the current server version and date, or drop the
   specific number in favor of the group breakdown, which is more informative and
   less volatile.
2. Add `configuration` to the group list so the enumeration matches the response.
3. Frame the drift as support for the existing rule: note that the count moved
   between server versions while the two named loading snippets did not, which is
   exactly why selection matches on shape rather than position or count.

## Acceptance criteria

- [ ] `phase1-verification.md` states a snippet count and group list matching what
      server 1.32.9 returns (22 across initialization, configuration, loading,
      searching), stamped with that version and date.
- [ ] The step's selection rule still reads as shape-based and count-independent —
      the correction must not turn an illustrative figure into something a reader
      could mistake for a check to perform.
- [ ] No other file under `plugins/` repeats the stale 18/three-group figures.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md`
  — lines 244-245: the snippet count and the group enumeration.

## Source

- Feedback: n/a — found by `/dry-run` phase 1 (MCP call contracts), 2026-08-13,
  Module 3 (`Source: self-observed (assistant retrospective)`).
- Priority: Low — stale illustrative prose. No instruction depends on either figure,
  and the surrounding rule was re-verified correct on the current server.
- MCP re-check: server **1.32.9**, **2026-08-13** — **still reproduces** (the figures
  are stale). Tool called: `generate_scaffold(language='python', workflow='full_pipeline')`.
  No absence claim is made in this spec, so no `owner-checked:` clause is required.
- Upstream: not applicable — the server is entitled to change how many snippets it
  indexes; the plugin's job is to not depend on the number.
- Related specs: none.
