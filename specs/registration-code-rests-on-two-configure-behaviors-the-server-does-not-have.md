# The generated registration code rests on two `configure` behaviors the server does not have

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two retrospective findings from one bootcamp run, both landing on the same paragraph — the
instruction that tells the guide how to produce `register_data_sources.[ext]`. Each is a Senzing
fact the plugin implicitly relies on, and neither holds.

**1. `sdk_guide(topic='configure')` accepts `data_sources` and never puts them in the snippet.**
The tool's schema documents the parameter as *"Data sources to register (for configure topic)"*.
Called with the bootcamper's three codes, the returned snippet still carried the hardcoded sample
tuple, with a note saying to replace them. A guide that reasonably assumes the snippet is
parameterized ships code registering three codes the bootcamper does not have — and the first load
then fails with `SENZ2207` for the codes they **do** have, which is the exact failure step 4a exists
to prevent.

**2. Idempotency was coded against a documented error the Python binding does not raise.** Step 4a
requires the registration code to be idempotent. Searching for the documented failure mode returned
an SDK reference stating that re-registering an existing code raises `BadInput`, so the script was
written to catch that per code. Run twice against the same config, all three codes reported as newly
registered **both** times, with an identical new config ID (`3975847437`): nothing was raised and the
`except` branch never executed. The net result was still idempotent — but by a different mechanism
than the one the code was written to rely on, so the handling was dead code that would fail in
exactly the case it existed for.

## Root cause

### The shipped instruction, and what each half assumes

`module-06-data-processing/phaseA-build-loading.md:277-289` (step 4a item 2):

> **Generate the registration code from the MCP server** (never hand-write it): call
> `sdk_guide(topic='configure')` … The generated code MUST load the current default config,
> register each code from step 1, set the updated config as the new default, and be **idempotent** —
> a code already registered is treated as success, not an error, so re-runs and multi-source
> orchestration stay safe.

`module-03-system-verification/phase1-verification.md:409-411` states the same idempotency rule in
the same words for Module 3's `VERIFY` registration, and
`module-03b-truthset-visualization/phase1-visualization.md:170`,
`module-05-data-quality-mapping/phase3-test-load.md:45` and
`module-06-data-processing/phaseC-multi-source.md:138` all require "idempotently" by reference. So
this is one wording at two statement sites and three referring sites, not one line.

### 1. The parameter selects a snippet; it never substitutes values

**Still reproduces on MCP server 1.32.9, verified 2026-08-17.**
`sdk_guide(topic='configure', language='python', data_sources=["ECOMMERCE_ORDERS", "POS_LOYALTY", "EMAIL_MARKETING"])`
returns, verbatim:

```python
    for data_source in ("CUSTOMERS", "REFERENCE", "WATCHLIST"):
        sz_config.register_data_source(data_source)
```

with `notes` still reading *"Replace sample data source names with your own"*. None of the three
supplied codes appears anywhere in the response.

⚠️ **The parameter is not inert, which is the part that makes this a plugin problem and not only an
upstream one.** `specs/sdk-guide-configure-now-leads-with-seeding.md` established, and this
re-check confirms, that `data_sources` is the **discriminator** for which snippet is primary:
passing it returns `python/configuration/register_data_sources.py`, omitting it returns
`python/configuration/init_default_config.py`. The 1.32.9 response also carries a
`compatibility_notes` entry that exists only on the `data_sources` branch ("If you haven't confirmed
a default config exists yet, call `sdk_guide(topic='configure', ...)` WITHOUT `data_sources` first").

So the parameter **selects** correctly and **substitutes** not at all, and step 4a's shipped call
lands on the wrong side of that: it says `sdk_guide(topic='configure')` with no `data_sources`, which
makes the **seeding** snippet primary — not the registration snippet step 4a needs. A guide that
notices and adds `data_sources` gets the right snippet with the wrong codes. Both routes need the
substitution said out loud, and step 4a's own item 1 already forbids the outcome: *"Never register a
code that is not present in the data."*

Module 2 already handles this correctly — `module-02-sdk-setup/SKILL.md:1347-1348` ships the
discriminator as a two-row table keyed by `source_path`. Step 4a never inherited it.

### 2. The raised-error contract is a community Rust doc, and the owning route states no contract at all

**Still reproduces on MCP server 1.32.9 (docs index 2026-08-11 20:52 UTC), verified 2026-08-17.**
`search_docs(query='register_data_source already exists idempotent duplicate', category='sdk')`
returns as its **top** hit (relevance 32.9) the Rust `SzConfig` trait doc:

> **Errors** — `SzError::BadInput` - Data source code is invalid or already exists

Two things the entry did not record, both of which sharpen the finding:

- **The doc is a community wrapper's, not an official Senzing SDK's.** `get_capabilities` (1.32.9)
  states the index covers "SDK documentation (Python, Java, C# official; Rust, TypeScript/Node.js
  community), … plus Rust and TypeScript/Node.js (community-maintained wrappers, **not official
  Senzing SDKs**)", and the hit's `source_url` is `brianmacy.github.io/sz-rust-sdk`. So the
  cross-binding hazard is worse than "a Rust trait doc answered a Python question": a
  community-maintained doc answered a question about an official binding, and nothing in the result
  says so.
- **The route that owns the method's contract states no errors at all.**
  `get_sdk_reference(topic='parameters', filter='register_data_source', language='python')` returns
  `register_data_source(data_source_code: str) -> str` with warnings only about argument types
  across bindings — no error condition for any binding. There is therefore no authoritative
  raised-error contract for this method to code against, in any language.

**The server and the observation do not contradict each other (INV-169).** The community Rust doc
describes the Rust wrapper; the observation is the official Python binding, SDK 4.3.4 (build
4.3.4.26210), Linux, 2026-08-17. Those are two bindings, not one disagreement, and the spec must not
flatten them into "`register_data_source` never raises" — an absolute nobody measured. What is
established is narrower and sufficient: **the plugin must not make idempotency depend on an error
being raised, because no route documents one for the bootcamper's binding.**

**The server corroborates the mechanism that actually made it idempotent.** The same `search_docs`
call returned Senzing's own release notes: *"Fix `G2ConfigMgr.addConfig` function to return success
and the ConfigID if the configuration already exists."* Different method — the config-registration
step, not the data-source step — but it is the documented behavior behind the identical config ID
observed on the second run. Idempotency held **by construction**, one call later than where the code
was watching for it.

## Proposed change

1. **State the discriminator and the substitution at step 4a item 2**, in the shape Module 2 already
   uses: pass `data_sources` so the **registration** snippet is primary, locate it by
   `source_path` rather than by position, and then **substitute the codes from step 1 into the
   returned snippet** — the parameter selects the snippet and does not fill in its values. Cite the
   call, server version and date that establish it.
2. **Re-point the idempotency requirement at construction, not at error handling.** Replace *"a code
   already registered is treated as success, not an error"* — at both statement sites
   (`phaseA-build-loading.md` step 4a and `phase1-verification.md` step 2) — with a requirement that
   the sequence itself be safe to re-run: load the current default config, register each code,
   export, register the config, and replace the default config ID. Say that re-registering an
   identical config returns the existing config ID, attributed to the release note above.
3. **Permit an error catch as a fallback and forbid it as the mechanism.** A guide may still catch a
   per-code error, but the step must say plainly that **no route documents one for any binding**, so
   a script whose idempotency depends on that catch is untested by construction. This is the
   generalizable half.
4. **Warn about the community-doc hazard where the search happens.** A ⛔ noting that
   `search_docs(category='sdk')` indexes community-maintained Rust and TypeScript wrapper docs
   alongside the official Python/Java/C# ones, so an error contract found there is not necessarily
   the contract for the bootcamper's binding — `get_sdk_reference(…, language=…)` is the route that
   answers per binding. `get_sdk_reference` already warns about name and type divergence across
   bindings; error-condition divergence is the gap, and this is the plugin's own note, not a relayed
   server claim.
5. **Stay language-agnostic.** None of the above may name Python's exception type as the contract.
   The instruction is: read the signature for the chosen binding, build for re-runnability, and treat
   any raised error as a fallback path.

**Re-verify before implementing (INV-080).** Re-call both routes. If `data_sources` has started
substituting, item 1 collapses to a version note; if `get_sdk_reference` has gained an error
contract, item 3 changes from "none documented" to relaying it.

## Acceptance criteria

- [ ] Step 4a item 2 names the `data_sources` discriminator, locates the registration snippet by
      `source_path`, and requires the step-1 codes to be substituted into the snippet — with the
      tool, parameters, server version and date cited.
- [ ] No shipped step says a code already registered is "treated as success, not an error" as the
      idempotency mechanism; both statement sites require re-runnability by construction, and the
      three referring sites still resolve to the corrected wording.
- [ ] The plugin nowhere asserts that re-registering an existing code raises, or that it does not
      raise, as a binding-independent fact.
- [ ] The community-versus-official distinction for `search_docs(category='sdk')` is stated once,
      where the lookup is prescribed, and attributed to `get_capabilities`.
- [ ] A test asserts the substitution instruction and the absence of the error-as-mechanism wording
      across all five sites — negative-controlled by restoring the old phrasing at one site and
      confirming the mutation lands.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      changed text is prose plus a tool call that carries the bootcamper's chosen language, and no
      binding's exception type appears as a contract.
- [ ] ⚠️ The idempotency mechanism itself is only fully confirmable against a live engine: the
      criterion is that the **instruction** no longer depends on an undocumented error, not that a
      test observes a second registration.

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — step 4a
  item 2 (`:277-289`): the call, the discriminator, the substitution, the idempotency wording.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — step 2
  (`:400-411`): the same idempotency wording, and the same missing substitution.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md:170`,
  `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md:45`,
  `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md:138` — check each
  still resolves correctly once the referenced wording changes.
- `tests/` — the new guard.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "sdk_guide(topic='configure') ignores its own
  data_sources parameter" (2026-08-17, Module Data processing, Priority Medium) and
  "register_data_source() does not raise on an already-registered code (Python), contrary to the
  indexed SDK reference" (2026-08-17, Module Data processing, Priority Low); both
  `Source: self-observed (assistant retrospective)`. Merged because both are the same fix site —
  step 4a item 2's generated registration code — and because each is a Senzing fact the instruction
  silently assumes.
- Priority: **Medium.** Neither crashes at the step. The first produces a load failure one phase
  later for a universal path (every bootcamper registers their own codes here); the second produces
  handling that looks correct and is untested.
- MCP re-check: **server 1.32.9, docs index 2026-08-11 20:52 UTC, 2026-08-17 — both still
  reproduce.** Tools called: `get_capabilities` (server version, and the official-versus-community
  SDK-doc split); `sdk_guide(topic='configure', language='python', data_sources=[three codes])` →
  snippet still iterates `("CUSTOMERS", "REFERENCE", "WATCHLIST")`;
  `search_docs(query='register_data_source already exists idempotent duplicate', category='sdk')` →
  Rust `SzConfig` trait doc, `SzError::BadInput` "invalid or already exists", plus the
  `G2ConfigMgr.addConfig` release note. The claim that no raised-error contract is served for the
  official bindings is **owner-checked: `get_sdk_reference(topic='parameters',
  filter='register_data_source', language='python')` — returns the signature
  `register_data_source(data_source_code: str) -> str` with cross-binding argument-type warnings and
  no error condition for any binding**.
- Upstream: **already sent 2026-08-17** for both findings as filed (per both entries' `Upstream:`
  field — batched via `submit_feedback`, category `bug`, anonymous, so no reply is possible). No
  follow-up on those two: the re-check adds only that both still reproduce on 1.32.9, which the
  same-day submission already described. **One new finding the re-check produced was sent
  separately, 2026-08-17, via `submit_feedback` (category `feature`, anonymous), with the
  maintainer's approval of the exact text**: `search_docs(category='sdk')` results carry no field
  marking a hit as community-maintained rather than official, which is the mechanism by which the
  Rust error contract was adopted for the official Python binding. That is a retrieval-labeling gap,
  distinct from the doc-content report already filed, and it is the reason item 4 of the proposed
  change is a plugin-side warning rather than a wait for the server. There is no ticket id —
  submissions are anonymous — so this note is the only record.
- Related specs: `specs/sdk-guide-configure-now-leads-with-seeding.md` (established the
  `data_sources` discriminator and Module 2's two-row table),
  `specs/sdk-guide-configure-unseeded-datastore.md`, `specs/module6-register-data-sources-before-load.md`
  (created step 4a), `specs/module3-register-truthset-data-sources.md`,
  `specs/sdk-reference-carries-signatures-under-every-topic.md`.
