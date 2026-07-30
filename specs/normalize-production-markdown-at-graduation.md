# INV-060's normalization pass over the generated `production/*.md` was never built; graduation hand-formats them instead

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-060 requires graduation to run one CommonMark normalization pass over **two** sets of files:

> … graduation MUST perform a single best-effort, structure- and content-preserving CommonMark
> normalization pass over `docs/*.md` (before the recap PDF renders) **and the generated
> `production/*.md`** …

Graduation runs the normalizer over `docs/` only. For `production/*.md` it instead instructs the
guide to hand-author them to the house rules — the exact practice INV-060 exists to replace. So the
`production/` project the bootcamper is handed over carries whatever formatting the guide happened
to produce, unchecked, while the recap next to it went through a content-guarded normalizer.

## Root cause

Only the `docs/` half of the pass was implemented.

- **Built.** `plugins/senzing-bootcamp/skills/graduation/SKILL.md:388-400` defines the pass and runs
  the bundled normalizer:

  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/normalize_docs_markdown.py"
  ```

  and states, at `:406-408`, *"It globs top-level `docs/*.md` only and never recurses"* — correct
  and deliberate for the feedback file (INV-015/INV-067), but it also means `production/` is out of
  reach by construction.

- **Not built.** `production/*.md` gets prose instructions instead:
  - `:611` — *"Author every `production/*.md` deliverable … to the same CommonMark house rules
    applied to the recap in Step 1a"*
  - `:675` — the same for `docs/REVISIT_BOOTCAMP.md`

  Hand-authoring is precisely what `ground-rules.md:267-274` tells the guide **not** to rely on:
  *"write for correctness and readability — do NOT spend effort making them CommonMark-lint-clean as
  you go … graduation runs a single normalization pass."* The plugin asks for the discipline in the
  one place it also says the discipline is unreliable.

- **The originating spec required it.** `specs/defer-commonmark-to-graduation.md:78`:

  ```text
  - [ ] `graduation/SKILL.md` defines a single best-effort CommonMark normalization pass over
        `docs/*.md` performed after recap reconcile and **before** the Step 1b PDF render, and over
        the generated `production/*.md` files.
  ```

  and `:86` lists the same two-part change. The spec is recorded implemented
  (`specs/IMPLEMENTED.md:2588`, 2026-07-16, commit `d69c360`) with `graduation/SKILL.md` in its
  Files-changed list — the file was edited, but only for `docs/`. No test references INV-060.

- **The tool already supports the fix.** `plugins/senzing-bootcamp/scripts/normalize_docs_markdown.py`
  takes `--docs-dir` (default `docs`, "Never recursed"), so a second invocation over `production/`
  needs no code change and inherits the content guard — the fingerprint-and-restore behavior
  INV-129 requires of any cosmetic pass over a deliverable.

**Ordering matters.** `production/` does not exist at Step 1a; it is created in Steps 3-5. So the
production pass belongs **after Step 5** (and after `docs/REVISIT_BOOTCAMP.md` is written in Step
6c, if that file is included in the run), not merged into the existing Step 1a invocation.

## Proposed change

1. **Add the second invocation** after the `production/` deliverables are written (end of Step 5, or
   a short Step 5a), scoped and non-recursing exactly like the first:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/normalize_docs_markdown.py" --docs-dir production
   ```

   Carry over the surrounding contract verbatim in intent: best-effort, non-blocking, warn-and-
   continue if it fails or is unavailable (INV-048), never hand-edit prose to make formatting pass,
   and a file the normalizer leaves as written is a normalizer bug to report rather than to fix by
   hand.
2. **Re-scope the hand-authoring instructions** at `:611` and `:675` from "author to the house
   rules" to "write plain, functional Markdown; the Step 5a pass prettifies it" — consistent with
   `ground-rules.md:267-274`. Keep the structural requirements (headings, sections, checkbox lists)
   binding: INV-060 defers *formatting*, never structure.
3. **Decide `docs/REVISIT_BOOTCAMP.md` explicitly.** It lives in `docs/` (INV-017) but is written in
   Step 6c, *after* the Step 1a pass — so today it is normalized by neither invocation. Either write
   it before Step 1a (it depends on Step 6a's restore command, so probably not), or include `docs/`
   in the late pass as well. State the choice in the file so the gap cannot reopen.
4. **Assert both invocations** exist and that the late one runs after the `production/` build.

## Acceptance criteria

- [ ] `graduation/SKILL.md` runs `normalize_docs_markdown.py` over `production/` after the
      `production/*.md` deliverables are generated, in addition to the existing `docs/*.md` pass.
- [ ] The production pass is documented as best-effort, non-blocking, and content-guarded, with the
      same "a file left as written is a normalizer bug" instruction as the `docs/` pass.
- [ ] `:611` and `:675` no longer ask the guide to hand-format `production/*.md`; they ask for plain
      functional Markdown and point at the pass.
- [ ] `docs/REVISIT_BOOTCAMP.md`'s normalization is explicitly covered by one of the two passes, and
      the file says which.
- [ ] The feedback file remains structurally unreachable by both passes
      (`docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` survives graduation intact — INV-015/INV-067).
- [ ] A test asserts both invocations are present and that the production one is ordered after the
      production build.
- [ ] `tests/test_normalize_docs_markdown.py` still passes; no change to the normalizer's own
      behavior or content guard is needed.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      normalizer is stdlib Python 3 invoked in exec form (INV-052).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — add the post-Step-5 pass; re-scope `:611`
  and `:675`; settle `REVISIT_BOOTCAMP.md`.
- `tests/test_normalize_docs_markdown.py` (extend) or a new `tests/test_graduation_normalization_scope.py`.
- `specs/defer-commonmark-to-graduation.md` — append a dated note that the `production/*.md` half of
  criterion 1 was found unmet on 2026-07-29 and is discharged here; do not edit the criterion text.
- `specs/IMPLEMENTED.md` — append a correction to the 2026-07-16 entry rather than rewriting it.

## Source

- Feedback: n/a — found by the deep-dive invariant-conformance audit of 2026-07-29, run at the
  maintainer's request; `Source: self-observed (assistant retrospective)`.
- Priority: **Medium** — cosmetic in effect, but it is an unimplemented MUST that has stood since
  2026-07-16 while recorded as done, and it affects the project the bootcamper hands to colleagues.
- MCP re-check: n/a (no Senzing fact — Markdown formatting of generated files). Server **1.32.2**
  confirmed current at triage time via `get_capabilities`, 2026-07-29.
- Upstream: not applicable.
- Related specs: `specs/defer-commonmark-to-graduation.md` (the originating spec whose criterion this
  discharges), `specs/artifact-level-verification-for-deliverables.md` (INV-129's requirement that a
  cosmetic pass prove it preserved content — already satisfied by the normalizer's guard),
  `specs/feedback-file-durability.md` (INV-067, why neither pass may recurse).
