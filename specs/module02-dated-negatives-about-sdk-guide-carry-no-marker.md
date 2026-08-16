# Module 2's dated "`sdk_guide` documents neither of these" claims carry no `MCP-NEGATIVE` marker

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Module 2 splits its version-check and update commands into **server-documented** and
**plugin-owned**, and each `plugin-owned` label is a dated absence claim about an MCP tool's
content. Four of them, none carrying an `MCP-NEGATIVE` marker:

| `file:line` | The claim |
|---|---|
| `module-02-sdk-setup/SKILL.md:155-159` | "The server documents `brew install --cask` and `scoop install`, **never** `brew upgrade --cask` or `scoop update` (checked across `install_commands`, `gotchas` and `post_install` for both, 2026-07-31)" |
| `module-02-sdk-setup/SKILL.md:164` | "`# plugin-owned — sdk_guide documents neither of these`" (over `dpkg-query -W` and `apt-cache policy`) |
| `module-02-sdk-setup/SKILL.md:185-186` | "`sdk_guide` documents brew tap / trust / install --cask only, **never** outdated, info or upgrade (checked across its whole response, 2026-07-31)" |
| `module-02-sdk-setup/SKILL.md:209-210` | "`sdk_guide` documents scoop bucket add / scoop install only, **never** status, info or update (checked across its whole response, 2026-07-31)" |

`coverage_reports.py negatives` reports **three** markers in `plugins/`, and none of them is any of
these — the only marker in this file is at `:982`, for an unrelated `macos_arm` claim. So four dated
negatives shape what shipped guidance tells a Bootcamper to run, on a surface the offline suite
cannot re-check, and they are on no worklist. This is the claim shape the convention exists for, in
the module a Bootcamper actually executes.

**The claims themselves are true where re-asked.** Server **1.32.9**, docs indexed
**2026-08-11 20:52 UTC**, 2026-08-13:

- `sdk_guide(topic='install', platform='windows')` — `install_commands` are `Set-ExecutionPolicy`,
  `Invoke-RestMethod`, `scoop bucket add senzingsdk …`, the EULA prompt, `scoop install
  senzingsdk/senzingsdk` and the non-interactive EULA form; `post_install` is `echo $env:SENZING_DIR`
  and `Test-Path "$env:SENZING_DIR\lib\Sz.dll"`; `gotchas` cover SUPPORTPATH/SENZ7426, the
  Python-Linux-only rule, Java, C#, verification and network. **No `scoop status`, `scoop info` or
  `scoop update` anywhere in the response.** Confirms `:209-210`.
- `sdk_guide(topic='install', platform='linux_apt')` — no `dpkg-query`, no `apt-cache policy`
  anywhere in the response. Confirms `:164`.

⚠️ **The `brew` half was NOT re-asked.** `sdk_guide(topic='install', platform='macos_arm')` was not
called in this sweep, so `:155-159` and `:185-186` still rest on their 2026-07-31 observation. The
implementer must ask it (see the acceptance criteria) — and if the server has since gained
`brew upgrade --cash`/`outdated`/`info` coverage, the fix is to correct those two claims, not to
mark them.

## Root cause

Sequencing, not carelessness. These claims are dated **2026-07-31**; the `MCP-NEGATIVE` convention
and its `owner:` requirement were established later (INV-209, and INV-217 on 2026-08-13). Nothing
retro-fitted the negatives that predate the convention, and nothing sweeps for them:

- `coverage_reports.py negatives` finds markers. A negative with **no** marker is invisible to it by
  construction — the report can only ever list what is already tagged.
- `tests/test_dated_negatives_are_marked.py` polices **test assertions** —
  `unmarked_negative_assertions()` scans `tests/*.py` for lines matching `self.assert\w+\(`. Plugin
  prose is outside its corpus entirely.
- INV-217 closed the same hole for `specs/DECLINED.md` on 2026-08-13 and deliberately scoped itself
  to that one file.

So shipped plugin prose is the remaining unswept surface for unmarked negatives, and this spec fixes
the four instances rather than the class. **The class gap is real and is left as a maintainer
decision** — a guard over plugin prose has genuine false-positive risk, because the plugin
legitimately *discusses* absences (INV-192's "the payload of a gate is empty by design" is a
sentence about emptiness that must not require a marker).

## Proposed change

Add one `MCP-NEGATIVE` marker per claim, in the HTML-comment form this file already uses at `:982`
so nothing bootcamper-facing changes. Each marker's `owner:` clause names the route that would
**carry** an install-or-update command for that platform — which is `sdk_guide(topic='install',
platform=<p>)` itself, asked across `install_commands`, `gotchas` and `post_install`. These are
**absence** negatives: the asked route is the owner, and saying so is what separates them from a
wrong-route conclusion.

```text
MCP-NEGATIVE: sdk_guide(topic='install', platform='windows') — install_commands, gotchas and post_install carry no scoop status, scoop info or scoop update — owner: sdk_guide(topic='install', platform='windows') IS the route that would carry an update or version-query command for Scoop, and it documents installing only (absence negative) — server 1.32.9, 2026-08-13
```

**What stays:** every command, every `plugin-owned` / `server-documented` label, the ⚠️ at
`:148-153` about the plugin-owned commands being Linux-exercised only, and the dated-illustration
framing on the server-documented forms. This adds markers; it removes nothing and rewords nothing.

**Re-stamp only what is re-asked.** A marker's version and date must be the call that established
it. Do not stamp the `brew` claims 1.32.9/2026-08-13 unless `platform='macos_arm'` is actually
called — copying the stamp from the Windows call is precisely the laundering INV-080 forbids.

## Acceptance criteria

- [ ] Each of the four claims at `:155-159`, `:164`, `:185-186`, `:209-210` carries a parseable
      `MCP-NEGATIVE` marker with an `owner:` clause naming `sdk_guide(topic='install', platform=<p>)`
      as the owning route.
- [ ] `python3 .claude/skills/dry-run/coverage_reports.py negatives` reports **7** markers (3
      existing plugin + 2 in `DECLINED.md` + … recount at implementation time; the point is that the
      four new ones appear and nothing is reported malformed).
- [ ] **`sdk_guide(topic='install', platform='macos_arm')` is called at implementation time**, and
      the `brew` claims are either confirmed and marked with that call's stamp, or corrected because
      the server now documents `brew outdated`/`info`/`upgrade`. Do not mark an unasked claim.
- [ ] The Windows and apt claims are re-confirmed at implementation time rather than taken from this
      spec (INV-080): `platform='windows'` still carries no `scoop status|info|update`, and
      `platform='linux_apt'` no `dpkg-query|apt-cache policy`.
- [ ] No command, label, or warning in the affected region is removed or reworded — `git diff` shows
      only added marker lines.
- [ ] Markers use the HTML-comment form already used at `:982`, so no bootcamper-facing text changes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — four markers added at `:155-159`,
  `:164`, `:185-186`, `:209-210`.

## Source

- Skill: `delegate-to-mcp-server` sweep, 2026-08-13. Server **1.32.9**, docs indexed
  **2026-08-11 20:52 UTC** (both axes unchanged since 2026-08-12).
- Found while re-checking `module02-step1b-command-provenance-split` — that row's `delegate` verdict
  **is** implemented (the provenance split is explicit, per-line), and the markers are what the
  implementation did not have a convention for yet.
- Ledger key: `module02-update-commands-negatives-carry-no-marker`.
- Priority: Medium. Nothing is wrong today — the commands work and the labels are honest. It is a
  visibility defect on four claims that cannot go stale detectably, which is the exact failure the
  convention was built for after it happened twice.
- Upstream: the underlying coverage gap (the server documents installing, not updating) is recorded
  as `module02-update-check-commands-unsupplied`. ⚠️ `SKILL.md:159` states it was "reported upstream
  on 2026-07-31" while that ledger row reads `not reported upstream` — **one of the two is wrong, and
  this must be settled before any new upstream report is filed**, or the same gap is filed twice.
- Related: INV-209 (marker form and `owner:` requirement), INV-217 (the same hole closed for
  `DECLINED.md`), `specs/mcp-negative-markers-must-name-the-owning-route.md`.

## Deviations from this spec, and why (2026-08-13)

The markers landed as specified. Three things differ, and the first is a criterion this spec set
and the server then overruled.

1. **Criterion 5 is NOT met: two fence comments were reworded.** The criterion said "no command,
   label, or warning in the affected region is removed or reworded — `git diff` shows only added
   marker lines". Calling `sdk_guide(topic='install', platform='macos_arm')` at implementation time
   — the call this spec insisted on — showed the claims' word **"only"** is wrong at 1.32.9:
   - `:185` said `sdk_guide` "documents brew tap / trust / install --cask **only**". The response
     also documents `brew uninstall --cask`, `brew untap`, `brew install libpq`, `brew link libpq`
     and `brew --prefix`.
   - `:209` said "scoop bucket add / scoop install **only**". The response also documents
     `scoop config SENZING_ACCEPT_EULA …` in its non-interactive EULA note.

   The part that matters — no `brew outdated|info|upgrade`, no `scoop status|info|update` anywhere
   in either response — is **confirmed**. So both comments were narrowed to the version-management
   scope they were actually making ("documents no brew version-management command"), and re-dated
   to the call that established it. Marking an imprecise claim would have been worse than leaving it
   unmarked: the marker certifies the claim as reviewed.
2. **`tests/test_sdk_update_offer.py` changed, and it is not in this spec's Affected files.** Its
   `test_the_labels_are_inside_the_command_blocks_not_only_the_preamble` pinned both fence comments
   **in full**, so correcting the prose failed the suite with a message asserting the opposite of
   what the server returns — the exact failure mode `tests/test_dated_negatives_are_marked.py` was
   written to prevent, arriving from the direction that file does not police (plugin prose, not test
   assertions). The guard was **rescoped, not deleted**: it now pins the ownership label
   (`# ALL plugin-owned — sdk_guide documents no brew`), which is what a skimming reader needs and
   what stays true when the server moves, with the history recorded in its docstring.
   Negative-controlled: removing the brew label from the fence fails it.
3. **The marker count is 9, not the "7" this spec guessed.** The criterion said to recount at
   implementation time, which is what 9 is: 3 pre-existing `plugins/` markers + 2 in
   `specs/DECLINED.md` + the 4 added here. Nothing reported malformed. Second negative control:
   stripping one `owner:` clause drops the worklist to 8, prints `MALFORMED markers: 1`, and fails
   `tests/test_dated_negatives_are_marked.py`.

⚠️ **Also left alone deliberately.** `test_sdk_update_offer.py:179` still pins
`"never \`brew upgrade --cask\` or \`scoop update\`"` — the same pin-the-claim pattern, on a claim
that **is** currently true and was re-confirmed today on both platforms. Rescoping every such guard
is outside this spec; it is named here so the next reader finds it rather than rediscovering it.
