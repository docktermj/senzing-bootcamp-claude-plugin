# Step 4's dated snippet count for `workflow='initialize'` is now wrong in its particulars

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 2 Step 4 carries a ⛔ warning that `generate_scaffold(workflow='initialize')` cannot satisfy
the verification step on its own, because it never prints the SDK version. The warning is **correct**
and load-bearing. Its supporting evidence is now stale.

`module-02-sdk-setup/SKILL.md:670-676`:

> ⛔ **`workflow='initialize'` alone cannot satisfy this step.** Verified live (server 1.32.2,
> 2026-07-29): it returns **ten snippets, every one under `initialization/`** — abstract-factory
> variants, `engine_priming`, `purge_repository`, `factory_destroy`, `signal_handler`,
> `sz_engine_config_ini_to_json` — and **none of them prints the version**.

Called live on **server 1.32.9, 2026-08-12**, `generate_scaffold(language='python',
workflow='initialize', version='current')` returns **14 snippets**: the ten under
`python/initialization/` as described, **plus four under `python/configuration/`** —
`get_config_registry.py`, `get_data_source_registry.py`, `init_default_config.py`,
`register_data_sources.py`.

So two clauses are now false: the count ("ten") and the scope ("every one under `initialization/`").

**What is still true, and why that matters.** None of the 14 prints the version — there is no
`get_version.py` among them. The ⛔'s conclusion therefore stands, and the paired call it prescribes
is confirmed: `generate_scaffold(workflow='information')` returns
`python/information/get_version.py` (same server, same date). The two-call requirement is right.

**Why a stale detail on a still-correct warning is worth fixing.** The plugin's own re-verification
discipline invites a future editor to check dated claims. An editor who re-runs this call finds 14
snippets spanning two directories where the text promises ten in one, and the natural inference from
"this citation is wrong" is "this warning is obsolete" — deleting a ⛔ whose conclusion is still
valid. The risk is not that the count misleads a Bootcamper (it is internal guidance they never see);
it is that a correct guard looks discredited by its own evidence. `specs/refresh-reverified-provenance-stamps.md`
established the practice of refreshing these stamps for exactly this reason.

There is also a mild second-order point: four `configuration/` snippets now arriving under
`initialize` overlaps Step 8a's territory (seeding the default config), so the sentence understates
what the workflow now offers.

## Root cause

The claim was written from a live call on 2026-07-29 against server 1.32.2 and dated honestly —
which is the correct practice, and is why the drift is detectable at all. The upstream snippet
repository (`senzing/code-snippets-v4`) or the server's workflow-to-directory mapping has since
widened `initialize` to include `configuration/` snippets. Nothing in this repo re-checks it: the
suite is offline and stdlib-only by INV-108, so a dated `generate_scaffold` claim can only be
refreshed by a dry run or an `auto-test` pass.

This is the same class as `tests/test_mcp_call_contracts.py`'s `CONTRACT_VERIFIED_ON` — a static copy
of a live contract, correct when taken, with no mechanism to notice it aging.

## Proposed change

1. **Re-verify and restate the evidence**, keeping the ⛔ and its conclusion intact. Replace the count
   and scope with what the server returns at implementation time, and re-date the stamp. Prefer
   wording that does not re-stale on the next widening — the load-bearing fact is the **absence of a
   version-printing snippet**, not the inventory:

   > Verified live (server &lt;version&gt;, &lt;date&gt;): its snippets are factory/engine **lifecycle**
   > and configuration helpers — **none prints the version**, which lives in
   > `workflow='information'` (`information/get_version.py`).

   That phrasing survives the addition of further snippets, which a hardcoded count cannot.
2. **Leave the paired-call requirement exactly as it is.** Both halves were re-confirmed today; the
   step's actual instruction needs no change.
3. **Optionally note the `configuration/` overlap** where Step 8a cites this workflow, since
   `init_default_config.py` and `register_data_sources.py` now arrive here too.

**Do not delete the ⛔.** Its conclusion is confirmed on 1.32.9. This spec refreshes evidence; it does
not reopen the finding the ⛔ records.

## Acceptance criteria

- [ ] Step 4's ⛔ no longer asserts a snippet count or that every snippet sits under
      `initialization/`, and states the absence of a version-printing snippet as the load-bearing
      fact.
- [ ] The stamp carries the server version and date of the re-verification actually performed at
      implementation time (INV-080) — not this spec's 1.32.9/2026-08-12 copied forward.
- [ ] The ⛔ still forbids citing `workflow='initialize'` alone for Step 4, and the paired
      `workflow='information'` call is still required.
- [ ] `git diff` shows no change to Step 4's actual instructions or to Step 9's separate, correct
      citation of `workflow='initialize'`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md). Note the
      re-verification above is **Python-only**; if the wording implies all bindings, check at least
      one more language or scope the claim to Python.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 4's ⛔ (`:670-676`).

## Source

- Dry run: `dry-run` phase 3, extended into SDK setup at the maintainer's request, 2026-08-12
  (`Source: self-observed (assistant retrospective)`). Found by executing Step 4's two prescribed
  calls rather than reading them — the drift is invisible without the call, and the ⛔'s conclusion
  is correct so nothing else flags it.
- Both calls run against server **1.32.9**: `initialize` → 14 snippets (10 `initialization/`,
  4 `configuration/`), no version print; `information` → 5 snippets including
  `information/get_version.py`.
- Priority: **Low.** Internal guidance only, never seen by a Bootcamper, and the warning it supports
  is still correct. The cost is that a correct guard carries evidence a re-check will contradict.
- MCP re-check: **changed** — count and scope both moved since 2026-07-29; the conclusion did not.
- Upstream: not applicable — the server is free to widen a workflow's snippet set; the plugin's
  citation is what needs refreshing.
- Related specs: `specs/refresh-reverified-provenance-stamps.md` (the established practice for this
  class), `specs/verify-sdk-parameter-shapes-and-flag-families.md`.

## Deviations from this spec, and why (2026-08-12)

Re-verified against **server 1.32.9, 2026-08-12**. Python `initialize` returns **14** snippets — the
10 under `python/initialization/` plus `get_config_registry.py`, `get_data_source_registry.py`,
`init_default_config.py`, `register_data_sources.py` under `python/configuration/` — with **no
version printer**, and `information` returns `python/information/get_version.py`. Exactly as this
spec reports. Three things went further than it asked.

1. **Criterion 6 was satisfied by checking Java, not by scoping the claim to Python — and Java
   changed the reasoning.** `generate_scaffold(language='java', workflow='initialize')` on the same
   server returns **5** snippets under `java/snippets/initialization/` and
   `java/snippets/configuration/`, again with no version printer. So the conclusion generalises while
   the inventory varies **per language in both size and path**, not merely over time. That is a
   stronger argument against ever stating a count than this spec's (which reasons only from the
   widening), and the shipped ⛔ now says so explicitly.

2. **A guard was added, though this spec asks for none.** Its criteria are all prose, and its root
   cause notes the suite cannot re-check a `generate_scaffold` claim offline (INV-108) — true of the
   *fact*, but not of the *shape*: that Step 4's warning states no count is offline-checkable and is
   precisely what regressed. `NoCountRestatesTheSnippetInventory` in
   `tests/test_scaffold_citations_and_database_type.py` asserts no count, the absence-as-load-bearing
   phrasing, a present version+date stamp, and the two-axis explanation; negative-controlled by
   restoring the original "returns ten snippets" wording, verified to land and to fail.

3. **Two further stale copies of the same evidence were refreshed.** Proposed change §3 offers the
   `configuration/` overlap note as optional; Step 8a already carried it, dated 1.32.8/2026-08-11, so
   its stamp was refreshed to today and it now records that the set is language-dependent (Java
   returns the two writers and not the two registry readers). And the **docstring of
   `tests/test_scaffold_citations_and_database_type.py`** restated the retired "ten snippets, all
   under `initialization/`" claim as current fact — the same stale-docstring shape that
   `explain-error-code-now-owns-senz7426` had to fix in a sibling file. Refreshed and de-quantified,
   with the reason recorded inline.

Criterion 4 verified as prescribed: the diff touches Step 4's ⛔, Step 8a's stamp, and (from a
separate spec in the same batch) the SENZ7426 block — Step 4's two prescribed calls and Step 9's
citation are unchanged.
