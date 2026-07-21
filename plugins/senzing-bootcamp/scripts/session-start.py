#!/usr/bin/env python3
"""SessionStart hook: to inject bootcamp resume context when a bootcamp is in progress.

Also folds any in-progress module recap checkpoint into docs/bootcamp_recap.md on
resume, so a module that was interrupted (quit / compaction / prior session) keeps
its in-progress narrative in the recap (see recap_checkpoint.py).

Cross-platform: invoked in exec form (``python3 <path>``) so no shell is required on
any platform. Python is already a hard bootcamp dependency (the Module 3
visualization server and the graduation recap PDF both run under python3).
"""
import sys

import recap_checkpoint

if recap_checkpoint.bootcamp_active():
    folded = recap_checkpoint.fold_checkpoint()
    message = (
        "A Senzing bootcamp is in progress. Read config/bootcamp_progress.json "
        "and offer to resume from the last recorded module before doing anything else."
    )
    if folded:
        message += (
            " An in-progress module recap checkpoint was found and folded into "
            "docs/bootcamp_recap.md (source: docs/progress/recap_checkpoint.md). "
            "Continue that module and finalize its recap section on completion."
        )
    print(message)

sys.exit(0)
