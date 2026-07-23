# Show the plugin version at bootcamp start and record version + environment in the recap

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The Senzing Bootcamp Claude Plugin (SBCP) version is not reliably shown to the bootcamper at the
start of the bootcamp, and neither the plugin version nor the workstation's hardware/software
environment is recorded in the keepsake recap (`docs/bootcamp_recap.md` and the generated
`docs/bootcamp_recap.pdf`). This costs provenance/reproducibility: a completed run does not record
which plugin version produced it or the environment it ran in, which are exactly the facts needed to
debug or reproduce a run.

The maintainer asks for two things:

1. Display the plugin version at the beginning of the bootcamp **and** in `docs/bootcamp_recap.md`
   and `docs/bootcamp_recap.pdf`.
2. In the `.md` and `.pdf` only, also capture the hardware and software versions — this environment
   detail need **not** be shown in the live bootcamp output.

## Root cause

By design/omission, not a defect:

- **Bootcamp start — version is optional.**
  `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:33` reads "**Optionally**
  show the plugin version (from `.claude-plugin/plugin.json`): `Senzing Bootcamp vX.Y.Z`." Because it
  is optional, it may never appear.
- **Recap `.md` carries no version/environment.** The recap header is created at
  `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:34` with only
  `Bootcamper` / `Started` / `Completed` / `Programming language` / `Path` (confirmed by the shipped
  fixture `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md:1-8`). No plugin version,
  no environment.
- **Recap PDF renderer has no version/environment field.**
  `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `parse_recap` (`:134`) reads the header
  into `Recap.meta`; `_render_cover` (`:436`) and `_render_certificate` (`:580`, INV-100) render
  meta; neither captures nor renders a plugin version or an environment block.

The building blocks already exist: the plugin version is read from
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` elsewhere (`scripts/feedback-capture.py:47`,
`skills/bootcamp-onboarding/feedback.md:22`), and OS + architecture are already auto-detected and
persisted in `config/bootcamp_preferences.yaml` (INV-061).

**Invariant notes (respect, do not violate):**

- **INV-012** — the environment block is recorded in the recap files only and suppressed from live
  bootcamp output; the version line shown at start is verbosity-aware (INV-011).
- **INV-022** — the version line belongs with the WELCOME preface.
- **INV-048 / INV-100 / INV-103 / INV-066** — the recap PDF must still be created with its four
  required subsections and Certificate of Completion, `--check` must still pass, and both the fpdf2
  and stdlib-fallback renderers must render the new content offline.
- **INV-061** — reuse the already-detected/persisted OS and architecture; do not re-ask (INV-006).
- **INV-080** — the Senzing SDK/engine version comes from the Senzing MCP tools, never guessed.
- **INV-065** — the shipped example recap (`.md` + `.pdf`) must be updated and stay regenerable and
  **PII-free**: the environment block must record OS/arch/software versions only, never a hostname,
  username, IP, or other personal/host identifier.
- **INV-058** — persist any newly gathered values in batched writes, not per sub-step.

## Proposed change

1. **Show the version at bootcamp start (`onboarding-flow.md`).** Replace the "Optionally show" line
   with a standard, verbosity-aware version line presented with the WELCOME preface (INV-022), read
   from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` → `version` (fall back to "Unknown" if
   unreadable). Suppressed under the `minimal` verbosity preset (INV-011/INV-012).
2. **Record version + environment in the recap `.md` header (`module-completion.md` header block,
   and gathered at graduation).** Add to the recap header:
   - `**Plugin version:**` (from the manifest).
   - An **Environment** block (recap-only): OS + architecture (from `config/bootcamp_preferences.yaml`,
     INV-061), Python version, the chosen-language runtime version, the Senzing SDK/engine version
     (via the Senzing MCP tools, INV-080), and the database backend. Gather it at graduation (recap
     assembly) so it is current; write it to the recap `.md` and never to live output (INV-012).
3. **Render both in the recap PDF (`generate_recap_pdf.py`).** Parse the new header fields into
   `meta` and render the plugin version (on the cover and/or certificate) and the environment block
   (a small metadata section, not on the certificate face), in **both** `render_with_fpdf2` and the
   stdlib fallback (INV-066), offline, from `brand_tokens` (INV-081). Keep the four required
   subsections and `--check` intact (INV-048/INV-103) — the environment block is additive metadata,
   not one of the four module subsections.
4. **Update the shipped example (INV-065).** Add a sanitized, PII-free plugin-version line and
   example environment block to `docs/examples/bootcamp_recap.example.md` and regenerate
   `bootcamp_recap.example.pdf`; confirm `--check` still passes.

## Acceptance criteria

- [ ] The plugin version (from `.claude-plugin/plugin.json`) is displayed at the start of the bootcamp with the WELCOME preface, verbosity-aware (suppressed under `minimal`).
- [ ] `docs/bootcamp_recap.md` records the plugin version and an Environment block (OS+arch, Python, chosen-language runtime, Senzing SDK/engine version, database backend).
- [ ] `docs/bootcamp_recap.pdf` renders the plugin version and the environment block in both the fpdf2 and stdlib renderers; `generate_recap_pdf.py --check` still passes and the four required subsections + Certificate of Completion are intact (INV-048/INV-100/INV-103/INV-066).
- [ ] The environment detail is NOT shown in live bootcamp output (INV-012); only the version line is shown at start.
- [ ] OS/architecture are reused from the persisted detection (INV-061), not re-asked; the Senzing SDK/engine version is sourced via the Senzing MCP tools (INV-080), not training data.
- [ ] The shipped example recap `.md`/`.pdf` is updated, remains regenerable, and contains no real PII (INV-065) — the environment block carries no hostname/username/IP.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — make the version line a shown, verbosity-aware part of the WELCOME preface (was "Optionally").
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — add `Plugin version` + Environment block to the recap `.md` header.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — gather the environment (MCP-sourced SDK version; persisted OS/arch; runtime/DB) at recap assembly and ensure it lands in the recap before rendering.
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — parse + render the version and environment metadata in both renderers.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` and `bootcamp_recap.example.pdf` — sanitized example + regenerated PDF (INV-065).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Show the plugin version at bootcamp start and record version + hardware/software environment in the recap" (2026-07-23, Whole-bootcamp onboarding + Graduation recap)
- Priority: Medium
- Related specs: `example-recap-reference.md` / `recap-pdf-professional-design.md` / `landscape-certificate-of-completion.md` (recap PDF), `robust-fpdf2-install.md` (both renderers), `auto-detect-platform.md` (OS/arch detection, INV-061), `enrich-feedback-context.md` (reads the same plugin.json version); INV-012, INV-022, INV-048, INV-061, INV-065, INV-066, INV-080, INV-100, INV-103

## Invariants introduced

- `INV-105` — The bootcamp MUST display the SBCP plugin version at bootcamp start (verbosity-aware) and record the plugin version + a run-environment provenance block (OS+arch, Python, chosen-language runtime, Senzing SDK/engine version, database backend) in `docs/bootcamp_recap.md` and the rendered PDF; the environment block is recap-only (INV-012), reuses persisted OS/arch (INV-061) and the MCP SDK version (INV-080), renders in both PDF renderers (INV-066), and carries no PII (INV-065) (recorded in `specs/INVARIANTS.md`).
