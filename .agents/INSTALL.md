# Installing the Securable Engineering pack for any AGENTS.md / SKILL.md agent

For agents that read [AGENTS.md](https://agents.md) context files and discover
[Agent Skills](https://agentskills.io)-format skills (`SKILL.md` + YAML
frontmatter) from an `.agents/` tree — Codex, Zed, Amp, opencode, and others.
These instructions are written to be followed by an agent ("Fetch and follow
instructions from …") or by a person at a terminal. They only copy files —
no packages are installed and no runtime hooks are added.

Agent-specific adapters exist for Claude Code (`.claude-plugin/`), Cursor
(`.cursor-plugin/`), Devin (`.devin-plugin/`), and opencode
(`.opencode/INSTALL.md`); prefer those where they apply.

## Installation

1. Clone this repository somewhere temporary:

   ```bash
   git clone --depth 1 https://github.com/Securability-Engineering/securable-claude-plugin.git /tmp/securable-claude-plugin
   ```

2. From the project root, run the layout-preserving installer against the
   agent-standard path:

   ```bash
   /tmp/securable-claude-plugin/scripts/install_skills.sh --target .agents
   ```

   The script copies `skills/`, `data/`, `plays/`, `templates/`, `schema/`,
   `core/`, and `rules/` together under `.agents/`. That sibling layout is
   load-bearing: the relative references inside each `SKILL.md`
   (`../../data/…`, `../../plays/…`, `../../templates/…`) depend on it.
   If your agent discovers skills from a different root, pass that root as
   `--target` instead — the whole set moves as one unit.

3. Optionally, give the agent the always-on securability kernel: append the
   contents of `.agents/core/kernel.md` (about 300 tokens) to the project's
   `AGENTS.md`, or point your agent's always-on context at it. Pre-generated
   harness bindings of the same kernel ship under `bindings/` (Cursor rule,
   Copilot instructions, Gemini CLI context, Aider conventions).

4. Optionally remove the clone:

   ```bash
   rm -rf /tmp/securable-claude-plugin
   ```

## Verify

Ask the agent to list its skills. You should see:

- `securability-engineering-review`
- `securability-engineering`
- `prd-securability-enhancement`
- `fiasse-lookup`

## Updating

Re-clone and re-run the installer with `--force`.

## Getting help

- Issues: https://github.com/Securability-Engineering/securable-claude-plugin/issues
- Full documentation: https://github.com/Securability-Engineering/securable-claude-plugin
