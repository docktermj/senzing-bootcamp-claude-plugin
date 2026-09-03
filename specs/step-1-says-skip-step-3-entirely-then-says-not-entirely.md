# SDK setup Step 1 says "skip Steps 2 and 3 entirely", then says "Not Step 3 entirely"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-02-sdk-setup/SKILL.md` Step 1 tells the guide two different things about the same step,
27 lines apart.

Line **90**, closing the filesystem-fallback paragraph:

> If the library is present, report the SDK as installed, **skip Steps 2 and 3 entirely**, and
> proceed to Step 4 verification.

Line **117**, in the `If the SDK is found and version is V4.0+` branch:

> - **Skip the *installation* — Step 2, and Step 3's install commands.** **Not Step 3 entirely:**
>   see the required stop below.

They cannot both be followed. And the file itself spells out, at length, what following the first
one costs:

> Skipping both leaves the bootcamper with a healthy install and no environment, and every later
> module then fails at import with `libSz.so: cannot open shared object file` — which reads as a
> broken install, in a *later* module, far from this decision.

**This is not hypothetical — the failing state is what the check actually finds.** Observed live on
2026-08-31, Ubuntu 24.04.4, Python 3.12.3:

- The Python import check **failed**: `senzing_core/_helpers.py` → `cdll.LoadLibrary("libSz.so")`
  raised, because `LD_LIBRARY_PATH` was unset.
- The native library **is present**: `/opt/senzing/er/lib/libSz.so`, 453,728,152 bytes.
- `szBuildVersion.json` reports `VERSION: 4.4.0` — comfortably above the V4.0 floor.

So the machine is in precisely the state Step 1's fallback was written to detect: a healthy install
with no environment. A guide that reached line 90 first, followed it, and skipped Step 3 would leave
that machine exactly as it found it — and the bootcamper would meet the failure several modules
later, with nothing connecting it back to this decision.

The line-90 reading is also the *more likely* one to be taken. It is the concluding sentence of the
paragraph a guide is reading at the moment the check succeeds, phrased as a complete instruction
("report … skip … proceed"), while the correction lives inside a branch further down under a
different heading.

## Root cause

`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:90` was written when the fallback was
about *detecting* the install, and it states the consequence in terms of the two install steps. The
Step 3 carve-out at line 117, and the "Required stops" block beneath it, were added later to fix
exactly this hazard — but line 90 was not updated to match, so the file now contains the pre-fix
instruction and the fix side by side.

The residual ambiguity is small and total: **which of the two a guide follows depends on which it
reads first**, and line 90 comes first.

## Proposed change

Rewrite line 90 so it cannot be read as licensing a skip of Step 3's environment-script work.
Suggested:

> If the library is present, report the SDK as installed and skip the **installation** — Step 2, and
> Step 3's install commands. Step 3's environment-script work still runs; see "Required stops" in
> the V4.0+ branch below. Then proceed to Step 4 verification.

This keeps line 90's job (tell the guide what a successful fallback means) and removes the only
clause that contradicts line 117. Do not solve it by deleting line 90 — a guide arriving via the
fallback needs an instruction at that point, and an unterminated paragraph would send them hunting.

## Acceptance criteria

- [ ] No line in Step 1 instructs skipping Step 3 in full; every statement about skipping names the
      *installation* specifically.
- [ ] Following Step 1 from the filesystem-fallback path alone — without reading the V4.0+ branch —
      still routes the guide through Step 3's environment-script work.
- [ ] The "Required stops" block (Step 3's environment script, Step 4, Step 5) is unchanged.
- [ ] A grep for `skip Steps 2 and 3 entirely` in `plugins/` returns nothing.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — line 90: restate the skip as the
  installation only, and point at the required stops.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, SDK setup Step 1
  (`Source: self-observed (assistant retrospective)`) — found by running Step 1's check on a machine
  that is in the exact state the step's fallback describes: native library present, import failing
  for want of `LD_LIBRARY_PATH`. No previous phase-3 walk had an SDK installed, so no previous walk
  could reach this branch.
- Priority: Medium
- MCP re-check: server **1.35.1**, 2026-08-31 —
  `sdk_guide(topic='install', platform='linux_apt', language='python')` confirms the environment
  variables the script must export (`PYTHONPATH=/opt/senzing/er/sdk/python`,
  `LD_LIBRARY_PATH=/opt/senzing/er/lib`) and states *"Do NOT pip install them — instead set
  PYTHONPATH … and LD_LIBRARY_PATH …"*, which is what makes the environment script load-bearing
  rather than cosmetic on this platform.
- Upstream: not applicable — the contradiction is internal to the plugin.
- Related specs: none
