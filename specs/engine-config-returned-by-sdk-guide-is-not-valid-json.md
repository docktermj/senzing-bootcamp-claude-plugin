# engine_config returned by sdk_guide is not valid JSON

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

SDK setup Step 8 opens with an absolute instruction:

> 🚨 **NEVER construct `SENZING_ENGINE_CONFIGURATION_JSON` manually.** Always use
> the exact JSON returned by `sdk_guide(topic='configure', platform=…, language=…,
> version='current')`.

The exact string that call returns is **not valid JSON**. Every brace in it is
doubled:

```text
{{
  "PIPELINE": {{
    "CONFIGPATH": "/etc/opt/senzing",
    "RESOURCEPATH": "/opt/senzing/er/resources",
    "SUPPORTPATH": "/opt/senzing/data"
  }},
  "SQL": {{
    "CONNECTION": "sqlite3://na:na@/tmp/sqlite/G2C.db"
  }}
}}
```

`json.loads` on it raises
`JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2`.
So the instruction cannot be followed as written: a guide that uses the string
verbatim produces an engine configuration the SDK cannot parse, and one that fixes
it is — strictly — constructing the JSON manually, which the same sentence forbids
in bold with a 🚨.

The step already handles the *other* thing wrong with that string (the `/tmp`
path), so a reader reasonably assumes the rest is usable as-is.

## Root cause

The doubling has the shape of an un-rendered Python format template: `{{` and `}}`
are how `str.format` escapes literal braces, so the server appears to be returning
the template rather than the rendered result. It is consistent across topics —
`sdk_guide(topic='install', platform='linux_apt', language='python')` returns the
same doubled form in its own `engine_config` field.

The plugin side is `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:965-970`,
which tells the guide to use the returned string exactly and warns only about
guessing the three paths. Nothing tells it the string needs un-escaping, and
nothing distinguishes "take these three path *values* from the server" (which is
the real, correct intent, and is what protects against the SENZ2027 /
wrong-SUPPORTPATH failure the step goes on to explain at length) from "paste this
blob".

Two independent problems, one line: the values are authoritative and must come from
MCP; the *rendering* is broken and must not be pasted.

n/a for a plugin-side Senzing fact — the three path values are correct; only the
serialization is wrong.

## Proposed change

1. Reword Step 8 to say what it actually means: **take the `CONFIGPATH`,
   `RESOURCEPATH` and `SUPPORTPATH` values, and the connection-string form, from
   the `sdk_guide` response — never guess them (INV-080)** — and assemble the JSON
   from those values. Keep the 🚨 on *guessing the values*, which is the failure
   the step exists to prevent, and drop the "use the exact JSON" phrasing, which is
   unfollowable.
2. Add a one-line note that the response's `engine_config` field currently returns
   brace-escaped template text (`{{`/`}}`) and must not be written to disk as-is,
   with the date and server version, so a future reader can tell whether it is
   still true.
3. Note that the same field carries `/tmp/sqlite/G2C.db`, which INV-200 already
   requires overriding to `database/G2C.db` — so `engine_config` needs **two**
   corrections, not one. The step currently mentions only the paths.
4. Prefer building the config from `environment.default_paths` in the same
   response (`config_path`, `support_path`, `resource_path`), which are plain
   correct strings and need no un-escaping — a more robust source than the
   rendered blob.

## Acceptance criteria

- [ ] Step 8 no longer instructs the guide to use `engine_config` verbatim.
- [ ] Step 8 states that the three path values and the connection-string form come
      from `sdk_guide` and are never guessed.
- [ ] The brace-escaping observation is recorded with its server version and date.
- [ ] The step names both corrections `engine_config` needs: un-escaping and the
      `/tmp` override.
- [ ] Following Step 8 produces a `config/engine_config.json` that `json.loads`
      parses and that points at `database/G2C.db`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 8's
  "use the exact JSON" instruction.

## Source

- Feedback: dry run phase 3, 2026-08-13 — executing Step 8 on the SQLite branch
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — the failure is immediate and legible (invalid JSON) rather
  than silent, but it makes a 🚨 instruction impossible to obey, which is corrosive
  to the surrounding rules.
- MCP re-check: server 1.32.9, docs indexed 2026-08-11 20:52 UTC, checked
  2026-08-13. `sdk_guide(topic='configure', platform='linux_apt',
  language='python', version='current')` and `sdk_guide(topic='install',
  platform='linux_apt', language='python')` both return the doubled-brace form in
  `engine_config`. Confirmed unparseable with `json.loads`. Still reproduces.
- Upstream: **not yet reported** — this looks like a server-side rendering bug
  (`str.format` escaping left unrendered) and is worth reporting via
  `submit_feedback(category='bug')`. Not sent from the dry run, which is forbidden
  from calling that tool; the maintainer's call.
- Related specs: `specs/sqlite-branch-says-no-additional-setup-but-the-schema-is-required.md`
  (same step's other correction to the same returned string)
