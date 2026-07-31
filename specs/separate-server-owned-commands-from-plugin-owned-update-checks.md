# Step 1b mixes server-owned install commands with plugin-owned update checks, and says neither wins

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-02-sdk-setup/SKILL.md:132` gives two instructions and no precedence between them:

```text
Get the platform's commands from
`sdk_guide(topic='install', platform='<platform>', language='<language>')` and use the ones below.
```

Fetch from the server, **and** use the inlined ones. Which governs when they differ is unstated —
and the list below that sentence is **half server-owned and half plugin-owned**, which makes the
ambiguity actively misleading rather than merely loose.

Verified against server 1.32.2, docs indexed 2026-07-29 11:11 UTC, 2026-07-31, by reading what
`sdk_guide(topic='install', platform=…)` actually returns for all four platforms:

| Command in Step 1b | In the server's response? |
|---|---|
| `apt install senzingsdk-runtime senzingsdk-setup` | **yes** — `install_commands` |
| `brew install --cask senzingsdk`, `brew upgrade --cask` (install form) | **yes** — `install_commands` |
| `scoop install senzingsdk/senzingsdk` | **yes** — `install_commands` |
| `yum install -y senzingsdk-runtime senzingsdk-setup` | **yes** — `install_commands` |
| `dpkg-query -W` / `rpm -q` (installed version) | **no** |
| `apt-cache policy` / `yum check-update` (available version) | **no** |
| `brew outdated --cask` / `brew info --cask` | **no** |
| `scoop status` / `scoop info` | **no** |

The server's `install_commands` cover installing; `post_install` covers *presence* checks
(`ls libSz.so`, `Test-Path Sz.dll`). **Nothing in any of the four responses queries an installed
version or checks for an available one.** Those six commands are ordinary package-manager
mechanics the plugin supplies because the server documents none of them — which is the same
coverage hole as the 4.x → 4.y procedure gap reported upstream on 2026-07-31.

**What the ambiguity costs.** An agent that follows the sentence literally fetches from
`sdk_guide`, finds no `brew outdated --cask` anywhere in the response, and has to guess: either
the inlined list is wrong and should be discarded, or the server's response is incomplete. Both
guesses are bad. The likelier failure is quieter — substituting a server *install* command where
Step 1b wanted a *check*, which on macOS means running `brew install --cask` when the intent was
`brew outdated --cask`, i.e. performing the update instead of testing for one, before the
bootcamper has been asked.

This is not a wrong Senzing fact. Every fact in Step 1b agrees with the server. It is a
**provenance** defect: the text does not distinguish what the plugin holds on loan from the server
(and must re-ask) from what the plugin owns outright (and the server cannot supply).

## Root cause

Step 1b was written in one pass from four `sdk_guide` responses plus package-manager knowledge,
and the two sources were never separated in the prose. The `sdk_guide` call was cited once, at the
top, as though it covered everything below it. Nothing was factually wrong, so nothing flagged it —
the defect is only visible when you ask *which* of these commands the server actually returned,
which is precisely the question this sweep exists to ask.

## Proposed change

1. **Split the sentence into two, by ownership.** State that install and update *commands* come
   from `sdk_guide` and its live response is authoritative — the inlined forms are a dated
   illustration, re-read them per run. Then state separately that the **installed-version query
   and the available-version check are plugin-owned**, because the server documents neither, and
   name that explicitly so a reader who cannot find them in the response does not conclude they
   are wrong.
2. **Mark the two groups in the per-platform blocks**, so the distinction survives someone
   skimming to the code fence rather than reading the preamble. A one-word label per line
   (`# server-documented` / `# plugin-owned`, or grouping them under two sub-headings) is enough;
   the point is that a reader copying a command can tell which kind it is.
3. **Adopt the shape the plugin already uses correctly elsewhere.**
   `module-05-data-quality-mapping/phase1-quality-assessment.md` inlines a feature table and
   labels it verified-against-a-version, explicitly partial, and "re-read it … rather than
   trusting this table — it is an illustration of *how the specification marks type*, not a
   substitute for asking". Step 1b's server-owned half wants exactly that framing.
4. **Keep the plugin-owned half inlined and unhedged.** It is not on loan and there is nothing to
   re-ask; hedging it would send readers to a server that has no answer, which is worse than
   stating it plainly. Its honest caveat is a different one — see criterion 5.

⚠️ **Do not "fix" this by deleting the inlined commands and relying on `sdk_guide` alone.** Half of
them are not in the server's response, so that would remove the only source for the update check
and leave Step 1b unable to do its job.

## Acceptance criteria

- [ ] Step 1b states which source is authoritative for install/update commands (the server's live
      response) and that the inlined forms are a dated illustration to be re-read per run.
- [ ] Step 1b states that the installed-version query and available-version check are
      **plugin-owned because the server documents neither**, so a reader who cannot find them in
      `sdk_guide`'s response knows that is expected.
- [ ] The two groups are distinguishable **inside** the per-platform command blocks, not only in
      the preamble.
- [ ] No inlined command is deleted — the plugin-owned half has no other source.
- [ ] The dated provenance on the server-owned half names the tool, the server version and the
      date, as it does now.
- [ ] The plugin-owned half carries its real caveat: it is unverified on macOS and Windows in this
      repo's environment (Linux only), consistent with the disclosure already recorded in
      `specs/offer-to-update-an-existing-senzing-install.md`.
- [ ] `tests/test_sdk_update_offer.py` still passes; a test asserts the ownership split so a later
      edit cannot re-merge the two groups.
- [ ] **Re-verification clause:** implementing this requires re-confirming that
      `sdk_guide(topic='install', platform=…)` still returns **no** installed-version query and
      **no** available-version check, for all four platforms. If the server has started supplying
      either, that half stops being plugin-owned and should be delegated instead — which would
      change this spec's answer, not just its wording.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 1b's preamble (`:130-133`) and the four per-platform command blocks.
- `tests/test_sdk_update_offer.py` — the ownership-split assertion.

## Source

- **Found by `delegate-to-mcp-server`, 2026-07-31.** Server 1.32.2, docs indexed
  2026-07-29 11:11 UTC — **both axes unchanged since the previous sweep**, so this run was scoped
  to sites with no ledger row, which is where Step 1b sat: it was added the same day, by
  `offer-to-update-an-existing-senzing-install`.
- Priority: Medium. No Senzing fact is wrong and nothing is blocked; the risk is an agent
  substituting an install command for a check, which on macOS would perform the update before the
  bootcamper is asked.
- MCP re-check: `sdk_guide(topic='install', …)` for `linux_apt`, `linux_yum`, `macos_arm`,
  `windows` (all with `language='java'` for the non-Linux pair, since `language='python'` returns
  nothing there — the Python SDK is Linux-only). Install commands confirmed present;
  installed-version query and available-version check confirmed **absent** from all four.
- Upstream: not applicable to this spec. The underlying coverage gap — the server documenting no
  update path — was sent as a `feature` request on 2026-07-31 and **must not be re-filed**; see
  `specs/offer-to-update-an-existing-senzing-install.md` → "Upstream: feature request sent
  2026-07-31".
- Related specs: `specs/offer-to-update-an-existing-senzing-install.md` (added the text this
  corrects, and carries the macOS/Windows unverified disclosure),
  `specs/why-entities-default-flags-has-no-composite-members.md` (INV-194 — the same
  ask-the-right-tool discipline that surfaced this).

