# Name which Claude interface is meant, everywhere

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The plugin and its docs say "the Claude app" — a phrase that names nothing. Claude Code, which
this plugin plugs into, runs in more than one interface, and **Claude Desktop runs Claude Code
too**, so "Claude Code" does not distinguish the terminal from the desktop application either.
Two concrete consequences:

- A Bootcamper is told, in a pinned question, to "set it with your **Claude app's** model and
  effort controls" and has to guess which controls that means.
- `README.md` offered "**Claude Desktop** (desktop)" beside "**Claude Code** (command line)" as
  though they were two products, then linked to a section headed "Using Claude Code" — which is
  the CLI, but says so nowhere.

The maintainer's ruling: there are two interfaces a Bootcamper installs into — **Claude Desktop**
and the **Claude Code CLI** — and every reference must say which one.

## Root cause

No rule ever said to name the interface, so each file chose its own shorthand:

- `skills/bootcamp-onboarding/ground-rules.md` — the surface-adaptive model/effort nudge (INV-098)
  names "**Claude Code (CLI)**" against "**Desktop, web, or an IDE extension**", and its pinned
  non-CLI question and its "how to make the change" line both say "their Claude app's controls".
- `skills/graduation/SKILL.md` — carries its own copy of the same nudge, with the same wording.
- `docs/model-selection.md` — "adapts to the Claude application surface"; "the app's model/effort
  controls".
- `README.md` / `docs/README.md` — "Claude Desktop (desktop)" vs "Claude Code (command line)";
  "Using Claude Code" as the CLI heading; one stray "Claude CLI"; a troubleshooting section headed
  "Claude code inoperative" whose body is entirely about Claude Desktop.
- `tests/test_retired_vocabulary.py` — the repo's registry for exactly this defect class had no
  entry for it, and scans only `plugins/`, so the install docs were out of its reach anyway.

## Proposed change

- Fix a canonical name per interface: **Claude Desktop**, **Claude Code CLI**, **the Claude web
  app**, **a Claude IDE extension**. Reserve "Claude Code" for the product.
- Sweep the shipped plugin: the model/effort nudge in `ground-rules.md` and `graduation/SKILL.md`
  (both pinned question forms, both "how to change it" lines, the per-stage table note) and
  `docs/model-selection.md`.
- Add a **Naming the Claude interface** section to `ground-rules.md` so the rule governs all
  output rather than only the nudge, including that "Claude Code" is the product and that vague
  wording is allowed only where the interface genuinely cannot be determined.
- Rewrite the install docs: `README.md` states that this is one Claude Code plugin with two
  interfaces, names both, and heads its walkthrough "Using Claude Desktop"; `docs/README.md`
  becomes "Using the Claude Code CLI" and links back. Fix the anchors on both sides and rename
  "Claude code inoperative" to "Claude Desktop inoperative".
- Register `Claude app` / `Claude application` in the retired-vocabulary registry, and extend that
  registry to the repo-root install docs `propagate-to-public` mirrors as user-facing content.
- Clarify INV-098's own wording in place (no meaning change; the four interfaces stand).

## Acceptance criteria

- [ ] No shipped or user-facing file says "Claude app" / "Claude application" except on a line framing it as retired; the registry enforces it and covers `README.md` and `docs/*.md`.
- [ ] The model/effort nudge names all four interfaces, in both `ground-rules.md` and `graduation/SKILL.md`, and its non-CLI pinned question substitutes the one interface the Bootcamper is on.
- [ ] "Claude Code" is used only for the product; the terminal is the "Claude Code CLI".
- [ ] `README.md` names both primary interfaces, says they are two interfaces of one plugin, and heads its walkthrough "Using Claude Desktop"; `docs/README.md` heads "Using the Claude Code CLI".
- [ ] Every cross-document and in-page anchor in both install docs resolves.
- [ ] Vague wording appears only alongside the unknown-interface condition.
- [ ] INV-098's four interfaces are unchanged; the pinned gate question (INV-069) is unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — nudge wording; new "Naming the Claude interface" section.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — its copy of the nudge.
- `plugins/senzing-bootcamp/docs/model-selection.md` — the table note.
- `plugins/senzing-bootcamp/hooks/README.md` — two bare "the CLI" references.
- `README.md`, `docs/README.md` — install paths, headings, anchors.
- `.claude/skills/propagate-to-public/SKILL.md` — the file-inventory note.
- `tests/test_retired_vocabulary.py`, `tests/test_interface_naming.py` (new).
- `specs/INVARIANTS.md` — the naming requirement; INV-098 clarified in place.

## Source

- Maintainer request (2026-07-28): "In the past, I've been using the phrase 'Claude app'. This is not precise. There are two user interfaces: 'Claude Desktop' and 'Claude CLI'. Review and modify the plugin and it's documentation so that there is clear specification of which user interface is referenced."
- Maintainer decisions (2026-07-28, asked before the sweep): the terminal is named **Claude Code CLI** (product-accurate, and keeps "Claude Code" free to mean the plugin host); the web app and IDE extensions are **kept and named precisely** rather than collapsed into the two, so INV-098's coverage is not narrowed.
- Priority: Medium
- Related specs: `surface-aware-model-effort-instructions.md` (established INV-098); INV-063, INV-069, INV-098, INV-114

## Invariants introduced

- `INV-158` — Every reference to a Claude user interface names which one, from a fixed set of four names; "Claude Code" names the product and never an interface; "the Claude app" is retired vocabulary; vague wording is permitted only where the interface cannot be determined; the install docs document both primary interfaces with resolving cross-links (recorded in `specs/INVARIANTS.md`).
