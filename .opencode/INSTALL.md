# Installing the Securable Engineering pack for opencode

These instructions are written to be followed by an agent ("Fetch and follow
instructions from …") or by a person at a terminal. They only copy files into
opencode's normal skill-discovery paths — no packages are installed and no
runtime hooks are added.

## Prerequisites

- [opencode](https://opencode.ai) installed
- `git` available on PATH

## Installation

1. Clone this repository somewhere temporary (it is only needed during the copy):

   ```bash
   git clone --depth 1 https://github.com/Securability-Engineering/securable-claude-plugin.git /tmp/securable-claude-plugin
   ```

2. Run the layout-preserving installer at the scope you want:

   ```bash
   # Project-level (run from the project root):
   /tmp/securable-claude-plugin/scripts/install_skills.sh --target .opencode

   # Global (all projects):
   /tmp/securable-claude-plugin/scripts/install_skills.sh --target "$HOME/.config/opencode"
   ```

   The script copies `skills/`, `data/`, `plays/`, `templates/`, `schema/`,
   `core/`, and `rules/` together under the target root. That sibling layout is
   load-bearing: the relative references inside each `SKILL.md`
   (`../../data/…`, `../../plays/…`, `../../templates/…`) depend on it.

3. Optionally remove the clone:

   ```bash
   rm -rf /tmp/securable-claude-plugin
   ```

## Verify

Ask opencode to list its skills (it has a native `skill` tool). You should see:

- `securability-engineering-review`
- `securability-engineering`
- `prd-securability-enhancement`
- `fiasse-lookup`

Then try: "Use the fiasse-lookup skill to explain Canonical Parsing."

## Updating

Re-clone and re-run the installer with `--force`:

```bash
/tmp/securable-claude-plugin/scripts/install_skills.sh --target .opencode --force
```

## Notes for the agent following this file

- opencode discovers project skills under `.opencode/skills/`, `.claude/skills/`,
  and `.agents/skills/`, plus the same paths under `~/.config/opencode`. Any one
  target is enough; don't install to several.
- The skills reference tools by action ("read a file", "search file contents",
  "run a shell command"). On opencode these resolve to `read`, `grep`/`glob`,
  and `bash` respectively; skill invocation goes through opencode's native
  `skill` tool.
- The pack's tooling policy applies: the skills never install scanners or other
  tools into the user's project. If a held check (e.g. the opengrep rule pack
  under `rules/opengrep/`) can't run because the tool is absent, say so rather
  than implying verification happened.

## Getting help

- Issues: https://github.com/Securability-Engineering/securable-claude-plugin/issues
- Full documentation: https://github.com/Securability-Engineering/securable-claude-plugin
