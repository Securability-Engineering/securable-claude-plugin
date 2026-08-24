---
description: Generate code with FIASSE/SSEM securable-engineering constraints applied
argument-hint: [description of the code to generate or refactor]
---

Run the **securability-engineering** skill to generate: $ARGUMENTS

Load and follow the skill at `${CLAUDE_PLUGIN_ROOT}/skills/securability-engineering/SKILL.md` (in a repo checkout: `skills/securability-engineering/SKILL.md`). That file is authoritative for the SSEM attribute constraints, trust-boundary handling, the anti-pattern reference, the generation checklist, and the Securability Notes output block — do not restate or improvise different constraints here.

Stay in the skill's Default Mode (single-shot generation) unless the user passes `--full-loop` or asks for the end-to-end loop.
