#!/usr/bin/env python3
"""A/B-test the securability kernel against a code-generation CLI.

Runs each eval prompt twice through an agent CLI — baseline (no extra
context) and kernel (core/kernel.md appended as system context) — then grades
both outputs with deterministic anti-pattern detectors. No LLM judge: the
detectors are regexes over the emitted code, so results are reproducible.

This measures the claim that the ~300-token kernel changes ordinary code
generation. Lower anti-pattern count is better; "notes" tracks whether the
output closed with a Securability Notes block (kernel adoption signal).

Usage:
  python3 tests/kernel_ab.py                 # both configs, all evals
  python3 tests/kernel_ab.py --config kernel --eval-id flask-order-lookup
  python3 tests/kernel_ab.py --cli claude --model claude-sonnet-5
  python3 tests/kernel_ab.py --grade-only    # re-grade saved outputs

Outputs land in tests/kernel-ab-workspace/iteration-<N>/<config>/<eval>.md
with results.json beside them. Requires the agent CLI on PATH for runs;
--grade-only needs only saved outputs.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORKSPACE = REPO / "tests" / "kernel-ab-workspace"
KERNEL = REPO / "core" / "kernel.md"

DETECTORS: dict[str, tuple[str, str]] = {
    # name: (description, regex over the full response text)
    "fstring_sql": ("f-string built SQL passed to execute()", r"execute(?:script)?\(\s*f['\"]"),
    "concat_sql": ("string-concatenated SQL passed to execute()",
                   r"""execute(?:script)?\(\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')\s*\+"""),
    "percent_sql": ("%-formatted SQL passed to execute()",
                    r"""execute(?:script)?\(\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')\s*%"""),
    "requests_no_timeout": ("requests call without any timeout", None),  # special-cased below
    "jwt_verify_unpinned": ("jwt.verify without pinned algorithms", None),  # special-cased below
    "bare_except": ("bare except / except-pass", r"except\s*(Exception\s*)?:\s*\n\s*pass\b|except\s*:\s*pass\b"),
    "bare_catch": ("empty catch block", r"catch\s*(\([^)]*\))?\s*\{\s*\}"),
}


def detect(name: str, text: str) -> bool:
    if name == "requests_no_timeout":
        return bool(re.search(r"\brequests\.(get|post|put|delete|head|request)\s*\(", text)) and "timeout" not in text
    if name == "jwt_verify_unpinned":
        return bool(re.search(r"\bjwt\.verify\s*\(", text)) and "algorithms" not in text
    desc, pattern = DETECTORS[name]
    assert pattern is not None, name
    return bool(re.search(pattern, text))


def kernel_body() -> str:
    text = KERNEL.read_text(encoding="utf-8")
    return re.sub(r"\A\s*<!--.*?-->\s*\n", "", text, count=1, flags=re.S).strip()


def run_cli(cli: str, prompt: str, system_append: str | None, model: str | None, timeout: int) -> str:
    cmd = [cli, "-p", prompt, "--output-format", "text"]
    if system_append:
        cmd += ["--append-system-prompt", system_append]
    if model:
        cmd += ["--model", model]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(WORKSPACE))
    if proc.returncode != 0:
        raise RuntimeError(f"{cli} failed ({proc.returncode}): {proc.stderr[-500:]}")
    return proc.stdout


def grade(evals: list[dict], iteration_dir: Path, configs: list[str]) -> dict:
    results: dict = {"configs": {}}
    for config in configs:
        cfg_dir = iteration_dir / config
        cfg_results = []
        for ev in evals:
            out_file = cfg_dir / f"{ev['id']}.md"
            if not out_file.is_file():
                cfg_results.append({"id": ev["id"], "missing": True})
                continue
            text = out_file.read_text(encoding="utf-8")
            hits = [d for d in ev["detectors"] if detect(d, text)]
            cfg_results.append({
                "id": ev["id"],
                "anti_patterns": hits,
                "anti_pattern_count": len(hits),
                "securability_notes": "securability notes" in text.lower(),
            })
        total = sum(r.get("anti_pattern_count", 0) for r in cfg_results)
        notes = sum(1 for r in cfg_results if r.get("securability_notes"))
        results["configs"][config] = {"evals": cfg_results, "total_anti_patterns": total, "notes_blocks": notes}
    return results


def print_table(results: dict, evals: list[dict]) -> None:
    configs = list(results["configs"].keys())
    print(f"\n{'eval':<24}" + "".join(f"{c:>22}" for c in configs))
    for i, ev in enumerate(evals):
        row = f"{ev['id']:<24}"
        for c in configs:
            r = results["configs"][c]["evals"][i]
            if r.get("missing"):
                cell = "missing"
            else:
                cell = f"{r['anti_pattern_count']} anti" + ("+notes" if r["securability_notes"] else "")
            row += f"{cell:>22}"
        print(row)
    print(f"{'TOTAL anti-patterns':<24}" + "".join(
        f"{results['configs'][c]['total_anti_patterns']:>22}" for c in configs))
    print(f"{'Securability Notes':<24}" + "".join(
        f"{results['configs'][c]['notes_blocks']:>22}" for c in configs))


FIXTURES = REPO / "tests" / "opengrep-fixtures"

# (relative fixture path, detector, expected) — shared ground truth with the
# opengrep pack, so the A/B harness's own detectors are verifiable without any
# CLI call. Inline snippets cover detectors with no file fixture.
SELF_TEST_FILES = [
    ("fails/sql.py", "fstring_sql", True),
    ("fails/sql.py", "concat_sql", True),
    ("fails/sql.py", "percent_sql", True),
    ("fails/http.py", "requests_no_timeout", True),
    ("fails/silent.py", "bare_except", True),
    ("fails/verify.js", "jwt_verify_unpinned", True),
    ("passes/sql.py", "fstring_sql", False),
    ("passes/sql.py", "concat_sql", False),
    ("passes/sql.py", "percent_sql", False),
    ("passes/http.py", "requests_no_timeout", False),
    ("passes/silent.py", "bare_except", False),
    ("passes/verify.js", "jwt_verify_unpinned", False),
]
SELF_TEST_SNIPPETS = [
    ("try { x(); } catch (e) {}", "bare_catch", True),
    ("try { x(); } catch (e) { log.warn('x failed', e); }", "bare_catch", False),
]


def self_test() -> int:
    failures = []
    for rel, detector, expected in SELF_TEST_FILES:
        text = (FIXTURES / rel).read_text(encoding="utf-8")
        got = detect(detector, text)
        (failures.append(f"{rel}: {detector} expected {expected}, got {got}") if got != expected
         else print(f"ok  {detector:<22} on {rel}: {got}"))
    for snippet, detector, expected in SELF_TEST_SNIPPETS:
        got = detect(detector, snippet)
        (failures.append(f"snippet: {detector} expected {expected}, got {got}") if got != expected
         else print(f"ok  {detector:<22} on snippet: {got}"))
    if failures:
        print(f"\n{len(failures)} detector self-test failure(s):")
        for f in failures:
            print(f"  FAIL {f}")
        return 1
    print("\nAll kernel A/B detector self-tests passed.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true",
                    help="verify the detectors against the opengrep fixtures; no CLI calls")
    ap.add_argument("--cli", default="claude", help="agent CLI supporting -p / --append-system-prompt (default claude)")
    ap.add_argument("--model", help="model override passed to the CLI")
    ap.add_argument("--config", choices=["baseline", "kernel"], help="run one config only")
    ap.add_argument("--eval-id", help="run one eval only")
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=600, help="per-call timeout seconds")
    ap.add_argument("--grade-only", action="store_true", help="re-grade saved outputs without calling the CLI")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    spec = json.loads((WORKSPACE / "evals.json").read_text(encoding="utf-8"))
    evals = [e for e in spec["evals"] if not args.eval_id or e["id"] == args.eval_id]
    if not evals:
        print(f"no eval matches {args.eval_id}", file=sys.stderr)
        return 2
    configs = [args.config] if args.config else ["baseline", "kernel"]
    iteration_dir = WORKSPACE / f"iteration-{args.iteration}"

    if not args.grade_only:
        kernel = kernel_body()
        for config in configs:
            system_append = kernel if config == "kernel" else None
            cfg_dir = iteration_dir / config
            cfg_dir.mkdir(parents=True, exist_ok=True)
            for ev in evals:
                out_file = cfg_dir / f"{ev['id']}.md"
                print(f"[{config}] {ev['id']} …", flush=True)
                out_file.write_text(run_cli(args.cli, ev["prompt"], system_append, args.model, args.timeout),
                                    encoding="utf-8")

    results = grade(spec["evals"], iteration_dir, configs)
    (iteration_dir / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print_table(results, spec["evals"])
    print(f"\nresults: {iteration_dir / 'results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
