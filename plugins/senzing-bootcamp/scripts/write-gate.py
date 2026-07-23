#!/usr/bin/env python3
"""PreToolUse gate for Write/Edit: to block writes into the system temp or Downloads
directory, and block obvious secrets -- DURING a bootcamp only.

Cross-platform: invoked in exec form (``python3 <path>``) so no shell is required.
Native JSON parsing replaces the previous grep/sed field extraction.
"""
import json
import os
import re
import sys

data = sys.stdin.read()

# Gate: only enforce when a bootcamp is active, so the plugin never blocks writes in
# unrelated Claude Code sessions.
if not os.path.isfile(os.path.join("config", "bootcamp_progress.json")):
    sys.exit(0)

LOC_MSG = (
    "Write blocked: use a project-relative path, not a system temp or Downloads "
    "directory."
)
SECRET_MSG = (
    "Write blocked: a possible hardcoded secret was detected. Use environment "
    "variables instead."
)


def block(message):
    sys.stderr.write(message + "\n")
    sys.exit(2)


# Extract the write target (tool_input.file_path). Prefer JSON; fall back to a field
# match. File paths do not contain double quotes, so the first match is the real
# target; fail open (allow on location grounds) if extraction yields nothing.
file_path = ""
try:
    file_path = (json.loads(data).get("tool_input") or {}).get("file_path") or ""
except (ValueError, AttributeError):
    m = re.search(r'"file_path"\s*:\s*"([^"]*)"', data)
    file_path = m.group(1) if m else ""

# An unexpanded Windows temp env-var reference (%TEMP%/%TMP%) is always a temp
# target, independent of the project directory. Windows env-var names are
# case-insensitive, so compare case-folded (%Temp%, %tmp%, ... all count).
_fp_upper = file_path.upper()
if "%TEMP%" in _fp_upper or "%TMP%" in _fp_upper:
    block(LOC_MSG)

# Resolve to an absolute path. A relative path is, by definition, inside the project,
# so it is always allowed on location grounds.
if file_path.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", file_path):
    abs_path = file_path                       # POSIX or Windows-drive absolute
elif file_path == "":
    abs_path = ""                              # extraction failed -> fail open
else:
    abs_path = os.path.join(os.getcwd(), file_path)


def norm(path):
    """Backslash-normalize, collapse repeated slashes, and resolve `.`/`..`
    segments (portably, without touching the filesystem) so Windows and POSIX
    targets compare correctly and cannot escape the project via `..`."""
    p = re.sub(r"/+", "/", path.replace("\\", "/"))
    leading = "/" if p.startswith("/") else ""
    out = []
    for seg in p.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if out and out[-1] != "..":
                out.pop()
            elif not leading:
                out.append("..")
        else:
            out.append(seg)
    return leading + "/".join(out)


# Location check: exempt the project directory FIRST, then block temp/Downloads. The
# gate's intent is "don't write outside the project"; a project that merely lives
# under a path containing /tmp/ (e.g. /home/user/tmp/proj) must not trip it.
if abs_path:
    target = norm(abs_path)          # `..` resolved, so escapes can't slip the block
    here = norm(os.getcwd())
    if target == here or target.startswith(here + "/"):
        pass  # inside the project -> allowed on location grounds (checked FIRST)
    else:
        # Temp/Downloads checks are case-insensitive (Windows/macOS filesystems are
        # case-insensitive). This only ever tightens the block on OUTSIDE-project
        # paths — in-project paths already passed the exemption above.
        low = target.lower()
        if (
            low.startswith("/tmp/")
            or low.startswith("/var/tmp/")
            or low.startswith("/private/tmp/")
            or low.startswith("/private/var/folders/")
            or "/downloads/" in low
            or "/appdata/local/temp/" in low
        ):
            block(LOC_MSG)
        else:
            # macOS puts the per-user temp dir under $TMPDIR (e.g. /var/folders/...).
            tmpdir = os.environ.get("TMPDIR", "")
            if tmpdir:
                tmp_norm = norm(tmpdir.rstrip("/")).lower()
                if low.startswith(tmp_norm + "/"):
                    block(LOC_MSG)

if re.search(r"BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY|AKIA[0-9A-Z]{16}", data):
    block(SECRET_MSG)

sys.exit(0)
