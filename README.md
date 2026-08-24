# securable-claude-plugin <a href="https://www.buymeacoffee.com/xcaciv"> <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="25"> </a>

A Claude Code plugin offering secure code generation and securability analysis through application of the OWASP FIASSE: The Securable framework. Also, part of (OWASP Secure Agent Playbook)[https://github.com/OWASP/secure-agent-playbook].

## Overview

This plugin augments Claude Code with three capabilities:

1. **Securability Engineering Review** — Analyze existing code for securable qualities using the ten SSEM attributes (FIASSE v1.1) across three pillars (Maintainability, Trustworthiness, Reliability), producing scored assessments with actionable findings.
2. **Securability Engineering Code Generation** — Generate new code that embodies securable qualities by default, applying OWASP FIASSE principles as engineering constraints.
3. **PRD Securability Enhancement** — Enhance product requirements documents with ASVS level selection, feature-level ASVS requirement mapping, SSEM implementation annotations, and FIASSE tenet coverage.
4. **FIASSE Lookup** — Answer FIASSE/SSEM questions (definitions, principles, attributes, scoring conduct, section numbers) from the bundled framework reference, citing section numbers.

Agent-facing guidance lives in [AGENTS.md](AGENTS.md) (the [AGENTS.md standard](https://agents.md) entry point, imported by `CLAUDE.md`). A critical assessment of this plugin and its enhancement roadmap lives in [docs/critical-review-2026-08.md](docs/critical-review-2026-08.md).

## Installation

### Claude Code (recommended)

Install through the Claude Code plugin manager: open the interactive manager with `/plugin`, then use the Discover and Marketplaces tabs to add/install graphically.

### opencode and other agent tools

The skills follow the [Agent Skills](https://agentskills.io) standard (`SKILL.md` + YAML frontmatter) and the repo ships a tool-agnostic [AGENTS.md](AGENTS.md) entry point, so the pack also works outside Claude Code:

```bash
# From a checkout of this repo, into the current project (agent-standard path):
scripts/install_skills.sh --target .agents

# opencode project config, or global:
scripts/install_skills.sh --target .opencode
scripts/install_skills.sh --target "$HOME/.config/opencode"

# Claude Code project skills (without installing the plugin):
scripts/install_skills.sh --target .claude
```

The script copies `skills/`, `data/`, `plays/`, and `templates/` together under one root — the layout the skills' internal references depend on.

### Developing this plugin

Run `claude --plugin-dir .` from the repo root so commands and skills load exactly as a plugin install would. Note that the repo's root `CLAUDE.md`/`AGENTS.md` is read only when the repo is opened as a project; installed plugin users get the skills and commands, not that file.

## Slash Commands

Commands live in `commands/` (the plugin-standard location) and are thin dispatchers — each delegates to its skill, which holds the authoritative procedure.

| Command                      | Description                                               |
| ---------------------------- | --------------------------------------------------------- |
| `/securability-review`       | Run a full SSEM securability assessment on code           |
| `/secure-generate`           | Generate code with FIASSE/SSEM constraints applied        |
| `/prd-securability-enhance`  | Enhance PRD features with ASVS + FIASSE/SSEM requirements |
| `/fiasse-lookup`             | Look up FIASSE/SSEM reference material by topic           |

## Example: PRD Enhancement

See the before/after example in:

- `examples/prd-enhancement/input-prd.md`
- `examples/prd-enhancement/enhanced-prd.md`
- `examples/prd-enhancement/README.md`

## SSEM Model (FIASSE v1.1)

The Securable Software Engineering Model (SSEM) defines ten attributes across three pillars:

| **Maintainability** | **Trustworthiness** | **Reliability** |
| ------------------- | :-----------------: | --------------: |
| Analyzability       |   Confidentiality   |    Availability |
| Modifiability       |    Accountability   |       Integrity |
| Testability         |     Authenticity    |      Resilience |
| Observability       |                     |                 |

Each attribute is scored 0–10 and carries **equal weight** (1/10 of the overall score). The overall score is the mean of the attribute scores, subject to a weakest-link floor:

```text
raw mean = mean of all assessed attribute scores
floor    = lowest assessed attribute score + 3.0
overall  = min(raw mean, floor)
```

The floor keeps a single catastrophic attribute from being averaged away — a service that is strong everywhere except input handling is not an adequate service. Pillar scores are reported as diagnostics and never feed the overall score. See `skills/securability-engineering-review/SKILL.md` for the full rubric, the `Not assessed` / `N/A` states, and severity classification.

> **Scoring conduct**: Per FIASSE v1.1 Appendix A.4, a composite SSEM score is a directional management aid for tracking a system against itself over time — not a statement of assurance, compliance, or security. Every report pairs the score with its rationale and a prioritized list of changes.

> **v1.1 update**: "Request Surface Minimization" is now **Canonical Parsing** (S4.4.1.1) and "Derived Integrity" is now **Isolated Integrity** (S4.4.1.2). v1.1 also adds the Quality-Security Relationship (S2.4), the Securability Report (S5.2.1–S5.2.5), and scoring guidance (SA.4). Measurement guidance lives in Appendix A (`data/fiasse/SA.*.md`).

## Project Structure

```text
AGENTS.md                          # Canonical agent entry point (AGENTS.md standard, tool-agnostic)
CLAUDE.md                          # Thin stub importing AGENTS.md (project-mode Claude Code)
.claude-plugin/
  plugin.json                      # Plugin manifest (Claude Code)
  marketplace.json                 # Marketplace manifest
commands/
  securability-review.md           # /securability-review — thin dispatcher to the review skill
  secure-generate.md               # /secure-generate — thin dispatcher to the generation skill
  prd-securability-enhance.md      # /prd-securability-enhance — thin dispatcher to the PRD skill
  fiasse-lookup.md                 # /fiasse-lookup — thin dispatcher to the lookup skill
.claude/
  settings.json                    # Repo-development permissions (not shipped to plugin installs)
.claudeignore                      # Files excluded from context (repo development only)
.gitignore                         # Excludes test run artifacts (iteration-*/) from VCS
data/
  asvs/                            # OWASP ASVS 5.0 requirement chapters (V1–V17)
  fiasse/                          # FIASSE v1.1 reference sections (S1.x–S8.x + Appendix A as SA.x)
skills/
  securability-engineering/        # Code generation wrapper skill
  securability-engineering-review/ # Code analysis skill
  prd-securability-enhancement/    # PRD securability enhancement skill
  fiasse-lookup/                   # FIASSE/SSEM reference lookup skill
plays/
  code-generation/                 # Step-by-step code generation workflows
  code-analysis/                   # Step-by-step analysis procedures
  requirements-analysis/           # Step-by-step PRD enhancement workflows
templates/
  finding.md                       # Individual finding format
  report.md                        # Full assessment report format
template/
  SKILL.md                         # Template for creating new skills
scripts/
  extract_fiasse_sections.py       # Utility to extract sections from FIASSE v1.1 framework markdown
  install_skills.sh                # Layout-preserving installer for opencode / other agent tools
  build_plugin_zip.sh              # Release zip builder
  generate_marketplace_json.sh     # Release marketplace manifest builder
examples/
  prd-enhancement/                 # Before/after PRD securability enhancement example
docs/
  critical-review-2026-08.md       # Critical assessment + enhancement plan for this plugin
tests/                             # Skill regression tests (see Testing below)
  run_tests.py                     # Claude Code CLI test runner
  README.md                        # Test workspace conventions
  prd-securability-enhancement-workspace/
  securability-engineering-workspace/
  securability-engineering-review-workspace/
```

## Testing

Each skill has a regression workspace under [`tests/`](tests/) that exercises it
on three realistic prompts and grades the output via LLM-as-judge against an
asserted expectation set. Workspaces share a common shape:

```text
tests/<skill>-workspace/
  evals/
    evals.json            # prompts + assertions for each eval
    inputs/               # input fixtures (PRDs / source files)
  skill-snapshot/         # frozen pre-optimization SKILL.md (the baseline)
  iteration-N/            # generated outputs (gitignored)
```

To run a workspace end-to-end against the live skill plus the snapshot
baseline, with grading:

```bash
# Requires the `claude` CLI on PATH and Python 3.9+
python tests/run_tests.py tests/securability-engineering-workspace --grade

# Just the live skill, just one eval
python tests/run_tests.py tests/securability-engineering-review-workspace \
    --config with_skill --eval-id 1 --grade
```

See [`tests/README.md`](tests/README.md) for full conventions, the per-iteration
output layout, and how the runner integrates with the skill-creator
aggregator and viewer.

## Versioning

The plugin carries its own semantic version, independent of the FIASSE version it targets.

- **Plugin version** (`.claude-plugin/plugin.json`) — semver for this plugin's own behaviour. A major bump means the review output changed incompatibly. `2.0.0` is the first release of the ten-attribute, equal-weight scoring model with a weakest-link floor.
- **FIASSE target version** — the framework release the reference data is extracted from. Recorded machine-readably in the `fiasse_version` frontmatter of every file under `data/fiasse/`, and in prose here and in `CLAUDE.md`.

The two moved together through `1.0.4` and no longer do. Tracking a new FIASSE release is not automatically a major plugin bump, and a scoring change is a major bump whether or not FIASSE moved.

Release tags are `v<semver>` (e.g. `v2.0.0`). `scripts/build_plugin_zip.sh` and `scripts/generate_marketplace_json.sh` both derive the published version by stripping the leading `v`; the git ref keeps it.

## References

- [FIASSE Framework v1.1](https://github.com/OWASP/FIASSE/blob/v1.1/docs/securable_framework.md)  referenced version
- [OWASP/FIASSE](https://github.com/OWASP/FIASSE) — Source repository
- [OWASP/FIASSE](https://owaspfiasse.org) — Official Home
- [OWASP secure-agent-playbook](https://github.com/OWASP/secure-agent-playbook) — Larger combined project for agent-oriented guidance
- [Securability-Engineering](https://github.com/Securability-Engineering) — Organization hosting IDE-specific versions of this plugin
- [loose-notes_claude_aspnet_pva](https://github.com/Securability-Engineering-Plugin-Tests/loose-notes_claude_aspnet_pva) — Worst-case experiment test project

## License

CC-BY-4.0 — See [LICENSE](LICENSE)
