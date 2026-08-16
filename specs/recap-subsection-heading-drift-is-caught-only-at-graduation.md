# Recap subsection headings drifted to bold labels for nine modules, because the only validator that catches it runs once, at graduation

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-completion.md` Step 2b's template specifies the four recap subsections as **H3 headings** —
`### Information Shared`, `### Questions & Responses`, `### Actions Taken`,
`### End-of-Module Summary`. A run wrote them as bold labels (`**Information Shared**`) instead, at
the first module, and then reproduced that shape faithfully for all nine.

Bold labels render fine in every Markdown viewer, so the recap looked correct at every point during
the bootcamp. The failure appeared only at graduation:

```text
ERROR: refusing to render docs/bootcamp_recap.md
  - input does not look like a bootcamp recap: 0 of 9 '##' sections carry any recognized sub-section
  - catastrophic content loss: only 2% of the input's content would reach the PDF (minimum 60%)
```

The generator's refusal is correct and its message names the cause precisely — a good failure. But
it is the **last step of the last module**, and by then the drift had been repeated nine times.
Recovering it meant a structural rewrite of the entire keepsake in the same turn that was supposed
to render it. Had the generator been more permissive, the same nine sections would have rendered at
2% and shipped.

⚠️ **The authoring mistake is the run's, not the plugin's** — the template says H3 in plain text.
What this spec fixes is the **eleven-module gap between making the mistake and being told**.

## Root cause

**Step 2c verifies the section by name; the PDF requires it by heading level; nothing reconciles
the two until graduation.**

- `bootcamp-onboarding/module-completion.md:140-156` — Step 2c, "Verify it landed". It re-reads
  `docs/bootcamp_recap.md` and confirms (a) a `## {Name}` heading for the just-completed module and
  (b) that the **End-of-Module Summary** carries its three labeled blocks. Neither check
  distinguishes `### End-of-Module Summary` from `**End-of-Module Summary**` — a substring check
  passes on both, and the three labeled blocks are bold by design, so their presence says nothing
  about the enclosing heading.
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py:963`, `:988-995` — the check that *does*
  distinguish them: sections carrying no recognized sub-section are refused, with the "0 of N"
  message quoted above.
- `--check` is invoked **only at graduation**: `graduation/SKILL.md:629` (content check),
  `:404`, `:509`, `:674`. `bootcamp-preparation/SKILL.md:426` documents the
  `--expect-modules` flag but does not run it per module. So the validator that would have caught
  this at module one never runs before module eleven.

Step 2c is otherwise well-aimed and says why it exists — *"This is the cheapest place to catch it:
the module's own work is still in context, whereas graduation has to reconstruct it from artifacts
weeks of session-time later."* That reasoning is right and it argues for exactly the change below;
the step simply performs a weaker check than the one it justifies.

## Proposed change

1. **Run `generate_recap_pdf.py --check` from Step 2c, after the append.** It reads one file and is
   fast. Running it after **every** append is the simplest rule and the one to prefer; running it
   after the **first** module's append is the minimum that closes the reported failure. Prefer
   every-append: the drift this found was introduced at module one, but a drift introduced at
   module five is equally possible and equally invisible.
2. **Keep it non-blocking and Bootcamper-invisible.** A `--check` finding at Step 2c is a
   correction the guide makes to the recap it just wrote, not a gate and not output (INV-012). The
   Bootcamper sees the existing `Recap updated: {Name}.` line either way.
3. **Say what to do on a finding, at the step.** Rewrite the just-appended section to the template's
   shape and re-run. At module one that costs one correction; the whole point is that the cost does
   not compound.
4. **Name the H3 requirement where the drift starts.** Add one line to Step 2b's rules block
   (`:103-111`) stating that the four subsections are `###` headings and that bold labels render
   identically in a Markdown viewer while producing a section the PDF generator refuses. The
   template already shows the shape; what is absent is the statement that the shape is
   load-bearing — the same reason `:109` had to spell out that the three summary blocks are labels
   rather than prose.

⛔ **Do not make the generator more permissive.** Its refusal is the one thing that worked, and
`:988-995` is what stopped a 2%-retention keepsake from shipping. This spec adds an earlier check;
it does not soften the last one.

## Acceptance criteria

- [ ] Step 2c runs `generate_recap_pdf.py --check` after appending, and states what to do when it
      reports a finding.
- [ ] A subsection written as `**Information Shared**` instead of `### Information Shared` is
      reported at the module where it is written, not at graduation.
- [ ] The check is non-blocking and produces no Bootcamper-facing output (INV-012); the module
      completes either way.
- [ ] Step 2b states that the four subsections are H3 headings and that bold labels pass a visual
      read while failing the PDF generator.
- [ ] `generate_recap_pdf.py`'s refusal thresholds are unchanged.
- [ ] A test asserts Step 2c invokes `--check`, and that the recap generator still refuses a
      bold-label recap.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — Step 2c
  (`:140-156`), and one line in Step 2b's rules block (`:103-111`).
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — no behaviour change; note that `--check`
  is no longer first run here, so its findings should normally be empty.
- `tests/` — new guard for the Step 2c invocation and the generator's continued refusal.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Recap subsections drifted to bold labels for nine straight modules; nothing noticed until graduation refused to render" (2026-08-16, Module: all — introduced at the first recap append, surfaced at graduation Step 1b; `Source: self-observed (assistant retrospective)`)
- Priority: High — the cost is paid at the worst possible moment, in the turn that renders the Bootcamper's keepsake.
- MCP re-check: n/a (no Senzing fact). The template, the validator and the graduation step all ship with the plugin.
- Upstream: not applicable — routed `plugin`.
- Related specs: `specs/consolidate-recap-per-module-summary.md`, `specs/end-of-module-summary-blocks-guaranteed.md` (the sibling gap: the three labeled blocks, already pulled forward into Step 2c), `specs/defer-commonmark-to-graduation.md` (why Step 2b deliberately does *not* prettify — the check proposed here is structural, not cosmetic, and does not disturb that)

## The shape worth recording

`end-of-module-summary-blocks-guaranteed` already pulled one graduation-time validation forward into
Step 2c — the three labeled blocks. It pulled forward the check for the failure that had been
observed, and left the enclosing heading, which had not. The general form is that a validator whose
only invocation is at the end of an eleven-module run cannot bound the cost of anything it detects:
every finding is already N repetitions old when it fires. Worth stating at Step 2c so the next
graduation-time check that proves useful is considered for the same move.
