# Six dated tool-absence claims in shipped prose need their owning route re-asked, then marking

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`coverage_reports.py unmarked` — added 2026-08-13 by
`plugin-prose-negatives-are-unswept-by-any-guard` — reports **6** dated tool-absence claims in
shipped plugin prose carrying no `MCP-NEGATIVE` marker. Oldest stamp first, as the report prints
them:

| Stamp | Site | The claim |
|---|---|---|
| 2026-07-26 | `module-02-sdk-setup/SKILL.md:802` | "`search_docs` does **not** answer this — asked for the evaluation license's record limit it returns EULA and pricing prose with no figure" |
| 2026-07-31 | `module-02-sdk-setup/SKILL.md:316` | "Senzing documents no 4.x → 4.y update procedure. `search_docs` returns only V3→V4 migration material … and `sdk_guide` has no `upgrade` topic" |
| 2026-08-13 | `module-02-sdk-setup/SKILL.md:748` | "The license environment variable is `SENZING_LICENSE_FILE`, and **only ONE tool route returns it** — do not go looking for it anywhere else" |
| server 1.32.2 | `module-02-sdk-setup/SKILL.md:728` | "the tool's **declared schema has no `inline` parameter at all** — only `language`, `version` and `workflow`" (`generate_scaffold`) |
| server 1.32 | `module-02-sdk-setup/SKILL.md:1211` | "`SENZ7221 …`? The datastore has no default configuration" |
| server 1.32.2 | `module-03-system-verification/phase1-verification.md:206` | "`generate_scaffold` returns a **listing**, not code … with no source text" |

Two of them are **stale by two minor versions** (recorded at 1.32.2, current is 1.32.9) — the exact
condition under which `senz7221-now-names-its-own-remedy` and `explain-error-code-now-owns-senz7426`
each turned out to be wrong. Nothing in the offline suite (INV-108) can notice.

⚠️ **One is a likely false positive and must be triaged, not marked.**
`module-02-sdk-setup/SKILL.md:1211`'s "the datastore has no default configuration" is a statement
about the Bootcamper's *datastore*, not about a tool's content — the report's own header says a hit
needs judgement. Its correct outcome is a recorded verdict of *not a tool-content claim*, and if the
vocabulary can be tightened to exclude it without losing a true positive, that is the better fix.

## Root cause

The marker convention arrived after this prose. `MCP-NEGATIVE` and its `owner:` requirement were
established 2026-08-12/13 (INV-209, INV-217); these claims are dated 2026-07-26 to 2026-08-13. The
four in `module-02`'s Step 1b were retro-fitted the same day
(`module02-dated-negatives-about-sdk-guide-carry-no-marker`), but that sweep found them by *reading*
the region it happened to be in — so it fixed the instances in front of it and not the population.
The `unmarked` report exists because that is not a repeatable method.

## Proposed change

**Re-ask each claim's owning route, then act on what comes back — one claim at a time.**

⛔ **Never mark one of these by stamping today's date on it.** A marker asserts the claim was
verified at that version on that date; writing one without the call is the laundering INV-080
forbids, and it would make an unverified claim read as reviewed — worse than leaving it unmarked.

For each of the five genuine claims, in report order (oldest first):

1. **Ask the route that would carry the fact**, not only the route the prose names — INV-194. For
   `:748` the owner is already identified by INV-208 (`sdk_guide(topic='load', language=…,
   record_count=<above the limit>)`); for `:728` and `:206` the owning route for a *declared schema*
   is the tool's own schema as the server advertises it (`get_capabilities`' tool manifest), not the
   response prose; for `:316` and `:802` it is `search_docs`, which is the corpus route.
2. **Then one of three outcomes**, and each changes what ships:
   - **Confirmed** → add the marker with the `owner:` clause, stamped with the version and date of
     *that* call.
   - **Changed** → correct the prose to what the server says now, and mark the corrected claim.
     Where the plugin routes around a gap the server has since closed, remove the workaround.
   - **Unverifiable from here** → say so at the site with the reason (INV-163) and leave it
     unmarked rather than certifying it.
3. **Triage `:1211`** to a recorded verdict rather than a marker, and tighten
   `PROSE_ABSENCE`/the unit rule only if the tightening keeps all five true positives reported —
   verified by re-running the report, not by inspection.

**Sequence it so a partial run is useful.** Do them oldest-first, as the report orders them: the two
1.32.2 claims are the most likely to have moved. A run that gets through two has permanently
verified the two riskiest, and `unmarked` will show the remainder.

## Acceptance criteria

- [ ] Each of the five genuine claims has been re-asked against the live server this session, with
      the tool, parameters, version and date recorded in the ledger entry.
- [ ] Every claim that **confirmed** carries a parseable `MCP-NEGATIVE` marker whose `owner:` clause
      names the route that would carry the fact, stamped with that call's version and date.
- [ ] Every claim the server **contradicts** has its prose corrected rather than marked, and the
      correction is dated and legible as one.
- [ ] No marker's stamp is copied from another call — each corresponds to a call actually made
      (INV-080, INV-191).
- [ ] `module-02-sdk-setup/SKILL.md:1211` has a recorded verdict; if the vocabulary was tightened,
      re-running `unmarked` still reports the other genuine claims.
- [ ] `coverage_reports.py unmarked` reports **0** for the claims resolved, and any left unresolved
      are named in the ledger entry with why — never dropped silently.
- [ ] `coverage_reports.py negatives` count rises by the number of markers added, with none reported
      malformed.
- [ ] `tests/test_coverage_reports.py`'s `TestUnmarkedReport` still passes, including its
      non-vacuity test — if the report legitimately reaches zero, that test's expectation is
      updated in the same edit with the reason, not deleted.
- [ ] Full suite green and `citations.py verify` clean **after** the ledger entry is written.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — up to five sites.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — one site.
- `.claude/skills/dry-run/coverage_reports.py` — only if `PROSE_ABSENCE` is tightened for `:1211`.
- `tests/test_coverage_reports.py` — only if the non-vacuity expectation changes.

## Source

- Feedback: none — self-observed. The population was measured by the `unmarked` report on its first
  run, 2026-08-13 (`Source: self-observed (assistant retrospective)`).
- Priority: **Medium-High.** Two claims are two minor versions stale, and a stale negative is the one
  claim shape that cannot go stale detectably — it has shipped wrong twice. Nothing a Bootcamper does
  breaks today; what breaks is a reader trusting a routed-around gap the server has since closed.
- MCP re-check: **required at implementation; deliberately not done in this spec.** This spec asserts
  no Senzing fact of its own — every claim quoted above is the plugin's, with its own recorded stamp,
  and quoting it here is provenance rather than a current claim. `owner-checked:` is therefore not
  applicable to this spec; it is what the implementation must produce, per claim.
- Upstream: not applicable — the gaps these claims describe are separately tracked in
  `specs/mcp-coverage.jsonl` (e.g. `inv160-inline-param-undeclared`,
  `module02-no-4x-to-4y-upgrade-procedure`), which already record their upstream status.
- Related specs: `plugin-prose-negatives-are-unswept-by-any-guard` (added the report that found
  these), `module02-dated-negatives-about-sdk-guide-carry-no-marker` (the four found by reading),
  `declined-ledger-negatives-are-invisible-to-the-scanner` (INV-217), INV-209 (marker form),
  INV-194 (ask the owning route), INV-208 (the `:748` claim's registered owner), INV-163.

## Deviations from this spec, and why (2026-08-13)

**All five genuine claims CONFIRMED at server 1.32.9 — none had changed.** That was the outcome the
spec most wanted named either way, since two were 1.32.2 and the `senz7221` precedent says a stale
negative sometimes inverts. Three deviations, none affecting that result.

1. **Three of the five needed no new call, because the verification already happened this session.**
   The spec budgeted a re-ask per claim. In fact `:316` (`search_docs(query='upgrade Senzing SDK 4.3
   to 4.4 procedure')` → six hits, all V3-to-V4, plus `get_capabilities`' `sdk_guide` topic enum with
   no `upgrade` entry), `:728` (`generate_scaffold`'s declared schema, read directly — `language`,
   `version`, `workflow` only) and `phase1-verification.md:206` (`generate_scaffold(language='python',
   workflow='initialize')` → `snippets[]` with `file_path`/`source_url`/`repo`/`raw_url`/`size_bytes`/
   `line_count` and no `content`) were all established earlier in the same session at the same
   version. Only `:748` and `:802` required fresh calls. Each marker's stamp corresponds to a real
   call with those exact parameters — none was copied (INV-080, INV-191).

2. **`:802` turned out to be a ROUTING negative, not the absence the prose implies.** The spec listed
   it as "`search_docs` does not answer this". True — `search_docs(query='evaluation license record
   limit how many records without a license')` returns EULA grant-of-license and DSR-pricing prose
   ("solely for up to the number of DSRs designated therein") with no figure. But the figure **does**
   exist: `sdk_guide(topic='load', language='python', record_count=1000)` `compatibility_notes` say
   "exceeds the default Senzing license limit of **500**", and `explain_error_code('SENZ9000')` calls
   it the default 500-DSR free tier. The marker's `owner:` clause therefore routes the reader there
   rather than recording a dead end — which is the distinction INV-209 exists to force, and it only
   surfaced because the owning route was asked.

3. **`:1211` got a new escape token rather than a recorded-elsewhere verdict.** The spec asked for a
   verdict and offered tightening the vocabulary as the better fix. Neither worked: `has no` is load-
   bearing for two **true** positives ("declared schema has no `inline` parameter", "has no such
   parameter"), so tightening would lose them, and a verdict recorded only in a ledger entry leaves
   the report flagging the site forever — which would keep `unmarked` above zero and make the eventual
   gate unbuildable. So `MCP-NEGATIVE-SCAN: not-a-tool-claim` was added, honoured alongside
   `quoted-history`, and declared at the site with its reasoning. It converts a judgement into a
   greppable, reviewable decision, which is exactly why `quoted-history` exists.

   ⚠️ **Implementing it exposed a real inconsistency in the report:** the escapes were checked inside
   the *unit* while markers were checked in a ±6-line *window*, so an escape written as an HTML
   comment before a bullet landed in a different unit and did nothing. Both now use the window.

**Two guards fired and both were right; neither was weakened.**
`tests/test_scaffold_citations_and_database_type.py` caught my `:728` marker mentioning `inline=true`
without a negating word in its 200-character window — the parameter *is* undeclared, so the marker now
says so. `tests/test_prescribed_search_queries.py` caught two new `search_docs(query=…)` literals; both
were added to `VERIFIED_QUERIES` with their observed top hits and relevance, in that allowlist's idiom.

**And one expectation legitimately flipped.** `test_it_is_not_vacuous_on_the_live_corpus` asserted the
report finds ≥1 — correct when it was written with six live hits, and wrong once the corpus is clean.
Rewritten as `test_the_live_corpus_is_clean` **with the reason in its docstring**, per this spec's own
criterion that the expectation be updated rather than deleted; the detector's non-vacuity is proven on
scratch trees, which is where a claim about the detector belonged all along.
