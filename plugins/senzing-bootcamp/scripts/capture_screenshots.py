#!/usr/bin/env python3
"""Capture screenshots of a bootcamp visualization for the recap.

Best-effort and dependency-optional (INV-052/INV-066): this helper renders a
**local** HTML file (or a localhost URL served by the bundled visualization app)
to one or more PNG screenshots, so the graduation recap PDF can show what the
bootcamper actually built. It tries several headless backends in order and uses
the first that works; if none is available it exits with code 2 so the caller
degrades gracefully — keeping the HTML link and never blocking graduation
(INV-048).

Offline guarantee (INV-071): only local files and ``localhost``/``127.0.0.1``
URLs are ever opened. A non-local ``http(s)`` host is refused — this helper
never fetches from the network.

Backends tried, in order (each optional):
  1. Playwright (``playwright`` + a browser) — ``python3 -m pip install playwright``.
  2. Selenium (``selenium`` + a headless Chrome/Firefox driver).
  3. Headless Chrome/Chromium CLI (``--headless --screenshot``).
  4. ``wkhtmltoimage`` CLI.

Usage::

    python3 capture_screenshots.py --html docs/visualizations/foo.html \
        --out-dir docs/visualizations --name foo [--count 3]

On success it prints one written PNG path per line and exits 0. The agent then
reviews the shots, keeps the 2-3 most representative, and embeds them into the
matching recap section. Exit codes: 0 = wrote at least one PNG; 2 = no headless
capability available (caller should skip screenshots); 1 = bad arguments.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

# Viewport sizes to capture, giving the agent a few shots to compare and pick
# the 2-3 best from. (width, height, label)
_VIEWS = [
    (1280, 800, "wide"),
    (1280, 1600, "tall"),
    (1024, 768, "compact"),
]


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


def _out_paths(out_dir: Path, name: str, count: int) -> list:
    return [out_dir / f"{name}-{i + 1}.png" for i in range(count)]


def _capture_playwright(url: str, outs: list) -> bool:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception:
        return False
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            wrote = False
            for out, (w, h, _label) in zip(outs, _VIEWS):
                page = browser.new_page(viewport={"width": w, "height": h})
                page.goto(url, wait_until="networkidle")
                page.screenshot(path=str(out), full_page=(_label == "tall"))
                page.close()
                wrote = out.is_file() or wrote
            browser.close()
            return wrote
    except Exception:
        return False


def _capture_selenium(url: str, outs: list) -> bool:
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
        wrote = False
        for out, (w, h, _label) in zip(outs, _VIEWS):
            driver.set_window_size(w, h)
            driver.get(url)
            if driver.save_screenshot(str(out)):
                wrote = True
        return wrote
    except Exception:
        return False
    finally:
        try:
            driver.quit()
        except Exception:
            pass


def _capture_chrome_cli(url: str, outs: list) -> bool:
    exe = None
    for cand in (
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "chrome",
    ):
        if shutil.which(cand):
            exe = cand
            break
    if exe is None:
        return False
    wrote = False
    for out, (w, h, _label) in zip(outs, _VIEWS):
        try:
            subprocess.run(
                [
                    exe,
                    "--headless",
                    "--no-sandbox",
                    "--disable-gpu",
                    f"--window-size={w},{h}",
                    f"--screenshot={out}",
                    url,
                ],
                check=False,
                capture_output=True,
                timeout=60,
            )
        except Exception:
            continue
        if out.is_file() and out.stat().st_size > 0:
            wrote = True
    return wrote


def _capture_wkhtmltoimage(url: str, outs: list) -> bool:
    if not shutil.which("wkhtmltoimage"):
        return False
    wrote = False
    for out, (w, _h, _label) in zip(outs, _VIEWS):
        try:
            subprocess.run(
                ["wkhtmltoimage", "--width", str(w), url, str(out)],
                check=False,
                capture_output=True,
                timeout=60,
            )
        except Exception:
            continue
        if out.is_file() and out.stat().st_size > 0:
            wrote = True
    return wrote


_BACKENDS = (
    _capture_playwright,
    _capture_selenium,
    _capture_chrome_cli,
    _capture_wkhtmltoimage,
)


def capture(target: str, out_dir: Path, name: str, count: int) -> list:
    """Capture up to ``count`` screenshots; return the list of PNGs actually written."""
    if not _is_local_target(target):
        raise ValueError(
            f"refusing non-local target {target!r}: only local files and "
            "localhost URLs are captured (offline guarantee, INV-071)"
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    count = max(1, min(count, len(_VIEWS)))
    outs = _out_paths(out_dir, name, count)
    url = _to_url(target)
    for backend in _BACKENDS:
        if backend(url, outs):
            return [o for o in outs if o.is_file() and o.stat().st_size > 0]
    return []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Capture PNG screenshots of a local bootcamp visualization."
    )
    ap.add_argument(
        "--html",
        help="Path to a local HTML file (or a localhost URL) to screenshot.",
        required=True,
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
        "--count",
        type=int,
        default=len(_VIEWS),
        help=f"How many shots to attempt, up to {len(_VIEWS)}.",
    )
    args = ap.parse_args(argv)

    try:
        written = capture(args.html, Path(args.out_dir), args.name, args.count)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not written:
        print(
            "No headless screenshot capability available (tried Playwright, "
            "Selenium, headless Chrome/Chromium, wkhtmltoimage). Skipping "
            "screenshots; keep the HTML link instead.",
            file=sys.stderr,
        )
        return 2

    for path in written:
        print(os.path.relpath(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
