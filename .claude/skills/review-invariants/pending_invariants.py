#!/usr/bin/env python3
"""Read the pending `DEFERRED INVARIANT` blocks out of `specs/IMPLEMENTED.md`.

This exists because the by-hand version failed twice on 2026-09-01, in both directions:

* A count taken by grepping for the phrase returned **29** pending blocks when there were
  **11** — ledger prose that merely mentions the term matched too.
* A block the maintainer had **already held**, twice, with a recorded revisit condition,
  was presented as awaiting a first decision. Nothing in a grep distinguishes *"not yet
  decided"* from *"decided: wait"*, and re-offering a settled decision wastes the one
  thing this workflow is short of.

So the queue is computed here rather than assembled by reading, and `held` is a first-class
state with its reason carried beside it.

Read-only. Stdlib only. Exit 0 whatever it finds.

Subcommands
    list                 the review queue, numbered, with held blocks listed separately
    show <n>             one block in full: rules, drafted wording, enforcer, sites
    sites <n>            where the rule ships, and candidate sites a citation must reach
    next-id              the next free INV id, read off INVARIANTS.md
    check                every rule quote matches the file it names
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
LEDGER = REPO / "specs" / "IMPLEMENTED.md"
INVARIANTS = REPO / "specs" / "INVARIANTS.md"
SPECS = REPO / "specs"
PLUGIN = REPO / "plugins" / "senzing-bootcamp"

AWAITING = "awaiting the maintainer's sign-off; NOT minted"
HELD_IN_BLOCK = "must be approved before implementation"
HELD_IN_SPEC = "Held, not merely unapproved"
BOILER = re.compile(r"\*\(written as NNN deliberately.*?\)\*\s*", re.S)
# A rule bullet is an indented list item carrying a stop sign. Three shapes occur, and a
# pattern fitted to one silently drops the others -- `⛔ **rule**`, `**⛔ rule**`, and a
# rule whose location reads "same section" instead of naming a path. Fitting only the
# first reported 1 rule for a block that ships 3.
BULLET = re.compile(r"^\s+- .*⛔")
QUOTE = re.compile(r"\*\*(?:⛔\s*)?(.+?)\*\*", re.S)
LOC = re.compile(r"—\s*in `([^`]+)`")
CITED = re.compile(r"\(INV-\d{3}\)")


def flat(s):
    return re.sub(r"\s+", " ", s).strip()


def blocks():
    """Every DEFERRED INVARIANT block that is not already resolved."""
    lines = LEDGER.read_text(encoding="utf-8").splitlines()
    spec, out, i = None, [], 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            spec = line[3:].strip()
        if ("DEFERRED INVARIANT" in line and "resolved INV-" not in line
                and line.lstrip().startswith("- ")):
            buf, j = [line], i + 1
            while j < len(lines) and not (
                    lines[j].startswith("## ") or re.match(r"^- \*\*", lines[j])):
                buf.append(lines[j])
                j += 1
            body = "\n".join(buf).rstrip()
            # ⛔ Membership is decided by the block's own MARKER, never by the phrase
            # appearing on the line. The first version of this filter kept any bullet
            # containing "DEFERRED INVARIANT" and reported 25 pending against a true 9:
            # ledger prose ABOUT deferrals -- audit summaries, "INVARIANT REGISTERED"
            # entries quoting the term -- matched too. That is the same overcount this
            # module's docstring was written to prevent, reproduced inside the fix for it.
            if AWAITING in body or HELD_IN_BLOCK in body:
                out.append({"spec": spec, "line": i + 1, "text": body})
            i = j
            continue
        i += 1
    return out


def hold_reason(spec):
    """The maintainer's recorded reason for holding, from the spec file. None if not held."""
    f = SPECS / f"{spec}.md"
    if not f.is_file():
        return None
    text = f.read_text(encoding="utf-8")
    if HELD_IN_SPEC not in text:
        return None
    m = re.search(r"Revisit (?:after|when|if)[^.]*\.", text)
    return m.group(0) if m else "revisit condition recorded in the spec"


def parse(b):
    """Split a block into its rules, its drafted wording, and its trailing notes."""
    text = BOILER.sub("", b["text"])
    rules, sites = [], []
    for line in text.split("\n"):
        if not BULLET.match(line):
            continue
        q = QUOTE.search(line)
        if not q:
            continue
        loc = LOC.search(line)
        where = loc.group(1) if loc else "(same section as the rule above)"
        rules.append(f"{flat(q.group(1))} — in {where}")
        if loc:
            sites.append(loc.group(1))
    m = re.search(r"\*\*INV-NNN\*\*\s*—?\s*(.+?)(?=\n\s*⛔ \*\*Nothing was written|\Z)",
                  text, re.S)
    wording = flat(m.group(1)) if m else ""
    enf = re.search(r"Enforced by `([^`]+)`", text)
    return {**b, "rules": rules, "sites": sites, "wording": wording,
            "enforcer": enf.group(1) if enf else None,
            "held": hold_reason(b["spec"]) or (
                "spec requires approval before implementation"
                if HELD_IN_BLOCK in b["text"] else None)}


def queue():
    parsed = [parse(b) for b in blocks()]
    return ([p for p in parsed if not p["held"]], [p for p in parsed if p["held"]])


def next_id():
    ids = [int(m) for m in re.findall(r"\*\*INV-(\d{3})\*\*",
                                      INVARIANTS.read_text(encoding="utf-8"))]
    return max(ids) + 1


def resolve(loc):
    """Resolve a ledger location to a real shipped file, by PATH not basename."""
    for base in (PLUGIN / "skills", PLUGIN / "scripts", PLUGIN):
        if (base / loc).is_file():
            return base / loc
    return None


def shipped_files():
    return sorted(p for p in PLUGIN.rglob("*")
                  if p.suffix in (".md", ".py") and p.is_file())


def cmd_list():
    pending, held = queue()
    print(f"== Invariants awaiting your review ==\n")
    print(f"pending: {len(pending)}   held: {len(held)}   "
          f"next free id: INV-{next_id():03d}\n")
    if not pending:
        print("  (none — every deferred invariant has been decided)")
    for i, p in enumerate(pending, 1):
        n = len(p["rules"])
        print(f"  {i:2}. {p['spec']}")
        print(f"      {n} rule{'s' if n != 1 else ''} · "
              f"IMPLEMENTED.md:{p['line']} · enforcer: {p['enforcer'] or '(none named)'}")
    if held:
        print("\n-- HELD: already decided, NOT for review --")
        for p in held:
            print(f"   · {p['spec']}")
            print(f"     {p['held']}")
    print("\nRun `show <n>` for the full block, `sites <n>` before citing.")


def _pick(n):
    pending, _ = queue()
    if not (1 <= n <= len(pending)):
        print(f"no pending invariant {n} (there are {len(pending)})")
        raise SystemExit(0)
    return pending[n - 1]


def cmd_show(n):
    p = _pick(n)
    print(f"== {n}. {p['spec']} ==\n")
    print(f"ledger    : specs/IMPLEMENTED.md:{p['line']}")
    print(f"spec      : specs/{p['spec']}.md")
    print(f"enforcer  : {p['enforcer'] or '(none named)'}")
    print(f"would be  : INV-{next_id():03d}   <- read again at mint time; only the first "
          f"one minted gets it\n")
    print("-- RULES ALREADY SHIPPING, bound by nothing --")
    for r in p["rules"]:
        print(f"  ⛔ {r}")
    print("\n-- DRAFTED WORDING --")
    body = p["wording"] or "(not in the ledger — read the spec's `## Invariants introduced`)"
    for line in _wrap(body, 92):
        print(f"  {line}")


def _wrap(s, w):
    out, cur = [], ""
    for word in s.split():
        if len(cur) + len(word) + 1 > w:
            out.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        out.append(cur)
    return out


def cmd_sites(n):
    """Where the rule ships, plus candidates a citation must reach.

    ⛔ (INV-246) The deferral's own list is where the author NOTICED the rule, which is
    exactly what is unreliable when a rule is applied in several places. On 2026-09-01
    INV-286's block named two sites and the rule shipped in THREE; the third was found by
    scanning and would have been missed by reading the list. So the named sites and the
    scan are printed separately, and the scan is a LEAD GENERATOR — a candidate is a line
    to read, never a site to cite blind.
    """
    p = _pick(n)
    print(f"== sites for {n}. {p['spec']} ==\n")
    print("-- NAMED by the deferral (definite) --")
    for s in sorted(set(p["sites"])):
        n = p["sites"].count(s)
        print(f"  {s}" + (f"   ({n} rules)" if n > 1 else ""))

    # Terms weighted by RARITY. An unweighted overlap matches on "module", "whether",
    # "already" -- words in almost every shipped file -- and buries the real candidate in
    # noise. Only terms appearing in a small minority of files discriminate.
    files = shipped_files()
    texts = {f: f.read_text(encoding="utf-8").lower() for f in files}
    def rare(term):
        return sum(1 for s in texts.values() if term in s) <= max(2, len(files) // 8)
    terms = {w for w in re.findall(r"[a-z_]{6,}", p["wording"].lower()) if rare(w)}
    named = set(p["sites"])

    # ⚠️ A path the block mentions in PROSE is a named site whose bullet nobody wrote.
    # Both third sites found on 2026-09-01 -- INV-286's `phase2-document-confirm.md` and
    # this block's `module-04-data-collection/SKILL.md` -- were named exactly this way.
    # Only paths that RESOLVE under plugins/ are candidate sites. A block also names its
    # enforcer test, `specs/INVARIANTS.md` and generated artifacts; none of those is a
    # place a citation goes, and listing them buries the one that is.
    prose = {m for m in re.findall(r"`([a-z0-9][\w./-]*\.(?:md|py))`", p["text"])
             if m not in named and "/" in m and resolve(m) is not None}
    if prose:
        print("\n-- NAMED in the block's PROSE but not as a bullet (check these first) --")
        for s in sorted(prose):
            print(f"  {s}")

    print("\n-- CANDIDATES from scanning (read each; do not cite blind) --")
    hits = 0
    for f in files:
        rel = str(f.relative_to(PLUGIN))
        if rel in named or rel in prose:
            continue
        for i, line in enumerate(texts[f].splitlines(), 1):
            if "⛔" not in line or CITED.search(line):
                continue
            overlap = terms & set(re.findall(r"[a-z_]{6,}", line))
            if len(overlap) >= 2:
                hits += 1
                print(f"  {rel}:{i}   shares: {', '.join(sorted(overlap)[:5])}")
    if not hits:
        print("  (none — the named sites are likely the whole set, but read them to confirm)")


def cmd_check():
    """Every rule quote must appear verbatim in the file it names."""
    bad = checked = 0
    for p in [parse(b) for b in blocks()]:
        for r in p["rules"]:
            quote, _, loc = r.rpartition(" — in ")
            if loc.startswith("("):          # no path named; nothing to check against
                continue
            f = None
            for base in (PLUGIN / "skills", PLUGIN / "scripts", PLUGIN):
                if (base / loc).is_file():
                    f = base / loc
                    break
            if f is None:
                continue
            checked += 1
            src = CITED.sub("", flat(f.read_text(encoding="utf-8")))
            if CITED.sub("", quote).strip() not in src:
                bad += 1
                print(f"  MISMATCH {p['spec']}\n    {quote[:110]}")
    print(f"{checked} rule quotes checked, {bad} mismatched")


def main(argv):
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "list":
        cmd_list()
    elif cmd == "next-id":
        print(f"INV-{next_id():03d}")
    elif cmd == "check":
        cmd_check()
    elif cmd in ("show", "sites"):
        if not rest or not rest[0].isdigit():
            print(f"usage: {cmd} <n>   (see `list`)")
            return 0
        (cmd_show if cmd == "show" else cmd_sites)(int(rest[0]))
    else:
        print(f"unknown subcommand {cmd!r}")
        print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
