#!/usr/bin/env python3
"""SessionStart hook: if a bootcamp is in progress, inject resume context.

Cross-platform: invoked in exec form (``python3 <path>``) so no shell is required
on any platform. Python is already a hard bootcamp dependency (the Module 3
visualization server and the graduation recap PDF both run under python3).
"""
import os
import sys

if os.path.isfile(os.path.join("config", "bootcamp_progress.json")):
    print(
        "A Senzing bootcamp is in progress. Read config/bootcamp_progress.json "
        "and offer to resume from the last recorded module before doing anything else."
    )
sys.exit(0)
