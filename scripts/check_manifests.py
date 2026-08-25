#!/usr/bin/env python3
"""Keep the per-agent plugin manifests in lockstep.

The pack ships one adapter manifest per agent harness:

    .claude-plugin/plugin.json       (canonical: version + metadata source of truth)
    .claude-plugin/marketplace.json  (plugins[0] mirrors the canonical manifest)
    .cursor-plugin/plugin.json
    .devin-plugin/plugin.json

Every manifest must parse, agree with the canonical manifest on name, version,
license, and repository, and any relative resource pointer (e.g. the Cursor
manifest's "skills" path) must resolve inside the repo. Install documents that
carry no version (.opencode/INSTALL.md, .agents/INSTALL.md) must exist.

Exit status: 0 when consistent, 1 with one line per problem otherwise.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CANONICAL = ".claude-plugin/plugin.json"
MIRROR_MANIFESTS = [
    ".cursor-plugin/plugin.json",
    ".devin-plugin/plugin.json",
]
INSTALL_DOCS = [
    ".opencode/INSTALL.md",
    ".agents/INSTALL.md",
]
LOCKSTEP_FIELDS = ["name", "version", "license", "repository"]


def load(rel: str, errors: list) -> dict:
    path = REPO_ROOT / rel
    if not path.is_file():
        errors.append(f"{rel}: missing")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rel}: invalid JSON ({exc})")
        return {}


def main() -> int:
    errors: list = []

    canonical = load(CANONICAL, errors)
    if not canonical:
        for line in errors:
            print(f"FAIL {line}", file=sys.stderr)
        return 1

    for rel in MIRROR_MANIFESTS:
        manifest = load(rel, errors)
        if not manifest:
            continue
        for field in LOCKSTEP_FIELDS:
            if manifest.get(field) != canonical.get(field):
                errors.append(
                    f"{rel}: {field} {manifest.get(field)!r} != "
                    f"{CANONICAL} {field} {canonical.get(field)!r}"
                )
        # Resource pointers resolve against the plugin root (the repo root),
        # per the Claude/Cursor plugin convention — not the manifest's own dir.
        skills = manifest.get("skills")
        if skills is not None:
            skills_dir = (REPO_ROOT / skills).resolve()
            if not skills_dir.is_dir() or not list(skills_dir.glob("*/SKILL.md")):
                errors.append(f"{rel}: skills path {skills!r} has no */SKILL.md")

    marketplace = load(".claude-plugin/marketplace.json", errors)
    plugins = marketplace.get("plugins") or [{}]
    entry = plugins[0]
    for field in ["name", "version", "license"]:
        if entry.get(field) != canonical.get(field):
            errors.append(
                f".claude-plugin/marketplace.json: plugins[0].{field} "
                f"{entry.get(field)!r} != {CANONICAL} {field} {canonical.get(field)!r}"
            )

    for rel in INSTALL_DOCS:
        if not (REPO_ROOT / rel).is_file():
            errors.append(f"{rel}: missing")

    if errors:
        for line in errors:
            print(f"FAIL {line}", file=sys.stderr)
        return 1

    for rel in [CANONICAL, ".claude-plugin/marketplace.json", *MIRROR_MANIFESTS, *INSTALL_DOCS]:
        print(f"ok {rel}")
    print(f"manifests in lockstep at version {canonical['version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
