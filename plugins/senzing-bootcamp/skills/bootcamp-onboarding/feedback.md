# Bootcamp Feedback Workflow (available at any time)

The bootcamper can submit feedback at any point in the bootcamp: onboarding, any
module, or graduation. Feedback is saved locally to
`docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` and is never sent anywhere
unless the bootcamper explicitly asks.

This workflow is triggered by the plugin's `UserPromptSubmit` hook ("to capture
bootcamp feedback") or by the `/bootcamp-feedback` command, or whenever the
bootcamper says something like "bootcamp feedback", "I have feedback", or "report
an issue". Follow `ground-rules.md`: one 👉 question per turn, end the turn on it.

## Step 0: Capture context silently

Before asking anything, capture the bootcamper's context so they never have to
re-explain it:

- Read `config/bootcamp_progress.json` for the current module and completed modules (record "Unknown" if the file is missing).
- Note what the bootcamper was doing in the last few turns.

## Step 1: Ensure the feedback file exists

If `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` does not exist, create the
`docs/feedback/` directory and write this header once:

```markdown
# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp. Saved locally only.

**Started:** YYYY-MM-DD

## Your Feedback
```

## Step 2: Gather the feedback, one 👉 question at a time

Ask these in order, each as its own turn (pre-fill the module from captured
context so you do not ask the bootcamper to repeat it):

1. 👉 **What would you like to give feedback about?**
2. 👉 **What happened, or what would you change?**
3. 👉 **Why does it matter to you?**
4. 👉 **Do you have a suggested fix or improvement?**
5. 👉 **What priority would you give this: high, medium, or low?**

If the bootcamper gives everything in one message, do not re-ask: confirm what you
captured and proceed.

## Step 3: Append the entry (never overwrite)

Append a formatted entry to the "Your Feedback" section. Append only: never
rewrite the file, so earlier entries are preserved.

```markdown
## Improvement: [brief title from the bootcamper's description]

**Date:** YYYY-MM-DD
**Module:** [module number or "General"]
**Priority:** [High/Medium/Low]

### What happened

[the bootcamper's description]

### Why it matters

[the bootcamper's stated impact]

### Suggested fix

[the bootcamper's suggestion, or "None provided"]

### Context when reported

- **Current module:** [from config/bootcamp_progress.json, or "Unknown"]
- **What they were doing:** [short summary]
```

## Step 4: Confirm and return

- Confirm: "Saved your feedback to `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`. You can add more anytime by saying \"bootcamp feedback\"."
- Do NOT submit feedback to the Senzing MCP server or anywhere external unless the bootcamper explicitly asks.
- Return the bootcamper to exactly where they left off, resuming the pending step or question. Do not make them re-navigate.
