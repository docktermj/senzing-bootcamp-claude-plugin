---
name: retrofit-from-public
description: 'Retrofit changes made in the public access repo (Senzing/senzing-bootcamp-claude-plugin) back into this development repo. Use when the maintainer wants to bring public-repo edits (PR fixes, typo/spelling corrections, direct changes) back into development. The inverse of propagate-to-public: copies the propagated content back, applies the inverse owner rewrite (Senzing to docktermj), never deletes, and stops at the working tree (no commit, no push). Maintainer tool — not part of the bootcamper experience.'
---

# Retrofit ← Public access repo

This is a **maintainer** tool for developing the Senzing Bootcamp Claude Plugin
(SBCP). It brings changes that were made in the **public access repo**
(`Senzing/senzing-bootcamp-claude-plugin`, cloned locally at
`~/senzing.git/senzing-bootcamp-claude-plugin`) back into this **development
repo** (`docktermj/senzing-bootcamp-claude-plugin`).

It is the counterpart to `propagate-to-public`. Propagate is authoritative
(dev → public). Retrofit is the *return path* for edits that happen in public —
PR fixes, spelling corrections, or direct changes — so they aren't lost.

The work is done by [`retrofit.sh`](retrofit.sh) in this skill's directory.

## Retrofit is NOT a mirror image of propagate — three asymmetries

1. **The transform is inverted, narrowly.** Propagate rewrites
   `docktermj → Senzing`; retrofit undoes it, or the dev repo's identity would be
   poisoned with Senzing URLs:
   - `Senzing/senzing-bootcamp-claude-plugin` → `docktermj/senzing-bootcamp-claude-plugin`
   - `marketplace.json` owner `"name": "Senzing"` → `"name": "docktermj"` (that file only)

   It is **not** a blanket `Senzing → docktermj`. `plugin.json`'s
   `"author": { "name": "Senzing" }` is the *company* (stays Senzing in both
   repos), the skill content mentions "Senzing" constantly, and the
   `docktermj/senzing-bootcamp-free-data` links are already `docktermj` — none of
   those are touched. Because the rewrite is a clean inverse, **retrofit is a
   no-op when the repos are already in sync** (the dev diff comes back empty).

2. **It never deletes.** Propagate can mirror-with-delete because dev is the
   source of truth. Retrofit can't: a new dev file under `plugins/` not yet
   propagated would be wrongly deleted. So retrofit is **add/update only** and
   *reports* tracked dev files that are absent from public for you to remove by
   hand — it never deletes them for you.

3. **Governance is one-directional.** The public repo owns a governance layer
   (`.github/`, `LICENSE`, `.vscode/cspell.json`, `.gitignore`,
   `.claude/settings.json`) that the dev repo has never had. Retrofit **does not**
   pull it in — dev keeps its own setup.

## What gets retrofit (the manifest)

**Retrofit** (public → dev, add/update, reverse-transformed):

- `plugins/senzing-bootcamp/**` — the whole plugin payload, minus `__pycache__/`
  and `*.pyc`.
- `.claude-plugin/marketplace.json`
- `README.md`
- `docs/`

**Never touched in dev** (dev-only — preserved because they are outside the
retrofit paths and nothing is ever deleted):

- `.claude/**` — dev commands, memory, skills (**including this skill and
  `propagate-to-public`**) and `settings.local.json`.
- `specs/**`, `MIGRATION.md`, `scripts/sync-check.sh`, `.sync-state.json`,
  `resources/` — development infrastructure and maintainer assets.

**Never read from public** (public-owned governance): `.github/`, `LICENSE`,
`.vscode/`, `.gitignore`, public `.claude/settings.json`.

## How to run

1. Make sure the public repo is at `~/senzing.git/senzing-bootcamp-claude-plugin`
   (or note its path), checked out at the branch/commit whose changes you want.
2. Ideally start from a **clean dev working tree** so the retrofit diff is easy
   to review (the script warns if the retrofit paths are already dirty).
3. Run from the dev repo:

   ```console
   .claude/skills/retrofit-from-public/retrofit.sh
   ```

   Pass a path to override the default source:

   ```console
   .claude/skills/retrofit-from-public/retrofit.sh /path/to/public-repo
   ```

The script enforces safety guards and **aborts** if any fail: the destination
isn't this dev repo, the source isn't a git repo, the source's `origin` isn't
`Senzing/senzing-bootcamp-claude-plugin`, source and destination are the same
directory, or `rsync` is missing.

## After it runs

The script **only updates the dev working tree** — no commit, no push.

1. Report the script's summary, including its "In dev but not in public" list and
   the `git status --short` block.
2. Review the diff before committing:
   `git -C . diff -- plugins .claude-plugin docs README.md`.
3. For anything in the "In dev but not in public" list, decide per file whether
   it's a dev-only addition to keep or content removed in public to delete — the
   script never deletes it for you.
4. Sanity-check the reverse transform in the diff: dev self-references should read
   `docktermj/senzing-bootcamp-claude-plugin` and `plugin.json` `author` should
   still be `Senzing`.
5. ⛔ **Run the full suite, and reconcile every test the retrofit desynced.**

   ```bash
   python3 -m pytest -q
   ```

   **This is not a formality, and no guard can replace it — the suite going red
   *is* the signal.** A retrofit copies `plugins/`, `.claude-plugin/`, `docs/` and
   `README.md`; it never copies `tests/`, because they are not in the public mirror
   and cannot come back. So a prose edit made downstream lands in a shipped file
   while the dev-only test that pins that sentence **verbatim** keeps asserting the
   old wording, and nothing reconciles the two.

   The worked example is `2223961` (2026-08-16), the British→US spelling
   corrections: a *correct* edit, faithfully retrofitted, which left **12 failed /
   2730 passed** — ten of them this desync, each pinning a sentence the retrofit had
   already changed, plus an INV-065 pair where the example `.md` was retrofitted and
   the committed PDF was not. Nobody noticed until the next full run, because this
   step did not exist.

   Reconcile by **updating the assertion to the retrofitted wording**, not by
   reverting the prose — the public edit is the correction. Where a shipped file and
   a generated artifact are pinned to each other (INV-065), regenerate the artifact.

6. Do **not** commit unless asked. If you do, commit subjects in these repos start
   with `#<issue-number>`.

## Guardrails

- **Apply the inverse transform, scoped.** Only the repo slug and the marketplace
  owner name. Never touch `plugin.json`'s `author`, product mentions of "Senzing",
  or `LICENSE`.
- **Never delete** dev files; report and let the maintainer decide.
- **Never report a retrofit as done on an unrun suite.** `tests/` cannot come back
  from public, so the copy routinely moves prose out from under the assertions that
  quote it. Step 5 is the only thing that catches it.
- **Never pull governance** into dev.
- **Don't guess the source.** If the public repo isn't at the default path and
  none was given, ask rather than retrofitting from somewhere uncertain.
- **Don't commit or push.** Sync files, report, stop.
- Keep this manifest and `retrofit.sh` in step with `propagate-to-public` — the
  two must always agree on which paths are propagated and on the transform.
