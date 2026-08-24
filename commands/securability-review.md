---
description: Run a full SSEM securability assessment (FIASSE v1.1) on code
argument-hint: [files, directories, PR, or repo path to review]
---

Run the **securability-engineering-review** skill against: $ARGUMENTS

If no target is given, review the current project.

Load and follow the skill at `${CLAUDE_PLUGIN_ROOT}/skills/securability-engineering-review/SKILL.md` (in a repo checkout: `skills/securability-engineering-review/SKILL.md`). That file is authoritative for the scoring rubric, the weakest-link floor, `Not assessed`/`N/A` handling, severity classification, and the three-part report shape — do not restate or improvise a different rubric here.

Lead the report with the FIASSE v1.1 SA.4 framing: the score is a directional management aid, not a statement of assurance or compliance.
