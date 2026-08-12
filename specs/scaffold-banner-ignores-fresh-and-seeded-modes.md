# The dry-run scaffold's fixture banner is static, so `--fresh` and `--seeded` over-claim coverage

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`.claude/skills/dry-run/scaffold_project.py` prints a fixture-to-invariant map whose stated purpose
is to tell the operator what the project exercises — `dry-run/SKILL.md` introduces it as *"The
scaffold prints which fixture exercises which invariant. Each one is there because a naive fixture
hid a defect."* The map is **static** and printed in every mode, while the fixtures it describes are
created in only one.

Run 2026-08-12 with `--fresh`, the banner claimed 8 fixtures; the project contains **4 files**:

| Banner claims | `--fresh` reality |
|---|---|
| `config/bootcamp_progress.json` — *"mid-module so resume paths run"* | present but `{}` — **no** module, no resume path |
| ↳ `docker_containers` — *"names an ABSENT container -> warn-and-continue (INV-101)"* | **no such key** — progress is empty |
| `config/bootcamp_preferences.yaml` — *"saved verbosity + language to test honor-don't-ask (INV-133)"* | present but **empty** — the exact opposite |
| `docs/bootcamp_recap.md` — *"a completed section carrying all four subsections (INV-103)"* | **absent** |
| `docs/progress/recap_checkpoint.md` — *"an UNFINALIZED block -> fold idempotency, run it 3x (INV-059)"* | **absent** |
| `docs/loading_strategy.md` — *"deliberately messy Markdown for the normalizer (INV-060)"* | **absent** |
| `src/system_verification/records.jsonl` — *"records for the viz server's snapshot build"* | **absent** |
| `docs/feedback/…FEEDBACK.md` — *"a precious entry (INV-067)"* | present ✅ |
| `config/engine_config.json` — *"minimal settings"* | present ✅ |

**The `--fresh` preferences line is not merely stale, it is inverted.** The banner says the file holds
saved preferences "to test honor-don't-ask (INV-133)". In `--fresh` it is empty, which is the whole
point of that mode. `phase3-conversational.md` is explicit about why the distinction matters: a walk
where everything was asked *"exercises the honor path **only in its inert direction** — it shows the
rule does not fire when it shouldn't, and says nothing about whether it fires when it should"*, which
is why a separate `--seeded` walk exists. A banner telling the operator that `--fresh` carries seeded
preferences invites precisely the false conclusion that doc was written to prevent.

**`--seeded` over-claims too**, in the same way: its preferences line happens to be true, but the
recap, checkpoint, messy-Markdown and records lines are all false, so a seeded walk still reads as
though INV-059/INV-060/INV-103 coverage came with it.

**Why this is worth a spec despite being maintainer tooling.** `dry-run/SKILL.md`'s own reporting
rules say ⛔ *"State the coverage limits explicitly"* and call an unstated limit *"the difference
between a report and a false clean bill of health"*. The banner is the operator's primary input for
writing that section, and in two of three modes it inflates it. The failure is silent and reads
authoritative — the same stale-enumeration class the audit skill ranks fourth, here in tooling rather
than in a doc.

Nothing a Bootcamper sees is affected: `.claude/` is not propagated to the public repo
(`propagate.sh` mirrors `plugins/`, `.claude-plugin/`, `docs/` and `README.md` only).

## Root cause

`scaffold_project.py:259-305`. `build()` branches correctly — `if fresh or seeded:` writes only
`bootcamp_progress.json` (`{}`) and `bootcamp_preferences.yaml` (seeded content or empty), while the
`else:` branch writes the recap, checkpoint, messy Markdown and records. It then calls `explain()`
unconditionally at `:305`, and `explain()` (`:249-256`) iterates the module-level `FIXTURE_MAP`
(`:236-246`) with no reference to the mode.

So the data structure describes one mode and the printer is shared by three. The two halves were
correct when written — `--fresh` and `--seeded` were added later, and the banner was not revisited.
No test covers the tooling's own output, which is consistent with it being tooling, and is why the
divergence was invisible.

## Proposed change

Make the banner report what was actually created, rather than a fixed list.

1. **Tag each `FIXTURE_MAP` entry with the modes it applies to** (e.g. a third element:
   `{"mid"}`, `{"fresh", "seeded"}`, or all three), and have `explain(mode)` print only the matching
   rows.
2. **Give the two mode-dependent files their own per-mode descriptions**, since the same path means
   different things: `bootcamp_progress.json` is *"mid-module so resume paths run"* under `mid` and
   *"empty `{}` — hooks see an active but unstarted bootcamp"* under fresh/seeded;
   `bootcamp_preferences.yaml` is *"saved verbosity + language to test honor-don't-ask (INV-133)"*
   under `mid`/`seeded` and *"deliberately EMPTY — every question must be asked (the inert direction
   of INV-133)"* under `fresh`.
3. **Derive the printed list from disk where practical** — the strongest version walks the created
   tree and prints a line per file actually written, so the banner cannot drift from `build()` again.
   If that is more churn than wanted, (1) plus a test is sufficient.
4. **`--explain` needs a mode too.** It currently prints the map without writing anything
   (`:331`, `:344-351`); it should either take the mode flags or state which mode it is describing.

## Acceptance criteria

- [ ] `--fresh` prints no line for `docs/bootcamp_recap.md`, `docs/progress/recap_checkpoint.md`,
      `docs/loading_strategy.md` or `src/system_verification/records.jsonl`, and no
      `docker_containers` / INV-101 line.
- [ ] `--fresh` describes `bootcamp_preferences.yaml` as deliberately empty, not as carrying saved
      preferences — the inverted claim is gone.
- [ ] `--seeded` prints the preferences line as seeded **and** omits the four mid-only fixtures.
- [ ] Default (mid-bootcamp) output is unchanged — it is the mode the current banner already
      describes correctly.
- [ ] A test asserts every path the banner prints for a mode **exists** in a project built in that
      mode, and that every file `build()` writes is described. Run for all three modes, so the
      banner cannot drift from `build()` again. Negative-controlled: adding a fixture to `build()`
      without a banner entry (or vice versa) fails, with the mutation verified to land.
- [ ] `--explain` either accepts the mode flags or names the mode it describes.
- [ ] Stdlib-only, no `plugins/` import (INV-108); holds on Linux, macOS and Windows (the scaffold
      is `pathlib`-based and must stay so).

## Affected files

- `.claude/skills/dry-run/scaffold_project.py` — `FIXTURE_MAP` (`:236-246`), `explain()`
  (`:249-256`), the `explain()` call (`:305`), and the `--explain` path (`:331`, `:344-351`).
- `tests/` — the banner/`build()` agreement test.
- `.claude/skills/dry-run/SKILL.md` — only if the "Build the project first" text needs to match the
  new per-mode output.

## Source

- Dry run: `dry-run` phase 3 setup, 2026-08-12 (`Source: self-observed (assistant retrospective)`).
  Found on the `--fresh` scaffold call itself: the banner listed a mid-module recap and seeded
  preferences, and `find` showed 4 files. `build()` is **correct** — only the banner is wrong, which
  is what makes it a reporting defect rather than a fixture defect.
- Priority: **Low-medium.** No Bootcamper impact and no wrong fixture; the cost is that a dry-run
  operator writing the mandatory coverage-limits section is handed an inflated list, and the
  invariants over-claimed (INV-059, INV-060, INV-101, INV-103) are exactly the ones the mid-bootcamp
  fixtures exist to reach.
- MCP re-check: **n/a — no Senzing fact.** Internal tooling only; no tool called for this finding.
- Upstream: not applicable.
- Related specs: none. (`specs/inv050-tree-has-no-reachability-guard.md` is the same
  stale-enumeration class in a different artifact, if a reader wants the precedent.)
