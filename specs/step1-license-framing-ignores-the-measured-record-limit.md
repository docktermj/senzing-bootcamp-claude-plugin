# Data processing Step 1's license framing ignores the measured `license_record_limit`, contradicting the reconciliation rule 30 lines below it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-06-data-processing/phaseA-build-loading.md` contains two blocks that decide what to say
about licensing, they key on **different state**, and they give **opposite answers** for the same
bootcamper.

**Block 1 — Step 1's "License framing (default + expansion paths)"** (`:100-118`), which fires
immediately after the production-volume tier is classified:

> Frame the built-in evaluation license as the default they already have. Present the expansion
> paths — apply an existing license, request one through the external channel
> (<support@senzing.com>), and, when available, request one in-flow via the Senzing MCP server —
> before any mention of downsizing.
> […]
> If the bootcamper already has a license (`license` set in `config/bootcamp_preferences.yaml`),
> route them to the apply-an-existing-license path and omit the in-flow option.

Its only escape hatch keys on **`license` in `config/bootcamp_preferences.yaml`**.

**Block 2 — the `sdk_guide` licensing-verdict reconciliation** (`:158-166`), thirty lines later:

> Read `license_record_limit` from `config/bootcamp_progress.json` […]
> - **`0` (no cap), or ≥ the dataset size** — the note does not apply. **Suppress it entirely**: say
>   nothing about licenses or sampling, take the returned code, and ignore the licensing prose. A
>   warning the bootcamper cannot act on is noise (INV-012).

It keys on **`license_record_limit` in `config/bootcamp_progress.json`** — the field INV-244 makes
authoritative, because it is *measured* from `SzProduct.get_license()` rather than assumed.

**These two states come apart on a normal path, and did on this run.** Observed 2026-08-27 walking
the module for real:

```text
config/bootcamp_preferences.yaml : license           -> NOT SET
config/bootcamp_progress.json    : license_record_limit -> 0   (measured, no cap)

Step 1 license framing  -> 'license' unset -> frame the built-in eval license, offer expansion paths
Reconciliation section  -> license_record_limit = 0 -> suppress ALL license/sampling talk
```

So Step 1 tells a bootcamper whose license has been **measured as uncapped** that their default is
the built-in evaluation license, and offers them three ways to expand a capacity they are not
constrained by. That is precisely the output the reconciliation block calls *"noise (INV-012)"* —
delivered by the block that runs first.

**Why the two states come apart is not an edge case.** `license` is written to preferences only by
Module 4 Step 8a's **apply** (sub-step 5) or **obtain** (sub-step 6) paths. `license_record_limit`
is written by Step 8a sub-step 7's **measurement**. A bootcamper who simply *has* a good license —
no application, no request needed — gets the measurement and never gets the `license` key. That is
the ordinary case for anyone with a corporate or internal license already installed, and it is the
case this run hit without contriving anything.

⚠️ **The reconciliation block is right and needs no change.** It is careful, it cites INV-244 and
INV-012, and it explicitly walks the "absent or null → measure it → re-enter these three branches"
path. The defect is that Step 1's framing was written against a different, older model of the state
(is there a `license` key?) and never picked up the measured field the rest of the module now
treats as authoritative.

## Root cause

Two decision points over one fact, added at different times, reading different fields:

- Step 1's framing predates the INV-244 measurement discipline and asks *"has a license been
  applied or requested?"* (`license` in preferences).
- The reconciliation block asks *"what is the license's actual record limit?"*
  (`license_record_limit` in progress), which is the question that determines whether any licensing
  talk is actionable at all.

`license` and `license_record_limit` answer different questions and are written by different
sub-steps, so neither implies the other. Nothing in Step 1 points at the reconciliation block, and
nothing in the reconciliation block scopes itself to "the `sdk_guide` note only, not Step 1's
framing" — so on a plain reading they simply conflict.

## Proposed change

1. **Make Step 1's license framing read `license_record_limit` first**, and suppress itself on the
   same branch the reconciliation block already defines: when the measured limit is `0` or ≥ the
   dataset size, say nothing about licensing here — no default framing, no expansion paths. The
   bootcamper is not constrained, so there is nothing to act on.
2. **State the precedence once, and cite it from both places rather than restating it** (INV-179).
   The rule is: *a measured `license_record_limit` governs; `license` in preferences records only
   how the license was obtained and never substitutes for the measurement.* The reconciliation
   block's three branches are already the canonical statement — Step 1 should defer to them by
   reference.
3. **Keep the `license`-key clause as a narrowing, not a gate.** It is still useful for choosing
   *which* expansion path to show when licensing genuinely is in scope; it just must not be the
   thing that decides *whether* licensing is in scope.
4. ⛔ **Do not fix this by having Step 1 measure the license again.** Module 4 Step 8a already
   measured and persisted it; re-measuring here would duplicate the SDK call the module explicitly
   routes through one place, and would diverge if the two disagreed.

## Acceptance criteria

- [ ] With `license_record_limit: 0` in `config/bootcamp_progress.json` and `license` **unset** in
      `config/bootcamp_preferences.yaml`, Step 1 emits **no** licensing framing and **no** expansion
      paths — matching the reconciliation block's "suppress it entirely" branch.
- [ ] With a positive `license_record_limit` below the dataset size, Step 1's framing still appears
      and still presents expansion before downsizing (today's behavior for the case where it is
      correct).
- [ ] With `license_record_limit` genuinely absent, Step 1 follows the existing INV-244 path
      (measure, persist, re-enter the branches) rather than assuming the built-in limit.
- [ ] `phaseA-build-loading.md` states the `license` vs `license_record_limit` precedence once and
      cites it from Step 1 rather than duplicating the three branches (INV-179).
- [ ] A test asserts Step 1's framing block references `license_record_limit`, so the two decision
      points cannot silently drift apart again. Stdlib only, no `plugins/` import (INV-108).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — Step 1's
  "License framing (default + expansion paths)" block at `:100-118`
- `tests/` — a guard that Step 1's framing consults the measured limit

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-27, in the **analysis stretch** at the
  maintainer-chosen start module (Data processing), while executing Step 1 for real
  (`Source: self-observed (assistant retrospective)`). Surfaced because the walk had actually
  measured the license in Module 4 and carried `license_record_limit: 0` forward — a static read of
  either block alone looks correct, and only running both against the same live state shows them
  disagreeing.
- Priority: **Medium.** Nothing breaks and no load is blocked, but a bootcamper with an uncapped
  license is handed licensing framing and three expansion paths for a constraint they do not have —
  the exact INV-012 "output the bootcamper cannot act on" the neighboring block forbids by name.
  It also undercuts INV-244: the module measures the license precisely so it can stop guessing, and
  then the first place that talks about licensing ignores the measurement. Not High because the
  consequence is noise rather than a wrong action, and the reconciliation block still prevents the
  damaging half (being told to sample down).
- MCP re-check: **n/a (no Senzing fact).** The defect is entirely in the plugin's own cross-block
  state handling — which of two project files a step reads. No Senzing behavior, SDK surface or
  server claim is involved, so there is nothing to re-verify and no absence claim to substantiate.
  `get_capabilities` was called at the start of this run to date it: server **1.33.0**, 2026-08-27.
  The measured `recordLimit: 0` quoted above came from `SzProduct.get_license()` on this machine
  (SDK 4.3.4) — an environment observation, correctly marked as such (INV-080/INV-149).
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `specs/no-license-path-environment-variable.md` (the INV-244 lineage — measuring
  rather than assuming license state); `specs/mcp-tools-disagree-on-eval-license-duration.md` (the
  other licensing-facts spec, upstream rather than internal)

## Deviations from this spec, and why (2026-08-28)

**None on content.** The root cause was re-confirmed in the code before anything changed: Step 1's
framing at `phaseA-build-loading.md:96-108` keyed on `license` in `config/bootcamp_preferences.yaml`,
while the reconciliation block at `:158-166` keyed on the measured `license_record_limit` — two
decision points over one fact, thirty lines apart, giving opposite answers.

**MCP re-check: n/a, as the spec states — and re-confirmed as n/a rather than assumed.** The defect is
entirely in this plugin's cross-block state handling: which of two project files a step reads. No
Senzing behavior, SDK surface or server claim is involved, and the fix asserts no new Senzing fact.
`get_capabilities` was called this session to date the run: server **1.33.0**, 2026-08-28.

**A sweep for other sites found none — and one file that looked like a hit is correct.**
`module-04-data-collection/SKILL.md:803-810` reads *both* signals (`license: custom` **or** a
`license_record_limit` reflecting a custom key) and carries its own volume-skip that handles `0`
explicitly, so Step 8a does not have this defect and was left untouched. Recording the near-miss
because "the spec named one site" is not evidence there was only one (INV-246); here, checking
confirmed there was.

**The precedence rule was already written — Step 1 now cites it instead of a second copy.** The
spec's proposed change item 2 asked for the rule to be stated once and referenced from both places.
It turned out the reconciliation block at `:174-183` already says it (*"a value you measured on this
machine governs over generic guidance about that same value"*), so the implementation points Step 1
at those branches by name rather than adding a third statement of them (INV-179). The guard asserts
`suppress it entirely` appears exactly **once** in the file, so a future edit cannot reintroduce the
duplication that caused the drift.

⚠️ **Two criteria are implemented but not runtime-verified**, and are disclosed rather than ticked:
the behavior with `license_record_limit: 0` and with a positive sub-dataset limit is asserted as
**text** in a shipped instruction file. Whether a guide actually suppresses the framing on a live run
is a runtime property no offline test can see (INV-108); it needs a `dry-run` phase-3 walk through
Data processing Step 1 with each of the three states set.
