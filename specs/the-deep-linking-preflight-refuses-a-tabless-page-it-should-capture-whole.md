# The deep-linking pre-flight refuses a tabless live page, costing every single-page deliverable its recap image

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A **single-page** deliverable served over `http://` — a quality report, a mapping summary, any
generated page with no tab bar — is now refused by `capture_screenshots.py --url` with exit 1 and no
image, where it previously captured correctly as one page.

Measured 2026-08-31 against a localhost stub serving
`<h1>A quality report</h1><p>No tabs at all.</p>`, driving `main()` exactly as the module's capture
step does:

```text
before b826db5:   rc = 0   files = ['dq.png']
after  b826db5:   rc = 1   files = []
```

The stderr in both runs is the routine per-tab "not present in this visualization" notice; the
difference is entirely the exit and the missing file.

⛔ **This is the exact failure the code it was added beside warns about.** The safety net at
`capture_screenshots.py` `main()` carries the comment *"Capture it whole instead of exiting empty —
exiting was the behavior that silently cost every single-page deliverable its recap image."* The new
pre-flight reintroduced that behavior three lines above the net that exists to prevent it.

## Root cause

`_supports_deep_linking`'s call site is ordered wrongly, not written wrongly.

`main()` runs `_tabs_present` first, which correctly finds none of the six tab ids in a tabless page
and leaves `tabs == []`. The new pre-flight then fires:

```python
if is_url and tabs != [SINGLE_PAGE_ID] and not _supports_deep_linking(source):
```

`[] != [SINGLE_PAGE_ID]` is true, and a document with no tabs has no reason to read the query string,
so `_supports_deep_linking` correctly returns `False` — and the run exits 1 **before** reaching:

```python
if not tabs and not _has_tab_controls(source):
    # Safety net: the page has no tab bar at all … Capture it whole instead of exiting empty
```

So the check asks "can this page select a tab?" of a page that was never going to select one. Both
the pre-flight and the safety net are individually correct; only their order is wrong.

⚠️ **The guard that should have caught this asserts the opposite case.**
`tests/test_capture_verifies_tab_activation.py` drives a page that HAS tab controls and lacks
deep-linking, and `tests/test_capture_single_page.py` exercises the single-page path but not over
`http://` with tabs requested — so the full suite (3,768 passed) was green across the regression.
This is the "guard narrower than the case it protects" class, at the moment of writing the guard.

## Proposed change

1. **Move the pre-flight below the single-page safety net**, so it can only see a page that has tab
   controls and a non-empty `tabs` list. Ordering, not a new condition, is the fix — a condition
   added at the current position would leave the next reader to re-derive why it is there.
2. **Add the tabless-live-page case to the activation guard**, asserting exit 0 and one image, so the
   ordering cannot silently invert again.

## Acceptance criteria

- [ ] A tabless page served over `http://` captures as a single page with exit 0 and one image, as it
      did before `b826db5`.
- [ ] A tabbed page served over `http://` with no `?tab=` support still exits non-zero with no images
      and a message naming deep-linking.
- [ ] The guard covers both, negative-controlled by restoring the pre-flight to its current position.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — the pre-flight's position in `main()`
- `tests/test_capture_verifies_tab_activation.py` — the tabless-live-page case

## Source

- Feedback: none — found by `/production-readiness-audit` on 2026-08-31, auditing the diff since the
  previous audit entry, which was this same session's own work
  (`Source: self-observed (assistant retrospective)`). Found by probing the path the new code
  *did not* claim to change, rather than the path it did.
- Priority: **High.** It breaks a documented path that worked one commit earlier, silently: the run
  exits non-zero with no image, and the single-page deliverable simply has no picture in the recap.
- MCP re-check: **n/a (no Senzing fact).** The defect is entirely in a bundled script's control flow.
- Upstream: not applicable — plugin-side only.
