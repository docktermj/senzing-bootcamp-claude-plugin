# Bytecode caching hides a latent syntax error from the suite

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`tests/test_sdk_update_offer.py:175` contains an invalid escape sequence inside a docstring:

```python
        ⚠️ **Asserts the ownership distinction, not the sentence that carries it (INV-219).**
        This used to also pin `never \`brew upgrade --cask\` or \`scoop update\`` — the verbatim
```

`\`` is not a recognised Python escape. Today that is a **`SyntaxWarning`**; Python has scheduled
it to become a **`SyntaxError`**, at which point the file stops importing and the suite stops
running.

⛔ **The suite has been green over it, and the reason is the interesting part.** A
`SyntaxWarning` fires at **compile** time, not at import of a cached module — so once
`__pycache__` holds a `.pyc` for the file, every subsequent run is silent. The warning surfaced
only when an unrelated one-line edit (`d35046d`, changing a docstring's invariant ID at `:295`)
invalidated the cached bytecode and forced a recompile.

Verified rather than assumed: the escape is present in `d35046d~1` (`grep -c` → 1), and
`git show d35046d -- tests/test_sdk_update_offer.py` shows the commit changed exactly one line,
`:295`. **The defect predates the commit that revealed it.**

## Root cause

**Nothing in the repo compiles Python from source, so a compile-time diagnostic has no route to a
failure.** The suite runs `unittest`/`pytest`, which import modules — and importing prefers cached
bytecode. `conformance.py`, `citations.py` and `coverage_reports.py` all read files as *text*.
There is no check whose failure mode is "this file no longer compiles cleanly".

That makes this a **runtime-relative defect (class 2)**: the string is wrong only relative to the
interpreter's caching behaviour, and correct-looking to every text-based scan the repo owns.

**The class is one instance today, and that was measured, not assumed.** Compiling every `.py`
under `tests/`, `plugins/`, `.claude/` and `scripts/` from source with `warnings.simplefilter
("always")` returns exactly **one** hit — this file. But the *mechanism* reaches further than the
instance:

- `plugins/senzing-bootcamp/scripts/*.py` **ship to bootcampers** and run on their machines under
  whatever Python they have. A latent `SyntaxError` there is a broken deliverable, not a warning.
- **INV-052** makes hooks Python 3 exec-form and **INV-108** makes the offline suite stdlib
  Python, so both surfaces are exposed to the same future-Python change.
- **INV-004** (production-ready) is the invariant actually at stake: shipping code with a
  scheduled syntax error is not production-ready, and nothing currently notices.

## Proposed change

1. **Fix the escape** at `tests/test_sdk_update_offer.py:175`. The docstring is quoting shipped
   prose that contains backticks; the fix is to make the docstring raw (`r"""`) or to drop the
   backslashes, whichever leaves the quoted text readable. ⛔ **Do not reword the quoted claim** —
   it is a deliberate record of a pin that was removed, and INV-219's reasoning depends on it.
2. **Add a guard that compiles every repo `.py` from source and fails on any `SyntaxWarning`,
   `DeprecationWarning` or `SyntaxError`** — deriving its file set by scanning (INV-246), never a
   path list. It must compile from **source text**, not import, so `__pycache__` cannot mask the
   result. That is the whole point: the existing suite cannot see this class by construction.
3. **State in the guard's docstring why importing is insufficient**, so nobody later "simplifies"
   it into an import check and silently restores the blind spot.

## Acceptance criteria

- [ ] `tests/test_sdk_update_offer.py` compiles from source with no warning, and the quoted claim
      it records is unchanged in meaning.
- [ ] A guard compiles every `.py` under `tests/`, `plugins/`, `.claude/` and `scripts/` from
      source and fails on `SyntaxWarning`/`DeprecationWarning`/`SyntaxError`, with its file set
      **derived by scanning** and a membership floor so an empty scan cannot pass vacuously.
- [ ] The guard reads source text rather than importing, and its docstring says why — bytecode
      caching is exactly what hid this.
- [ ] **Negative-controlled:** plant an invalid escape in a scanned file, confirm the guard
      fails, revert. Plant one in each scanned *root* (`tests/`, `plugins/`, `.claude/`,
      `scripts/`) so the reach is proven per-root, not by one representative.
- [ ] The guard stays stdlib-only and imports nothing from `plugins/` (INV-108).
- [ ] ⛔ Not runtime-verified: this proves the files *compile* cleanly under the Python running
      the suite. It does not prove they run correctly, and it cannot prove behaviour under a
      future Python that has promoted the warning to an error — it only ensures the repo is
      already clean when that lands.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `tests/test_sdk_update_offer.py` — `:175`, the escape.
- `tests/` — one new guard.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15m
  (`Source: self-observed (assistant retrospective)`). Surfaced while self-auditing `d35046d`:
  the pytest summary gained "1 warning" that earlier runs in the same session did not show, which
  looked like something I had introduced and turned out to be a pre-existing defect my edit had
  merely un-cached.
- Priority: **Medium.** No bootcamper is affected today and the instance is in `tests/`, not
  shipped. It is filed at Medium rather than Low because of the **mechanism**: a compile-time
  diagnostic that bytecode caching can hide indefinitely, on a repo whose shipped `scripts/*.py`
  run on bootcampers' machines, against a change Python has already scheduled.
- MCP re-check: **n/a (no Senzing fact).** A Python source-syntax defect and a gap in the repo's
  own checks. No Senzing claim asserted, no absence about the server relied on. Server **1.32.9**
  (`get_capabilities`, 2026-08-15) recorded earlier this session.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `env-script-must-be-shell-portable` and `windows-powershell-encoding-and-syntax`
  (the same "correct-looking text that a runtime rejects" class on other interpreters), and
  INV-004, INV-052, INV-108, INV-246.
