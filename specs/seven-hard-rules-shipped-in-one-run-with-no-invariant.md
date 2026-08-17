# Seven hard rules shipped in one run with no invariant, because the run would not mint wording the maintainer had not approved

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`conformance.py rules` went from **1** hard-rule line in a section citing no invariant to **10**
in a single unattended session (2026-08-17), while the suite stayed green throughout. Two were
missing citations and were fixed during the audit; **seven are genuinely unregistered rules** —
durable ⛔/MUST guarantees now shipped in the plugin and recorded in no invariant:

| Site | Rule |
|---|---|
| `module-03b-truthset-visualization/visualization-api-reference.md:1007` | A graph node is colored by its whole source **set**, never by one member |
| `…:1023` | The palette MUST be allocated in a single pass over the full key set |
| `…:1027` | The legend MUST name each combination it colors |
| `…:1043` | The visualization server MUST bind the loopback interface explicitly, never the wildcard |
| `…:1060` | A successful bind is NOT proof the port was free |
| `…:1066` | The server MUST confirm, before handing over the URL, that the process answering `/api/stats` is the one it started |
| `module-05-data-quality-mapping/phase1-quality-assessment.md:706` | Every named cross-source pair carries `measured` or `candidate, overlap unmeasured` |

⚠️ **This is the exact reverse-direction defect the audit exists to catch**, and the audit caught
it — but on the audit's own session's work, one round later than ideal. `INVARIANTS.md`'s reverse
contract is stated plainly: a change that ships a durable rule and registers no invariant leaves
the guarantee in the product and nowhere in the ruleset, so nothing binds future work to it and
nothing notices when a later change contradicts it. INV-134 and INV-155 are the two precedents,
and both cost weeks.

## Root cause

**A deliberate policy, applied consistently, with an unaccounted-for side effect.**

`implement-spec` requires the maintainer's sign-off before an invariant is recorded (*"Never record
an invariant the maintainer has not agreed to"*). The 2026-08-17 run was unattended, so it adopted
the rule: **where a spec drafts the invariant wording, mint it verbatim; where the wording would be
the implementer's own, do not mint — report it as a candidate.** That produced INV-253 through
INV-258 (all spec-drafted) and correctly declined to invent others.

⛔ **What the policy did not account for is that declining to mint does not decline to ship.** Seven
of the eighteen implementations shipped hard rules anyway — the rules were the fix — so the run
created exactly the unregistered-guarantee state the reverse contract forbids, while believing it
was being conservative. The conservative-looking half (no unapproved invariant) and the unsafe half
(an unregistered shipped rule) were the same decision.

Verified: `coverage_reports.py shipped` is clean and `citations.py verify` is clean at 257
invariants, so nothing dangles — the guarantees are simply absent from the ruleset rather than
mis-cited. `conformance.py rules` is the only report that can see this class, which is why it is the
one that moved.

**No Senzing fact is involved.** All seven rules govern the plugin's own artifacts — a rendering
encoding, a socket bind, a report's labels. Server **1.32.9** was reachable throughout the session
and every Senzing claim made during it was re-asked at the time (INV-080); none of that bears on
this finding.

## Proposed change

1. **Register the three subjects as invariants, with the maintainer's sign-off on the wording.**
   Drafts below, for approval — not to be recorded until approved. Three, not seven: the seven
   lines are three rules stated at their points of use.

   > **Graph source encoding.** A graph node's visual encoding — fill, stroke and stroke width
   > alike — MUST derive from the entity's whole **set** of data sources, joined and sorted, never
   > from one member of it; the palette MUST be allocated in a single pass over every source and
   > every observed combination together; and any combination color the graph draws MUST be named
   > in the legend. A single-source entity degenerates to its own source code, which is what makes
   > the rule backward-compatible. ⛔ Coloring by the first source renders every cross-source
   > entity as single-source under a legend that says so, and it is invisible on a dataset whose
   > entities mostly sit in one source.

   > **Visualization server binding and identity.** A visualization server MUST bind the loopback
   > interface explicitly and MUST NOT bind the wildcard address, and MUST confirm — before its URL
   > is handed to the Bootcamper — that the process answering `/api/stats` is the one just started,
   > by comparing a per-process nonce rather than any figure two runs of the same project would
   > agree on. A disagreement stops the step and reports the conflict; it MUST NOT degrade to a
   > warning above a working link. ⛔ A successful bind is not proof the port was free: a wildcard
   > bind coexists with an existing loopback listener, and either process may then answer.

   > **A prediction carries its evidence or its absence.** Where shipped guidance has the guide
   > write a prediction into a Bootcamper-facing deliverable, every predicted item MUST be labeled
   > either **measured** — with the measurement named — or explicitly **unmeasured**. A grouped or
   > aggregate score is not a measurement of a per-member claim.

2. **Record the policy gap in `implement-spec`**, so the next unattended run does not repeat it:
   an implementation that ships a hard rule owes an invariant *or* an explicit deferral recorded in
   the ledger entry, and "the wording would be mine" is a reason to **flag loudly**, not a reason to
   let the rule ship unregistered and unmentioned.

3. ⚠️ **Do not weaken `conformance.py rules` to make this pass.** It found the defect on the day it
   was introduced, having previously sat at 1 for weeks. It is working.

## Acceptance criteria

- [ ] The three invariants are recorded in `specs/INVARIANTS.md` with the maintainer's approved
      wording, each with its index entry in the same edit, next unused IDs, and provenance.
- [ ] All seven sites cite the invariant that governs them, and `conformance.py rules` returns to
      its pre-session baseline of **1** (the known-triaged `phaseB-load-first-source.md:23`).
- [ ] `implement-spec` states that shipping a hard rule without registering an invariant requires an
      explicit, recorded deferral — never silence.
- [ ] `coverage_reports.py shipped` stays clean: each new invariant naming a shipped artifact is
      cited in shipped text.
- [ ] No existing invariant is renumbered, reworded in place, or deleted (`INVARIANTS.md` rule 2).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — all
      three subjects are stated as behavior in the any-language contract already.

## Affected files

- `specs/INVARIANTS.md` — three new invariants, appended, plus index entries.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — citations at the six sites.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  citation at `:706`.
- `.claude/skills/implement-spec/SKILL.md` — the recorded-deferral rule.

## Source

- Feedback: none — found by `production-readiness-audit`, 2026-08-17, on the same session's own
  work (`Source: self-observed (assistant retrospective)`).
- Priority: **Medium.** Nothing is broken for a Bootcamper today; all seven rules are shipped,
  guarded by tests, and correct. The exposure is the one the reverse contract names: a later change
  can contradict any of them and nothing will notice, and the two precedents on record each stood
  wrong for weeks.
- MCP re-check: **n/a (no Senzing fact).** All seven rules govern plugin-owned artifacts. Server
  **1.32.9** (`get_capabilities`, 2026-08-17) reachable this session; no claim here depends on it.
- Upstream: not applicable — internal to the plugin.
- Related specs: `specs/graph-nodes-are-colored-by-their-first-data-source.md`,
  `specs/the-viz-contract-never-states-the-bind-host-so-a-port-conflict-can-succeed.md`,
  `specs/a-shared-feature-group-is-read-as-a-shared-attribute-when-predicting-joins.md` (the three
  implementations that shipped these rules), and the two precedents the reverse contract cites,
  INV-134 and INV-155.

## Why this is worth one spec rather than three

The three subjects are unrelated as rules and identical as a **failure mode**: each is an
implementation whose fix *was* a hard rule, shipped by a run that had decided not to mint invariant
wording it could not get approved. Filing three specs would record three rules and lose the reason
all three happened in one session — which is the part that will recur, because the next unattended
run inherits the same constraint and the same reasonable-looking policy.

## Invariants introduced

- `INV-259` — A graph node's visual encoding (fill, stroke and stroke width) MUST derive from the
  entity's whole sorted **set** of data sources; the palette MUST be allocated in a single pass over
  every source and every observed combination; every combination color drawn MUST be named in the
  legend. (Recorded in `specs/INVARIANTS.md`, indexed under *Visualization and screenshots*.)
- `INV-260` — A visualization server MUST bind the loopback interface explicitly, never the
  wildcard, and MUST confirm before handing over its URL that the process answering `/api/stats` is
  the one just started, by comparing a per-process nonce; a disagreement stops rather than warns.
  (Indexed under *Visualization and screenshots*.)
- `INV-261` — A named cross-source join prediction in a Bootcamper-facing deliverable MUST be
  labeled `measured` — backed by a count of distinct values shared on the named attribute — or
  explicitly `candidate, overlap unmeasured`. (Indexed under *Data quality, mapping and validation
  gates*.)

## Deviations from this spec, and why (2026-08-17)

1. ⛔ **The third invariant was NARROWED before recording, on the maintainer's decision.** This spec
   drafted it as *"Where shipped guidance has the guide write a prediction into a Bootcamper-facing
   deliverable…"* — general to all predictions. As recorded, `INV-261` is scoped to **cross-source
   join predictions** specifically. The reason: the general form would bind recap prose, discoveries
   reports and quality summaries, none of which produced the evidence, and a rule cited far from its
   evidence is the shape that gets re-argued. The narrowed rule still covers the reported defect in
   full. The first two were recorded as drafted.

2. **The invariant entries were kept deliberately lean.** The same session's earlier work expanded
   spec-drafted wording by 1.6x–12.3x with added rationale; the maintainer flagged that, so these
   three carry the drafted rule, one dated observation, the enforcing test, and provenance — nothing
   further.

3. **Each of the three guards already existed** — they were written when the rules shipped, before
   the invariants were registered — so no new test was needed. Each gained a back-citation to its
   invariant, which `tests/test_invariant_enforcer_citations.py` requires, and `EXPECTED_PAIRS` rose
   73 → 76.

4. ⚠️ **The `implement-spec` guardrail (proposed change 2) was added during the audit itself**, ahead
   of this spec being implemented, because the next unattended run would otherwise inherit the same
   gap. It is recorded in the `production-readiness-audit-2026-08-17` ledger entry.
