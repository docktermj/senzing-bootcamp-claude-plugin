# `explain_error_code('SENZ7426')` now names SUPPORTPATH first; the plugin still tells the guide to suppress it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The plugin instructs the guide to **withhold a tool's output** for `SENZ7426`, on the grounds that
the output is unhelpful. That was true when written. It is now false, and the suppressed output is
the best diagnosis available.

**What the server returns now.** `explain_error_code('7426')` on **MCP server 1.32.9, 2026-08-12**:

> `common_causes[0]`: *"SUPPORTPATH points at a directory with no transliteration modules — the
> engine aborts with 'No transliteration rules found! Transliteration requires at least one module.'
> **This is a configuration error, NOT a broken install**"*
> `common_causes[1]`: *"Fails on getEngine()/getDiagnostic()/addRecord() while SzProduct keeps
> working (it needs no support data), so the install looks healthy"*
> `common_causes[2]`: the macOS Homebrew cask's shipped `etc/sz_engine_config.ini` pointing at a
> nonexistent `er/data`
> `common_causes[3]`: Windows Scoop installing support data to a **sibling** of `er`
> `resolution_steps[0]`: *"**Check SUPPORTPATH FIRST** — confirm the directory exists and contains
> the `*TransRules.sz` transliteration modules (plus address_datamodel, nomicon)"*
> `resolution_steps[1]`/`[2]`: the exact macOS and Windows fixes
> `resolution_steps[3]`: *"See sdk_guide topic='install' for your platform"*

That is the plugin's own diagnosis, its own remedy, its own two platform cases, and a pointer to the
tool the plugin currently credits instead. The input-encoding cause still exists but is ranked
**last** and explicitly conditioned: *"only when the error occurs on a record operation after the
engine has initialized successfully."* The exact misdirection the plugin suppresses the tool to
avoid is now handled by the server itself.

**Three shipped claims are now wrong.**

1. `module-03-system-verification/phase1-verification.md:138-141` — *"send them to the same Step 8
   check — and **do not relay what `explain_error_code` returned** for it … `explain_error_code`
   ('SENZ7426') returns only generic input-validation causes and names no connection to
   `SUPPORTPATH` (both re-checked on MCP server 1.32.3, 2026-07-31)."*
   This is a standing instruction to discard the correct answer mid-failure.
2. `module-02-sdk-setup/SKILL.md:940-946` — *"⛔ Attribute this to `sdk_guide`, **not** to
   `explain_error_code`: re-checked on 1.32.3, 2026-07-31, `explain_error_code('SENZ7426')` still
   returns only generic input-validation causes (malformed input, missing `DATA_SOURCE`/`RECORD_ID`,
   bad JSON encoding) and makes no connection to `SUPPORTPATH`."*
   Every clause after "re-checked" is now false, and it is dated and cited, so it reads as verified.
3. `tests/test_engine_verification_and_senz2027.py:113-114` — the docstring asserts
   *"`explain_error_code('SENZ7426')` returns generic transliteration causes and makes no SUPPORTPATH
   connection — **re-verified 2026-07-31, still true**."*

**And a test actively protects the false claim.** `test_senz7426_is_never_tied_to_supportpath_
unconditionally` (`:141`) skips its check whenever the surrounding window matches a `denial` regex
(`:155-158`):

```python
denial = re.search(r"(?i)explain_error_code[^.]{0,220}?(?:generic|makes no|no connection)", window)
if denial:
    continue
```

The comment calls this *"the safety text, not the claim"*. The sentence it exempts is now the
inaccurate one, so correcting the prose **removes the exemption** and the same window must then
satisfy the platform-condition branch. Anyone fixing site 1 or 2 will trip a guard whose docstring
tells them the opposite of what the server says — which is how a correct fix gets reverted.

**Live reproduction, this session.** Initializing an engine against a minimal
`engine_config.json` (`{"PIPELINE": {}}`, no `SUPPORTPATH`) failed with exactly
`SENZ7426 | Transliteration failed: No transliteration rules found! Transliteration requires at
least one module.` — thrown at engine construction, before any record. Confirms the failure shape
both the plugin and the server describe; the disagreement is only about which tool explains it.

**What must NOT change.** The guard's *rule* is still correct and INV-169 still requires it: an
**unconditioned** "SENZ7426 means SUPPORTPATH" is an over-generalization, because the server itself
lists a genuine record-level encoding cause. This spec narrows what the plugin claims about
`explain_error_code`; it must not relax the ban on the absolute.

## Root cause

Two dated re-checks (2026-07-28, 2026-07-31) both found `explain_error_code('SENZ7426')` unhelpful,
so the plugin routed around it and wrote the routing down as a durable fact with provenance. The
server has since gained the coverage. Nothing re-asks: the claim is a **negative** about a tool's
content, and no test can detect that a negative went stale without calling the tool — which INV-108
forbids the suite from doing.

This is the **second** instance of the class. `senz7221-now-names-its-own-remedy` (2026-07-30) was
the first: same tool, same shape — the plugin said the explanation named no remedy, the server had
gained one, and *"one of them had pinned the false premise"* there too. That ledger entry explicitly
anticipated recurrence: *"a fifth instance of this class would be the better trigger"* for an
invariant. Recording the count here so the threshold is countable rather than remembered.

## Proposed change

1. **`phase1-verification.md` (Step 3b)** — delete the do-not-relay instruction. Present what
   `explain_error_code` returns (step 2 already says to), and keep the Step 8 SUPPORTPATH routing as
   corroboration rather than as a correction of the tool. Re-verify and re-date the citation.
2. **`module-02-sdk-setup/SKILL.md`** — replace the ⛔ attribution block. `sdk_guide` and
   `explain_error_code` now **agree**; say so, and keep `sdk_guide` cited for the per-platform
   install detail it still owns. Do not simply delete the passage: its point — ask the tool that owns
   the fact — is still right, and the two-tools-two-coverages example is now obsolete rather than
   wrong in principle.
3. **`tests/test_engine_verification_and_senz2027.py`** — correct the docstring, and **remove the
   `denial` exemption** now that the sentence it protected is going. Keep
   `test_senz7426_is_never_tied_to_supportpath_unconditionally` and its platform-condition
   requirement intact (INV-169). Follow the SENZ7221 precedent: invert or rescope the stale
   assertion rather than deleting the guard.
4. **Add a guard against the negative going stale again** — assert that no shipped file tells the
   guide to withhold or discount `explain_error_code` output for a specific code. That is the
   durable form of both instances of this class, and unlike the underlying fact it needs no network.

**Re-verify before implementing (INV-080).** Call `explain_error_code('SENZ7426')` and quote what it
returns then, not this spec's copy. If the coverage has regressed, the current wording may be right
again — in which case record that and stop.

## Acceptance criteria

- [ ] No shipped file instructs the guide to withhold, not relay, or discount what
      `explain_error_code` returns for `SENZ7426`.
- [ ] Neither `phase1-verification.md` nor `module-02-sdk-setup/SKILL.md` asserts that
      `explain_error_code('SENZ7426')` returns only generic/input-validation causes or makes no
      SUPPORTPATH connection; both carry a re-verified citation with the server version and date.
- [ ] `test_senz7426_is_never_tied_to_supportpath_unconditionally` still fails an **unconditioned**
      SENZ7426/SUPPORTPATH pairing (INV-169 preserved), and its `denial` exemption is gone, and its
      docstring no longer states the retired claim as current fact.
- [ ] A new guard fails if any shipped file tells the guide to suppress `explain_error_code` output
      for a named code. Negative-controlled, with the mutation verified to land.
- [ ] The SENZ2027 guidance is **untouched** — `explain_error_code('SENZ2027')` was a stub as of
      2026-07-30 and this spec is scoped to 7426. Confirm by `git diff` showing no SENZ2027 change,
      and re-check 2027 separately before generalising anything across codes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md). The macOS
      and Windows SUPPORTPATH cases are **documentation** here; neither is runtime-verified without
      a host of each.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — Step 3b
  (`:138-146`).
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — the ⛔ attribution block
  (`:940-946`).
- `tests/test_engine_verification_and_senz2027.py` — docstring (`:113-114`) and the `denial`
  exemption (`:155-160`).
- `tests/` — the new suppression guard.

## Source

- Dry run: `dry-run` phase 2 (hooks and scripts), 2026-08-12, server **1.32.9**
  (`Source: self-observed (assistant retrospective)`). Found by reproducing `SENZ7426` live against
  the scratch project's minimal `engine_config.json`, then asking the tool the plugin says not to
  ask.
- Live repro: `SzAbstractFactoryCore(...).create_engine()` with `{"PIPELINE": {}}` →
  `SENZ7426 | Transliteration failed: No transliteration rules found!`, at construction.
- Priority: **Medium-high.** A live, wrong instruction on a documented path: Module 3 Step 3b runs
  when a Bootcamper's engine fails, and it currently discards the answer that would fix them. No
  Bootcamper is harmed silently — they are harmed slowly, by being sent to a Step 8 check without the
  tool's own ranked causes.
- MCP re-check: **already fixed upstream.** `explain_error_code('7426')` on 1.32.9, 2026-08-12 now
  names SUPPORTPATH as `common_causes[0]` and *"Check SUPPORTPATH FIRST"* as `resolution_steps[0]`,
  with both platform cases. Tool called: `explain_error_code`. The plugin carries a workaround for a
  server gap that no longer exists.
- Upstream: **not applicable** — the server is now correct; the plugin is the stale party. Nothing to
  file.
- Related specs: `specs/senz7221-now-names-its-own-remedy.md` (instance 1 of this class, 2026-07-30),
  `specs/supportpath-failure-code-and-szproduct-masking.md`,
  `specs/supportpath-trap-is-not-windows-only.md`.
