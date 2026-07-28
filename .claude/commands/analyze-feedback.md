---
description: Analyze a bootcamp feedback file and generate improvement specs under specs/ (maintainer tool).
argument-hint: "[path to feedback file]"
---

Maintainer request: analyze collected bootcamp feedback and turn it into
improvement specs.

Invoke the `feedback-to-specs` skill and follow it end to end: locate and read
the feedback file, parse each item, **re-verify every Senzing fact against the live
Senzing MCP server** (the server ships independently of this plugin, so a report may
be stale, already fixed, or now contradicted), triage each item against
`specs/INVARIANTS.md` and the existing `specs/*.md` (deduplicating), confirm root
causes in the codebase, and write one or more `specs/<title>.md` files. Where the
current server is itself the defect, draft an upstream report and ask before sending
it via `submit_feedback`. Finish with the triage table — including what the re-check
found and the server version it ran against — and the list of specs created. Do not
implement the fixes unless asked.

Feedback file to analyze: $ARGUMENTS

If `$ARGUMENTS` is empty, default to `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` at the
repo root, then `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`; if neither
exists, say so and stop.
