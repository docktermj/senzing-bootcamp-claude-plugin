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
