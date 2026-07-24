# Tests

Dev-only tests for the Senzing Bootcamp plugin. They live here at the repo top
level — **not** under `plugins/` — so `propagate.sh` (which mirrors `plugins/`
into the public repo) never ships them to bootcampers.

Standard library only; no third-party dependency.

Run everything:

```bash
python3 -m unittest discover -s tests
```

- `test_write_gate.py` — exercises the PreToolUse write-gate security control
  (`plugins/senzing-bootcamp/scripts/write-gate.py`): location allow/block,
  `..`-traversal, home-relative and `$TMPDIR`/`%TEMP%` temp paths, the
  case-folded in-project exemption, and secret detection (PEM / AWS / Senzing
  `AQAAAD` license blobs). Invoked as a subprocess because the gate reads stdin
  at import time.
- `test_brand_sync.py` — asserts the inlined fallback palettes in
  `senzing_viz_server.py` and `generate_recap_pdf.py` stay equal to
  `brand_tokens.py`, so the hand-maintained copies cannot drift silently.
