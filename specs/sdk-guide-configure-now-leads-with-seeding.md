# Module 2's seeding instructions point at a response shape the server no longer returns

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

**The plugin ships two wrong Senzing facts today, and a Bootcamper following either is sent looking
in a place the answer is not.** Both were true when written against server 1.32.2 and both were
fixed upstream — the second by a bug report this project filed.

**Wrong fact 1 — the seeding snippet is no longer an alternative.**
`module-02-sdk-setup/SKILL.md:1023-1029` says:

> 1. Call `sdk_guide(topic='configure', language='<chosen_language>')`.
> 2. In the response's `alternatives`, take the **`init_default_config`** entry — that is the seeding
>    snippet. Verified on server 1.32.2 (2026-07-30) …
> 3. Run it, then proceed to register data sources with the primary snippet, which now has a config
>    to build from.

`sdk_guide(topic='configure', language='python')` on **server 1.32.8, 2026-08-11** returns
`init_default_config` as the **primary `code` block**, not as an alternative:

```json
"code": {"source_path": "python/configuration/init_default_config.py",
         "source_repo": "senzing/code-snippets-v4", "code": "…create_config_from_template()… set_default_config(…)…"},
"alternatives": [{"name": "get_config_registry",       "source_path": "python/configuration/get_config_registry.py"},
                 {"name": "get_data_source_registry",  "source_path": "python/configuration/get_data_source_registry.py"},
                 {"name": "register_data_sources",     "source_path": "python/configuration/register_data_sources.py"}]
```

The roles have **swapped**. `init_default_config` is the primary; `register_data_sources` is now the
alternative. A guide following step 2 searches `alternatives` for an entry that is not there, and
step 3's "the primary snippet" now names the seeding snippet it was just told to run.

**Wrong fact 2 — `generate_scaffold(workflow='initialize')` now does seed.**
`SKILL.md:1031-1034` says:

> ⚠️ **`generate_scaffold(workflow='initialize')` does not do this.** Its snippets cover factory and
> environment lifecycle — creation, priming, destroy, purge, signal handling — and none of them seeds
> a configuration, even though `get_capabilities` names that workflow for "schema and default config
> must exist".

`generate_scaffold(language='python', workflow='initialize')` on **1.32.8, 2026-08-11** returns 14
snippets, four of them from `python/configuration/`: `init_default_config.py`,
`register_data_sources.py`, `get_config_registry.py`, `get_data_source_registry.py`. The workflow now
matches what `get_capabilities` advertises for it, and the ⚠️ warning is false.

**INV-169 applied.** Neither is a conditions mismatch. Both were re-asked with the *same* tool and
the *same* parameters the plugin's own text names, on the same `version='current'`. The plugin's
claims do not hold under some narrower flag set, binding or platform the server's answer fails to
cover — they are simply describing an older response shape.

Verdict: **`contradicted`**, and it simultaneously **retires** the ledger's
`generate-scaffold-initialize-does-not-seed` coverage gap (`keep-server-lacks-it`, upstream `bug`
sent 2026-07-30) — the gap this project reported is closed.

## Root cause

The text was written when it was accurate, and dated honestly: `:1025` says "Verified on server
1.32.2 (2026-07-30)". `specs/sdk-guide-configure-unseeded-datastore.md:33-34` records the original
finding — "**`init_default_config` is present but unsignposted.** It appears only as a bare entry in
`alternatives`" — and the project filed it upstream. Senzing acted on it. Nothing in the plugin
notices a fix: a dated provenance stamp proves when a fact was checked, never that it is still true,
and the ⚠️ block reads exactly as authoritative on the day it goes stale.

## Proposed change

**Rewrite Step 8a's "How to seed" to read the response the server returns now.**

1. Call `sdk_guide(topic='configure', language='<chosen_language>')`.
2. Take the **primary `code` block** — confirm `code.source_path` ends `configuration/init_default_config.py`.
   Extract `code.code` verbatim; that is the seeding snippet. Do not hand-write it (INV-080).
3. Register data sources from the **`register_data_sources`** entry in `alternatives`
   (`source_path: python/configuration/register_data_sources.py`), after the seed exists.

**Delete the ⚠️ `generate_scaffold` block at `:1031-1034` outright.** It now warns against a tool
that does the thing. Replace it with nothing, or one sentence noting that
`generate_scaffold(workflow='initialize')` also returns the configuration snippets, so either route
reaches the same code.

**What stays.** Everything else in Step 8a: the `SENZ0031`/unseeded-datastore diagnosis at
`:1012-1019` (re-verify separately — it cites 1.32.2 and this spec did not re-ask
`explain_error_code`), the take-the-code-from-MCP rule (INV-080), the "verify the seed before moving
on" check at `:1036`, and the reinitialize requirement. **Newly available and worth capturing:** the
1.32.8 response carries a `compatibility_notes` entry stating that `env.reinitialize(config_id)`
must follow `set_default_config()` "before loading records" — the plugin can now cite the tool for
that instead of asserting it.

**Do not hardcode the new shape either.** The lesson of this spec is that a response shape is not a
fact to cache. Instruct the reader to locate the seeding snippet by its `source_path` ending
`configuration/init_default_config.py` **wherever it appears** — primary or alternative — rather than
by its position in the response. That survives the next reorganisation; naming a position does not.

**Fallback when the call fails (INV-125).** Unchanged from today: `sdk_guide` is already the sole
route and the step already depends on it. If it is unreachable, stop and report — do not hand-write a
seeding sequence from memory.

## Acceptance criteria

- [ ] `module-02-sdk-setup/SKILL.md` no longer tells the reader to find `init_default_config` in
      `alternatives`; it locates the snippet by `source_path` ending `configuration/init_default_config.py`
      in either position.
- [ ] The ⚠️ "`generate_scaffold(workflow='initialize')` does not do this" block is gone.
- [ ] **Re-verification clause:** implementing this requires `sdk_guide(topic='configure', language='python')`
      to still return `code.source_path == "python/configuration/init_default_config.py"`, and
      `generate_scaffold(language='python', workflow='initialize')` to still list
      `python/configuration/init_default_config.py`. If either has moved again, re-triage rather than
      implementing this text.
- [ ] Any test pinning the `alternatives` wording or the `generate_scaffold` warning is repointed to
      the requirement (the step obtains seeding code from MCP and never hand-writes it), with a
      docstring recording what changed and when (INV-181). Check `tests/test_mcp_call_contracts.py`
      and `tests/test_config_seeding_guidance.py`.
- [ ] The `specs/mcp-coverage.jsonl` row `generate-scaffold-initialize-does-not-seed` is superseded by
      a `retire-workaround` row — appended, never edited in place.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      snippet is fetched per `<chosen_language>` and no language is privileged.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 8a, `:1021-1034`.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md:51` — cites the
  same seeding path; check it does not repeat the `alternatives` claim.
- `tests/` — the assertions named above.

## Source

- Sweep: `delegate-to-mcp-server`, 2026-08-11. Server **1.32.8** (was 1.32.2), docs index
  **2026-08-11 13:35 UTC** (was 2026-07-29 11:11 UTC) — both axes moved.
- Tools called: `get_capabilities`, `sdk_guide(topic='configure', language='python')`,
  `generate_scaffold(language='python', workflow='initialize')`.
- Priority: **High.** Two wrong instructions in a mandatory setup step, one of which sends the reader
  hunting a response key that no longer exists.
- Upstream: the `generate_scaffold` half was reported by this project as a `bug` on 2026-07-30 and is
  now fixed. Nothing further to send.
- Related specs: `specs/sdk-guide-configure-unseeded-datastore.md` (the original finding),
  `specs/refresh-reverified-provenance-stamps.md:78-79` (the `init_default_config` sequence stamp).

## Deviations from this spec, and why (2026-08-11)

⚠️ **This spec's central explanation was wrong, and INV-169 is exactly why.** The spec says the
primary/alternative "roles have **swapped**". They do not swap — the tool **selects** by whether
`data_sources` was passed. Re-verified on MCP server 1.32.8, 2026-08-11, calling both ways in
`language='python'`:

| Call | Primary `code.source_path` | In `alternatives` |
|---|---|---|
| `sdk_guide(topic='configure', language='python')` — no `data_sources` | `python/configuration/init_default_config.py` | `register_data_sources` |
| `sdk_guide(..., data_sources=["CUSTOMERS","WATCHLIST"])` | `python/configuration/register_data_sources.py` | `init_default_config` |

The spec was written after calling it **one** way and generalising — the precise failure INV-169
names, and which this repo has had to retract twice before. `explain_error_code('SENZ7221')` gave it
away: its first resolution step now reads "see sdk_guide topic='configure' **(called WITHOUT
`data_sources`, this returns the seeding snippet)**".

**The defect is real but narrower than the spec claims.** Module 2's step 1 makes the
no-`data_sources` call; its step 2 then reads the response as if `data_sources` had been passed. So
the instruction is wrong *for the call its own step 1 issues* — not because anything swapped. The
implementation states the discriminator as a two-row table and tells the reader to locate the
snippet by `source_path`, never by position, which is what survives the next argument change.

**Two things the spec did not know were available, both now relayed instead of asserted.**
`sdk_guide(topic='configure', data_sources=[…])` carries a `compatibility_notes` entry stating the
precondition, the `SENZ7221` consequence and the remedy in full; and `explain_error_code('SENZ7221')`
now names cause and remedy itself. Module 2 quotes the former and Module 5 cites the latter, rather
than the plugin asserting either on its own authority (INV-080).

**The `generate_scaffold` half of the spec is confirmed unchanged.** Called with exactly the
parameters the plugin's ⚠️ block named — `generate_scaffold(language='python', workflow='initialize')`
— it returns the four `python/configuration/` snippets. Same condition, genuinely false claim; the
block is gone.

**Scope beyond the Affected files list.** `module-05-data-quality-mapping/phase3-test-load.md:49-51`
repeated the same `alternatives` claim *and* said `SENZ7221`'s "own `explain_error_code` guidance does
not name the cause", which is now false. Both corrected. The spec anticipated the first ("check it
does not repeat the `alternatives` claim") but not the second.

**A spec citation was wrong.** The spec says the `SENZ0031` diagnosis sits at `:1012-1019`. There is
no `SENZ0031` there — the code is `SENZ7221`. `explain_error_code('SENZ0031')` returns
`EAS_ERR_INVALID_VALUE_OF_MAX_DEGREE`, unrelated to config seeding.
