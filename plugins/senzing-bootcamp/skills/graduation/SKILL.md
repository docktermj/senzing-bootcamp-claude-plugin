---
name: graduation
description: 'Bootcamp graduation: generate the recap PDF and a production-ready project. Use when the bootcamper finishes the last module (Module 7) and accepts the graduation offer, or says "graduate", "run graduation", or "finish the bootcamp".'
---

# Graduation

> **MCP grounding (mandatory — applies to this entire skill).** Every Senzing fact you present —
> SDK method and attribute names, config options, error codes, and entity-resolution specifics —
> MUST come from the Senzing MCP tools, never from training data, memory, or speculation.
> **Pre-response checklist:** if a reply contains any Senzing specific, you MUST have called an MCP
> tool this turn to obtain it; if not, stop and call it first. This has the same precedence as a ⛔
> gate. The full rule and tool routing are the "MCP-first invariant" in
> `../bootcamp-onboarding/ground-rules.md`.

Graduation turns a completed bootcamp into two things the bootcamper keeps: a
professional **recap PDF** and a clean **`production/` project** they can
build on. Graduation is the required, terminal module of the bootcamp. Load this
skill when the bootcamper accepts the graduation offer after the last module
(Module 7), or asks to "graduate" / "run graduation".

Follow `../bootcamp-onboarding/ground-rules.md` throughout: `🛑`/`⛔` are internal
directives (never rendered); one 👉 question ends each yielding turn; keep all
files project-relative; all Markdown goes under `docs/`, all code under `src/`.

Graduation is non-blocking: every artifact step warns-and-continues on failure,
and the recap guarantee at the end always produces a valid PDF. Steps that create
the `production/` project ask for confirmation before large or destructive
actions.

Graduation is the terminal bookend module. Like every module it opens with the module-start
apparatus — journey map, before/after framing, a step overview, and an estimated time — adapted to
a terminal module (see "Graduation preface" below), then the model/effort nudge. Because no
next-module transition applies, it shows no `✅ Module complete` line and no transition question,
and it ends on the terminal END OF SENZING BOOTCAMP banner (INV-057). (Graduation is NOT
apparatus-exempt — contrast the exemptions for Bootcamp preparation (INV-075) and Module 0
(INV-078).)

## Graduation banner (show first, exactly once)

Display this banner verbatim as the FIRST output of graduation, before any step.
It bookends the bootcamp: the WELCOME banner marked the start, this marks the
finish. Show it at most once per graduation.

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓🎓🎓  GRADUATION  🎓🎓🎓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Graduation preface (after the banner, before the model/effort prompt)

Like every module, graduation opens with the module-start apparatus (INV-029–032), adapted to a
terminal module — no next-module transition. Present these in order, right after the banner and
before the model/effort prompt. First read `config/bootcamp_preferences.yaml` (`selected_modules`)
and `config/bootcamp_progress.json` (`modules_completed`) to render the journey map. Honor the
active verbosity preset (INV-011/INV-012): suppress the explanatory parts under `minimal`, keep
them to one line under `concise`. Refer to modules by name, never number (INV-079).

1. **Journey map.** List the selected modules by name, every one marked ✅ (all experienced), with
   **Graduation** marked 🔄 as the current, final stage — nothing ⬜ after it.
2. **Before / After.** Before: every module is complete and your data is resolved, but your work
   still lives in the bootcamp workspace. After: you keep two things — a professional recap PDF
   (`docs/bootcamp_recap.pdf`) and a clean, production-ready `production/` project to build on.
3. **What we'll do.** A brief numbered overview of graduation's steps: (1) normalize the `docs/`
   Markdown and render the recap PDF keepsake, (2) build the `production/` project, (3) create a
   silent revisit/resume bundle — a database backup plus a return guide — so you can come back
   later (INV-094), and (4) close with the END OF SENZING BOOTCAMP banner.
4. **Estimated time.** Give an honest, range-based estimate caveated per INV-096 — e.g.
   "⏱️ Roughly 5–15 minutes, depending on your workstation, the database backup size, and PDF
   rendering speed." If no meaningful estimate is possible, say "hard to estimate" rather than
   inventing a number. Suppress under `minimal`; one line under `concise`.

Graduation is terminal, so it has no "what's next / next module" line and no `✅ Module complete`
transition — it ends on the END OF SENZING BOOTCAMP banner (INV-057). What the bootcamper carries
forward is the recap PDF and the `production/` project.

## Best-value model/effort prompt

After the preface, prompt for the best-value model/effort before the heavier graduation work.
Graduation is correctness-critical (Opus 4.8 + high effort) and steps up from the Module 7
recommendation, so end this turn with a single 👉 yes/no question — its own turn, not combined
with another 👉:

On the **CLI**, pin the switch question verbatim:

> 👉 **Would you like to switch to `/model opus` + `/effort high` for graduation?** (Recommended for best value; reply no to keep your current model.)

On **Desktop / web / IDE** (or an unknown surface), pin the intent-based equivalent (INV-098):

> 👉 **Would you like to switch to Opus 4.8 at high reasoning effort for graduation?** (Recommended for best value; set it with your Claude app's model and effort controls; reply no to keep your current model.)

The switch question ends this turn. On **yes**, preface the reply turn with a one-line statement
telling the bootcamper how to make the change (run the `/model`/`/effort` commands on the CLI, or
use the model and reasoning-effort controls in their Claude app), then end the turn on this pinned
confirmation gate (its question verbatim, INV-056/INV-069 — only the answer hint adapts) — do NOT
start the graduation work yet:

> 👉 **Are you done modifying the model and effort?** (Reply yes once you've set your model and effort; reply no if you need more time.)

Run the Pre-checks and the first graduation step on the turn **after** the bootcamper confirms; if
they need more time, acknowledge and wait, then continue — do not re-ask this gate (ask-once,
INV-006). On **no**, continue straight into the graduation work the same reply turn: run the
Pre-checks and proceed to the first step, ending that turn on its own 👉 question. You never change
the session yourself. See `../../docs/model-selection.md`.

## Pre-checks

Gather context before any step. Do this silently.

1. **Read preferences:** load `config/bootcamp_preferences.yaml` and extract `name`, `language`, `path` (Core/Customized; older sessions may store this as `track`), `selected_modules`, `database` (SQLite/PostgreSQL), and `data_sources` if present.
2. **Read progress:** load `config/bootcamp_progress.json` and extract `modules_completed`.
3. **Fallback if files are missing:** tell the bootcamper, then ask for the programming language and database type with one 👉 question at a time; use sensible defaults for the rest (path unknown, data sources none).

## Step 1: Finalize the recap and render the recap PDF

The recap is the crown-jewel deliverable. Produce it before the `production/`
project so the recap PDF always exists.

A finished-recap sample ships with the plugin at
`${CLAUDE_PLUGIN_ROOT}/docs/examples/bootcamp_recap.example.pdf` (skill-relative
fallback: `../../docs/examples/bootcamp_recap.example.pdf`). You may point the
bootcamper to it so they see what theirs is about to look like — a non-blocking
statement, never a 👉 question or gate, and it adds no turn.

### 1a. Reconcile the recap

Confirm `docs/bootcamp_recap.md` has a name-based `## {Module name}` section for **every** module
in `modules_completed` — match by module **name**, not a catalog number. Iterate the full
`modules_completed` list in its recorded (experienced) order and, for any completed module with no
matching section, append one now from the module's artifacts and progress data, following
`../bootcamp-onboarding/module-completion.md` (append only, never rewrite existing sections, never
re-sort into catalog order). The module flow records each module it completes — including
`entity_resolution_concepts` (Module 0, when it ran — INV-092) and both `system_verification` and
`truthset_visualization` when the Truth Set visualization ran (each self-recording with its own
`modules_completed` entry and recap section, INV-086/INV-087/INV-092) —
so this reconcile is normally a **no-op**; its job is to **recover** a section missing because a
module was interrupted before its completion step ran (e.g. synthesize a missing
`truthset_visualization` section from its artifacts). If `docs/bootcamp_recap.md` does not exist at
all, reconstruct it from `config/bootcamp_progress.json` and the files each module produced.

If an in-progress recap checkpoint remains at `docs/progress/recap_checkpoint.md` (a
module interrupted before completion), fold its content into that module's
`## {Module name}` section (append only), then remove the
`<!-- RECAP-CHECKPOINT:START -->` … `<!-- RECAP-CHECKPOINT:END -->` block from
`docs/bootcamp_recap.md` and clear the checkpoint. This ensures the recap carries any
narrative captured from an interrupted module and the PDF renders clean, completed
sections.

**Backfill orphaned screenshots (before rendering).** Scan `docs/visualizations/*.png`. For any PNG
**not already referenced** by an `![...](...)` image line in `docs/bootcamp_recap.md`, embed it into
the matching `## {Module name}` section's **Actions Taken** — 2-3 best per module. Map each PNG to
its module by the visualization it came from: match the PNG's base name against the `<name>.html`
referenced in a module's recap section (e.g. `truthset_verification-*` → Truth Set visualization;
`multi_source_results-*`/`results_dashboard-*` → the module that produced them; `entity_graph-*`,
`due_diligence_results-*`, or any other `<name>-*` → the module whose section references
`<name>.html`). If a PNG matches no section, place it in the nearest preceding module section. This
is a **safety net** for captures whose embed step was skipped mid-bootcamp
(`../bootcamp-onboarding/module-completion.md` makes the embed a required step, but this guarantees
the recap PDF still shows captured screenshots if one was missed). Append-only and **idempotent** —
never rewrite a completed section's prose (INV-085), never add a reference that already exists, and
skip any image that is missing or unreadable (INV-048). Like every graduation step it is
non-blocking: if it is uncertain, warn and continue — never block the PDF on a screenshot.

**Normalize the Markdown (once, before rendering).** Now — after reconcile and **before** the
Step 1b render — make a single best-effort CommonMark pass over `docs/*.md`, including
`docs/bootcamp_recap.md`. Scope it to top-level `docs/*.md` only: **never recurse into
`docs/feedback/`, and never rewrite, empty, or delete the bootcamper's feedback file**
(`docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` must survive graduation intact — INV-015).
During the bootcamp these files were written plain (see
`../bootcamp-onboarding/ground-rules.md` → "Markdown files"); this is where they get prettified.
Apply the house rules: blank lines around headings (MD022), fenced blocks (MD031), and lists
(MD032); a language on every fenced block (MD040); and `**Label:**` colon spacing (a space after
the colon, none before). The pass is **purely cosmetic — structure- and content-preserving**: it
must never reorder, remove, or rewrite the prose of a completed `## {Module name}` section, nor
drop any of its four subsections (Information Shared, Questions & Responses, Actions Taken, Journal).
Like every graduation step it is non-blocking: if normalization fails or is uncertain, warn,
leave the content as written, and continue — a formatting issue is never a reason to skip the PDF.

### 1b. Render the PDF

Generate `docs/bootcamp_recap.pdf` with the bundled generator. It always produces
a valid PDF (a professionally designed one when `fpdf2` is installed, a plainer
stdlib-rendered one otherwise), so a missing `fpdf2` is never a reason to skip.

**Prefer the professionally designed renderer.** Before rendering, check whether
`fpdf2` is importable (`python3 -c "import fpdf"`). If it is not, offer to install it
so the designed renderer is used (a cover page, a table of contents with page
numbers, color-coded per-module sections, and page footers — INV-048, the recap PDF
should look professional). Install it **robustly**, never with a bare `pip`:

- **Prefer a project-local virtualenv.** This sidesteps PEP 668
  "externally-managed-environment" Python (common on macOS/Homebrew and many Linux
  distros) and never touches the global/system Python:

  ```bash
  python3 -m venv data/temp/recap-venv
  # Linux/macOS:
  data/temp/recap-venv/bin/python -m pip install fpdf2
  # Windows:
  data\temp\recap-venv\Scripts\python -m pip install fpdf2
  ```

  Then run the generator with **that venv's** Python (below) so it imports `fpdf2`.
- **Never call bare `pip`** — a stale shim on PATH may point at a deleted
  interpreter. Always go through an explicit interpreter: `python3 -m pip` (or
  `py -3 -m pip` on Windows). `--user` / `--break-system-packages` are last-resort
  opt-ins only, never the default.
- **Degrade gracefully.** If the bootcamper declines, or venv creation / the install
  fails (offline, no `ensurepip`, etc.), proceed with the stdlib fallback — it still
  produces a valid, complete PDF, so this never blocks graduation.

(Maintainers can visually verify a render by rasterizing pages to PNG — e.g. with
`pymupdf` — to confirm the TOC page numbers and the absence of overlaps or blank
pages; `pymupdf` is a dev-only aid, never required at bootcamper runtime.)

Locate and run the bundled script (it ships with this plugin). Use the venv's Python
if you created one above; otherwise `python3`:

```bash
# fpdf2 already importable, or using the stdlib fallback:
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/generate_recap_pdf.py"
# Or, when you installed fpdf2 into the project-local venv above:
data/temp/recap-venv/bin/python "${CLAUDE_PLUGIN_ROOT}/scripts/generate_recap_pdf.py"
```

If `${CLAUDE_PLUGIN_ROOT}` is not set in the current context, resolve the script
relative to this skill's directory instead (this skill lives at
`skills/graduation/`, so the generator is two levels up under `scripts/`):

```bash
python3 <this-skill-dir>/../../scripts/generate_recap_pdf.py
```

The script reads `docs/bootcamp_recap.md` and writes `docs/bootcamp_recap.pdf`.

- **Success** is a `PDF generated:` line on stdout with exit 0. Only then tell the bootcamper: "📄 Recap PDF generated at `docs/bootcamp_recap.pdf`." Never claim success without that line.
- **Content check (optional, non-blocking):** run the script with `--check --expect-modules "<semicolon-separated display names of the modules reconciled in Step 1a>"` — this confirms each present section carries the four required subsections **and** flags any completed module missing its section entirely. Separate the names with **semicolons**, not commas, since some names contain a comma (e.g. "Query, Visualize and Discover"). (The names are the same ones Step 1a ensured have sections, so pass them directly; whole-module presence is primarily guaranteed by that reconcile.) If it reports gaps, backfill per 1a and re-render. A gap never blocks graduation.
- **If the bundled script cannot be located or run:** do not stop. Generate the PDF inline instead: parse `docs/bootcamp_recap.md` and render a cover page plus one page per module (each with Information Shared, Questions & Responses, Actions Taken, Journal) using `fpdf2` if importable, else a minimal valid PDF. The recap Markdown at `docs/bootcamp_recap.md` is always the source of truth, so content is never lost.

## Step 2: Build the production project

If `production/` already exists, pin this 👉 question verbatim (neutral lead + numbered list):

👉 **`production/` already exists — how should I proceed? Reply with a number:**

1. **Overwrite** — replace the existing `production/` contents.
2. **Merge** — keep existing files and add or update the generated ones.
3. **Abort** — leave `production/` untouched and skip to the graduation report.

Wait for the answer. On abort, skip to the graduation report noting the abort.

Create `production/` and copy production-relevant files (skip any source that
does not exist; on a copy failure, log and continue):

| Source | Destination | Notes |
|--------|-------------|-------|
| `src/transform/**` | `production/src/transform/` | Mapping/transform code |
| `src/load/**` | `production/src/load/` | Loading code |
| `src/query/**` | `production/src/query/` | Query/discovery code |
| `src/utils/**` | `production/src/utils/` | Shared helpers |
| `data/senzing-ready/**` | `production/data/` | Senzing-ready data |
| `requirements.txt` / `pom.xml` / `Cargo.toml` / `package.json` / `*.csproj` | `production/` | Dependency manifest |

Create `production/database/.gitkeep` as an empty placeholder (never copy the
eval database itself).

**Exclude (never copy):** `config/bootcamp_progress.json`,
`config/bootcamp_preferences.yaml`, `docs/bootcamp_recap.md`, `data/samples/`,
`data/raw/`, `logs/`, `backups/`, and `docs/feedback/`.

Present a short, one-line statement of what was copied, what was excluded, and the directories
created, then continue directly to Step 3 — generate the production configuration files
automatically. Do not gate this behind a 👉 question (one fewer low-stakes confirmation).

## Step 3: Production configuration files

Generate these in `production/`, parameterized by the language and database from
pre-checks. Use placeholder values only, never real secrets:

- **`.env.example`:** `SENZING_ENGINE_CONFIGURATION_JSON`, `SENZING_LICENSE_PATH`, `DATABASE_URL`, `LOG_LEVEL` with safe example values and comments.
- **`docker-compose.yml`:** SQLite (single service + volume mount) or PostgreSQL (app + db service with a health check), per the chosen database.
- **`.gitignore`:** language-appropriate, always including `.env`, `.env.production`, `*.db`, `*.sqlite`, `__pycache__/`, `node_modules/`, `target/`, `bin/`, `obj/`, `build/`, `dist/`, `*.log`.

## Step 4: Production README and migration checklist

- **`production/README.md`:** parameterized by language, database, and data sources. Use no bootcamp language (no "bootcamp", "module", "track", or "bootcamper"). Sections: Project Overview, Prerequisites, Installation, Configuration, Usage, Project Structure. Show it to the bootcamper and apply any requested revisions.
- **`production/MIGRATION_CHECKLIST.md`:** `- [ ]` checkboxes under six sections (Database, Security, Licensing, Performance, Data, Deployment). Because the bootcamp does not include dedicated performance/security/monitoring/deployment modules, add a note at the top: "⚠️ Some production topics (performance, security, monitoring, deployment) are not covered in depth during the bootcamp: complete these items before deploying," and mark those items with ⚠️.

Author every `production/*.md` deliverable — this README, the migration checklist, and the
Step 5 `GRADUATION_REPORT.md` — to the same CommonMark house rules applied to the recap in
Step 1a (MD022/MD031/MD032 blank lines, MD040 fenced-block languages, `**Label:**` colon
spacing), so the handed-over project reads clean. Best-effort and non-blocking, as everywhere in
graduation.

## Step 5: Graduation report

Always generate `production/GRADUATION_REPORT.md`, even if earlier steps had
errors. Include: completion timestamp, bootcamp path (Core/Customized) and the modules completed,
language, database type, a files-generated table, a files-excluded table, and
next steps (fill in secrets, obtain a production license, work through the
checklist, configure CI/CD, test with production data). If any step failed, add a
"⚠️ Issues Encountered" section naming what failed and what was skipped.

## Step 6: Save the revisit/resume bundle

Silently preserve everything a returning bootcamper needs to pick the bootcamp back up — so
"graduated" becomes a genuine save point. Like every graduation step this is **non-blocking**
(warn-and-continue on any failure) and administrative in spirit (no narration beyond a short
closing summary). The bundle lives **outside `production/`**, under the reserved top-level
`backups/revisit/` directory, so Step 2's "never copy the eval database into `production/`" rule
is preserved (INV-094).

If `backups/revisit/` already exists from a prior graduation, pin this 👉 question verbatim before
overwriting it (neutral lead + numbered list, INV-051/INV-056); otherwise create it silently:

👉 **A revisit bundle already exists — how should I proceed? Reply with a number:**

1. **Overwrite** — replace the previous revisit bundle.
2. **Keep** — leave the existing bundle untouched and skip this step.

### 6a. Database backup

Back up the resolved repository so it can be restored later. Read `database` (SQLite/PostgreSQL)
from pre-checks and the connection from `config/engine_config.json`.

- **SQLite:** copy the repository file into `backups/revisit/database/` (e.g.
  `cp database/G2C.db backups/revisit/database/G2C.db`).
- **PostgreSQL:** run `pg_dump` of the Senzing database to
  `backups/revisit/database/senzing.dump`. When the database runs in a Docker container, dump
  through the container (e.g.
  `docker exec <container> pg_dump -U <user> -d <db> -Fc > backups/revisit/database/senzing.dump`).
  Confirm the exact user / database / container from `config/engine_config.json` (and the recorded
  container, when container-lifecycle tracking is present); never invent credentials.

Record the exact **restore** command in the return guide (Step 6c): SQLite = copy the file back to
`database/`; PostgreSQL = `pg_restore` (or `psql <` for a plain dump) into a fresh database. If the
backup cannot be produced (tool missing, database unreachable), warn and continue — the rest of the
bundle still saves.

### 6b. RESUME_STATE manifest

Snapshot the resume-critical state into `backups/revisit/state/` (copy each if it exists):
`config/bootcamp_progress.json`, `config/bootcamp_preferences.yaml`, `config/data_sources.yaml`,
`config/engine_config.json`, `config/license.json`, and `docs/mapping/`. Then write
`backups/revisit/RESUME_STATE.json` — a manifest indexing what was saved: the bootcamp path and
`modules_completed`, the programming language and database type, the business problem and data
sources, the relative path of each snapshotted file, the database backup path and its restore
command, the recap PDF (`docs/bootcamp_recap.pdf`), and any visualization snapshots under
`docs/visualizations/`. Use only project-relative paths.

### 6c. Return guide

Write `docs/REVISIT_BOOTCAMP.md` (Markdown under `docs/`, per INV-017), authored to the same
CommonMark house rules as the other graduation deliverables (Step 4). Cover:

- **Quick start when you return** — a short command list at the very top (re-source the env, restore
  the database, re-init the engine, re-run a query and the visualization).
- **What you accomplished** — per completed module, drawn from the recap.
- **Your business problem and data sources** — from `docs/business_problem.md` /
  `config/data_sources.yaml`.
- **Restore the database** — the exact SQLite copy-back or PostgreSQL `pg_restore` / `psql` command
  recorded in Step 6a.
- **Re-initialize and re-run** — how to re-source `src/scripts/senzing-env.sh` (if present) and
  re-init the engine, then re-run the loader, queries, and visualization.
- **License** — where the license lives (`licenses/g2.lic` when custom, else the built-in
  evaluation license) and any expiry.
- **Where things are** — point at `backups/revisit/` (state + database backup), the recap PDF, and
  `docs/visualizations/`.

Then present a one-line summary of what the bundle saved and where, and continue to Step 7.

## Step 7: Feedback reminder

If `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` exists and contains at
least one real feedback entry, remind the bootcamper it is there and offer to
help them share it (see `../bootcamp-onboarding/feedback.md`). Do not send email
or open issues automatically: wait for explicit confirmation. Otherwise, add one
line: "Say \"bootcamp feedback\" anytime if you'd like to share your experience."

## Mandatory closing step: guaranteed recap and announcement

This runs exactly once, after the report, before graduation is reported finished.

1. **Guarantee the recap PDF exists.** Confirm `docs/bootcamp_recap.pdf` exists and is non-empty. If it is missing, re-run Step 1b (or the inline fallback) once so a valid PDF exists before you announce it. Never announce an artifact you have not confirmed exists at its path.
2. **Emit one closing announcement** naming only the artifacts confirmed to exist. State that the recap PDF at `docs/bootcamp_recap.pdf` opens with a summary page and then walks through every completed module, capturing that module's Information Shared, Questions & Responses, Actions Taken, and Journal, and that the source lives at `docs/bootcamp_recap.md`. Name the `production/` project and its `GRADUATION_REPORT.md` and `MIGRATION_CHECKLIST.md`. Frame the PDF as a keepsake to revisit and share with their team.

Example (list only what exists):

> 🎓 **Here's your bootcamp recap.** Your complete recap is at `docs/bootcamp_recap.pdf`: a shareable PDF that opens with a summary and then walks through every module you completed, capturing the Information Shared, Questions & Responses, Actions Taken, and Journal for each. Your production project is ready in `production/`: start with `production/GRADUATION_REPORT.md` and work through `production/MIGRATION_CHECKLIST.md`.

3. **End on the single closing question.** The announcement carries no 👉. After it, end the graduation turn with exactly one 👉 question:

> 👉 **Is there anything else you would like to explore?**

Then stop and wait. This is the single closing question for the whole bootcamp.

4. **Terminal banner — only after the bootcamper declines.** Handle the reply to the closing question:

   - **Wants to keep exploring** (asks a question, names a topic, or otherwise continues): help them, then offer the closing question again when they are ready. Do **not** show the terminal banner yet — it must never pre-empt continued exploration.
   - **Declines** ("no", "I'm done", "that's all", "nothing else"): the bootcamp is complete. Do these two things, in order:
     1. **Stand down the Stop-hook nudge, silently.** Set a top-level `bootcamp_complete: true` key in `config/bootcamp_preferences.yaml` (a single minimal edit; do not narrate it). The `Stop` hook (`../../scripts/stop-nudge.py`) reads this key and will not nudge for a closing 👉 question once the bootcamp is over — so the terminal banner, which ends the turn with no 👉, is not re-opened.
     2. **Render the terminal banner, verbatim, exactly once** as the final output. It bookends the WELCOME banner that opened the bootcamp (start) and the GRADUATION banner (finish) with a clear end-of-bootcamp marker. No 👉 question follows it; the turn simply ends.

     ```text
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     🎓🎓🎓  END OF SENZING BOOTCAMP  🎓🎓🎓
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     ```

     Show this banner at most **once** per bootcamp, and never while exploration is still continuing.
