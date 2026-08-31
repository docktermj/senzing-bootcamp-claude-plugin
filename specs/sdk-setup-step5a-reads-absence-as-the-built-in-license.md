# SDK setup Step 5a reads `license_record_limit`'s absence as "only the built-in evaluation license is active" — the exact inference INV-244 forbids

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

At SDK setup Step 5a, a Bootcamper with a real, uncapped license installed is told their limit is
500 records.

`module-02-sdk-setup/SKILL.md:1058-1080` branches on `config/bootcamp_progress.json`'s
`license_record_limit`: present → reconcile against a measurement; **absent → "Otherwise (only the
built-in evaluation license is active), present this briefly"**, followed by the pinned note:

> "Your Senzing SDK uses a **built-in evaluation license** automatically when no custom license is
> present (limited to {record limit} records) — no license file needed. That's enough for the demo
> modules that come next…"

Absence is the normal state at this point: the field's only writer is Module 4's Step 8a gate, which
has not run. Measured on this walk (Senzing 4.3.4-26210, Java 21.0.12, 2026-08-28), at Step 5a, in
the Bootcamper's chosen language, using the env script Step 3 had just written and the SDK Step 4 had
just verified:

```text
$ java -cp "$SENZING_SDK_JAR:src/verify" CheckLicense
{"customer":"Senzing Internal","contract":"Senzing Internal","issueDate":"2026-03-12",
 "licenseType":"EVAL (Solely for non-productive use)","licenseLevel":"STANDARD","billing":"YEARLY",
 "expireDate":"2027-03-12","recordLimit":0,"advSearch":0}

$ python3 -c "...; print('license_record_limit present?', 'license_record_limit' in d)"
license_record_limit present? False
```

`recordLimit: 0` — **no cap**. The step would state 500.

## Root cause

This is **INV-244's own worked example, at a second site.** That invariant reads:

> Where a bootcamp state field is written only **conditionally**, a step branching on it MUST NOT
> read that field's absence as a measured finding. […] On the walk that found it,
> `SzProduct.getLicense()` reported `recordLimit: 0` (no cap) while the field was absent, so the
> guide would relay a 500-record limit […] ⚠️ **The tell is a field whose writer is gated on
> something other than the question being asked.**

INV-244 was raised from Module 6 Phases A and B and is enforced by
`tests/test_module06_license_reconciliation.py` — a **Module-6-scoped** guard. SDK setup's Step 5a
has the identical shape and no guard reaches it, so the fix landed at one site and the pattern
survived at another.

Step 5a is in fact the *worst* site for it, because it is the first step where the measurement is
actually available: Step 4 verifies the SDK works one step earlier, and Step 3 writes the env script
that supplies the settings. INV-244's remedy clause applies verbatim — *"Where such a value is one
call away on this machine, the measured value governs the generic note (INV-012) and the step MUST
take that call rather than infer from silence."*

⚠️ **The step's existing ⛔ does not forbid the fix, and must not be read as forbidding it.**
`:1070-1073` says *"Never write this field when it is ABSENT"* (INV-244, INV-278). That governs
**writing the field**, and its stated reason is to keep a volume-gated measurement from becoming an
unconditional one. It says nothing about **measuring and presenting**, which is what INV-244's remedy
requires. The current text satisfies the write prohibition and then presents the unmeasured
assumption as fact, which is the half INV-244 actually forbids.

**Downstream consequence, observed on this walk.** Module 1 Step 5a had already compared the ~10,000
record scenario against the built-in 500 and set `license_guidance_deferred: true`. With Step 5a
leaving the real license unmeasured, Module 4's Step 8a gate then fires and asks a Bootcamper whose
license has **no cap** to supply a License Key, continue with a 500-record sample, or request an
evaluation license — three options, all premised on a limit they do not have. Note this is the
*opposite* polarity to INV-278's failure: there a too-high figure **suppressed** a needed gate; here
a too-low assumption **fires** an unneeded one and can shrink the dataset, under-demonstrating the
cross-source resolution Modules 6 and 7 exist to show.

## Proposed change

1. **Measure at Step 5a rather than inferring.** Replace the `Otherwise` branch's unconditional note
   with: take the license reading via the chosen language's product interface (`getLicense` /
   `get_license`) — available here because Step 4 has just verified the SDK — and present the
   measured `recordLimit`, rendering `0` as "no record cap (unlimited)", matching the wording the
   already-licensed guard directly above already uses.
2. **Keep the built-in-license note as the branch for a measurement that cannot run**, and state it
   as an assumption naming what could not be determined (INV-163/INV-244), never as a detected value.
3. ⚠️ **Whether the measured value is persisted to `license_record_limit` needs the maintainer's
   decision, and this spec does not settle it.** Persisting is the most useful outcome — it is a
   genuine measurement, which is the only thing the field's contract requires — but a recorded
   `0` **suppresses** Module 4's Step 8a gate, which is a change to that gate's semantics and
   therefore the maintainer's call, not an implementer's. The two options:
   - **Persist** — `license_record_limit: 0` is written; Module 4's gate correctly does not fire for
     an uncapped license. Requires re-reading INV-278's reconciliation clause and the ⛔ at `:1070`.
   - **Present only** — the ⛔ stays exactly as written, Step 5a states the measured figure, and
     Module 4 still performs its own measurement at its gate. Smaller change; the Bootcamper is told
     the truth here, and the redundant gate in Module 4 remains.
4. **Generalize the guard.** `tests/test_module06_license_reconciliation.py` proves the rule at one
   site. Add a test that scans **every** step branching on `license_record_limit` across the plugin
   and asserts none renders the absent branch as a detected finding — so a third site cannot repeat
   this.

## Acceptance criteria

- [ ] SDK setup Step 5a takes a license measurement rather than branching to the built-in note on
      absence, and presents `recordLimit: 0` as "no record cap (unlimited)".
- [ ] The built-in-evaluation note is reachable only when the measurement genuinely cannot run, and
      when presented it names itself as an assumption and states what could not be determined.
- [ ] The maintainer's decision on item 3 (persist vs. present-only) is recorded in the ledger entry,
      with the ⛔ at `SKILL.md:1070` either reworded or explicitly reaffirmed.
- [ ] A repo-level test enumerates every `license_record_limit` branch in `plugins/` and fails if any
      absent branch asserts a licensing finding (stdlib only, no `plugins/` import — INV-108),
      negative-controlled by reintroducing the Step 5a wording.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 5a's `Otherwise` branch and
  its pinned note (`:1058-1080`), and the ⛔ at `:1070-1073` if item 3 resolves to "persist"
- `tests/` — a plugin-wide guard over `license_record_limit` absent-branches
- `specs/INVARIANTS.md` — INV-244's enforcer list, if the new guard supersedes the Module-6-scoped one

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-28, in the **analysis stretch** at the
  maintainer-chosen start module (SDK setup), while executing Step 5a for real
  (`Source: self-observed (assistant retrospective)`). Surfaced only because this was the first
  phase-3 walk with a real Senzing install carrying a **non-default** license: with the built-in
  license the assumed and measured figures agree, and the branch looks correct.
- Priority: **High.** It states a false Senzing fact directly to the Bootcamper at a decision point,
  and the error propagates into Module 4's only volume-gated prompt. Filed High rather than Medium
  because the invariant forbidding it already exists and is already documented with this exact
  scenario — so this is an unguarded recurrence of a known defect, not a new judgment call, and the
  remedy is already specified in INV-244's own text.
- MCP re-check: **n/a (no Senzing fact from the server is in dispute).** The 500-record built-in
  figure the step relays is correct and correctly sourced — `sdk_guide(topic='load',
  language='java', platform='linux_apt', record_count=10000)` `compatibility_notes` on server
  1.33.0, 2026-08-28, return *"exceeds the default Senzing license limit of 500"*. The defect is
  that the step relays that generic figure **instead of** measuring the installed license, which is
  an environment reading rather than a server fact (INV-080/INV-149).
- Upstream: not applicable — this is entirely a plugin-side branch.

## Deviations from this spec, and why (2026-08-31)

- **Item 3 resolved to PERSIST, on the maintainer's decision.** The spec deliberately left this
  open. The evidence put to the maintainer was that Module 4's Step 8a **never measures before
  gating** — it reads the recorded value at `SKILL.md:798-812` and only measures at `:949`, *after*
  a custom key has been applied — so "present only" would have fixed what the Bootcamper is told at
  Step 5a and left the unneeded gate firing one module later. Consequently the ⛔ at the old
  `SKILL.md:1070` was **reworded, not reaffirmed**: *"Never write this field when it is ABSENT"*
  became *"Write this field ONLY from the reading taken here, and never from an assumption"*, with
  ⛔ **"When the measurement cannot run, write nothing"** carrying the protection that sentence
  existed for. Absence still means *not measured*; it now means the measurement was skipped or
  failed rather than never attempted.
- **The change is larger than `## Affected files` predicted, and the extra sites are the point
  (INV-246).** Making Step 5a a writer falsified a claim at **four** shipped sites in three other
  modules — `module-01-business-problem/phase1-discovery.md` (twice), `module-04-data-collection/
  SKILL.md`, `module-06-data-processing/phaseA-build-loading.md` and `phaseB-load-first-source.md` —
  each of which said Module 4's Step 8a was the only writer, or the only one reached before that
  point. All four were corrected to state the **property** rather than the order of writers. Two
  existing guards had to move with them: `tests/test_license_limit_is_written_only_from_a_
  measurement.py` (two assertions pinned the superseded behavior — the old needles are now pinned
  in the must-NOT-match direction) and `tests/test_module06_license_reconciliation.py`.
- **`specs/INVARIANTS.md` was edited, as the spec predicted, but not in the way it predicted.**
  INV-244's *rationale* — not its condition — asserted *"The only writer of `license_record_limit`
  is Module 4's Step 8a gate"* and *"the field is absent no matter what license is installed"*.
  Both are now historical, so a dated correction was appended in place (permitted by
  `INVARIANTS.md`'s own rule 2: clarification without a change of meaning). The new plugin-wide
  guard was added to INV-244's enforcer list **alongside** the module-scoped one rather than
  replacing it — a guard scoped to one module is what let the second site ship.
- **MCP re-check found a newer server than the spec assumed.** The spec was written against
  **1.33.0**; this ran against **1.35.1** (2026-08-31). Nothing it relied on changed. Two facts were
  established live rather than carried from the spec: `SzProduct`'s license method takes no
  arguments and returns a JSON string in all five bindings (`get_sdk_reference(topic='parameters',
  filter='getLicense')`), and — new, and what makes the fix cheap — the `GetLicense` snippet ships
  in the **same** `generate_scaffold(workflow='information')` response Step 4 already fetches for
  `GetVersion`, so Step 5a adds no new scaffold call.
- ⛔ **The new guard's first version PASSED the mutation, and that is recorded rather than
  quietly fixed.** `tests/test_no_absence_branch_asserts_a_licensing_finding.py` was written,
  reviewed and passing before the real Step 5a text was reintroduced to test it — at which point it
  still passed, because *"say the current limit is unavailable from the MCP server"* sat in the same
  branch and had been included as a discharge phrase. That sentence is about failing to fetch a
  published figure, not about marking a claim unverified. It was removed, and the guard now fails on
  the shipped defect and passes on the correction, both verified by mutating the real file.
