---
name: graduation
description: 'Bootcamp graduation: generate the recap PDF trophy and a production-ready project. Use when the bootcamper finishes the Core track (Module 7) and accepts the graduation offer, or says "graduate", "run graduation", or "finish the bootcamp".'
---

# Graduation

Graduation turns a completed bootcamp into two things the bootcamper keeps: a
professional **recap PDF trophy** and a clean **`production/` project** they can
build on. Load this skill when the bootcamper accepts the graduation offer at the
end of the Core track, or asks to "graduate" / "run graduation".

Follow `../bootcamp-onboarding/ground-rules.md` throughout: `🛑`/`⛔` are internal
directives (never rendered); one 👉 question ends each yielding turn; keep all
files project-relative; all Markdown goes under `docs/`, all code under `src/`.

Graduation is non-blocking: every artifact step warns-and-continues on failure,
and the recap guarantee at the end always produces a valid PDF. Steps that create
the `production/` project ask for confirmation before large or destructive
actions.

## Graduation banner (show first, exactly once)

Display this banner verbatim as the FIRST output of graduation, before any step.
It bookends the bootcamp: the WELCOME banner marked the start, this marks the
finish. Show it at most once per graduation.

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓🎓🎓  GRADUATION  🎓🎓🎓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

After the banner, surface a one-line best-value nudge (non-blocking — a statement, not a 👉
question, and never a gate): graduation is correctness-critical, so for best value run it on
Opus 4.8 at high effort — `/model opus` then `/effort high` (skip if you are already there or
prefer one model for everything). See `../../docs/model-selection.md`.

## Pre-checks

Gather context before any step. Do this silently.

1. **Read preferences:** load `config/bootcamp_preferences.yaml` and extract `name`, `language`, `track`, `database` (SQLite/PostgreSQL), and `data_sources` if present.
2. **Read progress:** load `config/bootcamp_progress.json` and extract `modules_completed`.
3. **Fallback if files are missing:** tell the bootcamper, then ask for the programming language and database type with one 👉 question at a time; use sensible defaults for the rest (track unknown, data sources none).

## Step 1: Finalize the recap and render the PDF trophy

The recap is the crown-jewel deliverable. Produce it before the `production/`
project so the trophy always exists.

### 1a. Reconcile the recap

Confirm `docs/bootcamp_recap.md` has a `## Module N:` section for every module in
`modules_completed`, each carrying the four labeled subsections (Information
Shared, Questions & Responses, Actions Taken, Journal). If any completed module's
section is missing, append it now from the module's artifacts and progress data,
following `../bootcamp-onboarding/module-completion.md` (append only, never rewrite
existing sections). If `docs/bootcamp_recap.md` does not exist at all, reconstruct
it from `config/bootcamp_progress.json` and the files each module produced.

If an in-progress recap checkpoint remains at `docs/progress/recap_checkpoint.md` (a
module interrupted before completion), fold its content into that module's
`## Module N:` section (append only), then remove the
`<!-- RECAP-CHECKPOINT:START -->` … `<!-- RECAP-CHECKPOINT:END -->` block from
`docs/bootcamp_recap.md` and clear the checkpoint. This ensures the trophy carries any
narrative captured from an interrupted module and the PDF renders clean, completed
sections.

**Normalize the Markdown (once, before rendering).** Now — after reconcile and **before** the
Step 1b render — make a single best-effort CommonMark pass over `docs/*.md`, including
`docs/bootcamp_recap.md`. During the bootcamp these files were written plain (see
`../bootcamp-onboarding/ground-rules.md` → "Markdown files"); this is where they get prettified.
Apply the house rules: blank lines around headings (MD022), fenced blocks (MD031), and lists
(MD032); a language on every fenced block (MD040); and `**Label:**` colon spacing (a space after
the colon, none before). The pass is **purely cosmetic — structure- and content-preserving**: it
must never reorder, remove, or rewrite the prose of a completed `## Module N:` section, nor drop
any of its four subsections (Information Shared, Questions & Responses, Actions Taken, Journal).
Like every graduation step it is non-blocking: if normalization fails or is uncertain, warn,
leave the content as written, and continue — a formatting issue is never a reason to skip the PDF.

### 1b. Render the PDF

Generate `docs/bootcamp_recap.pdf` with the bundled generator. It always produces
a valid PDF (a professionally designed one when `fpdf2` is installed, a plainer
stdlib-rendered one otherwise), so a missing `fpdf2` is never a reason to skip.

Locate and run the bundled script (it ships with this plugin):

```bash
# When invoked via the /graduate command, the plugin root is available:
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/generate_recap_pdf.py"
```

If `${CLAUDE_PLUGIN_ROOT}` is not set in the current context, resolve the script
relative to this skill's directory instead (this skill lives at
`skills/graduation/`, so the generator is two levels up under `scripts/`):

```bash
python3 <this-skill-dir>/../../scripts/generate_recap_pdf.py
```

The script reads `docs/bootcamp_recap.md` and writes `docs/bootcamp_recap.pdf`.

- **Success** is a `PDF generated:` line on stdout with exit 0. Only then tell the bootcamper: "📄 Recap PDF generated at `docs/bootcamp_recap.pdf`." Never claim success without that line.
- **Content check (optional, non-blocking):** run the script with `--check` to confirm every completed module carries the four required subsections. If it reports gaps, backfill per 1a and re-render. A gap never blocks graduation.
- **If the bundled script cannot be located or run:** do not stop. Generate the PDF inline instead: parse `docs/bootcamp_recap.md` and render a cover page plus one page per module (each with Information Shared, Questions & Responses, Actions Taken, Journal) using `fpdf2` if importable, else a minimal valid PDF. The recap Markdown at `docs/bootcamp_recap.md` is always the source of truth, so content is never lost.

## Step 2: Build the production project

If `production/` already exists, ask one 👉 question as a neutral lead plus a
numbered list of the choices — (1) overwrite, (2) merge, (3) abort.
Wait for the answer. On abort, skip to the graduation report noting the abort.

Create `production/` and copy production-relevant files (skip any source that
does not exist; on a copy failure, log and continue):

| Source | Destination | Notes |
|--------|-------------|-------|
| `src/transform/**` | `production/src/transform/` | Mapping/transform code |
| `src/load/**` | `production/src/load/` | Loading code |
| `src/query/**` | `production/src/query/` | Query/discovery code |
| `src/utils/**` | `production/src/utils/` | Shared helpers |
| `data/transformed/**` | `production/data/` | Senzing-ready data |
| `requirements.txt` / `pom.xml` / `Cargo.toml` / `package.json` / `*.csproj` | `production/` | Dependency manifest |

Create `production/database/.gitkeep` as an empty placeholder (never copy the
eval database itself).

**Exclude (never copy):** `config/bootcamp_progress.json`,
`config/bootcamp_preferences.yaml`, `docs/bootcamp_recap.md`, `data/samples/`,
`data/raw/`, `logs/`, `backups/`, and `docs/feedback/`.

Present a short summary of what was copied, what was excluded, and the directories
created, then ask one 👉 question to confirm before generating config files.

## Step 3: Production configuration files

Generate these in `production/`, parameterized by the language and database from
pre-checks. Use placeholder values only, never real secrets:

- **`.env.example`:** `SENZING_ENGINE_CONFIGURATION_JSON`, `SENZING_LICENSE_PATH`, `DATABASE_URL`, `LOG_LEVEL` with safe example values and comments.
- **`docker-compose.yml`:** SQLite (single service + volume mount) or PostgreSQL (app + db service with a health check), per the chosen database.
- **`.gitignore`:** language-appropriate, always including `.env`, `.env.production`, `*.db`, `*.sqlite`, `__pycache__/`, `node_modules/`, `target/`, `bin/`, `obj/`, `build/`, `dist/`, `*.log`.

## Step 4: Production README and migration checklist

- **`production/README.md`:** parameterized by language, database, and data sources. Use no bootcamp language (no "bootcamp", "module", "track", or "bootcamper"). Sections: Project Overview, Prerequisites, Installation, Configuration, Usage, Project Structure. Show it to the bootcamper and apply any requested revisions.
- **`production/MIGRATION_CHECKLIST.md`:** `- [ ]` checkboxes under six sections (Database, Security, Licensing, Performance, Data, Deployment). Because the Core track does not cover Modules 8-11, add a note at the top: "⚠️ Some production topics (performance, security, monitoring, deployment) were not covered during the Core track: complete these items before deploying," and mark those items with ⚠️.

Author every `production/*.md` deliverable — this README, the migration checklist, and the
Step 5 `GRADUATION_REPORT.md` — to the same CommonMark house rules applied to the recap in
Step 1a (MD022/MD031/MD032 blank lines, MD040 fenced-block languages, `**Label:**` colon
spacing), so the handed-over project reads clean. Best-effort and non-blocking, as everywhere in
graduation.

## Step 5: Graduation report

Always generate `production/GRADUATION_REPORT.md`, even if earlier steps had
errors. Include: completion timestamp, track completed, modules finished,
language, database type, a files-generated table, a files-excluded table, and
next steps (fill in secrets, obtain a production license, work through the
checklist, configure CI/CD, test with production data). If any step failed, add a
"⚠️ Issues Encountered" section naming what failed and what was skipped.

## Step 6: Feedback reminder

If `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` exists and contains at
least one real feedback entry, remind the bootcamper it is there and offer to
help them share it (see `../bootcamp-onboarding/feedback.md`). Do not send email
or open issues automatically: wait for explicit confirmation. Otherwise, add one
line: "Say \"bootcamp feedback\" anytime if you'd like to share your experience."

## Mandatory closing step: guaranteed recap and announcement

This runs exactly once, after the report, before graduation is reported finished.

1. **Guarantee the trophy exists.** Confirm `docs/bootcamp_recap.pdf` exists and is non-empty. If it is missing, re-run Step 1b (or the inline fallback) once so a valid PDF exists before you announce it. Never announce an artifact you have not confirmed exists at its path.
2. **Emit one closing announcement** naming only the artifacts confirmed to exist. State that the recap PDF at `docs/bootcamp_recap.pdf` opens with a summary page and then walks through every completed module, capturing that module's Information Shared, Questions & Responses, Actions Taken, and Journal, and that the source lives at `docs/bootcamp_recap.md`. Name the `production/` project and its `GRADUATION_REPORT.md` and `MIGRATION_CHECKLIST.md`. Frame the PDF as a keepsake to revisit and share with their team.

Example (list only what exists):

> 🏆 **Here's your bootcamp trophy.** Your complete recap is at `docs/bootcamp_recap.pdf`: a shareable PDF that opens with a summary and then walks through every module you completed, capturing the Information Shared, Questions & Responses, Actions Taken, and Journal for each. Your production project is ready in `production/`: start with `production/GRADUATION_REPORT.md` and work through `production/MIGRATION_CHECKLIST.md`.

3. **End on the single closing question.** The announcement carries no 👉. After it, end the graduation turn with exactly one 👉 question:

> 👉 **Is there anything else you would like to explore?**

Then stop and wait. This is the single closing question for the whole bootcamp.

4. **Terminal banner — only after the bootcamper declines.** Handle the reply to the closing question:

   - **Wants to keep exploring** (asks a question, names a topic, or otherwise continues): help them, then offer the closing question again when they are ready. Do **not** show the terminal banner yet — it must never pre-empt continued exploration.
   - **Declines** ("no", "I'm done", "that's all", "nothing else"): the bootcamp is complete. Do these two things, in order:
     1. **Stand down the Stop-hook nudge, silently.** Set a top-level `bootcamp_complete: true` key in `config/bootcamp_preferences.yaml` (a single minimal edit; do not narrate it). The `Stop` hook (`../../scripts/stop-nudge.py`) reads this key and will not nudge for a closing 👉 question once the bootcamp is over — so the terminal banner, which ends the turn with no 👉, is not re-opened.
     2. **Render the terminal banner, verbatim, exactly once** as the final output. It bookends the WELCOME banner that opened the bootcamp (start) and the GRADUATION banner (finish) with a clear end-of-bootcamp marker. No 👉 question follows it; the turn simply ends.

     ```text
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     🎓🎓🎓  END OF SENZING BOOTCAMP  🎓🎓🎓
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     ```

     Show this banner at most **once** per bootcamp, and never while exploration is still continuing.
