# Find the installed browser on Windows, and stop reporting "no capability" when one is present

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`scripts/capture_screenshots.py` reported, twice in one session — once in Truth Set visualization
and again in Query, Visualize and Discover:

```text
No headless screenshot capability available (tried Playwright, Selenium, headless
Chrome/Chromium, wkhtmltoimage). Skipping screenshots; keep the HTML link instead.
```

**Nothing was missing.** Two capable browsers were already installed on the machine:

```text
C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
C:\Program Files\Google\Chrome\Application\chrome.exe
```

Both visualization recap sections lost their embedded images. The bootcamper asked what Windows
needs for screenshots to work and suggested the plugin install it — a question the message
provoked by naming the wrong cause. Being sent to install software you already have is worse than
"could not find your browser", because it sends you to fix the wrong thing.

This is not an edge case. Windows 11 ships Edge, so a Windows workstation is essentially always
capable, and every Windows bootcamper loses the screenshots of the artifact the bootcamp bills as
its "wow moment".

Invoked directly, the browser captured all six tabs on the first attempt:

```text
chrome.exe --headless --disable-gpu --hide-scrollbars --window-size=1600,1200 \
  --virtual-time-budget=12000 --screenshot="<out.png>" "http://localhost:8080/?tab=stats"
```

## Root cause

**`plugins/senzing-bootcamp/scripts/capture_screenshots.py:292-311` — `_chrome_exe()` cannot see a
Windows install.** It probes exactly two shapes, neither of which reaches `C:\Program Files\...`:

- bare command names resolved via `shutil.which()` (`:293-301`, `:309`) — Windows places neither
  Chrome nor Edge on `PATH` by default, so `msedge`, `chrome`, `google-chrome` and `chromium` all
  resolve to nothing while both executables exist on disk;
- hard-coded **macOS** absolute paths (`:302-304`, `/Applications/...`), which cannot match on
  Windows.

So `_capture_chrome_cli()` (`:314-317`) returns `False` before ever launching a browser, and the
Chrome CLI backend — the one that should have succeeded — is skipped.

**`:536-542` conflates two different failures into one message.** The no-capability text is printed
whenever `written` is empty, so "no backend was available" and "a backend ran and produced nothing"
are indistinguishable in the output. INV-122 already requires distinguishing "no headless
capability" from "no requested tab exists"; this is the third case it does not yet separate.

**The reported second gap is already closed in the current tree.** The feedback also found that a
plain `--screenshot` captures before the page's async `init()` completes, yielding branded-but-empty
tab bodies. `_capture_chrome_cli()` already passes `--virtual-time-budget`
(`:327`, `_CHROME_VIRTUAL_TIME_MS = 15000` at `:105`), added after the 0.4.1 release the bootcamper
ran. No change is needed there — but the acceptance criteria below pin it so a future edit cannot
silently drop it, since a found browser without it produces blank-looking tabs that read as a broken
app.

## Proposed change

1. **Add Windows install-path discovery to `_chrome_exe()`.** On Windows, after the `PATH` probe
   fails, expand the standard install locations and return the first that exists:

   - `%ProgramFiles%\Google\Chrome\Application\chrome.exe`
   - `%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe`
   - `%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe`
   - `%ProgramFiles%\Microsoft\Edge\Application\msedge.exe`
   - `%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe`

   Expand the variables from the environment rather than hard-coding `C:\Program Files` — the
   drive and localization vary. Optionally consult
   `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe` (and the `msedge.exe`
   sibling) as a further fallback; keep it in a `try` so a registry failure degrades to the path
   probe rather than raising. Keep the existing macOS paths and the `PATH` probe, and keep the
   backend order (Playwright → Selenium → Chrome CLI → `wkhtmltoimage`) unchanged.

2. **Separate the three failure reasons at `:536-542`.** Report which case occurred:

   - no backend available at all — name what was probed **and, for the Chrome CLI backend, the
     paths searched**, so a bootcamper can see the lookup rather than infer a missing install;
   - a backend was found but every capture failed — say which backend and that the browser was
     found, so the next question is "why did the capture fail", not "what must I install";
   - the existing no-requested-tab case (`:519-526`), unchanged.

3. **Do not install a browser.** The bootcamper's suggestion was to install what is missing; on the
   machine that produced this report nothing was missing, and change 1 resolves it with no
   download. Capture must stay dependency-optional and exit 2 with a message when no backend exists
   (INV-122, INV-048/INV-052/INV-066), so a silent install is forbidden either way. If a genuinely
   incapable machine is later worth handling, it belongs behind an explicit 👉 consent question that
   states the download size and the system change (INV-056-style gate), with declining costing
   nothing — not in this script's probe path. This spec deliberately does not add it.

## Acceptance criteria

- [ ] On a Windows machine with Chrome or Edge installed and neither on `PATH`, `_chrome_exe()`
      returns the executable path and the Chrome CLI backend captures every requested tab.
- [ ] Windows candidate paths are built by expanding environment variables, not by hard-coding a
      drive letter or an English `Program Files` name.
- [ ] A registry lookup failure (key absent, `winreg` unavailable) degrades to the path probe and
      never raises.
- [ ] The macOS `/Applications/...` paths and the `PATH` probe still resolve as before on Linux and
      macOS; backend probe order is unchanged.
- [ ] The no-capability message names the Chrome/Edge locations searched, and a run where a browser
      was found but produced no image reports that distinctly from a run with no backend at all
      (extends INV-122's reason-distinguishing requirement).
- [ ] `--virtual-time-budget` is still passed on the Chrome CLI path, and a test asserts it — a
      capture without it renders the tab body empty.
- [ ] No screenshot backend is installed automatically, and a machine with no backend still exits 2
      with a message and lets the module continue (INV-122, INV-048).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      helper is a bundled Python script the flow calls regardless of the bootcamper's chosen
      language, and the added lookup is platform-gated rather than platform-specific behavior.

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — `_chrome_exe()` (`:292-311`): Windows
  install-path and optional registry discovery; `main()` (`:536-542`): split the failure reasons and
  name the searched paths.
- `tests/` — a test that `_chrome_exe()` finds a browser from a faked Windows layout with an empty
  `PATH`, that the three failure messages are distinguishable, and that the Chrome CLI argv carries
  `--virtual-time-budget`.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — if it restates the
  capture failure text, keep it consistent with the new messages.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Screenshot capture fails on Windows even when a
  capable browser is installed" (2026-07-28, Modules Truth Set visualization and Query, Visualize and
  Discover; `Source: bootcamper-reported`; `Routing: plugin`; `Upstream: not applicable`)
- Priority: Medium
- Related specs: `specs/per-tab-screenshot-capture-and-grounded-captions.md` (INV-122/INV-123 — the
  capture contract and its reason-distinguishing rule),
  `specs/capture-visualization-screenshots-for-recap.md`,
  `specs/embed-every-captured-tab-in-tab-order.md` (INV-146/INV-147 — what the lost images were
  owed to),
  `specs/recap-pdf-images-resolve-against-recap-directory.md` (the other half of the same session's
  screenshot loss),
  `specs/pdf-layout-verification-without-poppler.md` (the sibling Unix-toolchain assumption)

## Invariants introduced

- `INV-168` — A helper that discovers an external executable MUST search each supported platform's
  conventional install locations (expanded from the environment, never hard-coded), MUST NOT report a
  capability as absent when it is present, MUST name the locations searched when it does report one
  absent, and MUST report "found but produced nothing" distinctly from "nothing found" (recorded in
  `specs/INVARIANTS.md`).
