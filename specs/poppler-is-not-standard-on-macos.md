# poppler is not part of macOS, and the spec that established INV-163 says it is

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`graduation/SKILL.md` Step 1b groups macOS with Linux for PDF-verification tooling:
"**Linux / macOS:** poppler is usually present (`pdftoppm` / `pdftotext` / `pdfinfo` /
`pdfimages`), so the full check set normally runs," and reserves the missing-poppler case for
Windows.

On a real run — macOS 26.5.2 on Apple Silicon, **with Homebrew installed and in active use
for the Senzing SDK itself** — all four poppler binaries were absent, and poppler was not
installed as a formula. macOS ships none of them; they arrive only via an explicit
`brew install poppler`, which a Bootcamper has no reason to have run.

⚠️ **The error is not confined to the skill.** It originates in an implemented spec:
`specs/pdf-layout-verification-without-poppler.md` states poppler "is standard on Linux and
macOS and **not** present on Windows by default" (line 43) and "poppler is typically present
on Linux and macOS and typically **absent on Windows**" (line 77). That spec established
**INV-163**, so the false platform premise is carried by the invariant's own source document
and by the guidance it produced.

**What it costs.** The grouping removes exactly the two checks that spec itself identifies as
irreplaceable, on a platform where it promises the full set:

- the page raster (`pdftoppm`) — the only check that catches border-clipped glyphs;
- `pdftotext` — the only check that catches content positioned outside the page box.

And the reduced-check-set priority it gives — "keep the positive `pdftotext` content probe" —
is not actionable on macOS either, because `pdftotext` is one of the four missing binaries.

So an agent following the guidance on macOS may report the keepsake as verified having
silently run fewer checks than it believes it ran — the precise overstatement the same
section forbids ("Say what you could not verify"), and the failure INV-163 exists to prevent.
INV-129 correctly rules out installing a tool to satisfy a verification step, so macOS needs
the reduced-check-set treatment Windows already has.

## Root cause

"poppler is standard on Linux" is true, and "Linux and macOS" is the habitual pairing for
Unix-like tooling. It is wrong here: poppler is a Linux distribution package, not a macOS
system component. The claim was written into the spec, inherited by the skill, and never
tested — no test can check what is installed on a platform the suite is not running on, and
this repo's CI runs on Linux, where the claim happens to hold.

## Proposed change

1. **`graduation/SKILL.md` Step 1b** — separate macOS from Linux. State that poppler is
   **not** part of the macOS base system and is present only if the user installed it
   explicitly, so the missing-poppler path is the expected case on **both macOS and
   Windows**, and the full check set is the Linux case.
2. **Say what remains available on macOS**, so the reduced set is actionable rather than
   merely reduced: `fpdf2` brings in Pillow, so the image count via Pillow works; and the
   generator's own `embedded N of M images` line needs no external tool at all. (Note the
   companion spec `embedded-image-count-needs-an-external-denominator.md` — that line
   measures Markdown references, not tab coverage, and must not be cited as coverage
   evidence.)
3. **Correct the premise in `specs/pdf-layout-verification-without-poppler.md`** with a dated
   note rather than a rewrite: the platform claim at lines 43 and 77 was wrong for macOS,
   observed 2026-07-31 on macOS 26.5.2 with Homebrew present. The spec's substance — verify
   the artifact, never install a tool to do it, report what you could not check — is
   unaffected and stands.
4. **INV-163 needs no new ID.** Its requirement (record a skipped check, say which
   verification did not run) is unchanged; only the platform example inside it is wrong.
   Correct the example in place per `INVARIANTS.md`'s rules, with the date.

## Acceptance criteria

- [ ] No shipped file or invariant states or implies that poppler is normally present on
      macOS.
- [ ] Step 1b treats macOS and Windows together as the missing-poppler case, and Linux as
      the full-check-set case.
- [ ] Step 1b names what *is* available on macOS with no new dependency — Pillow via `fpdf2`,
      and the generator's own embedded-image line — so the reduced set is actionable.
- [ ] `specs/pdf-layout-verification-without-poppler.md` carries a dated correction of its
      platform claim; its substance and its criteria are otherwise untouched.
- [ ] INV-163's platform example is corrected in place; its ID is not renumbered and its
      MUST is unchanged.
- [ ] INV-129 is still honoured — nothing instructs installing poppler to satisfy a check.
- [ ] A test asserts that macOS is not grouped with Linux for poppler availability, so the
      habitual pairing cannot be reintroduced.
- [ ] **Not runtime-verifiable in this environment**, and disclosed as such: this repo runs
      on Linux, where poppler is present, so the macOS absence cannot be reproduced here. The
      evidence is the field observation (macOS 26.5.2, arm64, Homebrew present, all four
      binaries absent, `fpdf2` 2.8.4 present) recorded in the feedback entry, not an MCP
      source and not a local run.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1b platform note and reduced-check-set priority.
- `specs/pdf-layout-verification-without-poppler.md` — dated correction, lines 43 and 77.
- `specs/INVARIANTS.md` — INV-163's platform example, corrected in place.
- `tests/test_pdf_verification_toolchain.py` — the grouping assertion.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "graduation's PDF-verification guidance
  assumes poppler is present on macOS; on a stock macOS machine none of it is" (2026-07-31,
  Module: Graduation; `Source: self-observed (assistant retrospective)`)
- Priority: Low as reported. Worth noting the reporting entry did not know the claim came
  from an implemented spec and its invariant, which widens the fix from one skill line to
  three files.
- MCP re-check: n/a — poppler availability is a platform fact, not a Senzing fact, and no
  MCP tool owns it. Recorded as an environment observation with its version and date, never
  laundered into an MCP-sourced claim (INV-080).
- Upstream: not applicable.
- Related specs: `specs/pdf-layout-verification-without-poppler.md` (established INV-163;
  this corrects its premise), `specs/artifact-level-verification-for-deliverables.md` (INV-129).
