---
name: dry-run-phase3-full-walk-structure
description: /dry-run phase 3 runs as phases 1+2 in one session then the walk in a fresh one; the full end-to-end walk was completed 2026-08-31, so the next run should start later than Data Quality, Mapping, and Transformation
metadata:
  type: feedback
---

**Structure (still current).** For `/dry-run` phase 3 the maintainer runs **phases 1 and 2 in one
session, then the walk in a fresh session** so the walk gets the whole context window. Offer that
structure rather than assuming a single session.

**Why:** `phase3-conversational.md` warns that a walk analyzing from the top exhausts its context
around Discover the Business Problem, which is why the later modules went unwalked for so long.
Splitting the phases removes the main avoidable cost — phases 1 and 2 consuming the window first.

**The end-to-end walk is DONE — do not repeat it from the top.** On **2026-08-31** the maintainer
delegated the start point ("you figure out when to start analyzing"), analysis began at Bootcamp
preparation, and **all eleven modules were walked through to graduation** — the first phase-3 run
ever to get past SDK setup. It produced **14 findings**, all written to `specs/`. The environment is
what made it possible: 32 SDK builds under `/opt`, an uncapped license, sqlite3, docker, Chrome.

**How to apply next time.** The rotation is live again, so **recommend a start module later than
Data Quality, Mapping, and Transformation** — Module 5's steps 10–26 and its Phase 3 test-load are
the largest untouched surface, followed by Module 6's Phase C/D branches. Do not re-analyze the
opening stretch; it has now been covered three times.

**One thing that walk left owed:**

- **The INV-133 seeded walk.** Analysis started at Bootcamp preparation, so only `--fresh` ran. The
  honor path was exercised only in its inert direction — it shows the rule does not fire when it
  should not, and says nothing about whether it fires when it should. Scaffold `--seeded` and check
  that Bootcamp preparation asks nothing.

**Graduation's upstream gate fired for the first time, and the report was sent.** The gate needs at
least one `mcp-server` finding and that walk produced two. During the run it was correctly recorded
as `submission blocked: dry run …` (never `offered, declined`); **after** the run closed the
maintainer approved the text and it was submitted **2026-08-31** via `submit_feedback`
(`category='bug'`, anonymous) — the sanctioned path `phase3-conversational.md` describes. The sent
text is preserved in `specs/routing-report-flags-every-payload-field-as-dropped.md` and
`specs/flag-gated-fields-are-unannotated-in-both-reference-topics.md`.

⚠️ **Watch the spelling guard when writing specs from a walk.** That run introduced 10 INV-253
British-spelling violations across five specs and this memory file, which turned the next run's
preflight red. Write US English as you go: `license`, `honor`, `behavior`, `neighboring`,
`recognize`.

Related: [[spec-commit-message-format]].
