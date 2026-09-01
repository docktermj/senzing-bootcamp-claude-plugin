# The RECAP-CHECKPOINT block is parsed as modules instead of being lifted out, unlike BOOTCAMP-NOTES

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`SessionStart:resume` folds `docs/progress/recap_checkpoint.md` into `docs/bootcamp_recap.md`
verbatim, fenced in `<!-- RECAP-CHECKPOINT:START/END -->`. The checkpoint's own internal structure
uses `## ` headings (`## Where we are`, `## What is done in this module`, `## Still to do`,
`## To restart the visualization`, `## Headline results to carry in`).

`generate_recap_pdf.py` parses **every** `## ` heading as a module section, and **does not lift the
`RECAP-CHECKPOINT` fence before doing so** — even though it lifts the sibling `BOOTCAMP-NOTES`
fence for exactly this reason. `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py:669`:

> *"Lift the BOOTCAMP-NOTES fence out of `text` before any module parsing."*

There is no equivalent for `RECAP_CHECKPOINT_START` / `RECAP_CHECKPOINT_END`
(`:122-123`). Grep confirms the two constants are referenced in exactly one other place — the audit
at `:1322` — and nowhere in the parse path.

Reported after a pause/resume on 2026-08-26: five checkpoint headings would have become five
phantom "modules" beside the nine real ones in the keepsake PDF.

⚠️ **The reporter's "no error, no warning" is not accurate today, and the correction narrows the
finding rather than dissolving it.** `audit_recap` (`:1322`) *does* warn when a checkpoint block
survives into the recap:

> `recap still contains a <!-- RECAP-CHECKPOINT:START --> … <!-- RECAP-CHECKPOINT:END --> block —
> a module was folded by the durability hooks but never finalized (module-completion step 2d)`

So the condition is **detected**. What it is not is **prevented**: the warning goes into `warnings`,
not `fatal`, so the PDF still renders — and it renders with the phantom sections, because the block
was never lifted before parsing. The reporter's other two observations both hold: content retention
would report ~100% (no characters are lost, they are mis-parsed), and `--expect-modules` checks that
expected modules are **present**, never that unexpected ones are **absent**.

## Root cause

`plugins/senzing-bootcamp/scripts/generate_recap_pdf.py`. The notes fence and the checkpoint fence
are the same hazard — an author-controlled block, folded verbatim, whose interior headings are
indistinguishable from module headings once inside the recap — and only one of them is lifted.

The asymmetry is not a considered decision: `graduation/SKILL.md` states the principle for the notes
block in general terms — the fence *"is what makes this safe, not the heading text"*, because a
Bootcamper's private note is *"one heading away from being printed on their Certificate of
Completion"*. The checkpoint fold has the same fence and the same exposure; it simply never got the
same treatment in the parser.

⚠️ This is the **rule applied to some of the sites it binds** class: one rule (lift a fenced block
before module parsing), two fences, one implementation.

## Proposed change

1. **Lift the `RECAP-CHECKPOINT` block before module parsing**, exactly as the `BOOTCAMP-NOTES`
   fence is lifted. The block's content is transient working state; nothing in it belongs in the
   PDF as a module.
2. **Keep the `audit_recap` warning.** It answers a different question — *a module was folded and
   never finalized* — which stays worth reporting even once the headings can no longer leak.
   Lifting the block must not silence it.
3. **Derive the fence set by scanning rather than listing two constants**, so a third fenced block
   added later is lifted by construction (INV-246). If that is too large a change, at minimum place
   the two fences in one collection the parse path iterates.

⚠️ Do **not** fix this by demoting the checkpoint's headings to `### ` at write time alone. That
narrows the blast radius for one writer and leaves the parser accepting whatever the next writer
emits — the file is written by a hook, and the parser is what the guarantee has to live in.

## Acceptance criteria

- [ ] A recap containing a `RECAP-CHECKPOINT` block renders no module section for any heading
      inside that block.
- [ ] The `audit_recap` warning for a surviving checkpoint block still fires.
- [ ] The `BOOTCAMP-NOTES` behavior is unchanged.
- [ ] A repo-level test builds a recap with a checkpoint block containing `## ` headings and
      asserts the parsed module list excludes them. Negative-controlled: remove the lift, confirm
      the test fails, restore.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — the module parse path (`:122-123`,
  the notes lift at `:669`, the audit at `:1322`).
- `tests/test_recap_checkpoint_is_lifted_before_module_parsing.py` (new) — the guard.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`, entry *"Resumed-session recap checkpoint injects
  phantom module headings into the recap PDF"*, 2026-08-26, module **Bootcamp graduation**,
  priority **High**, `Source: self-observed (assistant retrospective)`, plugin 0.5.2, macOS 26.5.2.
- Priority: High — it reaches `docs/bootcamp_recap.pdf`, the keepsake deliverable, and the
  pause/resume path is common.
- MCP re-check: **n/a (no Senzing fact)** — the fold, the fence and the parser are all the
  plugin's, and no Senzing behavior is in dispute.
- Upstream: not applicable
- Related specs: `nothing-writes-the-recap-checkpoint.md` (the checkpoint's *production*, a
  different subject); `bootcamp-notes-capture-and-recap-section.md` (the sibling fence whose lift
  this one is missing).
