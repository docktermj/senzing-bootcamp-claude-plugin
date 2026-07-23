#!/usr/bin/env python3
"""SessionStart hook: to resume an in-progress bootcamp by injecting resume context.

Also folds any in-progress module recap checkpoint into docs/bootcamp_recap.md on
resume, so a module that was interrupted (quit / compaction / prior session) keeps
its in-progress narrative in the recap (see recap_checkpoint.py).

Cross-platform: invoked in exec form (``python3 <path>``) so no shell is required on
any platform. Python is already a hard bootcamp dependency (the graduation recap PDF always
runs under python3; the Truth Set visualization server also does when the chosen language is
Python).
"""
import sys

import docker_lifecycle
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
    containers = docker_lifecycle.resume_summary()
    if containers:
        message += " " + containers
    print(message)

sys.exit(0)
