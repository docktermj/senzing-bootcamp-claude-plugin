# Declined Specs

Record of specs under `specs/` that the maintainer has **decided not to implement**. This file is
the counterpart to `IMPLEMENTED.md`: together they are the two terminal states a spec can reach, and
`implement-spec` subtracts both from the candidate set, so a spec named here is never offered again.

**The spec files named below stay exactly where they are.** They are not archived, moved or deleted.
The analysis in a declined spec is the reason the decision could be made at all, and its filename is
a permanent address — the same principle `INVARIANTS.md` applies when it marks a rule superseded
rather than removing it.

**Declined is not superseded, and not wrong.** A spec whose facts are wrong, or that a later spec
overtakes, is `feedback-to-specs`' business — the remedy there is a corrected or superseding spec.
This file is only for specs that are *correct* and deliberately not being built.

**A declined spec stays visible to deduplication.** `feedback-to-specs` Step 4 lists every
`specs/*.md` when triaging new feedback, and that is deliberate: if the same subject arrives again,
the triage must find the existing spec rather than write a second one. Declined means "not building
it", never "forget it existed".

**Why every entry needs a reason.** (This paragraph is deliberately not an `##` heading: every `##`
in this file is read as a declined spec name, so a prose heading here would be counted as one.)
`delegate-to-mcp-server` learned this for a different asset class and states it plainly: *"An
unreasoned keep is indistinguishable from 'nobody looked', and the next run will look again."* A
decline with no recorded reason costs more than no record at all, because the spec's own text argues
*for* the change and nothing argues against it.

**`Revisit if:` is what keeps this from becoming a graveyard.** Most declines are made against
current architecture, current tooling, or a current upstream gap — none of which are permanent.
Naming the condition that would reopen the question lets a future run check it cheaply instead of
re-deriving the whole argument. Write "nothing foreseeable" only when that is genuinely true.

<!-- New entries go directly below this line. Format:

## <spec-name>

- **Declined:** YYYY-MM-DD
- **Decided by:** <who made the call>
- **Reason:** <why not — required; never leave this empty>
- **Revisit if:** <the condition that would reopen it, or "nothing foreseeable">

-->

## inv050-layout-tree-names-three-artifacts-nothing-produces

- **Declined:** 2026-08-11
- **Decided by:** maintainer ("remove #2 as we won't be doing that")
- **Reason:** **Its central factual claim is false, and the work it proposes does not exist.** The
  spec says three tree entries — `config/session_log.jsonl`, `config/visualization_tracker.json`,
  `docs/completion_summary.md` — "say nothing" about not being produced. All three carry
  `(reserved)` (`specs/INVARIANTS.md:166,167,197`), annotated deliberately on 2026-07-17 via
  `specs/layout-tree-reconciliation.md` (commit `cc46a55`). The audit that produced it ran
  `line.split("#")[0]` before matching, discarding the comment column where the annotation lives —
  the evidence refuting the finding sat in the part the scan deleted. Re-verified 2026-08-11: the
  corrected check returns **zero** unaccounted entries across 24 files and 30 directories. The one
  idea worth keeping was rebuilt on an honest premise as
  `specs/inv050-tree-has-no-reachability-guard.md`, implemented the same day.
- ⚠️ **This entry deliberately widens what this file records, and a reader should know it.** The
  header above says declined is "only for specs that are *correct* and deliberately not being
  built", and by that rule a wrong spec belongs to `feedback-to-specs` instead. That remedy was
  applied first — the superseding spec exists and this spec carries a `## Superseded by` pointer —
  but supersession is **not** a state `implement-spec` Step 1 subtracts, so the spec kept being
  offered on every run with its false Problem section as the summary. This is recorded here because
  it is the only terminal state available, not because the spec was correct.
- **Revisit if:** `implement-spec` gains a third terminal state for superseded specs, in which case
  this entry should move there and this file's stated scope stops being stretched. Nothing about the
  spec's own subject would reopen it — the claim is refuted, not merely unwanted.

## no-route-for-bootcampers-who-cannot-add-an-mcp-server

- **Declined:** 2026-07-31
- **Decided by:** maintainer
- **Reason:** **Architectural.** The SBCP's dependency on the Senzing MCP server is deliberate and
  load-bearing: INV-080 makes it the sole source of every Senzing fact, and there is no offline mode
  to degrade to. Adding a sanctioned alternative access path is a change to what the plugin *is*,
  not a defect to repair — so it is a decision about the product's boundary rather than a spec to
  implement. The spec's analysis stands and is worth keeping: the failure mode it describes is real
  (a bootcamper blocked by policy meets a health check that only knows how to diagnose connectivity),
  and the routes it found are real (the server's own tool descriptions name a stdio-mode local binary
  and a private deployment).
- **Revisit if:** Senzing documents a self-service route for stdio mode or the private deployment. A
  `category='feature'` request asking for exactly that was sent 2026-07-31 via `submit_feedback`
  (anonymous, so no reply is possible). If the indexed corpus gains that coverage, the premise
  changes: pointing a blocked bootcamper at a documented route becomes a small documentation change
  rather than an architectural one, and this should be reopened. The spec's own re-verification
  clause already requires that check at implementation time.
- **Revisit check, 2026-08-13 (server 1.32.9, docs index 2026-08-11, 14,240 docs): condition NOT met,
  and it has moved further away.** Decision unchanged — this note records evidence, not a reversal.
  - The corpus still documents neither route. Re-ran the spec's keyword query (same result as
    2026-07-31), and additionally asked the document that *owns* the subject:
    `search_docs(query='Agentic Entity Resolution MCP server configuration setup connect assistant')`
    reaches `senzing.com/docs/agentic`, the MCP server's own page, which returns an overview and
    carries no setup or self-hosting content. So "named but undocumented" is now established via the
    owning route rather than by a query that merely missed.
  - ⚠️ **One of the two routes lost its citation.** At 1.32.3 `sdk_guide`'s description named a
    **stdio mode** whose package URL was a local `sz-mcp-coworker extract` command. At 1.32.9 neither
    "stdio" nor `sz-mcp-coworker` appears in that description or anywhere in the `get_capabilities`
    manifest. Whether the mode was retired or the text trimmed cannot be told from here.
  - The **private deployment** is still named, though on a different surface than the spec cited:
    `get_capabilities`' tool manifest, in its `get_sample_data` entry — not that tool's own schema
    description.
  - Net effect on the revisit test: the upstream `feature` request has not been actioned in the
    corpus, and the evidence base for the spec's routes has **narrowed from two to one**. Anyone
    reopening this should re-run the check above rather than trusting the spec's 1.32.3 citations.
  - ⚠️ **Recorded because this entry was briefly implemented in error on 2026-08-13** (reverted in
    `f12de7d`). The cause was a candidate-listing that compared only against `IMPLEMENTED.md` and did
    not subtract `DECLINED.md`, as `implement-spec` Step 3 requires; `tests/test_declined_ledger.py`
    caught it. Noted here so the next reader knows this entry has been tested against the guard and
    survived, rather than wondering why the git history touches it.
