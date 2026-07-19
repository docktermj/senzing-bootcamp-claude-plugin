# TODO

This are ideas for future specs.

- Drop the "reconcile later / porting-phase" language around the MCP temporary-license option (INV-036 works at runtime; `submit_feedback` is live) — `module-01/phase1-discovery.md:153-155`, `module-02/SKILL.md:366-368,513-517`.
- Add the best-value model/effort prompt to each module's `First:` step enumeration for parity with graduation (source of truth stays `ground-rules.md:169-200`) — coherence nit under INV-063.
- (Audit 2026-07-19, LOW) Name-lead module references near transitions (INV-079 polish): `module-05-data-quality-mapping/phase3-test-load.md:169-170` (options lead with "Module 7"/"Module 6"), lead-in prose `module-01-business-problem/phase2-document-confirm.md:145`, `module-05-.../phase3-test-load.md:155`.
- (Audit 2026-07-19, LOW) Interaction polish: Module 3 "done exploring?" near-double-ask (`module-03-system-verification/phase2-visualization.md:198` vs `phase3-report-close.md:131`); split the compound Module 1 question (`module-01-business-problem/phase1-discovery.md:243` — ask the interface yes/no first, then "which systems?").
- (Audit 2026-07-19, cosmetic) Hook-convention tidy: make 3 hook docstrings begin with "to" (`scripts/session-start.py`, `scripts/write-gate.py`, `scripts/stop-nudge.py`); add a Windows env-sourcing note where only `.sh` is shown (`module-03-system-verification/phase2-visualization.md:102`, `.bat` exists per Module 2); change `scripts/capture_screenshots.py:17` docstring `pip install` → `python3 -m pip` (INV-066 wording); consider pinning INV-016's "documented purpose vs runtime-emitted string" interpretation into its wording in `specs/INVARIANTS.md`.
