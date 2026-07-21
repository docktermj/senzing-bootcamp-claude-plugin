# Clear the low/cosmetic deep-dive audit findings (#6/#7/#8)

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvements:

## Problem

The deep-dive audit surfaced three low/cosmetic items, parked in `specs/todo.md`:

- **#6 Name-leading transition prose (INV-079 polish).** A few bootcamper-facing spots lead with a
  module **number** instead of its name near transitions.
- **#7 Interaction polish (INV-006/008/009).** Module 3 asks "done exploring?" twice (once at the
  end of the Truth Set visualization, again before cleanup), and a Module 1 question is compound.
- **#8 Convention/cosmetic tidy.** Three hook docstrings don't begin with "to"; the viz-server env
  step shows only the `.sh` env script (no Windows `.bat`); a `capture_screenshots.py` docstring
  uses a bare `pip install`.

## Root cause

Confirmed locations:

- #6: `skills/module-05-data-quality-mapping/phase3-test-load.md:155,159,163,169-170` (path labels
  and options lead with "Module 7"/"Module 6"); `skills/module-01-business-problem/phase2-document-confirm.md:145`
  (ascending-numeric-order lead-in prose).
- #7 double-ask: `skills/module-03-system-verification/phase2-visualization.md:198` ("Take your
  time exploring… I'll continue with cleanup") and `skills/module-03-system-verification/phase3-report-close.md:131`
  ("Have you finished exploring the visualization?…") — the Step 10 report between them is silent,
  so the same "done?" gate is asked twice.
- #7 compound question: `skills/module-01-business-problem/phase1-discovery.md:243` ("…interface
  with other software…? If so, which systems?") bundles a yes/no with a follow-up.
- #8: `scripts/session-start.py`, `scripts/write-gate.py`, `scripts/stop-nudge.py` module docstrings
  (purpose clause not "to"-prefixed); `skills/module-03-system-verification/phase2-visualization.md:102-105`
  (only `source src/scripts/senzing-env.sh`, though Module 2 also creates `senzing-env.bat`);
  `scripts/capture_screenshots.py:17` (`pip install playwright` in a docstring comment).

## Proposed change

- **#6:** Reword the module-05 path labels/options and the module-01 lead-in to name the module
  (name optional-number), e.g. "Shortcut path — go directly to Query, Visualize and Discover".
- **#7 double-ask:** Make the end-of-Truth-Set-visualization gate the single "done exploring?"
  question; in Step 11, proceed directly to cleanup (do not re-ask — INV-006), keeping the
  no-web-server skip case.
- **#7 compound:** Split the Module 1 software-integration question into a yes/no, then a
  "Which systems?" follow-up only on yes.
- **#8:** Make the three hook docstrings' purpose clause begin with "to"; add a Windows
  `senzing-env.bat` line beside the `.sh` env step; change the `capture_screenshots.py` docstring
  hint to `python3 -m pip install playwright`.

## Acceptance criteria

- [ ] The module-05 path options and module-01 lead-in name the next module (no bootcamper-facing "Module N" lead); INV-079 holds.
- [ ] Module 3 asks "done exploring?" exactly once (INV-006); Step 11 proceeds to cleanup without re-asking, preserving the no-web-server skip.
- [ ] The Module 1 software-integration question is a single yes/no, with "Which systems?" asked only on yes (INV-008/009).
- [ ] `session-start.py`, `write-gate.py`, `stop-nudge.py` docstrings begin their purpose clause with "to"; the viz-server env step names the Windows `.bat`; `capture_screenshots.py` docstring uses `python3 -m pip`.
- [ ] Hook scripts still `py_compile`; behavior unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md`
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md`
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md`
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md`
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase3-report-close.md`
- `plugins/senzing-bootcamp/scripts/session-start.py`, `write-gate.py`, `stop-nudge.py`, `capture_screenshots.py`

## Source

- Audit (deep-dive conformance/coherence review), 2026-07-19 — findings #6/#7/#8 (LOW/cosmetic).
- Priority: Low.
- Related specs: `module-references-by-name-not-number.md` (INV-079), `interaction-or-questions.md` (INV-051), `cross-platform-hook-execution.md` (INV-052). The INV-016 wording-clarification sub-item is handled separately (it edits the canonical ruleset).
