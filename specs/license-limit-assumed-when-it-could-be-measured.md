# Phase A assumes the default licence limit on the one path where nothing ever measures it

## Problem

`module-06-data-processing/phaseA-build-loading.md:155-171` reconciles `sdk_guide`'s
record-count-derived `LICENSE REQUIRED` note against the licence the bootcamp has detected, reading
`license_record_limit` from `config/bootcamp_progress.json`. Its three branches are:

- `0` (no cap) or ≥ dataset size → suppress the note entirely;
- positive and below the dataset size → the note applies;
- **absent or null → "no custom license was detected, so the default-limit note is the right
  assumption. Relay it."**

The third branch is reached on the common path and is wrong there. The only writer of
`license_record_limit` is Module 4's Step 8a licence gate
(`module-04-data-collection/SKILL.md:663`, "single, volume-gated"), which by design fires **only**
when the collected volume approaches the limit. A bootcamper with a small dataset never triggers it,
so `license_record_limit` is absent — regardless of what licence is actually installed.

The result is that the guide relays a 500-record default-limit note, and `sdk_guide`'s sampling
prescription with it, to a bootcamper whose installed licence has no cap at all.

**Measured on this walk (2026-08-14).** `SzProduct.getLicense()` on the installed SDK 4.3.4 returned:

```json
{"customer":"Senzing Internal","licenseType":"EVAL (Solely for non-productive use)",
 "expireDate":"2027-03-12","recordLimit":0,"advSearch":0}
```

`recordLimit: 0` — the "no cap" case the first branch exists to suppress. `license_record_limit` was
absent from `config/bootcamp_progress.json`, so the file as written routes to "relay it".

This is the same harm the step already names two paragraphs earlier — *"it sends a bootcamper with
an unlimited license to sample down to 500 records, and the shrunken dataset then
under-demonstrates the cross-source resolution that Modules 6 and 7 exist to show"* — reached
through the **absent** branch instead of the positive one. The step guarded the branch it had seen
fail and left open the branch that is far more commonly taken.

It also contradicts a higher-precedence rule. `bootcamp-onboarding/ground-rules.md:13-21` states:

> **A value you measured on this machine governs over generic guidance about that same value.**
> … Where the bootcamp already holds a detected value for the same thing — the license record
> limit, the installed SDK version, the platform — the detected value decides, the generic note is
> suppressed rather than relayed (INV-012)

The licence record limit is named there explicitly. Phase A's absent-branch relays generic guidance
about exactly that value without ever measuring it, on a machine where it is one SDK call away.

## Root cause

`license_record_limit` is treated as "the detected limit", but it is really "the limit Module 4
happened to record while asking a volume question". Absent means *not asked*, not *no custom
licence*. Nothing in Phase A converts "not asked" into "go and measure it".

## Proposed change

In `phaseA-build-loading.md`, change the **absent or null** branch from *assume the default and
relay* to *measure, then apply the same three branches to the measured value*:

1. Call `SzProduct.getLicense()` through the loader's own environment — the module already builds
   and runs SDK programs in the bootcamper's language, so this needs no new machinery. Signature
   confirmed via `get_sdk_reference(topic='response_schemas', filter='getLicense', language='java')`
   on MCP server 1.32.9, 2026-08-14: `getLicense() -> String` on `SzProduct`.
2. Read `recordLimit` from the returned JSON and persist it as `license_record_limit` in
   `config/bootcamp_progress.json`, so later steps and graduation see a detected value rather than
   an absence.
3. Re-enter the existing three-branch reconciliation with that value. `recordLimit: 0` then
   correctly suppresses the note.
4. Keep a genuine fallback: only when the call **fails** (no engine yet, SDK error) does the
   default-limit assumption apply — and say that it is an assumption.

Consider whether Module 4 Step 8a should record `license_record_limit` unconditionally rather than
only when its volume gate fires, which would fix this at the source; that is a larger change and is
noted rather than proposed here.

## Acceptance criteria

- `phaseA-build-loading.md`'s absent/null branch instructs measuring the licence before assuming a
  limit, and names `SzProduct.getLicense()` / `recordLimit` as the route.
- The measured value is persisted to `license_record_limit` in `config/bootcamp_progress.json`.
- The default-limit assumption survives only as the failure fallback, and is stated as an
  assumption when used.
- A test asserts that the absent/null branch text does not instruct relaying a default limit
  without a measurement step, and that `getLicense` appears in that branch.

## The same branch exists twice

`phaseB-load-first-source.md:44-58` ("License capacity before loading") repeats the identical
three-branch reconciliation, with the identical absent/null wording — *"warn that the evaluation
license halts the load at its cap"*. Both locations must change together, or the suppressed warning
in Phase A reappears one phase later.

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md`
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md`
- `tests/test_module06_license_reconciliation.py` (new)

## Source

`/dry-run` phase 3, 2026-08-14. Analysis started at Data processing; modules 1–8 fast-forwarded.
Licence JSON measured live on the walk's own install (Senzing SDK 4.3.4, Java binding). MCP server
1.32.9, docs indexed 2026-08-11 20:52 UTC.

## Invariants introduced

- `INV-244` — Where a bootcamp state field is written only **conditionally**, a step branching on
  it MUST NOT read that field's absence as a measured finding (recorded in `specs/INVARIANTS.md`,
  indexed under *Module flow, selection and progress*; enforced by
  `tests/test_module06_license_reconciliation.py`). Sibling to INV-194, which forbids the same
  inference on the other surface — concluding the *server* lacks a fact from one tool's empty
  response. ✅ **Approved by the maintainer on 2026-08-14**, on review of the wording as registered. Originally minted under the standing authorization given before that unattended run.

## Deviations from this spec, and why (2026-08-14)

Implemented as proposed, both locations, all four criteria. Four notes.

1. **The signature is server-confirmed; the payload field is not, and the plugin already says so.**
   `get_sdk_reference(topic='response_schemas', filter='getLicense')` on server 1.32.9 (2026-08-14)
   returns `SzProduct` `getLicense() -> String` for every binding — Java, Python, C#, Rust,
   TypeScript — so the spec's citation is confirmed and generalised beyond Java. But its `data`
   array is **empty**: the server does not document the license JSON's fields, so `recordLimit` is
   not server-established. Asked the prose route as well, per INV-194:
   `search_docs(query='license recordLimit getLicense record limit JSON')` returns only EULA,
   pricing and DSR material, nothing describing the response shape. **No `MCP-NEGATIVE` marker was
   added, deliberately** — the plugin already states this correctly at `module-04-data-collection/
   SKILL.md:800`, *"`get_license` has **no** `response_schemas` entry (an empty `data` array is the
   expected result there, not a failed lookup)"*, with the INV-115 route to confirm the shape from
   a saved response. Adding a second dated claim of the same absence would create two records to
   keep in sync.

2. **The procedure is cited, not restated.** Module 4 Step 8a already defines the whole measurement
   — scaffold, save the JSON, confirm the shape before parsing (INV-115), parse `recordLimit`,
   write `license_record_limit`. Phase A routes to it rather than duplicating it, and Phase B
   routes to Phase A. The spec's own closing section is that this branch already exists twice; a
   third copy of the *procedure* would have been the same mistake one level down.

3. **Phase B defers to Phase A's measurement** rather than measuring again. Phase A runs first and
   persists the value, so Phase B's absent branch is reached only if Phase A's measurement failed —
   stated explicitly so the two do not both call `getLicense()` on every run.

4. **A guard escaped a mutation and was strengthened.** The "explain why the field is absent" test
   originally asserted only that `Step 8a` is named; deleting the whole explanation still passed,
   because the branch names Step 8a again when routing to its procedure. It now pins **volume-gated**
   — the mechanism — plus the inference itself (*absent no matter what license is installed*).
   Naming the writer says where a value comes from; only the mechanism says why its absence carries
   no information. That is the fourth-recorded instance in this repo of asserting a token appears
   somewhere rather than that the claim holds where it is made.

**The spec's own deferred question is left open**, as it proposes: whether Module 4 Step 8a should
record `license_record_limit` unconditionally rather than only when its volume gate fires, which
would fix this at the source. That is a Module 4 change with its own consequences and is noted
here, not built. INV-244 makes the downstream branches safe either way.
