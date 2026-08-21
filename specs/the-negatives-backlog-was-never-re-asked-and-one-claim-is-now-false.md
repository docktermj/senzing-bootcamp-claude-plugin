# 21 of 23 `MCP-NEGATIVE` markers are dated against a superseded server, none has been re-asked, and sampling four found one already false

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`coverage_reports.py negatives` exists to produce a worklist a run re-asks, oldest first, because a
negative — "tool X does not contain Y" — is the one claim shape that cannot go stale detectably.
The suite is offline (INV-108), so nothing notices when the server gains the coverage the plugin
routed around.

**Measured 2026-08-21: 23 markers, of which 21 are dated `server 1.32.9` (2026-08-13 to -17). The
live server is 1.33.0. Not one of the 21 has been re-asked.** The two at 1.33.0 were written today.

Four were sampled against the live server. **One is now false:**

| Marker | Claim | Against 1.33.0 |
|---|---|---|
| `module-05-data-quality-mapping/SKILL.md:82` | `search_docs(query='globalization')` "returns no UTF-8 / supported-languages answer in its top hits" | ⛔ **FALSE.** `search_docs(query='UTF-8 supported languages non-Latin scripts', category='globalization')` returns *"Senzing Globalization Guide" → "What languages does Senzing support?"*: "Senzing utilizes UTF-8 encoding which allows for most languages of the world to be properly captured and processed…" |
| `module-02-sdk-setup/SKILL.md:205` | install response carries no `brew upgrade --cask` | still true |
| `module-02-sdk-setup/SKILL.md:232` | no `brew outdated`, `brew info` or `brew upgrade` anywhere in the response | still true |
| `module-02-sdk-setup/SKILL.md:891` | `generate_scaffold`'s schema carries only `language`, `version`, `workflow` | still true |

The failing one is also a **route** problem, not only a staleness problem: `search_docs` now
advertises a `globalization` **category**, and the answer is reachable through it. The marker's
`owner:` clause named `search_docs` itself, so the negative was recorded as an *absence* negative
when the fact was — or has since become — served under a filter the marker never used.

⚠️ **The response metadata dates the change.** The same call reports
`index_built: 2026-08-20 17:33 UTC` against 14,348 documents. The marker was written 2026-08-13, so
the corpus was rebuilt **after** it — which is exactly the event no offline check can see.

## Root cause

**Nothing schedules the re-ask.** The marker format, the `owner:` requirement, the oldest-first
report and the guard that fails on an unmarked absence claim all exist — the whole apparatus is
built — and the one step that closes the loop is a human remembering to run `negatives` and act on
it. Three audit iterations ran on 2026-08-21 and all three read `negatives` as **clean**, because
the report answers "does every dated negative carry a well-formed marker?" and not "has any of them
expired?"

So the report's own success criterion is the gap: a marker that is well-formed and eight days stale
is indistinguishable, in that output, from one re-asked this morning.

⛔ **This is not an argument for deleting negatives.** Three of the four sampled are still true and
are load-bearing — the brew ones stop a run inventing an upgrade command the server does not
document. The problem is that nothing distinguishes the three from the one.

## Proposed change

1. **Make the report answer the staleness question it is read for.** Have `negatives` compare each
   marker's recorded server version against the current one — passed in as an argument, since the
   scan is offline and must not pretend to know — and mark every marker whose version differs as
   **DUE**. A run then sees "21 due, 2 current" instead of a list it must date by eye.
2. **Fix the false claim at `module-05-data-quality-mapping/SKILL.md:82`.** The guidance routes a
   Bootcamper around content the server serves. ⛔ Prefer restating it as what **is** true —
   `search_docs(category='globalization')` answers the UTF-8 and supported-languages question — over
   re-dating the negative, because the positive form does not expire (Step 3.4's own preference).
   Check `:83` in the same file, which is the adjacent marker.
3. **Re-ask the remaining 20 and record the outcome for each**, rather than re-dating them in bulk.
   ⛔ A bulk re-date is the failure mode this spec describes: it makes every marker look reviewed at
   the cost of reviewing none. Each needs its owning route called and its result recorded.
4. **Decide whether a marker older than one server minor version should fail the suite.** It cannot
   be checked offline against the live server, but it *can* be checked against a committed
   "last-known server version" the audit updates — which converts silent expiry into a loud one.
   ⚠️ That introduces a file that itself goes stale; weigh it against the alternative of a report
   nobody runs. This is a maintainer decision, not a foregone one.

## Acceptance criteria

- [ ] `coverage_reports.py negatives` reports each marker's version against a supplied current
      version and labels the differing ones DUE, with a total.
- [ ] The `module-05-data-quality-mapping/SKILL.md:82` claim is corrected — preferably restated in
      positive form naming `category='globalization'` — with the server version and date.
- [ ] `:83`, the adjacent marker in the same file, is re-asked and its outcome recorded.
- [ ] Every remaining marker dated below the current server version is either re-asked with its
      outcome recorded, or listed as still-due in the ledger entry so the next run inherits a
      worklist rather than a clean bill.
- [ ] No marker is re-dated without its owning route having been called this session.
- [ ] A test covers the DUE labeling — negative-controlled by supplying a version that should mark
      every marker current, and one that should mark all of them due.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      `coverage_reports.py` is stdlib-only maintainer tooling under `.claude/`.

## Affected files

- `.claude/skills/dry-run/coverage_reports.py` — the DUE comparison.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/SKILL.md` — lines 82 and 83.
- `plugins/senzing-bootcamp/skills/**` — the remaining markers, as each is re-asked.
- `tests/` — coverage for the DUE labeling.

## Source

- Audit: `production-readiness-audit`, 2026-08-21 (fourth run of the day, first with the maintainer
  present). Found by reading the `negatives` report's version column instead of its "well-formed"
  verdict.
- Priority: **High.** One shipped claim is false today and it routes a Bootcamper away from content
  the server serves — the INV-194 class, which this repository has now hit four times. The backlog
  makes the next occurrence equally invisible.
- MCP re-check: server **1.33.0**, 2026-08-21 — **changed** for one of four sampled markers.
  `search_docs(query='UTF-8 supported languages non-Latin scripts', category='globalization')`
  returns the Globalization Guide's "What languages does Senzing support?" section;
  `sdk_guide(topic='install', platform='macos_arm', language='java')` still carries no
  `brew upgrade`/`outdated`/`info`; `generate_scaffold`'s loaded schema still declares only
  `language`, `version`, `workflow`. owner-checked: not applicable — this spec's own claim is that a
  recorded absence is now **served**, which is a positive finding; the absence claims it re-examines
  each carry their own `owner:` clause.
- Upstream: not applicable — nothing here is a server defect.
- Related specs: `specs/mcp-negative-markers-must-name-the-owning-route.md`,
  `specs/guards-pinning-a-dated-negative-outlive-it.md`,
  `specs/the-eval-license-duration-tools-now-agree-so-retire-the-note-and-its-guard.md`

## Deviations from this spec, and why (2026-08-21)

⛔ **This spec's headline claim is WRONG, including its filename. No marker was false.** All 21
were re-asked against server 1.33.0 on 2026-08-21 and **all 21 hold**.

### How the wrong claim was reached

The marker at `module-05-data-quality-mapping/SKILL.md:82` records that
**`search_docs(query='globalization')`** — a bare query, no category — returns no
UTF-8/supported-languages answer in its top hits, and that its highest-ranked Guide hit is a
title-only stub. The audit "disproved" it by calling
`search_docs(query='UTF-8 supported languages non-Latin scripts', category='globalization')` — **a
different query with a category filter** — and treating that answer as evidence about the bare
query.

Re-asking the actual route returns: hit 1 *"Senzing Globalization Guide"* whose entire excerpt is
`# Senzing Globalization Guide` — the title-only stub the marker names — then Guide sections on
*name* and *address* comparisons. No "What languages does Senzing support?" in the top hits. The
marker is correct, verbatim, down to the stub detail.

⚠️ **This is INV-194's wrong-route error, committed by the audit that exists to catch it**, and it
is the fourth occurrence of the class in this repository. The prose immediately above the marker
*already* says *"With `category='globalization'` the on-topic rows come back first"* — so the plugin
had the routing right all along, and the audit's "finding" was re-deriving the plugin's own
correction and mistaking it for a contradiction.

⛔ **Consequently `module-05:82` was NOT changed.** There is nothing wrong with it. Change 2 of
this spec is void.

### What survives, and it is most of the spec

- **The staleness-visibility gap is real.** 21 of 23 markers were dated `server 1.32.9` against a
  live 1.33.0 and none had been re-asked, while three audit runs the same day read the report as
  clean — because it answers "is every marker well-formed?" and not "has any expired". Change 1 is
  implemented: `negatives` now takes `--server <version>` and splits DUE from current.
- **Change 3 is done properly: all 21 re-asked individually**, each against its own recorded route,
  each outcome recorded. That is the work the spec forbade shortcutting, and it is what produced
  the correction above.
- **Change 4 is decided report-only** by the maintainer: no suite failure on a stale marker.

### Bonus findings from the sweep, recorded rather than acted on

1. **`szBuildVersion.json`'s Windows location is now MCP-documented.**
   `sdk_guide(topic='install', platform='windows', language='java')` states the support data —
   naming `szBuildVersion.json` — installs to `<scoop-app-dir>\data`, a **sibling** of `er`. The
   plugin currently marks that location an *"environment observation, not an MCP-sourced fact"*
   (`module-02-sdk-setup/SKILL.md:107` context). It can be upgraded to MCP-sourced for Windows;
   macOS remains unknown.
2. **The server contradicts itself on repository count** — `find_examples` says "37 indexed Senzing
   GitHub repositories", `get_capabilities` says "42 GitHub repositories". The plugin cites neither,
   so nothing is wrong here; noted because a future citation would have to pick one.
3. **`generate_scaffold`'s undeclared `inline` is now acknowledged upstream.** Its `access_steps`
   step 3 says the call works only if "your client forwards arguments that are not in a tool's
   declared schema" and that "clients that validate arguments against the declared schema cannot
   use this step" — so the mismatch `module-02:891` records is documented rather than hidden.
4. **`mapping_workflow` step 1 contradicts its own schema.** Its prose `ADVANCE FORMAT` shows
   `profile_summary` as an object keyed by schema name; the JSON Schema beneath it declares an
   **array** of `{schema_name, record_count, field_count}`. INV-136 tells the guide to satisfy
   required parameters "as the live schema states them", so the schema governs — but a reader
   following the prose would send the wrong shape.
5. **INV-177's basis re-confirmed.** Step 1 still writes exactly `profile_report.md`,
   `schema_hints.md` and `JOURNAL.md` into `workspace_dir`, and still calls `JOURNAL.md`
   APPEND-ONLY.
