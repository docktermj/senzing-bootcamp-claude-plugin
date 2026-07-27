# Make the production-volume question unambiguous, echo its consequence, and lower the threaded-loader cutover

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Data processing Phase A step 1 asks:

> 👉 **How many records do you expect to load in a production system?**

Nothing in the question distinguishes the bootcamper's eventual production volume from the dataset they
are actively working with. Mid-bootcamp, with 4,000 records freshly mapped and about to be loaded, the
natural reading is "how many records are we loading?" — so the bootcamper may answer with the bootcamp
number instead of their real production target.

**This is not a cosmetic ambiguity — the answer silently selects the loader's architecture.** A
bootcamper who reads the question as being about the bootcamp answers ~4,000, lands in the `small` tier,
and receives a **single-threaded** loader. Per the Senzing anti-patterns documentation the feedback
retrieved via MCP (`search_docs(query="loading", category="anti_patterns")`, "Senzing Anti-Patterns:
Architecture and Performance"), that outcome is named explicitly:

> "Do Not Use Single-Threaded Loading — Symptoms: Very slow loading, CPU utilization far below capacity,
> loading takes hours or days when it should take minutes, only one core being used."

The bootcamper then takes that program home as their reference implementation. A misread of one question
yields a loader that embodies a documented anti-pattern, with no warning at any point.

In their words: "A load job for a small number of records is built differently from one for a
medium-to-large production system. That is what the question is really about — and the question does not
say so." The loading program is one of the bootcamp's take-home deliverables.

**Secondary finding, independent of wording.** The `small` tier spans **500 to 500,000** records and
still receives the single-threaded scaffold. Single-threaded loading at 500K records contradicts the same
anti-pattern guidance, so the thread-pool cutover appears to be set too high.

## Root cause

**Confirmed, both halves.**

**The question, `phaseA-build-loading.md:40-49`:**

```
## 1. Assess production record volume

👉 **How many records do you expect to load in a production system?**

Example ranges to help answer:

1. Fewer than 500, demo/evaluation
2. 500 to 500,000, small production
3. 500,000 to 10,000,000, medium production
4. 10,000,000+, large production
```

The phrase "in a production system" is the only disambiguator, and it reads as scene-setting rather than
as a contrast with the exercise. The question never states that the answer changes what gets built. The
architectural consequence *is* documented — but at `:104-113`, for the assistant, and it is never
surfaced to the bootcamper, so they cannot tell the answer matters beyond bookkeeping.

**The branch, `phaseA-build-loading.md:104-113`:**

| Tier | Scaffold |
|---|---|
| `medium` / `large` | `generate_scaffold(…, record_count=<raw_value>)` → **threaded** loading |
| `demo` / `small` / missing | `generate_scaffold(…)` without `record_count` → **single-threaded** |

So the `small` tier — up to 500,000 records — gets the single-threaded path, exactly as reported.

Note the tier boundaries are also **overlapping** as written at `:46-48` and `:53-54`: "500 to 500,000"
then "500,000 to 10,000,000", with 500,000 in both. Worth fixing while in the file.

## Proposed change

1. **Rewrite the pinned question** to separate production from the bootcamp and to state that the answer
   changes the architecture. Keep it a single pinned 👉 question with one meaning (INV-005/INV-008/
   INV-056). Substance to carry, adapted from the bootcamper's own draft:

   > 👉 **In production — not in this bootcamp — how many records do you expect to load?**
   >
   > This is about the system you're ultimately building, **not** the records we're using here. It
   > changes the loading program's *architecture*: a demo loader and a 50-million-record loader are
   > genuinely different programs (single-threaded vs thread-pooled, batching, checkpoint/resume,
   > throughput instrumentation, queue-based distribution). Answer for your real target volume even if
   > it dwarfs the bootcamp dataset.
   >
   > 1. Fewer than 500 — demo/evaluation
   > 2. 500 to 500,000 — small production
   > 3. 500,000 to 10,000,000 — medium production
   > 4. 10,000,000+ — large production
   >
   > Not sure yet? Give your best estimate — we'll build for that, and it can be revisited.

   Do **not** hardcode the bootcamp's record count into the pinned text (the draft's "the 4,000 records
   we're using here"); reference it dynamically or omit the number, or the pinned wording goes stale.
2. **Echo the consequence back after they answer** — e.g. "Medium production, so I'll build a
   thread-pooled loader with batching and checkpoint/resume." A misread then surfaces immediately, while
   correcting it is free, instead of being discovered when the loader is already written. This is the
   cheapest half of the fix and the one that actually catches the error.
3. **Lower the threaded-scaffold cutover** so no realistic production volume receives a single-threaded
   loader. Set the boundary well below 500,000. **Determine the specific threshold from the Senzing MCP
   server at implementation time** (`search_docs` on loading/anti-patterns and `generate_scaffold`'s own
   guidance) rather than from this spec or from training data — the plugin's MCP-grounding rule applies,
   and a threshold asserted here would be exactly the kind of unsourced Senzing specific the plugin
   forbids. Options to weigh: move `small` to the threaded branch outright, or split `small` at the
   MCP-sourced threshold.
4. **Fix the overlapping tier boundaries** at `:46-48` and `:53-54` so 500,000 and 10,000,000 each fall
   in exactly one tier.
5. **Keep the existing license framing intact.** `phaseA-build-loading.md:64-72` deliberately presents
   licensing as a default with expansion paths "before any mention of downsizing". A larger stated
   production volume must not turn into a downsizing conversation — that ordering was set by
   `specs/single-license-gate-at-data-processing.md` and must survive this change.
6. **Revisit the SQLite volume pre-load check** at `phaseA-build-loading.md:182-190`, which prompts only
   when the tier is `medium` or `large`. If the threaded cutover moves, confirm this check's trigger
   still matches the intent (warn when a production-scale volume meets a demo-scale datastore) rather
   than silently drifting out of step with the new boundary.

## Acceptance criteria

- [ ] The pinned question explicitly contrasts production with the bootcamp and states that the answer
      changes the loading program's architecture; it remains a single 👉 question with one meaning
      (INV-005/INV-008/INV-009/INV-056).
- [ ] The pinned wording contains no hardcoded bootcamp record count.
- [ ] After the answer, the assistant echoes the selected tier **and** the architecture it implies,
      before any code is generated.
- [ ] No tier that represents a realistic production volume receives the single-threaded scaffold; the
      chosen cutover is sourced from the Senzing MCP server this session and cited in the skill file.
- [ ] Tier boundaries are non-overlapping across both the question text and the classification logic.
- [ ] The license framing still presents expansion paths before downsizing.
- [ ] The SQLite volume pre-load check's trigger is consistent with the new cutover.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the threaded
      vs single-threaded distinction is expressed through `generate_scaffold`'s `record_count` parameter
      in the bootcamper's chosen language, not through any language-specific threading construct
      described in the skill.

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — the pinned
  question and ranges (lines ~40-49), the classification (lines ~53-59), the volume-aware scaffold branch
  (lines ~104-113), and the SQLite volume pre-load check (lines ~182-190)

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Clarify that the production-volume question is
  about PRODUCTION, not the bootcamp" (2026-07-24, Data processing Phase A step 1)
- Priority: Medium
- Related specs: `specs/single-license-gate-at-data-processing.md` (the license framing that must
  survive), `specs/pin-remaining-interaction-questions.md` (pinned-question requirements),
  `specs/post-load-match-key-semantic-audit.md` (the other Phase A/D take-home-quality gap),
  `specs/mcp-grounding-in-every-skill.md`
