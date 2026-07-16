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

Before asking anything, silently capture as much relevant context as possible, so
the bootcamper never has to re-explain it and so `feedback-to-specs` can later
reconstruct the exact situation. Gather only from available sources — never ask an
extra question for this — and record "Unknown"/"Unavailable" (never a guess) when a
source is missing:

- **Time:** the current date and time.
- **Plugin version:** the `version` field of `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`.
- **Module and step:** `current_module`, `current_step`, and completed modules from `config/bootcamp_progress.json`.
- **Recent questions and responses:** the last few 👉 questions asked and the bootcamper's answers, from the transcript.
- **Behind the scenes:** what the plugin was doing — which hook fired, which skill/phase/gate was active, and any relevant config or state.
- **Observed problem:** what the bootcamper saw.
- **Expected behavior:** what the active hooks, skills, and `ground-rules.md` imply should have happened.
- **Divergence:** the best assessment of why the expected action did not occur.

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
2. 👉 **What happened?**
3. 👉 **Why does it matter to you?**
4. 👉 **Do you have a suggested fix?**
5. 👉 **What priority would you give this? Reply with a number:** (1) High, (2) Medium, (3) Low.

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

- **Time:** [YYYY-MM-DD HH:MM local, or "Unknown"]
- **Plugin version:** [from `.claude-plugin/plugin.json`, or "Unknown"]
- **Module / step:** [`current_module` / `current_step` from `config/bootcamp_progress.json`, or "Unknown"]
- **Recent questions:** [the last few 👉 questions asked]
- **Bootcamper responses:** [their answers to those questions]
- **Behind the scenes:** [active hook/skill/phase/gate and relevant state]
- **Observed problem:** [what the bootcamper saw]
- **Expected behavior:** [what the active hooks/skills/ground-rules imply should happen]
- **Divergence:** [why expected did not match actual]
```

## Step 4: Confirm and return

- Confirm: "Saved your feedback to `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`. You can add more anytime by saying \"bootcamp feedback\"."
- Do NOT submit feedback to the Senzing MCP server or anywhere external unless the bootcamper explicitly asks.
- Return the bootcamper to exactly where they left off, resuming the pending step or question. Do not make them re-navigate.
