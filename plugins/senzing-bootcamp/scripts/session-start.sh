#!/usr/bin/env bash
# SessionStart hook: if a bootcamp is in progress, inject resume context.
progress="config/bootcamp_progress.json"
if [ -f "$progress" ]; then
  echo "A Senzing bootcamp is in progress. Read $progress and offer to resume from the last recorded module before doing anything else."
fi
exit 0
