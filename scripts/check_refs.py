#!/usr/bin/env python3
"""Validate ASVS and FIASSE references against the bundled reference data.

Scans the instruction surfaces (skills, commands, plays, templates, examples,
AGENTS.md, README.md) for:

  - ASVS references (V6, V6.3, V6.3.8) — the chapter/section file must exist
    under data/asvs/, and a full requirement ID must appear as a requirement
    row (e.g. `**6.3.8**`) in its section file.
  - FIASSE references (S4.4.1.2, SA.4) — the section file must exist under
    data/fiasse/, or be a parent whose leaf files exist.

This is the guard against the failure mode where instruction text cites
requirement IDs from a different catalog version than the one shipped
(e.g. ASVS 4.x chapter numbers against the ASVS 5.0 data files).

Exit code 0 = all references resolve; 1 = at least one dangling reference.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# docs/ is intentionally not scanned: the critical-review document quotes
# invalid references as findings and must be able to name them verbatim.
SCAN_TARGETS = [
    "AGENTS.md",
    "README.md",
    "core",
    "skills",
    "commands",
    "plays",
    "templates",
    "examples",
]

ASVS_DIR = REPO / "data" / "asvs"
FIASSE_DIR = REPO / "data" / "fiasse"

# V6 | V6.3 | V6.3.8 — require a word boundary and not part of e.g. "V6.3.x"
ASVS_REF = re.compile(r"\bV(\d{1,2})(?:\.(\d{1,2}))?(?:\.(\d{1,2}))?\b(?!\.[x\d])")
# S4.4.1.2 / SA.4 / S8 — avoid matching things like "SP 800" or "SHA256"
FIASSE_REF = re.compile(r"\bS(A)?\.?((?:\d{1,2})(?:\.\d{1,2}){0,3})\b")


def iter_files() -> list[Path]:
    files: list[Path] = []
    for target in SCAN_TARGETS:
        path = REPO / target
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
    return files


def asvs_chapters() -> set[str]:
    return {p.stem.split(".")[0] for p in ASVS_DIR.glob("V*.md")}


def check_asvs(text: str, rel: str, errors: list[str]) -> None:
    chapters = asvs_chapters()
    for m in ASVS_REF.finditer(text):
        chapter, section, req = m.group(1), m.group(2), m.group(3)
        ref = m.group(0)
        line_no = text.count("\n", 0, m.start()) + 1
        where = f"{rel}:{line_no}"
        if f"V{chapter}" not in chapters:
            errors.append(f"{where}: {ref} — chapter V{chapter} not in data/asvs/")
            continue
        if section is None:
            continue
        section_file = ASVS_DIR / f"V{chapter}.{section}.md"
        if not section_file.is_file():
            errors.append(f"{where}: {ref} — no data/asvs/V{chapter}.{section}.md")
            continue
        if req is not None:
            body = section_file.read_text(encoding="utf-8")
            if f"**{chapter}.{section}.{req}**" not in body:
                errors.append(
                    f"{where}: {ref} — requirement {chapter}.{section}.{req} "
                    f"not found in data/asvs/V{chapter}.{section}.md"
                )


def check_fiasse(text: str, rel: str, errors: list[str]) -> None:
    for m in FIASSE_REF.finditer(text):
        prefix = "SA" if m.group(1) else "S"
        number = m.group(2)
        ref = f"{prefix}.{number}" if prefix == "SA" else f"S{number}"
        line_no = text.count("\n", 0, m.start()) + 1
        where = f"{rel}:{line_no}"
        exact = FIASSE_DIR / f"{ref}.md"
        if exact.is_file():
            continue
        # Accept a parent section whose leaves exist (e.g. "S2" via S2.1.md).
        if any(FIASSE_DIR.glob(f"{ref}.*.md")):
            continue
        errors.append(f"{where}: {ref} — no matching file in data/fiasse/")


def main() -> int:
    errors: list[str] = []
    files = iter_files()
    for path in files:
        rel = str(path.relative_to(REPO))
        text = path.read_text(encoding="utf-8")
        check_asvs(text, rel, errors)
        check_fiasse(text, rel, errors)

    if errors:
        print(f"{len(errors)} dangling reference(s):")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"OK — all ASVS/FIASSE references in {len(files)} file(s) resolve against data/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
