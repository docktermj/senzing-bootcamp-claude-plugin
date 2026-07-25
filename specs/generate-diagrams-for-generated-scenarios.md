# Don't ask for diagrams the bootcamper can't have — generate them for bootcamp-generated scenarios

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

After the bootcamper accepted the bootcamp-generated business scenario (Customer 360°, ENFORMION +
EQUIFAX, ~4,000 records), Phase 2 Step 9 asked:

> 👉 **Do you have any diagrams of your data architecture and flows you'd like to share?**

The scenario was invented by the bootcamp minutes earlier. There are no diagrams to share. The
bootcamper interrupted with feedback instead of answering.

Their point: "The question is a dead end for anyone who took the generated-scenario path, wasting a
turn on something that can't be answered usefully." And the constructive half — since the bootcamp
authored the scenario, it should *generate* the data architecture and data flow diagrams rather than
ask for them.

## Root cause

`phase2-document-confirm.md:5-15` presents Step 9's question unconditionally:

> ## 9. Encourage visual explanations
>
> Invite the bootcamper to share any diagrams. Ask this single, pinned 👉 question, verbatim
> (INV-056), and end the turn on it:
>
> 👉 **Do you have any diagrams of your data architecture and flows you'd like to share?**

There is no branch on scenario provenance. The provenance is available and the same file already
branches on it 100 lines later — `phase2-document-confirm.md:109` has a **"Generated scenario
(Business Case Offer accepted)"** branch that adds the `> 🤖 Bootcamp-generated business case` marker
and registers the generated sources. So the signal exists and the branching pattern is established in
this exact file; Step 9 simply never consults it.

This is the same class of defect as two already-fixed items — asking a bootcamper about data the agent
itself produced — which is why the fix should follow their established shape rather than invent one.

## Proposed change

1. **Branch Step 9 on scenario provenance.** Determine whether the business problem came from the
   accepted Business Case Offer (Phase 1 Step 4a) or from a bootcamper-described real case, using the
   same signal the Step 11 generated-scenario branch already relies on
   (`phase2-document-confirm.md:109`).
2. **Bootcamper-described case:** unchanged. Ask the pinned question verbatim as today — a real case
   plausibly has real diagrams.
3. **Generated scenario:** skip the question and **generate the diagrams instead**, from the scenario
   the bootcamp just authored:
   - A **data architecture** diagram — the generated sources, the Senzing engine, and the datastore.
   - A **data flow** diagram — raw → mapped/Senzing-ready → loaded → resolved → queried.

   Announce them in one line rather than gating them behind a yes/no offer, per the
   generate-and-announce principle established by `specs/drop-deliverable-generation-gates.md`. Write
   them under `docs/` alongside `docs/business_problem.md`, and reference them from it so they are
   discoverable rather than incidental.
4. **Do not lose the turn's other purpose.** Step 9 also handles a bootcamper who shares an image
   containing `[variable]` placeholders (`phase2-document-confirm.md:14-15`). On the generated-scenario
   path that cannot arise, so nothing is lost — but keep that handling intact on the
   bootcamper-described branch.
5. **Diagram format.** Render as text-based diagrams (e.g. Mermaid or ASCII) embedded in Markdown, not
   as binary images: it keeps the artifact language-agnostic, diffable, offline (INV-091), and
   renderable in the recap without a headless browser. If the diagrams are to appear in the recap PDF,
   confirm the generator handles the chosen construct — `scripts/generate_recap_pdf.py` renders a
   specific set of Markdown constructs, and an unrenderable one would be silently dropped (see
   `specs/recap-pdf-generator-fail-loudly-on-content-loss.md`).
6. **Record it as a produced file** in the module's end-of-module summary "Files produced" list
   (INV-032), and in the recap section, so the bootcamper knows the diagrams exist.

Also worth checking while in this file: whether any *other* Step in Phase 2 asks the bootcamper for
input only a real-case owner could supply. The same audit found this class of question in three
separate places across the bootcamp; a fourth is plausible.

## Acceptance criteria

- [ ] On the generated-scenario path, Step 9's diagram-sharing question is **not** asked.
- [ ] On the generated-scenario path, data-architecture and data-flow diagrams are generated from the
      accepted scenario, written under `docs/`, referenced from `docs/business_problem.md`, and
      announced (not offered behind a yes/no gate).
- [ ] On the bootcamper-described path, the pinned question is asked verbatim, unchanged, including the
      `[variable]`-placeholder follow-up handling.
- [ ] The provenance branch uses the same signal as the existing generated-scenario branch in the same
      file — no second, divergent provenance mechanism.
- [ ] Generated diagrams are text-based Markdown constructs (no binary image dependency, no CDN) and
      render offline.
- [ ] The diagrams appear in the module's "Files produced" list (INV-032) and the recap section.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the diagrams
      describe the bootcamper's chosen language/datastore rather than assuming any, and require no
      platform-specific rendering tool.

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — Step 9
  (lines ~5-15): add the provenance branch and the generate-diagrams path; keep Step 11's existing
  generated-scenario branch (line ~109) as the provenance signal
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — confirm the generated
  diagrams flow into "Files produced" and the recap section

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Skip the 'share your diagrams' question after a
  generated scenario; generate diagrams instead" (2026-07-24, Discover the Business Problem)
- Priority: Medium
- Related specs: `specs/provenance-aware-phasec-load-questions.md` and
  `specs/skip-business-user-uat-for-generated-scenario.md` (the same don't-ask-about-generated-data
  pattern, already implemented — follow their shape), `specs/drop-deliverable-generation-gates.md`
  (generate-and-announce), `specs/pin-visual-explanations-question.md` (pinned this very question),
  `specs/encourage-own-business-case.md`
