# Make the recap-PDF fpdf2 install robust on externally-managed / broken-pip Python

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

At graduation Step 1b the guide offers to install `fpdf2` (for the professionally
designed recap PDF) with `pip install fpdf2`. On a macOS/Homebrew Python machine
that command failed twice before a workaround succeeded:

1. `pip install fpdf2` — the `pip` on PATH pointed at a deleted interpreter
   (`/usr/local/opt/python@3.11/bin/python3.11: no such file or directory`), exit 1.
2. `python3 -m pip install fpdf2` — blocked by PEP 668 (Homebrew's Python 3.14 is an
   "externally-managed-environment"), exit 1.
3. Creating an isolated virtualenv and installing `fpdf2` there finally worked, and
   the PDF rendered with the fpdf2 renderer.

Both failure conditions — a stale/broken `pip` shim and a PEP 668 externally-managed
Python — are common on macOS with Homebrew Python, so the happy-path command
reliably fails for a whole class of users and forces the agent to improvise. It did
not block graduation (the generator has a stdlib fallback), but it is avoidable
friction at the celebratory final step.

## Root cause

`plugins/senzing-bootcamp/skills/graduation/SKILL.md:104-105` instructs the install
as bare `pip install fpdf2`, which assumes a writable, non-externally-managed Python
and a valid `pip` shim:

> Before rendering, check whether `fpdf2` is importable (`python3 -c "import fpdf"`).
> If it is not, offer to install it (`pip install fpdf2` — a small, pure-Python
> package) …

Bare `pip` uses whatever shim is first on PATH (which may point at a deleted
interpreter), and even `python3 -m pip install` is refused under PEP 668 on
externally-managed interpreters (Homebrew, many Linux distros). The install offer
was introduced by `recap-pdf-professional-design` (`INV-048`) and is mirrored in
`example-recap-reference`; neither addresses install robustness. The generator's
stdlib fallback means this never blocks, but the guidance itself is fragile.

## Proposed change

Replace the bare-`pip` guidance in `graduation/SKILL.md` Step 1b with a robust,
cross-platform install recipe, keeping the whole step non-blocking:

1. **Never call bare `pip`.** Always go through an explicit interpreter:
   `python3 -m pip …` (and on Windows `py -3 -m pip …` as the equivalent), so a
   stale `pip` shim on PATH is never used.
2. **venv-first (the path that worked).** Prefer creating a project-local virtualenv
   and installing there, which sidesteps PEP 668 entirely:
   - `python3 -m venv <project-relative venv dir>` (e.g. under `data/temp/` or
     `build/`, never global, never `/tmp` — per the file-placement rules and
     `PreToolUseWriteError`),
   - install with that venv's own pip (`<venv>/bin/python -m pip install fpdf2` on
     Linux/macOS; `<venv>\Scripts\python -m pip install fpdf2` on Windows),
   - then run the generator with **that venv's** Python so the designed renderer is
     used.
3. **Degrade gracefully.** If venv creation or the install fails (offline, no
   `ensurepip`, etc.), fall back to the stdlib renderer — `INV-048` guarantees a
   valid PDF is always produced, so this never blocks graduation. `--user` /
   `--break-system-packages` may be mentioned only as explicit, last-resort opt-ins,
   never the default, and the plugin never modifies the global/system Python.
4. **(Optional, noted) zero-install path.** Because `generate_recap_pdf.py` already
   has a stdlib fallback, the maintainer may instead choose to default to the stdlib
   renderer (no install prompt) or vendor `fpdf2` — recorded as an alternative, not
   the primary fix.

Keep the `python3 -c "import fpdf"` capability check and the "missing fpdf2 is never
a reason to skip" posture. Update the mirrored install mention wherever it appears in
Step 1b (including the inline-fallback note at `graduation/SKILL.md:133`).

## Acceptance criteria

- [ ] Graduation Step 1b never instructs a bare `pip install`; it uses an explicit interpreter (`python3 -m pip` / `py -3 -m pip`) and prefers a project-local venv.
- [ ] On a PEP 668 externally-managed Python and/or a broken `pip` shim, the documented path still installs `fpdf2` (via the venv) or cleanly falls back to the stdlib renderer — without the agent having to improvise.
- [ ] The recap generator is run with the interpreter that actually has `fpdf2` (the venv's Python when the venv path is used).
- [ ] Any venv/created files live in a project-relative directory (never global site-packages, never `/tmp`), and the global/system Python is never modified.
- [ ] The step stays non-blocking: any install failure still yields a valid PDF via the stdlib fallback (`INV-048`).
- [ ] Holds on Linux, macOS, and Windows (venv `bin/` vs `Scripts/`) and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1b: replace the bare-`pip` install guidance (`:104-105`) with the venv-first / `python3 -m pip` recipe and the graceful-degrade note; update the inline-fallback mention (`:133`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "fpdf2 install for the recap PDF hits broken pip / PEP 668 on macOS" (2026-07-17, Graduation).
- Priority: Medium.
- Related specs: `recap-pdf-professional-design.md` (introduced the install offer under `INV-048`), `example-recap-reference.md` (mirrors the install). Upholds `INV-048`, `INV-052` (python3-only hooks/tooling), and the `PreToolUseWriteError` temp-path rules.

## Invariants introduced

- `INV-066` (broad scope, maintainer-approved) — Any Python package install the plugin instructs MUST use an explicit interpreter (`python3 -m pip`, never bare `pip`) and be robust to PEP 668 externally-managed environments (prefer a project-local virtualenv), and MUST NOT modify the global/system Python; where a working fallback exists (e.g. the recap PDF's stdlib renderer), an install failure MUST degrade to it rather than block. (Hardens `INV-052`/`INV-048` and the file-placement rules.) (Recorded in `specs/INVARIANTS.md`, 2026-07-17.) Implementing this also hardened `module-02-sdk-setup/SKILL.md`'s Python SDK-bindings install to comply.
