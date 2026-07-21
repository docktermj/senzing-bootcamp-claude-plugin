#!/usr/bin/env python3
"""Shared helper for the bootcamp recap-durability hooks.

The in-progress module recap lives at ``docs/progress/recap_checkpoint.md`` (see the
module-completion skill), authored by the guide and refreshed at each step boundary.
This module folds that checkpoint into ``docs/bootcamp_recap.md`` so an interrupted
module (quit / compaction / new session) never loses its in-progress narrative.

The fold is deterministic, idempotent, and append-only with respect to completed
``## {module}`` sections: it only ever replaces the marker-fenced checkpoint block,
never a finalized section. Pure Python 3 stdlib, no third-party dependency (INV-052).

This is NOT a hook itself. It is imported by the PreCompact, SessionEnd, and
SessionStart hook scripts, which run in exec form (``python3 <hook>.py``); Python
puts each hook script's own directory (this ``scripts/`` directory) on ``sys.path``,
so ``import recap_checkpoint`` resolves here on Linux, macOS, and Windows alike.
"""
import os

CHECKPOINT = os.path.join("docs", "progress", "recap_checkpoint.md")
RECAP = os.path.join("docs", "bootcamp_recap.md")
START = "<!-- RECAP-CHECKPOINT:START -->"
END = "<!-- RECAP-CHECKPOINT:END -->"


def bootcamp_active():
    """True during an active bootcamp (a progress file exists in the project)."""
    return os.path.isfile(os.path.join("config", "bootcamp_progress.json"))


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _strip_block(text):
    """Remove every checkpoint block (START..END) from recap text so a re-fold
    replaces the prior checkpoint instead of duplicating it. Completed
    ``## {module}`` sections carry no markers and are never touched."""
    while True:
        i = text.find(START)
        if i == -1:
            return text
        j = text.find(END, i)
        if j == -1:
            # Unterminated marker: drop from START to end of text.
            return text[:i].rstrip() + "\n"
        j += len(END)
        text = (text[:i].rstrip() + "\n\n" + text[j:].lstrip("\n")).strip() + "\n"


def fold_checkpoint():
    """Fold ``docs/progress/recap_checkpoint.md`` into ``docs/bootcamp_recap.md``.

    Returns True if a non-empty checkpoint was folded, else False. Safe to call
    repeatedly: it removes any prior checkpoint block before appending the current
    one, so folds never duplicate, and it creates ``docs/`` (and a minimal recap) if
    they do not yet exist. A missing or empty checkpoint is a no-op.
    """
    checkpoint = _read(CHECKPOINT)
    if not checkpoint or not checkpoint.strip():
        return False

    block = checkpoint.strip()
    # Guarantee the block is fenced so a later fold can find and replace it.
    if START not in block:
        block = START + "\n" + block
    if END not in block:
        block = block + "\n" + END

    recap = _read(RECAP) or ""
    recap = _strip_block(recap)

    if recap.strip():
        merged = recap.rstrip() + "\n\n" + block + "\n"
    else:
        merged = block + "\n"

    try:
        parent = os.path.dirname(RECAP)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(RECAP, "w", encoding="utf-8") as fh:
            fh.write(merged)
    except OSError:
        return False
    return True
