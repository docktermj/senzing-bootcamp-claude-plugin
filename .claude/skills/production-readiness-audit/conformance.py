#!/usr/bin/env python3
"""Lead generators for the production-readiness audit. Stdlib only, read-only, exit 0.

Four scans, one per property the audit has to establish. Every one is a **lead
generator, not a verdict** — a regex cannot tell a deliberately restated rule from a
rule that drifted, nor a worked illustration from a cached authority. Read every hit
before classifying it. A run that reports this tool's counts as findings has not done
the audit; it has run a grep.

    rules          reverse direction: hard rules in shipped text that no invariant covers
    duplication    passages repeated across shipped files — where "fixed in one place" hides
    enumerations   invariants that enumerate, i.e. the ones that go stale
    size           Goldilocks measurements for the concision pass
    all            every scan

Read-only. Exits 0 whatever it finds, because a hit is usually legitimate and a report
that gates is a report nobody runs.
"""
import argparse
import collections
import pathlib
import re
import sys

DEFAULT_REPO = pathlib.Path(__file__).resolve().parents[3]

INV_ID = re.compile(r"INV-\d{3}")

# The repo's own convention for a deliberate hard rule: a ⛔ lead-in, or a bolded
# MUST/NEVER/ALWAYS. Bare prose "must" is excluded — it is ordinary instruction, and
# including it took the candidate list from 16 to 202, which no one reads.
HARD_RULE = re.compile(
    r"^\s*>?\s*⛔"
    r"|\*\*[^*]*\b(?:MUST|NEVER|ALWAYS)\b[^*]*\*\*"
    r"|^\s*-?\s*\*\*.*?\*\*.*\b(?:MUST|NEVER)\b"
)


def paths(args):
    """Resolve the three roots every scan needs from --repo."""
    repo = pathlib.Path(getattr(args, "repo", None) or DEFAULT_REPO).resolve()
    return repo, repo / "plugins" / "senzing-bootcamp", repo / "specs" / "INVARIANTS.md"


def shipped_markdown(plugin):
    return sorted(p for p in plugin.rglob("*.md") if p.is_file())


def rel(p, repo):
    try:
        return str(p.relative_to(repo))
    except ValueError:
        return str(p)


def sections(lines):
    """Map each line index to its enclosing heading block (start, end)."""
    heads = [i for i, l in enumerate(lines) if l.startswith("#")] + [len(lines)]

    def enclosing(i):
        start = max([h for h in heads if h <= i], default=0)
        end = min([h for h in heads if h > i], default=len(lines))
        return start, end

    return enclosing


def cmd_rules(args):
    """Hard rules whose enclosing section cites no invariant.

    This is the direction the forward sweep cannot see: the plugin states a durable
    rule that `INVARIANTS.md` never records, so nothing binds future work to it and
    nothing notices when a later change contradicts it. Two invariants exist only
    because this went unnoticed — INV-134 (the name is detected, never asked: shipped,
    unregistered, and INV-113 cited INV-076 as its authority, which says nothing about
    names) and INV-155 (the six-tab app was non-conformant with still-standing INV-104,
    whose text still enumerated two tabs that had been removed).

    Scoped to the enclosing section rather than a line window: a rule under a heading
    that cites the governing invariant is covered, even when the citation is 30 lines up.
    """
    repo, plugin, _ = paths(args)
    print("== hard rules whose section cites no invariant\n")
    total = hits = 0
    by_file = collections.OrderedDict()
    for path in shipped_markdown(plugin):
        lines = path.read_text(encoding="utf-8").splitlines()
        enclosing = sections(lines)
        for i, line in enumerate(lines):
            if not HARD_RULE.search(line):
                continue
            total += 1
            start, end = enclosing(i)
            if INV_ID.search("\n".join(lines[start:end])):
                continue
            hits += 1
            by_file.setdefault(rel(path, repo), []).append((i + 1, line.strip()))
    for name, rows in by_file.items():
        print("   %s" % name)
        for lineno, text in rows:
            print("     :%-5d %s" % (lineno, text[:110]))
    print("\n   %d hard-rule lines, %d in a section citing no invariant, across %d file(s)"
          % (total, hits, len(by_file)))
    print("   ^ each is EITHER an unregistered rule (propose an invariant) OR a missing")
    print("     citation to one that exists. Both are findings; they need different fixes.")
    return 0


def _normalize(line):
    """Collapse a line to comparable words: code, emphasis and INV ids are noise here."""
    s = re.sub(r"`[^`]*`", " CODE ", line)
    s = re.sub(r"\*\*|\*|_", "", s)
    s = INV_ID.sub("INV", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def cmd_duplication(args):
    """Passages repeated across shipped files.

    This targets the audit's single most common finding: one rule stated in several
    places, corrected in some. INV-161's document-relative image path was fixed in
    `graduation/SKILL.md` and left wrong in three other files that *produce* the path,
    so every Bootcamper's recap silently lost every screenshot. INV-146's "2-3
    screenshots" survived in three places after the rule changed.

    Repetition is not automatically a defect — a rule required *at* the step it governs
    is INV-183's requirement, not a redundancy. The finding is repetition that has
    **drifted**: compare the hits and see whether they still say the same thing.
    """
    repo, plugin, _ = paths(args)
    n = args.words
    index = collections.defaultdict(set)
    for path in shipped_markdown(plugin):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            words = _normalize(line).split()
            if len(words) < n:
                continue
            for i in range(len(words) - n + 1):
                index[" ".join(words[i:i + n])].add((rel(path, repo), lineno))

    shared = {s: locs for s, locs in index.items() if len({f for f, _ in locs}) > 1}
    pairs = collections.Counter()
    for locs in shared.values():
        files = sorted({f for f, _ in locs})
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                pairs[(files[i], files[j])] += 1

    print("== passages of %d+ words appearing in more than one shipped file\n" % n)
    for (a, b), count in pairs.most_common(args.top):
        print("   %4d shared" % count)
        print("        %s" % a)
        print("        %s" % b)
    print("\n   %d repeated passages across %d file pair(s)" % (len(shared), len(pairs)))
    print("   ^ repetition required AT a step is INV-183, not redundancy. The finding is")
    print("     repetition that has DRIFTED — read both sites and compare.")
    return 0


def cmd_enumerations(args):
    """Invariants that enumerate, because enumerations are what go stale.

    An invariant stating a property survives change; an invariant *listing* members
    breaks the moment a member is added or removed, and it breaks silently — the list
    still reads authoritative. INV-104 enumerated two visualization tabs after both had
    been removed; INV-050's layout tree omitted three always-produced deliverables and
    misattributed a file to the wrong module.
    """
    _, _, invariants = paths(args)
    text = invariants.read_text(encoding="utf-8")
    entries = re.findall(r"^\s*- \*\*(INV-\d{3})\*\*\s*—\s*(.+?)(?=\n\s*- \*\*INV-|\n##|\Z)",
                         text, re.M | re.S)
    signals = (
        ("exact count", re.compile(r"\bexactly (?:one|two|three|four|five|six|seven|"
                                   r"eight|nine|ten|\d+)\b", re.I)),
        ("closed list", re.compile(r"\bis (?:exactly|precisely)\b|\bthe following\b"
                                   r"|\bconsists of\b|\bno other\b|\bonly these\b", re.I)),
        # Three or more backticked literals in a row. The separator must allow
        # "`A`, `B` and `C`" as well as "`A`, `B`, `C`" — real invariants use both, and
        # a comma-only pattern silently misses every Oxford-comma-less series.
        ("comma series", re.compile(
            r"`[^`]+`(?:(?:\s*,\s*|\s*,?\s*(?:and|or)\s+)`[^`]+`){2,}")),
    )
    print("== invariants that enumerate (stale-risk surface)\n")
    found = 0
    for ident, body in entries:
        body = " ".join(body.split())
        why = [label for label, pat in signals if pat.search(body)]
        if not why:
            continue
        found += 1
        print("   %s  [%s]" % (ident, ", ".join(why)))
        print("       %s" % body[:150])
    print("\n   %d of %d invariants enumerate something" % (found, len(entries)))
    print("   ^ for each, check the enumeration against what the plugin ships TODAY.")
    print("     A stale enumeration is a false premise that reads as authoritative.")
    return 0


def cmd_size(args):
    """Goldilocks measurements: where the definition is heaviest.

    Size is not a defect and this scan names no target. It exists so the concision pass
    starts from where the words actually are rather than from an impression, and so a
    later run can tell growth from churn.

    ⛔ Never cut rationale to move these numbers. Every "observed:" clause in this repo
    names a real defect, and it is what stops the rule being re-argued or re-broken.
    """
    repo, plugin, _ = paths(args)
    md = shipped_markdown(plugin)
    rows = []
    for path in md:
        body = path.read_text(encoding="utf-8")
        rows.append((len(body.split()), len(body.splitlines()), rel(path, repo)))
    rows.sort(reverse=True)
    total_words = sum(r[0] for r in rows)
    print("== shipped markdown: %d files, %s words\n" % (len(md), format(total_words, ",")))
    print("   heaviest files:")
    for words, lines, name in rows[:12]:
        print("     %7s words  %5d lines  %s" % (format(words, ","), lines, name))
    scripts = sorted((plugin / "scripts").glob("*.py")) if (plugin / "scripts").is_dir() else []
    if scripts:
        print("\n   bundled scripts: %d files, %d lines"
              % (len(scripts),
                 sum(len(p.read_text(encoding="utf-8").splitlines()) for p in scripts)))
    print("\n   ^ a number, not a target. Cutting rationale to shrink it is forbidden;")
    print("     the win is merging duplicated statements, never deleting the reason.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=None,
                        help="repository root (default: the one this script ships in)")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("rules", help="hard rules no invariant covers (reverse direction)")

    dup = sub.add_parser("duplication", help="passages repeated across shipped files")
    dup.add_argument("--words", type=int, default=14, help="shingle length (default 14)")
    dup.add_argument("--top", type=int, default=12, help="file pairs to show (default 12)")

    sub.add_parser("enumerations", help="invariants that enumerate, i.e. go stale")
    sub.add_parser("size", help="Goldilocks measurements")
    sub.add_parser("all", help="every scan")

    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 0

    # Fail loudly on a wrong --repo rather than reporting an empty, clean-looking sweep:
    # "0 findings" and "0 files read" are indistinguishable in the output (INV-110/INV-115).
    repo, plugin, invariants = paths(args)
    if not plugin.is_dir():
        sys.stderr.write("no plugins/senzing-bootcamp under %s — wrong --repo?\n" % repo)
        return 2
    if args.cmd in ("enumerations", "all") and not invariants.is_file():
        sys.stderr.write("no specs/INVARIANTS.md under %s — wrong --repo?\n" % repo)
        return 2

    if args.cmd == "all":
        for fn in (cmd_rules, cmd_enumerations, cmd_size):
            fn(args)
            print()
        args.words, args.top = 14, 12
        cmd_duplication(args)
        return 0

    return {
        "rules": cmd_rules,
        "duplication": cmd_duplication,
        "enumerations": cmd_enumerations,
        "size": cmd_size,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
