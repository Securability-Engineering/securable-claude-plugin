#!/usr/bin/env python3
"""Generate per-harness bindings from the securability kernel.

The kernel (core/kernel.md) is the single source of truth for the always-on
guidance. This script compiles it into each harness's always-loaded format and
keeps AGENTS.md's marked kernel block in sync. Bindings are generated, never
edited — hand-forked copies are how content rot happens.

Outputs:
  bindings/cursor/securable.mdc            Cursor rule (alwaysApply)
  bindings/copilot/copilot-instructions.md GitHub Copilot custom instructions
  bindings/gemini/GEMINI.md                Gemini CLI context file
  bindings/aider/CONVENTIONS.md            Aider conventions file
  AGENTS.md                                between securable-kernel markers

Modes:
  (default)   write all bindings
  --check     verify committed bindings match the kernel and the size budget
              holds; exit 1 on any drift (used by CI)

The size budget keeps the kernel honest: always-on context taxes every
completion in the host harness, so the body must stay small (~300 tokens).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KERNEL = REPO / "core" / "kernel.md"
AGENTS = REPO / "AGENTS.md"

# Body budget in characters (comment header excluded). ~4 chars/token puts
# this near 300 tokens — small enough for any harness's ambient context.
MAX_BODY_CHARS = 1500

GENERATED_HEADER = (
    "<!-- GENERATED from core/kernel.md (securable-skills) — do not edit; "
    "run scripts/build_bindings.py -->\n"
)

MARK_BEGIN = "<!-- securable-kernel:begin (generated from core/kernel.md — edit there, run scripts/build_bindings.py) -->"
MARK_END = "<!-- securable-kernel:end -->"

CURSOR_FRONTMATTER = """---
description: Securable engineering non-negotiables (FIASSE/SSEM securable-skills kernel)
alwaysApply: true
---
"""


def kernel_body() -> str:
    text = KERNEL.read_text(encoding="utf-8")
    # Strip the leading HTML comment header (source-of-truth note).
    body = re.sub(r"\A\s*<!--.*?-->\s*\n", "", text, count=1, flags=re.S)
    return body.strip() + "\n"


def render_bindings(body: str) -> dict[Path, str]:
    return {
        REPO / "bindings" / "cursor" / "securable.mdc": CURSOR_FRONTMATTER + GENERATED_HEADER + body,
        REPO / "bindings" / "copilot" / "copilot-instructions.md": GENERATED_HEADER + body,
        REPO / "bindings" / "gemini" / "GEMINI.md": GENERATED_HEADER + body,
        REPO / "bindings" / "aider" / "CONVENTIONS.md": GENERATED_HEADER + body,
    }


def render_agents(body: str, current: str) -> str:
    block = f"{MARK_BEGIN}\n{body}{MARK_END}"
    if MARK_BEGIN in current and MARK_END in current:
        pattern = re.compile(re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END), re.S)
        return pattern.sub(lambda _: block, current, count=1)
    # First run: insert the kernel section after the canonical-entry-point line.
    anchor = "This file is the canonical agent entry point"
    idx = current.find(anchor)
    if idx == -1:
        raise SystemExit("AGENTS.md: cannot find insertion anchor and no kernel markers present")
    para_end = current.index("\n\n", idx) + 1
    return current[:para_end] + "\n" + block + "\n" + current[para_end:]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="verify instead of write; exit 1 on drift")
    args = ap.parse_args()

    body = kernel_body()
    if len(body) > MAX_BODY_CHARS:
        print(
            f"kernel body is {len(body)} chars — over the {MAX_BODY_CHARS}-char budget. "
            "Always-on context taxes every completion; trim core/kernel.md.",
            file=sys.stderr,
        )
        return 1

    targets = render_bindings(body)
    agents_current = AGENTS.read_text(encoding="utf-8")
    agents_rendered = render_agents(body, agents_current)

    if args.check:
        drift: list[str] = []
        for path, content in targets.items():
            if not path.is_file():
                drift.append(f"{path.relative_to(REPO)}: missing")
            elif path.read_text(encoding="utf-8") != content:
                drift.append(f"{path.relative_to(REPO)}: differs from generated content")
        if agents_current != agents_rendered:
            drift.append("AGENTS.md: kernel block out of sync with core/kernel.md")
        if drift:
            print(f"{len(drift)} binding(s) out of sync — run scripts/build_bindings.py:")
            for d in drift:
                print(f"  {d}")
            return 1
        print(f"OK — kernel {len(body)} chars (budget {MAX_BODY_CHARS}); all bindings in sync.")
        return 0

    for path, content in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO)}")
    if agents_current != agents_rendered:
        AGENTS.write_text(agents_rendered, encoding="utf-8")
        print("updated AGENTS.md kernel block")
    else:
        print("AGENTS.md kernel block already in sync")
    print(f"kernel body: {len(body)} chars (budget {MAX_BODY_CHARS})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
