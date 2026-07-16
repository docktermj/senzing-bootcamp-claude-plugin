#!/usr/bin/env python3
"""SessionEnd hook: to preserve your in-progress recap when the session ends.

When a bootcamp is active, fold the in-progress module recap checkpoint into
docs/bootcamp_recap.md so quitting mid-module never loses that module's narrative.
Deterministic, idempotent, append-only (see recap_checkpoint.py). Silent and
non-blocking: it writes at most one file and never emits output.

Cross-platform: invoked in exec form (``python3 <path>``) so no shell is required on
any platform (INV-052). Python is already a hard bootcamp dependency.
"""
import sys

import recap_checkpoint

if recap_checkpoint.bootcamp_active():
    recap_checkpoint.fold_checkpoint()

sys.exit(0)
