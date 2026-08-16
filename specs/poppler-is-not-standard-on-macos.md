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
- [ ] INV-129 is still honored — nothing instructs installing poppler to satisfy a check.
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

## Deviations from this spec, and why (2026-07-31)

All four sites corrected as specified. Five things differ from the text:

1. **A fifth site: this repo's own test docstring.** `tests/test_pdf_verification_toolchain.py`
   opened by repeating the false claim verbatim — "poppler, which is standard on Linux and macOS
   and **absent on Windows by default**". The spec lists that file for the new assertion but not
   as a *source* of the claim. It is now corrected, with a note recording that it carried the
   premise and that a wording assertion is the only defense available, since no suite can check
   what is installed on a platform it is not running on.
2. **Line references drifted.** The spec cites Step 1b at `:608-616`; the block is at `:619-635`
   because commits `4cff770` and `022c4b2` added text to `graduation/SKILL.md` earlier the same
   day. `:43` and `:77` in the originating spec were confirmed exactly as cited.
3. **The macOS bullet is worded so the prohibition precedes the command.** A pre-existing guard
   (`test_does_not_instruct_installing_poppler`) requires every occurrence of
   `brew install poppler` to be preceded within 400 characters by "do not" / "never" /
   "MUST NOT" — correct, and my first draft mentioned the command *descriptively* and tripped it.
   Reworded to "you **must never install them** to make a check pass (INV-129) — they arrive only
   via an explicit `brew install poppler`…" rather than relaxing the guard. Better guidance
   anyway: a reader who sees the command sees the prohibition in the same breath.
4. **The Pillow route is verified rather than asserted.** The spec says `fpdf2` brings in Pillow;
   confirmed locally — `fpdf2` 2.8.5 declares `Pillow!=9.2.*,>=8.3.2`, and Pillow 10.2.0 imports
   in this environment. The version constraint is quoted in the guidance so a future reader can
   re-check it instead of trusting it.
5. **The reduced-set answer is better than the spec could know.** The spec notes that
   `embedded N of M images` measures Markdown references and "must not be cited as coverage
   evidence" — correct, and as of commit `022c4b2` (implemented earlier today) the generator emits
   a *separate*, manifest-derived `N of M captured tabs reached the recap`, which **is** the
   coverage figure and also needs no external tool. So on macOS the reduced set now answers both
   questions rather than only the render one. Step 1b names both and keeps them distinct.

**Criterion not ticked, as the spec itself requires:** the macOS absence is **not
runtime-verifiable in this environment**. This repo runs on Linux, where poppler is present. The
evidence is the field observation (macOS 26.5.2, Apple Silicon, Homebrew installed and in active
use, all four binaries absent, `fpdf2` 2.8.4 present) recorded in the feedback entry — an
environment observation, not an MCP source and not a local run (INV-080).

One artifact of the fix worth knowing for future audits: a grep for "poppler … present/standard …
macOS" now matches INV-163, because its correction note **quotes** the false claim in order to
retract it. That is the retraction, not a live claim.

## Invariants introduced

- None. This corrects the *platform example* inside `INV-163` in place — its ID, its MUST and its
  no-new-dependency requirement are all unchanged — and adds no new standing rule.
