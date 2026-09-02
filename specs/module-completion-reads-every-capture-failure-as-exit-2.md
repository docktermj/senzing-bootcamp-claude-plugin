# module-completion treats every capture failure as exit 2, and exit 1 needs the opposite response

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`bootcamp-onboarding/module-completion.md:278` handles a failed screenshot capture:

> 2. **If it exits non-zero** (exit 2 = nothing was captured): skip screenshots, keep the
>    visualization's HTML link in the recap, and continue. … **Read which of the three reasons it
>    gave** — they are not interchangeable and only one is about a missing install: no requested
>    tab exists in this app; **no browser was found**…; or **a browser was found but every capture
>    failed**…

All **three** reasons it lists are `exit 2` reasons. `capture_screenshots.py` also exits **1**,
for a different class of failure — an **unrecognized tab id**, rejected before any capture — and
INV-122 now makes that distinction normative (three codes: 0 captured, 1 caller-side tab error,
2 no headless capability). The step maps every non-zero exit onto the exit-2 response.

**The two need opposite responses, and this step gives the wrong one for exit 1.**

| | exit 2 | exit 1 |
|---|---|---|
| cause | no headless capability, or nothing capturable | a tab id outside the script's vocabulary |
| correct response | skip screenshots, keep the HTML link, continue | **fix the request and re-run** — every tab was capturable |
| this step's response | skip and continue ✅ | skip and continue ❌ |

⚠️ **The step's own command is what makes this reachable.** It passes a hardcoded list:

```
--tabs graph,stats,matchkeys,features,overlap,probe
```

If that list drifts from the script's tab vocabulary — a rename, a retired id, a typo in an edit
to this file — the helper exits 1 having written **nothing**, and this step tells the guide to
skip screenshots and continue. The Bootcamper's recap silently loses **every** screenshot, on a
run where all six tabs were capturable, and the guide is told not to investigate. That is the
INV-146 concern exactly ("a count cap or 'best of' selection can only delete unique content") —
reached through a caller error rather than a cap.

## Root cause

The step predates INV-122's exit-code distinction, which was added 2026-09-02 by
`capture-screenshots-aborts-where-inv-122-says-skip`. When it was written, the reasons worth
distinguishing were the three within exit 2, and its parenthetical `(exit 2 = nothing was
captured)` was an accurate gloss of the only failing code that mattered. Amending INV-122 to make
three codes normative left this step describing two of them as one.

⛔ **This is the "a rule applied to some of the sites it binds" class**, arriving from the
invariant side: INV-122 gained a clause and the sites that consume it were not swept. The
amendment updated `capture_screenshots.py` (the producer) and
`.claude/skills/dry-run/phase2-hooks-and-scripts.md` (the dev-side reader) and missed the
**shipped consumer**.

## Proposed change

1. Split the exit handling at `module-completion.md:278`: **exit 1** is a caller error — the
   `--tabs` list disagrees with the app's tab vocabulary; report it, do not treat it as a missing
   dependency, and re-run with a corrected list rather than continuing without screenshots.
   **exit 2** keeps the existing behavior and its three reasons verbatim.
2. Cite INV-122 at the split, since that is where the rule now binds (INV-183).
3. ⚠️ Sweep for other consumers rather than fixing this one line (INV-246): any file that reads
   this helper's exit status, or that hardcodes a `--tabs` list, is in the same class.
4. Consider whether the hardcoded six-tab list should be derived rather than written — out of
   scope for this spec, but it is the reason exit 1 is reachable at all.

## Acceptance criteria

- [ ] `module-completion.md` distinguishes exit 1 from exit 2 and gives each its own response,
      with exit 1 leading to a corrected re-run rather than to skipping screenshots.
- [ ] The three exit-2 reasons and the "do not suggest installing a browser" rule survive
      unchanged — they are correct and hard-won.
- [ ] Every shipped file that reads this helper's exit status is checked, found by scanning
      rather than from this spec's list.
- [ ] A test asserts no shipped file glosses non-zero as exit 2 alone.
- [ ] Negative control: collapse the two codes back into one branch, confirm the test fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — split the exit handling
- `tests/` — guard that non-zero is not glossed as exit 2

## Source

- Feedback: `/production-readiness-audit`, 2026-09-02 (`Source: self-observed (assistant retrospective)`)
- Priority: Low — reachable only when the `--tabs` list disagrees with the script's vocabulary, which it does not today; the cost when it happens is a recap with every screenshot missing and a guide instructed not to look into it
- MCP re-check: **n/a (no Senzing fact).** The subject is the plugin's own helper and its own invariant. The exit codes were verified live on 2026-09-02 while implementing `capture-screenshots-aborts-where-inv-122-says-skip` (exit 1 on an unrecognized id with zero files written; exit 2 with the pre-flight message) and are not re-claimed here.
- Upstream: not applicable.
- Related specs: `specs/capture-screenshots-aborts-where-inv-122-says-skip.md` (implemented 2026-09-02 — the amendment this step was not swept for)
