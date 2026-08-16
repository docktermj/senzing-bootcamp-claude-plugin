# SENZING_LICENSE_PATH is a confabulation; the real variable is SENZING_LICENSE_FILE

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

> ⚠️ **This spec was substantially wrong on first writing and was corrected the same day.** Its
> original claim — that Senzing reads *no* license environment variable — was false, and the fix it
> prescribed removed a **true** statement from module-02 and shipped a guard that banned the
> **correct** variable name. The section "The error in the first version" below records what
> happened, because the mistake is more instructive than the defect.

## Problem

`graduation/SKILL.md:749` wrote **`SENZING_LICENSE_PATH`** into the `.env.example` that the
bootcamper carries into production. No MCP tool returns that spelling. A bootcamper who sets it gets
no license, and the failure surfaces much later as a capacity error (`SENZ9000|LIMIT`) with nothing
pointing back at the unread variable. Wrong environment-variable names are on the MCP server's own
`common_confabulations` list.

The correct spelling is **`SENZING_LICENSE_FILE`**.

## Root cause

The plugin held a remembered variable name instead of the server's. Compounding it, the correct name
is reachable through **exactly one** tool route, and it is not one of the routes a reader would try
first — which is how a second, worse error got layered on top (below).

Live MCP server, **1.32.9, verified 2026-08-13**:

- ✅ **The route that carries it:** `sdk_guide(topic='load', language=…, record_count=<above the
  default limit>)`. Its `compatibility_notes` say a licensed user should "place the license file at
  the path specified by `SENZING_LICENSE_FILE` or in the `etc/` directory". Confirmed at
  `language='python', record_count=1000` and `language='java', record_count=600` — the note is
  language-independent and appears **only** when the count exceeds the limit.
- ❌ `sdk_guide(topic='configure', language='python', platform='linux_apt')` — `environment.env_vars`
  holds exactly two entries, `LD_LIBRARY_PATH` and `PYTHONPATH`. No license variable.
- ❌ `sdk_guide(topic='install', platform='macos_arm')` — license appears only as the `PIPELINE` keys
  `LICENSEFILE` / `LICENSESTRINGBASE64`.
- ❌ `search_docs(query='license file environment variable SENZING_LICENSE_FILE path')` — EULA and
  pricing prose, no variable name.

A `PIPELINE` key (`LICENSEFILE` for a `.lic` path, `LICENSESTRINGBASE64` for an inline key) is the
other supported route, and is what `module-04-data-collection/SKILL.md:616` already wires.

## The error in the first version

The first pass called `configure`, `install`, and `search_docs`, found no license variable in any of
them, and concluded that none exists. It then:

1. Rewrote `module-02-sdk-setup/SKILL.md` Step 5 to assert "There is no license-path environment
   variable" — **replacing a true statement with a false one.** The note it overwrote had said that
   `sdk_guide` returns `SENZING_LICENSE_FILE`. That was correct.
2. Registered INV-208 as a ban on the entire `SENZING_LICENSE_` prefix, so the guard **forbade the
   correct name**.
3. Recorded all of it as verified, with dated MCP evidence — evidence that was real but from the
   wrong tools.

This is textbook **INV-194**: *an empty or absent field in one MCP tool's response is NOT evidence
the server lacks the fact; ask the tool that owns it before recording a negative, and scope every
negative to the tool and parameters actually asked.* The invariant existed, was indexed, and was not
applied. Three tools' silence felt like proof because it was three rather than one.

It surfaced only because a phase-3 walk called `sdk_guide(topic='load', …, record_count=1000)` for an
unrelated reason — the evaluation-license record limit — and the license variable was sitting in the
same `compatibility_notes` block. Nothing in the offline suite could have caught it: the suite is
offline by INV-108, and the wrong claim had been written into the guard, so the guard agreed with it.

Two structural lessons worth keeping:

- **A prefix ban is only sound when every member is genuinely wrong**, and establishing that requires
  the same ask-the-owning-tool discipline as any other negative. Banning a family is *more*
  dangerous than banning a spelling, not safer.
- **A negative recorded with dated evidence from the wrong route is indistinguishable from a
  verified one.** The `MCP-NEGATIVE` marker convention makes such claims re-checkable, which is what
  eventually saves them — but only if the marker names the route, and the original marker named the
  routes that omit the fact rather than the one that owns it.

## Proposed change

1. **`graduation/SKILL.md`** — `.env.example` lists `SENZING_LICENSE_FILE` (not
   `SENZING_LICENSE_PATH`), names the `sdk_guide(topic='load', …, record_count>limit)` route to
   confirm the spelling, and shows the `PIPELINE` alternative as a comment so both routes are
   visible.
2. **`module-02-sdk-setup/SKILL.md`** — Step 5 states the correct variable, names the single route
   that returns it *including the `record_count` condition*, marks `SENZING_LICENSE_PATH` as a
   confabulation, and carries a ⚠️ warning not to conclude absence from the topics that omit it,
   citing what that inference already cost.
3. **INV-208** — rescoped in place to ban the one wrong spelling and require the correct one, with a
   dated correction note. Per this repo's own rule, an invariant encoding a false premise is worse
   than a missing one.
4. **The guard** — bans `SENZING_LICENSE_PATH` as an exact spelling; permits the two files whose
   subject *is* that it is wrong to quote it, and asserts each marks it wrong nearby; requires the
   correct spelling and its route to be present; and pins the INV-194 warning in the file that got it
   wrong.

## Acceptance criteria

- [x] No file under `plugins/` uses `SENZING_LICENSE_PATH`, except the two notes that name it in
      order to mark it wrong — each of which states nearby that it must not be used.
- [x] `graduation`'s `.env.example` names `SENZING_LICENSE_FILE` and asserts no absence claim.
- [x] `module-02` Step 5 names `SENZING_LICENSE_FILE`, the `record_count` condition on the route that
      returns it, and the `PIPELINE` alternative.
- [x] `module-02` keeps a warning that the omitting topics are not evidence of absence (INV-194).
- [x] Module-02 Step 5a still routes the evaluation-license **record limit** to
      `sdk_guide(topic='load', …, record_count=…)` and hardcodes no figure (INV-080).
- [x] A repo-level stdlib-only test in `tests/` enforces the above and fails when
      `SENZING_LICENSE_PATH` is reintroduced as a variable, and when either absence claim returns.
- [x] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the `.env.example` bullet.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 5's license note.
- `tests/test_license_env_var_absent.py` — the guard (5 tests).
- `specs/INVARIANTS.md` — INV-208, corrected in place.

## Source

- Feedback: none — dry run phase 1 found the defect; dry run **phase 3** found the error in the fix
  (both 2026-08-13). `Source: self-observed (assistant retrospective)`
- Priority: High — a fabricated environment variable shipped in a production deliverable, and the
  first correction made module-02 actively wrong for the duration of one commit.
- MCP re-check: server 1.32.9, 2026-08-13. `sdk_guide(topic='load', language='python',
  record_count=1000)` and `(language='java', record_count=600)` both return `SENZING_LICENSE_FILE`;
  `sdk_guide(topic='configure', …)`, `sdk_guide(topic='install', platform='macos_arm')` and
  `search_docs` all omit it. The plugin was wrong about the spelling, and the first fix was wrong
  about the existence.
- Upstream: not applicable — the plugin was wrong on both passes, not the server. Worth noting for
  the maintainer that the server surfaces this name in only one topic's
  `compatibility_notes`, which is a discoverability wrinkle rather than a defect.
- Related specs: none
