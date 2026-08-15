# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp. Every entry is saved here, whatever it turns
out to be about. Entries routed `mcp-server` may **also** have been forwarded to Senzing —
only ever with your explicit yes, and with identifying details stripped; each entry's
`Upstream:` field records what happened.

**Started:** 2026-08-15

## Your Feedback

## Improvement: Auto-mode option should not be offered during a live bootcamp run

**Date:** 2026-08-15
**Module:** General (onboarding preface)
**Priority:** High
**Source:** bootcamper-reported
**Routing:** unclear — the plugin's skills/hooks contain no reference to "auto-mode"; it appears to originate from the surrounding Claude Code CLI harness (a session-level "Auto Mode" toggle) rather than from any bootcamp-plugin skill or the Senzing MCP server, so the responsible component cannot be pinned to either of the two options this template distinguishes.
**Upstream:** not applicable

### What happened

While taking the bootcamp, the bootcamper was asked about "auto-mode for the bootcamp." They believe this option should only be available during bootcamp plugin development, never surfaced to someone actually taking the bootcamp.

### Why it matters

It confuses the experience and undermines confidence in the guided flow.

### Suggested fix

Don't ask the question — suppress the auto-mode prompt entirely for bootcamper-facing runs.

### Context when reported

- **Time:** 2026-08-15 10:00 local
- **Plugin version:** 0.5.0
- **Workstation:** Linux 7.0.0-28-generic (x86_64)
- **Model / effort:** claude-sonnet-5 / low
- **Context size:** Unknown
- **Module / step:** current_module: Unknown (none recorded yet — still in onboarding preface); current_step: Unknown
- **Recent questions:** "Do you have any questions before we get started?" (pending, not yet answered — bootcamper submitted feedback instead)
- **Bootcamper responses:** N/A — feedback flow interrupted the pending question before it was answered
- **Behind the scenes:** `UserPromptSubmit` hook detected the "bootcamp feedback:" trigger phrase and routed into the feedback workflow (`bootcamp-onboarding/feedback.md`) during the onboarding preface, before Bootcamp preparation had run
- **Observed problem:** An "auto-mode" question was presented to the bootcamper during a live bootcamp run
- **Expected behavior:** No bootcamp-plugin skill, hook, or ground rule references "auto-mode" (verified by search of the plugin source) — the bootcamp's own question set (Core/Customized, module selection, verbosity, language) contains nothing matching this
- **Divergence:** The prompt likely came from the Claude Code CLI harness's own "Auto Mode" session setting, not from the bootcamp plugin's content — it is presented alongside the bootcamp but is not part of it
