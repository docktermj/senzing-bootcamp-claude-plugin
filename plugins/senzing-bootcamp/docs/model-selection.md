# Model & effort selection (maintainer notes)

This is a maintainer/developer reference — it does not ship as bootcamper-facing
content. It records which plugin components can carry a model/effort override,
the scope of those overrides, and a best-value model evaluation for each skill,
so the analysis is not re-investigated.

**The headline:** a skill's `model:`/`effort:` override is **turn-scoped**, so
for this interactive, multi-turn plugin the **session** model/effort — not
per-skill frontmatter — is the lever that actually governs the experience.

## Which components can carry a model/effort override

A model/effort override only means anything for components that actually invoke
Claude. `type: command` hooks and the scripts they run are deterministic
programs and never "run under a model."

| Component | Model? | Effort? | How / scope |
|---|:---:|:---:|---|
| Skills (`SKILL.md` frontmatter) | ✅ | ✅ | `model:` + `effort:` (`low`/`medium`/`high`/`xhigh`/`max`). **Turn-scoped.** |
| Slash commands (`.md` frontmatter) | ✅ | ❌ | `model:`; no effort field |
| Subagents (`agents/*.md`) | ✅ | ✅ | `model:` (`inherit` default) + `effort:`; persists for the subagent's whole run |
| Command hooks (`type: command`) | ❌ | ❌ | Deterministic program; only reads session effort via `$CLAUDE_EFFORT` |
| Prompt hooks (`type: prompt`) | ✅ | ❌ | `model:` in hook config |
| Agent hooks (`type: agent`) | ➖ | ➖ | Inherits the spawned subagent's `model:`/`effort:` |
| Scripts (run by hooks/commands) | ❌ | ❌ | Not model-executed |

## Skill overrides are turn-scoped (the load-bearing constraint)

From the Claude Code skills docs:

> The override applies for the rest of the current turn and is not saved to
> settings; the session model resumes on your next prompt.

The bootcamp skills are **interactive and multi-turn** — every step ends by
yielding to the bootcamper after one 👉 question, so each following step arrives
as a *new user prompt* and the override **resets** to the session model/effort. A
`model:` on a module skill therefore governs only the module-start turn, not the
whole module.

Consequences:

- The reliable lever for the bootcamp is the **session** model/effort.
- Per-skill `model:` frontmatter on an interactive skill gives a false sense of
  cross-turn control — avoid it.
- Sustained per-skill model control exists only via `context: fork` (the skill
  runs in a subagent that holds its own `model:`/`effort:` for its whole run) —
  but that moves the work into an isolated subagent, which is wrong for skills
  that must converse with the bootcamper turn-by-turn.

## Model tiers (for "best value")

Approximate positioning (verify current pricing/availability before relying on
the numbers):

| Model | Tier | ~Price (in/out per MTok) | Adaptive thinking | Notes |
|---|---|---|:---:|---|
| Fable 5 (`claude-fable-5`) | Top | ~$10 / ~$50 | Always on | Most capable; for long-running agents; slower; ~2× Opus cost |
| Opus 4.8 (`claude-opus-4-8`) | High | ~$5 / ~$25 | Yes | Complex agentic coding default |
| Sonnet 5 (`claude-sonnet-5`) | Mid | ~$3 / ~$15 | Yes | Speed/cost/capability sweet spot |
| Haiku 4.5 (`claude-haiku-4-5`) | Budget | ~$1 / ~$5 | **No** | Fastest; no adaptive thinking |

For a protocol-heavy (⛔ gates, INV-056 pinned wording, one-👉-per-turn),
MCP-first teaching plugin, Haiku's lack of adaptive thinking is a real risk of
gate/format slips, and Fable's premium buys little the workloads here need.

## Per-skill best-value evaluation

Best value = the capability the workload needs, at the lowest tier that meets it.

| Skill | Workload | Best value | Rationale |
|---|---|:---:|---|
| `bootcamp-onboarding` | Gated preface, exact-wording gates, preference capture | Sonnet 5 | Protocol adherence needs adaptive thinking + strong instruction-following; no heavy code → Opus overkill, Haiku risky |
| `module-01-business-problem` | Discovery conversation, document the problem | Sonnet 5 | Conversation-led, light technical |
| `module-02-sdk-setup` | Cross-platform install, license/engine/DB config, build-from-source recovery | Opus 4.8 | Largest skill, most error-prone, platform-specific; install/config errors are high-cost |
| `module-03-system-verification` | Verify end-to-end, report | Sonnet 5 | Mostly run / check / report |
| `module-03b-truthset-visualization` | Load Truth Set, run viz server, visualize | Sonnet 5 | Mostly run / render |
| `module-04-data-collection` | Gather sources into `data/raw/` | Sonnet 5 | Data wrangling + light code |
| `module-05-data-quality-mapping` | Quality scoring + mapping to the Entity Spec via `mapping_workflow` | Opus 4.8 | Mapping correctness drives resolution quality — the technical crux |
| `module-06-data-processing` | Load mapped data (SDK), validate, load-safety rails | Sonnet 5 (Opus if bespoke load code) | Heavy mapping already spent in M5; M6 executes/validates with guardrails |
| `module-07-query-visualize-discover` | Query SDK code, visualize, discovery | Sonnet 5 | Iterative query/exploration; Sonnet's speed suits it |
| `graduation` | Recap reconcile, PDF, production project (code/config/docs), report | Opus 4.8 | Crown-jewel deliverable; production code/config correctness matters most |

## Module-start commands (the nudge)

`ground-rules.md` → "Module start banners and transitions" surfaces this per-stage recommendation
at the start of each module (and `graduation/SKILL.md` at the graduation banner): a single 👉
switch question when the recommendation changes from the current stage, otherwise a brief
statement. Switching is optional; the session-level `/model` and `/effort` persist for the session
(unlike per-skill frontmatter). Keep this table in sync with the mirror in `ground-rules.md`.

| Stage | Recommended | Commands |
|---|---|---|
| Onboarding, Bootcamp preparation, Modules 1, 3, 4, 7 | Sonnet 5, medium effort | `/model sonnet` · `/effort medium` |
| Modules 2, 5 | Opus 4.8, high effort | `/model opus` · `/effort high` |
| Module 6 | Sonnet 5, high effort (Opus if bespoke load code) | `/model sonnet` · `/effort high` |
| Graduation | Opus 4.8, high effort | `/model opus` · `/effort high` |

## Recommendation

Because skill overrides reset per prompt, realize the evaluation through the
**session** model — not per-skill frontmatter:

- **Value-optimized (the `README.md` default):** run the session on **Sonnet 5**,
  and switch the session up to **Opus 4.8** for the correctness-critical stretches
  — Modules 2 and 5, and graduation (optionally Module 6 with custom load code).
  Switch mid-session with `/model claude-opus-4-8` and back with
  `/model claude-sonnet-5`. **Haiku 4.5** is not recommended for any
  bootcamper-facing skill (protocol risk); **Fable 5** is not the value pick here.
- **Simplest (one model, no switching):** run the whole session on
  **Opus 4.8 + `--effort high`**. Zero-friction — one strong model for everything
  — at the cost of over-paying on the lighter conversational modules.

## Optional lever: invoking-turn-only effort

`effort:` frontmatter on the heaviest single-turn skills (`graduation`,
`module-02-sdk-setup`, `module-05-data-quality-mapping`) will bump reasoning on
the turn that *invokes* the skill, then reset like any skill override. It is a
minor, honest tuning knob — if added, it must be understood (and labeled in the
frontmatter's vicinity) as **invoking-turn-only**, not a module-wide setting. It
is intentionally **not** wired today, to avoid implying persistence the mechanism
does not provide.

## Sources

- Skills model/effort scope: `code.claude.com/docs/en/skills.md` (frontmatter reference).
- Subagents model/effort: `code.claude.com/docs/en/sub-agents.md`.
- Hooks: `code.claude.com/docs/en/hooks.md`.
- Model positioning/pricing: `platform.claude.com/docs/en/about-claude/models/overview`.
