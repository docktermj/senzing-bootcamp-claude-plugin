# Document PowerShell's encoding and syntax semantics — Windows is supported, its shell is not documented

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Windows is a first-class install path (Step 2 of SDK setup routes to `platform='windows'` with Scoop,
and several modules ship PowerShell command blocks alongside their bash blocks), but nothing in the
plugin documents how Windows PowerShell 5.1 — the default `powershell.exe` on Windows 11, not
PowerShell 7 — differs from bash. One session hit two classes of failure repeatedly.

### 1. Silent data corruption from PowerShell's text handling

**`-Encoding utf8` writes a BOM on PowerShell 5.1.** Writing the Truth Set JSONL with
`Out-File -Encoding utf8` prefixed the file with `EF BB BF`. The first record then failed to parse —
the BOM became part of the first JSON key. **158 of 159 records were fine**, which is the worst
possible failure shape: it reads as one bad source record, not a systemic encoding fault. Re-reading
with `utf-8-sig` and rewriting without a BOM gave 159/159.

**`Get-Content` reads UTF-8 as ANSI.** Appending to the feedback file with
`Add-Content -Value (Get-Content $src -Raw)` double-encoded every non-ASCII character: `Get-Content`
without `-Encoding` decoded the UTF-8 source as Windows-1252, then wrote that mojibake back out as
UTF-8. 25 em dashes became `â€”`.

The second is the more instructive failure, because **every obvious validity check passes**:

```text
BOM sequence count        : 0
em dashes decode cleanly  : True
replacement chars present : False
```

The file is valid UTF-8. It decodes without error. It contains no U+FFFD. It is simply wrong, and
only rendering it reveals that. It was caught by noticing that em dashes in older entries displayed
as `â€”` while a freshly written entry displayed correctly — a visual diff, not a validation check.

Both traps sit directly in the bootcamp's path: writing generated JSONL data, and appending to
Markdown deliverables. A BOM in record 1 of a data file gets misdiagnosed as bad source data. A
double-encoded recap or feedback file ships looking fine to every automated check and wrong to every
human reader.

### 2. Bash-shaped commands that PowerShell 5.1 cannot parse

A recurring tax across the whole session, each failure a parser error whose message points at syntax
rather than at the real cause — that the command was written for a different shell:

- **No `&&` / `||` pipeline chaining.** A parser error, not a runtime failure. The plugin's bash
  blocks routinely chain with `&&`; the 5.1 equivalent is `A; if ($?) { B }`.
- **`if` is not an expression.** `("{0}" -f (if ($x) { 'a' } else { 'b' }))` is a parser error. No
  ternary and no null-coalescing either — both are PowerShell 7 features.
- **Inline `python -c "…"` gets mangled.** PowerShell reinterprets quotes and parentheses inside the
  argument. A `select count(*)` probe failed with `* not recognized`; a
  `re.findall(rb"/Subtype\s*/Image", raw)` probe failed with `unexpected character after line
  continuation character`, because the quotes were stripped before Python saw them. This is the most
  consequential case, because inline probes are the natural way to check something quickly and they
  fail in a way that looks like a Python bug.
- **`Start-Process` splits quoted arguments.** `--title "Truth Set"` produced
  `Unknown argument: Truth`; the quoting must be escaped inside `ArgumentList`.
- **Heredocs are not here-strings.** A bash `<<'EOF'` heredoc failed with
  `unexpected EOF while looking for matching '`; PowerShell here-strings require the closing `'@` at
  column 0.

Individually small; together they cost several retry cycles. The durable fix was the same every
time: **stop passing code through the shell and write a script file instead.**

## Root cause

**`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` has no Windows or PowerShell
section at all** (confirmed by grep across its 512 lines: no occurrence of "PowerShell", "Windows",
"encoding" or "UTF-8"). The file carries the cross-cutting rules every module inherits — file
placement (`:190`), Markdown files (`:205`), no direct SQL (`:179`) — so a shell-semantics rule has a
home and is simply absent.

**The only BOM mention in the plugin points the wrong way.**
`module-05-data-quality-mapping/phase3-test-load.md:273` says to strip a UTF-8 BOM from Windows CSV
*inputs* — the case where a BOM arrives in someone else's file. It says nothing about PowerShell
*writing* one into a file the bootcamp just generated, which is the damaging direction: an input BOM
is a known nuisance, an output BOM corrupts a deliverable the bootcamp is accountable for.

**The dual-shell command blocks are the proximate hazard.**
`module-04-data-collection/SKILL.md:253-254` is representative: PowerShell alternatives are offered
alongside bash, which correctly signals that Windows is supported — but `>` and `Out-File` are not
equivalent to bash `>`, and `Get-Content` is not equivalent to `cat`. Providing the PowerShell half
without its semantics is what makes the corruption reachable.

**Nothing detects mojibake.** `scripts/normalize_docs_markdown.py` runs over `docs/*.md`
immediately before the recap render (`normalize_file`, `:200-228`) and already has the right shape for
this check — it reads UTF-8, transforms, and guards the result against content change. A
Windows-1252 round-trip detector belongs there and does not exist.

These two items are filed together because they share one fix: a single Windows/PowerShell section
in `ground-rules.md` plus one general rule. Splitting them would put two specs on the same new text.

## Proposed change

1. **Add a Windows / PowerShell section to `ground-rules.md`** stating the encoding semantics:

   - On PowerShell 5.1, `-Encoding utf8` writes a **BOM**. For BOM-free UTF-8 use
     `[System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))`.
   - `Get-Content` defaults to the system ANSI codepage for files with no BOM. Always pass
     `-Encoding utf8`, or use
     `[System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)`.
   - Note that `powershell.exe` is 5.1 and `pwsh` is 7+, and that the plugin's guidance assumes 5.1
     unless it has verified otherwise.

   And the syntax limits, with their PowerShell-correct forms: no `&&`/`||` (use `A; if ($?) { B }`),
   `if` is not an expression (no ternary, no null-coalescing), inline `python -c` quoting is
   unreliable, `Start-Process -ArgumentList` needs quotes escaped, and here-strings are not heredocs
   (closing `'@` at column 0).

2. **State the general rule: prefer a file over the shell.** Generated files should be written
   through Python or the agent's file tools rather than PowerShell redirection — every file written
   that way in the reporting session was clean; both corruptions came from PowerShell. And on
   Windows, multi-line or quote-heavy code goes in a script file under `src/` (INV-018) and is run as
   a file, never passed inline. Both are the session's working pattern, promoted to a rule.

3. **Make the PowerShell halves of existing command pairs actually PowerShell.** Where a skill shows
   a bash block chaining with `&&`, its PowerShell counterpart must use `; if ($?) { }` rather than
   copying the bash form. Sweep the modules that ship dual blocks.

4. **Add a mojibake check to `normalize_docs_markdown.py`.** Detect the Windows-1252 round-trip
   signature — `Â`–`Ã` followed by C1-range characters that decode back to a sensible UTF-8
   character — and report it. Reporting is the requirement; automatic repair is optional and must
   obey the existing content-preservation guard (`_signatures_compatible`, `:212-220`), never silently
   rewriting a document it cannot prove it improved. A detector must not flag legitimate text that
   merely contains those characters.

5. **Cross-reference from the input-BOM note.** `phase3-test-load.md:273` should point at the new
   section so the input and output cases are visibly two halves of one topic.

## Acceptance criteria

- [ ] `ground-rules.md` carries a Windows / PowerShell section naming both encoding traps with their
      correct forms, and the five syntax traps with their PowerShell 5.1 equivalents.
- [ ] The section states that `powershell.exe` is 5.1, that `pwsh` is 7+, and that guidance assumes
      5.1 unless verified.
- [ ] A stated rule prefers Python / the agent's file tools over PowerShell redirection for writing
      generated files, and requires quote-heavy or multi-line code to be run from a script file under
      `src/` (INV-018) on Windows.
- [ ] No PowerShell block anywhere in the plugin chains commands with `&&` or `||`; a test asserts
      this over the skills tree.
- [ ] `normalize_docs_markdown.py` reports a Windows-1252 round-trip (mojibake) signature in a
      `docs/*.md` file, with a unit test covering a known-mojibake fixture **and** a clean file
      containing `Â`/`Ã` legitimately (no false positive).
- [ ] Any repair the normalizer performs preserves content per its existing signature guard, and a
      file it cannot prove it improved is left untouched with a stderr line.
- [ ] `phase3-test-load.md`'s input-BOM note cross-references the new section.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      section is additive Windows guidance that changes no Linux/macOS instruction, and the mojibake
      detector is a bundled Python script independent of the bootcamper's chosen language.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — new Windows / PowerShell
  section (encoding + syntax + the prefer-a-file rule), placed with the other cross-cutting rules
  near "File placement" (`:190`) and "Markdown files" (`:205`).
- `plugins/senzing-bootcamp/scripts/normalize_docs_markdown.py` — mojibake detection in
  `normalize_file` / `normalize_text` (`:90-228`), honoring `_signatures_compatible` (`:66-82`).
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md` — `:273`:
  cross-reference the new section.
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — `:253-254` and any other
  dual-shell block: correct the PowerShell halves.
- Every skill shipping a PowerShell command block — sweep for `&&`/`||` and bash-shaped quoting.
- `tests/` — the no-`&&`-in-PowerShell-blocks assertion and the mojibake detector tests.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "PowerShell silently corrupts UTF-8 on both write
  and read — no guidance anywhere in the plugin" (2026-07-28, Cross-module — observed in Truth Set
  visualization and Graduation; Priority High) **merged with** → "no PowerShell shell-syntax guidance
  — bash-shaped commands fail on Windows PowerShell 5.1" (2026-07-28, Cross-module — observed from SDK
  setup onward; Priority Medium). Both `Source: self-observed (assistant retrospective)`;
  `Routing: plugin`; `Upstream: not applicable`. Merged because both are fixed by one new
  `ground-rules.md` section and the same prefer-a-file-over-the-shell rule.
- Priority: High (the encoding half; the syntax half is Medium)
- Related specs: `specs/cross-platform-hook-execution.md` (INV-052 — the no-shell-dependency
  precedent), `specs/auto-detect-platform.md`,
  `specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (INV-110/INV-111 — the
  corrupted-deliverable-reported-as-success class),
  `specs/windows-headless-browser-discovery-for-screenshots.md`,
  `specs/pdf-layout-verification-without-poppler.md` (the other Windows findings from this session)

## Invariants introduced

- `INV-166` — Every file the Bootcamp writes MUST be byte-correct UTF-8 with no BOM; generated files
  MUST be written through Python or the agent's file tools rather than PowerShell redirection; and
  Windows-1252 mojibake MUST be detected and **reported** (never silently repaired) over `docs/*.md`
  before the recap renders (recorded in `specs/INVARIANTS.md`).
- `INV-167` — A PowerShell counterpart to a shell command MUST use PowerShell syntax and MUST NOT
  carry bash-shaped constructs (`&&`/`||`, `if` as an expression, ternary/null-coalescing, heredocs,
  inline `python -c`); quote-heavy or multi-line code MUST be run from a script file under `src/`
  (recorded in `specs/INVARIANTS.md`).
