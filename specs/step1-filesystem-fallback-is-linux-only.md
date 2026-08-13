# Module 2 Step 1's filesystem fallback can only detect a Linux install

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Step 1 is the module's first action and is marked **MUST DO FIRST**. When the language import
check fails, it falls back to sentinel files — and both are Linux paths:

> **Filesystem fallback (if the import check fails):** When the language import check does not
> succeed (e.g., `PYTHONPATH` is not configured or the package manager query finds nothing),
> check for these sentinel files before concluding the SDK is not installed:
>
> - `/opt/senzing/er/lib/libSz.so` (native shared library)
> - `/opt/senzing/er/szBuildVersion.json` (build version metadata)
>
> Both sentinel files must be present to conclude the SDK is installed via filesystem detection.
> … If only one file or neither is found, proceed with the "SDK not found" path (Step 2).
> (`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:73-83`)

**On macOS and Windows neither path can ever exist**, so the fallback always concludes "not
installed". A Bootcamper with a working install whose import check fails is told *"Senzing SDK is
not installed yet. Let's set it up, this is a one-time process."* (`:113`) and routed into Step 2
for a **reinstall of software they already have** — the exact outcome Step 1 opens by forbidding:
*"There is no reason to re-install it."*

The trigger is not hypothetical, and it is **more** likely off Linux. The fallback exists for when
the import check fails, and the two non-Linux platforms are where this file documents that failure
mode most: `:610` warns that on macOS `DYLD_LIBRARY_PATH` must be set **before the JVM starts** and
`-Djava.library.path` "alone is insufficient", and today's `sdk_guide(topic='install',
platform='windows')` requires a `CLASSPATH` export for Java. A Java bootcamper on either platform
who has not exported those hits a failed import check with a perfectly good install.

**The correct paths are known — this file already states them, three times:**

| Platform | Artifact this file already names | Where |
|---|---|---|
| macOS | `$(brew --prefix)/opt/senzing/er/lib/libSz.dylib` | `:203`, `:1043` |
| Windows | `%SENZING_DIR%\lib\Sz.dll` | `:222` |
| Windows | `szBuildVersion.json` is in the **sibling** `data` directory, *not* under `%SENZING_DIR%` | `:231`, `:243` |

So this is a **consistency** defect inside a single file: `:73-83` contradicts `:203`, `:222` and
`:243`, and `:243` explicitly corrects the very path `:78` hardcodes. It is also a **completeness**
defect against **INV-001** (Linux, macOS and Windows are all supported) — an invariant this file
cites **zero** times.

Both paths were re-confirmed against the live server this session — **server 1.32.9, docs indexed
2026-08-11 20:52 UTC, 2026-08-13**: `sdk_guide(topic='install', platform='macos_arm')` gives
`SENZING_ROOT=$(brew --prefix)/opt/senzing/er` and verifies with
`ls "${SENZING_ROOT}/lib/libSz.dylib"`; `sdk_guide(topic='install', platform='windows')` verifies
with `Test-Path "$env:SENZING_DIR\lib\Sz.dll"` and warns that `SENZING_DIR` points at the `er`
subdirectory.

## Root cause

The step was written for the Linux reference environment and the fallback list was never revisited
when macOS and Windows support landed. Nothing caught it in either direction:

- **No test pins Step 1's sentinel list.** `grep -rn "szBuildVersion\|libSz.so" tests/` reaches
  `tests/test_sdk_update_offer.py` and `tests/test_viz_settings_resolution.py`, neither of which
  asserts anything about this step.
- **The repo already asserts the contradicting fact.**
  `tests/test_sdk_update_offer.py:260` is titled *"On Windows szBuildVersion.json is a sibling of
  er, not under SENZING_DIR"* — so one side of the contradiction is test-attested and the other is
  unguarded, which is why the two could drift apart and stay that way.
- **INV-001 is enforced by nothing mechanical here.** It is a whole-plugin property, so a
  Linux-only enumeration inside one step reads as complete.

## Proposed change

1. **Make the fallback platform-dispatched** in `:73-83`, using the artifacts this file already
   names and today's `sdk_guide` responses confirm:
   - `linux_apt` / `linux_yum`: `/opt/senzing/er/lib/libSz.so` + `/opt/senzing/er/szBuildVersion.json`
   - `macos_arm`: `$(brew --prefix)/opt/senzing/er/lib/libSz.dylib` + the `szBuildVersion.json`
     under the same `er` directory
   - `windows`: `%SENZING_DIR%\lib\Sz.dll` + `szBuildVersion.json` in the **sibling** `data`
     directory, per this file's own `:243`
   - `docker`: state that there is no host filesystem to probe and the check does not apply — the
     image tag is the version (this file's `:225` already says so for updates).
2. **Keep the primary route first.** The step already says to get the verification command from
   `sdk_guide(topic='install', platform=…, language=…)` (`:69-71`); that stays the first move, and
   the sentinel list stays explicitly the *fallback*.
3. **Do not let the fallback assert a negative it cannot support.** On a platform whose sentinels
   were not checked, the outcome is *unknown*, not "not installed" — say the check could not be
   completed and name why, per **INV-163**, rather than routing to a reinstall.
4. **Cite INV-001** at the step, so the next editor of a platform-dispatched list knows what binds
   it (INV-183's principle: name the governing rule where it governs).

## Acceptance criteria

- [ ] Step 1's filesystem fallback names a sentinel pair for `linux_apt`/`linux_yum`, `macos_arm`
      and `windows`, and states that `docker` has no host artifact to probe.
- [ ] The Windows entry places `szBuildVersion.json` in the **sibling** `data` directory, agreeing
      with `:243` and with `tests/test_sdk_update_offer.py:260`.
- [ ] The macOS entry uses `$(brew --prefix)`, not a hardcoded `/opt/homebrew` — the
      `sdk_guide(topic='install', platform='macos_arm')` anti-patterns list names the hardcoded form
      as an error.
- [ ] A platform whose sentinels were not checked yields "could not determine", never "not
      installed" (INV-163), and never routes to Step 2's reinstall path.
- [ ] The step still tries `sdk_guide` first; the sentinel list remains the fallback.
- [ ] A new test asserts the fallback names an artifact for each of the three INV-001 platforms and
      that the Windows path is the sibling `data` directory — **negative-controlled** by deleting one
      platform's entry and confirming failure, then reverting.
- [ ] **Re-verification clause:** implementing this requires `sdk_guide(topic='install',
      platform='macos_arm')` to still verify with `libSz.dylib` under `${SENZING_ROOT}/lib`, and
      `platform='windows'` with `Sz.dll` under `$env:SENZING_DIR\lib`. If either artifact name has
      moved, use what the server says and record the deviation.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — the fallback at `:73-83`.
- `tests/` — a new guard for the platform coverage of that list.

## Source

- Skill: `production-readiness-audit`, 2026-08-13. Found by the **completeness** sweep (INV-001
  coverage) after the `conformance.py rules` hit at `:197` led into the step's platform handling.
- Priority: **High.** It breaks a documented path on two of three supported platforms, its outcome
  is a wasted reinstall of working software, and Step 1 is the module's first action.
- MCP re-check: server **1.32.9**, 2026-08-13 — both replacement artifact paths confirmed live via
  `sdk_guide(topic='install', platform='macos_arm')` and `platform='windows'`. No Senzing fact is
  taken from this spec or from the ledger.
- Related: INV-001 (three platforms), INV-163 (say what you could not verify), INV-183 (name the
  governing rule at the step).

## Deviations from this spec, and why (2026-08-13)

One deviation, and the server is why.

**The macOS `szBuildVersion.json` sentinel was not written, and the "sentinel pair" became a single
artifact.** Proposed change 1 asked for a *pair* per platform — native library plus
`szBuildVersion.json` — with the macOS entry taking "the `szBuildVersion.json` under the same `er`
directory". That location had no source. Asked at implementation time,
`search_docs(query='szBuildVersion.json build version file location')` on server **1.32.9**, docs
indexed **2026-08-11 20:52 UTC**, returns **no document giving that file's path on any platform**:
all four hits are `SzProduct.get_version()` / `engine_version` SDK examples, top hit
`brianmacy/sz-rust-sdk -> code-snippets/information/get_version.rs` at relevance 39.5. Writing a
macOS path would have invented a Senzing fact (INV-080), and inferring it from the Windows
sibling-`data` placement would have been the same error one step removed.

So the fallback probes **the native library only** — the artifact that must exist for the SDK to
work, and the one `sdk_guide` names for every platform. Reading the *version* is now routed to the
primary mechanism (the language check, or `SzProduct.get_version()`, which the corpus does document),
with the `szBuildVersion.json` locations kept as explicitly-labelled **environment observations**:
Linux observed directly on this machine on 2026-08-13 (present in **both** `/opt/senzing/er/` and
`/opt/senzing/data/`), Windows per this file's existing `:243`, macOS unknown and said to be unknown.
The absence carries an `MCP-NEGATIVE` marker with its owning route, so it reaches the re-check
worklist.

This is a better fix than the one specced, not merely a smaller one: requiring **both** files was
what made the original test fail closed, and the version file was never what decides whether the SDK
is installed.

⚠️ **Also changed, and not in this spec's Affected files:** `tests/test_prescribed_search_queries.py`.
Its guard requires every `search_docs(query=…)` literal in shipped markdown to be verified or paired
with a re-query rule, and it cannot distinguish the marker's *evidence* query from one a step tells
the guide to *run*. That default is correct — an unexecuted phrasing is indistinguishable from an
executed one — so the query was added to `VERIFIED_QUERIES` with its observed top hit and relevance,
in that allowlist's own idiom, rather than the guard being narrowed to exclude markers.
