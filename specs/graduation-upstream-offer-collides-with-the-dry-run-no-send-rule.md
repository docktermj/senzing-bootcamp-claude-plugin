# Graduation's upstream-offer step asks a question a dry run is forbidden to honor

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two rules that are each correct on their own make a phase-3 dry run walk into a question it cannot
answer honestly.

**Graduation Step 0** (`graduation/SKILL.md:322-327`) instructs the guide to offer the upstream
forward and send on a yes:

> **`Upstream:`** for an `mcp-server`/`both` verdict, offer the forward **once** per
> `../bootcamp-onboarding/feedback.md` Step 3c: show the exact message, strip anything identifying
> (INV-065), and send only on a yes. Batch the offer — one question covering all such findings […]

**`/dry-run`'s absolute rules** (`.claude/skills/dry-run/SKILL.md`) forbid exactly that call:

> ⛔ **Never send anything outside the machine.** Do not call `submit_feedback` under any category.
> Verify its *schema* — never invoke it. A dry run must not file junk upstream or transmit a name
> and email.

A phase-3 walk that reaches graduation with any `mcp-server`-routed retrospective finding must
therefore do one of three things, and **all three are bad**:

1. **Send** — violating the dry-run skill's hardest rule and filing dry-run noise into Senzing's
   real upstream queue.
2. **Skip the offer silently** — deviating from the module under test without saying so, which
   corrupts exactly the thing phase 3 exists to observe.
3. **Ask, then refuse** — which is what happened on this run (2026-08-27): the maintainer answered
   "yes" in character as the Bootcamper, and the walk then had to break character to explain that
   the send could not happen. The question was real, the answer was real, and the action was
   impossible.

Option 3 is the least-bad and is what a careful runner will land on, but it means **the walk asks a
question it already knows it cannot honor** — and it puts the maintainer in the position of
answering a gate whose outcome was predetermined.

**This is not hypothetical or rare: it fires on every phase-3 run that reaches graduation with at
least one `mcp-server` finding.** Retrospective findings *skew* toward `mcp-server` — Step 0 says so
in its own words, because a tool behaving differently than documented is the defect class a
bootcamper cannot report. So the collision is close to guaranteed, not an edge case. It has simply
never been hit before because, until this run, no phase-3 walk had ever reached graduation.

## Root cause

The two documents were written against different assumptions about who is running the bootcamp and
never cross-reference each other:

- `graduation/SKILL.md` assumes a real Bootcamper whose consent is the only gate on sending. Its
  `Upstream:` vocabulary (`not applicable | offered, declined | submitted YYYY-MM-DD | submission
  failed: reason`) has **no value for "the runner is forbidden to send"** — the closest, `offered,
  declined`, is factually wrong when the Bootcamper said yes.
- `.claude/skills/dry-run/SKILL.md` forbids the call globally but scopes its reasoning to phase 1
  ("Verify its *schema* — never invoke it"), and its phase-3 doc never mentions graduation's
  upstream offer. Phase 3's own "How far the walk can go" section assumed the walk would stop well
  before graduation, so the interaction was never considered.

Neither file is wrong about its own concern. What is missing is the seam.

## Proposed change

1. **Give `/dry-run`'s phase-3 doc an explicit instruction for this gate.** The walk should still
   **present** the offer — it is a real gate under test and skipping it silently is worse — but must
   record the outcome truthfully and not send. State the wording to use so the runner is not
   improvising a disclosure mid-walk, and say plainly that breaking character here is correct.
2. **Add an `Upstream:` value for it.** Extend `feedback.md` Step 3's vocabulary with something like
   `submission blocked: <reason>` so the entry can record "the Bootcamper agreed; the runner was
   forbidden to send" as a first-class outcome. Today that outcome has to be written as free text,
   and the nearest legal value (`offered, declined`) actively misrepresents the Bootcamper's answer
   — which matters because `feedback-to-specs` reads this field to decide whether an upstream report
   is still owed. ⚠️ This is the half with downstream consequences: a finding recorded as `declined`
   is a finding nobody will forward.
3. **Consider whether the offer should be suppressed entirely under a dry run.** Argument for: it
   removes a question the maintainer cannot meaningfully answer. Argument against, and the reason
   this spec does not simply recommend it: the offer *is* module behavior under test — its wording,
   its batching, and its INV-065 stripping are all things phase 3 should observe — and suppressing
   it means that gate is never walked. **Recommend presenting it and blocking the send** (option 1),
   with suppression documented as the maintainer's call.
4. ⛔ **Do not resolve this by relaxing the dry-run rule.** The prohibition is load-bearing: a dry
   run generates exactly the plausible-looking-but-not-real findings that should never reach a
   vendor's queue, and this run produced four such entries within one retrospective.

## Acceptance criteria

- [ ] `.claude/skills/dry-run/phase3-conversational.md` names graduation's Step 0 upstream offer
      explicitly, states that the offer is presented but the send is refused, and gives the
      disclosure wording so it is not improvised.
- [ ] `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` Step 3's `Upstream:`
      vocabulary carries a value for a blocked-but-consented submission, and
      `graduation/SKILL.md` Step 0's `Upstream:` bullet references it.
- [ ] A finding recorded with that value is not readable as "the Bootcamper declined" — verified by
      checking how `feedback-to-specs` triages it.
- [ ] A test asserts the new `Upstream:` value is in the documented vocabulary wherever that
      vocabulary is enumerated (it appears in at least `feedback.md` and `graduation/SKILL.md`), so
      the two cannot drift. Stdlib only, no `plugins/` import (INV-108).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/dry-run/phase3-conversational.md` — instruction for the graduation upstream gate
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` — Step 3 `Upstream:` vocabulary
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 0's `Upstream:` bullet
- `tests/` — a guard on the shared vocabulary

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-27, in the analysis stretch, on the first
  phase-3 walk ever to reach Bootcamp graduation (`Source: self-observed (assistant
  retrospective)`). Surfaced by actually running Step 0's retrospective, producing four findings,
  triaging two as `mcp-server`, presenting the batched offer, and receiving a "yes" that could not
  be acted on.
- Priority: **Medium.** No bootcamper is affected — this fires only under `/dry-run` — and the
  correct behavior is reachable by a careful runner. It is filed at Medium rather than Low for two
  reasons: it will recur on **every** future phase-3 run that reaches graduation, and the
  vocabulary gap means a consented-but-blocked finding gets recorded as `declined`, which is the
  one value that guarantees nobody forwards it later. The second is a real information loss, not
  just an awkward moment.
- MCP re-check: **n/a (no Senzing fact).** The collision is between two of this repo's own
  instruction files; nothing about Senzing, the SDK or the server is asserted, so there is no server
  fact to re-verify and no absence claim to substantiate. `get_capabilities` was called at the start
  of this run to date it: server **1.33.0**, 2026-08-27. ⛔ `submit_feedback` was **not** called at
  any point in this session, under any category — which is the rule this spec is about.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `specs/feedback-routing-has-no-verdict-for-a-defect-neither-component-owns.md`
  (the other gap in this same routing/`Upstream:` vocabulary);
  `specs/mcp-tools-disagree-on-eval-license-duration.md` and
  `specs/find-examples-self-describes-two-different-coverages.md` (both carry "not yet sent — needs
  maintainer approval", the same blocked-send situation recorded from the maintainer side rather
  than the Bootcamper side)

## Deviations from this spec, and why (2026-08-28)

**Implemented as proposed — option 1, present the offer and block the send.** The spec left
suppression open as the maintainer's call and recommended against it; that recommendation is
followed, for the reason it gives: the offer's wording, batching and INV-065 stripping are module
behavior under test, and a walk that silently omits a gate corrupts what phase 3 exists to observe.

⚠️ **One claim in this spec is overstated, and the implementation does not rely on it.** The spec
argues that a finding recorded as `offered, declined` *"is a finding nobody will forward"*, because
`feedback-to-specs` reads the field to decide whether an upstream report is still owed. Checked at
`.claude/skills/feedback-to-specs/SKILL.md:219`: that step skips a finding only when the field says
it was already **sent** (`sent <date> via submit_feedback`); `offered, declined` is not a skip
condition, so such a finding is still considered for filing. The narrower harm is real and is what
the fix is written against — the field is the record of what happened, and `offered, declined`
records the opposite of what happened, reading as *"considered and rejected"* to whoever decides
later. Corrected here rather than in the spec body, per this skill's rule against editing spec
content; the guard's docstring states the accurate version so the overstatement is not inherited.

⛔ **An unrelated existing guard had to be corrected, and it is worth the maintainer's eye.**
`tests/test_feedback_routing.py` sliced graduation's Step 0 as `t[start : start + 4500]` — a magic
number standing in for "the section". The `**Non-blocking.**` bullet sat **18 characters** inside
that window, so the guard was one edit from failing on content it was never meant to police, and it
duly failed on the addition to the `Upstream:` bullet above it. Three assertions now slice at the
**next heading** instead, with an anti-vacuity floor so a collapsed section fails rather than passes
(INV-265). ⚠️ **No assertion was weakened** — each still requires exactly what it required, and both
directions are negative-controlled: removing the `Non-blocking` bullet fails, and stubbing the
section fails on the floor. The addition to graduation was also **shortened** in the same pass,
because it was restating what `feedback.md` Step 3 already says instead of citing it (INV-179).
