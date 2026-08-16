# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp. Every entry is saved here, whatever it turns
out to be about. Entries routed `mcp-server` may **also** have been forwarded to Senzing —
only ever with your explicit yes, and with identifying details stripped; each entry's
`Upstream:` field records what happened.

**Started:** 2026-08-15

## Your Feedback

## Improvement: Wrong plugin version displayed in the WELCOME banner

**Date:** 2026-08-15
**Module:** Onboarding (preface / WELCOME banner)
**Priority:** High
**Source:** bootcamper-reported
**Routing:** plugin — the WELCOME banner step read `plugin.json` from the wrong on-disk clone (a stale/alternate checkout) instead of the plugin root actually driving this skill invocation; no Senzing MCP server involvement.
**Upstream:** not applicable

### What happened

The WELCOME banner displayed "Senzing Bootcamp v0.5.0", but the actual plugin version in use is v0.5.1. The onboarding step read the `version` field from a different clone of the plugin repo (`/home/senzing/senzing.git/senzing-bootcamp-claude-plugin/...`, which reports 0.5.0) instead of the plugin root actually serving this skill invocation (`/home/senzing/github.com/docktermj/senzing-bootcamp-claude-plugin/...`, which reports 0.5.1). `$CLAUDE_PLUGIN_ROOT` was empty in this environment, so the guide guessed at a path rather than resolving it authoritatively.

### Why it matters

Version mismatches undermine trust in the bootcamp's status displays generally.

### Suggested fix

Show the actual version of the plugin in use. If multiple plugin versions/checkouts are available on the machine and the correct one can't be resolved unambiguously, ask the bootcamper which version they want to run instead of guessing.

### Context when reported

- **Time:** 2026-08-15 21:14 local
- **Plugin version displayed (wrong):** 0.5.0
- **Plugin version actually in use:** 0.5.1
- **Workstation:** Linux 7.0.0-28-generic (x86_64)
- **Model / effort:** claude-sonnet-5 / low
- **Context size:** Unknown (approximate — not directly available)
- **Module / step:** current_module: none recorded yet (still in onboarding preface, before Bootcamp preparation); completed modules: none
- **Recent questions:** "Do you have any questions before we get started?" (onboarding preface, step 4); then the feedback-flow questions: what happened, why it matters, suggested fix, priority
- **Bootcamper responses:** Reported the version mismatch as feedback; confirmed the "what happened" summary; said it matters because "version mismatches make me not trust the bootcamp's status displays"; suggested showing the actual version, and asking the bootcamper to choose if multiple versions are available; priority = High (1)
- **Behind the scenes:** Onboarding preface Step 0/3 — read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` per `onboarding-flow.md`, but `$CLAUDE_PLUGIN_ROOT` was unset in this environment; the guide located a `plugin.json` via a filesystem search that matched a stale/alternate clone before finding the correct plugin root (which was actually given as this skill invocation's base directory).
- **Observed problem:** Banner showed v0.5.0 instead of the correct v0.5.1.
- **Expected behavior:** `onboarding-flow.md` Step 0 says to read the version from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` (falling back to "Unknown" if unreadable) — not to search the filesystem and pick an arbitrary match.
- **Divergence:** `$CLAUDE_PLUGIN_ROOT` was empty, so the fallback path ("Unknown") should have been used, or the skill's own base directory (given at invocation) should have been treated as authoritative. Instead a broader filesystem search found and used an unrelated clone's `plugin.json` first.
