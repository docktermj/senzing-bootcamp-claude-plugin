# DECLINED.md revisit notes hold dated MCP negatives no scanner can see

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`coverage_reports.py negatives` is the only mechanism in the repo that hunts stale
"this MCP tool does not contain X" claims, and it cannot see the one place where such a claim has
no other means of being re-checked. Its scan roots exclude `specs/` deliberately:

```python
#: Where a live claim can live. `specs/` and `feedback/` are records, not shipped claims.
NEGATIVE_ROOTS = ("plugins", "tests", os.path.join(".claude", "skills"), "docs")
```

(`.claude/skills/dry-run/coverage_reports.py:93-94`)

The rationale is sound for a **spec body**: a spec is a plan, and `implement-spec` Step 3.3
re-verifies every Senzing fact it asserts before any code changes. A stale negative in a spec is
caught on the way in.

It does not hold for **`specs/DECLINED.md`**, for three compounding reasons:

1. **A declined spec is never implemented, so Step 3.3 never runs on it.** The re-verification
   path that justifies excluding `specs/` does not exist for this file.
2. **`implement-spec` directs readers to trust it over the spec.** `list_specs.py`'s own output
   says: "Check DECLINED.md's `Revisit if:` clause before reopening one, and re-verify the
   condition rather than trusting the spec's original citations." So `DECLINED.md` is positioned as
   the *higher-authority* record — and it is the unscanned one.
3. **A `Revisit if:` clause exists precisely to be re-checked later.** Its entire function is to
   let a future run decide cheaply whether to reopen. A dated negative inside it that has since
   gone stale makes that recheck reach the wrong answer while looking evidenced.

This is not hypothetical. The 2026-08-13 revisit note on
`no-route-for-bootcampers-who-cannot-add-an-mcp-server` asserts that `sz-mcp-coworker` appears
nowhere in `get_capabilities` (`specs/DECLINED.md:96-98`) when it is that response's
`server_name`, and concludes the evidence "narrowed from two to one" when
`explain_error_code('SENZ9000')` still names the binary. Two dated, cited, plausible negatives —
both wrong, both invisible to `negatives`, and one of them written the same day the report ran
clean. Specced as `specs/declined-revisit-note-asserts-an-absence-from-two-surfaces.md`.

## Root cause

`NEGATIVE_ROOTS` treats `specs/` as one category ("records, not shipped claims"), but the
directory holds two kinds of file with opposite re-verification properties:

| File | Re-verified by | Scanner should see it? |
|---|---|---|
| `specs/<spec>.md` | `implement-spec` Step 3.3, at implementation | No — correctly excluded |
| `specs/IMPLEMENTED.md` | its own `MCP re-check:` field, written at implementation | No — a point-in-time record |
| `specs/DECLINED.md` | **nothing, ever** | **Yes** |

`DECLINED.md` is the exception the constant flattens. Nothing else in the repo distinguishes it,
so a negative written there is the only claim shape with neither a scanner nor a re-verification
path.

## Proposed change

1. **Bring `specs/DECLINED.md` into the negatives scan** without pulling in the rest of `specs/`.
   Add it as an explicit file-level root alongside `NEGATIVE_ROOTS` (e.g. a
   `NEGATIVE_EXTRA_FILES = (os.path.join("specs", "DECLINED.md"),)` walked by `negative_files()`),
   and update the comment on `NEGATIVE_ROOTS` to record *why* this one file is different: it is the
   only Senzing claim in the repo with no re-verification path.
2. **Require the `MCP-NEGATIVE` marker form for absence claims in a `Revisit if:` clause or a
   dated revisit note**, so they parse with an `owner:` clause like every other negative. This is
   INV-194's rule applied to the file that most needs it — the wrong-route absence in
   `DECLINED.md:96-98` would not have parsed as well-formed had the marker been required, because
   naming the owning route is what forces the author to ask it.
3. **Update `implement-spec`'s decline section** (`.claude/skills/implement-spec/SKILL.md`) so the
   `DECLINED.md` entry template shows the marker on an absence-shaped `Revisit if:`, matching the
   discipline the spec template already documents.
4. **Guard it** in `tests/test_declined_ledger.py`: every absence-shaped claim in `DECLINED.md`
   carries a parseable `MCP-NEGATIVE` marker with an `owner:` clause. Negative-control the guard by
   reintroducing the `DECLINED.md:96-98` wording and confirming it fails.

## Acceptance criteria

- [ ] `python3 .claude/skills/dry-run/coverage_reports.py negatives` reports markers found in
      `specs/DECLINED.md`, and continues to report the 3 existing plugin markers.
- [ ] The scan still ignores `specs/<spec>.md` bodies and `specs/IMPLEMENTED.md` — adding one file
      does not open the directory. Asserted by a test, not by inspection.
- [ ] The comment on `NEGATIVE_ROOTS` states why `DECLINED.md` is included when the rest of
      `specs/` is not.
- [ ] A malformed or `owner:`-less negative in `DECLINED.md` is reported as malformed, exactly as
      it would be in `plugins/` — verified by mutation, then reverted.
- [ ] `tests/test_declined_ledger.py` fails when the `DECLINED.md:96-98` wrong-route wording is
      reintroduced, and passes on the corrected file (negative control recorded).
- [ ] `implement-spec`'s `DECLINED.md` entry template shows the marker form for an absence-shaped
      `Revisit if:`.
- [ ] `coverage_reports.py` stays stdlib-only, read-only, and exit-0 whatever it finds.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/dry-run/coverage_reports.py` — add `specs/DECLINED.md` to the negatives scan
  surface; document why that one file is in scope.
- `.claude/skills/implement-spec/SKILL.md` — show the `MCP-NEGATIVE` marker form in the
  `DECLINED.md` entry template for absence-shaped `Revisit if:` clauses.
- `tests/test_declined_ledger.py` — guard that absence claims in `DECLINED.md` name their owning
  route.
- `.claude/skills/dry-run/SKILL.md` — note in "Before you start" that `negatives` now covers
  `DECLINED.md`.
- `tests/test_coverage_reports.py` — assert the new surface is scanned and that the rest of
  `specs/` still is not.

## Source

- Feedback: none — self-observed during a `/dry-run` phase 1 sweep, 2026-08-13
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium-High — it is a class defect on the repo's only stale-negative detector, and it
  has already admitted one wrong negative into a terminal-state record. Low blast radius (no
  bootcamper-facing content), high leverage on record integrity.
- MCP re-check: **n/a (no Senzing fact)** — this spec changes which files a stdlib scanner reads
  and what a test requires. The Senzing facts that motivated it are re-checked in
  `specs/declined-revisit-note-asserts-an-absence-from-two-surfaces.md`, against server 1.32.9 on
  2026-08-13.
- Upstream: not applicable.
- Related specs: `specs/declined-revisit-note-asserts-an-absence-from-two-surfaces.md` (the
  instance), `specs/mcp-negative-markers-must-name-the-owning-route.md` (INV-194, the rule this
  extends to a new file)

## Deviations from this spec, and why (2026-08-13)

Implemented as written, with one addition the spec does not name and one placement difference.

1. **Added: a block-level `MCP-NEGATIVE-SCAN: quoted-history` escape.** Proposed change 4 asks
   for a guard requiring a marker on every absence-shaped claim in `DECLINED.md`. Applied
   literally it also fires on prose that *quotes a retracted claim* — which the corrected note
   does deliberately, so the correction is legible as one. Without an escape the honest move
   (quote the wrong claim verbatim) is the one the guard punishes, and the author is pushed to
   paraphrase history instead of adding evidence. The escape mirrors the file-level
   `MCP-NEGATIVE-SCAN: ignore-file` that `coverage_reports.py` already honors, carries the same
   abuse risk, and has the same answer: it is one grep away from review.
2. **The "why" comment sits on `NEGATIVE_EXTRA_FILES`, with `NEGATIVE_ROOTS`' own comment
   extended.** Criterion 3 asks for it "on the comment on `NEGATIVE_ROOTS`". The two constants
   are adjacent: `NEGATIVE_ROOTS` now states why a spec body and `IMPLEMENTED.md` are
   *correctly* excluded (Step 3.3 re-verifies one, the other is a point-in-time record), and
   `NEGATIVE_EXTRA_FILES` states why `DECLINED.md` is the exception.
   `tests/test_coverage_reports.py` asserts the content rather than the location.
3. **Disclosed, not fixed: the guard's absence vocabulary is a phrase list and is evadable by
   paraphrase.** It catches the shapes that have actually appeared — including the wording this
   spec was written from — not every possible way to say "absent". Stated in the code comment
   rather than implied to be complete; the backstop is that `report_negatives` now reads the
   file, so a marker is the durable route and the vocabulary is only a prompt to add one.

## Invariants introduced

- `INV-217` — An absence claim recorded in `specs/DECLINED.md` — in a `Revisit if:` clause or a
  dated revisit note — MUST carry a parseable `MCP-NEGATIVE` marker in INV-209's form, `owner:`
  clause included, and `specs/DECLINED.md` MUST stay inside `coverage_reports.py`'s negatives
  scan surface while the rest of `specs/` stays out. Prose that quotes a retracted claim is
  exempt and must declare it with `MCP-NEGATIVE-SCAN: quoted-history`. (Recorded in
  `specs/INVARIANTS.md`, indexed under **The development record itself**, approved by the
  maintainer 2026-08-13.)
