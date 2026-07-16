# Defer CommonMark prettification of Markdown files to graduation

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Throughout the bootcamp the guide authors many `*.md` files — the accumulating
recap at `docs/bootcamp_recap.md` (one section per module) and any other docs
under `docs/`. By imitating the plugin's own source style, the guide tends to
fuss over CommonMark cosmetics as it writes each file: the `**Label:**` colon
convention, blank lines around lists (MD032) and headings (MD022), fenced-code
info strings (MD040), and so on. That effort and edit churn is spent inside a
prose-driven teaching flow where the bootcamper never sees or cares about lint
compliance mid-bootcamp. The polish only matters at the very end, when the recap
becomes the PDF trophy and the `production/` project is handed over. There is no
need for "pretty" Markdown until graduation.

## Root cause

Two gaps, confirmed by inspection:

- **No bootcamper-facing CommonMark tooling exists, and none is wanted mid-run.**
  The only CommonMark enforcement anywhere is the maintainer's machine-global
  `~/.claude/settings.json` `PostToolUse` hook, which fires when the *maintainer*
  edits plugin **source** `.md` files — it never runs in a bootcamper session.
  The Kiro `scripts/validate_commonmark.py` and `commonmark-validation` command
  were deliberately not ported (`MIGRATION.md:258`, `MIGRATION.md:397`, both
  still unchecked). So nothing prettifies the bootcamper's `.md` output during a
  run — which is the desired end state, but it is undocumented and unintentional.
- **No rule tells the guide what to do at either end.** There is no written
  guidance either to *skip* prettification during the bootcamp or to *normalize
  once* at graduation. The guide follows `**Label:**` and blank-line conventions
  only by imitation of the templates it reads (`module-completion.md:56-76`,
  `graduation/SKILL.md`), spending cosmetic effort per module, while the end
  deliverables get **no** guaranteed normalization pass — so the trophy PDF and
  the `production/` docs carry whatever ad-hoc formatting happened to accumulate.

## Proposed change

Two coordinated, guidance-only changes (no new script — per the chosen
guide-driven mechanism):

1. **During the bootcamp — write plain, functional Markdown.** Add a ground rule
   (`ground-rules.md`) that the guide authors `*.md` files (recap sections, docs
   under `docs/`) for correctness and readability but does **not** spend effort
   making them CommonMark-lint-clean as it goes — no fussing over `**Label:**`
   colon spacing, MD022/MD031/MD032 blank-line rules, or MD040 fence info strings
   mid-bootcamp. This complements INV-058's write-churn reduction and keeps the
   teaching flow uncluttered (INV-012). Structural requirements are unchanged:
   every recap section keeps its `## Module N:` heading and the four required
   subsections (INV-048), and all placement rules (INV-017/INV-050) still hold.
   Reinforce the same "append plain, do not prettify per module" note where recap
   sections are authored (`module-completion.md` Step 2).

2. **At graduation — one best-effort CommonMark normalization pass.** Add a
   guide-driven step in `graduation/SKILL.md` that, once and best-effort (matching
   graduation's non-blocking, warns-and-continues posture, `SKILL.md:17-20`),
   normalizes CommonMark across **all** bootcamp-authored `*.md`:
   - `docs/*.md` (including `docs/bootcamp_recap.md`) — performed in **Step 1a**,
     after the recap reconcile and **before** the Step 1b PDF render, so the
     trophy renders clean.
   - the generated `production/*.md` (`README.md`, `MIGRATION_CHECKLIST.md`,
     `GRADUATION_REPORT.md`) — authored to / normalized under the same rules as
     they are generated in Steps 3-5.

   The pass applies the same rule set the maintainer's convention uses (MD022
   headings, MD031 fenced blocks, MD032 lists surrounded by blank lines, MD040
   fence info strings, `**Label:**` colon spacing). It is **purely cosmetic —
   structure- and content-preserving**: it never reorders, removes, or rewrites
   the prose of completed `## Module N:` sections or their four subsections, so it
   does not touch the append-only recap guarantee (INV-059) or the required PDF
   structure (INV-048). A failure to normalize is never a reason to skip the PDF
   or halt graduation.

## Acceptance criteria

- [ ] `ground-rules.md` states the guide writes functional, plain Markdown during the bootcamp and defers CommonMark prettification to graduation (referencing INV-012/INV-058); `module-completion.md` Step 2 reinforces "append plain, prettify at graduation."
- [ ] `graduation/SKILL.md` defines a single best-effort CommonMark normalization pass over `docs/*.md` performed after recap reconcile and **before** the Step 1b PDF render, and over the generated `production/*.md` files.
- [ ] The normalization is structure- and content-preserving: every `## Module N:` heading and the four subsections (INV-048) remain intact; no completed recap section content is reordered, removed, or rewritten (INV-059 upheld); `.md` placement (INV-017/INV-050) is unchanged.
- [ ] The pass is non-blocking: if it fails, graduation warns and continues, and the recap PDF still renders.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — add the "write plain Markdown during the bootcamp; defer CommonMark prettification to graduation" rule.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — add the single best-effort CommonMark normalization pass: Step 1a over `docs/*.md` before the 1b render, and over the generated `production/*.md` (Steps 3-5); note it is structure/content-preserving and non-blocking.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — reinforce that per-module recap sections are appended as plain, functional Markdown (no per-module prettification).

## Source

- Maintainer request (2026-07-16): "defer all CommonMark processing of `*.md` files until the graduation — there's no need to have pretty Markdown files until the end of the Bootcamp."
- Priority: Low (process/cosmetic; reduces per-module effort and edit churn; no bootcamper-visible behavior change during the bootcamp).
- Related specs: `suppress-admin-write-noise.md` (write-churn reduction, INV-058), `recap-durability.md` (append-only recap, INV-059).

## Invariants introduced

- `INV-060` — CommonMark prettification of bootcamp-authored `*.md` files MUST be deferred to graduation: during the bootcamp the guide writes functional, plain Markdown without incremental lint compliance, and graduation MUST perform a single best-effort, structure- and content-preserving CommonMark normalization pass over `docs/*.md` (before the recap PDF renders) and the generated `production/*.md`, never reordering, removing, or rewriting completed `## Module N:` recap sections or their four required subsections (recorded in `specs/INVARIANTS.md`).
