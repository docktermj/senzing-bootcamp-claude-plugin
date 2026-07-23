#!/usr/bin/env python3
"""Shared helper for the bootcamp Docker container lifecycle hooks (INV-101).

Any Docker container the bootcamp starts is recorded in
``config/bootcamp_progress.json`` under a ``docker_containers`` list (each entry
carrying at least a ``name``). This module lets the SessionEnd hook stop those
recorded containers when the session ends, and the SessionStart hook surface them
on resume so the guide can restart or regenerate them.

All Docker interaction is OPTIONAL and gated on the ``docker`` CLI being present:
when ``docker`` is absent, missing, or erroring, every function warns-and-continues
and never blocks the hook. Pure Python 3 stdlib, no third-party dependency
(INV-052/INV-001/INV-002).

This is NOT a hook itself. It is imported by the SessionEnd and SessionStart hook
scripts, which run in exec form (``python3 <hook>.py``); Python puts each hook
script's own directory (this ``scripts/`` directory) on ``sys.path``, so
``import docker_lifecycle`` resolves here on Linux, macOS, and Windows alike.
"""
import json
import os
import shutil
import subprocess

PROGRESS = os.path.join("config", "bootcamp_progress.json")


def _load_progress():
    try:
        with open(PROGRESS, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def tracked_containers():
    """Return the recorded bootcamp-started containers (list of dicts).

    Each entry is expected to carry at least a ``name``. Tolerates a bare list of
    name strings, and returns ``[]`` when the field is absent or unreadable.
    """
    data = _load_progress()
    if not isinstance(data, dict):
        return []
    raw = data.get("docker_containers") or []
    if not isinstance(raw, list):
        return []
    out = []
    for entry in raw:
        if isinstance(entry, str) and entry.strip():
            out.append({"name": entry.strip()})
        elif isinstance(entry, dict) and entry.get("name"):
            out.append(entry)
    return out


def docker_available():
    """True when a ``docker`` CLI is on PATH."""
    return shutil.which("docker") is not None


def _run(args, timeout=30):
    """Run a docker command, returning (ok, stdout). Never raises."""
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return proc.returncode == 0, (proc.stdout or "")
    except (OSError, subprocess.SubprocessError):
        return False, ""


def stop_started_containers():
    """Stop each recorded container (``docker stop``, never remove) so it can be
    restarted on resume. No-op when there are no tracked containers or ``docker``
    is unavailable. Returns the names for which a stop succeeded. Warn-and-continue
    on every failure; never raises."""
    containers = tracked_containers()
    if not containers or not docker_available():
        return []
    stopped = []
    for c in containers:
        name = c.get("name")
        if not name:
            continue
        ok, _ = _run(["docker", "stop", name])
        if ok:
            stopped.append(name)
    return stopped


def _container_state(name):
    """Return 'running', 'stopped', 'missing', or 'unknown' for a container."""
    ok, out = _run(
        [
            "docker", "ps", "-a",
            "--filter", "name=^%s$" % name,
            "--format", "{{.Names}}\t{{.State}}",
        ]
    )
    if not ok:
        return "unknown"
    for line in out.splitlines():
        parts = line.split("\t")
        if parts and parts[0] == name:
            state = parts[1].strip().lower() if len(parts) > 1 else ""
            return "running" if state == "running" else "stopped"
    return "missing"


def resume_summary():
    """Return a one-paragraph resume message about recorded containers for the
    guide to act on, or '' when there are none. Never raises."""
    names = [c["name"] for c in tracked_containers() if c.get("name")]
    if not names:
        return ""
    if not docker_available():
        return (
            "This bootcamp recorded Docker container(s) (%s), but the `docker` CLI "
            "is not available here. If they are needed, offer to help the bootcamper "
            "start Docker or regenerate them." % ", ".join(names)
        )
    parts = ["%s (%s)" % (name, _container_state(name)) for name in names]
    return (
        "This bootcamp uses Docker container(s): "
        + ", ".join(parts)
        + ". Offer to restart any that are stopped, or regenerate any that are "
        "missing, before resuming work that needs them."
    )
