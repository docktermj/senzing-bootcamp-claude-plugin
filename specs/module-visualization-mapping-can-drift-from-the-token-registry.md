# `MODULE_VISUALIZATIONS` is an inlined copy of the module-token registry with nothing pinning them together

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`scripts/generate_recap_pdf.py` derives the tab-coverage denominator from the modules that
ran, via a hardcoded map:

```python
MODULE_VISUALIZATIONS = {
    "truthset_visualization": "truthset_verification",
    "query_visualize_discover": "results_visualization",
}
```

Its keys are **module name tokens** whose canonical registry lives elsewhere:
`skills/bootcamp-preparation/SKILL.md`'s module table, which lists
`query_visualize_discover` for Query, Visualize and Discover and `truthset_visualization` for
Truth Set visualization. `skills/bootcamp-onboarding/module-completion.md:21` is what writes
a module's token into `modules_completed` at its close.

Both keys are **correct today** — verified against the registry table. Nothing asserts they
stay correct.

⛔ **The failure is silent and it lands exactly where the check was added.** If a token is
renamed, `expected_visualizations()` stops returning that module's visualization, the missing
manifest stops being reported, and tab coverage returns to printing a clean figure while a
whole visualization is absent — which is the 2026-08-25 defect
(`specs/tab-coverage-has-no-denominator-for-a-visualization-that-wrote-no-manifest.md`) restored
by a rename. The `read_completed_modules()` degradation is deliberately honest in the
under-reporting direction, which means a wrong key produces *no* error at all.

## Root cause

Step 7 class 7 of the audit method: **an inlined constant diverging from its source of
truth**. The plugin has a precedent and a remedy for exactly this shape — `brand_tokens.py`'s
palette is inlined into two generators and `tests/test_brand_sync.py` asserts the copies stay
equal — and the same run that added `MODULE_VISUALIZATIONS` used that precedent knowingly for
`secret_patterns.py` (`tests/test_secret_patterns_are_shared.py`).

It was not applied here. `tests/test_expected_visualization_denominator.py` pins the map's
**content**:

```python
self.assertEqual(
    {"truthset_visualization": "truthset_verification",
     "query_visualize_discover": "results_visualization"},
    GEN.MODULE_VISUALIZATIONS, …)
```

That notices an edit to the map. It cannot notice the map going stale because the *registry*
moved — which is the direction that breaks silently, since nothing fails when a token the map
names simply stops being written.

⚠️ **The registry is a markdown table, not a constant**, which is why this needs a test rather
than an import. The tokens cannot be read from a module at run time without the plugin's own
files being parsed, and `generate_recap_pdf.py` must not grow a markdown-table parser for it.

## Proposed change

**1. Assert the keys against the registry, not against themselves.** A repo-level test that
reads `skills/bootcamp-preparation/SKILL.md`'s module table, extracts the name tokens, and
asserts every key of `MODULE_VISUALIZATIONS` appears among them. stdlib only, no `plugins/`
import (INV-108).

**2. Assert the registry extraction is not vacuous** (INV-265). A table parse that silently
matches nothing satisfies "every key is present" trivially — the exact failure this test is
written to prevent, one level up. Require a floor on the number of tokens found, and assert a
token known to be in the table is among them.

**3. State the direction the existing test cannot cover**, in its docstring, and point at the
new one. The content-pin is still worth keeping: the two tests catch opposite drifts.

⚠️ **Do not replace the content-pin with the registry check.** A map whose keys are all valid
tokens can still map the wrong module to the wrong visualization name; only the content-pin
catches that.

## Acceptance criteria

- [ ] A test reads the module-token registry from `skills/bootcamp-preparation/SKILL.md` and
      asserts every `MODULE_VISUALIZATIONS` key appears in it.
- [ ] That test carries an anti-vacuity assertion: the extraction found at least a floor
      number of tokens, and a known token is among them (INV-265).
- [ ] The existing content-pin in `tests/test_expected_visualization_denominator.py` survives,
      with a docstring naming which drift each of the two tests catches.
- [ ] Negative-controlled: renaming a key to a token the registry does not carry fails the new
      test, and swapping the two visualization values fails the content-pin.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `tests/test_expected_visualization_denominator.py` — the registry check, and the docstring
  distinguishing it from the content-pin
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — a comment beside
  `MODULE_VISUALIZATIONS` naming the registry as its source of truth and the test that pins it

## Source

- Feedback: n/a — found by `production-readiness-audit-2026-08-26`. ⚠️ Found while chasing a
  *different* hypothesis: a grep of `module-07-query-visualize-discover/` for
  `modules_completed` returned nothing, which read as "Module 7 never records itself, so the
  denominator is inert for the module that motivated it". That was wrong — completion is written
  centrally by `module-completion.md:21` and the token is registered in
  `bootcamp-preparation/SKILL.md`. The mapping is correct; the missing guard is what survived.
  `Source: self-observed (assistant retrospective)`.
- Priority: Medium — nothing is wrong today, and the failure mode is a silent return to a defect
  fixed the same day.
- MCP re-check: n/a (no Senzing fact). Module name tokens and visualization names are the
  plugin's own vocabulary; no SDK method, flag, response shape or server behavior is asserted,
  and no absence is claimed.
- Upstream: not applicable.
- Related specs: `specs/tab-coverage-has-no-denominator-for-a-visualization-that-wrote-no-manifest.md`
  (the check this guards), `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md`
  (whose `secret_patterns.py` used the `brand_tokens` precedent this one missed)
