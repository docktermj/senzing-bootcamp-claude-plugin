#!/usr/bin/env python3
"""Capture one screenshot per tab of a bootcamp visualization, for the recap.

Best-effort and dependency-optional (INV-052/INV-066): this helper renders a
**local** HTML file (or a localhost URL served by the bundled visualization app)
to one PNG **per tab**, so the graduation recap PDF can show what the bootcamper
actually built. It tries several headless backends in order and uses the first
that works; if none is available it exits with code 2 so the caller degrades
gracefully — keeping the HTML link and never blocking graduation (INV-048).

⛔ **One capture per tab, never per viewport.** This script used to vary the
browser window size across a single page load — ``(1280,800)``, ``(1280,1600)``,
``(1024,768)`` — and had no interaction step at all, so every image showed
whichever tab was active by default. Three files were written, the script exited
0, and nothing looked wrong; the recap shipped three near-identical Entity Graph
shots with captions describing tabs that were never captured. Tab diversity was
not achievable, so the captions could not have been right.

Two consequences are designed in here:

* Output is named ``<name>-<tab-slug>.png``. A tab-named file makes a drifting
  caption structurally hard, and lets graduation's screenshot backfill map images
  to sections and tabs deterministically instead of by guesswork.
* Each written path is printed with its human tab label, tab-separated, so the
  caller derives the caption from the capture rather than from its plan.

How a tab is selected, without adding a browser-automation dependency:

* ``--url http://localhost:PORT`` — appended as ``?tab=<id>``, which the
  visualization app honors on load (``applyDeepLink``). ``--query`` adds ``&q=``
  so Search / Probe can be captured showing real results against the live engine.
* ``--html path/to/snapshot.html`` — a temp sibling copy is written with a small
  script injected before ``</body>`` that calls the app's own ``activate(<id>)``
  (falling back to clicking ``#navbtn-<id>``), retrying until the app's async
  init settles. Temp copies are always deleted.

Because selection happens *in the page*, every backend below works per tab —
including the ones with no interaction API.

Offline guarantee (INV-091): only local files and ``localhost``/``127.0.0.1``
URLs are ever opened. A non-local ``http(s)`` host is refused — this helper
never fetches from the network.

Backends tried, in order (each optional):
  1. Playwright (``playwright`` + a browser) — ``python3 -m pip install playwright``.
  2. Selenium (``selenium`` + a headless Chrome/Firefox driver).
  3. Headless Chrome/Chromium CLI (``--headless --screenshot``).
  4. ``wkhtmltoimage`` CLI.

Usage::

    # static snapshot, all applicable tabs
    python3 capture_screenshots.py --html docs/visualizations/foo.html \
        --out-dir docs/visualizations --name foo

    # live server, specific tabs, with a real search for Search / Probe
    python3 capture_screenshots.py --url http://localhost:8080 \
        --name results_visualization --tabs graph,stats,probe --query "Acme"

On success it prints one ``<png path>\\t<tab label>`` line per capture and exits 0.
Exit codes: 0 = wrote at least one PNG; 2 = no headless capability available
(caller should skip screenshots); 1 = bad arguments.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse, urlencode

# The visualization contract's tab inventory: id -> (filename slug, human label).
# Ids are the app's DOM ids (`tab-<id>`, `navbtn-<id>`) and are contract, not an
# implementation detail, so a server written in any language (INV-090) is capturable.
# The slug is what makes a caption hard to get wrong.
#
# ⛔ `network` and `merges` are RESERVED, not tabs to capture from a current app — a
# current server MUST NOT serve them, and DEFAULT_TABS excludes them. They stay here
# so this helper still names them correctly when pointed at a snapshot saved by an
# earlier eight-tab run, and so nothing reuses those ids for a different tab. Deleting
# them as "dead" silently re-slugs old snapshots to `<id>-<id>.png` (see _out_path's
# fallback) and breaks graduation's caption mapping.
TABS = {
    "graph": ("entity-graph", "Entity Graph"),
    "network": ("relationship-network", "Relationship Network"),
    "merges": ("record-merges", "Record Merges"),
    "stats": ("merge-statistics", "Merge Statistics"),
    "matchkeys": ("match-keys", "Match Keys"),
    "features": ("feature-scores", "Feature Scores"),
    "overlap": ("cross-source", "Cross-Source"),
    "probe": ("search-probe", "Search / Probe"),
}

# Captured when --tabs is not given. Ordered as the app presents them. A tab whose
# data is absent simply renders its empty state; the caller keeps what is useful.
DEFAULT_TABS = ("graph", "stats", "matchkeys", "features", "overlap", "probe")

# The RESERVED ids, split out from TABS so no user-visible string can enumerate them as
# live. `TABS` still accepts them (an old eight-tab snapshot must keep its slugs), but
# `--help` and the unknown-id error name the live six only — those strings are built at
# runtime and carry none of the framing the comment above TABS does, so a reader of
# `--help` was being shown eight capturable tabs for a six-tab app (INV-155).
RESERVED_TABS = tuple(t for t in TABS if t not in DEFAULT_TABS)

# Chrome needs a virtual-time budget or the frame is captured before the D3 layout
# and the /api/* fetches settle — the difference between a graph and a blank panel.
_CHROME_VIRTUAL_TIME_MS = 15000

# Tabs whose content ANIMATES to its final position need longer than the static ones.
# This is settle time, not a timeout: the Entity Graph runs a d3 force simulation, and a
# capture taken before it spreads shows every node bunched in a corner — a valid PNG of a
# graph that looks like it found nothing. The static tabs (tables, histograms) are done as
# soon as their data lands, so raising the budget globally would slow every capture to pay
# for one tab.
_CHROME_VIRTUAL_TIME_MS_ANIMATED = 30000
_ANIMATED_TABS = frozenset({"graph", "network"})


def _virtual_time_ms(tab: str = "") -> int:
    """Virtual-time budget for ``tab`` — longer where the layout animates."""
    return (
        _CHROME_VIRTUAL_TIME_MS_ANIMATED
        if tab in _ANIMATED_TABS
        else _CHROME_VIRTUAL_TIME_MS
    )


_WINDOW = (1440, 900)

# Injected into a temp copy of a snapshot. Retries because the app activates its
# first tab only after an async init; 60 × 100 ms is far longer than that takes.
_ACTIVATE_JS = """
<script>
(function(){
  var target = "__TAB__", tries = 0;
  function go(){
    tries++;
    try {
      if (typeof activate === "function" && document.getElementById("tab-" + target)) {
        activate(target);
        return;
      }
      var btn = document.getElementById("navbtn-" + target);
      if (btn) { btn.click(); return; }
    } catch (e) { /* keep retrying */ }
    if (tries < 60) setTimeout(go, 100);
  }
  go();
})();
</script>
"""


_NON_LOCAL_TARGET = (
    "refusing non-local target {target!r}: only local files and "
    "localhost URLs are captured (offline guarantee, INV-091)"
)


def _is_local_target(target: str) -> bool:
    """True for a local file path or a localhost URL; False for a remote host."""
    parsed = urlparse(target)
    if parsed.scheme in ("", "file"):
        return True
    if parsed.scheme in ("http", "https"):
        host = (parsed.hostname or "").lower()
        return host in ("localhost", "127.0.0.1", "::1")
    return False


def _to_url(target: str) -> str:
    """Turn a local file path into a file:// URL; pass URLs through unchanged."""
    parsed = urlparse(target)
    if parsed.scheme in ("http", "https", "file"):
        return target
    return Path(target).resolve().as_uri()


def _out_path(out_dir: Path, name: str, tab: str) -> Path:
    slug = TABS.get(tab, (tab, tab))[0]
    return out_dir / f"{name}-{slug}.png"


def _tab_url(url: str, tab: str, query: str = "") -> str:
    """Append ?tab=/&q= deep-link parameters to a live-server URL."""
    params = {"tab": tab}
    if query and tab == "probe":
        params["q"] = query
    joiner = "&" if urlparse(url).query else "?"
    return f"{url}{joiner}{urlencode(params)}"


def _page_source(target: str, is_url: bool) -> str:
    """The page's HTML, for the tab-presence pre-flight. Empty string if unreadable.

    ⛔ The locality check is *outside* the ``try`` on purpose. Everything inside it
    degrades to ``""`` so an unreachable page never blocks graduation — but a non-local
    target must never reach ``urlopen`` at all, and swallowing that as "unreadable"
    would fetch it first and then hide the fact (offline guarantee, INV-091).
    """
    if is_url and not _is_local_target(target):
        raise ValueError(_NON_LOCAL_TARGET.format(target=target))
    try:
        if is_url:
            import urllib.request

            with urllib.request.urlopen(target, timeout=10) as response:
                return response.read().decode("utf-8", "replace")
        return Path(target).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _tabs_present(source: str, tabs) -> tuple:
    """Split ``tabs`` into (present, absent) according to the page's own markup.

    ⛔ This pre-flight is what keeps a filename honest. Without it, asking for a tab the
    app does not have still produces a PNG: the injected ``activate()`` finds no
    ``tab-<id>`` element, exhausts its retries, and the **default** tab is captured — so
    e.g. ``viz-feature-scores.png`` would contain the Entity Graph. A file named for a
    tab it does not show is the exact defect tab-naming exists to prevent, so a tab that
    is not in the page is skipped and reported rather than captured wrongly.

    A tab hidden at runtime by ``tabApplicable`` still has its ``tab-<id>`` section in
    the markup and still activates, so this only rejects genuinely absent tabs. When the
    source cannot be read, every tab is treated as present (best-effort — never let an
    unreadable page block capture).
    """
    if not source:
        return list(tabs), []
    present, absent = [], []
    for tab in tabs:
        if re.search(rf'id\s*=\s*["\']tab-{re.escape(tab)}["\']', source) or re.search(
            rf'["\']{re.escape(tab)}["\']\s*,\s*["\']', source
        ):
            present.append(tab)
        else:
            absent.append(tab)
    return present, absent


def _snapshot_copy(html: Path, tab: str) -> Path:
    """Write a temp sibling copy of ``html`` that activates ``tab`` on load.

    A sibling (not /tmp) so any relative asset reference still resolves, and so the
    offline guarantee is unaffected.
    """
    source = html.read_text(encoding="utf-8", errors="surrogateescape")
    script = _ACTIVATE_JS.replace("__TAB__", tab)
    if "</body>" in source:
        patched = source.replace("</body>", script + "</body>", 1)
    else:
        patched = source + script
    handle, path = tempfile.mkstemp(
        prefix=f".{html.stem}-{tab}-", suffix=".html", dir=str(html.parent)
    )
    os.close(handle)
    temp = Path(path)
    temp.write_text(patched, encoding="utf-8", errors="surrogateescape")
    return temp


def _capture_playwright(url: str, out: Path) -> bool:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception:
        return False
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": _WINDOW[0], "height": _WINDOW[1]})
            # A self-contained file:// page produces no network events, so
            # "networkidle" can hang or fire inconsistently; wait for "load"
            # and give the D3 force layout a bounded moment to settle.
            page.goto(url, wait_until="load")
            page.wait_for_timeout(2500)
            page.screenshot(path=str(out))
            page.close()
            browser.close()
        return out.is_file() and out.stat().st_size > 0
    except Exception:
        return False


def _capture_selenium(url: str, out: Path) -> bool:
    try:
        from selenium import webdriver  # type: ignore
        from selenium.webdriver.chrome.options import Options  # type: ignore
    except Exception:
        return False
    try:
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=opts)
    except Exception:
        return False
    try:
        driver.set_window_size(*_WINDOW)
        driver.get(url)
        import time

        time.sleep(2.5)
        return bool(driver.save_screenshot(str(out)))
    except Exception:
        return False
    finally:
        try:
            driver.quit()
        except Exception:
            pass


# Where Windows installers put Chrome and Edge, relative to an environment variable.
#
# Windows puts neither browser on `PATH`, so `shutil.which()` finds nothing while both
# executables sit on disk — which is how a Windows 11 machine carrying Edge *and* Chrome
# reported "No headless screenshot capability available" and lost every recap screenshot.
# The variables are expanded at call time rather than hard-coded: the drive letter varies,
# and `Program Files` is localized on non-English installs.
_WINDOWS_BROWSER_PATHS = (
    ("PROGRAMFILES", r"Google\Chrome\Application\chrome.exe"),
    ("PROGRAMFILES(X86)", r"Google\Chrome\Application\chrome.exe"),
    ("LOCALAPPDATA", r"Google\Chrome\Application\chrome.exe"),
    ("PROGRAMFILES", r"Microsoft\Edge\Application\msedge.exe"),
    ("PROGRAMFILES(X86)", r"Microsoft\Edge\Application\msedge.exe"),
    ("LOCALAPPDATA", r"Microsoft\Edge\Application\msedge.exe"),
)

# Registry fallback for a browser installed somewhere non-standard.
_WINDOWS_APP_PATHS_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
_WINDOWS_APP_PATHS_EXES = ("chrome.exe", "msedge.exe")


def _windows_browser_candidates() -> list:
    """Absolute Chrome/Edge paths to try on Windows, in preference order.

    Returned whether or not they exist, so the failure message can name what was
    searched — being told a capability is absent when it is present sends the reader to
    install software they already have.
    """
    candidates = []
    for variable, relative in _WINDOWS_BROWSER_PATHS:
        base = os.environ.get(variable)
        if base:
            candidates.append(os.path.join(base, relative))
    return candidates


def _windows_registry_browsers() -> list:
    """Chrome/Edge paths registered under `App Paths`, best-effort.

    Any failure — no `winreg` (non-Windows), key absent, permission denied — yields
    nothing and leaves the path probe as the answer, never an exception.
    """
    try:
        import winreg  # type: ignore
    except Exception:
        return []
    found = []
    for exe in _WINDOWS_APP_PATHS_EXES:
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(root, f"{_WINDOWS_APP_PATHS_KEY}\\{exe}") as key:
                    value = winreg.QueryValue(key, None)
            except Exception:
                continue
            if value:
                found.append(value.strip('"'))
    return found


def _chrome_search_paths() -> list:
    """Every location `_chrome_exe` inspects, in order — the lookup, made reportable."""
    paths = [
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "chrome",
        "msedge",
        "microsoft-edge",
        "microsoft-edge-stable",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    if os.name == "nt":
        paths.extend(_windows_browser_candidates())
        paths.extend(_windows_registry_browsers())
    return paths


def _chrome_exe():
    for cand in _chrome_search_paths():
        if os.sep in cand or "/" in cand:
            if os.path.exists(cand):
                return cand
        elif shutil.which(cand):
            return cand
    return None


def _capture_chrome_cli(url: str, out: Path) -> bool:
    exe = _chrome_exe()
    if exe is None:
        return False
    try:
        subprocess.run(
            [
                exe,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                f"--window-size={_WINDOW[0]},{_WINDOW[1]}",
                f"--virtual-time-budget={_virtual_time_ms(_CURRENT_TAB)}",
                f"--screenshot={out}",
                url,
            ],
            check=False,
            capture_output=True,
            timeout=90,
        )
    except Exception:
        return False
    return out.is_file() and out.stat().st_size > 0


def _capture_wkhtmltoimage(url: str, out: Path) -> bool:
    if not shutil.which("wkhtmltoimage"):
        return False
    try:
        subprocess.run(
            [
                "wkhtmltoimage",
                "--width",
                str(_WINDOW[0]),
                "--javascript-delay",
                "3000",
                url,
                str(out),
            ],
            check=False,
            capture_output=True,
            timeout=90,
        )
    except Exception:
        return False
    return out.is_file() and out.stat().st_size > 0


_BACKENDS = (
    _capture_playwright,
    _capture_selenium,
    _capture_chrome_cli,
    _capture_wkhtmltoimage,
)


# The tab currently being captured, so a backend can size its settle time without every
# backend signature growing a parameter — `_BACKENDS` is called uniformly, and tests
# substitute two-argument callables for it.
#
# This is correct ONLY because captures run strictly one at a time: `capture()` walks the
# tabs in a loop, and `_capture_one` owns the global for the duration of exactly one
# capture. Parallelising that loop — the obvious optimisation on a step that shells out to
# a browser per tab — would apply one tab's virtual-time budget to another tab's capture,
# and the symptom is a subtly under-settled PNG rather than an error: the quiet way to
# break INV-122's guarantee that each file shows the tab it is named after. If capture is
# ever parallelised, thread the tab through the backend signature instead of this global.
# `_capture_one` says so on stderr if a second capture begins while one is in flight, so
# the change announces itself instead of silently mis-sizing a settle budget.
_CURRENT_TAB = ""
_CAPTURE_IN_FLIGHT = False


def _capture_one(url: str, out: Path, backend=None, tab: str = ""):
    """Capture ``url`` to ``out``; return the backend that worked, else None.

    Returning the winner lets the caller reuse it for the remaining tabs instead of
    re-walking the list — which would multiply the cost of every missing backend by
    the number of tabs.
    """
    global _CURRENT_TAB, _CAPTURE_IN_FLIGHT
    if _CAPTURE_IN_FLIGHT:
        # Warn, never raise: a capture step must not block the module (INV-052/INV-048).
        sys.stderr.write(
            "capture_screenshots: a capture started while another was still in flight. "
            "`_CURRENT_TAB` is a single module global, so the virtual-time budget may be "
            "sized for the wrong tab and a PNG may be captured under-settled (INV-122). "
            "Thread the tab through the backend signature rather than capturing in "
            "parallel.\n"
        )
    _CAPTURE_IN_FLIGHT = True
    _CURRENT_TAB = tab
    try:
        for candidate in (backend,) if backend else _BACKENDS:
            if candidate(url, out):
                return candidate
        return None
    finally:
        _CAPTURE_IN_FLIGHT = False


def resolve_tabs(spec: str) -> list:
    """Parse a --tabs value into known tab ids, preserving the given order."""
    if not spec:
        return list(DEFAULT_TABS)
    wanted, unknown = [], []
    for raw in re.split(r"[,\s]+", spec.strip()):
        if not raw:
            continue
        tab = raw.strip().lower()
        if tab in TABS:
            if tab not in wanted:
                wanted.append(tab)
        else:
            unknown.append(raw)
    if unknown:
        raise ValueError(
            f"unknown tab id(s): {', '.join(unknown)}. Tab ids: {', '.join(DEFAULT_TABS)}"
        )
    retired = [t for t in wanted if t in RESERVED_TABS]
    if retired:
        # Accepted, so an old eight-tab snapshot still captures under its own slugs —
        # but say so, or a caller who read a stale list never learns the tab is gone.
        sys.stderr.write(
            "note: %s names a tab the current app no longer serves; it is kept only for "
            "snapshots saved before the tab set was fixed at six. A current app will "
            "report it as not present.\n" % ", ".join(retired)
        )
    return wanted


def capture(
    target: str,
    out_dir: Path,
    name: str,
    tabs,
    query: str = "",
    is_url: bool = False,
) -> list:
    """Capture one PNG per tab; return ``(path, label)`` for each one written."""
    if not _is_local_target(target):
        raise ValueError(_NON_LOCAL_TARGET.format(target=target))
    out_dir.mkdir(parents=True, exist_ok=True)
    html = None if is_url else Path(target)
    if html is not None and not html.is_file():
        raise ValueError(f"no such HTML file: {target}")

    written = []
    working_backend = None
    for tab in tabs:
        out = _out_path(out_dir, name, tab)
        temp = None
        try:
            if is_url:
                url = _tab_url(target, tab, query)
            else:
                temp = _snapshot_copy(html, tab)
                url = _to_url(str(temp))
            winner = _capture_one(url, out, working_backend, tab=tab)
            if winner is not None:
                working_backend = winner
                written.append((out, TABS[tab][1]))
            elif working_backend is None:
                # Nothing worked for the first tab: no headless capability at all,
                # so stop rather than failing identically for every remaining tab.
                break
        finally:
            if temp is not None:
                try:
                    temp.unlink()
                except OSError:
                    pass
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Capture one PNG per tab of a local bootcamp visualization."
    )
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument("--html", help="Path to a local HTML snapshot to screenshot.")
    source.add_argument(
        "--url", help="localhost URL of the running visualization app (enables ?tab=/&q=)."
    )
    ap.add_argument(
        "--out-dir",
        default="docs/visualizations",
        help="Directory to write PNGs into (default: docs/visualizations).",
    )
    ap.add_argument(
        "--name",
        default="visualization",
        help="Base name for the PNG files (default: visualization).",
    )
    ap.add_argument(
        "--tabs",
        default="",
        help=f"Comma-separated tab ids (default, and the app's full tab set: "
        f"{','.join(DEFAULT_TABS)}).",
    )
    ap.add_argument(
        "--query",
        default="",
        help="Search text for the Search / Probe tab; requires --url (the static "
        "snapshot has no engine to search).",
    )
    args = ap.parse_args(argv)

    try:
        tabs = resolve_tabs(args.tabs)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if not tabs:
        print("no tabs to capture", file=sys.stderr)
        return 1
    if args.query and not args.url:
        print(
            "--query needs --url: the static snapshot has no running engine, so its "
            "Search / Probe tab cannot show results (see snapshot-static-search-results).",
            file=sys.stderr,
        )
        return 1

    target = args.url or args.html
    is_url = bool(args.url)
    # Refuse a non-local target *before* the pre-flight below reads the page. The same
    # check in capture() runs later, which is too late to keep the promise: the
    # pre-flight would already have fetched the remote host (offline guarantee, INV-091).
    if not _is_local_target(target):
        print(_NON_LOCAL_TARGET.format(target=target), file=sys.stderr)
        return 1
    if not is_url and not Path(target).is_file():
        print(f"no such HTML file: {target}", file=sys.stderr)
        return 1

    # Pre-flight: never capture a tab the page does not have (see _tabs_present).
    tabs, absent = _tabs_present(_page_source(target, is_url), tabs)
    for tab in absent:
        print(
            f"tab {tab!r} is not present in this visualization; skipping it rather than "
            "capturing the default tab under its name.",
            file=sys.stderr,
        )
    if not tabs:
        # Distinct from "no headless backend" — saying the wrong reason here would be
        # the same class of defect this script exists to stop.
        print(
            "None of the requested tabs exist in this visualization; nothing to capture. "
            f"Requested: {', '.join(absent)}.",
            file=sys.stderr,
        )
        return 2

    try:
        written = capture(
            target, Path(args.out_dir), args.name, tabs, query=args.query, is_url=is_url
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not written:
        # Two different failures used to share one message, and the shared wording named
        # the wrong cause: a Windows machine with Edge and Chrome installed was told no
        # capability was available, which sends the reader to install software they
        # already have. Distinguish "nothing to run" from "it ran and produced nothing"
        # (INV-122 requires the reported reason to be the actual one).
        browser = _chrome_exe()
        if browser is None:
            searched = "; ".join(_chrome_search_paths())
            print(
                "No headless screenshot capability available. Tried Playwright, "
                "Selenium, headless Chrome/Chromium, wkhtmltoimage. No Chrome, "
                "Chromium or Edge executable was found — searched: "
                f"{searched}. If a browser is installed elsewhere, put it on PATH. "
                "Skipping screenshots; keep the HTML link instead.",
                file=sys.stderr,
            )
        else:
            print(
                f"A browser was found ({browser}) but every capture attempt failed, so "
                "no image was written. This is not a missing install — do not install "
                "anything. Re-run and check the browser's own error output; if the "
                "target is a live server, confirm it is still serving. Skipping "
                "screenshots; keep the HTML link instead.",
                file=sys.stderr,
            )
        return 2

    captured = [p for p, _ in written]
    missed = [t for t in tabs if _out_path(Path(args.out_dir), args.name, t) not in captured]
    if missed:
        # Never a silent partial result: say which tabs produced nothing.
        print(
            f"Captured {len(written)}/{len(tabs)} tabs; no image for: {', '.join(missed)}.",
            file=sys.stderr,
        )

    for path, label in written:
        print(f"{os.path.relpath(path)}\t{label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
