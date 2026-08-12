# Module 03b hardcodes port 8080 in the lines that matter, while its own text says it may differ

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md`
**contradicts itself about the visualization server's port.**

It twice states the port may not be 8080:

```text
:266   `http://localhost:8080`. If port 8080 is in use, use a different port and tell the
       Bootcamper the [new URL]
:408   - Port in use → pass a different `--port` and share the new URL.
```

And then hardcodes 8080 in the three places that act on it:

```text
:236   running (2.3) and capture from **`--url http://localhost:8080`**, one image per tab
:367   - "Your visualization is running at `http://localhost:8080`, open it in your browser."
:418   "web_service": {"status": "passed|failed", "port": 8080},
:419   "web_page": {"status": "passed|failed", "url": "http://localhost:8080/",
```

**On the branch the file itself anticipates, both failures are real.** With the server on a
different port:

- `:236` captures from a dead URL. Screenshot capture exits 2 (INV-122), so the Truth Set module
  loses every screenshot — and INV-146 requires every captured tab to reach the recap, which it
  cannot if none were captured.
- `:367` tells the Bootcamper to open a port nothing is listening on. That is **verbatim the
  failure INV-172 was written from**: *"a Module 7 snapshot on a non-default port told its reader
  to open a port nothing was listening on"*.

**The sibling module already does it correctly**, which is what makes this the incomplete-
application class rather than an open question:

```text
module-07-query-visualize-discover/phase1-query-visualize.md:461   `--url http://localhost:<port>`
module-07-query-visualize-discover/phase1-query-visualize.md:476   "…running at `http://localhost:<port>`…"
```

**The file cites INV-172 — for the other half of the rule.** At `:200-201` it applies the
dataset-wording half (*"tell it what the data **is** so the retained snapshot says so (INV-172)"*)
and not the port half, in the same file that hardcodes the port four lines later.

**No Senzing fact is involved.** Internal consistency only.

## Root cause

**The INV-172 guard is narrower than the invariant.** `tests/test_snapshot_and_capture_fidelity.py`
enforces the rule thoroughly — but only against the **Python reference server's** snapshot code
path:

```text
tests/test_snapshot_and_capture_fidelity.py:76-81
    def test_no_hardcoded_port_literal_remains_in_the_note_path(self):
        body = source[start:source.index("def ", start + 10)]
        self.assertNotIn("localhost:8080", body)
```

It reads `senzing_viz_server.py`'s `_snapshot_probe_html` and asserts no literal survives there.
**Module instruction files are not scanned at all**, so `phase1-visualization.md` was free to keep
the literal. This is the audit skill's defect class 3 — *a guard narrower than the invariant it
claims to enforce* — and it is compounded by INV-002/INV-090: the rule binds the server in whatever
language it is generated, so a guard reading only the Python reference cannot establish it.

`snapshot-port-and-dataset-wording` (2026-07-28) fixed the reference server and Module 7's
instructions. Module 03b's instructions were the third site and were not swept.

## Proposed change

1. **`:236`** — capture from `--url http://localhost:<port>`, matching module-07's wording, with the
   port taken from the value actually used to start the server in 2.3.
2. **`:367`** — replace the pinned bootcamper-facing line's `8080` with the port in use.
3. **`:418-419`** — make the verification-report example show the port as a placeholder, so the
   shape does not teach a literal.
4. **Leave `:255`, `:262` and `:266` alone.** They are the *default* start command and the
   instruction for what to do when the default is taken — 8080 is correct there as the default, and
   `:266` is the sentence that makes the rest a contradiction rather than a mistake.
5. **Extend the guard to shipped module instructions**: assert no shipped `.md` instructs capture
   from, or tells the Bootcamper to open, a hardcoded `localhost:8080` — while still allowing the
   default-port start command and the example recap's record of a real run.

⛔ **Do not change `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md`.** Its
`:249`/`:253` mentions of port 8080 are a *record of a run that actually used 8080* (INV-065's
sanitized fixture), not an instruction. Rewriting them would falsify the fixture.
⛔ **Do not change `scripts/capture_screenshots.py:57`.** It is the `--help` usage example; the
literal is illustrative and INV-188 governs its wording separately.

## Acceptance criteria

- [ ] `phase1-visualization.md:236` instructs capture from a `<port>` placeholder, not `8080`.
- [ ] `phase1-visualization.md:367`'s bootcamper-facing line names the port in use, not `8080`.
- [ ] The verification-report example at `:418-419` no longer teaches a literal port.
- [ ] `:255`, `:262`, `:266` and `:408` are **unchanged** — verified by `git diff`, since the
      default start command and the port-in-use instruction are correct as written.
- [ ] `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` and
      `scripts/capture_screenshots.py` are **unchanged** — verified by `git diff` showing neither
      file in the changeset.
- [ ] A test asserts no shipped module instruction file tells the guide to capture from, or the
      Bootcamper to open, a hardcoded `localhost:8080`, and it **passes on the corrected tree**.
- [ ] **Not vacuous:** the test asserts it scanned a non-zero number of instruction files, and
      names at least one file it scanned by name.
- [ ] **Negative-controlled, mutation verified to land:** restoring `8080` at `:236` fails the test;
      restoring it at `:367` fails it; the default start command at `:262` does **not** fail it.
      Revert all three.
- [ ] `tests/test_snapshot_and_capture_fidelity.py` still passes unchanged — this adds a second,
      wider guard and does not weaken the reference-server one.
- [ ] Full suite passes (baseline **1743 passed, 3 skipped, 1342 subtests**). Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108); the rule is language-agnostic (INV-002/INV-090),
      so it is stated as behaviour and not as a Python detail.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md`
- `tests/` — one new guard file.

## Source

- Audit: `production-readiness-audit`, 2026-08-12 (`Source: self-observed (assistant
  retrospective)`). Found by a **near-duplicate** scan across shipped files, filtered to pairs whose
  numbers differ — the drifted-repetition check both prior runs measured and explicitly recorded as
  not performed. The pair was `phase1-visualization.md:367` vs `phase1-query-visualize.md:476` at
  0.894 similarity, differing only in `8080` vs `<port>`.
- Evidence established by opening the files, not inferred: the four hardcoded sites, the two
  "port may differ" sites, module-07's two correct sites, the INV-172 citation at `:200-201`, and
  the guard's reference-server scope at `test_snapshot_and_capture_fidelity.py:76-81`.
- Priority: **Medium-high.** No defect on the default path, and a complete loss of the module's
  screenshots plus a dead URL handed to the Bootcamper whenever 8080 is already in use — which on a
  developer workstation is common rather than exotic.
- MCP re-check: **n/a — no Senzing fact.** No tool was called for this finding.
- Related: `specs/snapshot-port-and-dataset-wording.md` (established INV-172 and fixed the first two
  sites); `specs/deep-dive-audit-2026-07-29-minor-fixes.md`.

## Invariants introduced

**None proposed.** INV-172 already states the rule; this is an unswept site plus a guard narrower
than the invariant. Registering a second invariant would duplicate INV-172 rather than enforce it.
