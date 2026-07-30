# Deep-dive audit 2026-07-29: minor fixes (wrong-module snapshot title, unused `--dataset`, pytest cache propagation, stale ledger commits, unverified ledger claims)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issues:

## Problem

Four small, independent items from the 2026-07-29 invariant-conformance audit. None is a runtime
defect; each is a coherence or process gap. Grouped in one spec in the manner of
`specs/audit3-minor-fixes.md` and `specs/pr4-review-minor-fixes.md`; implement in any order.

**Item 1 — the Truth Set snapshot is titled after the wrong module, and `--dataset` is dead.** The
Truth Set visualization module writes the bootcamper's kept snapshot titled
`"Senzing Truth Set - System Verification"`, naming the one module INV-082 says must never touch the
Truth Set. In the same command it omits `--dataset`, so the artifact's Search / Probe note reads the
neutral fallback "the loaded data" in the single module where the dataset is unambiguous.

**Item 2 — `propagate.sh` copies `.pytest_cache/` into the public repo.** Dev test residue crosses
into the shipped tree, and the script's own `git status` review step structurally cannot show it.

**Item 3 — 66 of 199 ledger entries say `Commit: uncommitted` against a clean tree.** The field
cannot answer the one question it exists for: which commit implemented this spec.

**Item 4 — nothing verifies a ledger completion claim against the spec's own acceptance criteria.**
Two of this audit's findings were specs recorded as implemented whose criteria were never met.

## Root cause

**Item 1.** `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md:199-206`
(and again at `:241` for the live server):

```bash
python3 <viz-server-path> \
  --records src/system_verification/truthset_data.jsonl \
  --title "Senzing Truth Set - System Verification" \
  --snapshot docs/visualizations/truthset_verification.html \
  --no-serve
```

INV-082 states System Verification *"MUST NOT acquire, load, or visualize the Senzing Truth Set"*, and
INV-087 split Truth Set visualization into its own module for that reason — so the title, which ships
permanently into `docs/visualizations/truthset_verification.html` and into the recap that embeds its
screenshots, attributes the artifact to the wrong module. Separately, `grep -rn -- --dataset skills/`
returns **nothing**: `senzing_viz_server.py:1646-1649` documents the option with the example *"'the
Senzing Truth Set', 'your CUSTOMERS and REFERENCE data' … Left empty the snapshot says 'the loaded
data' — never assume the Truth Set"*, and no caller passes it. This is **not** an INV-172 breach — the
default is neutral, not a wrong claim — but the option is dead and the artifact vaguer than intended.

**Item 2.** `.claude/skills/propagate-to-public/propagate.sh:48` excludes bytecode only:

```bash
excludes=(--exclude='__pycache__/' --exclude='*.pyc')
```

while `plugins/senzing-bootcamp/.pytest_cache/` and `plugins/senzing-bootcamp/scripts/.pytest_cache/`
both exist, so `rsync -a --delete "$here/plugins/" "$dest/plugins/"` copies them. `.pytest_cache` is
also absent from the repo `.gitignore` (which lists `.history`, `__pycache__/`, `*.pyc` and the
feedback working copy). Impact is small — pytest writes a self-ignoring `.pytest_cache/.gitignore`
containing `*`, so the copies stay ignored in the public repo — but that is precisely why the script's
`git status --short` review step cannot surface them, leaving the maintainer no way to notice test
residue crossing into the shipped tree (INV-108's concern).

**Item 3.** `specs/IMPLEMENTED.md` carries 199 `## <spec-name>` entries; 66 end with
`- **Commit:** uncommitted`. The tree is clean apart from the deliberately-untracked `auto-test` skill
(`specs/todo.md`), so that work is committed and the field is stale.

**Item 4.** Two specs' criteria were never met while the ledger recorded them as done:

| Spec | Unmet criterion | Ledger |
|---|---|---|
| `relocate-integration-deployment-questions-to-module1.md:48` | "…read by the Module 1 problem statement **and by graduation**" | `IMPLEMENTED.md:2041`, 2026-07-22 — `graduation/SKILL.md` not in Files-changed |
| `defer-commonmark-to-graduation.md:78` | "…and over the generated `production/*.md` files" | `IMPLEMENTED.md:2588`, 2026-07-16, commit `d69c360` |

Both established invariants (INV-097, INV-060) that then stood unimplemented for weeks, and neither
invariant is cited by any test. `IMPLEMENTED.md`'s own rule — a spec is done **iff** it has a heading
there — makes that heading a strong claim with no verification behind it.

## Proposed change

**Item 1.**

- Retitle to `"Senzing Truth Set"` (or `"Senzing Truth Set - Visualization"`) at `:199-206` and `:241`,
  and wherever the title is echoed in prose.
- Pass `--dataset "the Senzing Truth Set"` in the snapshot invocation, and state in
  `visualization-api-reference.md` that a language-native server's build mode takes the same
  caller-supplied dataset wording (INV-172 binds any language, INV-090).
- In Module 7 (`phase1-query-visualize.md`), state what dataset wording is passed for the
  bootcamper's own data — or that it is deliberately left empty, and why.
- **Leave the filename `truthset_verification.html` alone.** `graduation/SKILL.md:347-351` maps
  screenshots to modules by that base name and older recaps reference it; renaming buys nothing
  bootcamper-visible and breaks that mapping. Note the reason inline so a future audit does not
  re-raise it.

**Item 2.** Add `--exclude='.pytest_cache/'` to `propagate.sh`'s `excludes`; add `.pytest_cache/` to
the repo `.gitignore`; record the exclusion in `propagate-to-public/SKILL.md`'s manifest; check
`retrofit-from-public/retrofit.sh` for the same gap.

**Item 3.** Backfill each stale entry's commit hash where determinable (`git log -S` over the entry's
Files-changed list, or the commit whose subject names the spec). Where genuinely undeterminable, write
`committed (hash not recorded)` so the two states stay distinguishable. Add one line to
`implement-spec/SKILL.md`: an entry written before its commit exists is recorded `uncommitted` **and**
updated with the hash on the next `implement-spec` run.

**Item 4.**

- **Criteria-coverage check at ledger time.** `implement-spec/SKILL.md` requires that before the ledger
  entry is written, each `- [ ]` acceptance criterion is walked and either shown satisfied (naming the
  file/line or test that proves it) or recorded as a deviation. The skill already records deviations
  richly; this makes the criteria the checklist rather than the spec's narrative.
- **A mechanical guard for the commonest shape.** Assert that for each ledgered spec, every path in
  that spec's `## Affected files` appears in the entry's Files-changed list or is explained. Both
  findings above trip it: `graduation/SKILL.md` is named in the relocate spec's affected files and
  absent from its ledger entry.
- **Invariant-to-test coverage report.** 97 of 181 invariants are cited by no test file. That is not
  itself a defect — many are enforced by tests citing them by name rather than number — but it is where
  these two hid. Produce a maintainer-facing report (not a failing test) listing them, so an audit can
  see where to look.

## Acceptance criteria

- [ ] **(1)** No bootcamper-facing Truth Set visualization artifact is titled "System Verification".
- [ ] **(1)** The Truth Set snapshot invocation passes `--dataset "the Senzing Truth Set"`, and Module 7
      states what it passes and why.
- [ ] **(1)** `visualization-api-reference.md` states the dataset wording is caller-supplied for a
      server in any language (INV-172/INV-090).
- [ ] **(1)** `docs/visualizations/truthset_verification.html` keeps its filename, with an inline note
      on why, and `tests/test_snapshot_and_capture_fidelity.py` still passes.
- [ ] **(2)** `propagate.sh` excludes `.pytest_cache/`; a run over a tree containing one copies nothing
      from it; `.gitignore` lists it; the manifest in `propagate-to-public/SKILL.md` records it; and
      `retrofit.sh` is checked for the same gap.
- [ ] **(3)** No `IMPLEMENTED.md` entry says `uncommitted` while its changes are committed, and
      `implement-spec/SKILL.md` states the update-on-next-run rule.
- [ ] **(3)** `tests/test_spec_ledger_invariants.py` asserts a `Commit:` field is a plausible hash,
      `uncommitted`, or `committed (hash not recorded)` — no other free text.
- [ ] **(4)** `implement-spec/SKILL.md` requires per-criterion verification before ledgering and says an
      unsatisfiable criterion is recorded as a deviation rather than left silent.
- [ ] **(4)** A test asserts each ledgered spec's `## Affected files` paths are accounted for in its
      entry's Files-changed list or explained.
- [ ] **(4)** A maintainer-facing report lists invariants cited by no test, documented where the audit
      workflows (`dry-run`, `auto-test`) will find it.
- [ ] **(4)** The two mis-ledgered entries are corrected by **appending**, never by rewriting their
      text (INV-181's append-not-edit discipline).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — items 1-4
      are Markdown guidance, a shell exclude, and maintainer tooling; none is OS- or language-specific.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — item 1
  (`:199-206`, `:241`).
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` —
  item 1 (caller-supplied dataset wording, any language).
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  item 1 (Module 7's dataset wording).
- `.claude/skills/propagate-to-public/propagate.sh` (`:48`),
  `.claude/skills/propagate-to-public/SKILL.md`,
  `.claude/skills/retrofit-from-public/retrofit.sh`, `.gitignore` — item 2.
- `specs/IMPLEMENTED.md` — items 3 and 4.
- `.claude/skills/implement-spec/SKILL.md` — items 3 and 4.
- `tests/test_spec_ledger_invariants.py` — items 3 and 4.

## Source

- Feedback: n/a — found by the deep-dive invariant-conformance audit of 2026-07-29, run at the
  maintainer's request; `Source: self-observed (assistant retrospective)`.
- Priority: **Low** for items 1-3; **Medium** for item 4 — it is the process gap that let two
  invariants stand unimplemented while recorded as done, and the reason the rest of this batch exists.
- MCP re-check: n/a (no Senzing fact in any item). Server **1.32.2** confirmed current at triage time
  via `get_capabilities`, 2026-07-29.
- Upstream: not applicable.
- Related specs: `specs/graduation-reads-integration-and-deployment-answers.md` and
  `specs/normalize-production-markdown-at-graduation.md` (the two findings item 4 generalizes),
  `specs/snapshot-port-and-dataset-wording.md` (INV-172, item 1),
  `specs/split-truthset-visualization-into-standalone-module.md` (INV-087, item 1),
  `specs/module3-synthetic-verification-data.md` (INV-082, item 1),
  `specs/write-gate-tests.md` (INV-108, item 2), and the `invariant-drift-guards` ledger entry in
  `specs/IMPLEMENTED.md` (item 4's predecessor in spirit; recorded there directly, with no spec file).

## Deviations from this spec, and why (2026-07-29)

- **Item 1's contract criterion was already half-satisfied.**
  `visualization-api-reference.md:643-651` already stated the general rule (derive the port from
  the parsed value, "take the dataset wording from the caller — defaulting to neutral wording").
  What was missing was the actionable half, so that is what was added: the server MUST **accept**
  the wording as an argument (spelling left to the language, INV-090) and the caller MUST **pass**
  it. Recorded because the criterion reads as though nothing was there.
- **An existing guard rejected the first version of item 1's provenance citation.** The edit first
  cited the dataset name as ``get_capabilities`` → ``get_sample_data``'s ``truthset``, and
  `tests/test_truthset_acquisition_call.py` failed it: a bare `get_sample_data` mention in that
  module must sit beside its required parameter, or a reader learns to call it without one. Rewritten
  as `get_sample_data(dataset='truthset')`, which is both the correct call shape and the provenance.
  The guard was right and is left untouched.
- **Item 4's affected-files test is forward-only, not corpus-wide.** The criterion says "a test
  asserts each ledgered spec's `## Affected files` paths are accounted for". Implemented as a gate
  from `AFFECTED_CUTOFF = 2026-07-29` plus a whole-corpus **report**, because a spec's Affected
  files is a *prediction* and the ledger's Files-changed is the *outcome*: a prediction that did not
  come true is frequently the correct result, and **38 of 181** pre-existing entries carry one. A
  corpus-wide gate would be unsatisfiable-by-construction on legitimate input — the shape INV-144
  and INV-173 forbid — so the debt is made visible rather than made blocking. Two entries dated on
  the cutoff day itself are named in `AFFECTED_GRANDFATHERED` with their reasons, following the
  existing `GRANDFATHERED` precedent in the same file.
- **A discovery item 3 did not anticipate: 17 recorded hashes no longer resolve.** Beyond the 66
  `uncommitted` fields, 17 hashes recorded by hand (e.g. `d69c360`, `0cf7e9f`, `9391bf1`) name
  commits absent from the current history — it was rewritten at some point and orphaned them. They
  are **left as written** and documented in the ledger header: a hash that once meant something is
  better evidence than a blank, and the test therefore validates the field's *vocabulary*, not
  whether a hash resolves.
- **The 67 backfilled hashes are derived, not recovered.** The rule is "the commit that added this
  entry's `## <name>` heading to `IMPLEMENTED.md`", which in this repo is the commit carrying the
  implementation (spot-checked on three entries; resolved by hand for the one case where two
  headings share a prefix, `deep-dive-audit-2026-07-28` vs `-28b`). Every inserted hash was verified
  to resolve. Stated in the ledger header so no reader mistakes them for contemporaneous records.
  One entry was compound rather than bare (`dry-run-phase3-interaction-prose-defects`, "pass 2
  uncommitted") and was completed to `` `1235fa3` (pass 1), `c89c7f2` (pass 2) `` — 67 fields
  updated, not 66.
- **A first version of the report test was self-invalidating.** It asserted the invariants report
  still named INV-060 and INV-097 — but writing those IDs into a test file makes that file cite
  them, so the report correctly stopped listing them and the test failed on its own text. Replaced
  by an assertion of the report's *property* (everything it calls uncited is defined in
  INVARIANTS.md and appears in no `tests/*.py`). The same realization is recorded in the report
  itself: "cited" is a proxy for "asserted", a comment mention satisfies it, so the report
  **under-reports** — a hit is strong evidence of a gap, a miss is weak evidence of coverage.
- **Two files changed that the spec did not list:**
  `.claude/skills/dry-run/coverage_reports.py` (new — the reports item 4 asks for, placed with the
  audit tooling per the criterion's "where the audit workflows will find it"),
  `.claude/skills/dry-run/SKILL.md` (documents them in "Before you start"), and
  `tests/test_coverage_reports.py` (new — the reports are apparatus, and apparatus nothing executes
  rots silently; INV-175's discipline).
- **Not runtime-verified:** nothing. Every item was exercised — the rsync exclude against a
  purpose-built tree containing both cache directories, both new ledger guards by mutation (free
  text in a `Commit:` field; a post-cutoff entry omitting a predicted file, which reproduced the
  INV-097 shape verbatim), and both reports by execution from an unrelated working directory.

## Invariants introduced

- `INV-182` — A spec MUST NOT be recorded as implemented in `specs/IMPLEMENTED.md` until each of its
  `## Acceptance criteria` has been checked individually with its evidence named; a criterion that
  cannot be proven is recorded as a deviation or as not-runtime-verified rather than ticked, and a
  criterion naming a file, a module, or a second consumer is verified by opening that file. Item 4's
  standing rule — items 1-3 established none (a one-off content fix, a restoration of INV-108's
  intent, and a data cleanup). Recorded in `specs/INVARIANTS.md`, maintainer-approved 2026-07-29.
