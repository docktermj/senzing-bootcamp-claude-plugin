#!/usr/bin/env python3
"""Package a bootcamp project into one self-describing, transferable zip archive.

A bootcamper who finishes the bootcamp had no way to archive the work or hand it to anyone else.
Graduation frames the recap PDF as "a keepsake to revisit and share with their team", and INV-094's
revisit bundle was built for the resume story -- but it is written **in place**, so it only helps on
the machine that produced it. Switching machines meant re-doing SDK setup, the database, the mapping
and the load by hand; showing the work to a colleague meant attaching four or five files with no
index; archiving before a reimage had no supported path at all.

The artifacts were never the gap. Nothing gathered them, nothing said what to open first, and
nothing decided what must **not** travel.

Two profiles, because the two audiences need different contents:

- ``share``    -- for someone looking at the results. Keepsakes, visualizations, ``production/``.
                  Never a database, never source data, never a credential.
- ``transfer`` -- for the bootcamper resuming elsewhere. Everything in ``share`` plus the INV-094
                  revisit bundle (state snapshot **and** database backup), ``config/``,
                  ``docs/mapping/`` and ``src/``.

⛔ **This script writes an archive and stops.** It never uploads, emails, attaches or opens an issue
with it (INV-135) -- moving the file off the machine is the Bootcamper's action. The output lands
**inside** the project (INV-200), under ``backups/packages/``.

⛔ **Nothing is reported as existing until it has been re-opened.** ``testzip()`` runs on the
finished archive and a ``.sha256`` sidecar is written before the success line prints (INV-067's
discipline): an archive that cannot be read is worse than no archive, because the Bootcamper will
discover it on the machine that no longer has the original.

Format is **zip**, not tar: it opens natively on Windows, macOS and Linux with no extra tool
(INV-066). Stdlib only (INV-108-adjacent: no third-party dependency in a bundled script).

Usage::

    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/package_bootcamp.py" --profile share --dry-run
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/package_bootcamp.py" --profile transfer

``--dry-run`` prints the manifest and the total uncompressed size and writes **nothing**. The
conversation layer (`skills/bootcamp-onboarding/packaging.md`) runs it first so the consent question
can quote a real size rather than an estimate.
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from secret_patterns import find_secret
except ImportError:  # pragma: no cover - the helper ships beside this file
    def find_secret(_text):
        """Fail CLOSED, not open: with no scanner, nothing text-like is packaged.

        An ImportError here must not silently downgrade to "package everything unscanned".
        """
        return "secret scanner unavailable"

#: One top-level directory inside every archive, so extraction never scatters files into the
#: recipient's working directory.
ROOT_PREFIX = "senzing-bootcamp-{profile}-{date}"

#: Paths never included in ANY profile. Named in the manifest rather than dropped quietly, so a
#: recipient can tell what is missing without guessing.
ALWAYS_EXCLUDE = (
    ".env",
    ".env.production",
    "licenses",
    "config/license.json",
    "data/raw",
    "data/temp",
    "logs",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    "target",
    "backups/packages",
)

#: `share` additionally drops every backup, every database file, and the mapping layer.
#: ⛔ `docs/mapping/` is transfer-only by design: it describes the Bootcamper's own source schema
#: (field names, sample values), which the results audience does not need and which belongs with
#: the data rather than with the findings.
SHARE_EXCLUDE = ("backups", "docs/mapping")
DATABASE_SUFFIXES = (".db", ".sqlite", ".sqlite3")

#: What each profile reaches for. A missing entry is recorded as absent, never an error: the flow
#: runs at any point in the bootcamp, so most of this legitimately does not exist yet.
SHARE_INCLUDE = (
    "docs",
    "production",
)
TRANSFER_EXTRA = (
    "backups/revisit",
    "config",
    "src",
)

#: Above this, moving the file is awkward enough to be worth saying so.
SIZE_WARN_BYTES = 2 * 1024 * 1024 * 1024

#: Only text-like members are scanned; a PNG cannot carry a PEM armor line and reading every
#: binary would make the scan the slowest part of the run.
TEXT_SUFFIXES = (
    ".md", ".txt", ".json", ".yaml", ".yml", ".py", ".java", ".cs", ".rs", ".ts", ".js",
    ".sh", ".bat", ".csv", ".jsonl", ".html", ".css", ".ini", ".cfg", ".toml", ".sql", ".env",
)


def _rel(path, root):
    return path.relative_to(root).as_posix()


def is_excluded(relpath, profile):
    """Whether `relpath` (project-relative, posix) is excluded, and by which rule.

    Matches on path *segments* rather than substrings: a directory named ``logs`` is excluded and a
    file named ``changelogs.md`` is not.
    """
    parts = relpath.split("/")
    for rule in ALWAYS_EXCLUDE:
        rule_parts = rule.split("/")
        if parts[: len(rule_parts)] == rule_parts:
            return rule
        if len(rule_parts) == 1 and rule in parts:
            return rule
    if profile == "share":
        for rule in SHARE_EXCLUDE:
            rule_parts = rule.split("/")
            if parts[: len(rule_parts)] == rule_parts:
                return rule
        if Path(relpath).suffix.lower() in DATABASE_SUFFIXES:
            return "*%s (share profile carries no database)" % Path(relpath).suffix.lower()
    return None


def candidate_roots(profile):
    return list(SHARE_INCLUDE) + (list(TRANSFER_EXTRA) if profile == "transfer" else [])


def collect(project_root, profile):
    """(members, skipped) for the profile.

    ``members`` is a list of (absolute path, project-relative posix path).
    ``skipped`` is a list of dicts recording every path left out and why -- the manifest's whole
    value is that a recipient can tell what is absent.
    """
    project_root = project_root.resolve()
    members, skipped, seen = [], [], set()

    for top in candidate_roots(profile):
        base = project_root / top
        if not base.exists():
            skipped.append({"path": top, "reason": "not present in this project"})
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            here = Path(dirpath)
            # Prune excluded directories before descending, so a large excluded tree costs nothing.
            keep = []
            for name in sorted(dirnames):
                rel = _rel(here / name, project_root)
                rule = is_excluded(rel, profile)
                if rule:
                    skipped.append({"path": rel + "/", "reason": "excluded by rule: %s" % rule})
                else:
                    keep.append(name)
            dirnames[:] = keep

            for name in sorted(filenames):
                absolute = here / name
                rel = _rel(absolute, project_root)
                if rel in seen:
                    continue
                rule = is_excluded(rel, profile)
                if rule:
                    skipped.append({"path": rel, "reason": "excluded by rule: %s" % rule})
                    continue
                # Resolve, THEN compare -- the INV-200 rule, here because a symlink into ~/.ssh
                # would otherwise be packaged verbatim under an innocuous project-relative name.
                try:
                    resolved = absolute.resolve()
                except OSError as exc:
                    skipped.append({"path": rel, "reason": "unreadable (%s)" % exc})
                    continue
                if not str(resolved).startswith(str(project_root) + os.sep):
                    skipped.append({
                        "path": rel,
                        "reason": "resolves outside the project root; not packaged",
                    })
                    continue
                secret = _scan(resolved)
                if secret:
                    skipped.append({
                        "path": rel,
                        "reason": "excluded: content matched a secret pattern (%s)" % secret,
                    })
                    continue
                seen.add(rel)
                members.append((resolved, rel))
    return members, skipped


def _scan(path):
    """The secret class this file's content matches, or None. Text-like files only."""
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return find_secret(text)


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(131072), b""):
            digest.update(block)
    return digest.hexdigest()


def read_progress(project_root):
    try:
        with open(project_root / "config" / "bootcamp_progress.json", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def plugin_version():
    """The plugin's own version, per INV-252's skill-relative resolution."""
    here = Path(__file__).resolve().parent
    for candidate in (here.parent / "plugin.json", here.parent / ".claude-plugin" / "plugin.json"):
        try:
            with open(candidate, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        version = data.get("version")
        if isinstance(version, str):
            return version
    return "unknown"


def business_problem_line(project_root):
    """One line naming what the bootcamp was about, for OPEN_ME_FIRST.md."""
    path = project_root / "docs" / "business_problem.md"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    for index, line in enumerate(lines):
        if line.strip().startswith("## Problem Description"):
            for follow in lines[index + 1:]:
                text = follow.strip()
                if text and not text.startswith(("#", ">", "[")):
                    return text
            break
    return ""


def build_manifest(profile, members, skipped, project_root, date):
    progress = read_progress(project_root)
    files = []
    total = 0
    for absolute, rel in members:
        try:
            size = absolute.stat().st_size
        except OSError:
            size = 0
        total += size
        files.append({"path": rel, "size_bytes": size, "sha256": sha256_of(absolute)})
    return {
        "schema": 1,
        "profile": profile,
        "created": date,
        "plugin_version": plugin_version(),
        "modules_completed": progress.get("modules_completed", []),
        "root_directory": ROOT_PREFIX.format(profile=profile, date=date),
        "included_count": len(files),
        "total_uncompressed_bytes": total,
        "included": files,
        # ⛔ The exclusions are part of the manifest, not a footnote. A recipient must be able to
        # tell what is MISSING without guessing -- that is the difference between an archive and a
        # pile of files.
        "exclusion_rules_applied": {
            "always": list(ALWAYS_EXCLUDE),
            "share_only": list(SHARE_EXCLUDE) + ["*%s" % s for s in DATABASE_SUFFIXES]
            if profile == "share" else [],
        },
        "excluded": skipped,
    }


def open_me_first(manifest, project_root):
    profile = manifest["profile"]
    problem = business_problem_line(project_root)
    lines = [
        "# Open me first",
        "",
        "This is a packaged Senzing Bootcamp project.",
        "",
    ]
    if problem:
        lines += ["**The business problem it addresses:** %s" % problem, ""]
    lines += [
        "## Start here",
        "",
        "Open **`docs/bootcamp_recap.pdf`** first — it is the guided tour of what was built,",
        "in order, with the visualizations embedded.",
        "",
        "## What this package is",
        "",
    ]
    if profile == "share":
        lines += [
            "Profile **`share`** — the results, for reading. It carries the keepsake documents,",
            "the visualizations and the generated `production/` project.",
            "",
            "It deliberately carries **no database, no source data and no credentials**, so it is",
            "safe to hand to someone who should see the results but not the inputs.",
        ]
    else:
        lines += [
            "Profile **`transfer`** — everything needed to continue the bootcamp on another",
            "machine: the results, plus the revisit bundle (state snapshot and database backup),",
            "`config/`, the mappings and `src/`.",
            "",
            "**To resume:** open **`docs/REVISIT_BOOTCAMP.md`** — it carries the restore and",
            "re-initialization commands for this project's database and state.",
        ]
    lines += [
        "",
        "## What is NOT here, and why",
        "",
        "`PACKAGE_MANIFEST.json` lists every excluded path with its reason. The categories:",
        "",
        "- **Credentials and licenses** (`.env`, `licenses/`, `config/license.json`) — never",
        "  packaged, in either profile.",
        "- **Your own source data** (`data/raw/`) — never packaged. It is yours, it may be",
        "  sensitive, and the resolved results do not require it.",
        "- **Anything matching a secret pattern** — a PEM private key, an AWS access-key ID or a",
        "  Senzing license payload found in a file's contents excludes that file, and the",
        "  manifest names it.",
        "- **`.git/`** — excluded on purpose. This archive is a **snapshot, not a clone**: git",
        "  history can carry secrets that no longer exist in the working tree. If you want the",
        "  history, push the repository instead of relying on this package.",
        "- **Caches and virtualenvs** (`__pycache__/`, `.venv/`, `node_modules/`, `target/`) —",
        "  regenerated, not preserved.",
        "",
        "## Integrity",
        "",
        "The archive was re-opened and verified after writing, and a `.sha256` sidecar sits beside",
        "it. `PACKAGE_MANIFEST.json` records a SHA-256 for every included file, so you can check",
        "any single file rather than trusting the whole archive at once.",
        "",
        "---",
        "",
        "Packaged by the Senzing Bootcamp plugin %s on %s."
        % (manifest["plugin_version"], manifest["created"]),
        "",
    ]
    return "\n".join(lines)


def human(size):
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return "%.1f %s" % (size, unit) if unit != "B" else "%d B" % size
        size /= 1024.0
    return "%.1f GB" % size


def run(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--profile", choices=("share", "transfer"), required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--date", default=None,
                        help="YYYYMMDD stamp for the archive name (default: today, UTC).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the manifest and total size; write nothing.")
    parser.add_argument("--output", default=None,
                        help="Override the archive path (default: "
                             "backups/packages/senzing-bootcamp-<profile>-<date>.zip).")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        sys.stderr.write("project root not found: %s\n" % project_root)
        return 1
    if args.date:
        date = args.date
    else:
        import datetime
        date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")

    members, skipped = collect(project_root, args.profile)
    manifest = build_manifest(args.profile, members, skipped, project_root, date)
    total = manifest["total_uncompressed_bytes"]

    if not members:
        sys.stderr.write(
            "nothing to package: no included path exists yet for profile '%s'. "
            "Run this after at least one module has produced artifacts.\n" % args.profile
        )
        return 1

    if args.dry_run:
        print(json.dumps(manifest, indent=2, sort_keys=True))
        print("", file=sys.stderr)
        print("profile: %s" % args.profile, file=sys.stderr)
        print("files:   %d" % manifest["included_count"], file=sys.stderr)
        print("size:    %s uncompressed (%d bytes)" % (human(total), total), file=sys.stderr)
        print("excluded: %d path(s) — see `excluded` in the manifest above" % len(skipped),
              file=sys.stderr)
        if total > SIZE_WARN_BYTES:
            print(
                "WARNING: %s is large enough to be awkward to move. Consider the 'share' "
                "profile, or drop the database backup, rather than producing this." % human(total),
                file=sys.stderr,
            )
        print("DRY RUN: nothing was written.", file=sys.stderr)
        return 0

    root = manifest["root_directory"]
    out = Path(args.output) if args.output else (
        project_root / "backups" / "packages" / ("%s.zip" % root))
    out.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        archive.writestr("%s/PACKAGE_MANIFEST.json" % root,
                         json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        archive.writestr("%s/OPEN_ME_FIRST.md" % root, open_me_first(manifest, project_root))
        for absolute, rel in members:
            archive.write(absolute, "%s/%s" % (root, rel))

    # ⛔ Re-open before reporting. An archive nobody read is a claim, not an artifact -- and this
    # one is most likely to be opened on a machine that no longer has the original.
    with zipfile.ZipFile(out) as check:
        bad = check.testzip()
        if bad is not None:
            sys.stderr.write("archive verification FAILED on member %s; removing %s\n"
                             % (bad, out))
            try:
                out.unlink()
            except OSError:
                pass
            return 1
        names = check.namelist()

    tops = {name.split("/")[0] for name in names}
    if tops != {root}:
        sys.stderr.write("archive does not extract into one directory (%s); removing %s\n"
                         % (sorted(tops), out))
        out.unlink()
        return 1

    digest = sha256_of(out)
    sidecar = out.with_suffix(out.suffix + ".sha256")
    sidecar.write_text("%s  %s\n" % (digest, out.name), encoding="utf-8")

    size = out.stat().st_size
    print("Package written: %s" % out)
    print("  size:    %s (%d bytes)" % (human(size), size))
    print("  sha256:  %s" % digest)
    print("  sidecar: %s" % sidecar)
    print("  files:   %d included, %d excluded (see PACKAGE_MANIFEST.json)"
          % (manifest["included_count"], len(skipped)))
    print("  verified: re-opened after writing; extracts into %s/" % root)
    print("")
    print("Move this file wherever you need it — the plugin does not transmit it anywhere.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
