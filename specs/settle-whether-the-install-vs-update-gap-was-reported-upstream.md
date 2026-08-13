# Two records disagree about whether the install-vs-update gap was reported upstream

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two records in this repo make contradictory claims about the same upstream submission.

**The plugin says it was sent.** `module-02-sdk-setup/SKILL.md:159`:

> That asymmetry is the same coverage gap **reported upstream on 2026-07-31** — the server documents
> installing, not updating.

**The coverage ledger said it was not.** Until 2026-08-13, the `module02-update-check-commands-unsupplied`
row in `specs/mcp-coverage.jsonl` carried `upstream: "not reported upstream"`, and
`coverage_ledger.py summary` listed it under "open coverage gap(s) … not reported upstream".

One of the two is wrong. The discrepancy was surfaced to the maintainer on 2026-08-13, who chose to
file anyway, so a combined version-lifecycle `feature` request went out that day covering this gap as
its second item — meaning **if the plugin's claim is accurate, Senzing now has two reports of the
same gap**, and if it is not, the plugin has been asserting a submission that never happened.

Submissions are anonymous with no reply channel (INV-135 forbids the one category that carries
identity), so upstream cannot be asked which is true. The evidence has to come from this repo.

## Root cause

The plugin's prose and the coverage ledger are updated by different skills at different times, and
nothing cross-checks them. `delegate-to-mcp-server` Step 9 records the upstream outcome on a ledger
row; the plugin sentence was written by whichever spec landed that guidance. Neither reads the other,
and `citations.py verify` checks that IDs and paths resolve, not that two prose claims about the same
event agree.

Note the ledger *does* record sends on adjacent dates for adjacent subjects — `inv160-inline-param-undeclared`
and `record-preview-registration-prerequisite-undocumented` both carry `sent 2026-07-30`, and the
declined `no-route-for-bootcampers-who-cannot-add-an-mcp-server` records a `category='feature'`
request sent **2026-07-31**. So a submission on or about that date is plausible; what is unestablished
is whether it covered *this* gap.

## Proposed change

**Settle it from the evidence, then correct whichever record is wrong.** The evidence available:

1. `feedback/PROCESSED.jsonl` and the five `feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK_*.md` archives
   — check whether a 2026-07-31 entry records the submission and what it covered.
2. `git log --since=2026-07-29 --until=2026-08-02` over `plugins/` and `specs/` — the commit that
   introduced the `:159` sentence will say what it was recording, and its spec will say whether a
   `submit_feedback` call was made or merely recommended.
3. `specs/IMPLEMENTED.md` entries dated 2026-07-31 — the ledger's `MCP re-check` and Summary fields
   record upstream sends explicitly elsewhere, so their silence or mention is evidence.
4. The `no-route-for-bootcampers-who-cannot-add-an-mcp-server` decline, which documents a 2026-07-31
   `feature` submission — determine whether `:159` is referring to **that** one, in which case the
   sentence is conflating a *different* gap's submission with this one.

Then, whichever way it resolves:

- **If a 2026-07-31 submission covering this gap is established:** correct the ledger row's
  `upstream` field to record both sends, and add a dated note to the row that the 2026-08-13 filing
  is a **duplicate**, so no future run treats the gap as unreported a third time.
- **If it is not established:** correct `:159` — it must not assert a submission the repo cannot
  evidence. Replace it with what is provable (the gap is real, and it was reported on 2026-08-13),
  and keep a dated note saying the earlier claim could not be substantiated.

⛔ **Do not file anything upstream as part of this spec.** The 2026-08-13 report already covers the
gap. Filing again on the strength of a resolved discrepancy would be the third submission.

## Acceptance criteria

- [ ] The question is answered from repo evidence, and the evidence is **named** in the ledger entry
      (which file, which commit, what it said) rather than summarised as a conclusion.
- [ ] Exactly one of `module-02-sdk-setup/SKILL.md:159` or the
      `module02-update-check-commands-unsupplied` ledger row is corrected, and the other is left
      alone because it turned out to be right.
- [ ] The corrected record carries a **dated note** saying what was checked and on what evidence, so
      the correction is legible as one.
- [ ] The `mcp-coverage.jsonl` row's `upstream` field ends in a state that tells a future run
      whether to re-file: either "sent <date(s)>, duplicate filed <date>" or "sent 2026-08-13 only;
      the 2026-07-31 claim was unsubstantiated and corrected".
- [ ] **No `submit_feedback` call is made.**
- [ ] If the answer is genuinely undeterminable from the repo, that is recorded as the outcome — with
      what was checked — rather than a guess being written into either record (INV-163).
- [ ] `tests/test_declined_ledger.py` and the full suite still pass; the coverage ledger stays
      append-only (a revised verdict is a new row with the same key, never an edit).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/mcp-coverage.jsonl` — one appended row for `module02-update-check-commands-unsupplied`
  (append-only, read last-wins).
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — `:159`, only if the claim is the
  one that turns out to be wrong.

## Source

- Feedback: none — self-observed while drafting the upstream reports on 2026-08-13
  (`Source: self-observed (assistant retrospective)`).
- Priority: **Low-Medium.** Nothing a Bootcamper sees is affected. The cost is a possible duplicate
  filing already sent, and a repo that asserts an event it may not be able to evidence — which is the
  same class as a dated Senzing claim nobody can re-check, applied to our own record.
- MCP re-check: **n/a (no Senzing fact)** — the underlying coverage gap was re-confirmed at server
  1.32.9 on 2026-08-13 (`sdk_guide(topic='install', platform='windows'|'linux_apt'|'macos_arm')`
  verify by existence only, no version-query or update command). This spec is about our own record of
  a submission, not about what the server serves.
- Upstream: **already sent 2026-08-13** as item 2 of a combined version-lifecycle `feature` request
  (anonymous, no reply possible). Whether an earlier 2026-07-31 send also exists is the subject of
  this spec.
- Related specs: `module02-dated-negatives-about-sdk-guide-carry-no-marker` (which recorded the
  discrepancy in its Source block), `no-route-for-bootcampers-who-cannot-add-an-mcp-server` (the
  decline documenting a different 2026-07-31 submission), INV-135 (never `license_request`),
  INV-163 (report what could not be determined).
