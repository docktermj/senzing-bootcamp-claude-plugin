# Source encoding collides past twenty-four sources

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-127 requires that a categorical visualization "MUST NOT give two present
categories the same encoding — varying a second visual channel once the palette is
exhausted rather than reusing a color". `brand_tokens.color_for_sources()` satisfies
that up to **24** data sources and violates it at **25**: the 25th source renders
identically to the 7th.

The returned mapping stays collision-free at any size, because each entry carries a
distinct `cycle` integer. What collides is what the browser actually *draws*. The
served JS applies the stroke **only when `cycle` is non-zero**:

```js
.attr("stroke",      function(d){return srcCycle(d.data_sources[0])?srcStroke(d.data_sources[0]):null;})
.attr("stroke-width",function(d){return srcCycle(d.data_sources[0])?1.5:null;})
```
— `plugins/senzing-bootcamp/scripts/senzing_viz_server.py:885-886`, and the same rule
for the legend swatch at `:999`.

So the rendered encoding is `fill` × `{no stroke, #18160F, #FAF8F3, #FFFFFF}` —
6 fills × 4 states = **24 distinct visual encodings**. `cycle` itself never reaches
the canvas as a distinguishable property; it only decides *whether* a stroke is drawn
and *which* of three colours it takes. Measured directly against the shipped module:

| sources | dict encodings | distinct as rendered |
|---|---|---|
| 24 | 24 | 24 |
| 25 | 25 | **24** |
| 60 | 60 | **24** |

At n=25 the first collision is `SRC_006` and `SRC_024`, both drawn as fill `#8b5cf6`
with a `#18160F` stroke (cycle 1 and cycle 4 — `4 % 3 == 1`).

This is a real but low-severity defect: no realistic bootcamp reaches 25 data sources
(the largest CORD dataset, `las-vegas`, has 11). It is worth fixing because INV-127 is
stated absolutely and because the guard that is supposed to enforce it currently
certifies more than it checks.

## Root cause

Two independent gaps, in the code and in its guard.

**The code.** `plugins/senzing-bootcamp/scripts/brand_tokens.py:116` computes
`"stroke": SOURCE_STROKES[cycle % len(SOURCE_STROKES)]` with
`SOURCE_STROKES = ["#FFFFFF", "#18160F", "#FAF8F3"]` (`:83`) and
`FALLBACK_COLORS` of length 6. Three strokes modulo-cycled over 6 fills gives 18
combinations, plus the no-stroke state for `cycle == 0` gives 24 — after which
`cycle` keeps incrementing while the drawn appearance repeats. The comment at `:81`
calls `SOURCE_STROKES` the "Second visual channel for a source beyond the first
palette cycle", which is accurate for one wrap and stops being true at the fourth.

**The guard.** `tests/test_brand_sync.py:103-108`,
`test_more_sources_than_colors_stay_distinguishable`, asserts:

```python
sources = [f"SRC{i}" for i in range(len(self.bt.FALLBACK_COLORS) + 3)]   # 9 sources
pairs = {(v["fill"], v["stroke"]) for v in m.values()}
self.assertEqual(len(sources), len(pairs), "a second channel must distinguish the repeat")
```

It is under-scoped in two separate ways, and each alone would hide the defect:

1. **It stops at 9** — `len(FALLBACK_COLORS) + 3` — which proves one wrap past the
   palette and never approaches the 24-slot capacity, let alone the 25th source.
2. **It asserts on the wrong tuple.** `(fill, stroke)` is not what renders; the
   rendered key is `(fill, stroke if cycle else None)`. At n=9 the two agree by
   accident, because no source has reached `cycle == 3`. A cycle-0 source carries
   `stroke: "#FFFFFF"` in the dict while being drawn with **no stroke at all**, so
   the test's model of the output diverges from the output as soon as the third wrap
   is reached.

The docstring — "a second channel must distinguish the repeat" — is therefore a
claim the assertion does not check at the scale where it stops being true. This is
the failure shape the dry-run methodology calls out: a guard that certifies what it
never tested.

## Proposed change

1. Widen the encoding space in `brand_tokens.color_for_sources()` so distinct sources
   stay distinct as **drawn**, not merely as returned. Options, cheapest first:
   - Give `cycle == 0` its own stroke slot rather than treating "no stroke" as an
     accidental fourth state, and add stroke widths or a dash pattern as a genuine
     third channel, so capacity becomes fills × strokes × widths.
   - Or derive the fill by perturbing lightness/saturation per wrap, which scales
     without bound instead of adding fixed slots.
   Whichever is chosen, the property to hold is that the **rendered** key
   `(fill, stroke-if-drawn, width/dash)` is unique per present source.
2. Make the renderer consume whatever second channel is chosen, in both places that
   draw it (`senzing_viz_server.py:885-886` node, `:999` legend), so a source's
   swatch in the legend and its node in the graph agree.
3. Rewrite the guard to assert on the rendered key and at a scale past capacity —
   see acceptance criteria. Keep the existing small-n tests; they are correct and
   cover the reported case.
4. If a capacity ceiling is deliberately accepted instead of removed, say so in
   INV-127 with the number, and have `color_for_sources` warn when it is exceeded —
   an acknowledged limit is defensible, a silent one is not.

## Acceptance criteria

- [ ] For every n from 2 to at least 64, `color_for_sources` yields n distinct
      **rendered** keys, where the rendered key is
      `(fill, stroke if cycle else None, <any further channel>)` — the same
      expression the served JS uses, not the raw dict tuple.
- [ ] `tests/test_brand_sync.py` tests at a size past the encoding capacity (≥ 64,
      not `len(FALLBACK_COLORS) + 3`) and computes the rendered key rather than
      `(fill, stroke)`, so it fails on today's code.
- [ ] Negative-controlled: with the fix reverted, the new assertion fails and names
      the colliding sources; with it applied, it passes.
- [ ] Assignment stays deterministic and order-independent (existing
      `test_assignment_is_deterministic` still passes), `SIGNAL_GREEN` is still never
      assigned, and Truth Set sources keep their preferred fills.
- [ ] The legend swatch and the graph node agree on the encoding for the same source
      at n > 24.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      INV-127 binds a visualization server written in any language (INV-090), so the
      contract, not the Python implementation, is what must state the rule.

## Affected files

- `plugins/senzing-bootcamp/scripts/brand_tokens.py` — `color_for_sources()` (`:103-119`),
  `SOURCE_STROKES` (`:83`) and the second-channel comment (`:81`).
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — the inline fallback copy
  (`:148-157`) must stay identical to the helper (`test_viz_server_inline_fallback_matches_the_token_helper`
  pins this), plus the two draw sites `:885-886` and `:999`.
- `tests/test_brand_sync.py` — `test_more_sources_than_colors_stay_distinguishable`.
- `specs/INVARIANTS.md` — only if a capacity ceiling is accepted rather than removed.

## Source

- Feedback: n/a — found by `/dry-run` phase 2 (hooks and bundled scripts), 2026-08-13
  (`Source: self-observed (assistant retrospective)`). Found by driving
  `color_for_sources` past its palette as phase 2 instructs, then tracing whether the
  `cycle` field reaches the canvas.
- Priority: Low — correctness gap against an absolute invariant, at a scale no
  realistic bootcamp reaches (the largest CORD dataset has 11 sources). The
  under-scoped guard is the more valuable half of the finding.
- MCP re-check: n/a (no Senzing fact) — this is entirely local rendering behavior.
- Upstream: not applicable.
- Related specs: `source-colors-from-discovered-data-sources` (the spec that
  established INV-127).

## Deviations from this spec, and why (2026-08-14)

- **Option 1 was taken in a specific form, and option 4 was deliberately not.** The spec
  offered a capacity ceiling as an acceptable outcome provided it is "sa[id] so in INV-127
  with the number". That would be a **meaning change to a registered invariant**, which
  needs the maintainer's sign-off (`implement-spec` Step 5) — and this was implemented
  during an unattended batch on 2026-08-14 where the maintainer's standing instruction was
  to queue invariant changes, not make them. So the encoding space was widened instead:
  stroke width as a third channel, then a deterministic lightness perturbation of the fill,
  giving 210 distinct rendered appearances. No invariant text changed.
- **The limit is stated in code rather than in INV-127.** `brand_tokens.SOURCE_ENCODING_CAPACITY`
  names it, `color_for_sources` warns past it, and the contract states both requirements for
  any-language servers. This satisfies option 4's actual purpose — "an acknowledged limit is
  defensible, a silent one is not" — without editing an invariant.
- **A dash pattern was considered as the third channel and rejected.** CSS `box-shadow`, which
  draws the legend swatch, cannot express a dash, so a dash channel would have had to be
  rendered one way on the node and another (or not at all) in the legend — breaking the
  spec's own acceptance criterion that the two agree. Stroke width is expressible in both,
  identically.
- **`cycle` is retained in the returned dict** rather than replaced. It still records which
  wrap a source landed in, and removing it would have been a gratuitous contract change; the
  fix is that no draw site keys on it. `stroke_width` is the new field renderers must use, and
  it is `None` exactly when no stroke is drawn.
- **Two extra files changed** beyond the spec's Affected-files list, both required by its own
  criteria: `visualization-api-reference.md` (criterion 6 — the contract, not the Python
  implementation, must state the rule) and a new `tests/test_source_encoding_renders_distinctly.py`
  (criterion 1 and 5 asserted against what the browser draws).
- **An unrelated vacuity was fixed in `tests/test_brand_sync.py`.**
  `test_viz_server_inline_fallback_matches_the_token_helper` was comparing
  `brand_tokens.color_for_sources` to itself, because the inline fallback is bound only when
  the import fails and it never fails under test. It was demonstrated vacuous — a mutation
  gutting the inline copy escaped — and now loads the server with the import blocked. This is
  outside the spec's scope but inside the file it names, and leaving it would have meant the
  inline copy's half of this fix was unguarded.
