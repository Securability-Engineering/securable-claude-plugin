#!/usr/bin/env python3
"""Tests for scripts/validate_securable.py.

Runs the validator over the shipped valid example and over a set of invalid
fixtures, asserting each invalid fixture fails for the expected reason.
No test framework required: python3 tests/securable-contract/test_validate.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
VALIDATOR = REPO / "scripts" / "validate_securable.py"
EXAMPLES = REPO / "examples" / "securable"

VALID_REQUIREMENTS = (EXAMPLES / "requirements.yaml").read_text(encoding="utf-8")
VALID_BOUNDARIES = (EXAMPLES / "boundaries.yaml").read_text(encoding="utf-8")

# (name, mutate(requirements_text) -> text, expected error substring)
INVALID_CASES = [
    (
        "wrong-contract-version",
        lambda t: t.replace("securable_contract: 1", "securable_contract: 2", 1),
        "'securable_contract: 1' is required",
    ),
    (
        "bad-asvs-level",
        lambda t: t.replace("asvs_level: 2", "asvs_level: 5"),
        "'asvs_level' must be 1, 2, or 3",
    ),
    (
        "nonexistent-asvs-requirement",
        lambda t: t.replace("V6.3.8", "V6.3.99"),
        "6.3.99 not found",
    ),
    (
        "pre-5.0-style-chapter",
        lambda t: t.replace("V16.3.1", "V19.1.1"),
        "chapter V19 not found",
    ),
    (
        "escalation-missing",
        lambda t: t.replace("        escalation: true\n", ""),
        "set 'escalation: true'",
    ),
    (
        "verified-without-evidence",
        lambda t: t.replace("status: planned", "status: verified", 1),
        "requires non-empty 'evidence'",
    ),
    (
        "requirement-id-wrong-feature",
        lambda t: t.replace("id: F-03-R5", "id: F-04-R5"),
        "does not belong to feature F-03",
    ),
    (
        "duplicate-requirement-id",
        lambda t: t.replace("id: F-03-R4", "id: F-03-R1", 1),
        "duplicate id F-03-R1",
    ),
    (
        "unknown-boundary",
        lambda t: t.replace("browser-api, api-email", "browser-api, api-smtp"),
        "boundary 'api-smtp' not defined",
    ),
    (
        "missing-acceptance",
        lambda t: t.replace(
            "        acceptance:\n"
            "          - More than 5 requests for one email within 10 minutes are rejected with HTTP 429 and logged.\n",
            "",
        ),
        "'acceptance' must be a non-empty string or list",
    ),
    (
        "bad-status",
        lambda t: t.replace("status: planned", "status: done", 1),
        "'status' must be one of",
    ),
    (
        "unknown-key",
        lambda t: t.replace("generated_by:", "generated_from:"),
        "unknown top-level key 'generated_from'",
    ),
]


def run_validator(workdir: Path, extra: list[str] | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(VALIDATOR), "--dir", str(workdir)]
    return subprocess.run(cmd + (extra or []), capture_output=True, text=True)


def main() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "requirements.yaml").write_text(VALID_REQUIREMENTS, encoding="utf-8")
        (d / "boundaries.yaml").write_text(VALID_BOUNDARIES, encoding="utf-8")
        proc = run_validator(d)
        if proc.returncode != 0:
            failures.append(f"valid example rejected:\n{proc.stdout}{proc.stderr}")
        else:
            print("ok  valid-example accepted")

    for name, mutate, expected in INVALID_CASES:
        mutated = mutate(VALID_REQUIREMENTS)
        if mutated == VALID_REQUIREMENTS:
            failures.append(f"{name}: mutation did not change the fixture (test bug)")
            continue
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "requirements.yaml").write_text(mutated, encoding="utf-8")
            (d / "boundaries.yaml").write_text(VALID_BOUNDARIES, encoding="utf-8")
            proc = run_validator(d)
            out = proc.stdout + proc.stderr
            if proc.returncode == 0:
                failures.append(f"{name}: expected rejection, validator passed")
            elif expected not in out:
                failures.append(f"{name}: rejected, but without expected message {expected!r}:\n{out}")
            else:
                print(f"ok  {name} rejected as expected")

    # Boundaries-only and requirements-only runs must both work.
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "boundaries.yaml").write_text(VALID_BOUNDARIES, encoding="utf-8")
        if run_validator(d).returncode != 0:
            failures.append("boundaries-only run failed")
        else:
            print("ok  boundaries-only accepted")

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "requirements.yaml").write_text(VALID_REQUIREMENTS, encoding="utf-8")
        proc = run_validator(d)
        # Without boundaries.yaml, unknown-boundary checks are skipped: still valid.
        if proc.returncode != 0:
            failures.append(f"requirements-only run failed:\n{proc.stdout}{proc.stderr}")
        else:
            print("ok  requirements-only accepted")

    # Missing ASVS catalog degrades to a warning, not an error.
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "requirements.yaml").write_text(VALID_REQUIREMENTS, encoding="utf-8")
        proc = run_validator(d, ["--asvs-dir", str(d / "no-catalog")])
        if proc.returncode != 0 or "existence not verified" not in proc.stdout:
            failures.append(f"missing-catalog should warn and pass:\n{proc.stdout}{proc.stderr}")
        else:
            print("ok  missing-catalog degrades to warning")

    if failures:
        print(f"\n{len(failures)} test failure(s):")
        for f in failures:
            print(f"  FAIL {f}")
        return 1
    print("\nAll securable-contract validator tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
