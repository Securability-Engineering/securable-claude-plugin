#!/usr/bin/env bash
set -uo pipefail

# Run every fast check CI runs, in one command. Exits non-zero if any fails.
# The opengrep pack check is skipped (with a notice) when opengrep is missing;
# set OPENGREP_BIN to point at a specific binary.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${REPO_ROOT}"

FAILED=0
run() {
  echo
  echo "== $* =="
  if "$@"; then :; else
    echo "^^ FAILED: $*" >&2
    FAILED=1
  fi
}

run python3 scripts/check_refs.py
run python3 scripts/validate_securable.py --dir examples/securable
run python3 tests/securable-contract/test_validate.py
run python3 scripts/build_bindings.py --check
run python3 tests/kernel_ab.py --self-test
run python3 scripts/check_manifests.py
run python3 - <<'EOF'
import json, glob, sys, yaml
paths = [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".claude/settings.json",
         ".cursor-plugin/plugin.json", ".devin-plugin/plugin.json",
         "schema/securable/requirements.schema.json", "schema/securable/boundaries.schema.json"]
paths += glob.glob("tests/*/evals/evals.json") + ["tests/kernel-ab-workspace/evals.json"]
for p in paths:
    json.load(open(p)); print(f"ok {p}")
for p in ["rules/opengrep/securable.yaml", "examples/securable/requirements.yaml", "examples/securable/boundaries.yaml"]:
    yaml.safe_load(open(p)); print(f"ok {p}")
EOF
run bash -n scripts/build_plugin_zip.sh
run bash -n scripts/generate_marketplace_json.sh
run bash -n scripts/install_skills.sh
run bash -n scripts/securability_report.sh
run bash -n scripts/test_opengrep_rules.sh

echo
echo "== opengrep pack =="
if bash scripts/test_opengrep_rules.sh; then :; else
  code=$?
  if [[ $code -eq 3 ]]; then
    echo "opengrep unavailable — pack check skipped (install opengrep to run it)"
  else
    echo "^^ FAILED: opengrep pack" >&2
    FAILED=1
  fi
fi

echo
if [[ $FAILED -ne 0 ]]; then
  echo "run_checks: FAILURES PRESENT"
  exit 1
fi
echo "run_checks: all checks passed"
