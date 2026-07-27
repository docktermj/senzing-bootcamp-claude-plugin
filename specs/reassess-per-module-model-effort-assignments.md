# Re-assess the per-module model/effort assignments, and ask only when the Bootcamper is not already there

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The model/effort *mechanism* was rebuilt twice in two days — INV-119/INV-120 introduced three
configurable modes, INV-137 retired them and restored the unconditional pause — but the **values it
surfaces** have not been re-examined since 2026-07-16, and the modules underneath them have changed
substantially since. The maintainer reports the assignment still seems wrong.

Six distinct problems, all in the assignment rather than the flow.

**(a) The table oscillates, and every oscillation is now a mandatory pause.** Mapped onto the module
order, today's four rows produce **six** change points on the full path:

| # | Stage | Today | Change? |
|---|---|---|---|
| — | Onboarding | Sonnet 5, medium | — |
| 1 | Bootcamp preparation | Sonnet 5, medium | no (apparatus-exempt) |
| 2 | Entity Resolution Concepts | **no row** | undefined |
| 3 | Discover the Business Problem | Sonnet 5, medium | no |
| 4 | SDK setup | Opus 5, high | **yes — up** |
| 5 | System verification | Sonnet 5, medium | **yes — down** |
| 6 | Truth Set visualization | Sonnet 5, medium | no |
| 7 | Data collection | Sonnet 5, medium | no |
| 8 | Data Quality, Mapping, and Transformation | Opus 5, high | **yes — up** |
| 9 | Data processing | Sonnet 5, high (Opus if bespoke) | **yes — down (model)** |
| 10 | Query, Visualize and Discover | Sonnet 5, medium | **yes — down (effort)** |
| 11 | Graduation | Opus 5, high | **yes — up** |

Under INV-137 each change point costs one yielding turn for the switch question, and two on a
**yes** (question, then the "Are you done modifying the model and effort?" gate) before the module's
first step. Up to **12 extra turns** of model administration in a bootcamp. When the mechanism was
advisory this cost nothing; now the assignment is what sets the interruption rate, and a table that
ping-pongs makes a correct flow feel broken.

**(b) A bootcamper who is already on the recommended setting is asked anyway.** Change detection
compares this stage's recommendation to the **previous stage's recommendation** — not to what the
Bootcamper is actually running. `docs/model-selection.md:151-153` explicitly endorses "run the whole
session on Opus 5 + high effort" as a supported choice. That Bootcamper is asked "Would you like to
switch to `/model opus` + `/effort high`?" at SDK setup, at Data Quality and at Graduation — three
times, each time already on exactly that — and asked to *drop* to Sonnet three more times. Six
questions, none of which needed asking. INV-006 (ask once) and INV-012 (suppress what does not
matter to the Bootcamper) are both strained by this.

**(c) Three downgrade prompts carry no explanation.** The pinned question is the same whichever
direction the recommendation moves: "Would you like to switch to `/model sonnet` + `/effort medium`
for this module? (Recommended for best value; reply no to keep your current model.)" A Bootcamper on
Opus entering System verification is offered a step down with no statement of why that is safe. The
requirement that a below-current recommendation be flagged as a downgrade exists — but it is
attached to the **recommendation-unchanged** branch, which is the one case where a downgrade cannot
arise.

**(d) Two rationales are stale — the modules outgrew them.**

- *Truth Set visualization* is rated Sonnet 5 because it is "mostly run / render". That has not been
  true since INV-090: the module now **builds a visualization server in the Bootcamper's chosen
  language** from a written contract — tab ids and `activate()`/deep-linking (INV-124), script-payload
  escaping (INV-106), offline D3 vendoring (INV-091), brand tokens (INV-081), scale-aware defaults.
  It is the largest code-generation artifact in the bootcamp before graduation.
- *Query, Visualize and Discover* is rated Sonnet 5 / medium — the lightest setting in the table —
  because it is "iterative query/exploration; Sonnet's speed suits it". It is also where the
  silent-wrongness defects actually land. In the 2026-07-26 feedback file alone, **three** of the
  self-observed entries are Module 7: response-shape parsing with no `response_schemas` entry, the
  `MIN_ENTITY_ID`/`MAX_ENTITY_ID` endpoint keys that render a half-populated row, and the factory
  lifetime error. `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115) came from the same
  module. This is the module whose failures are invisible by construction, rated for speed.

**(e) One cell cannot drive the mechanism that reads it.** Data processing is "Sonnet 5, high effort
(Opus if bespoke load code)". Whether load code is bespoke is not known at module start, when the
nudge fires. INV-056 requires the switch question be pinned verbatim — a conditional recommendation
cannot be pinned, and change detection cannot compare against a value with two branches.

**(f) Entity Resolution Concepts (Module 0) has no row.** Onboarding and Bootcamp preparation are
listed specifically so change detection has a previous value to compare against
(`ground-rules.md:382-384`). Module 0 is apparatus-exempt for the same reason they are, but it is
missing, so when it runs, the stage entering Discover the Business Problem has no defined predecessor.

## Root cause

**The table.** `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:371-376` holds the
authoritative copy; `plugins/senzing-bootcamp/docs/model-selection.md:133-138` mirrors it, with the
per-skill rationale that produced it at `:80-91`. `tests/test_model_guidance_sync.py` keeps the two
identical but asserts nothing about the *values* — `test_every_row_names_a_model_and_an_effort` checks
only that each row names a model and an effort. Nothing has ever forced a re-read of the assignment
against what the modules do, so the 2026-07-16 evaluation survived every change to the modules it
rates.

**The detection rule.** `ground-rules.md:322` — "Two cases, decided only by whether the recommendation
**changed**" — and INV-137 in the same words. Neither reads the Bootcamper's actual setting. Nothing
in the plugin does: `docs/model-selection.md:23` records that only command hooks can see the session
effort (`$CLAUDE_EFFORT`), and no file reads it. Yet the retained INV-120 requirement already assumes
the current model is knowable — it requires the unchanged-branch line to "name the Bootcamper's
**current** model and reasoning effort alongside the recommendation". The guide is told its own model
in its context; the capability exists and is unused for detection.

**The downgrade framing.** `ground-rules.md:349-353` places the below-current flagging inside the
"Recommendation unchanged" bullet. The changed branch (`:324-348`) has no equivalent.

**A hardcoded coupling that the re-assessment breaks.** `skills/graduation/SKILL.md:81-86` states that
graduation "steps up from the Module 7 recommendation, so the recommendation has **changed** and the
switch question below always applies here." That is an assertion about the table baked into a
different file. Raising Module 7 makes it false, and graduation would keep asking a question its own
premise no longer supports.

## Proposed change

### 1. The re-assessed assignment

Best value remains "the capability the workload needs, at the lowest tier that meets it" — re-judged
against what each module does **today**, and against where defects have actually occurred. Verify
model names, IDs and pricing against current Claude documentation at implementation time (INV-114);
the tiers below are the judgement, not the model facts.

| # | Stage | Recommended | Change | Why |
|---|---|---|---|---|
| — | Onboarding | Sonnet 5, medium | — | Gated preface, pinned wording, preference capture. Protocol adherence, no code. |
| 1 | Bootcamp preparation | Sonnet 5, medium | — | Same; apparatus-exempt, listed for detection only. |
| 2 | Entity Resolution Concepts | Sonnet 5, medium | **new row** | Teaching and quiz, conversational; apparatus-exempt, listed for detection only. |
| 3 | Discover the Business Problem | Sonnet 5, medium | — | Discovery conversation, light technical. |
| 4 | SDK setup | Opus 5, high | — | Largest skill; cross-platform install, licence/engine/DB config, build-from-source recovery. Errors here are high-cost and platform-specific. |
| 5 | System verification | Sonnet 5, **high** | effort ↑ | Not "run / check / report" any more: it writes and runs the first real SDK code, and the export-flag defect in the 2026-07-26 feedback was filed against **this** module at step 7. Sonnet still fits the volume of work; the reasoning load justifies high. |
| 6 | Truth Set visualization | **Opus 5, high** | model ↑, effort ↑ | Builds a full web application in an arbitrary language from a written contract (INV-090/INV-124/INV-106/INV-091/INV-081). The largest code-generation task before graduation, and historically the most defect-prone. |
| 7 | Data collection | Sonnet 5, medium | — | Gathering sources, light code. Genuinely the lightest technical module. |
| 8 | Data Quality, Mapping, and Transformation | Opus 5, high | — | Mapping correctness drives resolution quality — the technical crux, unchanged. |
| 9 | Data processing | **Opus 5, high** | conditional resolved | Removes the unpinnable "(Opus if bespoke load code)". Its failures are the silent kind: export flag families producing valid-but-empty rows, a redo drain that hangs, the threading cutover. |
| 10 | Query, Visualize and Discover | **Opus 5, high** | model ↑, effort ↑ | Three of the 2026-07-26 self-observed defects landed here, plus INV-115's originating incident. Wrong field names render blank rather than raising — the failure mode least tolerant of a speed-tuned setting. |
| 11 | Graduation | Opus 5, high | — | Crown-jewel deliverable: recap reconcile, PDF rendering, production project. |

Effects: the back half (Data Quality → Data processing → Query, Visualize and Discover → Graduation)
becomes **flat at Opus 5 / high**, eliminating three change points in the stretch where the Bootcamper
is deepest in the work; change points fall from six to five, and the remaining ones sit at genuine
workload boundaries rather than at artefacts of an ageing table.

**Considered and rejected, recorded so they are not re-litigated:**

- *Sonnet 5 / high for Truth Set visualization* instead of Opus — the cost-conscious variant, and
  defensible since the contract is explicit and a reference implementation ships. Rejected because the
  module generates a complete app in an unconstrained language. **Settled by the maintainer,
  2026-07-26: Opus 5 / high.** The resulting up-down-up across Truth Set visualization → Data
  collection → Data Quality is accepted; §2's detection fix is what keeps it from costing prompts.
- *`xhigh` effort for Graduation.* The effort dial supports `low`/`medium`/`high`/`xhigh`/`max`
  (`docs/model-selection.md:20`). Rejected: no evidence `high` is insufficient, and a third value on
  the dial adds a change point and a vocabulary the rest of the table does not use.
- *Flattening the table to reduce prompts.* Rejected: the assignment should describe the work. Prompt
  volume is a detection problem, fixed in §2 — not a reason to misrate a module.

### 2. Ask only when a change is actually needed

Keep the flow exactly as INV-137 defines it — on a change, a single pinned 👉 switch question as its
own yielding turn; on **yes**, the one-line run-commands statement followed by the pinned
"👉 Are you done modifying the model and effort?" gate, with the module's first step deferred to the
turn after the Bootcamper confirms; on **no**, the first step lands that same reply turn. That is the
requested behaviour and it is already shipped. Three corrections:

1. **Compare against the Bootcamper's actual setting, not the previous recommendation.** The trigger
   is "the recommendation differs from what the Bootcamper is running now". The guide is told its own
   model in its context, so the model side is directly knowable; where the effort in force cannot be
   determined, fall back to the previous stage's recommendation as today. When the Bootcamper is
   already on the recommended model **and** effort, present the unchanged one-line statement — never
   a question. This is what removes the pointless prompts in problem (b), including all three
   "switch to Opus?" asked of someone already on Opus.

2. **Say which dial is moving, and which is not.** Model and effort are separate dials (retained from
   INV-120). When only one differs, the question and the run-commands line name only that one — a
   Bootcamper on Opus/medium entering a Sonnet/high stage should not be told to change both.

3. **Carry the downgrade framing into the changed branch.** When the recommendation sits *below* what
   the Bootcamper is running, the switch question must say so plainly — that staying put is fine, that
   the recommendation is about cost rather than capability, and that declining costs them nothing.
   The requirement currently lives only on the unchanged branch, which is the one place it cannot
   apply.

### 3. Invariants to revise

The supersession chain is intact — INV-062 → INV-063 → INV-119 → INV-137 and INV-064 → INV-069 →
INV-119 → INV-137 all carry their notes, and INV-119/INV-120 are correctly marked retired. No
renumbering or deletion is needed (INVARIANTS.md rule 1). What changes:

- **INV-137** (governing) — amend the trigger from "whether the recommendation **changed** from the
  stage just completed" to "whether the recommendation differs from the model/effort the Bootcamper is
  currently running, falling back to the previous stage's recommendation where the current setting
  cannot be determined". Add: when only one dial differs, only that dial is named. This is a change of
  meaning, so per rule 2 it is a **new invariant** superseding INV-137, not an in-place edit.
- **New invariant** — a below-current recommendation MUST be flagged as a downgrade in the **switch
  question** as well as in the unchanged statement, stating that declining costs nothing. (Extends the
  INV-120 requirement that INV-137 retained.)
- **New invariant** — every stage the bootcamp can run MUST have a row in the per-stage table,
  including apparatus-exempt stages, so change detection always has a defined value on both sides.
  This is what closes problem (f).
- **New invariant** — a per-stage recommendation MUST name exactly one model and one effort. No
  conditional or two-branch cell, because INV-056 requires the question be pinnable and detection
  requires a single comparable value. This is what closes problem (e).
- **INV-114** — unchanged in meaning, but its scope note should state that the two tables must match
  **row for row including the stage list**, so a newly added stage row cannot land in one file only.
- **INV-063/INV-069** — no change; their behaviour is what §2 preserves.
- **INV-098** — no change; surface adaptation applies unchanged to the revised wording.
- **INV-133** — no change; it already records that it no longer governs `model_guidance`.
- **INV-096** — no change, but confirm the apparatus order (step overview → time estimate →
  model/effort prompt) still holds for the modules whose recommendation now changes.

## Acceptance criteria

- [ ] The per-stage table in `ground-rules.md` carries one row per stage the bootcamp can run —
      including Entity Resolution Concepts — and `docs/model-selection.md` mirrors it row for row
      (`tests/test_model_guidance_sync.py` passes).
- [ ] No table cell names a conditional or alternative recommendation; every row names exactly one
      model and one effort.
- [ ] The per-skill rationale table in `docs/model-selection.md` is updated for every row whose value
      changed, and its Truth Set visualization and Query, Visualize and Discover rationales no longer
      describe the modules as run/render and speed-suited.
- [ ] Walking the full module order, the recommendation is flat from Data Quality, Mapping, and
      Transformation through Graduation — a Bootcamper who switches at Data Quality is asked nothing
      further for the rest of the bootcamp.
- [ ] A Bootcamper already running the recommended model and effort receives the one-line statement,
      never the switch question — verified for the "Opus 5 / high throughout" path documented in
      `docs/model-selection.md`, which must produce **zero** switch questions after the first stage
      that recommends it.
- [ ] When only the model differs, the question and run-commands line name only the model; likewise
      for effort alone.
- [ ] The pause is symmetric: a recommendation that differs from the Bootcamper's current setting
      produces the switch question whether it is higher **or** lower — no direction-based asymmetry,
      and no path where a differing recommendation is downgraded to a statement.
- [ ] A recommendation below the Bootcamper's current setting is explicitly identified as a downgrade
      **in the switch question**, stating that declining costs nothing and that the recommendation is
      about cost rather than capability.
- [ ] The accepted-switch path still ends on the pinned "👉 Are you done modifying the model and
      effort?" gate with the first step deferred to the next turn, and a declined switch still lands
      the first step on the reply turn (INV-137/INV-063/INV-069 unchanged).
- [ ] Exactly one 👉 per turn throughout, every gate pinned verbatim, and the gate asked once
      (INV-008/INV-009/INV-056/INV-006).
- [ ] `graduation/SKILL.md` no longer asserts that graduation always steps up from Module 7; it
      derives its behaviour from the table like every other stage.
- [ ] The apparatus-exempt stages still present no model/effort guidance at all (INV-075/INV-078).
- [ ] The revised invariants are recorded in `specs/INVARIANTS.md` as new IDs superseding INV-137
      where meaning changed, with no existing invariant deleted or renumbered.
- [ ] `tests/test_model_guidance_behavior.py` and `tests/test_model_guidance_sync.py` are extended to
      cover the new trigger, the single-dial case, the downgrade framing in the switch question, and
      total table coverage of the stage list — and fail against the pre-change files.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      recommendation is about the session model, independent of the Bootcamper's chosen language and
      platform, and the surface adaptation of INV-098 is preserved.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the authoritative table
  (`:371-376`), the change-detection rule (`:320-353`), the downgrade framing (`:349-353`), and the
  Entity Resolution Concepts row plus the detection note at `:382-384`.
- `plugins/senzing-bootcamp/docs/model-selection.md` — the mirrored table (`:133-138`), the per-skill
  best-value evaluation (`:80-91`), the behaviour table (`:103-106`), and the recommendation section
  (`:140-153`) whose "switch up for Modules 2 and 5, and graduation" summary changes.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — `:81-86`: drop the hardcoded "always steps
  up from Module 7" premise.
- `specs/INVARIANTS.md` — new invariants superseding INV-137 per §3; supersession notes only, nothing
  removed.
- `tests/test_model_guidance_sync.py`, `tests/test_model_guidance_behavior.py` — new coverage per the
  acceptance criteria.

## Decisions on record

Both open questions are settled. Nothing in this spec awaits a choice — implement it as written.

1. **Truth Set visualization is Opus 5 / high** (maintainer, 2026-07-26). The workload argument wins
   over the change-point argument; the resulting oscillation is accepted.
2. **The pause is symmetric — downgrades and upgrades both ask** (maintainer, 2026-07-26). The
   alternative considered was making a downgrade a one-line statement, on the reasoning that running
   *heavier* than recommended is never harmful, only more expensive; that would have left only
   upgrades pausing. **Rejected.** The rule is direction-neutral: whenever the recommendation differs
   from what the Bootcamper is running, they are asked, and the choice stays theirs in both
   directions.

   This makes §2 item 3 load-bearing rather than a nicety. A symmetric pause means the Bootcamper is
   periodically asked to step *down*, so the switch question must state that declining costs nothing
   and that the recommendation is about cost rather than capability. Without that framing a
   downgrade prompt reads as being asked to accept a worse experience — which is the reason the
   below-current flagging requirement (INV-120, retained by INV-137) exists at all.

## Source

- Maintainer request, 2026-07-26: re-assess the appropriate model and effort for each bootcamp module;
  ask the Bootcamper to switch when the next module's recommendation differs from the current one;
  on acceptance let them change it and then confirm they are done; and revisit every invariant related
  to the Bootcamper selecting model/effort.
- Supporting evidence: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` (2026-07-26) — the module attribution of
  the self-observed silent-wrongness entries is what grounds the System verification, Data processing
  and Query, Visualize and Discover re-ratings.
- Priority: High (the flow is shipped and unconditional, so the assignment now sets the interruption
  rate for every bootcamp)
- Related specs: `retire-model-guidance-modes` (INV-137 — the current governing behaviour; ledgered in
  `specs/IMPLEMENTED.md:71`, no spec file), `specs/skip-model-guidance-question.md` (its predecessor),
  `specs/model-effort-guidance-advisory-not-gate.md` (INV-119/INV-120, retired),
  `specs/model-effort-change-prompt.md` (INV-063), `specs/model-effort-switch-done-confirmation.md`
  (INV-069), `specs/model-switch-single-turn-continuation.md` (INV-064, superseded),
  `specs/module-start-model-nudge.md` (INV-062, superseded),
  `specs/surface-aware-model-effort-instructions.md` (INV-098),
  `specs/refresh-model-guidance-to-current-top-tier-model.md` and
  `specs/model-effort-table-name-based.md` (INV-114 — table currency and sync),
  `specs/skill-model-selection.md` (the turn-scoped-override analysis behind session-level guidance),
  `specs/visualization-server-in-chosen-language.md` (INV-090 — why Truth Set visualization is
  re-rated)

## Invariants introduced

- `INV-138` — The nudge MUST compare the stage's recommendation against the model/effort the
  Bootcamper is **currently running** (previous stage only as a fallback); a match presents the
  statement and asks nothing, a difference asks in either direction and names only the dial that
  differs (recorded in `specs/INVARIANTS.md`; supersedes INV-137's trigger only).
- `INV-139` — A below-current recommendation MUST be identified as a step down **in the switch
  question**, stating it is a cost saving rather than a needed capability and that staying put costs
  nothing (recorded in `specs/INVARIANTS.md`).
- `INV-140` — Every stage the Bootcamp can run MUST have exactly one row in the per-stage table,
  including apparatus-exempt setup stages (recorded in `specs/INVARIANTS.md`).
- `INV-141` — A per-stage row MUST name exactly one model and one reasoning effort; conditional
  recommendations are forbidden (recorded in `specs/INVARIANTS.md`).
