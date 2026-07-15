---
description: Analyze a bootcamp feedback file and generate improvement specs under specs/ (maintainer tool).
argument-hint: "[path to feedback file]"
---

Maintainer request: analyze collected bootcamp feedback and turn it into
improvement specs.

Invoke the `feedback-to-specs` skill and follow it end to end: locate and read
the feedback file, parse each item, triage it against `specs/invariants.md` and
the existing `specs/*.md` (deduplicating), confirm root causes in the codebase,
and write one or more `specs/<title>.md` files. Finish with the triage table and
the list of specs created. Do not implement the fixes unless asked.

Feedback file to analyze: $ARGUMENTS

If `$ARGUMENTS` is empty, default to `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` at the
repo root, then `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`; if neither
exists, say so and stop.
