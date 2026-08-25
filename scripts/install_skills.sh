#!/usr/bin/env bash
set -euo pipefail

# Install the securable skills into an agent tool's discovery path.
#
# Performs a layout-preserving copy of skills/, data/, plays/, and templates/
# into a single target root, so the relative references inside each SKILL.md
# (../../data/..., ../../plays/..., ../../templates/...) keep resolving.
#
# Common targets and the tools that discover them:
#   .agents                  agent-standard project location (opencode and others)
#   .opencode                opencode project config
#   .claude                  Claude Code project skills (also read by opencode)
#   ~/.config/opencode       opencode global config
#
# Usage:
#   scripts/install_skills.sh [--target DIR] [--force]
#
#   --target DIR   Destination root (default: .agents in the current directory)
#   --force        Replace an existing installation at the target

TARGET=".agents"
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:?--target requires a directory}"; shift 2 ;;
    --force)  FORCE=1; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Layout-preserving component set. schema/, core/, and rules/ ride along so the
# skills' contract references (schema/securable/*, scripts/validate_securable.py)
# and the kernel/rule pack work from an installed tree too.
COMPONENTS=(skills data plays templates schema core rules)
SCRIPT_FILES=(validate_securable.py)

for c in "${COMPONENTS[@]}"; do
  if [[ ! -d "${REPO_ROOT}/${c}" ]]; then
    echo "Missing ${REPO_ROOT}/${c} — run from a full checkout of securable-claude-plugin" >&2
    exit 1
  fi
done

mkdir -p "${TARGET}"

for c in "${COMPONENTS[@]}"; do
  dest="${TARGET}/${c}"
  if [[ -e "${dest}" ]]; then
    if [[ "${FORCE}" -eq 1 ]]; then
      rm -rf "${dest}"
    else
      echo "Refusing to overwrite existing ${dest} (use --force to replace)" >&2
      exit 1
    fi
  fi
  cp -R "${REPO_ROOT}/${c}" "${dest}"
done

mkdir -p "${TARGET}/scripts"
for f in "${SCRIPT_FILES[@]}"; do
  cp "${REPO_ROOT}/scripts/${f}" "${TARGET}/scripts/${f}"
done

echo "Installed securable skills into ${TARGET}/"
echo
echo "  skills:    $(ls "${TARGET}/skills")"
echo
echo "Discovery notes:"
echo "  - opencode reads project .opencode/skills, .claude/skills, and .agents/skills,"
echo "    plus the same paths under ~/.config/opencode and ~/.claude and ~/.agents."
echo "  - Claude Code reads project skills from .claude/skills (for the plugin itself,"
echo "    install via the plugin manager instead of this script)."
echo "  - Keep skills/, data/, plays/, and templates/ siblings under one root;"
echo "    the skills' internal references depend on that layout."
