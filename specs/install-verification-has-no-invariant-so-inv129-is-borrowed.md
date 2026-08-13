# "An installer's exit code is not evidence" is an unregistered rule, and INV-129 is borrowed for it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 2 states a durable rule about verifying an **install**, twice, with two different
authorities — one of them out of scope and one of them absent:

1. `module-02-sdk-setup/SKILL.md:197` — a hard `⛔` rule citing **no** invariant:

   > ⛔ **A ZERO EXIT CODE FROM `brew` DOES NOT MEAN IT INSTALLED.** If the EULA variable's name or
   > value is wrong the cask prints "No interactive terminal detected", purges the download, then
   > **still prints its Caveats block listing install paths** — so it reads as success while
   > installing nothing.

2. `module-02-sdk-setup/SKILL.md:287` — the same rule, citing **INV-129**:

   > 2. **Probe the platform artifact** as shown above — exit 0 is not evidence (INV-129).

**INV-129 does not reach an install.** Its subject is a rendered deliverable:

> **INV-129** — A step that produces a bootcamper-facing **deliverable (PDF, PNG, HTML artifact)**
> MUST verify the **rendered artifact**, not only the exit status and any self-reported metric:
> inspect the output for content the step knows must be present — rasterize the page, open the
> image, probe the extracted text positively, count unique objects.

An SDK install is not a PDF, PNG or HTML artifact, and "rasterize the page / open the image" cannot
be applied to it. The *principle* transfers; the invariant's text does not. So `:287` is defect
class 5 from this skill's own list — a cross-reference to an invariant whose subject does not match
the claim — joining the two already on record (INV-077 cited where INV-129 governs; INV-076 cited
for the name rule).

**The rule itself is real, load-bearing, and applied in at least four places** — so the plugin
guarantees something the ruleset does not record:

| Site | The artifact probed instead of the exit code |
|---|---|
| `:203` | `test -f "$(brew --prefix)/opt/senzing/er/lib/libSz.dylib" && ls …/data/*TransRules.sz` |
| `:222` | `Test-Path "$env:SENZING_DIR\lib\Sz.dll"` |
| `:287` | "Probe the platform artifact … exit 0 is not evidence" |
| `:1007-1017` | `Test-Path` on the SUPPORTPATH directory, both candidate locations |

The server states the same rule independently, which is why it matters: `sdk_guide(topic='install',
platform='macos_arm')` — **server 1.32.9, 2026-08-13** — opens its gotchas with *"A ZERO EXIT CODE
FROM brew install DOES NOT MEAN THE SDK INSTALLED… ALWAYS verify before proceeding"*, and the
Windows response carries the parallel `SENZ7426`/SUPPORTPATH trap where *"SzProduct still works
because it needs no support data, so the install LOOKS healthy."*

## Root cause

The reverse direction of the invariant contract: a durable rule shipped and registered no
invariant, so the nearest-looking ID was borrowed. This is the same mechanism as **INV-134** (the
silent name-detection rule shipped unregistered, and two files then cited INV-076 — an invariant
about the Core-vs-Customized path choice) and **INV-155** (two specs removed tabs, registered
nothing, and the shipped app contradicted INV-104's enumeration).

`conformance.py rules` surfaces the `:197` half — it is one of the 15 hard-rule lines in a section
citing no invariant — but it cannot see the `:287` half, because that line *does* cite an invariant
and the scan only checks that a citation exists, not that it is the right one. Only reading finds
the second half, which is why the count moved from 16 to 15 while the defect stayed.

## Proposed change

**Register the rule, then fix the citation.** Two steps, in this order:

1. **Propose an invariant** (maintainer sign-off required before recording — `INVARIANTS.md` is
   append-only and needs the next unused ID plus an index entry in the same edit). Draft wording:

   > A step that **installs or updates software** MUST verify the installed artifact on the
   > filesystem rather than the installer's exit status: a zero exit, printed install paths, or a
   > "success" line are necessary and insufficient, because a package manager can purge a download
   > and still print its caveats. The artifact probed MUST be named for the Bootcamper's platform,
   > and where it cannot be probed the outcome is reported as undetermined (INV-163), never as
   > installed.

2. **Re-point `:287`** at the new ID and **add the citation at `:197`**, so both statements of the
   rule name the same authority.

⛔ **Do not edit INV-129 to cover installs.** Widening its subject from "bootcamper-facing
deliverable (PDF, PNG, HTML artifact)" to "anything produced" is a change of meaning, which
`INVARIANTS.md` rule 2 forbids in place — it would be a new invariant with a new ID anyway, and
editing it would silently alter what its **15+ existing citations** resolve to.

**What stays:** every command, every probe, and the whole `:197` explanation of *why* brew reads as
success. Nothing about the guidance's behaviour changes — this makes the authority match the rule.

## Acceptance criteria

- [ ] A new invariant records the install-verification rule, worded and approved by the maintainer,
      appended with the next unused `INV-NNN` and an index entry in the same edit.
- [ ] `:287` cites the new invariant rather than INV-129.
- [ ] `:197` cites the same new invariant.
- [ ] **INV-129 is not edited**, not renumbered, and its text still scopes itself to rendered
      deliverables.
- [ ] `conformance.py rules` no longer reports `module-02-sdk-setup/SKILL.md:197`, and the total of
      uncited hard-rule lines drops by exactly one (15 → 14) with no other line appearing.
- [ ] A test asserts both sites cite the new ID — **negative-controlled** by reverting one citation
      to INV-129 and confirming failure.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — citations at `:197` and `:287`.
- `specs/INVARIANTS.md` — one new invariant, appended, plus its index entry.
- `tests/` — a guard on the two citations.

## Source

- Skill: `production-readiness-audit`, 2026-08-13. The `:197` half came from
  `conformance.py rules`; the `:287` half came from reading, and is invisible to that scan by
  construction.
- Priority: Medium. Nothing a Bootcamper does breaks — every probe is present and correct. The
  defect is that the ruleset does not bind the guarantee, so a future change can remove a probe
  without contradicting anything, and one site's citation misdirects a reader to an invariant about
  PDFs.
- MCP re-check: server **1.32.9**, 2026-08-13 — `sdk_guide(topic='install', platform='macos_arm')`
  independently states the zero-exit-code trap, confirming the rule is not merely a plugin
  convention. No Senzing fact in this spec is taken from another spec or the ledger (INV-080).
- Related: INV-129 (the deliverable rule being borrowed), INV-163 (report what could not be
  verified), INV-134 and INV-155 (the same unregistered-rule mechanism), and
  `specs/step1-filesystem-fallback-is-linux-only.md`, found in the same sweep and touching the same
  step's platform handling.

## Invariants introduced

- `INV-218` — A step that **installs or updates software** MUST verify the installed **artifact on
  the filesystem** rather than the installer's exit status; the artifact probed MUST be named for the
  Bootcamper's platform, and where it cannot be probed the outcome is reported as **undetermined**
  (INV-163), never as installed. INV-129 governs the parallel rule for rendered deliverables and is
  named in INV-218 as the sibling it is distinguished from. (Recorded in `specs/INVARIANTS.md`,
  indexed under **Platform, shell, encoding and file placement** beside INV-168, approved by the
  maintainer 2026-08-13.)

## Deviations from this spec, and why (2026-08-13)

Implemented as written. One file changed that this spec does not list, for the reason the spec
itself predicted.

**`tests/test_sdk_update_offer.py:349` asserted `INV-129` appears in Step 1b**, so re-pointing the
citation turned the suite red — the guard was pinning the very wrong-citation this spec exists to
correct, and it is what kept it alive. Updated to assert `INV-218`, with the correction recorded in
its docstring; the assertion's *purpose* (verification after an update is mandatory and cites its
governing rule) is unchanged. This is the second instance today of a guard pinning a claim rather
than a property — the first was `test_sdk_update_offer.py:195` in
`module02-dated-negatives-about-sdk-guide-carry-no-marker`, in the same file.
