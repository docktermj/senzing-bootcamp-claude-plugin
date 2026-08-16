# Declined revisit note asserts an absence from two surfaces the fact does not live on

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The 2026-08-13 revisit note on `no-route-for-bootcampers-who-cannot-add-an-mcp-server`
(`specs/DECLINED.md:95-104`) reports that one of the declined spec's two routes "lost its
citation", and concludes that the evidence base "has **narrowed from two to one**". It then
instructs the next reader to trust that check:

> Anyone reopening this should re-run the check above rather than trusting the spec's 1.32.3
> citations. (`specs/DECLINED.md:103-104`)

Both the sub-claim and the conclusion are wrong, and they are wrong in the INV-194 shape: the
sweep asked two surfaces and neither of them is where the fact lives.

1. **The sub-claim is false as written.** The note says that at 1.32.9 `sz-mcp-coworker` appears
   nowhere "in that description or anywhere in the `get_capabilities` manifest"
   (`specs/DECLINED.md:96-98`). `get_capabilities` returns it as the server's own name, in the
   same response object the note cites for the version number:

   ```json
   "server_info":{"senzing_version":"current","server_name":"sz-mcp-coworker",
                  "server_version":"1.32.9","tool_count":13}
   ```

2. **The conclusion is contradicted by two further surfaces.** `explain_error_code('SENZ9000')`
   names the binary, as something the reader can run, in its `resolution_steps`:

   > "Verify license is active: run `sz-mcp-coworker` **selfcheck** (airgap binary) or call
   > `SzProduct::license()` from any SDK to inspect record_limit and expire_date"

   And `mapping_workflow(action='start')`'s step-1 instructions name the **mode** by name, as a
   live branch a client is expected to handle:

   > "Each resource carries either a 'url' (HTTP mode — download from it) or a 'fetch' command
   > (**stdio/airgap mode** — run it in your shell to extract the file)."

   So at 1.32.9 both the binary and stdio mode are still cited by the server, on two surfaces the
   sweep did not ask. Neither lost its citation; the sweep asked routes that never carried them.

**The decline itself is unaffected and must stand.** The `Revisit if:` condition is "Senzing
documents a self-service route", and that is still not met — `search_docs(query='sz-mcp-coworker
selfcheck airgap binary stdio mode')` returns no `sz-mcp-coworker` content at all (four hits, all
unrelated: a Scala `SelfCheck.scala` in `brianmacy/sz_spark`, and `@senzing/sdk-*` npm prebuilt
binaries). Naming a binary in an error-code remedy is not documenting how to obtain or run it.
Only the *evidence* in the note is wrong, not the decision it supports.

## Root cause

The note's sweep asked `sdk_guide`'s tool description and the `get_capabilities` tool manifest.
Neither is a route that would carry an install or invocation fact about the server binary, so
their silence was recorded as the binary's disappearance. This is exactly the failure mode
INV-194 exists for — an absence concluded from routes that never owned the fact — occurring in a
`DECLINED.md` revisit note rather than in a spec, which is why no existing guard saw it.

Two things made it survive:

- **Nothing re-verifies `DECLINED.md`.** `implement-spec` Step 3.3 re-verifies a *spec's* Senzing
  facts at implementation time, but a declined spec is never implemented, so its revisit note is
  the one Senzing claim in the repo with no re-verification path at all.
- **The note carries no `MCP-NEGATIVE` marker**, and could not usefully carry one:
  `coverage_reports.py` excludes `specs/` from the negatives scan by design
  (`.claude/skills/dry-run/coverage_reports.py:93-94`). That exclusion is the class defect and is
  specced separately as `specs/declined-ledger-negatives-are-invisible-to-the-scanner.md`.

## Proposed change

Correct the note in place, keeping it as a dated record rather than rewriting history:

1. Replace the "⚠️ **One of the two routes lost its citation.**" bullet
   (`specs/DECLINED.md:95-98`) with what the three surfaces actually return at 1.32.9: the
   `sdk_guide` description no longer names stdio mode or the `extract` command; `get_capabilities`
   carries the binary's name as `server_info.server_name`; and `explain_error_code('SENZ9000')`
   names `sz-mcp-coworker selfcheck` as a runnable airgap binary.
2. Replace the "narrowed from two to one" conclusion (`specs/DECLINED.md:102-104`) with the
   accurate net effect: **both routes are still named by the server**, the stdio *install*
   citation specifically is gone, and the corpus still documents neither — so the revisit
   condition remains unmet on the strength of `search_docs`, not on the routes' disappearance.
3. Keep the instruction to re-run the check, but name `explain_error_code` in it, so the next
   sweep asks the surface this one missed.
4. Add a dated line recording that the 2026-08-13 sweep was under-scoped and how it was caught,
   so the correction is legible as a correction (the same discipline the entry already applies to
   its own erroneous implementation at `specs/DECLINED.md:105-109`).

Do **not** change the `Declined:`, `Decided by:`, `Reason:` or `Revisit if:` fields — the decision
and its trigger are unchanged.

## Acceptance criteria

- [ ] `specs/DECLINED.md` no longer claims `sz-mcp-coworker` is absent from `get_capabilities`,
      and states where it actually appears (`server_info.server_name`).
- [ ] The note names `explain_error_code('SENZ9000')` as a surface that cites the binary at
      1.32.9, with the quoted `resolution_steps` fragment.
- [ ] The "narrowed from two to one" conclusion is gone, replaced by one that survives asking all
      three surfaces.
- [ ] The `Revisit if:` condition still reads as **not met**, justified by `search_docs` returning
      no `sz-mcp-coworker` content — not by the routes being uncited.
- [ ] The re-run instruction names every surface checked, including `explain_error_code`.
- [ ] `tests/test_declined_ledger.py` still passes, and the entry still subtracts from
      `implement-spec`'s candidate set (`list_specs.py` reports `open: 0` for this spec).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/DECLINED.md` — correct the 2026-08-13 revisit note's evidence and conclusion; leave the
  decision fields untouched.

## Source

- Feedback: none — self-observed during a `/dry-run` phase 1 sweep, 2026-08-13
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — the decision is correct, so nothing ships wrong; but the note actively
  misdirects the next revisit check, which is the one thing it exists to support.
- MCP re-check: server **1.32.9**, 2026-08-13 — **server contradicts the record.**
  `get_capabilities` returns `server_info.server_name = "sz-mcp-coworker"`;
  `explain_error_code('SENZ9000')` names `sz-mcp-coworker selfcheck (airgap binary)` in
  `resolution_steps`; `mapping_workflow(action='start', file_paths=[…], data={'workspace_dir':…})`
  names "stdio/airgap mode" in its step-1 resource instructions; `sdk_guide(topic='install',
  platform='linux_apt')` and `sdk_guide(topic='install', platform='macos_arm', language='python')`
  return no stdio or `extract` content, confirming that half of the note.
  `owner-checked: search_docs(query='sz-mcp-coworker selfcheck airgap binary stdio mode') — returns
  no sz-mcp-coworker content (4 hits, all unrelated), so the corpus genuinely does not document the
  route and the Revisit-if condition is still unmet.`
- Upstream: not applicable — this is a defect in our own record, not in the server.
- Related specs: `specs/no-route-for-bootcampers-who-cannot-add-an-mcp-server.md` (the declined
  spec this note sits on), `specs/declined-ledger-negatives-are-invisible-to-the-scanner.md` (the
  class defect that let it through), `specs/mcp-negative-markers-must-name-the-owning-route.md`
  (INV-194, the rule this violates)

## Deviations from this spec, and why (2026-08-13)

Implemented as written; four things differ from the text, all recorded rather than silently
absorbed.

1. **The `search_docs` hit count is 10, not 4.** This spec's `MCP re-check` line records "four
   hits, all unrelated" for `search_docs(query='sz-mcp-coworker selfcheck airgap binary stdio
   mode')`. Re-run at implementation (server 1.32.9, 2026-08-13, same query, no `max_results`)
   it returned **10**, still with no `sz-mcp-coworker` content — the top hit the same Scala
   `SelfCheck.scala` in `brianmacy/sz_spark`, plus the `@senzing/sdk-*` npm prebuilt-binary
   tables and unrelated loaders. The substance is unchanged and the conclusion stands; the note
   records 10 at the default `max_results`, because writing 4 would have been copied from here
   rather than observed (INV-080).
2. **The parent bullet's "and it has moved further away" was removed too.** Proposed change 2
   names only the "narrowed from two to one" sentence, but the heading clause was the same
   conclusion stated earlier in the entry and derived from the same retracted sub-claim. It now
   reads "condition NOT met." — the decision fields are untouched, as required.
3. **The `sdk_guide` half was re-confirmed on `platform='linux_apt'` and on the tool manifest**
   inside `get_capabilities`, not on `platform='macos_arm', language='python'` as this spec's
   re-check line also cites. Both surfaces settle it: the manifest's `sdk_guide` description
   names neither stdio nor `extract`, and the `linux_apt` install response offers
   `direct_download` .deb URLs plus `dpkg-deb -x` as its firewalled-environment route instead.
4. **Two `MCP-NEGATIVE` markers and one `MCP-NEGATIVE-SCAN: quoted-history` escape were added
   to the note**, which this spec does not ask for. That is
   `specs/declined-ledger-negatives-are-invisible-to-the-scanner.md`'s proposed change 2,
   implemented in the same session; recorded here because it changed this file.
