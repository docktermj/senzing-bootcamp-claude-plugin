#!/usr/bin/env python3
"""Build a realistic scratch bootcamp project for a dry run (maintainer tool).

An empty directory exercises each hook's gating branch and nothing else. Most of the
plugin's scripts only misbehave when the state they read is *mid-flight*, so every
fixture written here exists because a naive one hid a defect. Run with --explain to
print the fixture-to-invariant map without writing anything.

Standard library only. Lives under .claude/, which propagate.sh does not mirror, so
this never ships to bootcampers.

Usage:
    python3 scaffold_project.py ~/senzing-bootcamp-dryrun
    python3 scaffold_project.py ~/senzing-bootcamp-phase3 --fresh
    python3 scaffold_project.py --explain
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

DIRS = (
    "config",
    "data/raw",
    "data/mapping",
    "data/samples",
    "data/temp",
    "database",
    "docs/progress",
    "docs/feedback",
    "docs/visualizations",
    "docs/mapping",
    "logs",
    "src/transform",
    "src/load",
    "src/system_verification",
)

# The recap cover clips module chips at 46 characters. No real module NAME reaches
# that — the longest is "Data Quality, Mapping, and Transformation" at 41, and even a
# numbered legacy heading ("10. …") only reaches 45. That is precisely why a renderer
# crash hid behind the shipped example fixture for so long.
#
# The realistic trigger is an UNFINALIZED section heading, because the durability
# hooks fold the checkpoint in with its "— in progress" suffix attached: 41 + 14 = 55,
# comfortably over. So the clip path is reached only *after* the fold runs, which is
# also the state a real interrupted bootcamp is in.
LONG_MODULE_NAME = "Data Quality, Mapping, and Transformation"
IN_PROGRESS_HEADING = f"{LONG_MODULE_NAME} — in progress"  # 55 chars -> clips at 46

PROGRESS = {
    "current_module": "data_quality_mapping",
    "current_step": "11",
    "modules_completed": [
        "entity_resolution_concepts",
        "business_problem",
        "sdk_setup",
        "system_verification",
        "truthset_visualization",
        "data_collection",
    ],
    "selected_modules": [
        "bootcamp_preparation",
        "entity_resolution_concepts",
        "business_problem",
        "sdk_setup",
        "system_verification",
        "truthset_visualization",
        "data_collection",
        "data_quality_mapping",
        "data_processing",
        "query_visualize_discover",
        "graduation",
    ],
    # Names a container that does not exist -> exercises warn-and-continue (INV-101).
    "docker_containers": [
        {"name": "bootcamp-dryrun-absent", "image": "postgres:16", "purpose": "repository"}
    ],
    "license_record_limit": 0,
    "step_history": {
        "data_quality_mapping": {
            "last_completed_step": "11",
            "updated_at": "2026-01-01T00:00:00-07:00",
        }
    },
}

PREFERENCES = """path: core
programming_language: Python
name: Ada Lovelace
os: Linux
arch: x86_64
git_init: true
verbosity:
  preset: standard
"""

RECAP = f"""# Senzing Bootcamp Recap

**Bootcamper:** Ada Lovelace
**Started:** 2026-01-01T09:00:00-07:00
**Programming language:** Python
**Path:** Core
**Plugin version:** 0.0.0-dryrun

---

## Data collection — 2026-01-01T11:00:00-07:00

### Information Shared
- CORD datasets and the Senzing Entity Specification.

### Questions & Responses
- **Q:** How would you like to provide the data for this source?
    - **R:** Option 2, a file path.

### Actions Taken
- Registered `data/raw/customers.csv` in `config/data_sources.yaml`.

### End-of-Module Summary
**What you accomplished:**
- Collected one source into `data/raw/`.

**Files produced:**
- `data/raw/customers.csv` — the raw source.

**Why it matters:** Nothing downstream runs without the data in the project.

---
"""

# An UNFINALIZED checkpoint block: what the durability hooks leave behind and
# module-completion step 2d is supposed to clear (INV-059). Its heading is also the
# recap's only chip long enough to reach the PDF cover's 46-character clip, so folding
# this block is what exercises that path (see LONG_MODULE_NAME above).
CHECKPOINT = f"""<!-- RECAP-CHECKPOINT:START -->
## {IN_PROGRESS_HEADING}

### Information Shared
- A line with an em dash — an ellipsis … and a middle dot ·
- Mapping CUSTOMERS to the Senzing Entity Specification.

### Questions & Responses
- **Q:** Which mapping mode would you like?
    - **R:** Verbose.

### Actions Taken
- Profiled `data/raw/customers.csv`.

### End-of-Module Summary
**What you accomplished:**
- Mapping in progress.
<!-- RECAP-CHECKPOINT:END -->
"""

FEEDBACK = """# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp.

**Started:** 2026-01-01

## Your Feedback

## Improvement: A precious entry that must survive graduation untouched

**Date:** 2026-01-01
**Module:** Data collection
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — the banner did not appear
**Upstream:** not applicable

### What happened

If graduation's normalization pass rewrites, empties or deletes this file, INV-067 is
broken and this sentence will be missing.
"""

MESSY_MARKDOWN = """## Messy heading
text immediately after a heading, no blank line
- a list with no blank line before it
```
a fenced block with no info string
```
**Label :** colon spacing is wrong
"""

RECORDS = "\n".join(
    json.dumps(r)
    for r in (
        {
            "DATA_SOURCE": "CUSTOMERS",
            "RECORD_ID": "1001",
            "PRIMARY_NAME_FULL": "Robert Smith",
            "ADDR_FULL": "123 Main St Las Vegas NV 89101",
        },
        {
            "DATA_SOURCE": "CUSTOMERS",
            "RECORD_ID": "1002",
            "PRIMARY_NAME_FULL": "Bob Smith",
            "ADDR_FULL": "123 Main St Las Vegas NV 89101",
        },
        {
            "DATA_SOURCE": "REFERENCE",
            "RECORD_ID": "2001",
            "PRIMARY_NAME_FULL": "Robert E Smith",
            "ADDR_FULL": "123 Main Street Las Vegas NV",
        },
    )
)

FIXTURE_MAP = [
    ("config/bootcamp_progress.json", "makes every hook consider the bootcamp active; mid-module so resume paths run"),
    ("  └ docker_containers", "names an ABSENT container -> warn-and-continue (INV-101)"),
    ("config/bootcamp_preferences.yaml", "saved verbosity + language to test honor-don't-ask (INV-133)"),
    ("docs/bootcamp_recap.md", "a completed section carrying all four subsections (INV-103)"),
    ("docs/progress/recap_checkpoint.md", "an UNFINALIZED block -> fold idempotency, run it 3x (INV-059); its '— in progress' heading is the only chip long enough to reach the PDF cover's 46-char clip, so FOLD FIRST, then render (INV-048)"),
    ("docs/feedback/...FEEDBACK.md", "a precious entry the normalizer must leave byte-identical (INV-067)"),
    ("docs/loading_strategy.md", "deliberately messy Markdown for the normalizer (INV-060)"),
    ("src/system_verification/records.jsonl", "records for the viz server's --no-serve snapshot build"),
    ("config/engine_config.json", "minimal settings so scripts reach their real failure, not a missing-file one"),
]


def explain():
    print("Fixtures and the invariant each one exercises:\n")
    for path, why in FIXTURE_MAP:
        print(f"  {path:42} {why}")
    print(
        "\nEvery fixture is here because a naive one hid a defect. An empty project\n"
        "exercises only each hook's gating branch."
    )


def build(root: Path, fresh: bool) -> None:
    if root.exists():
        shutil.rmtree(root)
    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)

    (root / "config/engine_config.json").write_text(
        json.dumps({"PIPELINE": {}}, indent=2) + "\n", encoding="utf-8"
    )

    if fresh:
        # The fresh-start path: hooks must see no active bootcamp, and Bootcamp
        # preparation must ask its questions rather than honor saved answers.
        (root / "config/bootcamp_progress.json").write_text("{}\n", encoding="utf-8")
        (root / "config/bootcamp_preferences.yaml").write_text("", encoding="utf-8")
    else:
        (root / "config/bootcamp_progress.json").write_text(
            json.dumps(PROGRESS, indent=2) + "\n", encoding="utf-8"
        )
        (root / "config/bootcamp_preferences.yaml").write_text(
            PREFERENCES, encoding="utf-8"
        )
        (root / "docs/bootcamp_recap.md").write_text(RECAP, encoding="utf-8")
        (root / "docs/progress/recap_checkpoint.md").write_text(
            CHECKPOINT, encoding="utf-8"
        )
        (root / "docs/loading_strategy.md").write_text(MESSY_MARKDOWN, encoding="utf-8")
        (root / "src/system_verification/records.jsonl").write_text(
            RECORDS + "\n", encoding="utf-8"
        )

    # The feedback file exists in both modes: nothing may ever delete or empty it.
    (root / "docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md").write_text(
        FEEDBACK, encoding="utf-8"
    )

    mode = "fresh (phase 3: onboarding from zero)" if fresh else "mid-bootcamp (phase 2)"
    print(f"Built {mode} project at {root}\n")
    explain()
    print(
        "\nReminders:\n"
        "  - test the hooks from a directory with NO bootcamp_progress.json first\n"
        "  - commit or `cp` aside before mutating the repo to negative-control a guard\n"
        "  - clear __pycache__ after any same-size revert\n"
        f"  - clean up with: rm -rf {root}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("directory", nargs="?", help="where to build the project")
    ap.add_argument(
        "--fresh",
        action="store_true",
        help="empty config for the phase-3 onboarding path (no saved state)",
    )
    ap.add_argument(
        "--explain",
        action="store_true",
        help="print the fixture-to-invariant map and exit without writing",
    )
    args = ap.parse_args()

    if args.explain:
        explain()
        return 0
    if not args.directory:
        ap.error("a directory is required (or pass --explain)")

    root = Path(args.directory).expanduser().resolve()
    repo = Path(__file__).resolve().parents[3]
    if root == repo or repo in root.parents:
        print(
            f"Refusing to build inside the repo ({repo}). Use a path outside it, "
            "e.g. ~/senzing-bootcamp-dryrun.",
            file=sys.stderr,
        )
        return 2
    if str(root).startswith(("/tmp/", "/var/tmp/")):
        print(
            "Refusing to build under /tmp: a maintainer hook blocks system-temp "
            "writes, and the plugin's file-placement rules assume a project dir.",
            file=sys.stderr,
        )
        return 2

    build(root, args.fresh)
    return 0


if __name__ == "__main__":
    sys.exit(main())
