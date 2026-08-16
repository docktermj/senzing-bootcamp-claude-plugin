# A spec the maintainer decides not to implement has nowhere to live, so it is offered forever

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`specs/` has exactly one terminal state: implemented. `implement-spec` Step 1 computes

> **Unimplemented = candidates − implemented**

where candidates is every `specs/*.md` minus three meta files (`INVARIANTS`, `todo`, `IMPLEMENTED`).
There is no representation for **decided against**, so a spec the maintainer rules out stays in the
candidate set permanently.

Three consequences, in increasing severity:

1. **Discovery re-offers it every run.** Each `implement-spec` invocation lists it, and the
   maintainer answers the same question again.
2. **The reasoning is nowhere.** A decision made in conversation dies at session end. The next run
   has the spec's full argument *for* the change and no record of the argument against it, so it
   re-derives, re-proposes, and re-asks.
3. **It can be implemented by accident.** The spec file reads as pending work — that is what a spec
   file *is*. Nothing in it says a decision was taken. A later session, or a different person, can
   implement something that was deliberately rejected.

This is live now: `no-route-for-bootcampers-who-cannot-add-an-mcp-server` was declined on
2026-07-31 as an architectural decision — the SBCP's dependency on the Senzing MCP server is
deliberate and load-bearing (INV-080), so adding a sanctioned alternative path changes what the
plugin is rather than fixing a defect. Nothing records that.

**A second consumer would report it as outstanding too.** `citations.py`'s census derives spec names
from `specs/*.md` minus its own `META_SPECS` set (`:48`, `:114-122`) and prints
`unimplemented: <name>` (`:229`) for any spec file with no ledger heading. A new ledger file that is
not added to that set would itself be counted as a spec, and every declined spec would keep showing
as unimplemented in a second place.

## Root cause

The ledger was designed around a single outcome, because for a long time there was only one: specs
were written to be implemented, and the ones that were not simply had not been reached yet.
"Reached but rejected" is a different state that never came up until the plugin matured enough for
architectural boundaries to be worth defending.

**This repo has already solved the same problem for a different asset class.**
`delegate-to-mcp-server` records a `keep-by-design` verdict with a **required** `--reason`, and says
exactly why:

> *"A large fraction of legitimate findings end in **keep** — record those too, or the next run
> re-litigates them."* (`:50`)
> *"An unreasoned keep is indistinguishable from 'nobody looked', and the next run will look
> again."* (`:230`)

Specs need the same thing and never got it.

## Proposed change

1. **Add `specs/DECLINED.md`**, mirroring `IMPLEMENTED.md`'s shape so the detection idiom is
   identical: a `## <spec-name>` heading whose text matches the spec's filename without `.md`. Its
   header states that the file records decisions *not* to implement, and that the spec files it names
   stay in place.
2. **Four fields per entry**, two of which carry the weight:

   ```markdown
   ## <spec-name>

   - **Declined:** YYYY-MM-DD
   - **Decided by:** maintainer
   - **Reason:** <why — required; an unreasoned decline is indistinguishable from "nobody looked">
   - **Revisit if:** <the condition that would reopen it, or "nothing foreseeable">
   ```

   **Revisit if** is what stops this becoming a graveyard. A decision taken against current
   architecture is not permanent, and naming the trigger lets a future run check cheaply instead of
   re-arguing from scratch.
3. **Subtract declined specs in `implement-spec` Step 1**: `Unimplemented = candidates − implemented
   − declined`. Add a short section on how to decline one, and require the maintainer's explicit
   decision — this skill must never decline a spec on its own initiative.
4. **Add `DECLINED` to `citations.py`'s `META_SPECS`** (`:48`) so the new ledger is not itself counted
   as a spec, and teach the census to report declined specs as a separate figure rather than folding
   them into `unimplemented`.
5. **Leave the spec file exactly where it is.** Same philosophy as `INVARIANTS.md` never deleting a
   superseded rule: the analysis is the value, and its address must stay resolvable. Archiving or
   deleting a declined spec would lose the reasoning that justified declining it.

⚠️ **Do not change `feedback-to-specs`' dedup.** Its Step 4 lists every `specs/*.md` to deduplicate
against, and a declined spec **must** stay visible there — otherwise the next feedback entry on the
same subject produces a duplicate spec, and the maintainer declines it again. Declined means "not
building it", not "forget it existed".

⚠️ **Do not touch `coverage_reports.py`.** It reads only `IMPLEMENTED.md` (`:51-52`), so it is
unaffected. Verified rather than assumed — named here so the implementer does not go looking.

⚠️ **A declined spec is not a superseded one.** If a spec is wrong, or has been overtaken by another
spec, that is `feedback-to-specs`' business and the remedy is a corrected or superseding spec.
`DECLINED.md` is only for specs that are *correct* and deliberately not being built.

## Acceptance criteria

- [ ] `specs/DECLINED.md` exists with a header explaining what it records and that named spec files
      stay in place, plus the four-field entry format.
- [ ] Every entry carries a non-empty **Reason** and a **Revisit if**; a test fails if either is
      missing or empty.
- [ ] `implement-spec` Step 1 subtracts declined specs, and a "how to decline" section requires the
      maintainer's explicit decision — the skill never declines on its own initiative.
- [ ] `DECLINED` is in `citations.py`'s `META_SPECS`, and the census reports declined specs
      separately instead of counting them as `unimplemented` — checked by **running the census**
      (INV-182: this criterion names a second consumer, so it is verified against that consumer).
- [ ] No spec name appears in **both** `IMPLEMENTED.md` and `DECLINED.md`; a test asserts it.
- [ ] Every name in `DECLINED.md` resolves to a real `specs/<name>.md`; a test asserts it, so the
      ledger cannot name something imaginary.
- [ ] `feedback-to-specs`' dedup still sees declined specs — verified by **opening its Step 4** and
      confirming it is unchanged.
- [ ] `no-route-for-bootcampers-who-cannot-add-an-mcp-server` is recorded as the first entry, with
      the architectural reason and the concrete revisit trigger (the `category='feature'` request
      sent 2026-07-31 asking Senzing to document the stdio / private-deployment routes).
- [ ] Running discovery mode afterwards lists **eight** specs, not nine, and does not name the
      declined one — the end-to-end check that the mechanism works.
- [ ] `citations.py verify` stays clean and the full suite passes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/DECLINED.md` — new.
- `.claude/skills/implement-spec/SKILL.md` — the meta-file list (`:45-50`), Step 1's candidate
  computation (`:54-57`), and a new "how to decline" section.
- `.claude/skills/compact-dev-environment/citations.py` — `META_SPECS` (`:48`) and the census's
  spec/ledger reporting (`:224-229`).
- `tests/` — the DECLINED-ledger integrity assertions.

## Source

- **Found by:** the maintainer, 2026-07-31, on being offered
  `no-route-for-bootcampers-who-cannot-add-an-mcp-server` and ruling it out as an architectural
  decision — then asking directly how the repo tracks requests it does not implement. The answer was
  that it does not.
- Priority: **Medium.** Nothing is broken and no Bootcamper is affected. The cost is process: without
  it, every declined spec is re-offered indefinitely and its rejection reasoning is lost, which is the
  re-litigation cost `delegate-to-mcp-server` already learned to avoid.
- MCP re-check: **n/a (no Senzing fact), server 1.32.3, 2026-07-31.** This is maintainer tooling under
  `.claude/` and a ledger under `specs/`; no MCP tool owns any of it and none was called. Stated
  rather than skipped per INV-080.
- Upstream: not applicable.
- Related specs: none — no existing spec covers spec lifecycle. The design precedent is
  `delegate-to-mcp-server`'s `keep-by-design` verdict and its required reason, and
  `specs/topical-index-for-the-invariants.md`'s principle that a permanent address is never removed,
  only re-labelled.
