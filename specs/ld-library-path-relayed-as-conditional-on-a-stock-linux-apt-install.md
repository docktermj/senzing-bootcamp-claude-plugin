# The plugin relays `sdk_guide`'s "only needed if not found automatically" gloss for `LD_LIBRARY_PATH`, which is false on a stock `linux_apt` Python install

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

On a **default** apt install — `senzingsdk-runtime` at `/opt/senzing`, no custom location —
`import senzing_core` failed with:

```text
libSz.so: cannot open shared object file: No such file or directory
```

until `LD_LIBRARY_PATH=/opt/senzing/er/lib` was exported. It was not conditional there; it was
**required**.

⚠️ **The failure lands in a later module.** The environment script is written in SDK setup; the
missing variable surfaces at the first real import, which reads as a broken SDK install rather than
an incomplete environment.

## Root cause

Two layers, and the plugin owns the second regardless of what the server does.

### 1. The server's own response contradicts itself (already reported upstream)

Re-verified on **MCP server 1.32.9, 2026-08-16**,
`sdk_guide(topic='install', platform='linux_apt', language='python')`:

- `install.platform.env_vars`:
  > `"LD_LIBRARY_PATH": "/opt/senzing/er/lib (only needed if native lib not found automatically)"`
- `gotchas[0]`, same payload:
  > "LD_LIBRARY_PATH is only needed if the native lib is not found automatically (e.g., custom
  > install location): export LD_LIBRARY_PATH=/opt/senzing/er/lib:$LD_LIBRARY_PATH"
- and the **Python SDK** entry in the *same* `gotchas[]` array, stated unconditionally:
  > "The senzing and senzing-core packages are included in senzingsdk-runtime at
  > /opt/senzing/er/sdk/python. Do NOT pip install them — instead set
  > PYTHONPATH=/opt/senzing/er/sdk/python:$PYTHONPATH **and**
  > LD_LIBRARY_PATH=/opt/senzing/er/lib:$LD_LIBRARY_PATH"

One payload carries both readings. `sdk_guide(topic='configure', platform='linux_apt',
language='python')` returns `environment.env_vars` with the **identical hedged string** — so
switching topics does not resolve it.

### 2. The plugin re-states the hedge in its own voice

`module-02-sdk-setup/SKILL.md:473`:

> `sdk_guide(...)` returns them in `install.platform.env_vars` (`PYTHONPATH`, and
> `LD_LIBRARY_PATH` **for when the native library is not found automatically**)

That parenthetical is the plugin's own gloss, not a quotation, and it reproduces exactly the reading
that produces a `PYTHONPATH`-only environment script. The env-script template compounds it:
`:658-660` says platform-specific exports "go here — take them from `sdk_guide(topic='install',
platform=…)`", routing the author to the response whose `env_vars` hedges, with no instruction to
read `gotchas[]` for the Python case that contradicts it.

`:746` ("On **Linux**, the equivalent variable is `LD_LIBRARY_PATH` and the same 'set it in the
launching shell' rule applies — confirm the specifics via `sdk_guide`") sits in the **JVM**
subsection, so a Python author does not reach it.

## Proposed change

1. **Rewrite `:473` to state the Python/Linux case as required, not conditional**, and attribute
   both halves: quote the unconditional Python-SDK `gotchas[]` line as the governing one for
   `language='python'` on `linux_apt`, and record that `env_vars` hedges the same variable in the
   same response. Do not silently pick a side — the contradiction is the fact a reader needs.
2. **Add the reason it matters at the step**: an env script written from `env_vars` alone imports
   fine until the first engine-class call, where the resulting `libSz.so: cannot open shared object
   file` reads as a broken install. One line, at the site that writes the script.
3. **Point the env-script template at `gotchas[]`, not only `env_vars`** (`:658-660`), for the
   language-specific exports. `env_vars` is a summary; the per-language requirement is in the
   gotchas array.
4. **Do not hardcode the paths.** `/opt/senzing/er/lib` appears here as the server's quoted value
   with its date and version, exactly as the surrounding text already handles Senzing facts
   (INV-080); the instruction stays "take it from `sdk_guide`".

## Acceptance criteria

- [ ] `module-02-sdk-setup/SKILL.md` no longer glosses `LD_LIBRARY_PATH` as needed only when the
      native library is not found automatically.
- [ ] The Python + `linux_apt` case states that both `PYTHONPATH` and `LD_LIBRARY_PATH` are set,
      quoting the `gotchas[]` line, and records that the same response's `env_vars` says otherwise.
- [ ] The env-script guidance routes the author to the language-specific `gotchas[]`, not to
      `env_vars` alone.
- [ ] The observed symptom (`libSz.so: cannot open shared object file`) appears at the step, framed
      as an incomplete environment rather than a broken install.
- [ ] No path or version figure is hardcoded as a plugin-owned fact; all are quoted from
      `sdk_guide` with route, server version and date (INV-080).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      change is scoped to the Linux/Python branch and must not disturb the macOS `DYLD_LIBRARY_PATH`
      or Windows `.bat` guidance.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — `:465-478` (the Python Step 3
  relay), `:655-662` (the env-script export placeholder), and a cross-reference from `:740-752` so
  the Linux note is reachable from the non-JVM path.
- `tests/` — guard asserting the conditional gloss does not return.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "SDK setup: `LD_LIBRARY_PATH` documented as conditional, but required on a stock linux_apt install" (2026-08-16, Module SDK setup Step 3; `Source: self-observed (assistant retrospective)`)
- Priority: High — it breaks the first real import, one module after the step that caused it.
- MCP re-check: **server 1.32.9, 2026-08-16 — still reproduces, verbatim.** `sdk_guide(topic='install', platform='linux_apt', language='python')` returns the hedged `env_vars.LD_LIBRARY_PATH` string *and* the unconditional Python-SDK `gotchas[]` line, in the same payload. `sdk_guide(topic='configure', platform='linux_apt', language='python')` returns `environment.env_vars` with the identical hedged string — so the contradiction is not topic-specific. Observed against Senzing SDK 4.3.4-26210 installed from apt at `/opt/senzing`; the import failure itself is engine/loader behavior and is observation-only.
- Upstream: **already sent 2026-08-16 via `submit_feedback` (`bug`, anonymous), per the entry.** Do not re-file — this triage adds only that `topic='configure'` carries the same hedge, which does not change the report's substance. Submissions are anonymous, so no reply is possible.
- Related specs: `specs/senzing-python-sdk-must-not-be-pip-installed.md`, `specs/skipping-step-3-on-an-existing-install-skips-the-env-script.md`, `specs/env-script-must-be-shell-portable.md`, `specs/macos-jvm-launch-environment-guidance.md`, `specs/step1-filesystem-fallback-is-linux-only.md`

## Routing note — why a plugin spec exists for an `mcp-server` finding

The entry routes this `mcp-server`, correctly: the wording originates in `sdk_guide` and a corrected
server response fixes it for everyone reading the tool directly. That report is filed. But the
plugin does not merely pass the response through — `:473` re-states the conditional in the plugin's
own words, and the env-script template routes the author to the hedged field. Both are the plugin's
to fix, and they remain wrong until the server changes, which is outside this repo's control and
has no delivery date. Filing both is the rule the skill states: a plugin spec and an upstream report
are not alternatives.
