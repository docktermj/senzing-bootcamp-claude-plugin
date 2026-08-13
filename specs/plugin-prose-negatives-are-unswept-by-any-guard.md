# Nothing sweeps shipped plugin prose for an *unmarked* MCP negative

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Three mechanisms exist for dated "tool X does not contain Y" claims, and none of them can find one
in shipped plugin prose that carries **no marker**:

| Mechanism | Corpus | Blind spot |
|---|---|---|
| `coverage_reports.py negatives` | markers, wherever they are | Lists only what is **already tagged**. An unmarked negative is invisible by construction. |
| `tests/test_dated_negatives_are_marked.py` | `tests/*.py` lines matching `self.assert\w+\(` | Plugin prose is outside its corpus entirely. |
| **INV-217** | `specs/DECLINED.md` | Deliberately scoped to that one file. |

So the only thing standing between shipped prose and an unre-checkable Senzing negative is someone
reading it. On 2026-08-13 that is exactly what happened: four dated `sdk_guide` absence claims in
`module-02-sdk-setup/SKILL.md` were found by reading, having survived two server minor versions
(`module02-dated-negatives-about-sdk-guide-carry-no-marker`). Those four are now marked. **That
proves the surface is unswept, not that it is clean** — the same read found them only because the
sweep happened to pass through that file.

The consequence is the one the marker convention exists to prevent, and it has already landed twice
(`senz7221-now-names-its-own-remedy`, `explain-error-code-now-owns-senz7426`): the suite is offline
(INV-108), so nothing notices when the server gains coverage the plugin routed around, and the
second time the stale claim was in the **guards** too, so correcting the prose failed the suite.

## Root cause

The convention was built from the test side. `test_dated_negatives_are_marked.py` was written when
the observed defect was a *guard* encoding a stale claim, so its corpus is `tests/`. The report was
built to prioritise re-checking, so its input is markers. Neither was ever pointed at the largest
surface — 42 shipped markdown files, 127,803 words — and INV-217 closed the gap for `DECLINED.md`
only, because that file had the additional property of having no re-verification path at all.

## Proposed change

**Add a guard over shipped markdown, and make the discriminator the *date*, not the absence.**

The design problem that has blocked this: plugin prose legitimately discusses absences, and a naive
scan flags correct writing. INV-192's rule contains the sentence *"the payload of a gate is empty by
design, not because the topic is undocumented"* — a true statement about emptiness that must never
require a marker.

The proposed discriminator resolves it: require a marker only where a line carries **all three** of

1. a named MCP tool,
2. absence vocabulary, **and**
3. a **date or server version**.

A *dated* absence about a named tool is precisely the claim shape that expires and that a dry run
must re-ask. Undated prose explaining how a tool behaves is not a re-checkable claim and needs no
marker. Every one of the four defects found on 2026-08-13 carried a date (`2026-07-31`); INV-192's
"empty by design" sentence carries none.

Reuse rather than reinvent: import the marker grammar from `coverage_reports.py` (as
`tests/test_declined_ledger.py` already does) so there is one definition of a well-formed marker,
and reuse the block-level `MCP-NEGATIVE-SCAN: quoted-history` escape for prose that quotes a
retracted claim.

**Disclose the limit rather than implying completeness:** the absence vocabulary is a phrase list and
is evadable by paraphrase. Say so in the guard, as `tests/test_declined_ledger.py` does.

## Acceptance criteria

- [ ] A test asserts that every line in shipped markdown carrying a named MCP tool **and** absence
      vocabulary **and** a date or server version also carries a parseable `MCP-NEGATIVE` marker
      (with its `owner:` clause) in the same block.
- [ ] The four now-marked claims in `module-02-sdk-setup/SKILL.md` pass, and removing any one of
      their markers fails the guard — **negative-controlled, each mutation verified to land**.
- [ ] INV-192's *"the payload of a gate is empty by design"* sentence does **not** trigger the
      guard, and a test pins that as a deliberate non-trigger so the discriminator cannot be
      widened into uselessness.
- [ ] The marker grammar is **imported** from `.claude/skills/dry-run/coverage_reports.py`, not
      restated.
- [ ] The `quoted-history` escape is honoured, so a correction can restate what it corrects.
- [ ] The guard's docstring states that the vocabulary is a phrase list and evadable by paraphrase,
      and names the marker as the durable route.
- [ ] Stdlib-only, imports nothing from `plugins/`, exits via `unittest` (INV-108).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `tests/` — one new guard over shipped markdown.
- Possibly `.claude/skills/dry-run/SKILL.md` — note the new coverage in "Before you start", as the
  `DECLINED.md` addition did.

## Source

- Feedback: none — self-observed during the 2026-08-13 `production-readiness-audit` and the
  `module02-dated-negatives-about-sdk-guide-carry-no-marker` implementation
  (`Source: self-observed (assistant retrospective)`).
- Priority: **Medium-High.** It is a class defect on the repo's only stale-negative detector,
  covering its largest surface, and the class has already shipped twice. No bootcamper-facing
  content changes.
- MCP re-check: **n/a (no Senzing fact)** — this spec changes which files a stdlib guard reads. The
  Senzing facts of the four instances were re-verified at 1.32.9 on 2026-08-13 in
  `module02-dated-negatives-about-sdk-guide-carry-no-marker`.
- Upstream: not applicable.
- Related specs: `module02-dated-negatives-about-sdk-guide-carry-no-marker` (the four instances),
  `declined-ledger-negatives-are-invisible-to-the-scanner` (INV-217, the same hole closed for one
  file), `guards-pinning-a-dated-negative-outlive-it`, INV-209 (marker form), INV-108 (offline
  suite), INV-192 (the sentence that must not trigger).
