# Ship a canonical, sanitized example recap PDF as the bootcamper's "this is what yours will look like" reference

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The recap PDF is the crown-jewel trophy (`INV-048`), and the
`recap-pdf-professional-design` work made it look genuinely professional. But there
is no **canonical, shippable example** a bootcamper can look at up front to see what
they will earn, and the renderer has no fixture to regenerate or verify against. The
one sample that exists — `docs/bootcamp_recap.pdf` — is unfit for that role three
ways:

1. **It is not inside the installed plugin.** It lives at repo-root `docs/` (plugin
   *repository* documentation). The installed plugin is `plugins/senzing-bootcamp/`,
   so the guide cannot reliably point a bootcamper at the file at runtime.
2. **Its source `.md` is not committed anywhere**, so it cannot be regenerated and
   will silently drift from the renderer as the generator evolves.
3. **It contains real PII** — the maintainer's name ("Michael"), email
   (`michael@senzing.com`), local Homebrew paths, and a specific real scenario
   (pages 1 and 5) — which is inappropriate to bundle as a shipped example
   (`INV-004`, production-ready).

The "use it as an example" intent already exists informally — `README.md:90` links
it ("e.g. [bootcamp_recap.pdf], but yours will differ") via a raw-GitHub URL at
`README.md:102` — but it is unformalized and points at the PII-bearing file.

## Root cause

There was never a bundled example artifact or fixture; the sample is a by-product of
a real run, not a maintained asset. Confirmed in code:

- `docs/bootcamp_recap.pdf` (30 KB) is the only recap sample in the repo; nothing
  under `plugins/senzing-bootcamp/` bundles one. `plugins/senzing-bootcamp/docs/`
  contains only `model-selection.md`.
- No `docs/bootcamp_recap.md` source exists (verified — the `.md` the sample was
  rendered from is not committed).
- `scripts/generate_recap_pdf.py` reads `docs/bootcamp_recap.md` and writes
  `docs/bootcamp_recap.pdf` (`main()` `:754-786`) and already supports
  `--input`/`--output`/`--check` (`:756-762`) — so it can render from and validate an
  arbitrary fixture — but ships no example input.
- The PII is visible in the sample itself (Module 2 page 5: `michael@senzing.com`).
- `README.md:102` — `[bootcamp_recap.pdf]:` raw URL targets the repo-root PII file.
- No plugin step shows or points to an example: onboarding gives a text overview
  (`onboarding-flow.md:99-112`) and graduation announces the freshly rendered trophy
  (`graduation/SKILL.md:196`), but neither references a sample of the finished PDF.
- **The bundled generator does not produce the admired design.** The committed
  `docs/bootcamp_recap.pdf` was rendered by the earlier project-local
  `generate_recap_pdf_v2.py`; only the redesign's TOC/footer/blank-page fixes were
  ported back into the bundled `generate_recap_pdf.py` (per
  `recap-pdf-professional-design`), **not** the cover/module redesign. The bundled
  `_render_cover` (`:334-392`) renders a single-column "Bootcamp Summary" card
  (`:373`) and a plain "Modules completed: …" line (`:392`) — no SZ badge, no
  two-column labeled metadata, no "Modules in this recap" chips — and
  `_render_subsection` (`:455-472`) has no colored per-section accent tabs, and module
  dates render only in ISO form. So "regenerate the example from the bundled
  generator" would produce a plainer PDF than the admired one. (Discovered during
  implementation; direction confirmed with the maintainer: **upgrade the generator
  first**, then generate the example from it.)

## Proposed change

Adopt a **sanitized canonical example** (source `.md` + rendered PDF) that ships
inside the plugin, doubles as the renderer's regeneration fixture / design target,
and is surfaced to the bootcamper at three touchpoints. (Approach chosen with the
maintainer: sanitized real run; surfaced at onboarding + graduation + README;
**upgrade the generator first** so the example — and every bootcamper's recap —
matches the admired design.)

0. **Upgrade the bundled fpdf2 renderer to the admired design (prerequisite).** Port
   the polish that the committed sample has but the bundled generator lacks, into
   `render_with_fpdf2` so `generate_recap_pdf.py` itself produces the admired look —
   which every bootcamper then gets, and which the example regenerates to:
   - **Cover** (`_render_cover`): an "SZ" circular badge in the navy band, a
     two-column labeled metadata card (uppercase labels over values, driven by the
     recap's `**Key**: value` meta rows), and a "Modules in this recap" chip row
     (one chip per module: "N. Title") — replacing the single-column "Bootcamp
     Summary" card and the "Modules completed: …" line.
   - **Module sections** (`_render_subsection`): a colored per-section accent tab and
     matching heading color — Information Shared (blue), Questions & Responses (gold),
     Actions Taken (green), Journal (navy).
   - **Dates:** format an ISO `YYYY-MM-DD` module date to long form
     ("July 16, 2026") in the module header.
   - Keep the stdlib fallback valid but plain (unchanged), the `_safe()` Latin-1
     sanitizer, the two-pass TOC, and the `footer()` page numbers intact
     (`INV-048`/`INV-052`). Verify visually by rendering (fpdf2 is a dev dependency
     here) and inspecting the output.

1. **Create the sanitized example, inside the plugin.**
   - Reconstruct the recap source as
     `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md`, derived from
     the current real recap but **scrubbed of PII**: fictional bootcamper name, no
     email, a representative fictional business scenario, no machine-local paths —
     while keeping the realistic depth and the four labeled subsections (Information
     Shared, Questions & Responses, Actions Taken, Journal) for every module.
   - Render `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf` from
     it with the bundled generator:
     `python3 scripts/generate_recap_pdf.py --input plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md --output plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf`.
   - The `.example.` infix keeps it unambiguously distinct from a bootcamper's own
     `docs/bootcamp_recap.{md,pdf}` (`INV-050`), so there is no collision or
     confusion. The `.md` lives under a `docs/` path (`INV-017`).

2. **Use the example `.md` as the renderer's regeneration fixture and
   design/regression target.** It is the canonical input a maintainer regenerates the
   example PDF from whenever the renderer changes, keeping the shipped example in
   lockstep (no drift — the current sample's core failing). `generate_recap_pdf.py
   --check --input <example.md>` validates it carries the four subsections per module.
   The `INV-048` "iterate to make it professional" visual loop (render-to-PNG, from
   `recap-pdf-professional-design`) runs against this fixture. Record the one-line
   regenerate command as a short maintainer note (e.g. alongside the example or in the
   scripts area) so regeneration is discoverable.

3. **Surface the example to the bootcamper — always non-blocking, never a 👉 question
   or gate.**
   - **Onboarding motivation:** add one bullet to the overview in
     `onboarding-flow.md` §4 (`:99-112`) pointing to the example trophy so the
     bootcamper sees what they will finish with. A statement only — it must not add a
     question, reorder the preface, or alter any pinned gate wording
     (`INV-019`–`INV-027`, `INV-056`).
   - **Graduation preview:** in `graduation/SKILL.md`, near Step 1 (before rendering
     the bootcamper's own), add a one-line non-blocking pointer ("your recap will look
     like this example: `<path>`"). No gate, no extra turn (respects the closing
     `INV-063`/`INV-064` flow — it is a statement inside an existing turn).
   - **README:** update the `README.md:102` reference definition to the sanitized
     bundled example, and **remove the PII-bearing repo-root `docs/bootcamp_recap.pdf`**
     (`INV-004`). Keep the `README.md:90` "but yours will differ" wording.
   - The guide cannot render a PDF inline in chat, so every touchpoint **points to a
     path**, resolved via `${CLAUDE_PLUGIN_ROOT}/docs/examples/bootcamp_recap.example.pdf`
     with a skill-relative fallback (the same resolution `graduation/SKILL.md:108-121`
     already uses for the generator). Nothing may assume the repo-root path.

The example is inherently one track/language (the sample is Java, Core Bootcamp); it
is illustrative, not prescriptive — "yours will differ" already frames this and the
plugin stays language-agnostic (`INV-002`).

## Acceptance criteria

- [ ] The bundled `generate_recap_pdf.py` fpdf2 renderer produces the admired design: an SZ badge cover with two-column labeled metadata and per-module chips, colored per-section accent tabs (Information Shared/Questions & Responses/Actions Taken/Journal), and long-form module dates — while the stdlib fallback stays valid, and the two-pass TOC, `footer()` page numbers, and `_safe()` sanitizer remain intact.
- [ ] A sanitized example ships in the plugin at `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` and `bootcamp_recap.example.pdf`, containing no real PII (no real name, no email, no machine-local paths).
- [ ] The example PDF is regenerable from the `.md` with `generate_recap_pdf.py --input … --output …`, and `generate_recap_pdf.py --check --input <example.md>` passes (four subsections for every module).
- [ ] Onboarding surfaces a non-blocking pointer to the example trophy in the overview, adding no 👉 question and leaving the preface order and pinned gate wording unchanged (`INV-019`–`INV-027`, `INV-056`).
- [ ] Graduation surfaces a non-blocking pointer to the example near/before rendering the bootcamper's own recap, adding no gate and no extra turn.
- [ ] `README.md` links the sanitized bundled example (`:102` updated) and the PII-bearing repo-root `docs/bootcamp_recap.pdf` is removed; the "but yours will differ" wording is retained.
- [ ] All runtime references resolve via `${CLAUDE_PLUGIN_ROOT}` with a skill-relative fallback; nothing assumes the repo-root path.
- [ ] The render path stays python3-only with `fpdf2` optional and the stdlib fallback intact (`INV-052`), and the change holds on Linux, macOS, and Windows and keeps the plugin language-agnostic (per @INVARIANTS.md). (The example's own content being one language is illustrative and does not violate this.)

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — upgrade `render_with_fpdf2` to the admired design (SZ-badge cover, two-column metadata, module chips, colored section tabs, long-form dates); stdlib fallback and TOC/footer/sanitizer unchanged.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` — **new**; sanitized canonical source and regeneration fixture.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf` — **new**; rendered from the fixture with the bundled generator.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — §4 overview: add the non-blocking example-trophy pointer.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1 area: add the non-blocking example pointer; resolve via `${CLAUDE_PLUGIN_ROOT}` with skill-relative fallback.
- `README.md` — update the `[bootcamp_recap.pdf]:` reference (`:102`) to the sanitized bundled example; keep `:90` wording.
- `docs/bootcamp_recap.pdf` — **removed** (contains PII; replaced as the reference by the sanitized bundled example).
- A short maintainer regenerate note (location maintainer's choice) — records the `--input/--output` command that keeps the example in sync with the renderer.

## Source

- Maintainer request (2026-07-16): improve the creation of `bootcamp_recap.pdf` and use the existing sample as a canonical example of a bootcamper's personal recap.
- Decisions (clarified 2026-07-16): (1) source = **sanitized real run** (ship `.md` + regenerated PDF); (2) surface at **onboarding + graduation + README**; (3) **upgrade the bundled generator first** to the admired design so the example and every bootcamper's recap match it.
- Priority: Medium.
- Related specs: `recap-pdf-professional-design.md` (the renderer that produces this look; this adds a fixture/design target for it), `recap-durability.md` (recap content/checkpoint), `defer-commonmark-to-graduation.md` (Markdown normalization before render). Upholds `INV-048`; enforces `INV-004` (PII removal).

## Invariants introduced

- `INV-065` — A sanitized, non-PII example recap MUST ship inside the plugin — a source `.md` fixture at `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` and its rendered `bootcamp_recap.example.pdf` — the PDF MUST remain regenerable from the `.md` via `generate_recap_pdf.py`, and neither MUST contain real personal data. (Complements `INV-048`; hardens `INV-004` for shipped example assets.) (Recorded in `specs/INVARIANTS.md`, 2026-07-17.)
