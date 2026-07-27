# Escape the visualization snapshot's embedded `<script>` payload

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The standalone, self-contained visualization snapshot (INV-077/INV-091 — the offline
HTML artifact the bootcamper can open and share with no server or network) embeds the
entire entity model into an inline `<script>` block without escaping HTML-significant
characters. Every string in that payload is data-sourced (entity names, data-source
names, match keys, resolution rules, feature descriptions — all taken from the loaded
JSONL records). If any such field contains the literal substring `</script>`, the
browser terminates the script block early and parses whatever follows as raw
HTML/JavaScript: a stored HTML/script-injection (XSS) vector in the shared artifact.

The live-server code paths route the same untrusted fields through `_esc_html`
(e.g. `_result_card`, `_match_key_chips`); the snapshot's JSON-payload embed is the one
place that skips escaping.

## Root cause

`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1113` (in `write_snapshot`):

```python
"<script>const __DATA__=" + json.dumps(payload) + ";"
```

`payload` (lines 1101–1109) is `model.stats()/graph()/merges()/dashboard()/overlap()/
match_keys()/feature_scores()` — data-sourced strings — serialized with a bare
`json.dumps()`. `json.dumps` does not escape `<`, so a `</script>` inside any string
value passes through verbatim and closes the inline `<script>` element.

The sibling embed at `senzing_viz_server.py:916`
(`.replace("__SRC_COLORS__", json.dumps(SOURCE_COLORS))`) has the same shape; its input
is a fixed constant palette (not data-sourced), so it is not currently exploitable, but
it should use the same safe helper for consistency and defense-in-depth.

## Proposed change

Escape the `<` character (and, defensively, `>` and `&`) when serializing any object
into an inline `<script>` block, so the payload can never break out of the script
context. `<` is a valid JSON string escape, so the result is still valid JS and the
parsed data is byte-identical.

- Add a small helper next to `_esc_html`, e.g.:

  ```python
  def _script_json(obj):
      """json.dumps safe to embed inside an inline <script> block."""
      return (json.dumps(obj)
              .replace("<", "\\u003c")
              .replace(">", "\\u003e")
              .replace("&", "\\u0026"))
  ```

- Use it at `senzing_viz_server.py:1113` for `payload` and at `:916` for `SOURCE_COLORS`.
- Leave the `/api/*` HTTP responses (`self._send(200, json.dumps(...))`, lines ~945–966)
  unchanged — those are `Content-Type: application/json` bodies, not embedded in HTML, so
  they are not a `<script>`-breakout surface.

## Acceptance criteria

- [ ] A snapshot generated from a record whose name/match-key field contains the literal
      `</script>` (and `<img onerror=...>`) renders that text as inert data — no early
      script termination, no injected markup executes.
- [ ] The generated snapshot HTML contains no unescaped `</script>` (or bare `<`)
      originating from the embedded `__DATA__`/`__SRC_COLORS__` payloads.
- [ ] The embedded data still round-trips: tabs/graph render identically to the
      pre-change snapshot for records with no HTML-significant characters.
- [ ] The offline guarantee (INV-091) is preserved — no new network dependency; the fix
      is pure string transformation.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — add `_script_json` helper;
  apply at the `write_snapshot` payload embed (~line 1113) and the `__SRC_COLORS__` embed
  (~line 916).

## Source

- Claude Code Review, `Senzing/senzing-bootcamp-claude-plugin` PR #4 (comment 5073711304),
  Parts 2 & 5 — "Stored HTML/script injection in the standalone snapshot".
- Priority: High (only data-sourced, autonomously generated artifact that is shared/opened
  outside the tool).
- Related specs: `specs/vendor-d3-offline-visualization.md`, `specs/snapshot-static-search-results.md`.

## Invariants introduced

- `INV-106` — Values embedded into an inline `<script>` block MUST use `_script_json`
  (escapes `<`/`>`/`&`), never bare `json.dumps` (recorded in `specs/INVARIANTS.md`).
