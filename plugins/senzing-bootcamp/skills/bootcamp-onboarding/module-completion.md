# Module Completion (run at the end of every module)

Every module skill runs this process at its end, immediately **before** its
transition 👉 question. It does three things, in this fixed order:

1. Update progress state.
2. Append this module's recap section to `docs/bootcamp_recap.md` (the recap
   the bootcamper keeps).
3. Present the end-of-module summary to the bootcamper.

Then the module asks its single transition question. Follow `ground-rules.md`
throughout: `🛑`/`⛔` are internal, never rendered; one 👉 question ends the turn.

This is the Claude-plugin port of the Kiro `module-completion*` / `module-completion-artifacts` steering. It is deliberately lightweight and non-blocking. If any write fails, name what failed, do not claim the module is complete, and let the bootcamper decide how to proceed.

## Step 1: Update progress state

In `config/bootcamp_progress.json`, apply all of the following as a **single** batched write (one
diff, not one write per field), done quietly (INV-012 — see `ground-rules.md`):

- Add this module's **name token** (e.g. `system_verification`, `truthset_visualization`, `data_collection`) to `modules_completed` — never a catalog number, so graduation's name-based reconcile matches (INV-085). Idempotent: do not duplicate. Each module records its own single name token at its own close — System verification and the separate Truth Set visualization module each record themselves (INV-086/INV-087).
- Set `current_module` to the next module in `selected_modules` (or leave it on this module if the bootcamper has not yet chosen to advance).
- Set top-level `current_step` to `null`.
- Under `step_history["<module>"]`, set `{ "last_completed_step": "<final step>", "updated_at": "<ISO 8601>" }`.

## Step 2: Append the recap section

The recap is the single accumulating record that becomes the graduation recap
PDF. Append one section per completed module. Do **not** rewrite existing
sections: append only.

### 2a. Create the recap on first module completion

If `docs/bootcamp_recap.md` does not exist, create `docs/` and write this header
(read `name` from `config/bootcamp_preferences.yaml`; default to `Bootcamper`;
the plugin version from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`, or "Unknown"; and
also include the chosen programming language and path (Core/Customized) when present):

```markdown
# Senzing Bootcamp Recap

**Bootcamper:** {name}
**Started:** {ISO 8601 timestamp with timezone offset}
**Programming language:** {language}
**Path:** {path}
**Plugin version:** {plugin version}

---
```

The **Run environment** provenance lines (operating system + architecture, Python version,
language runtime, Senzing SDK, database) are added to this header at graduation, where they are
current — see `../graduation/SKILL.md`. They are recorded in the recap only, never shown in the
bootcamp output (INV-012).

### 2b. Append this module's section

Append the section below at the end of the file, in module-completion order — the order the
bootcamper actually experienced the modules; never re-sort by catalog number. Use the module
**name** (from the module skills / `../bootcamp-onboarding/onboarding-flow.md` overview), not a
catalog number. Gather the content from what actually happened in this module, from the
bootcamper's point of view:

```markdown
## {Name} — {ISO 8601 timestamp}

### Information Shared
- {key concepts, explanations, and reference material presented this module}

### Questions & Responses
- **Q:** {question you asked}
    - **R:** {the bootcamper's answer}

### Actions Taken
- {files created or modified, code generated, commands run, decisions made}

### End-of-Module Summary
**What you accomplished:**
- {plain-language accomplishment 1}
- {accomplishment 2}

**Files produced:**
- `{path}` — {what it is}

**Why it matters:** {1-2 sentences tying this module's output to the bootcamper's goal}
**Bootcamper's takeaway:** {the bootcamper's stated takeaway — omit this whole line if the bootcamper gave no takeaway; never write "N/A"}

---
```

Rules for the four subsections (all four must be present for every module: the
graduation PDF renders exactly these four labeled sections per module):

- **Information Shared** and **Actions Taken** carry real content from this module, never placeholders.
- **Questions & Responses:** each substantive 👉 question you asked this module, paired with the bootcamper's actual answer, in ask order. If a module asked no substantive questions, write `- {none this module}`.
- **End-of-Module Summary:** the same What you accomplished / Files produced / Why it matters shown in the bootcamper-facing epilog (Step 3), persisted here as the permanent keepsake record (this subsection replaced the former Journal — INV-103); the **Bootcamper's takeaway** line is optional — include it only when the bootcamper gave a genuine takeaway, otherwise omit the line entirely (never write "N/A").
- **Visualization screenshots:** when this module produced a visualization, capture is best-effort (see "Capturing visualization screenshots" below) — but **when a capture succeeds, embedding the 2-3 curated screenshots is required**, not optional: add them to this module's **Actions Taken** as Markdown images — `![caption](docs/visualizations/<name>.png)` — in the same turn the capture ran. The graduation PDF embeds local images and silently skips any that are missing (INV-048), so an absent screenshot never breaks the recap PDF, and graduation backfills any capture whose embed was missed.

⛔ **Whenever a module step produces a bootcamper-facing artifact — a PDF, a PNG, an HTML
visualization — verify the artifact itself, not the exit code.** A zero exit, a written file, and a
self-reported metric are all necessary and none is sufficient: a capture helper exited 0 having
written three images of the same tab; a generator reported "content retained: 98%" with an entire
table drawn off the page. Neither raised an error.

So open it: view the PNG, rasterize the PDF page, grep the extracted text for a distinctive string you
know must be there, load the HTML and confirm the tab renders. Describe the artifact from what it
actually shows, never from what the step was supposed to produce (INV-115's principle, applied to
artifacts rather than parsed fields). This is best-effort and never blocks a module — if the tool to
inspect it is absent, say the artifact could not be verified rather than implying it was.

Append the section as plain, functional Markdown. Do not spend effort on CommonMark
prettification here (blank-line rules, `**Label:**` colon spacing, fence info strings):
graduation runs one normalization pass over the recap before the PDF renders (see
`ground-rules.md` → "Markdown files" and `../graduation/SKILL.md`). What matters at this step is
that the `## {Name}` heading (name-based, no catalog number) and all four subsections are present and carry real content.

### 2c. Verify it landed

Re-read `docs/bootcamp_recap.md` and confirm a `## {Name}` heading for the
just-completed module is present. If it is missing (a lost write or session
boundary), append it again before continuing. Only then display the one-line
confirmation: `Recap updated: {Name}.`

(The recap PDF is not rendered per-module: it is rendered once at graduation by
`scripts/generate_recap_pdf.py`, which reads this file. See `../graduation/SKILL.md`.)

### 2d. Finalize the in-progress checkpoint

During the module you kept an in-progress recap at `docs/progress/recap_checkpoint.md`
(see `ground-rules.md` → "Progress and state"), and the plugin's durability hooks may
have folded it into `docs/bootcamp_recap.md` as a `<!-- RECAP-CHECKPOINT:START -->` …
`<!-- RECAP-CHECKPOINT:END -->` block. Now that the finalized `## {Name}` section is
appended (2b), that block is superseded. Do two things:

- Remove any `<!-- RECAP-CHECKPOINT:START -->` … `<!-- RECAP-CHECKPOINT:END -->` block
  from `docs/bootcamp_recap.md` (the finalized section replaces it — this keeps the
  recap clean and never rewrites a completed `## {Name}` section).
- Clear `docs/progress/recap_checkpoint.md` (empty the file or delete it) so the next
  module starts a fresh checkpoint.

## Capturing visualization screenshots (optional)

Whenever a module generates a visualization (an HTML page under `docs/visualizations/`), capture a
few screenshots of it so the recap shows what the bootcamper actually built, not just a
link. This runs at the visualization step, right after the page exists, and is **non-blocking with
graceful degradation** — never a 👉 question, and never a reason to stall.

The app is a **tabbed** artifact, so capture is **one image per tab** — never several shots of one
tab. Procedure (parameterized by the visualization's `{html}` file or live `{url}`, and a short
`{name}`):

1. Run the bundled helper. Prefer the **live app's `localhost` URL** while the server is still up,
   because that is the only way the Search / Probe tab can show real results; fall back to the
   standalone snapshot file when the server is already down:

   ```bash
   # live app (preferred while it is running)
   python3 <helper> --url http://localhost:{port} --out-dir docs/visualizations \
       --name {name} --tabs graph,stats,matchkeys,features,overlap,probe --query "{a name in the data}"

   # standalone snapshot (no server needed)
   python3 <helper> --html docs/visualizations/{html} --out-dir docs/visualizations \
       --name {name} --tabs graph,stats,matchkeys,features,overlap,probe
   ```

   Resolve `<helper>` as `${CLAUDE_PLUGIN_ROOT}/scripts/capture_screenshots.py` (command/hook
   context) or `../../scripts/capture_screenshots.py` relative to a module skill. It tries several
   headless backends (Playwright, Selenium, headless Chrome/Chromium, `wkhtmltoimage`) and never
   fetches a remote URL (offline — INV-091). Pass only tabs the app actually shows for this data —
   the helper reports any tab that produced no image on stderr rather than dropping it silently.
2. **If it exits non-zero** (exit 2 = no headless capability available): skip screenshots silently,
   keep the visualization's HTML link in the recap, and continue. Honor verbosity (say nothing at
   the `minimal` preset).
3. **If it succeeds** it prints one `<png path>⇥<tab label>` line per capture, and each file is
   named `{name}-<tab-slug>.png`. **Keep every captured tab** — and, **as a required step, in the
   same turn** — embed them all in **this module's recap `Actions Taken`** as
   `![caption](docs/visualizations/{name}-<tab-slug>.png)`. Writing the image lines is not
   optional once a capture succeeded; record it at the step checkpoint. The graduation PDF embeds
   these local images and skips any that are missing (INV-048), and graduation backfills any that
   were captured but never embedded (see `../graduation/SKILL.md` Step 1).

   ⛔ **Do not prune to a "best" few.** Capture is one image per tab (INV-122), so every file is
   already a distinct view — there is nothing redundant to remove, and a count cap can only delete
   unique content. Delete only a true duplicate: two images of the *same* tab, which per-tab capture
   should not produce. Judging which shots are worth keeping is what previously dropped Merge
   Statistics, Match Keys and Feature Scores from a six-tab app — the three *analytical* tabs, since
   any such judgement pulls toward the most visually striking. The recap then showed the same three
   tabs in both visualization sections and the app looked narrower than it was.

   ⛔ **Embed in the app's tab order, never in capture or append order.** The order is the row order
   of the tab table in
   `../module-03b-truthset-visualization/visualization-api-reference.md` → "Tab identifiers and
   deep-linking" — read it there rather than restating the list, so a tab change updates one file.
   A tab that produced no image is simply skipped; the rest keep their relative order. The recap is
   a walkthrough of the app, so a reader must be able to line the images up against the interface
   left to right.

⛔ **Every caption is derived from the capture, never from the plan.** Build it from the tab label
the helper printed (which matches the filename slug), and — before writing it — **open the image and
confirm it shows that tab**. Describe only what is visible in it.

A caption asserting content the image does not contain is a defect of the same class INV-115
forbids: it renders the unverified as verified, in a permanent artifact the bootcamper is
encouraged to share. It has happened — captions reading "Cross-source overlap and match-key
frequency tabs" and "Search/Probe with a verified example query chip" were written for two images
that both showed the Entity Graph, because the app *is* tabbed so the captures were assumed to be
tab-diverse. Never infer image content from the visualization contract.

If the Search / Probe tab was captured from the **static snapshot** rather than the live server, its
search box is inert (the snapshot has no engine), so caption it explicitly as the empty/inactive
state or omit it — never imply a result set that was not captured.

## Step 3: End-of-module summary (shown to the bootcamper)

Present a short, skimmable summary from the bootcamper's point of view. This is a
required outcome of every module (INV-032) — one completion line and one four-part summary per
module, at that module's own close. **Lead with the lightly-highlighted completion line** — a bold
line wrapped in a thin rule of `─` characters above and below (more visible than plain prose,
lighter than the module-start banner's `━━━`/emoji triplet) — then the summary details. Render the
completion line as shown (bold, no module number), the rest as a plain summary:

──────────────────────────────────────────
**✅ Module complete: {Module name}**
──────────────────────────────────────────

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

This same What you accomplished / Files produced / Why it matters content is persisted into the
recap's **End-of-Module Summary** subsection (Step 2b) — keep the two consistent. "What's next" is
chat-only and is **not** written to the recap.

## Step 4: Transition question

Return to the module and ask its single transition 👉 question — "Are you ready to move on to the
next module: {next module name}?" (fill {next module name} with the next module in
`selected_modules`; after the last content module, use the graduation offer below instead). Ask it
**once**, after the module's summary. That question ends the turn. Do not combine it with the
summary content above into multiple questions: the summary is statements, the transition is the one
👉 question.

## Reaching graduation (after the last content module)

When the module just completed is the **last content module before Graduation in
`selected_modules`** — always **Query, Visualize and Discover** (Module 7), which is
required in every path — do Steps 1-3 as usual, then, instead of a next-module
transition, offer graduation (the mandatory terminal module):

👉 **Would you like to graduate now and generate your production project and recap?**

On an affirmative reply, invoke the `graduation` skill. If the bootcamper wants to
keep exploring first, stay available and offer graduation again whenever they are
ready. Graduation is the required close-out module; its production project and
migration checklist deliver the production-hardening guidance (performance,
security, monitoring, deployment) for every bootcamper.
