# Module Completion (run at the end of every module)

Every module skill runs this process at its end, immediately **before** its
transition 👉 question. It does three things, in this fixed order:

1. Update progress state.
2. Append this module's recap section to `docs/bootcamp_recap.md` (the trophy
   the bootcamper keeps).
3. Present the end-of-module summary to the bootcamper.

Then the module asks its single transition question. Follow `ground-rules.md`
throughout: `🛑`/`⛔` are internal, never rendered; one 👉 question ends the turn.

This is the Claude-plugin port of the Kiro `module-completion*` / `module-completion-artifacts` steering. It is deliberately lightweight and non-blocking. If any write fails, name what failed, do not claim the module is complete, and let the bootcamper decide how to proceed.

## Step 1: Update progress state

In `config/bootcamp_progress.json`, apply all of the following as a **single** batched write (one
diff, not one write per field), done quietly (INV-012 — see `ground-rules.md`):

- Add this module's number to `modules_completed` (idempotent: do not duplicate).
- Set `current_module` to the next module in `selected_modules` (or leave it on this module if the bootcamper has not yet chosen to advance).
- Set top-level `current_step` to `null`.
- Under `step_history["<module>"]`, set `{ "last_completed_step": "<final step>", "updated_at": "<ISO 8601>" }`.

## Step 2: Append the recap section

The recap is the single accumulating record that becomes the graduation PDF
trophy. Append one section per completed module. Do **not** rewrite existing
sections: append only.

### 2a. Create the recap on first module completion

If `docs/bootcamp_recap.md` does not exist, create `docs/` and write this header
(read `name` from `config/bootcamp_preferences.yaml`; default to `Bootcamper`;
also include the chosen programming language and path (Core/Customized) when present):

```markdown
# Senzing Bootcamp Recap

**Bootcamper:** {name}
**Started:** {ISO 8601 timestamp with timezone offset}
**Programming language:** {language}
**Path:** {path}

---
```

### 2b. Append this module's section

Append the section below at the end of the file. Use the module number and name
(names come from the module skills / `../bootcamp-onboarding/onboarding-flow.md`
overview). Gather the content from what actually happened in this module, from
the bootcamper's point of view:

```markdown
## Module N: {Name} — {ISO 8601 timestamp}

### Information Shared
- {key concepts, explanations, and reference material presented this module}

### Questions & Responses
- **Q:** {question you asked}
    - **R:** {the bootcamper's answer}

### Actions Taken
- {files created or modified, code generated, commands run, decisions made}

### Journal
**What we did:** {1-2 sentence summary of what was accomplished}
**What was produced:** {comma-separated artifact paths created or modified}
**Why it matters:** {how this module enables the modules that follow}
**Bootcamper's takeaway:** {the bootcamper's stated takeaway, or N/A}

---
```

Rules for the four subsections (all four must be present for every module: the
graduation PDF renders exactly these four labeled sections per module):

- **Information Shared** and **Actions Taken** carry real content from this module, never placeholders.
- **Questions & Responses:** each substantive 👉 question you asked this module, paired with the bootcamper's actual answer, in ask order. If a module asked no substantive questions, write `- {none this module}`.
- **Journal:** the four bold fields exactly as shown.

Append the section as plain, functional Markdown. Do not spend effort on CommonMark
prettification here (blank-line rules, `**Label:**` colon spacing, fence info strings):
graduation runs one normalization pass over the recap before the PDF renders (see
`ground-rules.md` → "Markdown files" and `../graduation/SKILL.md`). What matters at this step is
that the `## Module N:` heading and all four subsections are present and carry real content.

### 2c. Verify it landed

Re-read `docs/bootcamp_recap.md` and confirm a `## Module N:` heading for the
just-completed module is present. If it is missing (a lost write or session
boundary), append it again before continuing. Only then display the one-line
confirmation: `Recap updated for Module N: {Name}.`

(The recap PDF is not rendered per-module: it is rendered once at graduation by
`scripts/generate_recap_pdf.py`, which reads this file. See `../graduation/SKILL.md`.)

### 2d. Finalize the in-progress checkpoint

During the module you kept an in-progress recap at `docs/progress/recap_checkpoint.md`
(see `ground-rules.md` → "Progress and state"), and the plugin's durability hooks may
have folded it into `docs/bootcamp_recap.md` as a `<!-- RECAP-CHECKPOINT:START -->` …
`<!-- RECAP-CHECKPOINT:END -->` block. Now that the finalized `## Module N:` section is
appended (2b), that block is superseded. Do two things:

- Remove any `<!-- RECAP-CHECKPOINT:START -->` … `<!-- RECAP-CHECKPOINT:END -->` block
  from `docs/bootcamp_recap.md` (the finalized section replaces it — this keeps the
  trophy clean and never rewrites a completed `## Module N:` section).
- Clear `docs/progress/recap_checkpoint.md` (empty the file or delete it) so the next
  module starts a fresh checkpoint.

## Step 3: End-of-module summary (shown to the bootcamper)

Present a short, skimmable summary from the bootcamper's point of view. This is a
required outcome of every module. **Lead with the lightly-highlighted completion line** — a bold
line wrapped in a thin rule of `─` characters above and below (more visible than plain prose,
lighter than the module-start banner's `━━━`/emoji triplet) — then the summary details. Render the
completion line as shown (bold, no module number), the rest as a plain summary:

─────────────────────────────────────────────
**✅ Module complete: {Module name}**
─────────────────────────────────────────────

```text
What you accomplished:
- {plain-language accomplishment 1}
- {accomplishment 2}

Files produced:
- `{path}` — {what it is}
- `{path}` — {what it is}

Why it matters:
{1-2 sentences tying this module's output to the bootcamper's goal.}

What's next:
Next: {next module name in your selected sequence} — {one line on what it does}.
```

If the module produced no new files (rare), say so plainly rather than inventing
paths. Keep the list to what the bootcamper cares about; suppress internal
bookkeeping.

## Step 4: Transition question

Return to the module and ask its single transition 👉 question — "Are you ready to move on to the
next module: {next module name}?" (fill {next module name} with the next module in
`selected_modules`; after the last content module, use the graduation offer below instead). That
question ends the turn. Do not combine it with the
summary content above into multiple questions: the summary is statements, the
transition is the one 👉 question.

## Reaching graduation (after the last content module)

When the module just completed is the **last content module before Graduation in
`selected_modules`** — always **Query, Visualize and Discover** (Module 7), which is
required in every path — do Steps 1-3 as usual, then, instead of a next-module
transition, offer graduation (the mandatory terminal module):

👉 **Would you like to graduate now and generate your production project and recap trophy?**

On an affirmative reply, invoke the `graduation` skill. If the bootcamper wants to
keep exploring first, stay available and offer graduation again whenever they are
ready. Graduation is the required close-out module; its production project and
migration checklist deliver the production-hardening guidance (performance,
security, monitoring, deployment) for every bootcamper.
