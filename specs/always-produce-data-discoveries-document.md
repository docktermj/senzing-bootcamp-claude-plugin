# Always produce a data-discoveries document, on both branches of the Discover opt-in

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The Discover phase is gated behind an opt-in:

> 👉 **Would you like to explore Senzing's advanced discover capabilities using examples from your own
> data?**

All data-specific insight — why analysis, how analysis, relationship-network exploration — lives inside
that optional phase. A bootcamper who declines (entirely reasonable at the end of a long session)
finishes the bootcamp having seen only aggregate counts, and **never learns what Senzing actually found
in THEIR data.**

The bootcamper asked that, whether they answer yes or no, the plugin explore their data and produce
`docs/bootcamp_data_discoveries.md` and `docs/bootcamp_data_discoveries.pdf`.

Why it matters, in their framing: "The findings are the payoff for every preceding module — collection,
mapping, loading, resolution. Gating them behind an optional tutorial makes the single most valuable
output the easiest one to skip. It also inverts the value ordering: the bootcamper keeps the *programs*
unconditionally but loses the *insight* unless they opt in to more work."

The gap is structural: the plugin conflates **the tutorial** (walking through why/how/networks as a
teaching exercise — legitimately optional) with **the findings** (what Senzing discovered in this
specific dataset — a deliverable that should always be produced).

## Root cause

**Confirmed.** The decline branch produces nothing, and nothing downstream requires a findings artifact.

`phase2-discover.md:39-42`:

> - **Declines:** write `discover_phase: "skipped"` to `config/bootcamp_progress.json` under
>   `module_7_query` and return to `phase1-query-visualize.md` for the Query Completeness Gate.
> - **Agrees:** write `discover_phase: "in_progress"` under `module_7_query` and continue to step 4a.

The decline branch writes one status field and returns. The early-exit branches at
`phase2-discover.md:148-149` and `:203-204` do the same. The Query Completeness Gate it returns to
(`phase1-query-visualize.md:245`) does not require any discoveries artifact to exist.

Confirmed by grep: **no reference to a discoveries document exists anywhere in the plugin** — no
`bootcamp_data_discoveries`, no equivalent artifact under any other name. It was produced in the reported
session only because the bootcamper opted in and the assistant wrote it ad hoc.

The phase was designed as a teaching module rather than as a deliverable-producing step, so its artifacts
inherited the opt-in.

## Proposed change

**Split the tutorial from the deliverable.** Produce `docs/bootcamp_data_discoveries.md` + `.pdf`
unconditionally at the end of Module 7, on **both** branches. The opt-in then governs only whether the
bootcamper is *walked through* the analysis interactively — declining costs them nothing but time.

This follows the principle already established by `specs/drop-deliverable-generation-gates.md`: generate
auto-generated deliverables and announce them rather than gating them behind a yes/no.

**Content the document must carry** (all obtainable without bootcamper interaction, all sourced through
generated SDK code and `reporting_guide` per this module's MCP-grounding rule — never direct SQL against
`database/G2C.db`):

- **Headline resolution numbers with interpretation**, not raw counts alone.
- **Every merge with its match key**, so each is explainable and auditable.
- **The review queue** — cross-source POSSIBLY_SAME / AMBIGUOUS pairs. The bootcamper singles this out as
  the highest-value output for a business, since each is one human decision away from being actioned.
- **Worked why/how examples** from the bootcamper's own entities, including at least one **near-miss**,
  because the reasons things did *not* merge are usually more instructive than the merges.
- **Relationship-network findings** — multi-hop paths no single record states.
- **What was NOT found, and why.** The bootcamper is emphatic about this one, and it is the requirement
  most likely to be dropped: on their dataset the two sources shared only 8 organization names, so 4
  cross-source merges was near the achievable ceiling. A document omitting that context "would read as a
  weak result rather than a correct one." The doc MUST distinguish *"the pipeline underperformed"* from
  *"the data had little overlap to find"*, state which applies, and show the measurement behind it.

**PDF generation — reuse, do not reinvent.** Graduation already ships a generator for
`docs/bootcamp_recap.pdf` that uses `fpdf2` when importable and falls back to a stdlib renderer, so a
missing `fpdf2` is never a reason to skip (`graduation/SKILL.md`, Step 1b). The reporter verified that
none of `pandoc`, `wkhtmltopdf`, `weasyprint`, `reportlab`, or `fpdf2` was installed on their
workstation — **the fallback path is the common case, not an edge case.**

⚠️ **`scripts/generate_recap_pdf.py` cannot be pointed at this document as-is.** It parses recap-shaped
`## {Module name}` sections and renders only the four recap subsections; aimed at a discoveries document
it printed warnings and then `PDF generated: … (renderer: stdlib)` with **exit 0** and essentially no
content (`generate_recap_pdf.py:1238-1248`). Either generalize the generator or give the discoveries
document its own renderer — and in either case land
`specs/recap-pdf-generator-fail-loudly-on-content-loss.md` first or alongside, or this deliverable ships
empty and silently. That spec is a hard prerequisite, not a nicety.

**Announce it.** List both files in the module's end-of-module summary "Files produced" (INV-032) and in
the recap section, so their existence is discoverable rather than incidental.

**Keep it non-blocking.** A failure to produce the discoveries document must not block the Query
Completeness Gate or graduation — report what failed and continue, consistent with the guarded-generation
pattern used elsewhere (e.g. INV-077).

## Acceptance criteria

- [ ] `docs/bootcamp_data_discoveries.md` is produced whether the bootcamper accepts **or** declines the
      Discover opt-in, and on every early-exit branch (`phase2-discover.md:39, 148, 203`).
- [ ] `docs/bootcamp_data_discoveries.pdf` is produced from it, via a renderer that works with **no**
      optional PDF dependency installed.
- [ ] The document contains all six required content sections, including "what was NOT found, and why"
      with the measurement distinguishing low data overlap from pipeline underperformance.
- [ ] All findings are sourced through generated SDK code and `reporting_guide` — no direct SQL against
      `database/G2C.db`.
- [ ] Both files appear in the module's "Files produced" list (INV-032) and the recap section.
- [ ] Rendering is verified by extracting text from the PDF and confirming the findings are present — a
      "PDF generated" message alone does not satisfy this criterion.
- [ ] A failure to produce either file reports the failure and does not block the Query Completeness Gate
      or graduation.
- [ ] The opt-in question itself is unchanged and still governs the interactive walkthrough only.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the analysis
      runs through the bootcamper's chosen language, and PDF generation must not require a
      platform-specific binary (no `pandoc`/`wkhtmltopdf` dependency).

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md` — decline and
  early-exit branches (lines ~39-42, ~148-149, ~203-204): produce the deliverable on every path
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — the
  Query Completeness Gate (line ~245) and the module's "Files produced" list
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — generalize, or add a sibling renderer for
  non-recap Markdown
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — ensure both files reach
  "Files produced" and the recap section

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Always produce a data-discoveries document,
  regardless of the Discover opt-in" (2026-07-25, Query, Visualize and Discover)
- Priority: Medium
- Related specs: **`specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (prerequisite)**,
  `specs/drop-deliverable-generation-gates.md` (generate-and-announce),
  `specs/robust-fpdf2-install.md`, `specs/recap-pdf-professional-design.md`,
  `specs/post-load-match-key-semantic-audit.md` (the match-key findings overlap)
