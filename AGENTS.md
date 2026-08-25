# Securable Engineering Plugin — FIASSE / SSEM

This repository is an agent skill pack (and Claude Code plugin) that augments a coding agent with **securable software engineering** capabilities, aligned with [FIASSE v1.1](https://github.com/OWASP/FIASSE/blob/v1.1/docs/securable_framework.md). It provides four capabilities:

1. **Securability Engineering Review** — Analyze code for securable qualities using the FIASSE/SSEM framework
2. **Securability Engineering Code Generation** — Generate code that embodies securable qualities by default
3. **PRD Securability Enhancement** — Enhance product requirements with ASVS 5.0 coverage and FIASSE/SSEM implementation guidance
4. **FIASSE Lookup** — Answer FIASSE/SSEM questions from the bundled framework reference

This file is the canonical agent entry point ([AGENTS.md standard](https://agents.md)). `CLAUDE.md` imports it; do not duplicate guidance between the two.

<!-- securable-kernel:begin (generated from core/kernel.md — edit there, run scripts/build_bindings.py) -->
## Securable engineering (always apply)

1. **Parse, don't trust.** Input crossing a trust boundary (HTTP/RPC, queue, file, CLI, env, webhook, foreign DB rows) is parsed once at the boundary into a typed structure — only expected named fields, failing closed.
2. **Authority is server-side.** Identity, ownership, tenancy, role, and money/state come from authenticated server-side sources, never from client-supplied values or unverified claims.
3. **Never emit:** string-built SQL/shell/paths; JWT verification without pinned algorithm+audience+issuer; mass assignment from raw request bodies; bare catch-alls or silent failure; unbounded reads; external calls without timeouts; secrets in code/logs/errors; non-constant-time secret comparison.
4. **Observable security.** Security-relevant actions emit structured events (actor, action, target, outcome); failure paths log; errors shown to callers never leak internals.
5. **Securability Notes.** Close security-relevant work with 2–4 lines: boundaries handled, decisions a reviewer must see, anything unverified.

If `.securable/requirements.yaml` exists it is the authoritative security-requirements source: implement to its acceptance criteria and flip `status` planned→implemented only. Depth on demand via the securable skills: securability-engineering (generation) · securability-engineering-review (SSEM scoring) · prd-securability-enhancement (requirements) · fiasse-lookup (reference).
<!-- securable-kernel:end -->

## Repository Layout

- `core/kernel.md` — The **securability kernel**: the ~300-token always-on distillation. Single source of truth; every binding is generated from it.
- `.claude-plugin/`, `.cursor-plugin/`, `.devin-plugin/`, `.opencode/`, `.agents/` — **Per-agent install adapters** (superpowers-style): one manifest or agent-followable `INSTALL.md` per harness, all pointing at the same `skills/` + `data/` tree. `.claude-plugin/plugin.json` is the canonical version source; `scripts/check_manifests.py` keeps the rest in lockstep.
- `bindings/` — **Generated** per-harness kernel bindings (Cursor rule, Copilot instructions, Gemini CLI context, Aider conventions). Never edit — run `scripts/build_bindings.py`.
- `skills/<name>/SKILL.md` — Skill definitions in the [Agent Skills](https://agentskills.io) format (YAML frontmatter + instructions). These are the authoritative procedure definitions.
- `commands/` — Thin slash-command dispatchers for Claude Code plugin installs. Each delegates to its skill; they hold no procedure content of their own.
- `schema/securable/` — JSON Schemas for the **securable contract** (`.securable/requirements.yaml` + `.securable/boundaries.yaml` in consuming projects). See `docs/securable-contract.md`; validator: `scripts/validate_securable.py`.
- `rules/opengrep/` — Held-check opengrep pack mapping the skills' anti-pattern tags to enforceable rules; fixtures in `tests/opengrep-fixtures/`.
- `data/asvs/` — OWASP **ASVS 5.0** requirement chapters (V1–V17), one file per section, with `when_to_use` frontmatter. Authoritative for requirement IDs — confirm every cited ID against these files.
- `data/fiasse/` — FIASSE v1.1 reference sections (S1.x–S8.x plus Appendix A as `SA.x`) with YAML frontmatter. Authoritative for definitions, measurement criteria, and principles.
- `plays/` — Step-by-step runbooks sequencing multi-skill workflows.
- `templates/` — Output format templates (`finding.md`, `report.md`).
- `scripts/` — Build, validation, installation, and report utilities (`build_bindings.py`, `validate_securable.py`, `check_refs.py`, `securability_report.sh`, `install_skills.sh`).
- `tests/` — Skill regression workspaces (`run_tests.py`, LLM-as-judge), the contract validator tests, the kernel A/B workspace (`kernel_ab.py`), and the opengrep fixtures.

**Path resolution rule**: paths like `data/asvs/README.md` inside skills, commands, and plays are relative to this repository/plugin root — never to the user's project. In a Claude Code plugin install the root is `${CLAUDE_PLUGIN_ROOT}`; anywhere else, resolve relative to the referencing file's position in this tree.

## Skills

### securability-engineering-review

Score a codebase, file, or merge request against the SSEM model: ten attributes, 0–10, equal weight, weakest-link floor, evidence-backed findings, three-part report.

**Invoke when**: the user asks to review, assess, audit, score, or evaluate code securability, security posture, code quality for security, or FIASSE/SSEM compliance.

**Definition**: `skills/securability-engineering-review/SKILL.md` (authoritative rubric) · Runbook: `plays/code-analysis/securability-engineering-review.md`

### securability-engineering

Wrap code generation with FIASSE/SSEM constraints so output is engineered to be securable by default — including when the user doesn't say "secure" but the component is security-sensitive (auth, uploads, queries, API endpoints, anything crossing a trust boundary).

**Invoke when**: the user asks to generate, scaffold, or refactor code — especially security-sensitive components — or asks for "secure", "securable", "hardened", or "production-grade" code.

**Definition**: `skills/securability-engineering/SKILL.md` · Full-loop runbook (opt-in): `plays/code-generation/securable-generation.md`

### prd-securability-enhancement

Enhance PRD features step-by-step: choose an ASVS level first, map features to ASVS 5.0 requirements, fill gaps from the coverage-gap pattern table, and annotate implementation expectations with SSEM attributes and FIASSE tenets.

**Invoke when**: the user asks to harden a PRD/spec, choose an ASVS level, map features to ASVS, find missing security requirements, or add testable security acceptance criteria.

**Definition**: `skills/prd-securability-enhancement/SKILL.md` · Runbook: `plays/requirements-analysis/prd-fiasse-asvs-enhancement.md`

### fiasse-lookup

Answer FIASSE/SSEM questions (definitions, principles, attributes, scoring conduct, section numbers) from `data/fiasse/`, citing section numbers rather than answering from memory.

**Definition**: `skills/fiasse-lookup/SKILL.md`

## Guiding Principles

1. **Securable ≠ Secure** — There is no static "secure" state (S2.1). Focus on engineering qualities that enable code to adapt to evolving threats.
2. **Engineer, Don't Hack** — Build securely through quality attributes, not adversarial/exploit thinking (S2.5).
3. **Reduce Material Impact** — Aim to reduce the probability of material impact from cyber events through pragmatic, context-appropriate engineering, balanced against business objectives (S2.3). Eliminating breaches entirely is not a practical goal.
4. **Transparency** — Generated and reviewed code should be observable: meaningful naming, structured logging, audit trails (S2.6).
5. **Least Astonishment** — Systems should behave intuitively and predictably; eliminate hidden side effects and surprising boundaries (S2.7).
6. **Boundary Control** — Apply strict control at trust boundaries (the "hard shell"); preserve flexibility in the interior (S4.3).
7. **Canonical Parsing** — Parse, don't validate: one strict parse at each trust boundary into a typed structure, failing closed (S4.4.1.1).
8. **Isolated Integrity** — Integrity-critical values are derived from server-side authority a client cannot set or bias (S4.4.1.2).
9. **Scoring Is Directional** — A composite SSEM score is a management aid for tracking a system against itself, never a statement of assurance or compliance (SA.4).
10. **Evidence over Assertion** — Cite what was actually read or run. Mark what wasn't inspected `Not assessed`; never fabricate file paths, requirement IDs, or tool results.

## Tooling Policy (third-party tools)

Usage is endorsement, and installation is intrusion. Three tiers, strictly separated:

1. **Runtime (skills, kernel, commands — anything acting in a user's project): never install.** Use the tools already present; when a check cannot run because tooling is absent, say so instead of implying verification happened. That absence is itself evidence (Testability/Observability). Both the generation and review skills state this explicitly.
2. **This repository's own CI: pinned, verified test dependencies only.** CI installs exactly what is needed to test the artifacts this repo ships (currently PyYAML for the validators and a version-pinned, checksum-verified opengrep release to prove the rule pack fires) — on ephemeral runners, never in a consumer's environment. A shipped rule pack CI cannot execute would be untested text.
3. **Reference workflows for consuming repositories: provisioning is the consumer's explicit decision.** CI runners are ephemeral, so a consumer's workflow must provision its own agent CLI; the example marks that step as theirs to replace with whatever their team already runs.

Only community-governed, non-commercial tools may be named or used anywhere in this repository (e.g., opengrep, not commercially licensed scanners).

## SSEM Model Quick Reference (v1.1 — 10 attributes)

| **Maintainability** | **Trustworthiness** | **Reliability** |
|:--------------------|:-------------------:|----------------:|
| Analyzability       | Confidentiality     | Availability    |
| Modifiability       | Accountability      | Integrity       |
| Testability         | Authenticity        | Resilience      |
| Observability       |                     |                 |

> **v1.1 note**: The ten attributes are unchanged from v1.0.4. What changed: "Request Surface Minimization" is now **Canonical Parsing** (S4.4.1.1), "Derived Integrity" is now **Isolated Integrity** (S4.4.1.2), the Transparency Principle moved to S2.6 and Least Astonishment to S2.7, and Appendix A gained **SA.4 Scoring and Enhancement Suggestions**. Measurement guidance is in Appendix A (`data/fiasse/SA.*.md`).

> **Authorization is not an SSEM attribute** (S3.2.2.3). It is a security *feature*, gathered as a requirement and implemented against acceptance criteria. Authenticity, Confidentiality, Integrity, and Accountability are what make it defensible.

> **ASVS numbering**: the bundled catalog is **ASVS 5.0** (V1 Encoding/Sanitization … V6 Authentication … V8 Authorization … V16 Logging). Do not use pre-5.0 chapter numbers; confirm every requirement ID against `data/asvs/` before citing it.

## Output Formats

- Individual findings: `templates/finding.md`
- Full assessment reports: `templates/report.md`

## Using This Pack With Different Tools

- **Claude Code (plugin)** — install via the plugin manager (`/plugin`); skills, commands, and data ship together. Skill and command paths resolve via `${CLAUDE_PLUGIN_ROOT}`. Manifest: `.claude-plugin/plugin.json`.
- **Claude Code (this repo as a project)** — for plugin development, run `claude --plugin-dir .` so commands and skills load exactly as an install would.
- **Cursor** — plugin manifest at `.cursor-plugin/plugin.json` (`skills` points at the shared `skills/` tree); the always-apply kernel rule ships pre-generated at `bindings/cursor/securable.mdc`.
- **Devin** — `devin plugins install Securability-Engineering/securable-claude-plugin`; manifest at `.devin-plugin/plugin.json`.
- **opencode** — fetch-and-follow `.opencode/INSTALL.md`, or run `scripts/install_skills.sh --target .opencode` inside a project (or `--target "$HOME/.config/opencode"` for global use). opencode also discovers `.claude/skills/` and `.agents/skills/`; the installer supports those targets too.
- **Other AGENTS.md tools (Codex, Gemini CLI, Zed, Amp, …)** — this file is read natively when the repo (or an installed copy) is in scope; skills follow the Agent Skills standard. Fetch-and-follow `.agents/INSTALL.md`, or install with the same script (`--target .agents`).

`scripts/install_skills.sh` performs a layout-preserving copy (`skills/`, `data/`, `plays/`, `templates/` under one root), which is what keeps the relative references inside the skills working unchanged.

## Testing

```bash
scripts/run_checks.sh                 # everything CI runs: refs, contract, bindings, detectors, manifests
python3 scripts/check_refs.py         # ASVS/FIASSE references resolve against data/
python3 tests/securable-contract/test_validate.py
python3 scripts/build_bindings.py --check
python3 tests/kernel_ab.py --self-test
OPENGREP_BIN=opengrep scripts/test_opengrep_rules.sh # needs opengrep installed

# Skill-behavior regression (requires the `claude` CLI on PATH):
python tests/run_tests.py tests/securability-engineering-workspace --grade
python3 tests/kernel_ab.py            # kernel A/B against the agent CLI
```

See `tests/README.md` for workspace conventions. When changing a skill, run its workspace before and after; assertions include ASVS 5.0 numbering correctness. When changing `core/kernel.md`, rebuild bindings and re-run the A/B workspace.

## References

- [FIASSE Framework v1.1](https://github.com/OWASP/FIASSE/blob/v1.1/docs/securable_framework.md) · [OWASP/FIASSE](https://github.com/OWASP/FIASSE) · License: CC-BY-4.0
