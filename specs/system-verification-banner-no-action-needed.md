# State plainly in the SYSTEM VERIFICATION COMPLETE banner that no action is required

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The all-checks-passed banner reads:

```text
╔══════════════════════════════════════════════════════════╗
║  ✅ SYSTEM VERIFICATION COMPLETE                         ║
║                                                          ║
║  All checks passed. Your environment is verified and     ║
║  ready for subsequent modules.                           ║
╚══════════════════════════════════════════════════════════╝
```

It announces "complete" but does not tell the bootcamper they have nothing to do,
which can leave them wondering whether an action is required — especially right before
the transition question asks if they're ready to move on.

## Root cause

`plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-report-close.md`,
Step 9 success banner at `:24-31`. The banner states the environment is verified and
ready but contains no "nothing for you to do" reassurance. This is the only occurrence
of the banner.

**Invariant note:** no invariant governs this banner's wording; this is a wording-only
addition (INV-082 concerns synthetic-record verification content, not the banner
text).

## Proposed change

Add a plain no-action line inside or immediately after the banner, e.g.
"Nothing for you to do here — you're all set to continue." Keep it adjacent to the
existing banner in `phase2-report-close.md` Step 9, before the transition question.

## Acceptance criteria

- [ ] The SYSTEM VERIFICATION COMPLETE success path states explicitly that no action is required of the bootcamper.
- [ ] The line sits inside or immediately after the existing banner, before the transition question.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-report-close.md` — Step 9 success banner (`:24-31`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Tell the bootcamper explicitly that nothing is required of them in the SYSTEM VERIFICATION COMPLETE banner" (2026-07-22, Module System verification)
- Priority: Low
- Related specs: none
