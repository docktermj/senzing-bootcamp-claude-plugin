# INV-077's supersession dropped the visualization's verification guarantee

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`ground-rules.md:375` warns the guide about an `internal://` connection string by naming the
failure it causes:

> Adopting it is silent: every load reports success, and the visualization then renders an empty
> graph three modules later with nothing naming the cause **(the blank-render failure INV-077
> exists to prevent)**.

**INV-077 does not exist to prevent that.** Its condition is about *delivery and selection*:

> The guaranteed Truth Set web-app visualization is delivered by the selectable "Truth Set
> visualization" module … it MUST be produced whenever that module is selected (always in Core; in
> Customized only if chosen); when it is not selected, no workstation-verification visualization is
> produced.

An empty graph satisfies INV-077 completely. The module ran, the visualization was produced. The
invariant has nothing to say about whether anything is *in* it.

**The guarantee the citation is reaching for is real, but it is superseded.** It lived in INV-038:

> The Bootcamper **ALWAYS** sees a dynamic web-app visualization of the Truth Set **to verify that
> Senzing works on the Bootcamper's workstation**. (Superseded by INV-077…)

That trailing purpose clause — *to verify that Senzing works* — is what makes a blank render a
violation, and it is the half INV-077 did not carry forward. INV-077 kept "which module, and when",
and dropped "and it must actually demonstrate the thing".

## Root cause

**A supersession narrowed an invariant and nothing recorded the narrowing.** INV-077 was written to
settle *where the visualization lives* after `split-truthset-visualization-into-standalone-module`
moved it. It correctly supersedes INV-038's delivery clause. It silently also retired INV-038's
**purpose** clause, which no live invariant now carries.

Verified by sweeping every invariant mentioning the visualization: **INV-038 is the only one whose
text contains "verify that Senzing works", and it is marked superseded.** The live visualization
invariants govern placement (INV-070), offline rendering (INV-091, superseding INV-071), tab set
(INV-155), suppression (INV-232), colour sourcing (INV-127), legibility (INV-154), capture and
embedding (INV-122, INV-123, INV-146, INV-147) — every one of them about *how it renders or is
captured*, none about *whether it contains the bootcamper's resolved data*.

⚠️ **A second site is anchored to the same superseded invariant.** The implemented spec
`fix-truthset-snapshot-empty` — whose entire subject is a visualization that came out empty —
records **INV-038** as the invariant it establishes. So the one spec that exists precisely to stop
a blank visualization is bound to a rule marked superseded by one that permits it.

⛔ **Why this class is worse than an ordinary wrong citation.** `citations.py verify` passes: INV-077
exists, so the reference resolves. A reader who follows it lands on a real invariant that reads
authoritative and is about visualizations. Nothing in the toolchain can see that the *clause being
relied on* is not in it — which is the INV-134/INV-155 shape this audit's own charter names, and the
reason the reverse sweep is done by reading.

## What this is not

**Not a proposal to un-supersede INV-038.** `INVARIANTS.md` is append-only and a superseded
invariant stays marked. The remedy is a live invariant carrying the retired clause, plus a corrected
citation — never editing INV-077's condition or reviving INV-038.

**Not a claim that the plugin renders blank visualizations today.** No such failure was observed
this run; the shipped guidance at `ground-rules.md:366-376` correctly forbids the `internal://`
connection string that causes it, and does so with the server's own reasoning quoted. What is
missing is the *rule* the guidance cites as its authority.

## Proposed change

1. **Register the retired clause as a live invariant.** Draft for the maintainer's sign-off:

   > The Truth Set visualization, whenever it is produced (INV-077), MUST render the Bootcamper's
   > actually-resolved data — a visualization that opens with an empty graph is a failure, not a
   > success, and MUST be reported as one rather than presented as the verification step passing.

   This restores INV-038's purpose clause as a condition INV-077 can be cited alongside, without
   touching either existing entry.

2. **Correct `ground-rules.md:375`** to cite the new invariant rather than INV-077 for the
   blank-render failure. INV-077 may stay in the sentence for *which* visualization is meant; it is
   the "exists to prevent" attribution that is wrong.

3. **Re-anchor `fix-truthset-snapshot-empty`'s ledger entry** to the new invariant, with a dated
   note saying its original INV-038 anchor was superseded. ⛔ Append, never rewrite — the ledger
   records what was decided.

4. **The class sweep was run, and this is the only instance — the class is narrower than it
   looks.** Scanning shipped text for citations of any invariant marked superseded returns **26
   hits across 12 files**, and **all 26 are correct on reading.** They fall into two groups, both
   legitimate:

   - **Prose that names the supersession** — `model-selection.md:140`, `onboarding-flow.md:126`,
     `bootcamp-preparation/SKILL.md:231-232`, `module-07/SKILL.md:94`. These *describe* the chain;
     citing the retired ID is the point.
   - **"Superseded then restored"** — the ~14 INV-063/INV-069 module-start citations. INV-063 →
     INV-119 → INV-137, and **INV-137 restored the unconditional behaviour**; INV-063's own entry
     says so ("the behavior described here is once again the behavior, with no preference gating
     it"). `INVARIANTS.md`'s index defines this form explicitly and instructs **"Read it — for
     several of these the invariant is still the only statement of what it requires."**

   ⛔ **So a guard on "shipped text cites a superseded invariant" would be wrong**: it fires on 26
   correct citations and would pressure an implementer into breaking them. What distinguishes
   INV-038 is that it is **fully** superseded, the superseding invariant **dropped** a clause
   rather than restating or restoring it, and shipped text cites the successor **for the dropped
   clause**. That conjunction is what a guard would have to detect, and detecting "which clause
   was dropped" is a semantic judgement, not a scan.

## Acceptance criteria

- [ ] A live invariant states that the Truth Set visualization must render the Bootcamper's
      resolved data, and that an empty render is a reported failure — worded and **approved by the
      maintainer**, with its index entry in the same edit.
- [ ] `ground-rules.md` no longer attributes the blank-render guarantee to INV-077.
- [ ] No existing invariant's condition text was edited, and INV-038 remains marked superseded.
- [ ] `fix-truthset-snapshot-empty`'s entry records the re-anchoring, by append.
- [ ] A guard asserts that `ground-rules.md`'s blank-render sentence cites the **new** invariant
      and not INV-077 — **negative-controlled**, mutation verified to land, then reverted.
- [ ] ⛔ **No guard is written for "shipped text cites a superseded invariant."** The sweep in
      `## Proposed change` item 4 found 26 such citations and every one is correct, so that guard
      would fail on valid content. If a guard for this class is wanted at all, it must key on the
      narrower conjunction described there — and whether a superseding invariant *dropped* a clause
      is a semantic judgement no scan settles.
- [ ] ⛔ Not runtime-verified: whether a live engine actually produces a populated graph. That needs
      `libSz.so` and loaded data, absent from this environment. The guard asserts the rule exists
      and is cited correctly, never that a render succeeds.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — one new invariant, appended, plus its index entry. **No existing entry
  edited.**
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — `:375`, the attribution.
- `specs/IMPLEMENTED.md` — `fix-truthset-snapshot-empty`'s entry, appended note.
- `tests/` — one new guard for the superseded-citation class.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15j
  (`Source: self-observed (assistant retrospective)`). Found by reading citations against their
  invariants in `ground-rules.md` — the **defect class 5 sweep that audit 2026-08-15i attempted
  mechanically, failed at, and disclosed as unaudited.** Seven of the file's 93 citations were read
  (the highest-risk subset: low-numbered general invariants cited for specific claims); one is
  wrong. ⚠️ **The other 86 remain unread.**
- Priority: **Medium-High.** No bootcamper is harmed today — the guidance that prevents the failure
  is correct and present. But the rule it cites as its authority does not say what it claims, so a
  later editor reconciling the two would be right to weaken the guidance, and the guarantee that
  the verification step actually verifies anything is registered nowhere.
- MCP re-check: **n/a (no Senzing fact).** The finding is internal: an invariant's text against a
  citation of it, and a supersession chain within `INVARIANTS.md`. No Senzing claim is asserted and
  no absence about the server is relied on. Server **1.32.9** (`get_capabilities`, 2026-08-15)
  recorded earlier this session to date the run.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `fix-truthset-snapshot-empty` (anchored to the superseded INV-038),
  `split-truthset-visualization-into-standalone-module` (the move INV-077 was written to settle),
  `customizable-module-selection` (INV-077's source),
  `generalized-invariants-leave-no-pointer-on-the-narrower-rule` and
  `invariants-index-flattens-partial-supersession` (the same supersession-bookkeeping class), and
  INV-038, INV-070, INV-077, INV-091, INV-246.

## Invariants introduced

- `INV-250` — The Truth Set visualization step MUST NOT present an **empty** visualization as the
  workstation-verification step passing; where the visualization renders no entities, the step
  reports that as a failure and names the likely cause. (Recorded in `specs/INVARIANTS.md`,
  indexed under *Visualization and screenshots*.)

## Deviations from this spec, and why (2026-08-15)

- ⚠️ **The maintainer chose the report-only wording over the two alternatives this spec drafted**,
  2026-08-15. INV-250 binds the **step's reporting** and deliberately does **not** mandate a
  detection mechanism: a detect-and-confirm form cannot be verified offline (INV-108), and a
  criterion nobody can run is worse than a narrower rule that holds. The rejected third option —
  re-registering INV-038's clause verbatim — was a purpose rather than a testable MUST, which is
  the shape that let it be dropped unnoticed in the first place.
- ⛔ **The class is THREE live sites, not the one this spec claimed.** `## Proposed change` item 4
  reported the sweep as finding a single instance — but that sweep scanned `plugins/` only, and
  saying so in the spec did not make the scope correct. Re-run across `tests/` and `specs/`, the
  same misattribution also sat in **`tests/test_internal_connection_string_rejected.py:33`**
  (*"the outcome INV-077 forbids"*) and its assertion message at `:131`. Both corrected here, the
  docstring carrying a dated note saying what it previously read. A fourth instance lives in
  `specs/internal-connection-string-breaks-the-viz-server.md:43` and was **left alone**: it is an
  implemented spec's historical record, and correcting spec content is `feedback-to-specs`' job.
- **The step names the cause without writing `internal://`.** The drafted text used the literal,
  which reddened `test_no_file_offers_internal_connection_string` — an existing guard that permits
  **exactly one** mention of the scheme, in `ground-rules.md`, because forbidding it requires
  naming it. That design is deliberate and older than this spec, so the step describes the cause
  by its property and cites **INV-231** instead, pointing at the ground rules for the scheme
  itself. The guard's assertion was re-scoped to match.
- **`tests/test_invariant_enforcer_citations.py` needed `EXPECTED_PAIRS` 62 → 63**, because
  INV-250 names its enforcing test and that file counts invariant→test pairs deliberately.
- ⛔ **A guard assertion failed for the wrong reason and was made non-vacuous.** The index check
  first sliced `INVARIANTS.md` between literal boundaries that do not exist — the index is an
  `###` under a `##`, so the slice came out **empty** and the assertion failed as if INV-250 were
  missing. It now slices to the append marker and asserts the slice is non-trivial first, so a
  collapsed slice can never read as a passing or failing verdict about the index.
- **Not runtime-verified, exactly as the spec's criterion states.** Whether a live render is
  non-empty needs `libSz.so` and loaded data, absent here. Seven mutations prove the rule ships and
  is cited where it binds; none proves a bootcamper saw a populated graph. `dry-run` is owed.
