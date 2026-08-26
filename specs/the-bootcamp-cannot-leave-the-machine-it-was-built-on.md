# The bootcamp cannot leave the machine it was built on

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

A bootcamper who finishes the bootcamp has no way to **archive the work or hand it to
anyone else.** Graduation tells them the recap PDF is "a keepsake to revisit and share
with their team" (`skills/graduation/SKILL.md:1103`), and single files can of course be
copied by hand — but the *bootcamp* cannot be moved. There is no command, script or step
that packages the project into one transferable artifact, so:

- **Switching machines mid-bootcamp** means re-doing SDK setup, the database, the mapping
  and the load by hand on the new machine. The revisit bundle (INV-094) was built for
  exactly this resume story and then written **in place**, so it only helps on the machine
  that produced it.
- **Showing the work to a colleague or a stakeholder** means locating and attaching four
  or five separate files, with no index, no explanation of what to open first, and no
  visualizations unless the bootcamper knows they exist under `docs/visualizations/`.
- **Archiving the bootcamp** — keeping it after the workstation is reimaged — has no
  supported path at all.

The gap is not that the artifacts are missing. Graduation produces good ones. It is that
nothing gathers them, nothing says what a recipient should open, and nothing decides what
must *not* travel.

## Root cause

Nothing in the plugin packages anything; the capability was never ported from Kiro Power.

- `plugins/senzing-bootcamp/commands/` holds four commands — `start-bootcamp`,
  `graduate`, `bootcamp-feedback`, `bootcamp-note`. There is no packaging command.
- `plugins/senzing-bootcamp/scripts/` holds no archiving code: no `tarfile`, `zipfile`,
  `shutil.make_archive` or `copytree` call exists anywhere under
  `plugins/senzing-bootcamp/`.
- The Kiro predecessor had the feature and all three pieces are still unported in
  `MIGRATION.md`: `steering/slash-backup-project.md` -> `commands/backup-project.md`
  (`MIGRATION.md:257`), `hooks/backup-before-load.json` (`MIGRATION.md:265`), and
  `scripts/backup_project.py` (`MIGRATION.md:318`), all `[ ]` not started.
  `git log -S backup_project --all` returns exactly one commit — `6f91e56`, the commit
  that added that checklist — so nothing was removed; it was never built here.

The nearest existing thing is graduation Step 6 (`skills/graduation/SKILL.md:1011`,
INV-094 at `specs/INVARIANTS.md:598`), and it is deliberately **not** this:

- `6a` (`:1028`) backs the database up to `backups/revisit/database/`, `6b` (`:1052`)
  snapshots config plus `docs/mapping/` into `backups/revisit/state/` with a
  `RESUME_STATE.json` manifest, `6c` (`:1064`) writes the `docs/REVISIT_BOOTCAMP.md`
  return guide.
- The manifest indexes the recap PDF and `docs/visualizations/` by **project-relative
  path** rather than containing them (`:1057-1063`), and no step packages, compresses or
  copies anything out of the project. It is a save point, not a shipment.

Two adjacent details make hand-rolling it worse than it looks:

- The `.gitignore` graduation writes for `production/` excludes `*.db` and `*.sqlite`
  (`skills/graduation/SKILL.md:868`), so "just push the repo" silently drops the
  repository the results live in.
- `backups/` is already annotated *"Project backups/archives"* in INV-050's layout tree
  (`specs/INVARIANTS.md:208-209`) — the slot for this exists and only `revisit/` fills it.

**Invariant note (do not silently override):** this touches **INV-094** (the revisit
bundle — reuse it, do not duplicate its database branch), **INV-050** (layout — a new
`backups/packages/` entry), **INV-200** (every file the bootcamp writes stays inside the
project, so the archive lands in the project and the bootcamper moves it themselves),
**INV-109** (the write-gate's secret patterns), **INV-135** (nothing leaves the machine
without an explicit yes), **INV-017** (Markdown under `docs/`; the files written *inside
the archive* are archive members, not project files, and are not bound by it),
**INV-051/INV-056** (pinned, numbered 👉 question), **INV-185/INV-252** (a bundled script
is invoked through `${CLAUDE_PLUGIN_ROOT}`), **INV-066** (both platforms' behavior) and
**INV-254**'s any-time-flow precedent for where the workflow file lives.

## Proposed change

Add an **any-time** package-and-transfer flow — a bundled script that does the work, a
supporting workflow file that governs the conversation, and a slash command that reaches
it. Do not add a step or a question to graduation.

### 1. Two profiles, because the two audiences need different contents

| Profile | For | Contents |
|---|---|---|
| `share` | someone else looking at the results | `docs/bootcamp_recap.pdf`, `docs/business_problem.pdf`, `docs/data_source_evaluation.pdf`, `docs/bootcamp_notes.md`, `docs/visualizations/`, the `docs/*.md` deliverables, and `production/` |
| `transfer` | the bootcamper resuming elsewhere | everything in `share`, plus `backups/revisit/` (state snapshot **and** database backup), `config/`, `docs/mapping/`, `src/` |

**Never included in either profile**, and named as excluded in the manifest rather than
dropped quietly: `.env`, `.env.production`, `licenses/`, `config/license.json`,
`data/raw/` (the bootcamper's own source data), `data/temp/`, `logs/`, `.git/`,
`__pycache__/`, `.venv/`, `venv/`, `node_modules/`, `target/`, and `backups/packages/`
itself. `share` additionally excludes all of `backups/` and every `*.db`/`*.sqlite`.

⛔ **`.git/` is excluded on purpose.** The archive is a snapshot, not a clone; git history
can carry secrets that no longer exist in the tree. Say so in `OPEN_ME_FIRST.md` so a
bootcamper who wants history knows to push the repository instead.

### 2. The `transfer` profile reuses INV-094's database backup — it does not reimplement it

`transfer` includes the database by including `backups/revisit/`. When that directory is
absent (the flow was run before graduation), the packager MUST NOT grow its own
SQLite-vs-PostgreSQL branch: that branch is INV-094's, its indeterminate-`database_type`
handling is subtle (`skills/graduation/SKILL.md:1030-1037`), and a second copy is exactly
the drift this repo writes tests to prevent.

Instead, **factor Step 6a out of graduation into a supporting file** —
`skills/graduation/database-backup.md` — cited by both Step 6a and the new packaging
workflow, with graduation's behavior unchanged. Both callers, one implementation. When the
bundle is absent the packager runs that same file's procedure into
`backups/revisit/database/`, then packages it.

### 3. What the recipient opens

Every archive contains a single top-level directory
(`senzing-bootcamp-<profile>-<YYYYMMDD>/`) so extraction never scatters files into the
recipient's cwd, and at its root:

- **`OPEN_ME_FIRST.md`** — what this is, "open `docs/bootcamp_recap.pdf` first", the
  bootcamper's business problem in one line, what is included, what is excluded **and
  why**, and — `transfer` only — a pointer to `docs/REVISIT_BOOTCAMP.md` for the restore
  and re-init commands.
- **`PACKAGE_MANIFEST.json`** — profile, plugin version (read per INV-252), creation date,
  `modules_completed`, every included path with its SHA-256 and size, the exclusion rules
  actually applied, and any path skipped by the secret scan or the symlink rule. A
  recipient must be able to tell what is *missing* without guessing.

### 4. The script: `scripts/package_bootcamp.py`

Bundled, stdlib-only, invoked as
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/package_bootcamp.py"` (INV-185/INV-052 quoting).

- **Format: zip** (`zipfile`, `ZIP_DEFLATED`, zip64 on). It opens natively on Windows,
  macOS and Linux with no extra tool — `tar` does not (INV-066).
- **`--dry-run`** prints the manifest and the total uncompressed size **without writing
  anything.** This is what supplies the real number in the consent question below; the
  question must never quote a guessed size.
- **Secret scan before inclusion.** Every candidate text member is scanned for the three
  patterns the write-gate already detects — PEM private keys, `AKIA…` access-key IDs,
  `AQAAAD…` license blobs (`scripts/write-gate.py:156-158`). A hit is **excluded and
  named**, never packaged. Put the patterns in one importable helper both files use, and
  add a test asserting the two lists agree, so the packager cannot drift from INV-109.
- **Resolve, then compare.** Skip any member whose resolved path lands outside the project
  root — the same resolve-then-compare rule as INV-200, here because a symlink into
  `~/.ssh` would otherwise be packaged verbatim.
- **Verify before reporting success.** `ZipFile.testzip()` on the finished archive, write a
  `<archive>.sha256` sidecar, and report the path, byte size and digest. Never tell the
  bootcamper an archive exists without having re-opened it (INV-067's discipline).
- **Size guard.** When `--dry-run` totals more than 2 GB, say so and recommend `share` (or
  dropping the database) instead of silently producing something awkward to move.
- Output: `backups/packages/senzing-bootcamp-<profile>-<YYYYMMDD>.zip`, inside the project
  per INV-200.

### 5. The conversation: `skills/bootcamp-onboarding/packaging.md`

An any-time flow, filed beside `notes.md` and `feedback.md` per the INV-254 precedent, and
reachable at any point — onboarding, any module, graduation — from a new
`commands/package-bootcamp.md`.

Before writing anything, run `--dry-run` and ask one pinned, numbered 👉 question
(INV-051/INV-056) that states the real size and exactly what travels:

> 👉 **What should the package contain? Reply with a number:**
>
> 1. **Results to share** — your recap PDF, keepsake documents, visualizations and
>    `production/` project (~<n> MB). No database, no source data, no credentials.
> 2. **Everything to continue elsewhere** — the above plus your database backup, config
>    and mappings, so you can pick the bootcamp back up on another machine (~<n> MB).
> 3. **Cancel.**

⛔ **The plugin writes the archive and stops.** It never uploads, emails, attaches or
opens an issue with it — the same rule the feedback flow already follows
(`skills/graduation/SKILL.md:1094`). Moving the file off the machine is the bootcamper's
action, and the closing summary names the path so they can.

### 6. Discoverability, without touching graduation's flow

Add **one line** to graduation's closing announcement (`skills/graduation/SKILL.md:1103`)
offering the command — no new 👉 question, no new gate, INV-251's single closing question
untouched. ⛔ Note for the implementer: if the packager is ever run *from* a graduation bash
block, `tests/test_graduation_announces_what_it_produces.py` requires its `--output` path
to be named in the closing step. Under this design graduation does not run it, so mention
the command and name no path.

## Acceptance criteria

- [ ] `/package-bootcamp` works at any point in the bootcamp — onboarding, any module, after graduation — and produces `backups/packages/senzing-bootcamp-<profile>-<YYYYMMDD>.zip`.
- [ ] Exactly one pinned, numbered 👉 question precedes any write, and its size figures come from `--dry-run`, not an estimate; option 3 cancels with nothing written.
- [ ] The `share` archive contains no `*.db`, `*.sqlite`, `data/raw/`, `.env`, `licenses/`, or `config/license.json` member — asserted by an offline test over a fixture project tree.
- [ ] The `transfer` archive contains the revisit bundle's state snapshot and database backup, and `OPEN_ME_FIRST.md` points at `docs/REVISIT_BOOTCAMP.md` for the restore commands.
- [ ] When `backups/revisit/` is absent, the packager runs the **shared** `database-backup.md` procedure rather than a second SQLite/PostgreSQL branch; a test asserts graduation Step 6a and the packaging flow cite that one file.
- [ ] `backups/packages/` is excluded from its own archive — asserted by a test that runs the packager twice and shows the second archive does not contain the first.
- [ ] A member matching any INV-109 secret pattern is excluded and named in `PACKAGE_MANIFEST.json`; a test asserts the packager's pattern list and `write-gate.py`'s are the same list.
- [ ] A symlink resolving outside the project root is skipped and named in the manifest.
- [ ] Every archive extracts into exactly one top-level directory and contains `OPEN_ME_FIRST.md` and `PACKAGE_MANIFEST.json` at its root; the manifest records the plugin version, `modules_completed`, per-file SHA-256, and the exclusions applied.
- [ ] `ZipFile.testzip()` passes and a `<archive>.sha256` sidecar is written before the bootcamper is told the archive exists.
- [ ] Nothing is uploaded, emailed or attached; the flow ends by naming the local path.
- [ ] Graduation gains exactly one discoverability line and no new question; INV-251 and INV-094 remain satisfied.
- [ ] `specs/INVARIANTS.md` records the new guarantee and adds `backups/packages/` to INV-050's layout tree without breaking `tests/test_invariant_layout_tree.py`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic — stdlib `zipfile` only, no `tar`/`zip` binary, and no assumption about which language the bootcamper chose (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/package_bootcamp.py` — **new.** The packager: profiles, exclusions, secret scan, symlink rule, manifest, `--dry-run`, verification.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/packaging.md` — **new.** The any-time workflow and its pinned question.
- `plugins/senzing-bootcamp/commands/package-bootcamp.md` — **new.** Command entry point, `${CLAUDE_PLUGIN_ROOT}` script path.
- `plugins/senzing-bootcamp/skills/graduation/database-backup.md` — **new.** Step 6a's procedure, factored out for two callers.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 6a cites the new supporting file (behavior unchanged); one discoverability line in the closing announcement (`:1103`).
- `plugins/senzing-bootcamp/scripts/write-gate.py` — secret patterns moved into a shared importable helper (behavior unchanged).
- `specs/INVARIANTS.md` — new invariant; `backups/packages/` added to INV-050's tree.
- `tests/` — new tests for the exclusion sets, self-inclusion, the shared secret-pattern list, the shared database-backup citation, and the archive's root layout.
- `MIGRATION.md` — mark `slash-backup-project.md` / `scripts/backup_project.py` as superseded by this flow rather than pending.

## Source

- Feedback: n/a — raised by the maintainer in session on 2026-08-26 ("does the plugin still have the ability to back up the entire bootcamp directory so it can be archived or transferred to another machine so someone can see the results"), then confirmed against the tree; `Source: self-observed (assistant retrospective)`.
- Priority: **Medium.** Nothing is broken and no bootcamper is blocked — the argument against filing it Low is that graduation already frames the recap as something to "share with their team" (`:1103`) and INV-094 already built a resume story, so the plugin promises portability it delivers only one file at a time.
- MCP re-check: **n/a (no Senzing fact).** This spec asserts nothing about Senzing, the SDK, the entity specification or the MCP server — it concerns the plugin's own artifacts, file layout and interaction layer — so there is no server fact to re-verify and no absence claim about the server to substantiate (the `owner-checked:` clause is exempt for this reason). `get_capabilities` was called once at triage to date the run: server **1.33.0**, 2026-08-26.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `specs/graduation-revisit-resume-bundle.md` (INV-094 — the save point this makes portable), `specs/migrate-kiro-power.md` (the unported Kiro `backups/` slot, `:143`), `specs/harden-write-gate.md` (INV-109's patterns, now shared), `specs/bootcamp-notes-capture-and-recap-section.md` (INV-254 — the any-time-flow precedent this follows), `specs/render-any-bootcamp-document-as-a-styled-pdf.md` (the keepsake PDFs the `share` profile carries).

## Invariants introduced

- `INV-NNN` (unassigned — take the next unused number, with its index entry, in the implementing edit) — The Bootcamper MUST be able, at any point in the bootcamp, to package their bootcamp into a single self-describing archive under `backups/packages/`, in one of two profiles: a **share** profile (keepsakes, visualizations and `production/`; never a database, source data or credential) or a **transfer** profile (the share contents plus the INV-094 revisit bundle, config and mappings, sufficient to resume on another machine). Every archive MUST extract into one top-level directory carrying `OPEN_ME_FIRST.md` and a `PACKAGE_MANIFEST.json` that names what was included **and what was excluded**; MUST exclude `.env`, `licenses/`, `config/license.json`, `data/raw/`, `.git/` and its own output directory; MUST exclude and name any member matching the INV-109 secret patterns or resolving outside the project root; MUST be verified on disk (`testzip()` plus a SHA-256 sidecar) before the Bootcamper is told it exists; and MUST NOT be transmitted anywhere by the plugin. The `transfer` profile MUST reuse INV-094's database-backup procedure rather than implement a second one. **The consent gate is part of the guarantee, not an implementation detail: a packaging run MUST ask exactly one pinned, numbered 👉 question before anything is written; the sizes that question quotes MUST come from a `--dry-run` measurement rather than an estimate; and the cancel option MUST write nothing at all.** What the Bootcamper consents to is precisely which of their files travel, so a question that understates the contents is the failure this clause exists to prevent. Requires maintainer-approved wording before implementation.

⚠️ **The consent-gate sentence was added 2026-08-26** by `specs/the-packaging-consent-gate-is-an-unregistered-guarantee.md`, after `production-readiness-audit-2026-08-26` found that `packaging.md` shipped those two rules while this draft — written before the conversational layer existed — covered only the archive's contents and verification.

## Deviations from this spec, and why (2026-08-26)

No Senzing fact is involved, so nothing was re-verified against the server. Six deviations.

1. **`write-gate.py` was NOT changed; it keeps its inline pattern and a test pins the two equal.**
   The spec asks for the patterns to move "into a shared importable helper both files use". The
   helper exists and `package_bootcamp.py` imports it — but the gate is a `PreToolUse` security
   control, where an ImportError does not degrade to "no secret scan", it degrades to a hook that
   cannot run at all, on every write in the bootcamp. The plugin already has this exact shape for
   `brand_tokens.py`, inlined into two generators with `tests/test_brand_sync.py` asserting the
   copies stay equal; `tests/test_secret_patterns_are_shared.py` does that job here, comparing the
   pattern **strings** rather than sampled behavior. The spec's stated goal — "the packager cannot
   drift from INV-109" — is met without adding a failure mode to the gate.

2. **The `transfer` database backup is run by the conversation layer, not by the script.** The spec
   says "the packager runs that same file's procedure". `package_bootcamp.py` is stdlib-only and must
   not shell out to `pg_dump` or `docker`, and inventing credentials is forbidden — so
   `packaging.md` Step 3 runs `../graduation/database-backup.md` before invoking the script, and the
   script packages whatever `backups/revisit/` then contains. One implementation of the branch, as
   the spec requires; a different caller than its wording implies.

3. **`share` also excludes `docs/mapping/`.** The spec lists `docs/mapping/` under `transfer` only,
   but a whole-`docs` sweep pulled it into `share` too. Found by extracting a real archive and
   reading it, not by review. It describes the Bootcamper's own source schema — field names, sample
   values — which the results audience does not need, so it is now a `share`-profile exclusion.

4. **`backups/packages/` was given its own leaf in INV-050's tree, not a comment on `backups/`.** A
   comment-only continuation line is not a tree entry, and `test_invariant_layout_tree` pins the
   count of both. A real leaf is also what makes INV-202 satisfiable for the directory, since the
   path is referenced under `plugins/`. The pinned directory count moved 30 → 31 with the reason
   recorded beside the constant.

5. **`MIGRATION.md`'s `hooks/backup-before-load.json` entry is left OPEN, not marked superseded.**
   The spec asks for the Kiro items to be marked superseded; two are. The third is an *automatic
   pre-load* backup, which is a different decision — when it fires, whether it is silent, what it
   costs on a large repository — and this flow is bootcamper-invoked and asks before it writes.
   Marking it superseded would retire a question nothing has answered.

6. **The graduation discoverability line sits on its own line rather than appended to the closing
   announcement sentence.** Appending it produced a 991-character line with a stop sign ~800
   characters in, which `test_conformance_sees_a_rule_beside_a_citation` rejected — it validates the
   truncated string `since` prints rather than the source line (`classify()` accepts the full line).
   The prose is better on its own line and is now line-anchored for every conformance view.

**The invariant is deferred, and this spec asked for that explicitly** — its `## Invariants
introduced` note reads "Requires maintainer-approved wording before implementation." No ID was
minted and nothing was appended to the invariant list. The layout-tree edit is called out separately
in the `specs/IMPLEMENTED.md` entry so the maintainer can accept or revert it independently.
