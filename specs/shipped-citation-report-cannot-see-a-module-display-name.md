# The shipped-citation report cannot see a module display name

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`coverage_reports.py shipped` exists to answer one question: which invariants bind a
shipped artifact while no shipped file cites them. On 2026-08-14, eight invariants
(INV-222 – INV-229) were registered and **none** of them was cited anywhere under
`plugins/`. The report found **one**.

Executed against the live file, not argued:

```text
INV-222 no match -> not reported
INV-223 no match -> not reported
INV-224 no match -> not reported
INV-225 no match -> not reported
INV-226 MATCH:'Module 0'
INV-227 no match -> not reported
INV-228 no match -> not reported
INV-229 no match -> not reported
```

INV-226 was surfaced only because its text happens to say "Module 0". Change that
phrase to "Entity Resolution Concepts" — the name the plugin's own INV-079 requires
elsewhere — and the report goes silent on all eight.

## Root cause

`.claude/skills/dry-run/coverage_reports.py:283-292`, the `SHIPPED_ARTIFACT` filter:

```python
SHIPPED_ARTIFACT = re.compile(
    r"plugins/|"
    r"\bmodule-\d\d|\bModule \d|"
    r"SKILL\.md|phase[0-9A-Za-z-]*\.md|ground-rules\.md|"
    r"scripts/[\w-]+\.py|hooks/[\w-]+\.py|"
    r"\bgraduation\b|\bbootcamp-onboarding\b|\bbootcamp-preparation\b"
)
```

Every alternative is a **repo-internal** name: a path, a filename, a `module-NN`
directory, a `Module N` catalog label, or a hyphenated skill-directory name. The
vocabulary an invariant actually uses to name a module is the **display name** — and
the filter recognizes none of them:

| Invariant | Names, in its own text | Filter sees it? |
|---|---|---|
| INV-223 | "Truth Set visualization" | no |
| INV-225 | "System verification" | no |
| INV-227 | "Bootcamp preparation", "the progress file" | no |
| INV-229 | "System-verification checks" | no |
| INV-226 | "Bootcamp preparation", "module-completion", **"Module 0"** | yes — via the catalog label only |

So the filter is at odds with the plugin's own naming rule. INV-079 requires module
names in full and exact, and `bootcamp-preparation/SKILL.md:145` states the internal
"#" and "Maps to" columns are internal and must not be rendered. An invariant written
in the required vocabulary is therefore invisible to the report, while one written in
the discouraged vocabulary is visible. The better an invariant's prose, the less this
report can see it.

A second, smaller gap in the same filter: `\bbootcamp-preparation\b` and
`\bbootcamp-onboarding\b` are hyphenated only, so "Bootcamp preparation" written as
prose — the form INV-226 and INV-227 both use — misses even though the hyphenated
sibling is listed.

**This is the "guard narrower than the invariant it claims to enforce" class** (audit
Step 7, item 3), applied to a report rather than a test. The report's docstring is
honest that it under-reports — "a hit is not a defect… this is where to look, not a bug
list" — but the miss here is not a judgment call at the margin: it is the report's
central case, eight times, on the day the class occurred.

**No Senzing fact is at issue** — this is a repo-side detector, offline, touching no
MCP route (INV-080 untouched).

## Proposed change

1. **Add the module display names to `SHIPPED_ARTIFACT`**, sourced from the module table
   rather than hand-listed a second time where they can drift: Bootcamp preparation,
   Entity Resolution Concepts, Discover the Business Problem, SDK setup, System
   verification, Truth Set visualization, Data collection, Data Quality/Mapping and
   Transformation, Data processing, Query/Visualize and Discover, Bootcamp graduation.
   Match case-insensitively and tolerate the hyphenated adjectival form
   ("System-verification").
2. **Accept the spaced forms** of the three skill names already listed
   (`bootcamp[- ]preparation`, `bootcamp[- ]onboarding`), so prose and directory
   spelling are treated alike.
3. **Add the shipped state artifacts** an invariant routinely binds by name and that no
   current alternative matches: `bootcamp_progress.json`, `bootcamp_preferences.yaml`,
   `bootcamp_recap.md`, "the progress file", "the checkpoint".
4. **Prove the widening on the known set.** INV-223, INV-225, INV-227 and INV-229 must
   each be reported before their citations land, and must each drop out once cited —
   which is the negative control this change needs, and it is available for free because
   `newly-minted-invariants-carry-no-shipped-citation` supplies both states.
5. **Do not widen into a general-property matcher.** The filter's purpose is to keep the
   report readable; a rule stating a property with no artifact ("a value the Bootcamper
   was asked for MUST outrank…") should still be excluded. Widening to the plugin's own
   nouns is the fix; matching every invariant is not.

## Acceptance criteria

- [ ] `SHIPPED_ARTIFACT` matches an invariant that names a module by its display name,
      in both the spaced and hyphenated-adjective forms.
- [ ] With INV-222 – INV-229 uncited, `coverage_reports.py shipped` reports at least
      INV-223, INV-225, INV-226, INV-227 and INV-229 (the five that name a shipped
      artifact); once they are cited, it reports none of them.
- [ ] An invariant stating a general property with no artifact is still not reported —
      demonstrated against a named existing invariant, so the filter is shown to still
      filter.
- [ ] A repo-level test (`tests/`, stdlib only) asserts the display-name case, so a
      future edit cannot narrow the filter back without going red. Negative-controlled:
      revert the regex and confirm the test fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Source

`production-readiness-audit`, 2026-08-14. Found by asking why the reverse sweep's own
detector reported one uncited invariant when a grep for `INV-22[2-9]` across `plugins/`
returned zero hits for all eight.

- Related: `newly-minted-invariants-carry-no-shipped-citation` (the eight uncited
  invariants this report could not see).
- Establishes no new invariant. ⚠️ It does, however, bear on a standing one: the report
  is the mechanical half of the reverse contract this audit's own skill file describes,
  so its blind spots are worth stating there once fixed.

## Deviations from this spec, and why (2026-08-14)

- **The demonstration set differs from criterion 2, and it is stronger.** The criterion predicted
  INV-223, INV-225, INV-226, INV-227 and INV-229. INV-229 was already cited by the time this landed
  (the verification-report spec was implemented first, in the same session), so it correctly did not
  appear. What the widened filter surfaced instead: the other four **plus INV-140 and INV-214** —
  two pre-existing gaps that had been invisible for the same reason, which is better evidence than
  the predicted set because nobody had gone looking for them. Before: 1 hit. After: 6. Once all six
  were cited: 0.
- **`the checkpoint` was NOT added to the filter**, though proposed change 3 listed it. It appears in
  a large share of invariant prose, so adding it would have shifted the filter toward matching
  everything — which proposed change 5 forbids in the same spec. `bootcamp_progress.json`,
  `bootcamp_preferences.yaml`, `bootcamp_recap.md`, `module-completion.md` and "the progress file"
  were added; they name artifacts rather than a general property.
- **The absent-table case raises instead of degrading.** The spec did not say what to do when the
  module table cannot be read. `module_display_names` raises, because a silent empty list re-creates
  precisely this blind spot — the report would keep printing and keep looking authoritative while
  seeing no display-name invariant at all. The scratch-tree fixture in
  `tests/test_coverage_reports.py` therefore had to grow a module table; nine existing tests failed
  until it did, which is the behavior working as intended.
- **Two negative controls escaped and both were real weaknesses in the assertions, not in the fix.**
  (1) The "Bootcamp preparation" case passed on the table-derived name alone, proving nothing about
  the spaced form in `STATIC_ARTIFACT`; onboarding is the only skill named in invariant prose that
  the table does not supply, so that is now the case that pins it. (2) The first onboarding fixture
  said "MUST create the progress file" and matched `the progress file` instead — a fixture that
  defeated its own assertion.
