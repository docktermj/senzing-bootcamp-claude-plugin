# The no-fork discipline is stated at ~40 sites and registered only inside INV-183's artifact scope

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The plugin relies everywhere on one rule: **a procedure is stated once, and every other place
points at it rather than carrying a copy.** Measured 2026-09-03 across shipped guidance, that
discipline is asserted at roughly **forty** sites — *"do not restate it here"*, *"this is the
canonical statement"*, *"follow it there rather than re-deriving it"*, *"so the two cannot drift
apart"*.

**Twenty-seven of them cite no invariant at all.** The eight that do cite **INV-183**, whose
registered scope is narrower than the use:

> A step that instructs the guide to **generate a bootcamper-facing artifact** MUST, at that
> step, name every rule governing how the artifact is produced — or cite the file that states
> it — and MUST NOT rely on a rule stated only elsewhere. … The rule MUST be **named and
> linked, never restated or forked** at the step (INV-080's no-fork discipline), so one
> statement of record stays authoritative.

The no-fork clause lives **inside** the artifact-generation rule. So at a site that generates
no artifact — a server launch, an SDK error branch, a license reconciliation, a pinned
question's wording — INV-183 is cited for a clause whose enclosing scope does not reach it.

⛔ **This is a reverse-contract gap, not a citation error.** The rule is real, the plugin
depends on it, `bootcamp-preparation/SKILL.md:225` even records *why* — *"two copies is how
this drifted in the first place"* — and nothing in `specs/INVARIANTS.md` binds it. Nothing
notices when a later edit forks a procedure into a second copy, which is precisely the failure
the twenty-seven sites are each individually guarding against by hand.

## Root cause

The discipline was never registered on its own, because every time it came up it was **beside**
something that was registered. INV-183 covered it for generated artifacts, which is where the
first instances appeared, and later sites reached for the nearest available id or for none.

**Two facts make the scope stretch pre-existing rather than introduced:**

- `module-05-data-quality-mapping/phase2-data-mapping.md:245` — *"Step 10 owns that question's
  wording — it is pinned there and is not restated here, so the two cannot drift apart
  (INV-183)"* — is about a **pinned question**, not an artifact, and predates this spec.
- `inv-179-is-cited-as-a-state-it-once-rule-it-does-not-contain` (2026-09-03) repointed seven
  sites from INV-179 to INV-183 the same day. That was a strict improvement — INV-179 is about
  SDK response flags and had nothing to do with the subject — but it moved those sites from
  *wrong invariant* to *right invariant, scope stretched*, which is what surfaced this gap.
  ⚠️ **Four of those seven generate no artifact**: `phase1-verification.md:454` (an SDK error
  branch), `phaseA-build-loading.md:103` (license reconciliation),
  `visualization-api-reference.md:1121` (a server launch), and — borderline —
  `module-04-data-collection/SKILL.md:288` (a quality-band table).

## Proposed change

1. **Register a new invariant** for the discipline itself, extending INV-183's no-fork clause
   beyond artifact generation. ⛔ **Never amend INV-183 in place** — `INVARIANTS.md` forbids
   changing an invariant's meaning in place, and a widening needs its own id that extends it
   (the INV-268-extends-INV-132 precedent). Drafted wording is in `## Invariants introduced`
   below and **requires maintainer-approved wording before implementation.**
2. **Cite the new id at the sites that rely on the rule**, deriving the set **by scanning**
   (INV-246) rather than from this spec's list — which is where the author noticed it, not the
   extent. Keep INV-183 where the site really is an artifact-generating step; the two are
   complementary, not alternatives.
3. **Guard the property, not the phrasings.** A test asserting that a passage which claims a
   rule is stated once elsewhere carries an authority for that claim. ⚠️ The vocabulary is open
   ("canonical statement", "do not restate", "cannot drift apart", "point at it"), so a
   phrase-list matcher will under-report; state that limit in the guard rather than implying
   completeness, and derive the site set by scanning.
4. ⛔ **Do not "fix" this by deleting the twenty-seven claims.** Each is a real instruction
   against a real drift, and the reason clauses (`bootcamp-preparation/SKILL.md:225`) are what
   stop the rule being re-argued.

## Invariants introduced

- ✅ **`INV-300` — REGISTERED, approved by the maintainer 2026-09-03** (verdict: *register as drafted*, narrow scope). Recorded in `specs/INVARIANTS.md` with its index entry in the same edit, cited at 38 shipped sites, and enforced by `tests/test_a_single_statement_claim_names_its_authority.py`, which cites it back. The approved wording, which is what INVARIANTS.md now carries as the authority:

  > Where shipped guidance states that a rule, procedure or question's wording is **owned by
  > one place** — *"stated once"*, *"the canonical statement"*, *"do not restate it here"*,
  > *"cite it rather than restating it"* — that claim MUST name the owning file or step **and**
  > the invariant that makes single-statement authoritative, and the pointing site MUST carry
  > no second copy of the rule it points at. This binds whatever the rule governs: an
  > artifact-generating step (where **INV-183** states it and continues to govern), an SDK
  > error branch, a platform hazard, a license reconciliation, or a pinned question's wording.
  > A copy that drifts is undetectable by construction — the duplication scan reports **exact**
  > repeats, so two statements that have stopped matching are precisely what it cannot see.

  ⚠️ **Scope question the maintainer should settle before approving:** whether this binds only
  a site that *claims* single-statement ownership (the drafted form, ~40 sites, mechanically
  findable) or every passage that *could* have restated a rule and did not (unbounded, and not
  checkable). The narrow form is drafted deliberately.

## Acceptance criteria

- [ ] A new invariant registers the discipline, approved by the maintainer, appended with its
      index entry in the same edit; INV-183 is unchanged and still governs artifact-generating
      steps.
- [ ] Every shipped site claiming a rule is stated once elsewhere cites an authority — the new
      id, or INV-183 where the step generates an artifact — with the site set derived by
      scanning, not from this spec's list.
- [ ] The four sites named above as generating no artifact no longer rest on INV-183 alone.
- [ ] A guard asserts the property, states what its vocabulary cannot see, and is
      negative-controlled by removing one citation.
- [ ] `citations.py verify` clean; `coverage_reports.py shipped` reports the new id as cited in
      shipped text; full suite green.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — the new invariant plus its index entry, in one edit
- the shipped sites the scan finds — at minimum `module-03-system-verification/phase1-verification.md`,
  `module-04-data-collection/SKILL.md`, `module-06-data-processing/phaseA-build-loading.md`
  and `phaseB-load-first-source.md`, `module-07-query-visualize-discover/phase1-query-visualize.md`,
  `module-03b-truthset-visualization/{SKILL.md,phase1-visualization.md,phase2-close.md,visualization-api-reference.md}`,
  `module-05-data-quality-mapping/{phase2-data-mapping.md,phase3-test-load.md}`,
  `module-02-sdk-setup/SKILL.md`, `bootcamp-preparation/SKILL.md`,
  `bootcamp-onboarding/{ground-rules.md,module-completion.md}`, `graduation/SKILL.md`
- `tests/` — one new guard

## Source

- Feedback: none — self-observed during `production-readiness-audit-2026-09-03c`, cycle 1 of the
  unattended loop (`Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: **n/a (no Senzing fact).** The subject is which of the plugin's own invariants
  governs one of its own authoring disciplines. No Senzing claim is asserted (INV-080).
- Upstream: not applicable
- Related specs: `specs/inv-179-is-cited-as-a-state-it-once-rule-it-does-not-contain.md`,
  `specs/the-one-question-per-turn-rule-is-registered-nowhere.md`,
  `specs/the-2026-08-21-run-shipped-three-unregistered-guarantees.md`

## Blocked (unattended run 2026-09-03)

**Blocked on the maintainer's sign-off of an invariant's wording, which an unattended run may
not give.** `implement-spec` Step 5 reserves that decision, and `unattended-spec-loop` restates
it: an invariant is permanent and binds every future spec.

⛔ **Nothing partial was implementable, and that is worth stating rather than leaving as an
apparent omission.** All three remaining proposed changes depend on the id existing:

- **Change 2** cites the new id at the sites — unwritable before it is minted, which is the
  precise trap `implement-spec` records for 2026-08-14: eight implementations shipped their
  rules with no ids, the ids were minted later in one commit, and nothing sent anyone back to
  the prose.
- **Change 3**'s guard asserts that a single-statement claim carries an authority. Twenty-seven
  sites carry none today, so the guard cannot be green before change 2 — and an assertion
  weakened to pass would be the one outcome worse than a red suite.
- **Change 1** *is* the sign-off.

⚠️ **This is not the ship-the-rule-and-defer case.** That path applies when an implementation
**ships** a hard rule with no invariant; here the rule already ships at ~40 sites and has for
months. Nothing new was written into the plugin, so there is no new guarantee to defer — the
deferral would be about text that is already there. The working tree was left clean; no partial
work to revert.

⛔ **`/review-invariants` will NOT show this draft, so do not read an empty queue as nothing
waiting.** `pending_invariants.py` reads `DEFERRED INVARIANT` blocks in
`specs/IMPLEMENTED.md`, and this draft is not one: a deferral records a **rule that already
shipped** with no invariant, whereas nothing was shipped here — the wording is a *proposal*
living in this spec. On 2026-09-03 that queue reported `pending: 0`, `held: 1` and a next free id of
**300** — written here without its prefix, for the reason given above — with this draft
outstanding, and both statements were true. ⚠️ Whether the review
queue should also read specs' `## Invariants introduced` sections for unminted ids is a
maintainer decision, not a defect this run should have decided.

### The question that unblocks it

👉 **Approve, amend, or reject the drafted wording in `## Invariants introduced` above — and
settle the scope question it names:** does the invariant bind only a site that **claims**
single-statement ownership (the drafted form: ~40 sites, mechanically findable), or every
passage that *could* have restated a rule and did not (unbounded, and not checkable)?

On approval: mint the next free id — **300** at the time of writing, 2026-09-03, and
⛔ **re-read it with `pending_invariants.py next-id` rather than trusting that number**, since
several drafts can compete for one id. ⚠️ The id is written here **without its `INV-` prefix on
purpose**: `citations.py verify` scans this tree for `INV-nnn` and an unminted one is a dangling
reference that fails the suite. This note carried the prefixed form for one commit and did
exactly that — see the dated correction on `production-readiness-audit-2026-09-03d`. Append the minted
invariant with its index entry in the same edit, then work change 2's site set **by scanning** — not from this
spec's list, which is where the author noticed the rule rather than its extent (INV-246).

## Deviations from this spec, and why (2026-09-03)

- ⛔ **The index group is NOT the one this spec implied, and the reason matters.** *The
  development record itself* is the intuitive home for an authoring rule, and it is **the
  exemption group** `coverage_reports.py shipped` uses: its own admission rule says *"its
  members bind the development environment, so an ID here is never expected to appear in a
  shipped file under `plugins/`. File a new invariant here only when that is true of it."*
  INV-300 must be cited in shipped text, so filing it there would have exempted it from the
  one check that notices an uncited rule. Filed instead in *Generator behavior* beside
  **INV-183**, on the INV-268-extends-INV-132 precedent: an extension lives with its parent.
- **Criterion 5's wording was wrong about `coverage_reports.py shipped`.** It asks for the
  report to *"report the new id as cited in shipped text"*; that report lists only invariants
  **missing** a citation, so the pass signal is INV-300's **absence** from its output — which
  is what it shows. Verified, criterion met in substance.
- ⚠️ **The scan found a claim my own reading had dismissed** — `phase2-data-mapping.md:1278`.
  Its sentence begins with code reuse (*"reuse this same reader in later modules rather than
  re-deriving one per module"*), which I classified as out of scope, and **ends** with an
  ownership claim (*"Full rationale, and the rule … are in `module-02-sdk-setup/SKILL.md` →
  'The launch environment'"*) carrying no citation. That is INV-246 landing on the person
  applying it: the site set came from scanning, and scanning is what caught what reading
  missed.
- **Two existing guards pinned the exact phrase the citation was inserted into** —
  `test_cord_fetch_integrity.py:63` (*"canonical statement; do not restate it elsewhere"*) and
  `test_sampling_and_validation_routing.py:60` (*"canonical statement; do not restate it
  here"*). The citation was moved **clear of** the pinned phrase rather than the guards being
  rescoped: the phrase they pin *is* the canonical-declaration wording, so preserving it is
  correct and the insertion point was the mistake. ⚠️ **Fourth syntax-pinned-guard collision
  in this session.**
- **Six candidate hits are exempted as not ownership claims**, each with its reason in the
  guard, and each exemption is asserted to still match real text — a stale exemption silently
  widens as prose changes.

## My own mistakes in this implementation, recorded (2026-09-03)

- ⛔ **The guard's first version was too weak, and its own negative control is what caught
  it.** The citation check accepted any `INV-\d+` in the passage, so deleting INV-300 from a
  claim left it green — a neighboring rule six lines away cited something unrelated. That is
  proximity substituting for governance, reproduced *inside* the guard written to prevent it.
  Tightened to `INV-(?:300|183)`, and re-controlled three ways: a removed citation, a
  neighbor's unrelated id, and a stale exemption. **The lesson is that the control fired only
  because it was run — a control that "should" fail proves nothing until it does.**
- **A failure message printed 1.3 MB of shipped markdown**, because `assertIn(phrase, corpus)`
  prints the haystack. Replaced with a boolean assertion that names the missing phrase.
- **A British spelling of *neighboring* went into the new test** — the `-our-` form — and was
  caught by INV-253's guard, not by me. ⚠️ Written here as a description rather than as the
  word itself: quoting it would need a `PER_FILE_WAIVERS` entry in
  `tests/test_us_english_spelling.py`, and that guard deliberately has no inline marker, so
  a quote costs a maintained word/count pair that fails as stale once the prose moves.
