#!/usr/bin/env bash
set -euo pipefail

# Test the securable semgrep pack against its fixtures:
#   - every fails/ fixture triggers at least one finding
#   - every rule id fires at least once across the fails/ set
#   - passes/ fixtures trigger nothing
#
# SEMGREP_BIN overrides the binary (default: semgrep on PATH).
# Exits 0 on success, 1 on assertion failure, 3 if semgrep is unavailable.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RULES="${REPO_ROOT}/rules/semgrep/securable.yaml"
FIXTURES="${REPO_ROOT}/tests/semgrep-fixtures"
SEMGREP_BIN="${SEMGREP_BIN:-semgrep}"

if ! command -v "${SEMGREP_BIN}" >/dev/null 2>&1; then
  echo "semgrep not available (set SEMGREP_BIN or pip install semgrep) — skipping" >&2
  exit 3
fi

OUT="$(mktemp)"
trap 'rm -f "${OUT}"' EXIT

# Fixture files are passed explicitly: semgrep's default ignore patterns skip
# tests/ directories on a directory scan, but explicit targets always scan.
mapfile -t FIXTURE_FILES < <(find "${FIXTURES}/fails" "${FIXTURES}/passes" -type f | sort)

"${SEMGREP_BIN}" scan --quiet --json --config "${RULES}" \
  --metrics=off --no-git-ignore "${FIXTURE_FILES[@]}" > "${OUT}"

python3 - "${OUT}" "${RULES}" "${FIXTURES}" <<'PYEOF'
import json
import sys
from pathlib import Path

out_path, rules_path, fixtures = sys.argv[1], sys.argv[2], Path(sys.argv[3])
data = json.load(open(out_path))

findings = {}
for r in data.get("results", []):
    path = Path(r["path"]).resolve()
    findings.setdefault(path, set()).add(r["check_id"].rsplit(".", 1)[-1])

rule_ids = set()
for line in open(rules_path, encoding="utf-8"):
    line = line.strip()
    if line.startswith("- id:"):
        rule_ids.add(line.split(":", 1)[1].strip())

failures = []
fails_dir = (fixtures / "fails").resolve()
passes_dir = (fixtures / "passes").resolve()

fired = set()
for f in sorted(fails_dir.iterdir()):
    hits = findings.get(f.resolve(), set())
    fired |= hits
    if hits:
        print(f"ok  fails/{f.name}: {sorted(hits)}")
    else:
        failures.append(f"fails/{f.name}: no finding triggered")

for f in sorted(passes_dir.iterdir()):
    hits = findings.get(f.resolve(), set())
    if hits:
        failures.append(f"passes/{f.name}: unexpected finding(s) {sorted(hits)}")
    else:
        print(f"ok  passes/{f.name}: clean")

silent_rules = rule_ids - fired
for rid in sorted(silent_rules):
    failures.append(f"rule {rid}: never fired on any fails/ fixture")

errors = data.get("errors", [])
for e in errors:
    failures.append(f"semgrep error: {e.get('message', e)}")

if failures:
    print(f"\n{len(failures)} semgrep pack failure(s):")
    for f in failures:
        print(f"  FAIL {f}")
    sys.exit(1)
print(f"\nAll semgrep pack tests passed ({len(rule_ids)} rules, "
      f"{sum(1 for _ in fails_dir.iterdir())} fail fixtures, "
      f"{sum(1 for _ in passes_dir.iterdir())} pass fixtures).")
PYEOF
