#!/usr/bin/env bash
set -euo pipefail

# Produce a FIASSE v1.1 S5.2.1 Securability Report for a diff, via whatever
# agent CLI the team runs. Advisory by default (S5.2.2): the report directs
# attention; gating on it is a separate, explicit policy decision (S5.2.3).
#
# Usage:
#   scripts/securability_report.sh [--base REF] [--head REF] [--out FILE] [--dry-run]
#
# Environment:
#   AGENT_CLI    command template for a non-interactive agent run reading the
#                prompt from stdin. Default: "claude -p --output-format text"
#                Examples: "codex exec" · "opencode run"
#   SKILL_PATH   review skill path (default: skills/securability-engineering-review/SKILL.md
#                resolved against this repo)
#
# The prompt instructs the agent to follow the review skill against the diff,
# mark uninspected attributes `Not assessed`, and lead with the SA.4 framing.

BASE="${BASE:-origin/main}"
HEAD="${HEAD:-HEAD}"
OUT=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base) BASE="${2:?}"; shift 2 ;;
    --head) HEAD="${2:?}"; shift 2 ;;
    --out) OUT="${2:?}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_PATH="${SKILL_PATH:-${REPO_ROOT}/skills/securability-engineering-review/SKILL.md}"
AGENT_CLI="${AGENT_CLI:-claude -p --output-format text}"

if [[ ! -f "${SKILL_PATH}" ]]; then
  echo "Review skill not found at ${SKILL_PATH}" >&2
  exit 1
fi

CHANGED_FILES="$(git diff --name-only "${BASE}...${HEAD}" -- || true)"
if [[ -z "${CHANGED_FILES}" ]]; then
  echo "No changes between ${BASE} and ${HEAD}; nothing to report."
  exit 0
fi

PROMPT=$(cat <<EOF
You are producing a Securability Report (FIASSE v1.1 S5.2.1) for a merge request.

Follow the review skill at ${SKILL_PATH} exactly — it is authoritative for the
rubric, scoring math, Not assessed / N/A handling, severity classification, and
the three-part report shape.

Scope: the diff ${BASE}...${HEAD} in the repository at $(pwd). Changed files:
${CHANGED_FILES}

Conduct:
- Inspect the changed files and enough surrounding code to judge them; mark
  everything else Not assessed. More than two Not assessed attributes means no
  composite score — follow the skill's rule.
- If .securable/requirements.yaml exists, verify requirements with status
  'implemented' against their acceptance criteria and report per-requirement
  verdicts. Do not modify any files.
- This report is ADVISORY (S5.2.2): posture and direction, not a gate. Lead
  with the SA.4 framing line. Aggregate systemic findings; do not emit one
  finding per instance of the same root cause (S6.2).
- Cite file paths for every claim. Never fabricate evidence.

Output only the report, in the skill's three-part format.
EOF
)

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "--- securability_report dry run ---"
  echo "agent cli : ${AGENT_CLI}"
  echo "skill     : ${SKILL_PATH}"
  echo "diff      : ${BASE}...${HEAD}"
  echo "files     :"
  echo "${CHANGED_FILES}" | sed 's/^/  /'
  echo "--- prompt begins ---"
  echo "${PROMPT}"
  exit 0
fi

if [[ -n "${OUT}" ]]; then
  printf '%s' "${PROMPT}" | ${AGENT_CLI} | tee "${OUT}"
else
  printf '%s' "${PROMPT}" | ${AGENT_CLI}
fi
